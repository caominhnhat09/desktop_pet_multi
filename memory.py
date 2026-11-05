"""
memory.py — Persistent memory system for the pet.

Stores:
  • Last 50 conversation exchanges (user + pet)
  • Detected user habits (peak work hours, fav apps, late night patterns)
  • Named facts the user has told the pet ("my name is X", "I work at Y")
  • Emotional history (what made the pet happy/sad recently)
  • Session statistics (interactions today, tricks today, etc.)

All persisted to memory.json. Injected into LLM system prompt
to give genuine continuity across sessions.
"""

import json, os, re, time, datetime
from collections import defaultdict, deque

MEMORY_PATH = os.path.join(os.path.dirname(__file__), "memory.json")
MAX_EXCHANGES = 50
MAX_FACTS     = 30


class PetMemory:
    def __init__(self):
        self._data = self._load()
        self._session_start  = time.time()
        self._session_tricks = 0
        self._session_feeds  = 0
        self._session_chats  = 0
        self._hour_counts    = defaultdict(int)  # hour → interaction count

    # ── Persistence ──────────────────────────────────────────────────────

    def _load(self) -> dict:
        defaults = {
            "exchanges":      [],    # [{role, text, ts}]
            "facts":          {},    # {key: value} e.g. {"user_name": "Alex"}
            "app_time":       {},    # {app_name: minutes}
            "peak_hours":     [],    # list of ints (hours with most activity)
            "hour_counts":    {},    # {"21": phút hoạt động tích lũy qua MỌI phiên}
            "late_nights":    0,
            "total_sessions": 0,
            "emotions":       [],    # [{emotion, cause, ts}] last 20
            "topics":         [],    # recent topics discussed
        }
        if os.path.exists(MEMORY_PATH):
            try:
                with open(MEMORY_PATH) as f:
                    saved = json.load(f)
                defaults.update(saved)
                # Bản cũ tính peak_hours chỉ từ phiên hiện tại rồi ghi đè -> bỏ giá trị đó,
                # chờ dữ liệu tích lũy thật.
                if "hour_counts" not in saved:
                    defaults["peak_hours"] = []
            except Exception:
                pass
        defaults["total_sessions"] = defaults.get("total_sessions", 0) + 1
        return defaults

    def save(self):
        try:
            data = dict(self._data)
            data["app_time"] = {k: round(v, 3) for k, v in
                                self._data.get("app_time", {}).items()}
            with open(MEMORY_PATH, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    # ── Exchange logging ──────────────────────────────────────────────────

    def add_exchange(self, user_text: str, pet_text: str):
        """Log a conversation exchange."""
        self._data["exchanges"].append({
            "role": "user", "text": user_text[:200],
            "ts": time.time()
        })
        self._data["exchanges"].append({
            "role": "pet", "text": pet_text[:200],
            "ts": time.time()
        })
        # Keep only last MAX_EXCHANGES
        if len(self._data["exchanges"]) > MAX_EXCHANGES * 2:
            self._data["exchanges"] = self._data["exchanges"][-(MAX_EXCHANGES * 2):]

        self._session_chats += 1
        self._extract_facts(user_text)

    def get_recent_exchanges(self, n: int = 10) -> list:
        """Get last N exchanges formatted for LLM injection."""
        recent = self._data["exchanges"][-(n * 2):]
        return [{"role": e["role"], "content": e["text"]} for e in recent]

    # ── Fact extraction ───────────────────────────────────────────────────

    FACT_PATTERNS = [
        (r"my name is (\w+)",           "user_name"),
        (r"i(?:'m| am) (\w+)",          "user_name"),
        (r"call me (\w+)",              "user_name"),
        (r"i work (?:at|for) (.+?)[\.\!]", "workplace"),
        (r"i(?:'m| am) (?:a |an )?(.+?) (?:developer|engineer|designer|student)", "job"),
        (r"i(?:'m| am) (\d+) years? old", "age"),
        (r"i live in (.+?)[\.\!,]",     "location"),
        (r"i like (.+?)[\.\!]",         "likes"),
        (r"i love (.+?)[\.\!]",         "likes"),
        (r"my (?:fav|favorite) (.+?) is (.+?)[\.\!]", "favorite"),
    ]

    # "I'm tired" / "I am back" không phải là tên người dùng
    _NOT_A_NAME = {
        "a", "an", "the", "not", "so", "just", "very", "really", "going", "back",
        "here", "there", "ready", "sorry", "sure", "fine", "good", "great", "ok",
        "okay", "tired", "hungry", "sad", "happy", "bored", "busy", "angry",
        "working", "coding", "learning", "trying", "still", "also", "too", "done",
        "late", "early", "new", "in", "at", "on", "from", "with", "then", "now",
        "again", "today", "thinking", "looking", "waiting", "doing", "feeling",
    }

    def _extract_facts(self, text: str):
        low = text.lower().strip()
        for pattern, key in self.FACT_PATTERNS:
            m = re.search(pattern, low)
            if m:
                value = m.group(1).strip()
                if value in ("a", "an", "the"):      # vd "I am a developer" -> job="a"
                    continue
                if key == "user_name" and (value in self._NOT_A_NAME
                                           or value.isdigit()):
                    continue
                if key == "favorite" and m.lastindex and m.lastindex >= 2:
                    # "my favorite color is blue": lưu favorite_color = blue
                    # (bản cũ chỉ lưu "color" và làm mất giá trị "blue")
                    cat   = re.sub(r"\W+", "_", value)[:20].strip("_") or "thing"
                    key   = f"favorite_{cat}"
                    value = m.group(2).strip()
                if len(value) < 60:  # sanity check
                    self._data["facts"][key] = value

    # ── App time tracking ─────────────────────────────────────────────────

    def record_app_time(self, app_name: str, seconds: float):
        if not app_name or app_name == "unknown":
            return
        name = app_name.replace(".exe", "").lower()
        minutes = self._data["app_time"].get(name, 0) + seconds / 60
        # Bản cũ làm tròn 1 chữ số thập phân MỖI TICK (cộng ~0.0003 phút rồi round(..,1))
        # nên giá trị luôn về 0.0 -> tab Apps trống, "Top apps" xếp ngẫu nhiên.
        # Giờ giữ nguyên độ chính xác trong RAM, chỉ làm tròn khi ghi file (xem save()).
        self._data["app_time"][name] = minutes

    def top_apps(self, n: int = 3) -> list:
        apps = sorted(((k, v) for k, v in self._data["app_time"].items() if v > 0),
                      key=lambda x: x[1], reverse=True)
        return [a[0] for a in apps[:n]]

    # ── Hour tracking ─────────────────────────────────────────────────────

    MIN_SAMPLES_FOR_PEAK = 30      # cần ≥30 phút hoạt động mới kết luận "giờ cao điểm"

    def _bump_hour(self):
        hour = datetime.datetime.now().hour
        counts = self._data.setdefault("hour_counts", {})
        counts[str(hour)] = counts.get(str(hour), 0) + 1
        total = sum(counts.values())
        if total >= self.MIN_SAMPLES_FOR_PEAK:
            top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
            self._data["peak_hours"] = [int(h) for h, _ in top]
        return hour

    def record_interaction(self):
        """Gọi khi có tương tác (LLM trả lời, gửi lệnh)."""
        hour = self._bump_hour()
        if hour >= 23 or hour <= 3:
            self._data["late_nights"] = self._data.get("late_nights", 0) + 1

    def record_active_minute(self):
        """Gọi mỗi phút khi người dùng THỰC SỰ đang dùng máy (không AFK).
        Bản cũ chỉ đếm trong RAM của phiên hiện tại và ghi đè giá trị đã lưu,
        nên mở app lúc 21h là 'giờ hoạt động nhiều nhất' = 21:00 ngay."""
        self._bump_hour()

    # ── Emotion logging ───────────────────────────────────────────────────

    def log_emotion(self, emotion: str, cause: str):
        self._data["emotions"].append({
            "emotion": emotion, "cause": cause[:80], "ts": time.time()
        })
        if len(self._data["emotions"]) > 20:
            self._data["emotions"] = self._data["emotions"][-20:]

    def recent_emotions(self) -> list:
        recent = self._data["emotions"][-5:]
        return [e["emotion"] for e in recent]

    # ── LLM context builder ───────────────────────────────────────────────

    def build_context_block(self) -> str:
        """Build a compact memory summary to inject into LLM system prompt."""
        parts = []

        # Known facts about user
        facts = self._data.get("facts", {})
        if facts.get("user_name"):
            parts.append(f"The user's name is {facts['user_name']}.")
        if facts.get("job"):
            parts.append(f"They are a {facts['job']}.")
        if facts.get("workplace"):
            parts.append(f"They work at {facts['workplace']}.")
        if facts.get("likes"):
            parts.append(f"They like {facts['likes']}.")
        if facts.get("location"):
            parts.append(f"They live in {facts['location']}.")
        if facts.get("age"):
            parts.append(f"They are {facts['age']} years old.")
        # Mọi fact còn lại (kể cả fact thêm tay trong Dashboard) — tối đa 6 mục,
        # để bảng Facts thật sự ảnh hưởng tới câu trả lời của AI.
        known = {"user_name", "job", "workplace", "likes", "location", "age"}
        extra = []
        for k, v in facts.items():
            if k in known or not v:
                continue
            if k.startswith("favorite_"):
                extra.append(f"their favorite {k[9:].replace('_', ' ')} is {str(v)[:40]}")
            else:
                extra.append(f"{k.replace('_', ' ')}: {str(v)[:40]}")
        if extra:
            parts.append("Also: " + "; ".join(extra[:6]) + ".")

        # Usage patterns
        top = self.top_apps(2)
        if top:
            parts.append(f"They mostly use: {', '.join(top)}.")

        peak = self._data.get("peak_hours", [])
        if peak:
            hrs = ", ".join(f"{h}:00" for h in peak[:2])
            parts.append(f"Most active around {hrs}.")

        nights = self._data.get("late_nights", 0)
        if nights > 5:
            parts.append(f"Often works late at night ({nights} late sessions).")

        # Session info
        sessions = self._data.get("total_sessions", 1)
        parts.append(f"You've been together for {sessions} sessions.")

        # Recent mood
        emotions = self.recent_emotions()
        if emotions:
            parts.append(f"Recent pet moods: {', '.join(emotions[-3:])}.")

        return " ".join(parts) if parts else ""

    # ── Session summary ───────────────────────────────────────────────────

    def session_duration_minutes(self) -> float:
        return (time.time() - self._session_start) / 60

    def session_summary(self) -> str:
        dur = self.session_duration_minutes()
        parts = []
        if dur > 1:      parts.append(f"{dur:.0f}min session")
        if self._session_chats:  parts.append(f"{self._session_chats} chats")
        if self._session_tricks: parts.append(f"{self._session_tricks} tricks")
        if self._session_feeds:  parts.append(f"fed {self._session_feeds}x")
        return " | ".join(parts) if parts else "short session"
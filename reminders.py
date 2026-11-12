"""
reminders.py — Pomodoro-style break enforcement.

Cách hoạt động (chọn "Focus length" trong Settings → Reminders):

  FOCUS  : đếm thời gian bạn THỰC SỰ dùng máy (có thao tác chuột/phím).
           Đủ N phút (20/30/45/60/90) → chuyển sang BREAK.
           Nếu bạn tự nghỉ ≥ 3 phút giữa chừng thì đếm lại từ đầu.
  BREAK  : 10 phút. Pet nhắc liên tục (mỗi ~90 giây, mỗi lần một mức gắt hơn)
           cho tới khi bạn rời máy. Thời gian rời máy được cộng dồn;
           đủ 10 phút = hoàn thành 1 Pomodoro (🍅) → tính "Focus streak" hôm nay.
           Chỉ khi bạn NGỒI MÁY phớt lờ tổng cộng 30 phút trong giờ nghỉ thì mới bỏ vòng
           này (tính là "bỏ qua giờ nghỉ"). Thời gian nghỉ thật không bao giờ bị hủy
           giữa chừng, và được cộng dồn qua nhiều lần rời máy.

Giọng điệu theo "Reminder Style" (friendly / stern / silly) và tính cách của pet.
Thống kê lưu trong screen_time.json (xem ScreenTimeTracker.record_pomodoro).

API cũ được giữ nguyên để main.py / settings_window.py / tray.py không phải đổi:
    ReminderSystem(pet_ref, interval_minutes) · set_interval(minutes) · check() · _interval
"""
import time, random

try:
    import alert_sound
except Exception:                       # pragma: no cover
    alert_sound = None

FOCUS_CHOICES = (0, 20, 30, 45, 60, 90)       # 0 = Off

BREAK_MINUTES   = 10        # thời gian nghỉ cần đạt
AWAY_IDLE_SEC   = 30        # không thao tác ≥30s => coi là đã rời máy (đang nghỉ)
ACTIVE_IDLE_SEC = 60        # thao tác trong 60s gần nhất => đang làm việc
RESET_IDLE_SEC  = 180       # tự nghỉ ≥3 phút khi đang FOCUS => đếm lại giờ làm
NAG_EVERY_SEC   = 90        # khoảng cách giữa 2 lần nhắc khi vẫn ngồi máy
BREAK_GIVEUP    = 30 * 60   # tổng 30 phút NGỒI MÁY (phớt lờ) trong giờ nghỉ => bỏ vòng này
POLL_SEC        = 1.0       # xử lý 1 lần/giây (check() được gọi mỗi tick ~16ms)
SUSPEND_GAP_SEC = 30.0      # giữa 2 lần xử lý cách nhau > 30 s = máy vừa NGỦ/ngủ đông/khoá
MAX_AWAY_GAP    = 12 * 3600 # chặn trên cho khoảng trống (phòng đồng hồ hệ thống bị chỉnh)

# Placeholder: {n}=phút làm việc  {b}=phút nghỉ  {left}=phút nghỉ còn thiếu
#              {k}=Pomodoro hôm nay  {who}=cách gọi người dùng theo loại pet
MESSAGES = {
    "friendly": {
        "start": ["{n} min of great focus! Take a {b}-min break 🧘",
                  "You've earned a break! {b} min away from the screen 💧",
                  "Time to rest your eyes and stretch — {b} minutes! 🌿"],
        "nag": [
            ["Psst… still here? Your {b}-min break is waiting 🐾",
             "Just a gentle reminder: step away for a bit 💧"],
            ["Please stand up, {who}. {left} more min of rest 🧘",
             "Your eyes need a rest — {left} min to go 👀"],
            ["I'm worried about you! Leave the screen for {left} min 🥺",
             "Break first, work later. {left} min, please! 🙏"],
        ],
        "done":   ["Pomodoro #{k} complete! 🍅 Welcome back!",
                   "Fully rested! That's {k} 🍅 today — nice!"],
        "giveup": ["No break this time... let's try again next round 🐾"],
    },
    "stern": {
        "start": ["Focus block over. Stand up. {b} minutes.",
                  "{n} minutes done. Break. Not optional.",
                  "Stop. Hands off the keyboard for {b} minutes."],
        "nag": [
            ["I said break. Step away.",
             "The work will still be here in {b} minutes."],
            ["Leave the keyboard. {left} minutes remaining.",
             "Ignoring me, {who}? {left} min."],
            ["Last warning. Get up. NOW.",
             "Do I have to unplug the monitor? {left} min!"],
        ],
        "done":   ["Break complete. Pomodoro #{k}. Back to work.",
                   "Good. {k} 🍅 today. Don't slack."],
        "giveup": ["You skipped your break. We will discuss this."],
    },
    "silly": {
        "start": ["BEEP BOOP: {who} overheating! 🔥 Cool down for {b} min!",
                  "The keyboard is lava now 🌋 — {b} minutes!",
                  "Your chair misses you. Wait, no. LEAVE! 🪑 ({b} min)"],
        "nag": [
            ["Hello? Earth to {who}? Break time!! 🌍",
             "My tail says: stand up! 🐾"],
            ["I'm going to do a dramatic faint if you stay ({left} min) 🎭",
             "Pixel-powered pleading: please get up ({left} min) 🥺"],
            ["I WILL SING. LOUDLY. UNTIL YOU LEAVE. 🎤 ({left} min)",
             "Plot twist: the break is mandatory ({left} min) 🎬"],
        ],
        "done":   ["Pomodoro #{k}! 🍅 You legend!",
                   "Rested! {k} 🍅 today. Tomato sauce unlocked!"],
        "giveup": ["You ignored the break. Tomatoes are sad 🍅😢"],
    },
}

WHO = {"dog": "hooman", "cat": "human", "dragon": "mortal"}

# Tính cách của pet thêm "gia vị" cho lời nhắc (không áp dụng cho style stern)
PERSONALITY_TAIL = {
    "playful": " Then let's play! 🎾",
    "lazy":    " I'll nap too... 😴",
    "curious": " Go see something new! 👀",
    "loyal":   " I'll wait right here 🐾",
}


class ReminderSystem:
    def __init__(self, pet_ref, interval_minutes: int = 45,
                 style: str = None, idle_fn=None, clock=None, wall=None):
        self._pet      = pet_ref
        self._clock    = clock or time.monotonic
        self._wall     = wall or time.time                 # đồng hồ treo tường (đi tiếp cả khi máy ngủ)
        self._idle_fn  = idle_fn
        self._style    = self._valid_style(style or self._style_from_config())
        self._interval = interval_minutes * 60      # giữ tên cũ: số GIÂY của 1 focus block
        self._enabled  = interval_minutes > 0
        self._reset_cycle()

    # ── Cấu hình ─────────────────────────────────────────────────────────

    @staticmethod
    def _valid_style(style) -> str:
        return style if style in MESSAGES else "friendly"

    @staticmethod
    def _style_from_config() -> str:
        try:
            import config_manager
            return config_manager.load().get("reminder_style", "friendly")
        except Exception:
            return "friendly"

    @property
    def style(self) -> str:
        return self._style

    def set_style(self, style: str):
        self._style = self._valid_style(style)

    def set_interval(self, minutes: int):
        """Đổi độ dài FOCUS (phút). 0 = tắt. Bắt đầu lại một vòng mới."""
        self._interval = minutes * 60
        self._enabled  = minutes > 0
        self._reset_cycle()

    def _reset_cycle(self):
        self._state        = "focus"          # "focus" | "break"
        self._active_sec   = 0.0              # thời gian làm việc đã tích lũy
        self._rest_sec     = 0.0              # thời gian rời máy trong giờ nghỉ (cộng dồn)
        self._ignored_sec  = 0.0              # thời gian vẫn ngồi máy trong giờ nghỉ
        self._break_start  = 0.0
        self._last_nag     = 0.0
        self._nag_count    = 0
        self._pending_msg  = None             # lời chào khi người dùng quay lại
        self._last_poll    = self._clock()
        self._last_wall    = self._wall()

    # ── Trạng thái (cho Settings) ────────────────────────────────────────

    def status(self) -> dict:
        return {
            "enabled":    self._enabled,
            "state":      self._state,
            "focus_goal": self._interval // 60,
            "focus_min":  int(self._active_sec // 60),
            "break_goal": BREAK_MINUTES,
            "rest_min":   int(self._rest_sec // 60),
            "style":      self._style,
        }

    # ── Vòng lặp chính ───────────────────────────────────────────────────

    def _idle(self) -> float:
        try:
            if self._idle_fn:
                return float(self._idle_fn())
            from day_night import get_idle_seconds
            return float(get_idle_seconds())
        except Exception:
            return 0.0

    def check(self):
        """Gọi mỗi tick. Trả về lời nhắc (str) hoặc None."""
        if not self._enabled:
            return None
        now  = self._clock()
        wall = self._wall()
        if now - self._last_poll < POLL_SEC:
            return None
        # Khoảng trống giữa 2 lần xử lý. Lấy lớn hơn của đồng hồ đơn điệu và đồng hồ treo
        # tường vì tuỳ máy, đồng hồ đơn điệu có thể KHÔNG chạy trong lúc ngủ.
        gap = min(max(now - self._last_poll, wall - self._last_wall), MAX_AWAY_GAP)
        self._last_poll, self._last_wall = now, wall
        idle = self._idle()

        if gap > SUSPEND_GAP_SEC:
            # Máy vừa ngủ/ngủ đông/khoá: lúc đó chắc chắn bạn KHÔNG ngồi làm việc.
            # Bản cũ cắt khoảng trống còn 5 s (để không tính là làm việc) nên cũng làm
            # MẤT luôn thời gian nghỉ khi đang trong giờ nghỉ.
            if self._on_resume(gap):
                return None                       # vừa đủ giờ nghỉ; lời chúc hiện khi bạn thao tác
            dt = POLL_SEC
        else:
            dt = min(gap, 5.0)

        if self._state == "focus":
            return self._tick_focus(dt, idle, now)
        return self._tick_break(dt, idle, now)

    def _on_resume(self, gap: float) -> bool:
        """Xử lý khoảng trống `gap` giây do máy ngủ. Trả về True nếu hoàn thành Pomodoro."""
        if self._state == "break":
            self._rest_sec += gap                 # máy ngủ = đang nghỉ thật, cộng dồn
            if self._rest_sec >= BREAK_MINUTES * 60:
                self._finish_pomodoro()
                return True
        elif gap >= RESET_IDLE_SEC:               # đang FOCUS mà ngủ ≥ 3 phút = tự nghỉ
            self._active_sec = 0.0                # (như tự rời máy ≥ 3 phút: đếm lại focus)
        return False

    def _tick_focus(self, dt, idle, now):
        # Lời chào khi người dùng quay lại sau một Pomodoro hoàn chỉnh
        if self._pending_msg and idle < 5:
            msg, self._pending_msg = self._pending_msg, None
            return msg

        if idle >= RESET_IDLE_SEC:                 # đã tự nghỉ đủ lâu
            self._active_sec = 0.0
            return None
        if idle < ACTIVE_IDLE_SEC:
            self._active_sec += dt

        if self._active_sec >= self._interval:
            if self._in_meeting():                 # đang họp: đợi, không làm phiền
                return None
            return self._start_break(now)
        return None

    def _start_break(self, now):
        self._state       = "break"
        self._break_start = now
        self._last_nag    = now
        self._nag_count   = 0
        self._rest_sec    = 0.0
        self._ignored_sec = 0.0
        msg = self._compose("start")
        self._alert("break", msg)
        return msg

    def _tick_break(self, dt, idle, now):
        if idle >= AWAY_IDLE_SEC:                  # đang nghỉ thật
            self._rest_sec += dt                   # cộng dồn, KHÔNG bị hủy giữa chừng
            if self._rest_sec >= BREAK_MINUTES * 60:
                return self._finish_pomodoro()
            return None

        # Vẫn ngồi máy: tính thời gian phớt lờ rồi nhắc tiếp.
        # (Bản trước hủy giờ nghỉ khi đủ 30 phút KỂ TỪ LÚC BẮT ĐẦU NGHỈ, kể cả khi bạn
        #  đang nghỉ thật => mất phần nghỉ đã làm.)
        self._ignored_sec += dt
        if self._ignored_sec >= BREAK_GIVEUP:
            return self._give_up()
        if now - self._last_nag >= NAG_EVERY_SEC:
            self._last_nag = now
            self._nag_count += 1
            msg = self._compose("nag")
            if self._nag_count >= 2:
                self._alert("nag", None)
            return msg
        return None

    def _finish_pomodoro(self):
        focus_min = self._interval / 60.0
        try:
            self._pet.screen_time.record_pomodoro(focus_min)
        except Exception:
            pass
        self._state, self._active_sec, self._rest_sec = "focus", 0.0, 0.0
        self._ignored_sec = 0.0
        self._pending_msg = self._compose("done")
        self._alert("done", None)
        try:
            self._pet.notify.show("Pomodoro complete 🍅", self._pending_msg)
        except Exception:
            pass
        return None                                # hiện khi người dùng quay lại

    def _give_up(self):
        try:
            self._pet.screen_time.record_skipped_break()
        except Exception:
            pass
        self._state, self._active_sec, self._rest_sec = "focus", 0.0, 0.0
        self._ignored_sec = 0.0
        return self._compose("giveup")

    # ── Lời thoại ────────────────────────────────────────────────────────

    def _in_meeting(self) -> bool:
        try:
            return bool(self._pet.app_watch.get().in_meeting)
        except Exception:
            return False

    def _pomodoros_today(self) -> int:
        try:
            return int(self._pet.screen_time.pomodoros_today)
        except Exception:
            return 0

    def _compose(self, phase: str) -> str:
        pool = MESSAGES[self._style]
        if phase == "nag":
            level = min(max(self._nag_count - 1, 0), 2)
            tmpl  = random.choice(pool["nag"][level])
        else:
            tmpl = random.choice(pool[phase])

        pet_type = getattr(self._pet, "pet_type", "dog")
        left = max(1, int(round((BREAK_MINUTES * 60 - self._rest_sec) / 60.0)))
        msg = tmpl.format(
            n=int(self._interval // 60), b=BREAK_MINUTES, left=left,
            k=self._pomodoros_today(), who=WHO.get(pet_type, "friend"))

        personality = ""
        try:
            personality = self._pet.state.personality
        except Exception:
            pass
        if personality == "hyper":
            msg = msg.upper()
        elif phase in ("start", "done") and self._style != "stern":
            msg += PERSONALITY_TAIL.get(personality, "")
        return msg

    def _alert(self, kind: str, msg):
        if alert_sound:
            try:
                alert_sound.play(kind)
            except Exception:
                pass
        if kind == "break" and msg:               # toast: thấy được cả khi pet bị che
            try:
                self._pet.notify.reminder(msg)
            except Exception:
                pass

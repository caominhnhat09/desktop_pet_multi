"""
command_handler.py — Executes classified commands.
Uses Spotify Web API when configured, falls back to media keys.
"""

import subprocess, webbrowser, urllib.parse, sys, os, re

class CommandHandler:
    def __init__(self, pet_ref):
        self._pet    = pet_ref
        self._win32  = sys.platform == "win32"
        self._spotify = None
        # Lazy-load Spotify API
        threading.Thread(target=self._init_spotify, daemon=True).start()

    def _init_spotify(self):
        try:
            from spotify_api import SpotifyAPI
            self._spotify = SpotifyAPI()
        except Exception as e:
            print(f"[cmd] Spotify API init: {e}")

    def execute(self, classified: dict) -> str:
        action  = classified.get("action", "unknown")
        target  = classified.get("target", "")
        params  = classified.get("params", {})
        handler = {
            "music":   self._music,
            "app":     self._open_app,
            "timer":   self._set_timer,
            "search":  self._search,
            "feed":    self._feed,
            "trick":   self._trick,
            "volume":  self._volume,
            "unknown": self._unknown,
        }.get(action, self._unknown)
        try:
            return handler(target, params)
        except Exception as e:
            print(f"[cmd] {action} error: {e}")
            return "Couldn't do that! 😅"

    # ── Music ─────────────────────────────────────────────────────────────

    def _music(self, target: str, params: dict) -> str:
        sp = self._spotify

        # Use Spotify Web API if available
        if sp and sp.is_available:
            if not target or target == "resume":
                return sp.resume()
            elif target == "pause":
                return sp.pause()
            elif target == "next":
                return sp.skip()
            elif target == "prev":
                return sp.previous()
            else:
                return sp.play(target)

        # Fallback: media keys + Spotify URI
        if not target or target == "pause":
            self._media_key("play_pause"); return "Paused! 🎵"
        elif target == "next":
            self._media_key("next_track"); return "Skipped! ⏭️"
        elif target == "prev":
            self._media_key("prev_track"); return "Going back! ⏮️"
        else:
            q = urllib.parse.quote(target)
            try:
                subprocess.Popen(f"start spotify:search:{q}", shell=True)
                return f"Searching: {target} 🎵"
            except Exception:
                webbrowser.open(f"https://open.spotify.com/search/{q}")
                return f"Searching: {target} 🎶"

    def _volume(self, target: str, params: dict) -> str:
        """Âm lượng. Bản cũ chỉ bấm phím tăng/giảm đúng 3 lần (≈6%, Windows đổi 2%/lần),
        không làm gì khi 40-60 và LUÔN báo "adjusted" -> trông như không có tác dụng.
        Giờ đặt đúng mức bạn nói (xem system_volume.py)."""
        sp = self._spotify
        if sp and sp.is_available and "level" in params:
            return sp.set_volume(int(params["level"]))        # có Spotify API: như cũ

        import system_volume as sv
        if not sv.SUPPORTED:
            return "Volume control works on Windows only 🔇"

        if "mute" in params:
            state, how = sv.set_mute(bool(params["mute"]))
            if how == "keys":
                return "Mute toggled 🔇"
            return "Muted 🔇" if state else "Unmuted 🔊"

        if "level" in params:
            level, how = sv.set_level(params["level"])
        elif "delta" in params:
            level, how = sv.change(params["delta"])
        else:                                                  # chỉ nói "volume"
            level, how = sv.get_level(), "exact"
            if level is None:
                return "Say a number, like 'volume 60' 🔊"
            return f"Volume is at {level}% 🔊"

        if level is None:                                      # chỉ biết đã bấm phím
            return "Volume " + ("up" if params.get("delta", 0) > 0 else "down") + " 🔊"
        approx = "~" if how == "keys" else ""
        return f"Volume {approx}{level}% " + ("🔇" if level == 0 else "🔊")

    def _media_key(self, key: str):
        if not self._win32: return
        import ctypes
        vk = {"play_pause":0xB3,"next_track":0xB0,"prev_track":0xB1,
              "stop":0xB2,"volume_up":0xAF,"volume_down":0xAE,"volume_mute":0xAD}.get(key)
        if vk:
            ctypes.windll.user32.keybd_event(vk,0,0,0)
            ctypes.windll.user32.keybd_event(vk,0,2,0)

    # ── Apps ─────────────────────────────────────────────────────────────

    APP_MAP = {
        "spotify":"spotify","chrome":"chrome","google chrome":"chrome",
        "firefox":"firefox","edge":"msedge","vs code":"code","vscode":"code",
        "notepad":"notepad","calculator":"calc","explorer":"explorer",
        "task manager":"taskmgr",
        "terminal":"cmd","powershell":"powershell", "command line":"cmd",
        "word":"winword","microsoft word":"winword",
        "excel":"excel","microsoft excel":"excel",
        "powerpoint":"powerpnt","microsoft powerpoint":"powerpnt",
         "paint":"mspaint",
    }

    WEB_MAP = {
        "youtube":         "https://www.youtube.com",
        "gmail":           "https://mail.google.com",
        "g mail":          "https://mail.google.com",
        "google mail":     "https://mail.google.com",
        "email":           "https://mail.google.com",
        "google drive":    "https://drive.google.com",
        "google calendar": "https://calendar.google.com",
        "calendar":        "https://calendar.google.com",
        "git hub":          "https://github.com",
        "github":          "https://github.com",
        "git":          "https://github.com",
    }

    # App tự đăng ký giao thức riêng: mở bằng URI đáng tin hơn gọi tên .exe
    PROTOCOL_MAP = {
        "slack":   "slack://",
        "spotify": "spotify:",
    }

    # Đường dẫn cài đặt phổ biến, dùng khi Windows không tìm thấy qua App Paths
    _FALLBACK_PATHS = {
        "chrome": [
            r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
            r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
            r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
        ],
        "spotify": [r"%AppData%\Spotify\Spotify.exe"],
    }

    def _open_app(self, target: str, params: dict) -> str:
        name = target.lower().strip()
        if not name:
            return "Open what? 🤔"

        # 1) Trang web
        url = self.WEB_MAP.get(name)
        if url:
            webbrowser.open(url)
            print(f"[cmd] opened website {url}")
            return f"Opening {target}! 🌐"

        exe = self.APP_MAP.get(name, name)

        if self._win32:
            # 2) Giao thức riêng ( slack://, spotify:)
            proto = self.PROTOCOL_MAP.get(exe)
            if proto:
                try:
                    os.startfile(proto)
                    print(f"[cmd] launched {exe} via {proto}")
                    return f"Opening {target}! 🚀"
                except OSError as e:
                    print(f"[cmd] {proto} failed: {e}")


        # 3) Tên chương trình / đường dẫn cài đặt
        if self._launch(exe):
            return f"Opening {target}! 🚀"
        print(f"[cmd] could not launch '{exe}'")
        return f"Can't find {target} 🤔"

    def _launch(self, exe: str) -> bool:
        if not self._win32:
            try:
                subprocess.Popen([exe]); return True
            except Exception:
                return False

        # 1) ShellExecute: tìm qua registry "App Paths" như hộp thoại Win+R
        try:
            os.startfile(exe)
            print(f"[cmd] launched '{exe}' via ShellExecute")
            return True
        except OSError:
            pass

        # 2) Đường dẫn cài đặt phổ biến
        for p in self._FALLBACK_PATHS.get(exe, []):
            p = os.path.expandvars(p)
            if os.path.exists(p):
                try:
                    os.startfile(p)
                    print(f"[cmd] launched {p}")
                    return True
                except OSError:
                    pass

        # 3) Chương trình nằm trong PATH (code.cmd, v.v.)
        import shutil
        found = shutil.which(exe)
        if found:
            try:
                subprocess.Popen([found], shell=False)
                print(f"[cmd] launched {found}")
                return True
            except OSError:
                try:
                    subprocess.Popen(f'"{found}"', shell=True)
                    return True
                except Exception:
                    pass
        return False

    # ── Timer / search / feed / trick ─────────────────────────────────────

    def _set_timer(self, target: str, params: dict) -> str:
        # Bản cũ gọi set_reminder(), tức là ĐỔI chu kỳ nhắc nghỉ (và ghi đè cài đặt
        # Reminders), chứ không hề hẹn giờ. Giờ là hẹn giờ một lần thật sự.
        if params.get("cancel"):
            n = self._pet.cancel_timers()
            return "Timer cancelled! ⏹️" if n else "No timer is running 🤷"
        seconds = params.get("seconds")
        if seconds is None:
            seconds = int(params.get("minutes", 5)) * 60
        return self._pet.set_timer(seconds)

    def _search(self, target: str, params: dict) -> str:
        if not target: return "Search for what? 🤔"
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(target)}")
        return f"Searching: {target} 🔍"

    def _feed(self, target: str, params: dict) -> str:
        self._pet.feed(); return ""

    def _trick(self, target: str, params: dict) -> str:
        # Kiểm tra theo bộ hoạt ảnh của CHÍNH pet đang chạy (bản cũ luôn dùng của chó
        # nên rồng/mèo nhận lệnh "roll", "flip"... mà không có hoạt ảnh nào để chơi).
        anims = getattr(self._pet, "_ANIMS", None)
        if anims is None:
            import sprite
            anims = sprite.ANIMATIONS
        if target and target != "random" and target in anims:
            self._pet.behavior.current_trick = target
            self._pet.behavior._queued_trick = target
        else:
            self._pet.do_trick()
        return ""

    def _unknown(self, target: str, params: dict) -> str:
        return "I'll try! 🐾"


import threading  # needed for _init_spotify
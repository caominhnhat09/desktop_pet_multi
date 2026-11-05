"""
alert_sound.py — Short reminder sounds. No external audio files needed.

Windows : winsound.Beep() plays a short melody through the sound card.
Other   : terminal bell (best effort), so the app never crashes on a missing sound.

Used by: hẹn giờ ("set timer 5 minutes") và chế độ Pomodoro (reminders.py).
play() luôn chạy ở luồng nền nên không làm đứng pet.
"""
import sys, threading

_WIN32 = sys.platform == "win32"
_lock  = threading.Lock()          # không cho 2 giai điệu chồng lên nhau

# (tần số Hz, thời gian ms)
PATTERNS = {
    "timer": [(988, 160), (1319, 160), (988, 160), (1319, 300),
              (0, 150),
              (988, 160), (1319, 160), (988, 160), (1319, 300)],   # ding-dong x2: hết giờ hẹn
    "break": [(660, 200), (880, 200), (1100, 400)],                  # bắt đầu giờ nghỉ
    "nag":   [(880, 150), (0, 80), (880, 150)],                      # nhắc nhở (vẫn ngồi máy)
    "done":  [(784, 140), (988, 140), (1319, 140), (1568, 380)],     # hoàn thành 1 Pomodoro
}


def _run(kind: str):
    seq = PATTERNS.get(kind, PATTERNS["timer"])
    with _lock:
        if _WIN32:
            try:
                import winsound, time
                for freq, ms in seq:
                    if freq <= 0:
                        time.sleep(ms / 1000.0)
                    else:
                        winsound.Beep(freq, ms)
                return
            except Exception:
                try:
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    return
                except Exception:
                    pass
        try:                                   # fallback: chuông terminal
            sys.stdout.write("\a")
            sys.stdout.flush()
        except Exception:
            pass


def play(kind: str = "timer", blocking: bool = False):
    """Phát âm báo. kind: 'timer' | 'break' | 'nag' | 'done'."""
    if blocking:
        _run(kind)
    else:
        threading.Thread(target=_run, args=(kind,), daemon=True).start()

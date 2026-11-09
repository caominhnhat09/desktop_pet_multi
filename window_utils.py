"""
window_utils.py — Tiện ích z-order cho các cửa sổ phụ (Settings, Memory, Achievements, Pet Status).

Mục tiêu: pet LUÔN nổi trên cùng, kể cả khi các cửa sổ này đang mở.
Trước đây mỗi cửa sổ tự đặt "-topmost" vĩnh viễn nên tranh vị trí trên cùng với pet
và che mất pet. Giờ các cửa sổ chỉ "nhảy lên trước" một lần khi mở rồi trở về
cửa sổ thường; pet (topmost) luôn ở trên chúng.
"""
import sys


def _drop_topmost(win):
    try:
        if win.winfo_exists():
            win.wm_attributes("-topmost", False)
    except Exception:
        pass


def bring_to_front_once(win, hold_ms: int = 350):
    """Đưa cửa sổ lên trước các app khác khi vừa mở, rồi thôi giữ topmost.

    Việc tắt topmost được hẹn bằng root.after (không phải win.after): lịch hẹn gắn
    với widget sẽ gây "invalid command name ..." nếu cửa sổ đóng trước khi tới hạn."""
    try:
        win.wm_attributes("-topmost", True)
        win.lift()
        win.nametowidget(".").after(hold_ms, lambda: _drop_topmost(win))
    except Exception:
        pass


def detach_owner(win):
    """Windows: nếu cửa sổ Tk đang bị cửa sổ pet "sở hữu" thì Windows luôn đặt nó
    TRÊN pet bất kể z-order. Gỡ quan hệ sở hữu đó. Trả về HWND chủ cũ (để ghi log)
    hoặc None nếu không có gì phải sửa."""
    if sys.platform != "win32":
        return None
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        win.update_idletasks()
        hwnd = user32.GetParent(win.winfo_id()) or win.winfo_id()
        user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
        user32.GetWindow.restype  = wintypes.HWND
        owner = user32.GetWindow(hwnd, 4)                 # GW_OWNER
        if not owner:
            return None
        setter = getattr(user32, "SetWindowLongPtrW", None) or user32.SetWindowLongW
        setter.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
        setter.restype  = ctypes.c_ssize_t
        setter(hwnd, -8, 0)                               # GWLP_HWNDPARENT = bỏ chủ sở hữu
        return owner
    except Exception:
        return None


def prepare(win, name: str = "window"):
    """Gọi ngay sau khi tạo cửa sổ phụ: gỡ sở hữu (nếu có) + nhảy lên trước một lần."""
    owner = detach_owner(win)
    if owner:
        print(f"[window] {name} was owned by another window (hwnd={owner}); detached "
              f"so the pet can stay above it")
    bring_to_front_once(win)

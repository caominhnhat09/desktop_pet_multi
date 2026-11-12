"""
system_volume.py — Điều khiển âm lượng HỆ THỐNG của Windows (loa chính).

Hai cách, tự chọn:
  1. pycaw (khuyên dùng: pip install pycaw comtypes): ĐẶT chính xác theo %, đọc được
     mức hiện tại, bật/tắt tiếng đúng trạng thái.
  2. Dự phòng (không cần thư viện): giả lập phím âm lượng. Mỗi lần bấm Windows đổi 2%,
     nên muốn đặt X% thì bấm "giảm" 50 lần cho về 0 rồi bấm "tăng" X/2 lần.
     Cách này chỉ ước lượng, không đọc được mức hiện tại và "mute" chỉ bật/tắt xen kẽ.

Mọi hàm trả về (mức %, phương pháp) với phương pháp là "exact" | "keys";
hoặc (None, None) nếu không hỗ trợ (không phải Windows).
"""
import sys, time

SUPPORTED = sys.platform == "win32"
STEP      = 2                 # mỗi lần bấm phím âm lượng của Windows đổi 2%

_VK_MUTE, _VK_DOWN, _VK_UP = 0xAD, 0xAE, 0xAF
_KEYEVENTF_EXTENDEDKEY, _KEYEVENTF_KEYUP = 0x1, 0x2


# ── Cách 1: pycaw / Core Audio ───────────────────────────────────────────

def _endpoint():
    """IAudioEndpointVolume của loa mặc định. Hỗ trợ cả pycaw mới và cũ."""
    from pycaw.pycaw import AudioUtilities
    dev = AudioUtilities.GetSpeakers()
    ep  = getattr(dev, "EndpointVolume", None)         # pycaw mới
    if ep is not None:
        return ep
    from ctypes import cast, POINTER                     # pycaw cũ
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import IAudioEndpointVolume
    iface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(iface, POINTER(IAudioEndpointVolume))


def _with_com(fn):
    """Chạy fn trong ngữ cảnh COM của luồng hiện tại (lệnh giọng nói chạy ở luồng nền)."""
    import comtypes
    comtypes.CoInitialize()
    try:
        return fn()
    finally:
        try:
            comtypes.CoUninitialize()
        except Exception:
            pass


def exact_available() -> bool:
    if not SUPPORTED:
        return False
    try:
        _with_com(lambda: _endpoint().GetMasterVolumeLevelScalar())
        return True
    except Exception:
        return False


# ── Cách 2: giả lập phím ─────────────────────────────────────────────────

def _press(vk: int, times: int = 1, gap: float = 0.008):
    import ctypes
    user32 = ctypes.windll.user32
    for _ in range(max(0, times)):
        user32.keybd_event(vk, 0, _KEYEVENTF_EXTENDEDKEY, 0)
        user32.keybd_event(vk, 0, _KEYEVENTF_EXTENDEDKEY | _KEYEVENTF_KEYUP, 0)
        time.sleep(gap)


# ── API công khai ────────────────────────────────────────────────────────

def _clamp(level) -> int:
    return max(0, min(100, int(round(level))))


def get_level():
    """Mức hiện tại (0-100) hoặc None nếu không đọc được (cách dự phòng)."""
    if not SUPPORTED:
        return None
    try:
        return _with_com(lambda: _clamp(_endpoint().GetMasterVolumeLevelScalar() * 100))
    except Exception:
        return None


def set_level(level):
    level = _clamp(level)
    if not SUPPORTED:
        return None, None
    try:
        def _do():
            ep = _endpoint()
            ep.SetMute(0, None)                       # đặt mức > 0 thì phải bỏ tắt tiếng
            ep.SetMasterVolumeLevelScalar(level / 100.0, None)
            return _clamp(ep.GetMasterVolumeLevelScalar() * 100)
        return _with_com(_do), "exact"
    except Exception:
        pass
    _press(_VK_DOWN, 100 // STEP)                      # về 0 (50 lần)
    _press(_VK_UP, round(level / STEP))                # rồi lên đúng mức
    return level, "keys"


def change(delta):
    """Tăng/giảm delta % so với mức hiện tại."""
    if not SUPPORTED:
        return None, None
    try:
        def _do():
            ep  = _endpoint()
            cur = ep.GetMasterVolumeLevelScalar() * 100
            new = _clamp(cur + delta)
            if new > 0:
                ep.SetMute(0, None)
            ep.SetMasterVolumeLevelScalar(new / 100.0, None)
            return _clamp(ep.GetMasterVolumeLevelScalar() * 100)
        return _with_com(_do), "exact"
    except Exception:
        pass
    _press(_VK_UP if delta > 0 else _VK_DOWN, max(1, round(abs(delta) / STEP)))
    return None, "keys"                                # không biết mức hiện tại


def set_mute(muted: bool):
    """Tắt/bật tiếng. Trả về (muted, phương pháp); muted=None khi chỉ bật/tắt xen kẽ."""
    if not SUPPORTED:
        return None, None
    try:
        def _do():
            ep = _endpoint()
            ep.SetMute(1 if muted else 0, None)
            return bool(ep.GetMute())
        return _with_com(_do), "exact"
    except Exception:
        pass
    _press(_VK_MUTE, 1)                                # chỉ bật/tắt xen kẽ
    return None, "keys"

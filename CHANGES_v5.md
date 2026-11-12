# Đợt sửa thứ 5 (nền: phương án B)

Chép đè các file trong thư mục này vào project. **File mới:** `system_volume.py`. Gồm 9 file:
`main.py`, `settings_window.py`, `config_manager.py`, `tray.py`, `llm_brain.py`, `command_handler.py`, `system_volume.py`, `requirements.txt`, `README.md`.

> **Lưu ý về `command_handler.py` và `llm_brain.py`:** bạn đã tự sửa hai file này. Tôi không có bản mới nhất của bạn; tôi đã làm trên bản trong zip trước và
> thêm lại dòng `"command line":"cmd"` mà tôi thấy trong ảnh của bạn. Nếu bạn còn chỉnh gì khác thì hãy so sánh trước khi chép đè
> (phần tôi sửa nằm ở `_volume()` trong `command_handler.py` và `classify_command()` + hàm `_parse_volume()` trong `llm_brain.py`).
> Sau khi chép đè, cài thêm: `pip install pycaw comtypes` (khuyến nghị, xem mục 1).

## 1. Lệnh volume chỉnh âm lượng máy tính
**Nguyên nhân lệnh cũ không có tác dụng**: `volume 80` chỉ bấm phím "tăng âm lượng" đúng 3 lần (mỗi lần Windows đổi ~2% ⇒ ~6%), không làm gì khi mức 40–60
(và chỉ nói `volume` thì mặc định 50 ⇒ không làm gì), và **luôn báo** "Volume adjusted!". Không có Spotify API thì chỉ còn đường phím này.

**Giờ** (`system_volume.py` mới), không cần Spotify:

| Câu nói | Kết quả |
|---|---|
| `volume 70` | Đặt đúng 70% (0–100; tự bỏ tắt tiếng nếu mức > 0) |
| `volume up` / `volume down`, `louder` / `quieter` | ±10% |
| `volume max` | 100% |
| `volume` | Báo mức hiện tại |
| `mute` / `unmute` | Tắt / bật tiếng máy (trước đây `mute` lại là Play/Pause) |

* **Có `pycaw`** (`pip install pycaw comtypes`): đặt chính xác, đọc được mức hiện tại, mute đúng trạng thái. Hỗ trợ cả pycaw bản mới và cũ.
* **Không có `pycaw`**: tự rơi về giả lập phím, đặt X% bằng cách bấm "giảm" 50 lần về 0 rồi "tăng" X/2 lần. Chỉ ước lượng (hiện `~70%`), không đọc được mức hiện tại, `mute` chỉ bật/tắt xen kẽ.
* Nếu bạn **có Spotify API**: `volume N` vẫn chỉnh âm lượng của Spotify như cũ; `up/down/mute/volume` luôn dùng âm lượng máy.
* Thông báo trong bong bóng phản ánh kết quả thật (`Volume 70% 🔊`, `Muted 🔇`...).
Không thể kiểm thử trên Windows thật ở đây: logic được chạy với pycaw giả (cả hai kiểu API) và `keybd_event` giả; cần bạn xác nhận tiếng thật.

## 2. `config.json` lệch với trạng thái đang chạy
**Nguyên nhân**: file chỉ được ghi **khi thoát** (và vài chỗ lẻ), nên mọi thay đổi giữa chừng không có trong file:
* phụ kiện (`set_accessory` không ghi), tốc độ (thanh trượt chỉ gán vào pet), thời gian Pomodoro (`set_reminder` chỉ gán), màu, HUD, đổi pet (chỉ ghi khi thoát);
* `wake_words` **không bao giờ được ghi**: luôn là giá trị mặc định của chó trong `config_manager` (không ai đọc khóa này nên pet vẫn nhận đúng wake word theo pet; chỉ file bị sai).

**Sửa**
* `main.py`: `_config_snapshot()` + `save_config()` ghi cấu hình **hiện tại** (kèm `wake_words` của pet hiện tại). Được gọi ngay khi: đổi phụ kiện, màu, pet, HUD, thời gian Pomodoro, Save & Close, Reset to Defaults; thả thanh tốc độ (không ghi lúc đang kéo); chọn tốc độ từ menu khay (`tray.py`);
  3 giây sau khi khởi động (đồng bộ ngay từ đầu); mỗi 60 giây cùng lúc lưu trạng thái (`last_x`, `last_y` sát vị trí thật); và khi thoát.
* **Lỗi nặng hơn tôi tìm thấy khi làm việc này**: `config_manager.save()` ghi đè **cả file** bằng `{mặc định + cfg}` nên mọi khóa khác bị xóa mỗi lần pet lưu, ví dụ
  `spotify_client_id` / `spotify_client_secret` (do `spotify_api.py` đọc từ chính file này). Giờ `save()` **giữ nguyên các khóa lạ** và ghi **nguyên tử** (file tạm rồi thay thế) nên file không bao giờ bị cụt khi máy tắt giữa chừng; file hỏng thì được ghi lại hợp lệ.
  Nếu bạn đã từng thêm thông tin Spotify vào `config.json` thì có thể nó đã bị xóa ở lần thoát trước; hãy thêm lại.
* `last_x`/`last_y` vẫn chỉ "sát" chứ không khớp từng giây (pet di chuyển liên tục), tối đa lệch ~1 phút.

## 3. Ẩn "Follow Sensitivity" và "AFK Sleep Threshold"
Tab Behaviour chỉ còn **Animation Speed**. Hai giá trị vẫn được đọc từ `config.json` (`follow_speed`, `afk_sleep_sec`) và vẫn có tác dụng, chỉ không chỉnh trên giao diện.
Đã gỡ mọi tham chiếu tới hai thanh trượt trong `Save & Close` và `Reset to Defaults` (nếu để sót sẽ gây `AttributeError`).

## 4. README
`README.md` viết lại theo **cấu trúc của README gốc** (tiêu đề + huy hiệu, What is, Features, Installation, Usage + Voice Commands, Architecture, Roadmap, Contributing, Credits, License),
bằng tiếng Anh như bản gốc, cho đúng dự án hiện tại (phương án B). Đã đối chiếu với code: file trong sơ đồ kiến trúc (36/36 tồn tại, không thiếu file nào), wake words, các lệnh voice, số animation (30/24/30), 51 thành tựu, các tab của Settings và Memory Dashboard.
Khác bản gốc: bỏ Weather; thêm Pomodoro, hẹn giờ, volume, mục Configuration; sửa các chỗ README gốc ghi sai (menu chuột phải **không có** "Type Command" — nó nằm ở menu khay; `requirements.txt` thật; 24/28/26 animation → 30/24/30; "40+" → 51);
Roadmap: Productivity Guardian chuyển sang "Shipped", Evolution/Dream Journal không còn trong phạm vi.
**Hai điểm tôi chủ ý**: (a) nút "Download v1.0" ở đầu đổi thành "Build the .exe", vì bản phát hành trên GitHub gốc là bản chưa có các thay đổi này; (b) tên tác giả gốc `chron303` và các liên kết GitHub gốc được giữ nguyên
(ghi "Based on Desktop Pet by chron303"); nếu bạn có repo riêng thì hãy thay các liên kết đó.

## Đã kiểm thử gì — và chưa
Chạy thật: đồng bộ config với đúng kịch bản của bạn (đổi phụ kiện → file đổi; kéo tốc độ 3.0 → file 3.0; Pomodoro 60 → file 60; dragon → cat → dragon → `wake_words` đổi theo từng pet; khóa Spotify còn nguyên; file hỏng / chưa có file); Settings sau khi ẩn hai mục (Save & Close, Reset, thanh tốc độ ghi khi thả); lệnh volume (cả hai kiểu pycaw, đường phím, không phải Windows, có Spotify API); biên dịch và kiểm tra tĩnh phương án B (36 file).
**Chưa chạy trên Windows + Tk thật**: cần bạn xác nhận (1) `volume 50` đặt đúng thanh âm lượng Windows (cần `pip install pycaw comtypes` để chính xác), (2) `config.json` đổi ngay khi bạn chọn phụ kiện/tốc độ/Pomodoro, (3) tab Behaviour trông ổn.

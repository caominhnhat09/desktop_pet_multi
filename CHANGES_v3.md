# Đợt sửa thứ 3 — cửa sổ Pet Settings (4 ảnh)

Chọn **một** thư mục (A hoặc B, giống bản v2) và chép đè các file trong đó vào project.
Mỗi thư mục gồm **toàn bộ** file đã đổi từ bản gốc (kể cả các sửa của v2), nên chỉ cần chép đè.
File mới: `window_utils.py`.

## Hình 1 — Behaviour Toggles
Đã xóa mục **Behaviour Toggles** cùng 2 ô tick ("Avoid open windows while walking", "Night mode tint after 9pm").
Kiểm tra: hai biến của 2 ô này (`_window_avoid_var`, `_night_mode_var`) **không được đọc ở bất cứ đâu** trong project, nên chúng vốn không điều khiển chức năng nào → xóa không ảnh hưởng gì khác.

## Hình 2 — tab Voice chỉ để xem
* Ô Wake Words: `state="disabled"` (không gõ, không chọn được). Hiển thị wake words **thật** của pet hiện tại.
* 3 nút engine: `disabled`. Nút được chọn là engine **đang dùng thật**: Google khi có SpeechRecognition, Whisper khi chỉ có Whisper.
  (Trước đây nút radio này **không điều khiển gì**: `voice.py` tự chọn Google rồi rơi về Sphinx khi mất mạng.)
* "Voice Status" giữ nguyên, chỉ là nhãn.
* Bỏ đoạn lưu wake words trong `Save & Close`: đoạn đó có thể ghi đè wake words của pet mới bằng wake words cũ trong ô nhập.

## Hình 3 — Refresh và Reset to Defaults
**Nguyên nhân "không có gì xảy ra"**
* `_reset()` cũ chỉ gán giá trị cho biến giao diện: không áp dụng vào pet, không đổi nút phong cách nhắc (Reminder Style), không cập nhật dòng trạng thái / biểu đồ.
* `Refresh` chỉ tính lại biểu đồ; nếu dữ liệu không đổi thì nhìn y như cũ, và không có phản hồi nào.

**Sửa**
* **Reset to Defaults** nay: về mặc định **và áp dụng ngay**: Pomodoro 45 phút, style Friendly (được lưu vào config), tốc độ animation 1.0, follow 0.15, AFK 120 s, màu Default, tính cách playful, tên "Buddy" (tên chỉ áp dụng khi bấm Save & Close như trước). Dòng trạng thái cập nhật ngay.
* **Refresh** nay đồng bộ lại các nút chọn với trạng thái **thật** của pet (độ dài focus, style) rồi cập nhật tiến độ + biểu đồ.
* Cả hai hiện dòng thông báo xanh ở chân cửa sổ, tự tắt sau 3 giây: `✓ Refreshed 21:35:12` / `✓ Defaults restored`.

## Hình 4 — pet bị cửa sổ Settings che
**Nguyên nhân**: Settings tự đặt `-topmost` **vĩnh viễn**, nên tranh vị trí trên cùng với pet (pet cũng topmost) và che mất pet.
**Sửa** (`window_utils.py`, dùng chung):
* `bring_to_front_once`: cửa sổ chỉ **nhảy lên trước một lần** (topmost 350 ms) để không bị mở ra phía sau app khác, rồi trở về cửa sổ thường. Pet (topmost) luôn nằm trên.
  Việc tắt topmost được hẹn bằng `root.after` (không phải `win.after`) để không gây lỗi "invalid command name" nếu đóng cửa sổ sớm.
* `detach_owner`: nếu Windows đang coi cửa sổ là "thuộc sở hữu" của cửa sổ pet (khi đó nó luôn nằm trên pet bất kể z-order) thì gỡ quan hệ này. Chỉ in log nếu thực sự phải gỡ:
  `[window] Settings was owned by another window ...`. **Tôi không biết chắc Windows có coi nó như vậy không**, nên phần này là phòng thủ.
* Áp dụng cho: **Settings, Memory Dashboard, Achievements, Pet Status**.
* Giữ nguyên `-topmost` ở: hộp thoại Command (nhỏ, modal, cần nằm trên để nhập), thông báo toast, bong bóng chat, HUD, hiệu ứng hạt, màn hình chọn pet lúc khởi động.

## Đã kiểm thử gì — và chưa
* Chạy thật với Tk giả ghi lại thuộc tính từng widget: không còn Behaviour Toggles / checkbox; Entry và 3 radio của Voice đều `disabled`, không có nút thao tác; engine hiển thị đúng theo thư viện có sẵn;
  Refresh đồng bộ lại radio khi pet đổi ngầm sang 30 phút + silly; Reset áp dụng đúng 8 giá trị vào pet và lưu style; thông báo chân cửa sổ.
* `window_utils`: topmost bật rồi tắt sau 350 ms, đóng sớm không lỗi; `detach_owner` với Windows giả lập (có/không có chủ sở hữu, không phải Windows); kiểm tra tĩnh + biên dịch cả hai phương án.
* **Chưa chạy được trên Windows + Tk thật**: cần bạn xác nhận (1) bố cục tab Voice/Behaviour trông ổn, (2) mở Settings rồi pet vẫn nổi trên cửa sổ đó,
  (3) khi mở Settings, cửa sổ vẫn hiện trước các app khác.
  Nếu pet vẫn bị che, hãy gửi lại console: có thể có dòng `[window] ... was owned by ...` cho biết chẩn đoán đúng.

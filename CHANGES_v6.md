# Đợt sửa thứ 6 (nền: phương án B)

## 1. Delete Discord in command_handler

## 3. Follow Cursor / Sit-Stay / Default theo nút
**Nguyên nhân**: Follow và Sit là **hai công tắc độc lập** (`follow_mode = not follow_mode`): bấm lần hai là tắt, và có thể bật cả hai cùng lúc. Nên trông như chạy theo chu kỳ.
**Sửa**: mỗi nút **đặt** một chế độ, bấm bao nhiêu lần vẫn giữ nguyên, và ba chế độ loại trừ nhau:

| Nút | Kết quả |
|---|---|
| **Follow Cursor** | Luôn đi theo con trỏ |
| **Sit / Stay** | Đứng yên một chỗ nhưng vẫn có hoạt ảnh (như trước) |
| **Default** (mới) | Hành vi tự nhiên mặc định; thoát hẳn trạng thái đi theo con trỏ |

Có ở cả menu chuột phải (kèm dấu ✓ cạnh chế độ đang dùng) và menu khay hệ thống (dạng nút chọn một trong ba). `toggle_follow()` / `toggle_sit()` cũ được giữ tên nhưng không còn đảo trạng thái.

## 4. Rồng trả lời "Woof!"
**Nguyên nhân thật** (không phải ngẫu nhiên): `DRAGON_PERSONALITIES` ánh xạ tính cách **lazy** và **curious** vào hai prompt **của chó** ("You are Buddy, a tiny pixel dog...") vì rồng không có prompt riêng cho hai tính cách này.
Ngoài ra lịch sử hội thoại lưu (6 lượt gần nhất) còn các câu "Woof!" từ lúc pet là chó, mô hình nhỏ bắt chước chúng.
**Sửa (3 tầng)**
1. Thêm prompt `dragon_lazy`, `dragon_curious` và sửa ánh xạ. Ví dụ "WOOF WOOF WOOF!!!" trong prompt chó hyper đổi thành "BEST DAY EVER!!!".
2. **Bộ lọc tiếng kêu** trên câu trả lời của LLM: xóa woof/bark/arf/ruff/yip/yap/bow-wow/meow/mew/purr/hiss/roar/rawr/growl/grr (kể cả "barking", "purring"). Mô tả hành động có tiếng kêu (`*barks happily*`) bị bỏ cả cụm.
   Nếu chẳng còn gì thì dùng câu dự phòng. Lọc được áp dụng **trước** `_clean` (hàm này chỉ giữ câu đầu nên lọc sau sẽ làm mất phần còn lại).
3. Làm sạch lịch sử trước khi gửi cho mô hình (bỏ tiếng kêu trong các câu trả lời cũ của pet).

*Chủ ý / cần biết*: bộ lọc áp dụng cho **mọi loại pet** (đúng yêu cầu "xóa tiếng kêu động vật"; chó cũng không còn "Woof" do LLM sinh ra), và cả "roar/growl" của rồng. Muốn đổi, sửa `_SOUND_PATTERN` trong `llm_brain.py`.
Các **câu dự phòng viết tay** (ví dụ `*roars into the void*` của rồng, `WOOF WOOF WOOF!!!` của chó hyper) **không bị lọc**, vì chúng không phải câu của mô hình và lọc sẽ làm rỗng chúng.
Lọc cũng có thể xóa nhầm các thành ngữ như "barking mad" (còn "mad").

## 5. Pomodoro không cộng giờ nghỉ khi máy ngủ
**Nguyên nhân**: `check()` cắt khoảng trống giữa hai lần xử lý còn tối đa 5 giây (để thời gian máy ngủ không bị tính là *đang làm việc*), nhưng cũng làm **mất luôn** thời gian nghỉ khi đang ở giờ nghỉ.
**Sửa**: nếu khoảng trống > 30 s thì coi là máy vừa ngủ/ngủ đông/khoá và xử lý riêng (dùng cả đồng hồ treo tường, vì tùy máy đồng hồ đơn điệu có thể không chạy lúc ngủ):

| Trạng thái | Máy ngủ đúng X giây |
|---|---|
| **Giờ nghỉ** | Cộng X vào thời gian nghỉ; đủ 10 phút thì hoàn thành Pomodoro ngay khi thức dậy (có chime, lời chúc hiện khi bạn thao tác) |
| **Focus** | X ≥ 3 phút: coi là tự nghỉ, đếm lại focus. Dưới 3 phút: tạm dừng, không cộng thêm |

Chỉ **tắt màn hình** (máy vẫn chạy) thì không cần xử lý riêng: bộ đếm thời gian không thao tác vẫn chạy như cũ.

## Đã kiểm thử gì — và chưa
Chạy thật: `_spawn` (Windows giả lập, luồng Discord → Update.exe); vòng nghe micro với `speech_recognition` giả (6 kịch bản: bình thường, OSError, AttributeError, 5 lỗi liên tiếp, mở micro lỗi 3 lần, đồng hồ nhảy 20 phút);
chế độ di chuyển (bấm lặp và xen kẽ, thoát khỏi FOLLOW); bộ lọc tiếng kêu qua `_llm_call` với máy chủ Ollama giả (cả hai tính cách lazy/curious dùng prompt rồng, lịch sử gửi đi đã sạch);
Pomodoro khi máy ngủ (6 kịch bản) và chạy lại bộ thử Pomodoro cũ (không hồi quy); kiểm tra tĩnh + biên dịch phương án B.
Trong lúc kiểm thử tôi phát hiện và sửa 2 lỗi do chính mình: thứ tự lọc/`_clean` (xem mục 4) và vài kết quả sai do bộ thử.
**Chưa chạy trên Windows + Tk + micro thật**: cần bạn xác nhận (1) mở Discord không còn log trong terminal, (2) voice tự phục hồi sau khi máy ngủ, (3) menu Follow/Sit/Default, (4) ngủ máy trong giờ nghỉ được cộng dồn.

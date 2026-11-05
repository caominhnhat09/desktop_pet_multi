# Sửa 10 vấn đề — desktop_multi_pet_git

Nguyên tắc: chỉ **bổ sung / thay phần lỗi tại chỗ**, giữ nguyên kiến trúc từng file
(tên class, tên hàm, chữ ký hàm cũ vẫn dùng được). Khi bỏ một tính năng thì gỡ **đồng bộ ở mọi file**
tham chiếu tới nó.

## Cách áp dụng
1. Chép đè các file `.py`, `build.bat`, `README.md` trong thư mục này vào project (file mới: `alert_sound.py`).
2. Xóa 3 file trong `XOA_CAC_FILE_NAY.txt`.
3. Không cần xóa `config.json` / `memory.json`: dữ liệu cũ tự được chuẩn hóa (xem mục 4, 5).

## Tổng hợp

| # | Vấn đề | Nguyên nhân gốc | File sửa |
|---|--------|-----------------|----------|
| 1 | `close ...` lại mở app/web | `close ` nằm chung danh sách với `open/launch/start` nên bị gọi `_open_app` | llm_brain |
| 2 | `next` không chuyển bài | Bản zip đã có `next` ở cả 2 danh sách; ảnh log là trước khi thêm. Đã kiểm chứng `next` → `music/next` giống `skip` | (llm_brain: chỉ thêm `next` vào INTENT_PATTERNS) |
| 3 | `set timer` chỉ hiện 1 bong bóng | `_set_timer` gọi `set_reminder()` = **đổi chu kỳ nhắc nghỉ**, không phải hẹn giờ; còn ghi đè cài đặt (config của bạn có `reminder_min: 1` vì thế) | main, command_handler, llm_brain, alert_sound (mới) |
| 4a | Most active hours = 21:00 ngay | `_hour_counts` chỉ ở RAM, reset mỗi phiên rồi **ghi đè** giá trị đã lưu; chỉ đếm lượt LLM trả lời | memory, main |
| 4b | Break interval "không có tác dụng" | Chỉ nhắc 1 lần/chu kỳ, chỉ 9h–22h, không biết bạn có nghỉ hay không; `Reminder Style` không được dùng ở đâu; `--reminder` luôn =45 bỏ qua config | reminders, screen_time, settings_window, main, config_manager |
| 5 | Tab Apps trống | `record_app_time` cộng ~0.0003 phút mỗi tick rồi `round(..,1)` → luôn 0.0 (memory.json của bạn: toàn `0.0`) | memory, main, memory_dashboard |
| 6 | Bỏ Dreams | — | main, memory_dashboard, settings_window, xóa dream_journal.py + dreams.json |
| 7 | Facts có tác dụng gì | Xem mục 7 bên dưới | memory, memory_dashboard |
| 8 | Bong bóng đứng yên khi pet di chuyển | `say()` định vị đúng 1 lần | speech, main |
| 9 | Bỏ Weather | — | main, xóa weather.py |
| 10 | Thoát bị lỗi TclError / hình chữ nhật trắng | Menu Quit gọi `root.destroy()` trực tiếp khi vòng `tick`, bong bóng `after(...)` vẫn đang chạy | main, tray |

## 3. Hẹn giờ thật
* `set timer 5 minutes`, `30 seconds`, `1 hour`, `an hour`, `remind me in 2 hours`; `cancel timer` / `stop timer` để hủy.
* Hết giờ: **âm báo** (winsound, không cần file âm thanh) + bong bóng 12 giây + toast Windows + pet nhảy.
  Nếu chưa ai bấm vào pet, chuông **nhắc lại sau 20 s và 40 s**. Bấm vào pet = tắt chuông.
* `set_reminder()` vẫn tồn tại nhưng chỉ dành cho Settings → Reminders.

## 4b. Pomodoro (Settings → Reminders)
* **Focus length** (Off/20/30/45/60/90) = số phút bạn *thực sự dùng máy* (có thao tác) trước khi bị bắt nghỉ.
* Hết focus → **nghỉ 10 phút**. Pet nhắc mỗi ~90 s khi bạn còn ngồi máy, mỗi lần gắt hơn
  (nhẹ → nhắc → khẩn), kèm âm báo.
  Thời gian rời máy (không thao tác ≥30 s) được cộng dồn; đủ 10 phút = **hoàn thành 1 Pomodoro 🍅**.
* Tự nghỉ ≥3 phút giữa chừng → đếm lại focus. Đang họp → không bắt nghỉ. Quá 30 phút không chịu nghỉ → bỏ vòng, ghi "bỏ qua giờ nghỉ".
* **Giọng điệu**: Reminder Style (friendly/stern/silly) × tính cách pet (hyper → IN HOA, playful/lazy/curious/loyal → thêm câu cuối) × loại pet (hooman/human/mortal).
* **Focus streak** (số Pomodoro hôm nay) hiện trong Settings và Pet Status.
* **Weekly productivity report**: biểu đồ 7 ngày (cột = phút focus, số trên cột = số Pomodoro), tổng, trung bình/ngày, ngày tốt nhất, số lần bỏ qua giờ nghỉ. Dữ liệu lưu trong `screen_time.json`.
* Cài đặt được nhớ qua lần chạy sau (`reminder_min`, `reminder_style`). Giá trị lạ trong config cũ (vd `1`) tự về 45.
* Đã bỏ giới hạn giờ làm việc 9h–22h cũ.

## 5. Tab Apps / Top apps
Giờ cộng bằng thời gian **thật** giữa 2 tick (không giả định 16 ms), bỏ qua lúc AFK, làm tròn chỉ khi ghi file.
Dưới 1 phút hiện giây (`24s`), ≥2 giờ hiện `2.0h`. Dữ liệu `0.0` cũ bị bỏ qua, bắt đầu tích lũy lại từ bây giờ.

## 7. Facts
* Tab Facts hiển thị `memory.json → facts`. Ở **mọi lần** gọi LLM, `build_context_block()` được đưa vào system prompt
  (cùng 6 lượt hội thoại gần nhất) → pet biết tên/nghề/nơi làm việc/sở thích… của bạn.
* **Trước đây chỉ 4 khóa được dùng** (`user_name, job, workplace, likes`): fact thêm tay như `hobby = chess` bị bỏ qua.
  Giờ mọi fact (tối đa 6 mục thêm, mỗi mục ≤40 ký tự) được đưa vào prompt.
* Fact chỉ học từ câu **không phải lệnh** (câu rơi vào chat với LLM). Mẫu nhận diện: `my name is…`, `I work at/as…`,
  `I live in…`, `I like…`, `I'm N years old`, `my favorite X is Y`.
* Sửa kèm: "I'm tired / I am 21 years old / I am a developer" không còn bị lưu thành *tên* = `tired`/`21`/`a`;
  `my favorite color is blue` giờ lưu được cả giá trị (`favorite_color = blue`).
* Sửa bố cục: ô **Add a fact manually** bị đẩy sang mép phải, nút *Add* bị khuất — giờ nằm ở đáy tab.

## 10. Thoát chương trình
Chuỗi lỗi: bấm Quit → `root.destroy()` ngay trong lúc menu chuột phải còn vòng sự kiện lồng, `tick()` và bong bóng
vẫn gọi vào cửa sổ đã chết (`NULL main window`, `invalid command name ..._dismiss`), rồi `menu.grab_release()` lỗi thứ hai.
Giờ: `quit_app()` đặt cờ → `tick` dừng → ẩn bong bóng, hủy hẹn giờ → `root.quit()` → `run()` lưu dữ liệu → mới `destroy()`.
Menu chuột phải và khay hệ thống đều đi qua `quit_app()`.
Dữ liệu vẫn được lưu bình thường ở cả bản cũ; các thông báo lỗi chỉ gây nhiễu.

## 7 (phụ). Toàn bộ lệnh giọng nói
Gọi tên pet (hoặc nói cả câu): `hey dragon / okay dragon / dragon / hey buddy` (rồng);
`hey kitty / hey cat / okay kitty / kitty / hey buddy` (mèo); `hey buddy / okay dog / hey dog / hey doug / buddy` (chó).
Nói tên rồi dừng thì có **8 giây** để nói lệnh. Cùng bộ lệnh dùng được trong hộp thoại gõ lệnh của khay hệ thống.

| Nhóm | Câu nói | Hành vi |
|---|---|---|
| Nhạc | `play <bài/nghệ sĩ>` | Spotify API nếu cấu hình; không thì mở tìm kiếm trong Spotify |
| | `pause` · `house` · `stop` · `stop music` | Tạm dừng (không có Spotify API: phím Play/Pause, **bật/tắt xen kẽ**) |
| | `resume` | Phát tiếp (phím Play/Pause) |
| | `skip` · `next` | Bài kế |
| | `volume 0–100` | Có Spotify API: đặt đúng mức. Không có: >60 tăng, <40 giảm, 40–60 không làm gì |
| | `mute` | **Hiện đang là Play/Pause**, không phải tắt tiếng |
| Mở | `open / launch / start <tên>` | Chrome, Firefox, Edge, VS Code, Notepad, Calculator, Explorer, Task Manager, Discord, Slack, Terminal, PowerShell, Word, Excel, PowerPoint, Paint, Spotify (tên khác: thử để Windows tự tìm) |
| | `open youtube` · `open gmail` · `open google drive` · `open github`… | Mở web bằng trình duyệt mặc định (`WEB_MAP`) |
| Hẹn giờ | `set timer 5 minutes` · `30 seconds` · `1 hour` · `remind me in 2 hours` · `cancel timer` | Xem mục 3 |
| Tìm kiếm | `search <x>` · `google <x>` · `look up <x>` · `find <x>` | Tìm trên Google |
| Cho ăn | `feed` · `treat` · `bone` (từ nằm đâu trong câu cũng được) | Cho ăn |
| Trick | `trick` (ngẫu nhiên) · `jump` · `spin` · `dance` · `roll` · `flip` · `shake` · `moonwalk` · `sneeze` · `dizzy` | Pet làm trick. Tên nào pet không có hoạt ảnh → làm trick ngẫu nhiên của pet đó (bản cũ im lặng không làm gì) |
| Đổi tên | `your name is X` · `call yourself X` · `rename yourself to X` · `you are now X` | Đổi tên pet |
| Còn lại | bất kỳ câu nào khác | Trò chuyện với LLM (và học facts) |

Không còn là lệnh: `close ...` (→ chat). Chưa là lệnh dù có code: `previous/back` (hàm `_music` có nhánh `prev` nhưng bộ phân loại không sinh ra),
`hiccup` (có trong bảng trick nhưng không có trong danh sách nhận diện).
Lưu ý: `next`, `stop`, `house`, `skip`… khớp **ở bất cứ đâu trong câu** (như `pause` trước đây), vd "what's next" cũng chuyển bài.

## Đã kiểm thử gì — và chưa
* Chạy thật (Python): phân loại lệnh (hơn 50 câu), hẹn giờ từ lệnh giọng nói tới chuông (kể cả hủy, bấm tắt),
  Pomodoro 6 kịch bản + lưu/nạp file thật, memory (giờ/app/facts, dữ liệu thật của bạn), thống kê tuần, định vị bong bóng.
* Giao diện dựng bằng đối tượng Tk giả (kiểm tra luồng, thứ tự pack, vẽ biểu đồ), biên dịch toàn project, kiểm tra tĩnh thuộc tính/tên.
* **Chưa chạy được trên Windows + Tk thật**: hình dạng/khoảng cách giao diện Settings, âm thanh `winsound`, và chuỗi thoát chương trình
  cần bạn xác nhận khi chạy thật.

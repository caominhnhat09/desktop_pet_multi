# Đợt sửa thứ 2 — 4 vấn đề trong `vấn đề multi pet 2.docx`

Cách áp dụng: chọn **một** trong hai thư mục (A hoặc B), chép đè các file trong đó vào project.
Cả hai đều gồm bản sửa của mục 1, 3, 4. Hai phương án chỉ khác nhau ở mục 2 (Google Workspace).

---
## 1. Pomodoro

**Nằm ở đâu**
| File | Vai trò |
|---|---|
| `reminders.py` | **Toàn bộ logic** (đếm focus, giờ nghỉ, nhắc, lời thoại) |
| `screen_time.py` | Lưu thống kê Pomodoro + báo cáo tuần (`screen_time.json`) |
| `settings_window.py` | Tab Reminders (chọn focus, style, biểu đồ tuần) |
| `alert_sound.py` | Âm báo (`PATTERNS`: `break`, `nag`, `done`, `timer`) |
| `main.py` | Gọi `reminder.check()` mỗi tick, nạp/lưu cài đặt |
| `config_manager.py` | Lưu `reminder_min`, `reminder_style` |

**Các hằng số** (đầu `reminders.py`): `ACTIVE_IDLE_SEC=60` · `AWAY_IDLE_SEC=30` · `RESET_IDLE_SEC=180` ·
`BREAK_MINUTES=10` · `NAG_EVERY_SEC=90` · `BREAK_GIVEUP=30*60`.

**Trả lời 5 trường hợp** (đã chạy thật trên `reminders.py` bằng đồng hồ giả)

| # | Tình huống | Trước đợt sửa này | Sau khi sửa |
|---|---|---|---|
| 1 | Giờ nghỉ bắt đầu, bạn phớt lờ 21 phút, nghỉ 4 phút, làm lại 5 phút | Đúng phút 30 kể từ lúc bắt đầu nghỉ pet **bỏ vòng**, ghi "bỏ qua", mất phần nghỉ | Giờ nghỉ **tiếp tục** (đã nghỉ 3,5/10 phút, ngồi máy tổng 26 phút < 30) |
| 2 | Phớt lờ 25 phút rồi nghỉ thật | Đúng phút 30 (mới nghỉ ~4,5 phút) pet **hủy**, ghi "bỏ qua" | Nghỉ tiếp tới đủ 10 phút → **hoàn thành Pomodoro** |
| 3 | Tự nghỉ 2 phút giữa lúc focus | **Không** cộng đủ 2 phút, **không** reset: ~1 phút đầu vẫn tính (vì <60 s không thao tác), ~1 phút sau **tạm dừng**, quay lại thì đếm tiếp | (không đổi) |
| 4 | Âm báo khi hết giờ nghỉ | **Có**: chime `done` (4 nốt tăng dần) + toast "Pomodoro complete"; bong bóng hiện khi bạn quay lại. Đầu giờ nghỉ cũng có chime `break` + toast | (không đổi) |
| 5 | Focus 20 phút, làm 18 phút rồi rời máy | Rời 1–2 phút: focus dừng ở ~19 phút, quay lại làm thêm ~1 phút thì vào giờ nghỉ. Rời ≥3 phút: **về 0**, không có giờ nghỉ, không tính Pomodoro | (không đổi) |

Chi tiết cần biết:
* Focus chỉ tăng khi lần thao tác gần nhất cách nay **<60 giây**; trong khoảng 60–180 giây thì **tạm dừng**; chạm **180 giây** thì **về 0**.
* Focus đầy lúc bạn vừa rời máy (vd làm 19,5 phút rồi đi) thì giờ nghỉ bắt đầu ngay khi không thao tác 30 giây, và thời gian vắng mặt tính vào 10 phút nghỉ.
* Thời gian nghỉ chỉ tính khi không thao tác **≥30 giây** (30 giây đầu mỗi lần vắng không tính), nên chime `done` kêu sau khoảng 10,5 phút vắng mặt.
* Thời gian nghỉ được **cộng dồn** qua nhiều lần rời máy.

**Thay đổi hành vi duy nhất trong mục này (trường hợp 1, 2)**: bộ đếm "bỏ vòng 30 phút" trước đây tính từ lúc *bắt đầu giờ nghỉ*,
nay chỉ tính thời gian bạn **ngồi máy phớt lờ**. Nếu muốn giữ kiểu cũ, báo tôi.

---
## 2. Các dòng "disabled" khi chạy

Đây **không phải lỗi**, chỉ là thông báo; nhưng dòng thứ ba có một nguyên nhân thật:

| Dòng | Ý nghĩa |
|---|---|
| `[workspace] No credentials.json — Google integration disabled` | Tính năng **tùy chọn** chưa bật (cần file `credentials.json` do bạn tạo trên Google Cloud) |
| `[spotify] No credentials in config.json — using media keys fallback` | Tính năng **tùy chọn**: không có Spotify API thì pet điều khiển nhạc bằng phím media (vẫn chạy bình thường) |
| `[tracker] taskbar y=2040 looks wrong, using fallback 816` | Màn hình 4K hiển thị 250%: Windows trả vị trí taskbar theo pixel **vật lý** (2040) còn Tk dùng pixel **logic** (864 = 2160/2,5). Code thấy "ngoài màn hình" nên dùng giá trị dự phòng — kết quả (816) tình cờ **đúng**. |

**`google_workspace.py` làm gì**: đọc **chỉ-đọc** Gmail (số thư chưa đọc, người gửi) và Google Calendar (sự kiện sắp tới) qua OAuth;
pet bình luận + bắn toast khi có thư mới hoặc cuộc họp trong ≤10 phút. Dùng ở `main.py` (khởi tạo, vòng kiểm tra mỗi 300 s, dòng "Workspace" trong Pet Status, dừng khi thoát).
**Xóa có ảnh hưởng gì?** Hiện **không ảnh hưởng gì** vì bạn chưa có `credentials.json` nên nó không làm gì. Bạn chỉ mất khả năng bật tính năng này sau này
(và dòng "Workspace: Not configured" trong Pet Status). Nhận diện cuộc họp (`in_meeting`) dựa trên tiêu đề cửa sổ nên **không** phụ thuộc vào nó.

### Phương án A — giữ lại, chỉnh cho im lặng (`phuong_an_A_giu_lai/`)
* `google_workspace.py`, `spotify_api.py`: chỉ in dòng thông báo khi đặt biến môi trường `PET_VERBOSE=1`.
* `input_tracker.py`: quy đổi toạ độ taskbar theo tỉ lệ hiển thị (máy bạn: 2040 → **816**, in `taskbar detected at y=816 (display scaling x2.50, raw y=2040)`).
  Máy scaling 125% sẽ ra 826 (chính xác hơn mức dự phòng 816).
* Giữ nguyên mọi tính năng; sau này muốn dùng Workspace chỉ cần thêm `credentials.json`.

### Phương án B — xóa hẳn (`phuong_an_B_xoa_workspace/`) (choose this)
* Xóa `google_workspace.py`; `main.py` bỏ: import, `CD_WORKSPACE`, `self.workspace`, `_t_workspace`, `_last_unread`, khối kiểm tra thư/lịch,
  dòng "Workspace" trong Pet Status, và lệnh `workspace.stop`. `requirements.txt` bỏ 4 dòng chú thích về Google.
* Vẫn gồm sửa `spotify_api.py` và `input_tracker.py` như A. `notifications.py` còn hàm `email()`/`meeting()` không dùng tới (vô hại).

**Khuyến nghị**: nếu bạn không định dùng Gmail/Calendar thì chọn B cho gọn; nếu chưa chắc thì chọn A (không mất gì).

---
## 3. `achievement_ui.py` — TclError khi lăn chuột
**Nguyên nhân**: `bind_all("<MouseWheel>", lambda ...)` là gắn **toàn cục**. Đóng cửa sổ Achievements xong, lambda vẫn còn và
mỗi lần lăn chuột ở bất kỳ đâu lại gọi vào canvas đã bị xóa → `invalid command name ".!toplevel36.!frame6.!canvas"`.
**Sửa**: handler riêng (`_on_mousewheel`) kiểm tra canvas còn sống và nuốt `TclError`; khi cửa sổ đóng thì `unbind_all` (chỉ phản ứng với `<Destroy>` của cửa sổ chính, không phải widget con).
Đây là chỗ duy nhất trong project dùng `bind_all`.

---
## 4. Thoát vẫn phải click/bấm phím
**Nguyên nhân (suy luận, chưa tái hiện được trên Windows)**: bản trước chỉ gọi `root.quit()` rồi chờ `mainloop()` kết thúc.
Vòng lặp Tk chỉ kiểm tra cờ thoát sau khi xử lý một sự kiện, mà `tick` đã ngừng tự hẹn lịch → không còn sự kiện nào cho tới khi bạn click/bấm phím.
**Sửa**: `quit_app()` không còn phụ thuộc `mainloop()`: ẩn pet → lưu dữ liệu → dừng luồng nền → **tắt tiến trình**
(`os._exit(0)` sau khi đã lưu). Khay hệ thống được gỡ ở luồng riêng (chờ tối đa 1 s) và có **chốt chặn 3 giây**: dù bước dọn dẹp nào bị treo, tiến trình vẫn bị tắt.
Bấm Quit hai lần không gây lỗi. Menu chuột phải và khay hệ thống đều đi qua hàm này.

---
## Đã kiểm thử gì — và chưa
* Chạy thật: toàn bộ Pomodoro (5 trường hợp + bỏ vòng + biên), `achievement_ui` với đúng chuỗi lỗi trong log, quy đổi taskbar (4 cấu hình màn hình), đường thoát với đối tượng giả
  (thứ tự, thoát đúng 1 lần, khay treo 5 s vẫn thoát sau ~1,2 s), kiểm tra tĩnh + biên dịch cả hai phương án.
* **Chưa chạy được trên Windows + Tk thật**: cần bạn xác nhận (1) Quit thoát ngay không cần click, (2) tiếng chime ở đầu và cuối giờ nghỉ, (3) không còn TclError khi lăn chuột sau khi đóng Achievements.

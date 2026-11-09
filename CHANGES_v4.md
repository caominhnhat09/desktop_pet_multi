# Đợt sửa thứ 4 (nền: phương án B của v3)

Chỉ đổi **2 file**: chép đè `settings_window.py` và `memory_dashboard.py` vào project. (Hai file này giống hệt ở phương án A.)

## Settings → Voice
Chỉ còn một dòng **Google** (không bấm được, đang được chọn khi có SpeechRecognition). Đã xóa dòng Sphinx và Whisper.
Việc nhận dạng giọng nói không đổi: `voice.py` vẫn tự rơi về Sphinx/Whisper khi cần, chỉ là không liệt kê trên giao diện.

## Memory Dashboard
Còn 4 tab: **Facts, Apps, Emotions, Stats**. Đã xóa tab Chats cùng hai hàm chỉ phục vụ tab đó (`_build_exchanges`, `_clear_exchanges`).
Không có chỗ nào chọn tab theo số thứ tự nên việc bỏ một tab không làm lệch tab khác.

**Giữ nguyên có chủ ý**
* Lịch sử hội thoại vẫn được **lưu và vẫn được dùng làm ngữ cảnh cho AI** (6 lượt gần nhất): đó là cách pet nhớ bạn vừa nói gì. Chỉ là không còn tab để xem.
* Dòng **"💬 Conversations"** trong tab Stats (đếm số cuộc hội thoại) vẫn còn.
* Nút **Forget Everything** vẫn xóa cả lịch sử hội thoại. Giờ nó là cách duy nhất trên giao diện để xóa lịch sử này, vì nút "Clear all" của tab Chats đã mất.

## Đã kiểm thử
Dựng thử với Tk giả: tab dựng ra đúng `Facts, Apps, Emotions, Stats`; tab Voice có đúng 1 nút (Google, `disabled`, đang chọn) và không còn chữ Sphinx/Whisper;
thiếu SpeechRecognition thì không chọn nút nào; kiểm tra tĩnh + biên dịch phương án B. Chưa chạy trên Tk thật.

# Nhạc người nhà gửi và bỏ xác nhận tâm trạng — 15/10/2026

## Sử dụng

1. Cổng người nhà: chọn đúng người thân, mở **Âm thanh & Bài hát**.
2. Chọn MP3/WAV tối đa 50 MB, nhập tên (tùy chọn), bấm **Tải lên và gửi nhạc**.
3. App người cao tuổi: mở **Trò chơi trí nhớ và Thư giãn**, chọn bài có nhãn
   **[Người nhà]** trong danh sách nhạc, bấm **Phát Nhạc**.

Danh sách trên app tự làm mới khoảng 2 giây. Nhạc không tự phát khi nhận bài
mới, không đổi lựa chọn hay ngắt bài đang nghe. Đổi hồ sơ bệnh nhân thì dừng
bài của hồ sơ cũ và chuyển sang thư viện của hồ sơ mới.

Đã bỏ thẻ **Cảm nhận hôm nay** và các nút xác nhận tâm trạng trên app người
cao tuổi. Theo yêu cầu tiếp theo, cũng bỏ form **Ghi nhận tâm trạng của người
bệnh (Tự báo cáo)** ở cổng người nhà và handler JavaScript của form. Lịch sử cũ
và luồng tổng hợp biểu cảm camera vẫn giữ nguyên.

## Lưu trữ và đồng bộ

File gốc lưu trong `MEDIA_DIR = WRITABLE_ROOT / media`. Với bản portable này,
đường dẫn là `AICareDemo/runtime/media`. Tên file lưu được tạo riêng, không dùng
đường dẫn do trình duyệt cung cấp. Tên bài và tên file gốc được lưu trong CSDL.

Migration 010 tạo `family_music` trong CSDL chung. API tải nhạc xác thực vai trò
người nhà và quan hệ với bệnh nhân trước khi đọc dữ liệu; kiểm tra định dạng
MP3/WAV bằng PyAV, giải mã một frame và lấy thời lượng trước khi lưu. Lưu file
tạm rồi đổi tên; nếu giao dịch CSDL lỗi thì dọn file. Upload lặp cùng nội dung
cho cùng bệnh nhân không tạo bản trùng. Sự kiện `music.track_uploaded` cập nhật
danh sách người nhà qua SSE. Nghe thử trên web hỗ trợ byte ranges và yêu cầu
phiên đăng nhập được phân quyền.

Repository nhạc bên app hợp nhất nhạc có sẵn với nhạc người nhà của đúng hồ sơ,
đồng thời cache metadata cần thiết cho khóa ngoại lịch sử nghe ở CSDL trò chơi.
File âm thanh vẫn nằm trong media, không sao chép vào assets của module.

## Kiểm chứng

41 kiểm thử đạt khi chạy `test_family_music.py`, `test_emotion_summary.py` và
`test_vitals_sync_regression.py`. Các ca nhạc gồm WAV/MP3 thật, HTTP upload nhị
phân, Range GET, phân quyền hồ sơ, chống tệp giả/đường dẫn vượt media, giới hạn
dung lượng, upload trùng, rollback dọn file, danh sách desktop, gọi trình phát
đúng file, không autoplay/ngắt nhạc và bỏ thẻ tâm trạng.

Trên máy chủ QA riêng cổng 8098: đăng nhập bằng tài khoản mẫu, chọn file WAV
tổng hợp qua file chooser và bấm tải lên. Form báo lưu thành công, hiển thị
tên/thời lượng/bộ nghe thử; console không có lỗi JavaScript trong lần kiểm tra.

App Qt QA đọc cùng CSDL và media QA, nhận bài `[Người nhà]` vừa gửi từ browser.
Phát bằng QMediaPlayer thật với âm lượng 0: vị trí phát tăng tới 800 ms, không
có lỗi backend. Không ghi bài thử vào thư viện người dùng thực tế.

JavaScript qua `node --check`; các file Python sửa qua `py_compile`.

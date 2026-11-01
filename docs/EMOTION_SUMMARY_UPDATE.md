# Tổng hợp tâm trạng và giao diện trò chơi — 15/10/2026

## Quy tắc đã thống nhất

- Mỗi bệnh nhân có các khung 2 giờ liên tiếp, bắt đầu từ mẫu camera hợp lệ đầu tiên.
- Dùng tổng thời gian, không dùng số khung hình, để chọn trạng thái giữ lâu nhất.
- Theo lựa chọn của người dùng, cộng dồn Buồn + Bình thường trong từng khung,
  kể cả khi có Vui xen giữa. Khi đã quan sát cả hai trạng thái và tổng vượt
  900 giây, công bố Buồn ngay một lần trong khung đó. Đúng 900 giây chưa kích hoạt.
- Kết luận Buồn này được ưu tiên trong bản tổng hợp cuối khung; vẫn lưu trạng
  thái thực tế dài nhất và tổng thời gian từng trạng thái để đối chiếu.
- Sang khung mới, bộ đếm và cờ thông báo sớm được đặt lại. Nếu hòa thời gian,
  thứ tự chọn là Buồn, Bình thường, Vui.
- Chỉ ghi nhận camera thật và danh tính nhận diện hợp lệ; không đưa video thử
  hoặc kết quả JSON cũ vào bộ đếm. Mẫu không thấy mặt ngừng tính thời gian.
  Mỗi mẫu được duy trì tối đa 5 giây; khoảng mất camera/đóng app lâu hơn không
  được tính tiếp hoặc tạo số liệu giả.

## Triển khai

Migration 009 tạo trạng thái tích lũy và lịch sử tổng hợp riêng. Desktop ghi mẫu
khoảng mỗi giây; backend kết thúc các khung quá hạn mỗi 5 giây, kể cả khi desktop
ngừng chạy. Trạng thái, bản tổng hợp và sự kiện outbox được ghi trong giao dịch
SQLite, khóa trước khi đọc để tránh mất cập nhật giữa hai tiến trình. Khởi động
lại tiếp tục từ trạng thái đã lưu và không gửi lại thông báo cùng khung.

Cổng người nhà có ô tâm trạng trên bảng tổng quan và lịch sử chi tiết tại
Sức khỏe tinh thần. Sự kiện `emotion.summary_updated` dùng SSE hiện có để tải
lại dữ liệu ngay; không gửi email/SMS. Tâm trạng tự khai báo được giữ riêng.

Độ nhạy Buồn: tăng trọng số tín hiệu FACS buồn 10% (`sad_sensitivity=1.10`),
không thêm điểm buồn cố định cho mặt nghỉ và giữ nguyên bộ làm mượt theo thời gian.
Đây là điều chỉnh trọng số, không phải tuyên bố độ chính xác đã tăng 10%.

Các danh sách xổ xuống trong phần trò chơi/nhạc/hẹn giờ có nền trắng và chữ đen;
mục chọn dùng nền xanh nhạt và vẫn giữ chữ đen.

## Kiểm chứng

- 26 ca đạt khi chạy `test_emotion_summary.py` cùng `test_vitals_sync_regression.py`.
- 4 ca EmotionAdapter hiện có đạt, gồm mặt nghỉ, cười, buồn và bộ làm mượt.
- Các ca mới kiểm tra mốc 900 giây, 7200 giây, cộng dồn qua đoạn Vui, không gửi
  lặp, đặt lại giữa khung, thời gian mất mặt/camera, khởi động lại, phân tách
  bệnh nhân, giao dịch lỗi không ghi dở và luồng API/SSE.
- JavaScript cổng người nhà qua `node --check`; các file Python sửa qua py_compile.
- Máy chủ QA riêng cổng 8098, CSDL riêng: đăng nhập bằng tài khoản mẫu, thấy
  ô Buồn với thời gian Buồn 5 phút + Bình thường 10.1 phút (có Vui 1.7 phút).
  Khi mô phỏng hết khung 2 giờ, lịch sử tự thêm bản tổng hợp qua SSE mà không
  tải lại trang. Console không có lỗi JavaScript trong lần kiểm tra này.
- Kiểm tra palette 6 dropdown và render popup ra `runtime/game-dropdown-white.png`.
  Môi trường Qt offscreen cần nạp font Segoe UI tường minh để render chữ.

Dữ liệu mô phỏng chỉ ghi ở CSDL QA; không thêm tâm trạng giả vào CSDL sử dụng.

# Kiểm tra trên máy Windows triển khai

Các bước dưới đây chưa được thực hiện với camera, chế độ ngủ và Gmail thật trong tác vụ triển khai mã. Chỉ dùng hồ sơ và tên thuốc mẫu; không thay lịch thật để kiểm thử.

1. Chạy bản EXE trên máy mục tiêu, đăng ký hai hồ sơ mẫu. Kiểm tra camera, nhận diện, cảm xúc và cả ba bài tập; chuyển qua lại tab thuốc; đóng/mở đăng ký để kiểm tra việc trả camera. Ghi tên máy, Windows, camera và kết quả, không ghi email hoặc mật khẩu vào báo cáo công khai.
2. Tạo hai lịch mẫu cùng giờ cách hiện tại vài phút. Kiểm tra popup đủ hai lần nhắc và đúng người. Xác nhận một lần, kiểm tra lần còn lại không đổi. Thử hoãn rồi bỏ qua một lần khác; xác nhận muộn một lần quá hạn. Đóng/mở lại ứng dụng để kiểm tra lịch sử.
3. Tạo một lịch mẫu, thu nhỏ cửa sổ và chờ đến giờ. Kiểm tra âm thanh, cửa sổ nhắc và nút mở lịch. Kiểm tra riêng lúc Windows khóa màn hình; ghi giới hạn nhìn thấy thông báo. Ứng dụng chưa có khay hệ thống.
4. Cho máy ngủ trước giờ nhắc, mở lại sau giờ nhắc. Kiểm tra khoảng “Không giám sát” và thời điểm thực tế. Thử đóng hẳn ứng dụng rồi mở lại. Không kỳ vọng nhắc hay email trong thời gian máy ngủ/tắt.
5. Kiểm tra tại tài khoản Windows dùng thực tế rằng thư mục dữ liệu ghi được, dữ liệu nằm đúng chế độ portable/installed và tài khoản không liên quan không có quyền đọc. Đóng ứng dụng, sao lưu, rồi thử khôi phục vào thư mục thử nghiệm riêng.
6. Nếu cần nghiệm thu SMTP thật, dùng hộp thư do người kiểm thử sở hữu. Bật SMTP và opt-in chỉ trong lịch mẫu, bấm Kiểm tra Gmail rồi để một lần mẫu quá hạn. Kiểm tra SMTP_ACCEPTED khác với thư đã đến/đã đọc. Ngắt mạng trước khi đến hạn để kiểm tra lỗi; không dùng email người thân thật trong thao tác thử này.

Chỉ đổi trạng thái M04/M06/M08 thành PASS sau khi có bằng chứng trực tiếp. Không thay đổi giờ hệ thống của máy đang phục vụ lịch thật; các ca clock/DST đã có đồng hồ giả trong test tự động.

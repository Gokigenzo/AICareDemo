# Windows SETUP v3 — kiểm thử sửa lỗi Python

Ngày: 2026-10-03.

SETUP.bat chỉ gọi PowerShell và chuyển nguyên mã kết thúc. setup.ps1 xác minh bằng kết quả do Python thực thi, lấy đường dẫn interpreter thực, tạo và kiểm tra .venv trước khi chạy pip. Môi trường hỏng được đổi tên để giữ lại; cấu hình người dùng không bị ghi đè. Log ở runtime/logs/setup.log. Bộ cài Python lấy từ python.org và phải có chữ ký hợp lệ của Python Software Foundation.

Đã kiểm tra:
- Launcher giả trả exit 0 nhưng chỉ báo thiếu runtime: bị loại.
- Launcher trả exit 1 hoặc executable không tồn tại: bị loại.
- Python thật: được nhận diện qua đường dẫn tuyệt đối.
- Lệnh tạo venv trả 0 nhưng không tạo môi trường: setup dừng.
- Tạo venv thật trong đường dẫn có dấu cách, chạy lại dùng môi trường cũ: đạt.
- Mô phỏng thiếu runtime: gọi nhánh cài đặt rồi tiếp tục pip và kiểm tra ứng dụng.
- Mô phỏng tạo venv thất bại: không chạy pip hoặc kiểm tra ứng dụng.
- Tải và kiểm tra chữ ký bộ cài Python 3.12.10: đạt.
- Cài thật Python 3.12.10 vào thư mục riêng của dự án có dấu cách: đạt.

Lệnh kiểm thử: powershell -NoProfile -ExecutionPolicy Bypass -File packaging/portable/test_setup.ps1 -Python <duong-dan-python.exe>

Bản chia sẻ: release/AI_Rehabilitation_Assistant_Portable_SETUP_v3.zip.
Giải nén sang thư mục mới. Màn hình SETUP phải hiện SETUP v3 (2026-10-03).

Nghiệm thu từ ZIP giải nén trong đường dẫn có dấu cách:
- Chạy SETUP.bat với .venv mới: cài đủ thư viện, CHECK_SYSTEM.py đạt, mã kết thúc 0.
- Chạy lại SETUP.bat: tái sử dụng môi trường, tải/khởi tạo model Pose Lite ngay trong SETUP, CHECK_SYSTEM.py đạt, mã kết thúc 0.
- Máy kiểm thử có Python 3.11.15 được nhận diện và dùng đường dẫn thật; bộ cài tự động Python 3.12.10 được kiểm thử riêng trong thư mục mới.
- Chưa thử trên máy Windows thứ hai hoàn toàn sạch. Kiểm thử nhánh thiếu runtime gồm mô phỏng điều phối và chạy bộ cài thật riêng biệt.
- Dashboard: main.py --test đạt, exit 0; Face DNN, ExpressionNet, FaceMesh và MediaPipe Pose đều khởi tạo thành công sau SETUP, không tải model khi khởi động.

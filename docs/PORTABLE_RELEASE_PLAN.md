# Kế hoạch và nghiệm thu gói Windows portable

1. Xác định entry point, phiên bản Python và các tài nguyên cần thiết: `main.py`, `config.py`, model face/emotion, MediaPipe qua pip.
2. Tạo gói nguồn sạch, tách dữ liệu người dùng khỏi mã và chỉ tạo thư mục `runtime` rỗng.
3. `SETUP.bat` tìm Python 3.11/3.12 64-bit. Nếu thiếu, tải bộ cài Python 3.12.10 64-bit từ python.org, kiểm tra chữ ký số và cài cho người dùng hiện tại. Sau đó tạo `.venv`, cài thư viện, tạo cấu hình riêng và chạy `CHECK_SYSTEM.py`. Chỉ ghi dấu hoàn tất sau khi kiểm tra thành công.
4. `START.bat` khởi chạy bằng `.venv` đã cài; chạy lại setup khi thay máy hoặc cài đặt chưa hoàn tất.
5. Đối chiếu nội dung ZIP, kiểm tra CRC, quét hồ sơ và thông tin riêng, thử `main.py --test` từ bản staging.

## Giới hạn

Đây là gói nguồn Windows, không phải EXE độc lập. Máy nhận cần Internet trong lần SETUP đầu tiên để tải Python nếu thiếu và tải thư viện. Không cần cài Python lại trong các lần chạy START sau. Chưa có kiểm thử trên máy Windows thứ hai; kết quả trên máy build không thay cho kiểm thử camera, email và nhắc thuốc trong môi trường nhận.

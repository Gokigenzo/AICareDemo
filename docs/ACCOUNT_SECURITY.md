# Bảo vệ thông tin đăng nhập

Bản sửa ngày 01/11/2026 loại bỏ endpoint đăng nhập nhanh, danh sách tài khoản và bệnh nhân công khai. Tạo quan hệ chăm sóc qua API công khai bị tắt; quản trị viên cấp tài khoản và quyền qua các API đã xác thực. Người dùng vẫn đăng ký người chăm sóc qua ứng dụng Desktop cục bộ.

Mật khẩu dùng PBKDF2-HMAC-SHA256, 600.000 vòng và salt ngẫu nhiên 128 bit cho từng giá trị. API đăng nhập không trả password/hash, không phân biệt tài khoản không tồn tại, bị khóa hay sai mật khẩu trong thông báo lỗi. Bỏ việc tìm mật khẩu từ JSON để gợi ý hoặc bỏ qua mật khẩu đã lưu. Việc đổi mật khẩu/khóa tài khoản làm token cũ không còn hợp lệ.

## Cấp lại mật khẩu quản trị

Không có mật khẩu quản trị mặc định. Chạy trong terminal của máy cài ứng dụng:

```powershell
.venv\Scripts\python.exe scripts/set_account_password.py
```

Công cụ hỏi mật khẩu và xác nhận bằng `getpass`, yêu cầu ít nhất 12 ký tự và không nhận mật khẩu qua đối số dòng lệnh. Có thể chọn tài khoản bằng `--user-id` và cơ sở dữ liệu bằng `--database`. Công cụ không mở khóa tài khoản đã bị quản trị viên khóa.

Mật khẩu riêng cũ được băm khi chạy migration/khởi tạo dịch vụ xác thực; mật khẩu rỗng hoặc mặc định đã được công bố bị vô hiệu hóa và cần đặt lại. Hồ sơ JSON cũ được đổi từ mật khẩu rõ sang hash khi đồng bộ; đăng ký Desktop mới chỉ ghi hash. Đồng bộ hồ sơ không ghi đè mật khẩu đã được đặt lại trong cơ sở dữ liệu.

## Phạm vi công bố trên GitHub

Email giống thông tin cá nhân trong fixtures được thay bằng địa chỉ mẫu thuộc `example.com`. Các ảnh, PDF và Word trong `docs` được giữ cục bộ và loại khỏi Git bằng `.gitignore`; không xuất bản lại trước khi kiểm tra nội dung và metadata. Bản sao lịch sử trước xử lý được giữ cục bộ trong `runtime`, không đưa lên GitHub. Không đưa `.env`, database, dữ liệu người dùng hoặc bản sao Git chứa thông tin cũ vào repository.

Lịch sử remote được thay bằng một snapshot đã làm sạch theo lựa chọn của chủ repo. Force-push không thu hồi bản clone, fork hay nội dung đã được GitHub lưu cache; khi cần xóa dữ liệu nhạy cảm khỏi cache của GitHub phải yêu cầu GitHub hỗ trợ. Không cam kết không còn thông tin nhạy cảm ngoài phạm vi đã kiểm tra.

## Kiểm tra

`tests/test_credential_security.py` kiểm tra băm/salt, không nhận mật khẩu mặc định hay rỗng, lỗi đăng nhập không tiết lộ danh tính, đóng các API công khai, tạo/reset tài khoản quản trị, migration, không phục hồi mật khẩu cũ sau reset và hủy phiên cũ. Các kiểm thử đồng bộ Desktop kiểm tra không lưu lại mật khẩu rõ.

Các ZIP đã tạo trước bản sửa bảo mật vẫn là bản cũ và chưa có những thay đổi này. Không coi kết quả QA của ZIP cũ là kiểm thử bản sửa mới; cần đóng gói lại trước khi phân phối ứng dụng đã sửa.

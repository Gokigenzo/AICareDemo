# Nhắc uống thuốc

Bản này thay Fall Detection trong ứng dụng PyQt hiện có. Nhận diện khuôn mặt, cảm xúc và phục hồi chức năng vẫn dùng camera chung; lịch thuốc không phụ thuộc camera hoặc người đang được nhận diện.

## Sử dụng

1. Cài các dependency trong `requirements-windows.txt` vào `.venv`, bao gồm `tzdata`. Chạy `START.bat` hoặc `.venv\Scripts\python.exe main.py`.
2. Trong trang **Nhận diện & Phục hồi**, đăng ký/chỉnh hồ sơ người dùng và email người chăm sóc. Mỗi hồ sơ cần có mã riêng.
3. Mở **Nhắc uống thuốc → Thêm lịch**. Chọn đúng hồ sơ; nhập nguyên văn tên thuốc, hướng dẫn theo đơn; chọn giờ, ngày bắt đầu/kết thúc, ngày trong tuần, thời gian nhắc lại và quá hạn. Mặc định múi giờ `Asia/Ho_Chi_Minh`.
4. Bấm **Xem trước 7 ngày**, kiểm tra rồi lưu. Một lịch có thể chứa nhiều giờ, ví dụ `08:00, 20:00`. Đây chỉ là ví dụ lịch, không phải chỉ định uống thuốc.
5. Khi đến giờ, ứng dụng hiện thông báo tên người, tên thuốc và hướng dẫn. Mở trang nhắc thuốc, chọn đúng dòng rồi bấm **Đã uống (tự khai)**, **Nhắc lại sau** hoặc **Bỏ qua**. Hộp thoại yêu cầu xác nhận lại đúng thuốc và giờ.
6. Dùng bộ lọc người dùng và **Lịch sử và 7 ngày sắp tới** để xem giờ dự kiến, thời điểm thao tác, trạng thái email và khoảng không giám sát. Chọn dòng để đọc đầy đủ hướng dẫn.
7. **Sửa lịch** tạo phiên bản mới cho tương lai. **Ngừng lịch** hủy các lần nhắc tương lai; lịch sử và các lần đã đến giờ giữ nguyên. Không có thao tác xóa lịch sử tự động.

“Người dùng đã xác nhận” là thông tin tự khai, không phải bằng chứng thuốc đã được uống. Ứng dụng không tính liều, kiểm tra tương tác thuốc hoặc đề xuất uống bù. Nếu lỡ liều, kiểm tra đơn hoặc hỏi bác sĩ/dược sĩ.

## Điều kiện vận hành

- Ứng dụng phải đang chạy, máy phải thức. Thu nhỏ cửa sổ vẫn nhắc; đóng cửa sổ là thoát. Chưa triển khai khay hệ thống hoặc tự khởi động cùng Windows.
- Lịch được kiểm tra mỗi 15 giây. Khi máy ngủ/tắt hoặc ứng dụng ngừng, không thể nhắc hoặc gửi email đúng giờ. Khoảng cách heartbeat trên 90 giây được ghi là gián đoạn; đổi giờ lùi được ghi riêng. Thời điểm bắt đầu/kết thúc gián đoạn có độ phân giải theo heartbeat.
- Không cam kết hoạt động 24/7. Âm thanh phụ thuộc thiết bị/Windows; popup trong ứng dụng và trạng thái chữ vẫn là kênh chính. Thông báo có thể không nhìn thấy khi khóa màn hình.
- Sau restart, các lần nhắc cũ vẫn có lịch sử. Mặc định không gửi email cho lần nhắc cũ hơn 60 phút sau gián đoạn. Không suy luận người dùng đã hay chưa uống khi không giám sát.
- Sau ít nhất 24 giờ kể từ giờ dự kiến và ít nhất 60 phút kể từ ngưỡng quá hạn, lần chưa xác nhận được ghi “Đã qua ngày — chưa có xác nhận”; vẫn cho phép xác nhận muộn và giữ thời điểm thực tế.
- Giờ mùa hè: giờ địa phương không tồn tại được bỏ qua; giờ bị lặp được chọn lần đầu duy nhất. Việt Nam không có đổi giờ mùa hè. Đổi múi giờ của lịch bằng **Sửa lịch**, không thay lịch sử.
- Đây là ứng dụng dùng trên máy tin cậy: chưa có đăng nhập/phân quyền riêng cho người chăm sóc. Người có quyền mở ứng dụng có thể sửa lịch và xem dữ liệu.

## Gmail và chính sách gửi

Tạo `.env` tại thư mục dữ liệu đang dùng hoặc cạnh `main.py`/EXE; tham khảo `.env.example`. Các trường cần thiết: `EMAIL_ENABLED`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USERNAME`, `EMAIL_PASSWORD`. Cấu hình tài khoản gửi; người nhận được lấy từ hồ sơ gắn với từng lịch, không dùng email mặc định cho người không được nhận diện.

Ngoài cấu hình Gmail, người chăm sóc phải bật **Cho phép gửi email khi quá hạn chưa xác nhận** trong từng lịch. **Kiểm tra Gmail** chỉ kết nối và xác thực, không gửi thư. Không nhập mật khẩu hoặc email thật vào tài liệu/test.

`MEDICATION_CATCHUP_MINUTES=60`: giới hạn tuổi lần nhắc được gửi khi bắt kịp sau gián đoạn. `MEDICATION_ALERT_LIMIT=3`: giới hạn tổng lượt thử gửi trong một giờ, bền vững qua restart. Sửa `.env` rồi khởi động lại để áp dụng. Các giới hạn đang dùng được hiển thị trên trang.

Mỗi lần gửi được đánh dấu trong SQLite trước khi chạy worker. Lỗi kết nối trước khi nộp thư được thử tối đa 3 lượt, giãn cách 2 rồi 4 phút và chịu giới hạn giờ. Lỗi xác thực, thiếu cấu hình/email hoặc từ chối người nhận được ghi rõ và không tự lặp. Sửa cấu hình chỉ có hiệu lực cho các lần gửi tương lai; các lỗi cấu hình cũ không tự gửi bù.

Khi không rõ SMTP đã nhận thư chưa, hoặc ứng dụng dừng giữa lúc gửi, trạng thái là **Không rõ; không tự gửi lại**. Cách này ưu tiên tránh gửi trùng và có thể bỏ lỡ email. **SMTP chấp nhận** không có nghĩa thư đã vào inbox hoặc đã được đọc. Email chỉ báo “chưa có xác nhận cho liều dự kiến”.

## Dữ liệu, sao lưu và khôi phục

| Cách chạy | Cơ sở dữ liệu lịch thuốc |
| --- | --- |
| `python main.py`, không bật portable | `data/medication.sqlite3` trong thư mục dự án |
| `START.bat`, `PORTABLE_MODE=1`, hoặc có thư mục `runtime` | `runtime/medication.sqlite3` |
| EXE cài đặt, không portable | `%LOCALAPPDATA%/AIRehabilitationAssistant/data/medication.sqlite3` |
| `--test` hoặc `AI_CARE_TEST_MODE=1` | Thư mục kiểm thử riêng, không sao chép hồ sơ thật |

Đóng ứng dụng trước khi sao lưu toàn bộ thư mục dữ liệu đang dùng, gồm SQLite, `users`, các dữ liệu `shared` và cấu hình cần thiết. Không đưa bản sao lên Git hoặc chia sẻ công khai. Dữ liệu hiện chưa mã hóa ở mức ứng dụng; dùng quyền tài khoản Windows và quyền thư mục để hạn chế truy cập. Không đóng gói hồ sơ thật vào EXE.

Lần chạy đầu lưu bản sao `shared/state.json` và `shared/results/fall.json`, nếu có, vào `<DATA_DIR>/archive/fall_detection/`. Migration chạy lại không ghi đè bản sao. Hồ sơ, email và các trường cũ được giữ nguyên. Thư mục `fall_events`, ảnh, video và báo cáo cũ giữ nguyên vị trí, được xem là lưu trữ lịch sử; không có thời hạn xóa tự động.

Rollback mã nguồn: đóng ứng dụng, sao lưu dữ liệu thuốc, rồi khôi phục **có chọn lọc** các file mã từ `reports/medication_migration/before.zip`. Bản zip này là bản sao trước triển khai, chứa cả thay đổi chưa commit của người dùng; không dùng `git reset --hard`. Các test và launcher cũ được giữ trong `archive/fall_detection/`. Không khôi phục đè hồ sơ hiện tại bằng dữ liệu cũ. Mã cũ không đọc SQLite thuốc; giữ file này để quay lại phiên bản mới.

## Kiểm thử và bằng chứng

```powershell
.venv\Scripts\python.exe scripts/verify_medication.py
.venv\Scripts\python.exe main.py --test
.venv\Scripts\python.exe scripts/verify_medication_bundle.py
```

Runner dùng dữ liệu tạm và chặn SMTP. `EmailService` cũng khóa mạng khi có `--test`, `AI_CARE_TEST_MODE=1`, `pytest` hoặc `unittest`, kể cả có credentials thật. Các ca mô phỏng SMTP chỉ thay transport bằng mock. Không gửi email thật trong nghiệm thu này.

Lệnh `verify_medication_bundle.py` cần build debug trước theo hướng dẫn Windows. Xem [báo cáo nghiệm thu](acceptance_report.md), [kiểm kê migration](migration_inventory.md) và [ảnh giao diện với dữ liệu mẫu](screenshots/medication_sample.png).

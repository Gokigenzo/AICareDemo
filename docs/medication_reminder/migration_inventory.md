# Kiểm kê thay Fall Detection bằng nhắc thuốc

Ngày bàn giao: 03/10/2026. Nguồn yêu cầu: `KE_HOACH_THAY_FALL_DETECTION_BANG_NHAC_UONG_THUOC.md`.

## Trạng thái trước sửa

Repository có nhiều thay đổi chưa commit. Đã sao lưu file mã/cấu hình/tài liệu và JSON hiện có vào `reports/medication_migration/before.zip` trước khi chỉnh. Không commit, reset hoặc ghi đè thay đổi của người dùng. Bản sao này được loại khỏi Git vì có thể chứa hồ sơ riêng tư.

Baseline Windows/Python 3.12: **132 tests; 12 failures, 1 error**. Bằng chứng: `reports/medication_migration/baseline.txt`; console: `baseline_console.txt`. Cách chạy: `unittest.defaultTestLoader.discover('tests')` với `QT_QPA_PLATFORM=offscreen`, `smtplib.SMTP` bị mock chặn mạng. Vì có chặn mạng, đây là baseline an toàn trong môi trường kiểm thử, không phải kiểm tra Gmail thật. File JSON bị các test cũ chạm tới đã được đối chiếu và khôi phục đúng byte từ bản sao trước tác vụ; file `shared/data/patient.json` vốn đã bị xóa trước tác vụ được trả về trạng thái không tồn tại.

## Bản đồ phụ thuộc và quyết định

Ghi nhận khi tiếp tục ngày 03/10: hồ sơ `1`, danh sách bệnh nhân và dữ liệu phiên trong `shared` đã có cập nhật sau lần đối chiếu ban đầu (01:37–01:39), bao gồm việc tạo lại `shared/data/patient.json`. Giữ nguyên toàn bộ trạng thái mới, không lặp thao tác phục hồi baseline lên dữ liệu này. Snapshot riêng lúc tiếp tục được lưu cục bộ trong `reports/medication_migration/resume_data_snapshot.zip`, không đưa vào Git. Các cập nhật dữ liệu này không được tính là thay đổi triển khai mã.

| File / nhóm file | Nơi được gọi | Dữ liệu | Quyết định |
| --- | --- | --- | --- |
| `main.py` | `START.bat`, Python, PyInstaller | khóa ứng dụng theo DATA_DIR | Giữ entry point; thêm chống chạy hai scheduler cùng dữ liệu, đóng sạch khi `--test` |
| `app/dashboard.py` | main | camera, face/emotion/rehab telemetry | Tháo UI/video/timeline và xử lý frame của fall; gắn tab medication |
| `app/router.py`, `adapters/__init__.py` | dashboard | adapters | Bỏ khởi tạo và import eager FallAdapter; giữ 3 adapter camera |
| `core/camera_manager.py`, `core/frame_source.py` | camera/legacy tools | camera lease và frame | Giữ dùng chung; medication không đăng ký processor hoặc mở camera |
| `adapters/fall_adapter.py`, `services/fall_monitor.py`, `services/fall_test_runner.py`, `core/fall_*`, `modules/fall/`, `app/fall_video_worker.py` | Chỉ công cụ lịch sử | model và sự kiện ngã cũ | Giữ nguồn lịch sử tại chỗ; không import từ ứng dụng/không đưa vào spec |
| `services/email_service.py` | medication worker | SMTP credentials | Tái dùng cấu hình, bỏ dispatch fall, thêm sự kiện MEDICATION_OVERDUE và chặn test tại lõi |
| `services/user_service.py` | đăng ký, editor, worker | JSON hồ sơ/caregiver | Giữ định danh và email; bảo toàn trường mở rộng khi lưu; không log email |
| `services/medication_service.py` | panel, test | SQLite | Mới: schema v1, revision, occurrence duy nhất, lịch lặp, coverage, lịch sử, claim/retry |
| `app/medication_panel.py` | dashboard | lịch, thao tác tự khai | Mới: editor, preview, popup, lịch sử, bộ lọc hồ sơ, worker email |
| `services/medication_migration.py` | dashboard lúc mở | snapshot state/fall.json | Mới: bản sao một lần, không xóa hay ghi đè nguồn |
| `config.py`, `.env.example` | tất cả | đường dẫn runtime, chính sách nhắc | Thêm test isolation, catch-up/rate limit; bỏ fall khỏi mẫu cấu hình |
| `app/registration_dialog.py` | dashboard | hồ sơ | Sửa thông báo pause để không tuyên bố còn giám sát ngã |
| `app/launcher.py` | module launcher | camera-bound set | Bỏ fall khỏi danh sách module camera đang hỗ trợ |
| `requirements*.txt` | setup | dependency | Thêm tzdata; gỡ ultralytics/APScheduler khỏi requirements chính; giữ OpenCV/MediaPipe/PyTorch |
| Hai file `.spec`, `packaging/windows_dependency_scan.py` | PyInstaller 6.22.3 | model, package, native DLL | Bỏ fall assets/imports; thêm tzdata/SQLite/module thuốc; không bundle hồ sơ thật; dò DLL từ đường dẫn native để tránh import Qt trước MediaPipe trong bước build |
| Test fall và acceptance UI cũ | bộ test lịch sử | fixture ngã/video | Chuyển sang `archive/fall_detection/tests`; không dùng làm bằng chứng medication |
| `tests/test_medication*.py`, `scripts/verify_medication.py` | unittest | dữ liệu mẫu và đồng hồ giả | Thêm kiểm thử medication, UI, SMTP mock, archive idempotent; giữ test face/rehab/launcher/state |
| `demo.py`, `simulate_fall_alert.py`, `START_HFD.bat` cũ | công cụ lịch sử | mô phỏng ngã | Chuyển vào `archive/fall_detection`; không còn launcher fall ở gốc |
| `docs/fall_detection/`, báo cáo kỹ thuật fall | tài liệu tham khảo | kết quả cũ | Gắn nhãn lịch sử, giữ nội dung; không dùng để chứng minh tính năng mới |

Luồng hiện tại: `main → dashboard → MedicationPanel → MedicationService(SQLite)`; `MedicationPanel → worker → EmailService → SMTP`. Nhận diện, cảm xúc và rehab vẫn đi qua `CameraManager → DashboardRouter → adapter`. Email nhận theo patient_id của occurrence, không theo khuôn mặt hiện tại.

## Dữ liệu và rollback

Không chuyển đổi các sự kiện ngã thành lần uống thuốc. SQLite thuốc là schema độc lập. Unique key `(schedule_id, revision, due_at_utc)` được thực thi bởi SQLite. Lịch cũ và hành động được giữ lại; chỉnh sửa chỉ hủy occurrence tương lai còn PENDING. Migration lưu trữ JSON có thể chạy lại, không thay bản sao đầu tiên. Những hằng số/schema fall còn trong mã lịch sử không tham gia UI hoặc scheduler mới.

Sự kiện, ảnh/video và mô hình lịch sử không tự xóa. Giữ vô thời hạn cho tới khi chủ dữ liệu quyết định; xem đường dẫn và quy trình rollback trong `README.md` cùng thư mục. Không cần migration xóa trường `fall_*` trong hồ sơ vì trường cũ được bảo toàn và không được hiển thị như chức năng đang chạy.

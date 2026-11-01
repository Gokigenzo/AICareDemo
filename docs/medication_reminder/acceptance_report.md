# Nghiệm thu nhắc uống thuốc

Ngày: 03/10/2026. Môi trường: Windows, Python 3.12.13 trong `.venv`, PyQt5, SQLite và tzdata 2026.4. Báo cáo này không dùng kết quả Fall Detection để xác nhận tính năng thuốc.

## Kết quả đã chạy

| Kiểm tra | Kết quả | Bằng chứng |
| --- | --- | --- |
| Baseline trước sửa | 132 test; 12 thất bại, 1 lỗi | `reports/medication_migration/baseline.txt` |
| Bộ test hiện tại | **PASS — 53/53** | `reports/medication_migration/verification.txt` |
| Dashboard đầy đủ, chuyển tab, xử lý frame giả, hai hồ sơ, đóng sạch | **PASS** | `reports/medication_migration/dashboard_smoke.txt` |
| Không import fall trong dashboard mới | **PASS** | Assertion trong `scripts/smoke_medication.py` |
| Không kết nối SMTP trong test | **PASS** | Network guard tại lõi; runner mock chặn SMTP; các test SMTP dùng transport giả |
| Bảo toàn dữ liệu khi migration và kiểm thử | **PASS** trong test migration; giữ nguyên cập nhật mới sau gián đoạn | Đối chiếu ban đầu không có thay đổi JSON. Khi tiếp tục, dữ liệu có cập nhật lúc 01:37–01:39 ngày 03/10; không khôi phục đè từ snapshot cũ |
| Đóng gói EXE Windows | **PASS** — PyInstaller 6.22.3 | `reports/medication_migration/build_final.txt` |
| EXE `--test`, thoát mã 0; nạp DNN face, ExpressionNet, FaceMesh và Pose | **PASS** — camera giả lập, dữ liệu tạm | `reports/medication_migration/exe_smoke.txt`, `exe_exit.txt` |
| Mã trong EXE khớp nguồn, không có module fall/hồ sơ thật, có tzdata | **PASS** | `reports/medication_migration/bundle_audit.txt` |

Lệnh tái hiện:

```powershell
.venv\Scripts\python.exe scripts/verify_medication.py
.venv\Scripts\python.exe scripts/smoke_medication.py
.venv\Scripts\python.exe main.py --test
.venv\Scripts\python.exe scripts/verify_medication_bundle.py
```

Test hiện tại gồm các test face/rehab/camera/launcher/state được giữ lại và các test medication mới. Các bộ acceptance fall/UI cũ đã chuyển vào `archive/fall_detection/tests`, không bị đổi kỳ vọng thành PASS và không được tính vào 53 test hiện tại.

Bản Windows nằm tại `dist/medication/AI_Rehabilitation_Assistant_DEBUG/AI_Rehabilitation_Assistant_DEBUG.exe`. Cần giữ toàn bộ thư mục ONEDIR cạnh EXE. Đây là bản debug có console; chưa tạo installer hoặc kiểm thử máy Windows sạch. Build trước đó mở UI được nhưng thiếu matplotlib nên không được tính PASS. Spec cuối đã giữ matplotlib với backend Agg và sửa bước dò DLL; log EXE cuối xác nhận các module AI khởi tạo đầy đủ.

## Đối chiếu M01–M09

| Mã | Đã kiểm chứng | Trạng thái cổng đầy đủ |
| --- | --- | --- |
| M01 | Lịch đến giờ, popup đúng thông tin mẫu, xác nhận idempotent, persisted occurrence và thời điểm thao tác | PASS trong kiểm thử Windows tự động |
| M02 | Hai thuốc/hồ sơ cùng giờ, lọc độc lập, caregiver email theo patient_id; mock kiểm tra hai người nhận khác nhau | PASS trong kiểm thử Windows tự động |
| M03 | Hoãn và nhắc lại cùng occurrence, bỏ qua kết thúc, quá hạn nhận xác nhận muộn với giờ thực tế | PASS trong kiểm thử Windows tự động |
| M04 | Mở lại repository, heartbeat bị gián đoạn, khôi phục nhiều ngày, không gửi dồn thư cũ, thông báo chưa hiển thị tồn tại qua restart | **NOT VERIFIED toàn bộ** — Windows sleep/resume và thông báo khi thu nhỏ/khóa màn hình trên máy người dùng chưa kiểm chứng; khay hệ thống chưa triển khai |
| M05 | Clock backward không duplicate; midnight, end date, timezone revision; edit đúng thời điểm due; hủy future giữ history; DST thiếu giờ/lặp giờ | PASS với đồng hồ giả trên Windows |
| M06 | Thiếu cấu hình/email không kết nối; SMTP mock accepted, lỗi trước gửi, lỗi không rõ khi nộp thư; retry tối đa 3, backoff và giới hạn giờ; crash claim không tự gửi lại | PASS với mock; **Gmail/mất mạng thực tế NOT VERIFIED** |
| M07 | Cấu hình SMTP giả đầy đủ nhưng test mode chặn trước kết nối; runner dùng thư mục tạm, không seed dữ liệu thật; zero SMTP | PASS |
| M08 | Dashboard khởi động, adapter face/emotion/rehab nạp, xử lý frame giả, đổi tab, đóng sạch, zero fall imports | **NOT VERIFIED toàn bộ** — camera và người tập thật chưa có; EXE được ghi riêng trong bảng kết quả |
| M09 | Migration chạy hai lần không đè archive; source còn nguyên; profile/email được bảo toàn; SQLite và test paths riêng | PASS cho migration và dữ liệu; quyền thư mục trên máy triển khai cần kiểm tra tại máy đó |

Không tuyên bố cổng MVP M01–M09 đã PASS toàn bộ. Bản này là triển khai chức năng nhắc **khi ứng dụng đang mở**, cần nghiệm thu phần phần cứng/vận hành trước khi phát hành chính thức.

## Bằng chứng giao diện

- [Trang nhắc thuốc trong dashboard](screenshots/dashboard_medication.png)
- [Trang phục hồi chức năng](screenshots/dashboard_rehabilitation.png)
- [Panel với hai hồ sơ mẫu](screenshots/medication_sample.png)

Ảnh dùng hồ sơ mẫu và đồng hồ giả. Không dùng dữ liệu thuốc hoặc địa chỉ người thân thật. Thời gian thanh tiêu đề là giờ hệ thống khi chụp, còn lịch mẫu cố định ngày 02/10/2026 để tái hiện test.

## Giới hạn và quyết định phát hành

Chưa có khay hệ thống, tự khởi động Windows, tài khoản/phân quyền chăm sóc hoặc mã hóa cơ sở dữ liệu. Đóng cửa sổ dừng nhắc; khi máy ngủ/tắt không có dịch vụ máy chủ bù giờ. SMTP không hỗ trợ bảo đảm chính xác một lần trên mạng: kết quả không rõ không tự gửi lại để tránh trùng; điều này có thể làm thiếu email. Không tự gửi lại các lỗi cấu hình đã ghi trong lịch sử.

Chỉ phát hành như công cụ ghi lịch và nhắc tại máy, không công bố giám sát 24/7 hoặc xác nhận việc uống thuốc thực tế. Chưa phát hành/triển khai ra máy người dùng trong tác vụ này. Không gửi email thật.

Hướng dẫn cấu hình, sao lưu và rollback: [README](README.md). Các bước còn cần kiểm tra: [Windows thực tế](manual_windows_checks.md). File thay đổi từ bản sao trước tác vụ: `reports/medication_migration/changes_since_backup.txt`.

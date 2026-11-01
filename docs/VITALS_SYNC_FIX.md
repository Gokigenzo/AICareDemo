# Sửa luồng lưu và đồng bộ chỉ số sức khỏe — 15/10/2026

## Nguyên nhân được xác minh

CSDL đang chạy tại `runtime/unified_care.sqlite3` có 0 dòng trong
`observation_types`, 1 nhóm đo nhưng 0 dòng `health_observations`.
Danh mục chỉ số trước đây được tạo bởi legacy importer, trong khi web server
khởi động chỉ chạy migrations. API bỏ qua loại chỉ số không tìm thấy rồi vẫn
commit nhóm đo và trả 201, dẫn tới lịch sử toàn `--` và biểu đồ không có dữ liệu.

Ngoài ra, `ElderSyncClient.get_today_snapshot` chỉ tìm mã `bp_systolic` /
`bp_diastolic`, khác mã `blood_pressure_systolic` / `blood_pressure_diastolic`
được form và API sử dụng.

## Thay đổi

- Migration 008 bổ sung 7 loại chỉ số cho cả cài mới và CSDL hiện có,
  giữ nguyên các mã định danh đã tồn tại.
- API xác thực toàn bộ danh sách trước khi ghi: từ chối loại chỉ số không tồn tại,
  thiếu giá trị, giá trị không phải số hữu hạn hoặc trùng loại trong một lần đo.
  Không tạo nhóm đo, số đo một phần hay sự kiện thành công khi đầu vào lỗi.
- Nếu không truyền đơn vị, API dùng đơn vị chuẩn của loại chỉ số.
- ElderSyncClient đọc được cả mã huyết áp hiện hành và mã cũ.
- Giữ cơ chế outbox/SSE hiện có để hai cổng tải lại dữ liệu sau khi commit;
  widget desktop cập nhật qua timer hiện có.

## Kiểm chứng

13 kiểm thử tại `tests/test_vitals_sync_regression.py` đạt trên CSDL riêng,
chỉ tạo bằng migrations, không chạy legacy importer:

- Lưu đủ 6 giá trị, lịch sử và dữ liệu biểu đồ đọc đúng qua phiên bác sĩ/người nhà.
- Overview hai vai trò và snapshot người cao tuổi có huyết áp/nhịp tim mới.
- Widget PyQt thực tế hiển thị 128/84 mmHg sau refresh.
- Relay gửi `health.observation_created` đến cả hai client SSE được phân quyền.
- Gửi lặp không tạo thêm số đo; batch lỗi không để lại dữ liệu một phần.
- Migration chạy lại giữ nguyên ID danh mục đã có.

Lệnh đã chạy (PowerShell, từ thư mục AICareDemo):

```powershell
$env:AI_CARE_TEST_DATA_DIR = Join-Path (Get-Location) 'runtime/test-vitals-app-03'
.\.venv\Scripts\python.exe -m pytest tests/test_vitals_sync_regression.py -q --basetemp=runtime/test-vitals-03 --tb=short
```

Kết quả: `13 passed, 2 warnings` (cảnh báo protobuf có sẵn).
Không kiểm chứng trực quan trên browser: trình duyệt Codex không kết nối được
máy chủ localhost thử nghiệm ở cổng 8098. Chưa khẳng định đã kiểm thử thao tác
form và vẽ SVG trực tiếp trên trình duyệt.

## CSDL demo hiện tại

Đã sao lưu bằng SQLite backup API tới
`runtime/backups/before_vitals_fix_20261015_141555.sqlite3`, rồi áp dụng migration
008 thành công: danh mục hiện có 7 loại. Không thêm số đo thử vào CSDL này.
Nhóm đo rỗng cũ được giữ nguyên; các giá trị đã bị API cũ bỏ qua không thể
khôi phục từ CSDL, cần nhập lại từ kết quả đo gốc.

Khởi động lại demo để backend và desktop nạp mã mới, tải lại các trang web.

## Giới hạn công cụ khảo sát

Đã đọc skill codebase-memory tại cấu hình Copilot. Session không có các tool
graph và binary cũ `F:/codebase-memory/codebase-memory-mcp.exe` không tồn tại;
truy vết được thực hiện bằng đọc/tìm trực tiếp nguồn và kiểm thử, không tuyên bố
đã xác minh graph hoặc index coverage.

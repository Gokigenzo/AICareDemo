> C?p nh?t 02/10/2026: ?? tri?n khai prototype pose/tracking v3 v? backend ONNX local. Clip ngu?n v?n 0 s? ki?n x?c nh?n; accuracy NOT VERIFIED. Xem [k?t qu? tri?n khai v3](fall_detection/BAO_CAO_TRIEN_KHAI_POSE_TRACKING_V3.md). N?i dung/s? li?u v2 b?n d??i l? baseline l?ch s?.

# Biên bản hoàn tất kiến thức, audit và kế hoạch

Ngày đối chiếu: 02/10/2026. Phạm vi hoàn tất: yêu cầu đọc/ghi kiến thức vào codebase, chỉ ra cải thiện và lập kế hoạch module. Không đánh dấu toàn bộ backlog nâng cấp runtime đã hoàn thành.

## Đầu ra

- PROJECT_KNOWLEDGE.md đã cập nhật kiến trúc shared FallPipeline v2; phân biệt core đang chạy với detector/FSM legacy.
- CODEBASE_AUDIT.md giữ 23 mục baseline và có bảng trạng thái hiện tại, tránh báo lỗi đã sửa như lỗi còn tồn tại.
- UPGRADE_PLAN.md có dependencies, nghiệm thu, backlog từng module và tiến độ G0–G7 theo bằng chứng.
- codebase_inventory.json được tạo lại từ working tree: 116 file, 95 Python; hash, import và symbols phục vụ tra cứu. Không import mã ứng dụng khi inventory.
- codebase-memory được truy cập bằng CLI binary cục bộ; graph và ADR cập nhật với kiến trúc mới. Skill không được cấp trong danh mục session; không tuyên bố đã dùng skill/hot-load MCP tools.

## Kiểm tra đã chạy lại

| Kiểm tra | Kết quả | Bằng chứng |
|---|---|---|
| Python/spec AST parse | Không lỗi | Inventory script output |
| Inventory `--check` | Khớp snapshot | Chạy sau regenerate |
| `test_fall_pipeline_v2.py` qua harness | 24 chạy, 0 failures/errors/skips | [summary](../reports/fall_detection/knowledge_completion_core/summary.json), [unittest](../reports/fall_detection/knowledge_completion_core/unittest.txt) |
| `test_fall_ui_v2.py` qua harness | 1 chạy, 0 failures/errors/skips | [summary](../reports/fall_detection/knowledge_completion_ui/summary.json), [unittest](../reports/fall_detection/knowledge_completion_ui/unittest.txt) |

Lệnh dùng `.venv/Scripts/python.exe scripts/run_fall_checks.py --pattern <tên test> --output <thư mục trên>`. Harness redirect runtime constants sang thư mục tạm và chặn SMTP/SMTP_SSL mặc định; core tests dùng fake backend/mock SMTP, UI patch camera start và tạo clip tạm. Config được import trước patch nên có thể khởi tạo logging/thư mục nguồn; harness này chưa phải isolation hoàn toàn cho mọi test. Không chạy full suite hay camera/SMTP thật trong lần hoàn tất này.

## Giới hạn còn lại

25 tests kiểm tra hợp đồng/FSM/lifecycle, không xác nhận accuracy. Không chạy lại batch video thật: số liệu 0/2 candidate và hiệu năng được dẫn từ [báo cáo có sẵn](../reports/fall_detection/BEFORE_AFTER.md), không coi là phép đo mới trong session này. Backend HOG/crop-pose vẫn FAIL/NOT VERIFIED; live event ở bộ nhớ với DRY_RUN_NOT_VALIDATED. Cần dataset/nhãn spatial độc lập và backend phù hợp trước vận hành cảnh báo thật.

Các mục còn lại là backlog phát triển: state/profile repository atomic, identity TTL, callback cleanup, rehab/emotion, durable delivery, performance/UI và clean packaging. Không sửa/revert các thay đổi runtime người dùng đã có để hoàn tất đợt audit này.

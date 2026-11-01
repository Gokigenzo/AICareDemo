> C?p nh?t 02/10/2026: ?? tri?n khai prototype pose/tracking v3 v? backend ONNX local. Clip ngu?n v?n 0 s? ki?n x?c nh?n; accuracy NOT VERIFIED. Xem [k?t qu? tri?n khai v3](fall_detection/BAO_CAO_TRIEN_KHAI_POSE_TRACKING_V3.md). N?i dung/s? li?u v2 b?n d??i l? baseline l?ch s?.

# Audit mã nguồn và khoảng trống kiểm chứng

## Cập nhật sau FallPipeline v2

Bảng A01–A23 bên dưới là **baseline của audit ban đầu**, giữ lại để truy nguyên. Đối chiếu working tree ngày 02/10/2026 cho thấy một số lỗi đã thay đổi; không dùng bảng baseline như danh sách lỗi còn nguyên. Chi tiết kiểm tra ở [KNOWLEDGE_COMPLETION.md](KNOWLEDGE_COMPLETION.md).

| Mục baseline | Trạng thái hiện tại |
|---|---|
| A01 | Identity forwarding/TTL còn cần sửa; camera trial hiện không dispatch thật nên rủi ro recipient chưa kích hoạt trong pipeline mới |
| A02 | Còn tồn tại: StateService chưa lock/atomic và fallback NORMAL |
| A03 | Đã thêm capture_valid/capture_pts; dashboard gate theo validity, source chặn timestamp trùng; cần kiểm tra capture stalled thực và telemetry/UI |
| A04 | Live/video đã dùng chung core; MOG2 chuyển experiments. Benchmark/demo cũ vẫn phải rà; candidate HOG bỏ sót hai nhãn ngã theo báo cáo đã có |
| A05–A06 | Packaging dữ liệu và full-suite side effects còn cần xử lý; harness run_fall_checks đã cô lập phần regression được chọn |
| A07 | API CameraFrameSource đã sửa, regression kiểm tra pause/resume/freshness pass |
| A08 | Stop đã wait/join, restart có guard; close window vẫn chưa unregister processor/disconnect signal, chưa nghiệm thu 50 vòng lifecycle |
| A09 | Callback bỏ qua mode registration; concurrency train/model ở các luồng khác còn cần kiểm chứng |
| A10 | Repository legacy/multiple profiles vẫn cần thống nhất |
| A11 | Camera trial-only, dispatch legacy bị chặn; delivery có in-process idempotency và xử lý timeout submission unknown, chưa có durable outbox |
| A12 | Core mới scale góc bằng kích thước ảnh, dùng downward speed/upright-to-low; detector cũ còn tồn tại nhưng không quyết định sự kiện core |
| A13 | Core track TTL và history bounded; runner seek tạo run và replay từ đầu, lifecycle regression pass; replay sync/per-run trace vẫn cần kiểm tra clip dài |
| A14 | Evaluator mới ràng buộc SHA, subject spatial matching, one-to-one, partial/NOT VERIFIED; thiếu bbox/adjudication thực và dataset độc lập |
| A15–A18 | Backlog rehab/emotion/settings còn tồn tại, không tự đánh dấu đã sửa bởi thay đổi fall |
| A19 | Tests v2 xác nhận event thật được tạo và SMTP spies không gọi; assertion/tests legacy chưa được thay thế toàn bộ |
| A20–A23 | Còn trong backlog: launcher alias, controllers/performance, packaging/CI, calibration và subject split |

**Phát hiện mới P0:** shared HOG/crop-pose candidate chưa đạt regression clip chuẩn (báo cáo có 0 sự kiện so với 2 nhãn ngã). Camera đang trial-only là giới hạn có chủ đích; không bật gửi thật khi chưa có backend và validation đạt yêu cầu. 25 contract/UI tests pass không chứng minh phát hiện ngã thực tế đạt chuẩn.

## Baseline lịch sử

Ngày: 02/10/2026. Phạm vi: nguồn ứng dụng, modules, standalone/archive, tests, experiments, script và đóng gói trong working tree. Không đọc nội dung credentials/hồ sơ cá nhân để đưa vào báo cáo. Binary model/video, output build và dependency vendor không phải mã nguồn được đánh giá. Các phát hiện dưới đây dựa trên đọc mã; chưa phải kết quả chạy camera/SMTP hoặc chứng nhận accuracy.

P0: xử lý trước khi dùng kết quả để đánh giá/đóng gói giao người dùng. P1: tính đúng đắn và ổn định. P2: khả năng bảo trì và hiệu năng. Các đường dẫn chỉ rõ nơi kiểm tra lại, không khẳng định mọi rủi ro đã xảy ra trên máy.

| ID | Mức | Bằng chứng trong nguồn | Hệ quả và hướng sửa |
|---|---|---|---|
| A01 | P0 | `app/dashboard.py:update_dashboard_ui` chỉ gọi `update_recognized_user` ở nhánh recognized; `services/fall_monitor.py` giữ user hiện tại | Unknown/no_face có thể giữ người nhận trước đó. Truyền identity snapshot có TTL và chính sách người chưa xác định; test chuyển A → unknown → ngã |
| A02 | P0 | `services/state_service.py` read-modify-write không lock; nhiều adapter ghi state/results; lỗi đọc fallback NORMAL | Mất cập nhật, JSON đọc dở, biểu hiện an toàn khi dữ liệu lỗi. Một owner trạng thái, snapshot revision, atomic file replace, DEGRADED khi lỗi |
| A03 | P0 | `core/camera_manager.py:run` lỗi read chuyển simulated frame nhưng không hạ hardware flag; dashboard truyền `frame_fresh=True` | Camera mở không đồng nghĩa đang có ảnh mới. Frame sequence/capture time/source health phải điều khiển observability |
| A04 | P0 | `services/fall_test_runner.py` MOG2/ROI fixed; `experiments/benchmark.py` có fall rates hằng số; README/báo cáo có khẳng định độ chính xác mạnh | Chỉ số hiện không đủ xác nhận pipeline live. Tách tên pipeline, dataset/hash/coverage, bỏ metric giả và đánh giá tập độc lập |
| A05 | P0 | `packaging/portable/build_portable.py` copy shared và data/users; các spec bundle dữ liệu | Nguy cơ phát hành hồ sơ/ảnh mặt có sẵn. Allowlist tài nguyên, fixture ẩn danh, kiểm tra không có patient data/credentials trong artifact |
| A06 | P0 | `tests/test_source_capabilities.py` gọi luồng confirm với service mặc định; UserService temp vẫn dùng legacy global | Full suite có thể ghi dữ liệu thật hoặc gửi email nếu máy đã cấu hình. Inject repositories, fake camera/clock/delivery và chặn socket ở test |
| A07 | P1 | `core/frame_source.py:CameraFrameSource` gọi `get_raw_frame`, `pause_camera`, `resume_camera`; manager có `get_latest_frame`, `pause`, `resume` | Hợp đồng adapter hỏng nếu dùng lớp này. Sửa API và test với fake manager |
| A08 | P1 | `core/camera_manager.py` stop release capture trong khi worker read, chưa wait; `app/dashboard.py:closeEvent` chưa unregister callback | Race chuyển mode/đóng cửa sổ, callback tồn tại, buffer QImage không copy rõ ownership. Capture owner, stop/join, disconnect và ảnh sở hữu bộ nhớ |
| A09 | P1 | Dashboard/registration dùng cùng face detector ở worker và GUI; train LBPH trong save modal | Race OpenCV và UI đứng. Serialize model access, train worker rồi hoán đổi model snapshot |
| A10 | P1 | `face_adapter.py:delete_patient` không xóa data/users; `user_service.py` có nguồn legacy; ID không kiểm tra containment | Hồ sơ đã xóa còn chọn được, ID có thể thoát thư mục. Repository duy nhất, validate ID, delete nhất quán, báo lỗi I/O |
| A11 | P1 | `services/fall_monitor.py` daemon delivery, event ID giây, persist JSON trực tiếp; imwrite không kiểm tra kết quả | Mất retry khi thoát, collision và bằng chứng không đầy đủ. UUID, atomic event, durable outbox/idempotency, graceful shutdown |
| A12 | P1 | `modules/fall/fall_detector.py` torso angle tính từ x/y chuẩn hóa chưa scale w/h; velocity chưa dùng, chưa đo immobility | Góc phụ thuộc aspect ratio; tài liệu “bất động/động học” vượt khả năng code. Sửa hệ tọa độ, kiểm định theo góc camera; temporal features chỉ thêm sau baseline |
| A13 | P1 | `services/fall_test_runner.py` missing track giữ bbox/timer, không xóa track/history; seek UI không reset runner | Evidence cũ kéo dài, tăng bộ nhớ, replay không tất định. Track expiry, bounded history, reset/replay khi seek |
| A14 | P1 | Runner ghép GT bằng tên fall_P1/P2 + vùng x, chưa ràng buộc SHA; report xuất khi chưa EOF; smtp_called là hằng False | Metric trên clip khác/clip chưa hoàn tất dễ bị hiểu sai. Matcher theo event/IoU/time, validity flag, coverage và đo dry-run bằng spy |
| A15 | P1 | `rehab_engine.py` arm/sit/march 10/10/15; config 12/10/20; penalty cộng theo frame; march tăng khi nhấc chân | Mục tiêu bất nhất, điểm thay đổi theo FPS, rep chưa là chu kỳ hoàn chỉnh. Spec dùng chung, penalty theo thời lượng/sự kiện, định nghĩa rep rõ ràng |
| A16 | P1 | `rehabilitation_adapter.py` payload patient_001, chưa persist session; process không kiểm tra active | Session sai identity/khó tổng kết. Session ID, patient snapshot, lifecycle rõ, lưu summary khi stop |
| A17 | P1 | `emotion_adapter.py` torch import bắt buộc dù có FACS; rehab chỉ get_result; default neutral confidence cao | Dependency lỗi làm mất fallback, cảm xúc cũ trông như mới. Backend độc lập, timestamp/TTL ở getter, UNKNOWN khi không quan sát |
| A18 | P1 | `config.py` dotenv tải sau quyết định writable root; seed không copy thư mục registered_faces; runner output tương đối | Portable/env/path không nhất quán. Load settings trước, resource/read/write roots rõ, migration có phiên bản |
| A19 | P1 | `tests/test_plan_acceptance_u01_u03_f01_f05_r01.py`: so FALL_CONFIRMED trong runner dùng CONFIRMED, F05 dùng tên env không khớp config | Assertion có thể pass mà không kiểm tra điều mong muốn. Assert kích hoạt nhánh, đủ event và cấu hình thực tế; fixture video sinh được |
| A20 | P2 | `app/launcher.py` dùng sys không import khi alias python; PIPE chưa drain | Launcher legacy có NameError hoặc nghẽn. Import/sử dụng PYTHON_EXE, quản lý output và process cleanup |
| A21 | P2 | Dashboard xử lý UI, inference, identity, playback, reports; logger file không rotation | Khó sửa/đo latency. Tách controllers, pipeline và view; telemetry latency/FPS/age, rotating logs |
| A22 | P2 | CI cài requirements legacy, chưa test; hai spec và hook chưa gắn; batch python path có khoảng trắng | Build thiếu tái lập. Một manifest runtime, test CI cô lập, smoke portable trên máy sạch |
| A23 | P2 | `modules/emotion/src/data.py` split theo session; adapter ép năm lớp về ba; confidence LBPH/FACS chưa calibrate | Chưa đo tổng quát theo người/độ tin cậy. Subject-disjoint eval, taxonomy thống nhất, calibration/rejection |

## Tài liệu và demo cần sửa theo bằng chứng

`docs/BAO_CAO_KY_THUAT_FALL_DETECTION.md` mô tả live threshold 0.65, confirm 1 giây, cooldown 5 giây; `config.py` mặc định 0.75/3/30. Báo cáo mô tả multi-person/video riêng nhưng một số kết luận chung dễ bị áp sang live. Không có căn cứ từ source để bảo đảm “không bao giờ gộp người”, “triệt tiêu hoàn toàn báo động giả” hoặc suy ra accuracy tổng quát từ một clip.

`generate_user_guide_docx.py` chứa khẳng định bài tập được chứng nhận, giọng nói/chuông/báo cáo và hiệu năng chưa được chứng minh đầy đủ bởi luồng dashboard hiện tại. `demo.py` có nội dung minh họa dựng sẵn; `simulate_fall_alert.py` trống. Nên gắn nhãn demo, trích thông số từ settings và chỉ ghi chức năng có kiểm thử tích hợp tương ứng.

## Cách diễn giải kiểm tra hiện có

Mock landmark kiểm tra FSM và hợp đồng, không đo accuracy mô hình. Test widget hiện chủ yếu kiểm tra có/hiển thị, chưa đủ xác nhận không overlap hay dễ sử dụng. Test paths máy cá nhân/video ngoài repo chưa tái lập trên máy khác. Emotion tests dùng pytest và import `main` dễ đụng entrypoint root; unittest root không bảo đảm thu thập chúng.

Inventory script parse AST nguồn Python/spec và kiểm tra hash snapshot, không import ứng dụng, không mở camera, không gửi SMTP. Session audit này chưa chạy full suite do tác dụng phụ A06. Chưa đo FPS, độ trễ thực, độ chính xác trên camera hoặc kiểm tra executable Windows; các mục đó là gate trong kế hoạch.

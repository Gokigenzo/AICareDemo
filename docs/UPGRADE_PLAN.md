> C?p nh?t 02/10/2026: ?? tri?n khai prototype pose/tracking v3 v? backend ONNX local. Clip ngu?n v?n 0 s? ki?n x?c nh?n; accuracy NOT VERIFIED. Xem [k?t qu? tri?n khai v3](fall_detection/BAO_CAO_TRIEN_KHAI_POSE_TRACKING_V3.md). N?i dung/s? li?u v2 b?n d??i l? baseline l?ch s?.

# Kế hoạch nâng cấp theo module

Ngày: 02/10/2026. Đầu vào: [kiến thức codebase](PROJECT_KNOWLEDGE.md), [audit A01–A23](CODEBASE_AUDIT.md), snapshot nguồn. Đây là backlog thực thi, đã đối chiếu lại các thay đổi FallPipeline v2 có sẵn trong working tree. Không chốt thời gian lịch khi chưa có baseline, dataset và máy kiểm thử.

## Tiến độ đối chiếu và bước tiếp theo

- G0 đã có harness cô lập và 24 core + 1 UI lifecycle tests pass khi chạy lại. Chưa đạt gate toàn bộ tests/benchmark legacy, config import vẫn có side effects.
- G1 đã sửa FrameSource API, capture clock/validity và stop/join. Còn identity TTL, state degraded, unregister callbacks và kiểm tra lifecycle dài.
- G3/G5 đã có common core, góc scale theo ảnh, motion transition, track TTL, seek replay, GT hash/subject matching và trial-only dispatch. **Chưa đạt nghiệm thu detector**: candidate bỏ sót hai nhãn ngã trên clip theo báo cáo batch có sẵn. Durable delivery và dataset độc lập còn thiếu.
- G2/G4/G6/G7 chưa đủ bằng chứng hoàn thành; giữ gates bên dưới. Không coi công việc lập kiến thức đã hoàn tất là toàn bộ nâng cấp sản phẩm đã hoàn tất.

Ưu tiên kế tiếp: giữ trial-only; hoàn thiện G0/G1 và state repository; xác định backend có khả năng quan sát người ngã trên dữ liệu độc lập trước khi bật alert. Không tune theo một clip để đạt chỉ số. [Biên bản hoàn tất audit](KNOWLEDGE_COMPLETION.md) ghi kiểm tra đã chạy và giới hạn.

## Thứ tự triển khai

| Giai đoạn | Công việc/đầu ra | Phụ thuộc | Điều kiện hoàn thành |
|---|---|---|---|
| G0 — Baseline có thể tin | Cô lập tests; settings/repository/delivery injectable; khóa socket; fixture video portable; sửa assertion trạng thái; đánh dấu metric/demo chưa kiểm chứng | Không | Test không ghi shared/data thật, không gọi camera/SMTP; inventory/hash và danh sách test thu thập tái lập; không còn metric accuracy dựng sẵn |
| G1 — An toàn tích hợp | Identity TTL + unknown policy; capture health/freshness; sửa FrameSource API; stop/join/unregister; UNKNOWN/DEGRADED thay default an toàn giả | G0 | A→unknown không dùng caregiver cũ; mất frame/đọc JSON lỗi không hiển thị an toàn; 50 vòng start/stop/switch không treo hoặc leak callback |
| G2 — Trạng thái và hồ sơ | Một state owner, typed snapshot, revision; atomic persistence; patient repository thống nhất; ID containment, migration và delete | G1 | Concurrent updates không mất field; lỗi write được báo; delete hết hồ sơ liên quan; ID traversal bị từ chối; migration có backup/rollback |
| G3 — Fall live và cảnh báo | Tách inference/render, sửa aspect geometry; monotonic FSM; evidence kiểm tra write; UUID + outbox bền vững, idempotency | G2 | Synthetic time test đủ transitions/occlusion/recovery; restart tiếp tục retry không gửi lặp; recipient gắn snapshot sự kiện; SMTP_ACCEPTED hiển thị đúng nghĩa |
| G4 — Rehab/face/emotion | Spec exercise chung, penalty độc lập FPS, session summary; face train worker; backend emotion độc lập và TTL; đóng tài nguyên model | G2, nền G1 | Rep/score giống nhau trên replay 15/30/60 FPS trong tolerance đã chốt; UI/engine cùng target; session đúng patient; fallback/TTL/deletion kiểm thử |
| G5 — Đánh giá chung | Replay dùng detector+FSM live với sink dry-run; giữ MOG2 như experiment có tên riêng; GT hash/coverage, track expiry và seek policy | G3; dữ liệu có nhãn | Source SHA khớp GT; không nhãn/partial báo NOT_EVALUATED/PARTIAL; socket spy xác nhận zero network; metric event-level trên tập độc lập |
| G6 — Hiệu năng/UI | Tách Dashboard thành view/controllers, capture/pipeline workers; shared inference phù hợp; telemetry/rotation; kiểm thử accessibility | G3–G5 | Đo p50/p95 latency, FPS/age trên máy mục tiêu; UI không bị report/inference chặn; layout ở nhiều DPI, trạng thái nhất quán mọi mode |
| G7 — Phát hành | Dependencies/CI/spec thống nhất; clean artifact allowlist; portable path/migration; cập nhật báo cáo và user guide theo capability thực | G0–G6 | Máy sạch chạy được; artifact không có hồ sơ/ảnh/secret; path có dấu/khoảng trắng hoạt động; smoke camera/mock SMTP; docs khớp settings và test |

## Thiết kế đích để các module phối hợp

`FramePacket` dự kiến chứa frame thô, source_id/type, sequence, capture timestamp monotonic và health. `Observation` chứa timestamp, identity/tracking scope, visibility và lý do unavailable. Các detector nhận frame thô; overlay/render là bước cuối. Live và replay chạy cùng pipeline; replay truyền clock theo nguồn và delivery sink giả.

`IdentitySnapshot` phân biệt recognized, unknown, no_face và selected_profile; lưu độ mới. Fall event chụp snapshot danh tính/người nhận tại thời điểm xác nhận, không đọc profile đang thay đổi khi email worker gửi. Mặc định xử lý người chưa xác định cần cấu hình rõ, không kế thừa ngầm identity trước.

State store giữ snapshot trong bộ nhớ do một owner cập nhật; UI đọc snapshot, persistence ghi atomic và có revision/schema_version. Có thể bắt đầu JSON atomic để giảm phạm vi; cân nhắc SQLite khi cần transaction giữa profiles/sessions/events/outbox. Không đồng thời duy trì hai nguồn hồ sơ có quyền ghi ngang nhau.

## Backlog từng module

| Module | Việc nâng cấp cụ thể | Kiểm chứng bắt buộc |
|---|---|---|
| Camera/FrameSource | Sửa API; single capture owner; freshness; QImage copy; close/join; pause/seek/release idempotent | Fake capture lỗi/ngắt; duplicate sequence; close modal/window; seek/reset/replay |
| FallDetector/Monitor | Correct pixel/world geometry; config version; monotonic clock; visibility đủ khớp; temporal motion chỉ sau baseline | Standing/sitting/bending/lying/occlusion, nhiều tỷ lệ ảnh; event latency; không xác nhận bằng evidence cũ |
| Video evaluation | Một harness live-replay; ROI theo config nếu giữ MOG2; bounded tracks; GT matcher tổng quát | Clip khác độ phân giải, 2 người gần nhau, EOF/partial/no GT/hash mismatch, seek |
| Face/Patient | Repository thống nhất; chặn ID path; capture quality; train worker; model version; rejection calibration | Người ngoài tập, đổi ánh sáng/góc, delete người đang nhận diện, train trong live; dữ liệu rollback |
| Emotion | Bỏ import path generic; FACS chạy được không torch; thống nhất taxonomy; TTL getter | Torch/checkpoint hỏng; mất mặt khi rehab; subject-disjoint confusion matrix và macro-F1 |
| Rehabilitation | ExerciseSpec chung; rep hoàn chỉnh; penalty theo thời gian/sự kiện; active gate; session persistence | Rep dở/occluded/pause/change exercise, score FPS invariance, summary identity và counts |
| Email/Event | Outbox retry bền vững; UUID; evidence validation; trạng thái delivery đủ chi tiết | Auth/network/unconfigured; restart/crash; duplicate event; file ảnh lỗi; không SMTP trong test |
| Dashboard | Controllers cho monitor/rehab/video/registration; async report/train; thông báo từ source state | Pause/resume/modal/unknown/disconnect; DPI lớn, bàn phím, text dài; không state xanh giả |
| Config/Packaging | Load dotenv trước settings; validate số/paths; runtime resource split; clean data seeds; hook/spec review | Portable/read-only source/LOCALAPPDATA, paths có dấu/khoảng trắng, clean machine |
| Tests/CI/docs | Fixtures cô lập; test discovery rõ; integration theo contracts; report provenance; docs sinh từ settings | Không external side effects; baseline failure tái hiện trước fix; CI runtime và training riêng |

## Đánh giá chất lượng trước khi chọn model mới

Fall: báo event precision/recall, false alarms trên giờ video không ngã, thời gian từ impact đến alert, tỷ lệ thời gian observable, theo scene/occlusion/person. Chia tập theo video/người/cảnh, không tune trên clip test. Không đặt mục tiêu “100%” khi chưa có dữ liệu.

Face: false accept/reject trên người đã đăng ký và người ngoài tập, theo ánh sáng/góc nhìn; emotion: macro-F1/confusion matrix trên subject chưa thấy; rehab: sai số rep so với nhãn người đánh giá, agreement điểm và độ nhạy theo FPS/occlusion. Mọi report ghi dataset/model/config/source revision, hash và các trường hợp không đánh giá được.

Bắt đầu bằng PR G0, sau đó G1; mỗi PR có regression tái hiện lỗi, thay đổi nhỏ, điều kiện nghiệm thu trên bảng và cập nhật knowledge/ADR. Chỉ quyết định thay model sau khi có baseline cho thấy giới hạn cụ thể; tối ưu pose dùng chung cần đo hiệu năng và kiểm tra accuracy cho cả fall lẫn rehab.

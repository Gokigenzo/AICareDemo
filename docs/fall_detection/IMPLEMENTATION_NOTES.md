> HISTORICAL ARCHIVE: Fall Detection is retired from the main application. These results do not validate the medication reminder module.

# Bàn giao điều chỉnh Fall Detection — 02/10/2026

**Kết luận: FAIL nghiệm thu phát hiện trên clip chuẩn; NOT VERIFIED cho vận hành thực tế. Chỉ chạy thử, chưa bật Gmail thật.**

Mã đã chuyển sang một lõi dùng chung và có kiểm thử phần mềm, nhưng HOG + pose trên crop không quan sát đủ khớp trong clip ngã. Không sửa ngưỡng theo clip để lấy 2/2. Xem [bảng trước/sau và từng lượt](../../reports/fall_detection/BEFORE_AFTER.md).

## Trạng thái repository và hướng dẫn

Đã đọc chỉ dẫn AGENTS do người dùng cung cấp, `.agents/rules/codebase-memory.md`, manifest và cấu hình plugin. Không tìm thấy AGENTS.md vật lý hay SKILL.md của codebase-memory trong các nơi đã tìm (repository, thư mục skills/plugins, ổ F). Executable `F:\codebase-memory\codebase-memory-mcp.exe` có tồn tại, nhưng tool MCP không được cấp trong phiên. Sau khi người dùng yêu cầu toàn quyền ổ F và tiếp tục, khảo sát trực tiếp bằng đọc mã/rg. Không giả nhận đã sử dụng graph skill.

Working tree đã có nhiều thay đổi và file untracked trước khi bắt đầu. Không reset/clean/checkout, không commit thay người dùng. Baseline có code_commit **và** hash nội dung các file của working tree; commit riêng không mô tả đầy đủ baseline. `experiments/fall_legacy_reference.py` lưu nguyên runner cũ trước sửa. `experiments/fall_legacy_source.py` tái tạo đồng hồ index/FPS cho batch đối chiếu cũ; không dùng trong sản phẩm.

## Đầu vào

- Clip nguồn tìm được theo đường dẫn thật trong `experiments/test_runner_eval.py`: `C:\Users\USER\Downloads\Elderly Couple Slips and Falls Outside Front Door - 1498633 - RM Videos (720p, h264).mp4`. Hash đúng `5c70f33ed96d96bc8a306bc370a835c86a7c33db2404a1549caaa0aca614a5b4`. Không copy video vào git.
- `Test_Fall.mp4`, `TestUI.mp4`, `logs/app.log`, báo cáo kỹ thuật và nhãn cũ đã có. Hai video ghi màn hình được đọc tuần tự; không lấy timeline của chúng làm GT của video nguồn.
- Không tìm thấy `app(2).log`. `app.log` có các mốc cảnh báo được yêu cầu, nhưng chưa chứng minh là cùng file/phiên bản với `app(2).log`.
- Thiếu: nhãn độc lập từ hai người, biên bản thống nhất, bbox GT theo PTS, entry/exit/uncertainty được xác nhận, video âm tính độc lập và tập khác góc máy/người/bối cảnh.
- Bản nhãn v2 giữ mốc cũ, đổi nhãn thành `GT_MAN`/`GT_WOMAN`, giữ `legacy_label`; những trường chưa biết là null/[] và trạng thái NOT VERIFIED. Không tự dựng bbox từ dự đoán.

## Đường gọi thực tế

Trước sửa:

```text
CameraManager.run -> DashboardWindow._process_video_frame
 -> FallAdapter.process_frame -> FallMonitor.process_frame
 -> FallDetector.analyze_frame (MediaPipe Pose một người; time.time)
 -> FallMonitor._update_fsm (FSM toàn frame)
 -> _handle_fall_confirmed -> _persist_event / EmailService.send_fall_alert

VideoFileFrameSource.read_frame (frame_index/FPS)
 -> FallTestRunner.process_next_frame
 -> MOG2 -> contours -> ROI pixel cố định -> centroid tracker 140px
 -> FSM riêng mỗi track -> mock email / snapshot
 -> generate_evaluation_report (ghép bằng event_id GT và x=560)
 -> DashboardWindow._update_video_test_ui
```

Sau sửa:

```text
CameraManager.run (PTS capture monotonic + frame hợp lệ)
 -> DashboardWindow._process_video_frame (raw_frame riêng khỏi overlay face/rehab)
 -> FallAdapter.process_frame -> FallMonitor.process_frame -> FramePacket
VideoFileFrameSource.read_frame (decoder CAP_PROP_POS_MSEC)
 -> FallTestRunner.process_next_frame -> FramePacket
                         |
                         v
FallPipeline.process -> PersonPoseBackend.observe
 -> OpenCV HOG nhiều proposal -> NMS -> MediaPipe stateless Pose mỗi crop
 -> Hungarian association (IoU + chuyển động + khoảng cách theo chiều cao + score)
 -> TrackState -> _features -> _step (FSM theo PTS từng track)
 -> FallEvent(run_id,track_id,episode; person_identity=null)
 -> render và telemetry từ cùng summaries
                         |
        +----------------+----------------------+
        |                                       |
Video: EmailService(mode=video_file) guard       Camera: DRY_RUN_NOT_VALIDATED
 -> DRY_RUN trước mọi truy cập SMTP             -> chỉ sự kiện thử trong bộ nhớ
 -> core.fall_evaluation.evaluate               -> không ghi hồ sơ bệnh nhân
 -> report ở EOF/xuất thủ công                  -> không gửi Gmail
```

Camera UI dùng CameraManager đang có để giữ face/emotion/rehab; không mở camera thứ hai qua CameraFrameSource. CameraFrameSource vẫn là adapter tương thích. Hai đường vào cùng FallPipeline; chỉ đồng hồ/nguồn/output khác nhau. Mã `FallDetector` và `_update_fsm` cũ giữ cho đối chiếu/tương thích, không phải lõi đang chạy. Entry point dispatch legacy bị chặn để không vượt qua chế độ thử.

Kiểm tra thêm phát hiện CameraFrameSource cũ gọi `get_raw_frame/pause_camera/resume_camera` không tồn tại trên CameraManager thực tế. Đã sửa sang `get_capture_packet/pause/resume`, lấy image/PTS/validity cùng khóa và bỏ lần đọc trùng capture. Capture giả lập/mất tín hiệu không được xem là frame camera hợp lệ; stop chờ thread trước khi giải phóng và không restart khi thread cũ chưa dừng. Có test adapter với API này; soak test camera vật lý vẫn NOT VERIFIED.

## Thay đổi theo pha

| Pha / file | Chức năng và lý do |
|---|---|
| A: scripts/evaluate_fall.py | Một lệnh batch, 5 lần khởi tạo sạch, hash/config/commit/platform, sự kiện, PTS, thời gian, CPU/RAM, chặn SMTP và so hash kho live. |
| A: scripts/inspect_fall_inputs.py, inspect_fall_events.py | Đọc tuần tự, hash file, so metadata/decoded; ảnh hỗ trợ kiểm tra thủ công, không thành detector ROI. |
| A: data/video_annotations/elderly_fall_v2.json, ANNOTATION_PROTOCOL.md | Tách subject khỏi track; version nhãn, yêu cầu hai người gán độc lập; chưa có nhãn thì NOT VERIFIED. |
| B/C: core/fall_pipeline.py | Hợp đồng FramePacket/PersonObservation/TrackState/FallEvent; cùng backend/tracker/feature/FSM; bỏ ROI cố định của cảnh mẫu. |
| C: core/frame_source.py, core/camera_manager.py | Video dùng PTS decoder, từ chối PTS lỗi, pause không đọc frame, EOF lặp an toàn; camera có capture monotonic và validity. |
| B/C: services/fall_monitor.py, adapters/fall_adapter.py | Camera vào chung lõi, raw frame không bị overlay làm nhiễu; không gán danh tính từ người đang được chọn cho mọi track; khóa cảnh báo thật. |
| D: services/fall_test_runner.py | Adapter dry-run; mỗi restart/seek có UUID mới; seek replay từ đầu; archive riêng; EOF bỏ track và trả frame sạch; snapshots trong bộ nhớ không ghi report mỗi frame. |
| D: core/fall_evaluation.py | Ghép đúng subject bằng bbox GT + PTS rồi Hungarian một-một theo event/impact window; không ghép theo track-number hoặc x cố định; ba độ trễ, mẫu số thiếu là null. |
| D: app/dashboard.py | HUD, timeline, trạng thái hiện tại dùng cùng summaries; EOF xóa overlay; hiển thị NOT VERIFIED, không hiển thị confidence phần trăm chưa hiệu chỉnh; nhãn Unicode. |
| E: services/email_service.py | Chặn non-camera ngay dispatch và test_connection; idempotency trong process; retry có giới hạn; phân biệt SMTP_ACCEPTED/delivered_unknown; log không in tên/email người nhận. |
| E: tests/test_fall_pipeline_v2.py, test_fall_ui_v2.py | Unit/integration có synthetic falls và hành vi âm tính, scale, visibility, ID ambiguity, PTS, seek/restart/EOF, camera/video cùng lõi, dispatch có credential giả lập bật. |
| E: tests/test_fall_and_safety.py | Chuyển hai test monitor từ mock detector cũ sang observations mới; kiểm tra không ghi hồ sơ/gán sai danh tính khi chạy thử. Không bỏ qua test thất bại. |
| scripts/run_fall_checks.py | Runtime tạm cho test để không sửa bệnh nhân thật; SMTP mặc định bị chặn; lưu stdout test + JSON summary. |
| docs/BAO_CAO_KY_THUAT_FALL_DETECTION.md | Thay kết luận lâm sàng/100% không có căn cứ bằng kết quả và giới hạn thật; giữ bản cũ trong LEGACY_REPORT_UNVERIFIED.md. |
| requirements*.txt, .gitignore | Khai báo scipy cho Hungarian; không đưa video và snapshot thử vào git. |

## Thuật toán, cấu hình và giới hạn

- HOG là lựa chọn tham chiếu CPU có sẵn, không tải trọng số mới. Pose full của MediaPipe 0.10.20 đã có trong môi trường; dùng static_image_mode để không mang state người trước sang crop khác. Không nói HOG đã được kiểm định cho người nằm/khuỵu. **Kết quả clip cho thấy lựa chọn này không đáp ứng phát hiện ngã.**
- Thư viện/trọng số được dùng từ gói đã cài; cần giữ các LICENSE/NOTICE trong bản phân phối OpenCV và MediaPipe, không phát hành trọng số mới trong thay đổi này. Model hashes và version được ghi trong provenance bổ sung. Việc kiểm định mô hình thay thế vẫn chưa hoàn tất.
- Không có ROI loại trừ mặc định. Không có floor calibration thì floor_distance=null. Góc thân dùng tọa độ pixel theo aspect ảnh; bbox/association/giảm chiều cao/vận tốc chuẩn hóa theo kích thước người.
- Visibility của vai/hông/gối/cổ chân không đủ thì feature không biết=null; không xác nhận từ mất dấu. HOG margin là detector score chưa hiệu chỉnh; confidence sự kiện=null, không phải xác suất ngã 0.92/0.85 tự gán như trước.
- Nghi ngờ đòi quan sát upright→low kèm tốc độ hông đi xuống. Nằm sẵn không đủ. Cửa sổ nghi ngờ 0.5 s, xác nhận 0.8 s; TTL 1.2 s; khoảng hụt quan sát >0.25 s hủy timer; recovery 1 s, cooldown 2 s. Đây là cấu hình nghiên cứu, chưa hiệu chỉnh trên development/held-out.
- Association mơ hồ không ép nhận diện: ghi identity_uncertain, không xác nhận. Không có ReID appearance; giao nhau/merge/split có thể gây fragmentation. TTL chỉ giúp che khuất ngắn; không bảo đảm ID thực tế.
- Dedupe `(run_id,track_id,episode)` không gộp hai người gần nhau. Track mất lâu rồi tạo lại có thể duplicate cùng người: chưa có GT/ReID để kiểm định.
- FSM lưu lý do chuyển và features. Confirmation cần frame thực quan sát, không dùng bbox cũ để tích lũy thời gian.
- Event matching dùng IoU>=0.20, sample cách PTS<=0.75 s, chênh ứng viên>=0.10; impact window [-0.5,+3.0] s. Giá trị đánh giá đã ghi trong protocol, không phải tiêu chí nghiệm thu vận hành do chủ dự án chốt.
- Hai latency theo nhãn chỉ tính khi ghép có bằng chứng; latency suspected→confirmed luôn từ event. Không clip giá trị âm impact→confirmed về 0.
- Camera alert gate hiện đóng hoàn toàn. Việc nhận diện mặt độc lập vẫn hoạt động, nhưng chưa có association mặt→track tin cậy nên event.person_identity=null. Không đủ điều kiện mở Gmail bằng cách chỉ bật EMAIL_ENABLED.
- Email idempotency trong cùng process, chưa durable khi crash/restart. Không tuyên bố exactly-once SMTP. Kết nối mất trong lúc submission được ghi delivered_unknown, không tự retry.

## Lệnh tái hiện trên Windows PowerShell

Chạy tại `F:\AI_Rehabilitation_Safety_Assistant`. Không cần pytest; dùng unittest trong `.venv` hiện có.

```powershell
$clip = 'C:\Users\USER\Downloads\Elderly Couple Slips and Falls Outside Front Door - 1498633 - RM Videos (720p, h264).mp4'
.\.venv\Scripts\python.exe scripts/evaluate_fall.py $clip --legacy --phase baseline_repeat --repeats 5
.\.venv\Scripts\python.exe scripts/evaluate_fall.py $clip --phase candidate_repeat --repeats 5
.\.venv\Scripts\python.exe scripts/run_fall_checks.py --pattern test_fall_pipeline_v2.py --output reports/fall_detection/checks_repeat_core
.\.venv\Scripts\python.exe scripts/run_fall_checks.py --pattern test_fall_ui_v2.py --output reports/fall_detection/checks_repeat_ui
.\.venv\Scripts\python.exe scripts/run_fall_checks.py --pattern test_fall_and_safety.py --output reports/fall_detection/checks_repeat_fall
.\.venv\Scripts\python.exe scripts/run_fall_checks.py --pattern test_rehab_assistant.py --output reports/fall_detection/checks_repeat_rehab
.\.venv\Scripts\python.exe scripts/finalize_fall_report.py
.\.venv\Scripts\python.exe scripts/reassess_fall_runs.py
```

Mỗi batch dùng tên phase mới; script từ chối ghi đè thư mục lượt có sẵn. Đường dẫn clip là đường dẫn đã xác minh trong phiên; máy khác phải truyền đường dẫn thực của clip có đúng hash. Không dùng Test_Fall.mp4 làm source thay thế. Không copy dataset/video vào git khi chưa có quyền phân phối.

Manifest ngoài ghi thông tin batch; session_manifest bên trong ghi run_id thật của event, cấu hình FSM, hash GT, trạng thái complete/partial_seek. Trace/transition/tracking_audit giúp kiểm tra sự kiện và UI. `scripts/finalize_fall_report.py` chỉ tổng hợp các kết quả đã chạy, không sửa các lượt gốc.

## Còn thiếu / rollback

T01 không đạt; T05 phần lifecycle có test qua nhưng kiểm tra frame-count thất bại. T06 có bằng chứng mock và hash kho live. T02–T04/T08 cần video độc lập; T07 chưa thử Gmail thật; T09 chưa có ngân sách hiệu năng được chốt. Không lấy test synthetic thành bằng chứng hiệu quả camera thực tế.

Seek hiện replay đồng bộ từ đầu, đúng lịch sử nhưng có thể chặn UI trên clip dài/chậm; cần worker/cancellation để đạt chất lượng vận hành. Memory trace/report tăng theo độ dài clip; chưa có soak test dài. CAP_PROP_POS_MSEC tùy backend: nguồn không trả PTS đơn điệu bị từ chối, không tự thay bằng FPS. Không xác minh VFR thật ngoài test decoder PTS giả lập.

Không đủ dữ liệu để chọn và nghiệm thu một model đa người thay thế; HOG candidate được giữ để đối chiếu, **không được coi là bản nâng cấp độ nhạy**. Đường MOG2 cũ vẫn có thể chạy qua `--legacy` để rollback nghiên cứu, không đưa lại vùng pixel của clip vào camera live. Vì repo đã dirty từ trước, không dùng git reset --hard để rollback. Xem các file được liệt kê, dùng diff/cherry-pick từng phần khi người dùng commit; giữ nguyên snapshot baseline/nhãn/log bằng chứng. Cổng bật Gmail chỉ nên được thiết kế mở lại sau khi có model đạt tập độc lập, mapping danh tính, ngưỡng vận hành chốt trước và kiểm thử giao nhận phù hợp.

# Ánh xạ bằng chứng vào báo cáo KHKT THPT

## Nguyên tắc viết

Phần này cung cấp vật liệu kỹ thuật, không tự dựng động cơ cá nhân, khảo sát cộng đồng, thí nghiệm trên người hay tính mới khoa học. Status phải giữ đúng phạm vi từ manifest. Mã có thuật toán không tự chứng minh accuracy; mock/seed không thay nghiệm thu thiết bị. Screenshot hiện có chứa hồ sơ/thuốc nên không đưa vào báo cáo công khai trước tạo bản synthetic/anonymized phù hợp, xóa tên/liênhệ/health text thật; chỉ che ID chưa đủ. [C49–C55]

| Mục KHKT | Bằng chứng và file liên quan | Status phạm vi | Sơ đồ/ảnh phù hợp | Thiếu và trọng tâm đề xuất |
|---|---|---|---|---|
| I.1 Lý do chọn đề tài | Chức năng UI/services tại app/dashboard.py và app/today_todo_widget.py [C02/C20] | IMPLEMENTED UI test; động cơ xã hội UNKNOWN | System architecture 01 | Cần số liệu nhu cầu/tài liệu/xuất xứ khảo sát; mô tả bài toán hỗ trợ thao tác |
| I.2 Ý nghĩa khoa học/thực tiễn | Hình học/FSM/voice/context [C14–C19/C24–C33] | IMPLEMENTED thành phần; lợi ích lâm sàng UNKNOWN | Dataflow 01 | Cần usability/field data; nhấn ứng dụng kỹ thuật, không chẩn đoán |
| I.3 Mục tiêu | Snapshot năng lực và limitations 00 [C51–C55] | PARTIALLY_IMPLEMENTED toàn hệ thống | Ma trận 00 | Mục tiêu đo được và tiêu chí nghiệm thu, không thành quả đã đạt |
| I.4 Đối tượng/phạm vi | Patientbinding, 3 role portal, DB schemas [C04/C38/C44] | IMPLEMENTED guard tests; toàn UX PARTIAL | Component/ERD | Xác định người dùng/địa điểm/consent; no free-tier health records |
| I.5 Phương pháp nghiên cứu | Test source, benchmarks, training code [C12/C51–C54] | IMPLEMENTED test artefacts; missing human study UNKNOWN | Bảng thí nghiệm 06 | Tách thiết kế/kiểm thử/phương pháp chưa làm |
| I.6 Tính mới/sáng tạo | Tích hợp CV+STT+allowlist+transaction/context [C18/C27/C30/C43] | IMPLEMENTED một số integration; novelty UNKNOWN | Component 01 | Cần prior art/comparison; trình bày đóng góp gói tích hợp, không tuyên bố phát minh LBPH/Whisper |
| II.1.1 Cấu tạo chung | Entrypoint/desktop/backend/web [C01/C02/C40/C42] | PARTIALLY_IMPLEMENTED toàn chuỗi | System architecture 01 | Tách shared SQLite/DB games/JSON; flag Gemini tắt |
| II.1.2 Thiết kế chi tiết | Recorder/engine/worker/controller/dispatcher [C24–C33] | IMPLEMENTED contract/lifecycle mock | Component 01 | Boundary threads/context/privacy/auth |
| II.1.3 Sơ đồ nguyên lý | frame/audio→rules→handler→DB/outbox [C14/C25/C27/C42] | IMPLEMENTED subflow; E2E PARTIAL | Startup/dataflow/main interaction 01 | Không vẽ emotion→DB nếu chưa nối |
| II.1.4 Tổng thể sản phẩm | Desktop tabs/portals/spec/setup [C02/C38/C49/C50] | PARTIALLY_IMPLEMENTED đóng gói mới | UI ảnh synthetic cần chụp lại | Không dùng ảnh production/khẳng định Windows build passed |
| II.2 Phần mềm/xử lý dữ liệu | Preprocess face/emotion/PCM, DB DDL [C07/C11/C24/C40/C41] | PARTIALLY_IMPLEMENTED training provenance; IMPLEMENTED DDL test | ERD05/equations 03 | Đầu vào/chất lượng/data lifecycle/retention |
| II.3 Thiết kế/lập trình | Python/PyQt/std HTTP, dependency locks, services [C01/C49/C50] | IMPLEMENTED Linux install; Windows PARTIAL | Module tree 01/stack 02 | Phân biệt manifest/lock/runtime; không giả định FastAPI/Postgres |
| II.4 Nguyên lý từng chức năng | Algorithm detail 03/workflow 04 [C06–C39] | Theo từng module 00/manifest | FSM table 03/workflow 04 | Selfreport thuốc, quality count, unknown intent, limitations |
| III.1 Thử nghiệm/cải tiến | PyAV pin/import sideeffects/deadline fix/history [C25/C31/C49/C54] | IMPLEMENTED scope artefacts | Comparison 06/07 | Ghi thất bại/tập/môi trường, không kể thí nghiệm chưa chạy |
| III.2 Thử nghiệm tổng thể | HTTP 66 ms, mock Qt/SSE, 3SDK cases [C33/C42/C53/C54] | PARTIALLY_IMPLEMENTED real E2E | Testmatrix 06 | Thiếu mic→camera→DB→3 browser/email real; không gọi mock full system |
| III.3 Hoàn thiện | Baseline failure/caps/offline/fallback [C32/C43/C54/C55] | PARTIALLY_IMPLEMENTED | Checklist 09 | Security public password/auth, loop med, sync emotion game, physical stress |
| IV Kết luận | Summary 00 và measured 06 [C51–C55] | Nguyên mẫu có code/tests; full validation UNKNOWN | Bảng status 00 | Kết luận đúng phạm vi, không clinical efficacy/accuracyinvented |
| V Hướng phát triển | Missing checklist 09/experiments 06 [C21/C45/C47/C55] | PLANNED cho Postgres; đề xuất khác chưa thực hiện | Timeline đề xuất ghi rõ proposal | Ưu tiên correctness/privacy/E2E trước model mới |
| VI Tài liệu tham khảo | Source/manifest, existing reports và upstream doc links | Nguồn source đã đọc; nguồn web chưa xác minh lại | Không cần ảnh | Ghi version/ngày truy cập đúng; kiểmtra bản quyền/nguồn weight |

## Mẫu diễn đạt có thể dùng

“Nguyên mẫu sử dụng LBPH của OpenCV để so khớp ảnh khuôn mặt đã đăng ký; ngưỡng distance 58 và cơ chế làm mượt được cài đặt trong mã. Nghiên cứu chưa thu thập đủ dữ liệu để xác lập FAR/FRR trên nhóm người dùng độc lập.” [C06–C09/C55]

“Các bộ đếm phục hồi được kiểm thử bằng landmark tổng hợp. Trạng thái hoàn thành được tạo khi số lần ghi nhận đạt mục tiêu snapshot; hiện còn cần kiểm chứng điều kiện chất lượng từng lần và góc camera thực tế.” [C15–C19]

“Ứng dụng lưu xác nhận uống thuốc do người dùng tự khai báo, dùng chung service/idempotency cho nút tay và voice. Bản ghi không là bằng chứng khách quan người dùng đã uống thuốc.” [C20/C27]

“Lớp Gemini đã có code và smoke text trên ba câu tổng hợp; mặc định cloud tắt và chỉ catalog trung tính được phép gửi. Chưa nghiệm thu toàn bộ tập acceptance và luồng micro tới giao diện web.” [C28–C33/C53/C55]

## Nguồn tham khảo kỹ thuật cần đối chiếu khi viết bản cuối

Nguồn repo: main.py, adapters,rehab_engine.py, services/local_voice, services/transcript_intent, database/migrations, web và reports/* trong manifest. Nguồn upstream đã được hướng dẫn hiện có trỏ tới: https://docs.opencv.org/ ; https://ai.google.dev/edge/mediapipe/ ; https://github.com/SYSTRAN/faster-whisper ; https://opennmt.net/CTranslate2/ ; https://github.com/googleapis/python-genai ; https://ai.google.dev/gemini-api/docs/structured-output ; https://ai.google.dev/gemini-api/docs/rate-limits ; https://ai.google.dev/gemini-api/terms ; https://www.sqlite.org/wal.html . Audit không truy cập web lại; không ghi ngày“đã đọc online” hoặc thuật ngữ/giá/quota hiện hành như đã verify. Cần thêm tài liệu khoa học và khảo sát prior art để hỗ trợ ý nghĩa/tính mới, không chỉ thư viện software.

## Bằng chứng truy nguyên

- **C02 — IMPLEMENTED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._init_ui`; Lines: 175–528. Explanation: Dashboard mount TodayTodo, camera/phục hồi, trò chơi và thanh micro; smoke offscreen đã kiểm tra lifecycle. Giới hạn: Camera/audio mocked, TTS tắt, SMTP bị chặn; không phải nghiệm thu phần cứng.
  - Đối chiếu: `reports/gemini_intent/dashboard-smoke.txt` · `module` · 1–44 (existing_test_or_runtime_artifact).
- **C04 — PARTIALLY_IMPLEMENTED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._do_update_dashboard_ui`; Lines: 967–1083. Explanation: Nhận diện và chọn patient đồng bộ binding các widget; voice invalidates context khi đổi patient/tab/source. Giới hạn: Unknown-face không xóa current_patient_id; voice có guard riêng, hành động tay cần kiểm tra đổi/người lạ.
  - Đối chiếu: `app/dashboard.py` · `DashboardWindow._resolve_patient_id` · 936–953 (source_code).
  - Đối chiếu: `services/local_voice/dispatcher.py` · `CommandDispatcher.snapshot` · 24–45 (source_code).
- **C06 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.__init__`; Lines: 40–81. Explanation: Face detection ưu tiên OpenCV DNN, fallback Haar; nhận diện bằng LBPH radius 1/neighbors 8/grid8x8. Giới hạn: Có pipeline; chưa có FAR/FRR trên tập người độc lập; DNN detector không phải model nhận dạng identity.
  - Đối chiếu: `adapters/face_adapter.py` · `FaceAdapter.detect_face` · 107–146 (source_code).
- **C07 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.extract_face_roi`; Lines: 171–221. Explanation: ROI khuôn mặt grayscale, CLAHE, bilateral và resize200x200; augmentation flip, sáng/tối, xoay±4°. Giới hạn: Không có lớp background thực tế dù doc string nhắc; augmentation không tăng số người độc lập.
  - Đối chiếu: `adapters/face_adapter.py` · `FaceAdapter.train_recognizer` · 223–312 (source_code).
- **C09 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.register_patient`; Lines: 614–719. Explanation: Đăng ký lưu crop và hồ sơ JSON, sync sang unified DB và retrain LBPH. Giới hạn: Test registration tồn tại nhưng một số dùng đường dữ liệu mặc định; không chạy trong audit để tránh sửa hồ sơ.
  - Đối chiếu: `services/patient_sync_service.py` · `sync_single_patient` · 44–262 (source_code).
- **C12 — PARTIALLY_IMPLEMENTED**. File: `modules/emotion/src/data.py`; Symbol: `module`; Lines: 1–190. Explanation: Training biểu cảm có split theo session, baseline logistic regression và evaluator classification metrics. Giới hạn: Không tìm thấy CSV/splits/results phục vụ tái lập ở vị trí config; số người/data set/provenance UNKNOWN.
  - Đối chiếu: `modules/emotion/src/train.py` · `module` · 1–223 (source_code).
  - Đối chiếu: `modules/emotion/src/evaluate.py` · `module` · 1–189 (source_code).
  - Đối chiếu: `modules/emotion/src/baseline.py` · `module` · 1–66 (source_code).
- **C14 — PARTIALLY_IMPLEMENTED**. File: `modules/rehabilitation/rehab_engine.py`; Symbol: `calculate_angle`; Lines: 44–57. Explanation: Phục hồi dùng MediaPipe Pose/Tasks lite và góc2D từ tọa độ landmark chuẩn hóa. Giới hạn: Không dùng 3D chuẩn lâm sàng; x/y chuẩn hóa chưa sửa tỷ lệ khung hình; chưa có sai số góc với thước chuẩn.
  - Đối chiếu: `modules/rehabilitation/rehab_engine.py` · `RehabilitationEngine._init_pose` · 531–583 (source_code).
- **C18 — IMPLEMENTED**. File: `modules/rehabilitation/rehab_session_adapter.py`; Symbol: `RehabSessionAdapter.record_verified_rep`; Lines: 196–290. Explanation: RehabSessionAdapter khóa target snapshot, ghi event idempotent/outbox và completed khi count>=target. Giới hạn: Test DB với rep giả; tag camera là metadata từ caller, không tự xác thực frame/score; race đa writer chưa chứng minh.
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `modules/rehabilitation/rehab_session_adapter.py` · `RehabSessionAdapter.get_or_create_daily_session` · 126–194 (source_code).
  - Đối chiếu: `tests/test_realtime_sync_12_scenarios.py` · `TestRealtimeSync12Scenarios.test_scenario_03_camera_target_10_reps_auto_completion` · 187–253 (test_source).
- **C19 — PARTIALLY_IMPLEMENTED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._do_update_dashboard_ui`; Lines: 967–1083. Explanation: Dashboard ghi DB theo tổng reps, gồm incorrect_reps; score<=0 được thay 90 và quality_threshold chưa là điều kiện completed. Giới hạn: UI khen hoàn thành không chứng minh mọi lần đúng form. Chưa thấy chặn hardware_valid tại điểm record_verified_rep.
- **C20 — IMPLEMENTED**. File: `app/today_todo_widget.py`; Symbol: `TodayTodoWidget._on_confirm_taken`; Lines: 505–509. Explanation: Thuốc hiện hiển thị và thao tác qua TodayTodo/Elder Sync Client cùng unified DB. Giới hạn: Tự khai báo self_reported_taken; không chứng minh đã nuốt thuốc. Test không phải xác nhận từ người dùng thật.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/elder_sync_client.py` · `ElderSyncClient.flush_offline_queue` · 144–379 (source_code).
- **C21 — PARTIALLY_IMPLEMENTED**. File: `web/api_router.py`; Symbol: `ApiRouter._create_prescription`; Lines: 1384–1535. Explanation: Prescription create sinh occurrences hôm nay và3 ngày tiếp theo; relay chuyển quá hạn PENDING/REMINDING. Giới hạn: Chưa thấy tác vụ gia hạn occurrences dài ngày ở active dashboard/backend; UTC+7 hardcode ở create; SNOOZED không thuộc scan quá hạn.
  - Đối chiếu: `services/outbox_relay.py` · `OutboxRelayService.scan_overdue_tasks` · 208–331 (source_code).
- **C24 — IMPLEMENTED**. File: `services/local_voice/recorder.py`; Symbol: `AudioRecorder`; Lines: 8–71. Explanation: Recorder explicit sounddevice Input Stream, mono/resample16kHz, stop/cancel/bound duration; không nghe nền. Giới hạn: Stream48k→16k đã test bằng mock; physical mic chưa kiểm chứng trong artefact hiện có.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `tests/voice_ai/test_local_voice.py` · `test_recorder_hardware_sample_rate_resampling_bounded_and_close` · 208–234 (test_source).
- **C25 — IMPLEMENTED**. File: `services/local_voice/engine.py`; Symbol: `LocalSttEngine`; Lines: 8–44. Explanation: Engine faster-whisper small multilingual local files only, CPU/int8, beam 1, languagevi, VAD và consume segments ngoài UI. Giới hạn: Có inference file local; audio chuẩn/consent chưa xác minh; không có WER/CER hợp lệ; GPU chưa chạy thành công.
  - Đối chiếu: `reports/local_stt/cpu-final.json` · `module` · 1–145 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/local_stt/clean-smoke.txt` · `module` · 1–3 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/local_voice/config.py` · `VoiceConfig` · 7–29 (source_code).
  - Đối chiếu: `services/local_voice/worker.py` · `run_worker` · 8–49 (source_code).
- **C27 — IMPLEMENTED**. File: `services/local_voice/dispatcher.py`; Symbol: `CommandDispatcher.dispatch`; Lines: 47–104. Explanation: Dispatcher sáu intent dùng handler nút bấm, xác nhận dose default No và kiểm tra lại context/command id. Giới hạn: Không có intent hoàn thành phục hồi; không dùng transcript tự sửa DB; sample text/mock audio chưa là E2E thật.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/registry.py` · `module` · 1–53 (source_code).
  - Đối chiếu: `tests/transcript_intent/test_lifecycle_integration.py` · `test_proposed_medication_confirmation_same_db_and_web` · 193–221 (test_source).
- **C28 — PARTIALLY_IMPLEMENTED**. File: `services/transcript_intent/service.py`; Symbol: `GeminiIntentService`; Lines: 12–100. Explanation: Lớp hiểu text Gemini đã có code/backend/client/coordinator, nhưng cloud mặc định false và full acceptance chưa nghiệm thu. Giới hạn: 3 synthetic cases SDK thật; chưa 102 acceptance, mic→web, project/quota independent verify hoặc newest key smoke.
  - Đối chiếu: `reports/gemini_intent/limited-live-benchmark.json` · `module` · 1–60 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/config.py` · `BackendConfig` · 7–42 (source_code).
- **C30 — IMPLEMENTED**. File: `services/transcript_intent/schema.py`; Symbol: `module`; Lines: 1–44. Explanation: Schema Pydantic enum/extraforbid và semantic validator giới hạn intent/context/evidence/negation; không tin confidence. Giới hạn: Đúng trên các mock/tập tổng hợp đã kiểm tra; chưa đo unsafe routing quy mô người dùng thực.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/policy.py` · `validate_proposal` · 61–76 (source_code).
  - Đối chiếu: `tests/transcript_intent/test_contract_policy.py` · `test_schema_forbids_policy_confidence_tools_and_custom_snooze` · 52–63 (test_source).
- **C31 — IMPLEMENTED**. File: `services/transcript_intent/gemini_adapter.py`; Symbol: `GeminiIntentAdapter.generate`; Lines: 14–64. Explanation: OfficialSDK textgenerateContent, JSON schema, tools=[] và functioncalling disabled; total≤8s, transport≥10s. Giới hạn: Không cấp DB/SQL/email/grounding. Hạn total là client deadline; transport cancel/release thiết bị thật cần stress.
  - Đối chiếu: `reports/gemini_intent/limited-live-benchmark.json` · `module` · 1–60 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `tests/transcript_intent/test_lifecycle_integration.py` · `test_sdk_contract_and_no_implicit_tools` · 234–251 (test_source).
- **C32 — IMPLEMENTED**. File: `services/transcript_intent/budget.py`; Symbol: `ProjectBudget`; Lines: 17–75. Explanation: Quota file lock, reservation1200tokens, caps 1 RPM/2400 TPM/10 RPD reserve 2, retry bounded và circuit breaker. Giới hạn: Caps local, không phải quota provider được xác minh; file system shared không phải limiter nhiều host.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/service.py` · `GeminiIntentService._cloud_locked` · 43–82 (source_code).
  - Đối chiếu: `tests/transcript_intent/test_contract_policy.py` · `test_quota_shared_across_instances_and_circuit` · 107–123 (test_source).
- **C33 — IMPLEMENTED**. File: `services/transcript_intent/backend.py`; Symbol: `TranscriptIntentEndpoint.handle`; Lines: 18–55. Explanation: HTTP text endpoint kiểm tra session/auth/patient/context version trước và sau classification. Giới hạn: Loopback HTTP+Qt+DB giả, Gemini mock; không có mic/remoteprovider trong HTTPsmoke.
  - Đối chiếu: `reports/gemini_intent/http-smoke.json` · `module` · 1–10 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `tests/transcript_intent/test_lifecycle_integration.py` · `test_backend_rechecks_auth_and_version` · 143–172 (test_source).
- **C38 — PARTIALLY_IMPLEMENTED**. File: `web/api_router.py`; Symbol: `ApiRouter.handle_request`; Lines: 65–258. Explanation: Web có recommendation/reports/review/emergencycontacts và các màn caregiver/clinician/admin. Giới hạn: Sự có mặt endpoint/UI không chứng minh tất cả chức năng được browser nghiệm thu; emergencycontacts không tự gọi điện.
  - Đối chiếu: `web/templates/portal_caregiver.html` · `module` · 1–2375 (source_code).
  - Đối chiếu: `web/templates/portal_clinician.html` · `module` · 1–2256 (source_code).
  - Đối chiếu: `web/templates/portal_admin.html` · `module` · 1–2385 (source_code).
- **C40 — IMPLEMENTED**. File: `database/connection.py`; Symbol: `UnifiedDatabaseManager`; Lines: 51–115. Explanation: Database runtime là SQLite/WAL/foreignkeys/bus y timeout; không có PostgreSQL driver runtime trong manager. Giới hạn: Các comment PostgreSQL/ANSI/3NF là định hướng, không là chứng minh tương thích hoặc chuẩn hóa hình thức.
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
- **C41 — IMPLEMENTED**. File: `database/migrator.py`; Symbol: `module`; Lines: 1–62. Explanation: 4 migration định nghĩa schema, Migrator áp dụng theo version; importer gộp DB standalone/JSON. Giới hạn: Không mở DBproduction trong audit; seed không phải dữ liệu camera/micro/sensor thực; migration atomicity chưa fault inject.
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `database/importer.py` · `DataImporter.import_all` · 54–88 (source_code).
- **C42 — IMPLEMENTED**. File: `services/outbox_relay.py`; Symbol: `OutboxRelayService.process_pending_events`; Lines: 86–144. Explanation: Outbox relay poll0.5s gửi tín hiệu SSE/auth, side effect email và markprocessed; UI web refetch dữ liệu. Giới hạn: Test in-process queue; không phải 3 thiết bị qua Internet; processed≠client đã render hoặc SMTP đã tới mailbox.
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `web/sse_hub.py` · `SSEHub.dispatch_outbox_event` · 82–128 (source_code).
- **C43 — IMPLEMENTED**. File: `services/elder_sync_client.py`; Symbol: `ElderSyncClient.enqueue_event`; Lines: 101–142. Explanation: Elder Sync Client truy cập SQLite trực tiếp; offline JSON queue perpatient và sync inbox dedup; voice không replay. Giới hạn: is_online là flag, không đo mạng; không đồng bộ SQLite độc lập giữa nhiều máy.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/elder_sync_client.py` · `ElderSyncClient.flush_offline_queue` · 144–379 (source_code).
  - Đối chiếu: `tests/voice_ai/test_local_voice.py` · `test_voice_version_conflict_offline_and_restart_never_replay` · 177–191 (test_source).
- **C44 — IMPLEMENTED**. File: `web/auth.py`; Symbol: `AuthService.check_patient_access`; Lines: 428–509. Explanation: Auth phân quyền theo users active/patient active/careteam/consent và SSE recheck quyền; session RAM7 ngày. Giới hạn: Có các guard đã test; không suy ra hệ thống bảo mật production. Restart mất token/session.
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/http-smoke.json` · `module` · 1–10 (existing_test_or_runtime_artifact).
  - Đối chiếu: `web/auth.py` · `AuthService.create_session` · 399–412 (source_code).
  - Đối chiếu: `tests/transcript_intent/test_lifecycle_integration.py` · `test_real_auth_relationship_revocation` · 349–369 (test_source).
- **C45 — PARTIALLY_IMPLEMENTED**. File: `web/auth.py`; Symbol: `AuthService.authenticate_credentials`; Lines: 67–200. Explanation: Auth còn lưu password dạng prefix+plaintext, bypass kiểudemo và hint lộ mật khẩu khi sai. Giới hạn: Rủi ro nghiêm trọng nhìn thấy từ code; không kiểm tra khai thác, không sao chép giá trị mật khẩu vào báo cáo.
  - Đối chiếu: `web/auth.py` · `AuthService.register_caregiver` · 207–335 (source_code).
- **C47 — PLANNED**. File: `database/migrations/001_initial_schema.sql`; Symbol: `module`; Lines: 1–434. Explanation: PostgreSQL là định hướng trong tài liệu/schema comment, chưa là runtime backend. Giới hạn: Không suy đoán đã deploy Postgres/Supabase/Redis vì tên mục tiêu; runtime đã kiểm tra source chỉ sqlite 3.
  - Đối chiếu: `database/connection.py` · `UnifiedDatabaseManager` · 51–115 (source_code).
- **C49 — IMPLEMENTED**. File: `requirements.txt`; Symbol: `module`; Lines: 1–26. Explanation: Runtime requirements chính+lock Linux/STT/backend SDK; đã có log cài sạchLinux và pipcheck. Giới hạn: Windows constraints/build/installer/model DLL mới chưa nghiệm thu; pin Linux không chứng minh Windows wheel.
  - Đối chiếu: `reports/gemini_intent/clean-pip-check.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/clean-full-install.txt` · `module` · 1–186 (existing_test_or_runtime_artifact).
  - Đối chiếu: `requirements-linux.lock` · `module` · 1–64 (source_code).
  - Đối chiếu: `requirements-gemini-backend.txt` · `module` · 1–4 (source_code).
- **C50 — PARTIALLY_IMPLEMENTED**. File: `AI_Rehab_Safety_Assistant.spec`; Symbol: `module`; Lines: 1–143. Explanation: Spec excludes Gemini SDK/provider/backend env khỏi EXE; chưa build binary kiểm chứng ranh giới này. Giới hạn: Reviewsource recipe thôi, không chứng minh binary không secret. Không đọc .envprivate hoặc tải/cài package trong audit.
- **C51 — IMPLEMENTED**. File: `reports/local_stt/cpu-final.json`; Symbol: `module`; Lines: 1–145. Explanation: STT CPU 12 lượt: cold 727 ms, p50=4642 ms, p95=6015.95ms, RSS 1830600704 bytes; camera/GPU thất bại. Giới hạn: Đo script engine/audio 873–1170 ms, không phải full app/micđồngthời, thiếu groundtruth; p95 này là số cũ, chưa chạy lại.
  - Đối chiếu: `reports/local_stt/cpu-final.json` · `module` · 1–145 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/local_stt/gpu-camera.json` · `module` · 1–7 (existing_test_or_runtime_artifact).
- **C52 — IMPLEMENTED**. File: `reports/gemini_intent/offline-benchmark.json`; Symbol: `module`; Lines: 1–1385. Explanation: Offline policy 150 cases:104 correct; acceptance 72/102; 0 unexpected sensitive routes trong tập tổng hợp. Giới hạn: Cloudtắt; 69.33%toàn tập, 70.59%acceptance là policy coverage không là Geminiaccuracy hoặc STT WER.
  - Đối chiếu: `reports/gemini_intent/offline-benchmark.json` · `module` · 1–1385 (existing_test_or_runtime_artifact).
- **C53 — IMPLEMENTED**. File: `reports/gemini_intent/limited-live-benchmark.json`; Symbol: `module`; Lines: 1–60. Explanation: 3 synthetic API cases đạt schema/intent, latency 1633/1138/1562 ms; full acceptance=false/quota_verified=false. Giới hạn: n3 và một smoke1746ms riêng; không đủ chứng minh accuracy95% hay latency ổn định. Audit không gọi API.
  - Đối chiếu: `reports/gemini_intent/limited-live-benchmark.json` · `module` · 1–60 (existing_test_or_runtime_artifact).
- **C54 — IMPLEMENTED**. File: `reports/gemini_intent/REPORT.md`; Symbol: `module`; Lines: 1–75. Explanation: 3 nhóm test log hiện có 107+41+13 passed; không có bằng chứng toàn repo pass và không chạy lại trong audit. Giới hạn: Tổng 161 thuộc 3 nhóm được ghi; 85/17/6/16 ở report khác có overlap. Một số baseline native audio timeout/DB fail còn ghi.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/legacy-regression-isolated.txt` · `module` · 1–8 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
- **C55 — UNKNOWN**. File: `reports/local_stt/REPORT.md`; Symbol: `module`; Lines: 1–58. Explanation: Face FAR/FRR, emotion holdout F1, rehab clinical angle error, STT WER và nghiệm thu mic/camera/multi host chưa có bằng chứng phù hợp. Giới hạn: Không có số đo hợp lệ trong các artefact đã đối chiếu; không khẳng định không tồn tại ngoài repo.
  - Đối chiếu: `reports/gemini_intent/REPORT.md` · `module` · 1–75 (source_code).

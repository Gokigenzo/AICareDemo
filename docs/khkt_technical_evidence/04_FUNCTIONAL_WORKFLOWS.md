# Luồng chức năng và boundary dữ liệu

## 1. Danh tính→hồ sơ

Frame→FaceAdapter.detect_face→preprocess ROI→LBPH→recognize_face temporal state→Dashboard._do_update_dashboard_ui→_resolve_patient_id(legacy_patient_map trước fallback)→set_patient cho TodayTodo/games và context voice. Hồ sơ đăng ký qua Registration Dialog/FaceAdapter.register_patient, JSON/crop và sync_single_patient. Không có một faceembeddingDB riêng hiện hành. [C04/C06–C09]

Input cần mặt nhìn camera và crop có chất lượng. No face/unknown hiển thị trạng thái tương ứng; uncertain có TTL. Unknown không xóa current_patient_id nên cần nghiệm thu quyền thao tác tay khi người cũ rời chỗ. TodayTodo.refresh_data có fallbackfirstACTIVEpatient nếu patient không tìm thấy; branch này chưa thấy switch_patient sync client tương ứng. Voice snapshot rejectbindingmismatch; không suy ra mọi nút tay được bảo vệ tương tự. [C04/C20/C27]

## 2. Thuốc→hiển thị→xác nhận→người nhà

| Bước | Code path | Đọc/ghi và giới hạn |
|---|---|---|
| Tạo/sửa đơn | ApiRouter._create_prescription/_revise_prescription | prescriptions/items/schedules revision, occurrence snapshots; create sinh 4 ngày, UTC+7 hardcode |
| Hiển thị hôm nay | TodayTodo.refresh_data/_render_medications | SELECTdose theo ngày; ảnh, tên, dose, instructions và các nút state-dependent |
| Nhắc/quá hạn | OutboxRelayService.scan_overdue_tasks | PENDING/REMINDING quá grace→OVERDUE, alerts, outbox; SNOOZED không thuộc scan |
| Xác nhận tay | TodayTodo._on_confirm_taken | ElderSyncClient.confirm_dose_taken(self_reported_taken) |
| Xác nhận voice | CommandDispatcher.dispatch | Đúng 1 dose, exact context, dialog default No, recheck trước service |
| Commit | ElderSyncClient.flush_offline_queue | sync_inbox idempotency, dose_occurrencesCONFIRMED, dose_events, outbox; lateaction có note |
| Theo dõi | Relay→SSEHub→web refetch _get_medication_doses | Có selfreported label; SSE queue test đãpass, browser Internet/email thật chưa nghiệm thu |

Snooze hiện lưu stateSNOOZED; cần bổ sung bằng chứng nhắc lại sau delay và không mắc kẹt khi quá hạn. Help đổistateREMINDING và tạoalert, relay chọnprimaryactivecaregiver có consent/email. Hộp thoại desktop có liên hệ hardcode và khẳng định gửi tới người nhà/bác sĩ; không coi đây là chứng cứ thư đã tới hay bên kia sẽ đến ngay. [C20–C23/C27/C42]

Medication Service/Medication Panel và moduleScheduler có test riêng 16 case nhưng panel=None trong dashboard active. Không nối mũi tên từ schedulerlegacy sang TodayTodo khi source không có call. Xác nhận chỉ tự khai báo, không dùng camera để xác minh nuốt thuốc, không suy ra tuân thủ điều trị khách quan. [C20/C23]

## 3. Kế hoạch→camera reps→DB→bác sĩ

Web _update_exercise_plan tạo version/audit/outbox; dashboard pollplan mỗi2s, chọnbài và _on_start_exercise kiểm tra expected plan. RehabSessionAdapter.get_or_create_daily_session giữplan_version/target_count_snapshot. Camera Manager callback→RehabAdapter→RehabilitationEngine/FSM→metrics→dashboard record_verified_rep cho mỗi rep mới. Event unique +update count +outbox cùng transaction; web _get_rehab_sessions đọc sau SSE. [C14–C19/C27/C42]

Stop/pause/hide/mất pose xử lý state partial và metrics; missing camera cần markunavailable thay hoàn thành. Tuy nhiên hardware_valid không được chuyển thành điều kiện bắt buộc tại điểmDBwrite đã kiểm tra. Cần test ngắt camera/simulated frame và tình huốngframecũ trước gọi camera_verified_completed. DBcaller có thể đưa rep giả; tên state không là at test at io n nguồn camera. [C03/C18/C19]

Khi tổngreps đạt target, routine tiến bài tiếp theo và completed label, gồm cảincorrectreps; quality_threshold chỉ lưuversion chưa chặn completed. Không viết “10/10 đúng chuẩn” từ count 10/10. Ngày session dùng date.today của host, plan có time z one nhưng chưa chứng minh mọi đường respectIANA/DST. [C18/C19]

## 4. Biểu cảm→lưu→monitoring

Camera→EmotionAdapter.process_frame→3lớp/smoothing→_persist_result→shared/results/emotion.json và shared state. Web _get_mood đọc mood_checkins và emotion_inferences. Không thấy insertioncamera trongactiveadapter/controller/service. Seed DataImporter._seed_mood_and_emotions tạo demonstrationrows; không xem seed như historycảmxúc thực. Vì vậy workflow camera emotion→unifiedDB→web là PARTIALLY_IMPLEMENTED. Moodbutton→record_mood→mood_checkins/outbox là luồng tự khai báo riêng. [C10–C13/C41]

## 5. Voice→intent→action

LocalVoiceWidget dưới tabs luôn có micro; khi flagfalse/worker chưa có, clickđầu chuẩn bịmodel và idle; clicktiếp mới record. Ghi chủ động, Dừng→inference, Hủy→token invalidate; tối đa15s(default). Khi đổi patient/tab/source/plan, captured context mất giá trị. Các state/error code được render để giữ nút tay dùng tiếp. [C02/C24–C26]

Transcript→VoiceRequestCoordinator→local rules; câu đủ neutralcatalog và cloudconfigured mới→internalHTTPauthenticated→Transcript Intent Endpoint recheckauth/stateversion→Gemini Intent Service privacy/schema/budget→SDK→semanticvalidate→response ID/context check→dispatcher. Backend request có patient/context phục vụ auth nội bộ, payloadprovider bỏ chúng; không coi “ẩnID” đủ để gửi health text. Local med/rehab intent không gửi provider. [C27–C33]

Transcript chỉ là input, không SQL update. Proposal val id mới gọi cùng handler nút; confirmationtaken yêu cầu đúng occurrence/dose revision/context sau dialog, command dedup và service transaction. Offline voice không queue/replay về sau; buttonqueue vẫn tồn tại. Failure Gemini/offline 429/badJSON/late context không mất khả năng bấm tay. Voice không đánh dấu completed rehab. [C20/C27/C30/C33/C43]

## 6. Nhập sức khỏe, lời khuyên và báo cáo

Caregiver web nhập chỉ số→ApiRouter._add_observation→measurement_groups(client_request_idunique) +health_observations +requestmatchingPENDING→COMPLETED/log +outbox. Thời gian measured_at khác recorded_at; corrections/clinicianreviews được schema/API hỗ trợ. Web vẽ timeline/trend từ API, chưa có sensordevice ingestđã nghiệm thu. Nút“đã nhớ đo” ở elder chỉ hiệninfo, không là bản ghi kết quả đo. [C37/C38]

Caregiver report→caregiver_reports/outbox→đúngcareteam; clinician recommendation→care_recommendations→elder read→recommendation_receipts. Emergencycontacts/events chỉ lưu/hiển thị/log, không tự liên lạc cứu hộ. Aggregationtrend có trong Monitoring Service standalone; active Web có SQL/API riêng, không giả định dùng mọi phép aggregate của standalone. [C38/C42/C44]

## 7. Trò chơi và nhạc

CognitiveGamesWidget→Game Engine seededrandom tạoboard3/4/6cặp trên UI, sequence 2/3/4 hình; service repository ghi gamesessions/results vào data/cognitive_games.sqlite3. Engine có expert 8 cặp/5 hình nhưng UI hiện không expose mặc định. Musicwidget dùng Audio Service; voicepausesaudio khi record. Identity module dùng MockPatientIdentityAdapter như binding explicit, không một model nhận diệnthứhai. Importer có thể gộp history games vàounified; chưa chứng minh livepushgame→web. Không có bằng chứng trị liệu trí nhớ hiệu quả. [C34/C39/C41]

## Ma trận lỗi và fallback

| Trigger | Phản ứng có source/test | Phần chưa kiểm chứng |
|---|---|---|
| Thiếu model/PortAudio/micro | Voice unavailable, retry, nút tay | Micdriver/OS thật và restartkhi đang ghi |
| Face unknown/patient đổi | Voice context invalidate/guard | Hành động tay vàfallbackfirstpatient |
| Context/dose/plan đổi giữa request | Bỏ response/rechecktransaction | Stress nhiều writer/phút/thiết bị |
| Network/429/provider timeout | Bounded retry/circuit, local/unknown | Quota AI Studio, full 102 acceptance |
| SMTP error | Delivery FAILED trong service/test mock | Mailbox/nhận đọc/retry timed thực tế |
| SSEdisconnect | Frontendrefetch/reconnect/pollfallback | Latencybrowser3thiếtbị/HTTPS ngoài LAN |
| Cameraunplug/occlusion | Simulated frame/partial reset | Hardwaregate tạiDBcompletion |

## Bằng chứng truy nguyên

- **C02 — IMPLEMENTED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._init_ui`; Lines: 175–528. Explanation: Dashboard mount TodayTodo, camera/phục hồi, trò chơi và thanh micro; smoke offscreen đã kiểm tra lifecycle. Giới hạn: Camera/audio mocked, TTS tắt, SMTP bị chặn; không phải nghiệm thu phần cứng.
  - Đối chiếu: `reports/gemini_intent/dashboard-smoke.txt` · `module` · 1–44 (existing_test_or_runtime_artifact).
- **C03 — PARTIALLY_IMPLEMENTED**. File: `core/camera_manager.py`; Symbol: `CameraManager.run`; Lines: 193–270. Explanation: Camera Manager sở hữu luồng QThread và callback xử lý ảnh, có ảnh mô phỏng khi không đọc được camera. Giới hạn: Camera mất có thể tiếp tục ảnh mô phỏng; phải kiểm chứng không ghi completed sai khi mất phần cứng.
  - Đối chiếu: `app/dashboard.py` · `DashboardWindow._process_video_frame` · 530–570 (source_code).
- **C04 — PARTIALLY_IMPLEMENTED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._do_update_dashboard_ui`; Lines: 967–1083. Explanation: Nhận diện và chọn patient đồng bộ binding các widget; voice invalidates context khi đổi patient/tab/source. Giới hạn: Unknown-face không xóa current_patient_id; voice có guard riêng, hành động tay cần kiểm tra đổi/người lạ.
  - Đối chiếu: `app/dashboard.py` · `DashboardWindow._resolve_patient_id` · 936–953 (source_code).
  - Đối chiếu: `services/local_voice/dispatcher.py` · `CommandDispatcher.snapshot` · 24–45 (source_code).
- **C06 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.__init__`; Lines: 40–81. Explanation: Face detection ưu tiên OpenCV DNN, fallback Haar; nhận diện bằng LBPH radius 1/neighbors 8/grid8x8. Giới hạn: Có pipeline; chưa có FAR/FRR trên tập người độc lập; DNN detector không phải model nhận dạng identity.
  - Đối chiếu: `adapters/face_adapter.py` · `FaceAdapter.detect_face` · 107–146 (source_code).
- **C09 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.register_patient`; Lines: 614–719. Explanation: Đăng ký lưu crop và hồ sơ JSON, sync sang unified DB và retrain LBPH. Giới hạn: Test registration tồn tại nhưng một số dùng đường dữ liệu mặc định; không chạy trong audit để tránh sửa hồ sơ.
  - Đối chiếu: `services/patient_sync_service.py` · `sync_single_patient` · 44–262 (source_code).
- **C13 — PARTIALLY_IMPLEMENTED**. File: `adapters/emotion_adapter.py`; Symbol: `EmotionAdapter._persist_result`; Lines: 359–374. Explanation: Biểu cảm camera ghi JSON/state, web đọc emotion_inferences; chưa thấy writer unified DB trong đường camera. Giới hạn: Schema và seed emotion_inferences không chứng minh camera→DB→web; tìm kiếm call sites tĩnh chưa thấy cầu nối.
  - Đối chiếu: `web/api_router.py` · `ApiRouter._get_mood` · 1052–1076 (source_code).
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
- **C22 — PARTIALLY_IMPLEMENTED**. File: `services/elder_sync_client.py`; Symbol: `ElderSyncClient.flush_offline_queue`; Lines: 144–379. Explanation: Snooze đổi state sangSNOOZED, help tạo cảnh báo; chưa xác minh nhắc lại timed trong active dashboard. Giới hạn: Hộp thoại help tuyên bố gửi/nhận và dùng liên hệ hardcode; DB alert không chứng minh SMTP delivery hoặc người nhận xử lý.
  - Đối chiếu: `app/today_todo_widget.py` · `TodayTodoWidget._on_help_requested` · 515–525 (source_code).
- **C23 — DEPRECATED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._init_ui`; Lines: 175–528. Explanation: Medication Panel/Medication Service và scheduler standalone còn code/test nhưng không mount trong dashboard hiện tại. Giới hạn: Deprecated theo active dashboard, standalone vẫn có thể chạy; kết quả scheduler cũ không chứng minh luồng thuốc unified.
  - Đối chiếu: `reports/medication_migration/medication_tests.txt` · `module` · 1–21 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/medication_service.py` · `module` · 1–262 (source_code).
  - Đối chiếu: `modules/medication_adherence/services/scheduler.py` · `module` · 1–325 (source_code).
- **C24 — IMPLEMENTED**. File: `services/local_voice/recorder.py`; Symbol: `AudioRecorder`; Lines: 8–71. Explanation: Recorder explicit sounddevice Input Stream, mono/resample16kHz, stop/cancel/bound duration; không nghe nền. Giới hạn: Stream48k→16k đã test bằng mock; physical mic chưa kiểm chứng trong artefact hiện có.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `tests/voice_ai/test_local_voice.py` · `test_recorder_hardware_sample_rate_resampling_bounded_and_close` · 208–234 (test_source).
- **C26 — IMPLEMENTED**. File: `services/local_voice/controller.py`; Symbol: `VoiceSessionController`; Lines: 9–154. Explanation: Controller spawn một persistent worker, token/context bỏ response cũ; shutdown chờ rồi terminate/kill hữu hạn. Giới hạn: Native inference không bị ngắt mềm ngay khi cancel; chỉ bỏ kết quả/chờ acknowledgement; test không có mic vật lý.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/dashboard-smoke.txt` · `module` · 1–44 (existing_test_or_runtime_artifact).
  - Đối chiếu: `tests/voice_ai/test_local_voice.py` · `test_cancel_and_context_change_discard_late_results_and_shutdown` · 70–93 (test_source).
- **C27 — IMPLEMENTED**. File: `services/local_voice/dispatcher.py`; Symbol: `CommandDispatcher.dispatch`; Lines: 47–104. Explanation: Dispatcher sáu intent dùng handler nút bấm, xác nhận dose default No và kiểm tra lại context/command id. Giới hạn: Không có intent hoàn thành phục hồi; không dùng transcript tự sửa DB; sample text/mock audio chưa là E2E thật.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/registry.py` · `module` · 1–53 (source_code).
  - Đối chiếu: `tests/transcript_intent/test_lifecycle_integration.py` · `test_proposed_medication_confirmation_same_db_and_web` · 193–221 (test_source).
- **C28 — PARTIALLY_IMPLEMENTED**. File: `services/transcript_intent/service.py`; Symbol: `GeminiIntentService`; Lines: 12–100. Explanation: Lớp hiểu text Gemini đã có code/backend/client/coordinator, nhưng cloud mặc định false và full acceptance chưa nghiệm thu. Giới hạn: 3 synthetic cases SDK thật; chưa 102 acceptance, mic→web, project/quota independent verify hoặc newest key smoke.
  - Đối chiếu: `reports/gemini_intent/limited-live-benchmark.json` · `module` · 1–60 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/config.py` · `BackendConfig` · 7–42 (source_code).
- **C29 — IMPLEMENTED**. File: `services/transcript_intent/policy.py`; Symbol: `module`; Lines: 1–76. Explanation: Privacy gate production chỉ 20 câu điều hướng trung tính; nội dung thuốc/phục hồi xử lý local, unknown không đoán. Giới hạn: Đảm bảo theo catalog đã review, không phải bộ khử nhạy cảm tổng quát; không cho tùy ý text sức khỏe vào free API.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/prompts.py` · `module` · 1–23 (source_code).
  - Đối chiếu: `tests/transcript_intent/test_contract_policy.py` · `test_privacy_default_deny_not_id_redaction` · 38–39 (test_source).
- **C30 — IMPLEMENTED**. File: `services/transcript_intent/schema.py`; Symbol: `module`; Lines: 1–44. Explanation: Schema Pydantic enum/extraforbid và semantic validator giới hạn intent/context/evidence/negation; không tin confidence. Giới hạn: Đúng trên các mock/tập tổng hợp đã kiểm tra; chưa đo unsafe routing quy mô người dùng thực.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/policy.py` · `validate_proposal` · 61–76 (source_code).
  - Đối chiếu: `tests/transcript_intent/test_contract_policy.py` · `test_schema_forbids_policy_confidence_tools_and_custom_snooze` · 52–63 (test_source).
- **C33 — IMPLEMENTED**. File: `services/transcript_intent/backend.py`; Symbol: `TranscriptIntentEndpoint.handle`; Lines: 18–55. Explanation: HTTP text endpoint kiểm tra session/auth/patient/context version trước và sau classification. Giới hạn: Loopback HTTP+Qt+DB giả, Gemini mock; không có mic/remoteprovider trong HTTPsmoke.
  - Đối chiếu: `reports/gemini_intent/http-smoke.json` · `module` · 1–10 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `tests/transcript_intent/test_lifecycle_integration.py` · `test_backend_rechecks_auth_and_version` · 143–172 (test_source).
- **C34 — IMPLEMENTED**. File: `services/local_voice/controller.py`; Symbol: `VoiceSessionController.start`; Lines: 56–73. Explanation: TTS được suspend khi ghi; nhạc pause; child pyttsx3 local giữ entrypoint frozen riêng. Giới hạn: Phối hợp đã test code/mocks; chưa nghe playbackloa thật; nhắc thuốc/coach active chưa nối toàn bộ TTS callbacks.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/local_voice/tts_runtime.py` · `speak` · 5–19 (source_code).
  - Đối chiếu: `app/local_voice_widget.py` · `module` · 1–110 (source_code).
  - Đối chiếu: `tests/voice_ai/test_local_voice.py` · `test_tts_cannot_restart_during_capture` · 194–205 (test_source).
- **C37 — IMPLEMENTED**. File: `web/api_router.py`; Symbol: `ApiRouter._add_observation`; Lines: 701–822. Explanation: Theo dõi sức khỏe web ghi measurementgroups/observations, request completed và outbox cùng transaction. Giới hạn: Nhập tay từ người chăm sóc; không có đường sensor IoT đã nghiệm thu; unit/range validation cần đối chiếu backend/UI.
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
- **C38 — PARTIALLY_IMPLEMENTED**. File: `web/api_router.py`; Symbol: `ApiRouter.handle_request`; Lines: 65–258. Explanation: Web có recommendation/reports/review/emergencycontacts và các màn caregiver/clinician/admin. Giới hạn: Sự có mặt endpoint/UI không chứng minh tất cả chức năng được browser nghiệm thu; emergencycontacts không tự gọi điện.
  - Đối chiếu: `web/templates/portal_caregiver.html` · `module` · 1–2375 (source_code).
  - Đối chiếu: `web/templates/portal_clinician.html` · `module` · 1–2256 (source_code).
  - Đối chiếu: `web/templates/portal_admin.html` · `module` · 1–2385 (source_code).
- **C39 — PARTIALLY_IMPLEMENTED**. File: `app/cognitive_games_widget.py`; Symbol: `CognitiveGamesWidget.__init__`; Lines: 54–80. Explanation: Trò chơi lật cặp/nhớ trình tự dùng rules seededrandom, service/repository; desktop ghi SQLite riêng. Giới hạn: Import sang unified là bước import, chưa thấy live outbox từ gameplay; không có chứng cứ cải thiện nhận thức lâm sàng.
  - Đối chiếu: `modules/cognitive_games/services/game_engine.py` · `GameEngine` · 14–143 (source_code).
  - Đối chiếu: `database/importer.py` · `DataImporter._import_cognitive_games` · 472–541 (source_code).
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
- **C55 — UNKNOWN**. File: `reports/local_stt/REPORT.md`; Symbol: `module`; Lines: 1–58. Explanation: Face FAR/FRR, emotion holdout F1, rehab clinical angle error, STT WER và nghiệm thu mic/camera/multi host chưa có bằng chứng phù hợp. Giới hạn: Không có số đo hợp lệ trong các artefact đã đối chiếu; không khẳng định không tồn tại ngoài repo.
  - Đối chiếu: `reports/gemini_intent/REPORT.md` · `module` · 1–75 (source_code).

## Boundary bổ sung cần nghiệm thu

API rehab-event chỉ qua permission view, handler tăng count theo body và chưa đối chiếu session.patient_id với patient URL. Vì vậy API ngoài đường camera có thể ghi nhãn camera_verified_completed; phải kiểm tra quyền write/ownership và nguồn event trước sử dụng dữ liệu thật. Web chart còn có dải tham chiếu hardcode, chưa chứng minh cá nhân hóa/validation lâm sàng. Không dùng nhãn “an toàn” trên UI làm chứng cứ y tế. [C57/C58]

## Bằng chứng truy nguyên

- **C57 — PARTIALLY_IMPLEMENTED**. File: `web/templates/portal_clinician.html`; Symbol: `module`; Lines: 1–2256. Explanation: Web chart có dải tham chiếu sức khỏe hardcode; chưa có chứng cứ validation/personalization lâm sàng. Giới hạn: Chỉ mô tả source UI; không công nhận các dải này là khuyến nghị y tế đúng cho mọi người.
- **C58 — PARTIALLY_IMPLEMENTED**. File: `web/api_router.py`; Symbol: `ApiRouter._handle_rehab_event`; Lines: 1128–1224. Explanation: Rehab-event API nhận quyền view, tăng count từ body; chưa so session.patient_id với patient URL hay xác thực nguồn camera. Giới hạn: Rủi ro theo source, chưa gọi endpoint/thử khai thác. Không dùng tag camera_ai như at test at io n; cần auth/write/ownership tests.
  - Đối chiếu: `web/api_router.py` · `ApiRouter.handle_request` · 65–258 (source_code).

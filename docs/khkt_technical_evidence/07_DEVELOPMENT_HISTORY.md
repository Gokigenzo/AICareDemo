# Lịch sử phát triển có chứng cứ

## Nguồn và mức tin cậy

git log hiện có hai commit ngày 30/09/2026: c6aafea(feat,v3.0MVP) và ebcdcbb(updateREADME). Têncommit là mô tả tác giả, không chứng minh hoàn thiện mọi chức năng. Worktree hiện chứa nhiều file modified/untracked, nên không gán toànbộpipeline mới vào một commit hay dựng thời gian từng thay đổi. source_snapshot.json giúp đóng băng snapshot kiểm toán, không là releasehashđãpublish.

## Các chuyển đổi quan sát được

| Giai đoạn/record | Quyết định và chứng cứ | Trạng thái hiện tại / giới hạn |
|---|---|---|
| Face/emotion/rehab standalone vàlauncher | Module folder vàadapter integration | Dashboardactive LBPH/biểu cảm 3 lớp/FSM; không dùng age/gender độc lập làm identity |
| Fall/HFD/video experiment at io n | core/fall_*, modules/fall, archive/fall_detection, reportcandidate/fusion | DEPRECATED theo dashboardcameraactive; videotool retained; không thêm vào productcurrentdiagram |
| Chuyển trọng tâm thuốc | plan migration, services/medication_migration, medication report | Legacy service có test nhưng Dashboardpanel=None; activeTodayTodo dùngunifiedDB |
| Thống nhất DB/real time |4migrations, connection/importer, outbox/SSE | IMPLEMENTED phạm viDBtest; games/emotion live vẫn chưa hoàn toànunified |
| GỡAPI STT | plan/KE_HOACH_GO_API_STT.md, router 410, factory disabled, archivevoice | REMOVEDactiveAPIpipeline; không nói everyproviderfile đã xóa |
| STT local 09/10 theo report | services/local_voice, requirementslocks, local_sttREPORT | IMPLEMENTED file inference/lifecycle; micro vật lý/camera/GPU acceptance còn thiếu |
| Nút nhận giọng hiển thị | Dashboard/LocalVoiceWidget, ui-visible-smoke | IMPLEMENTED offscreen; clickđầu load worker nếu chưa có, không listenbackground |
| Gemini text 09/10 theo report | services/transcript_intent, backend/client/SDK, limited-live-benchmark | PARTIALLY_IMPLEMENTED feature; productioncloud=false và free-tiergatecatalog |

Ngày 09/10 từ headingreport/records, không phải timestamp commit đã xác minh độc lập. Kế hoạch mô tả điều dự định làm; report+source/test mới hỗ trợ điều thực sự đãcó. “API STT removed” khác “Gemini text classification”: model nhận text neutral, không nhận audio. [C23/C28/C35/C36/C40–C43/C48/C54]

## Những cải tiến có bằng chứng và bài học

PyAV 19 có lỗi tương thích trong report STT; pin18.1.0 được clean install/transcribe kiểm tra. Bảndevpatched không dùng làm bằng chứng reproducibility; lock Linux vànewcleanenv hữu ích nhưng chưa thay Windows nghiệm thu. [C25/C49]

Native audio import từng làm test timeout. Config/serviceslazy hạn chế side effect backend; smokeQt vẫn mock sounddevice/camera. Đây là cải tiếnboundaryimport, không chứng minh PortAudio được cài và micro thật. [C01/C02/C49/C54]

SDK deadline8s bịprovider400 khi minimum10s; adapter dùng transport≥10s và total client wait≤8s. Recordschema-probe.json giữ failure, limited-live-benchmark giữ3success. Bài học: import SDK hay JSONsuccess không chứng minh quota, privacy, stale context hoặcbusinessE2E. [C31–C33/C53]

Rule/schema/context và privacygate được viết trước/độc lập model. Existing tests phủ case phủ định/unknown/cancel/đổi patient/duplicate/HTTP auth; aggregateofflinecoverage70.59% cho acceptance vẫn thấp. Không mô tả mọiparaphrase tiếng Việt đã hiểu nhờLLM. [C27–C33/C52]

## Điều lịch sử không thể khẳng định

Không có lịch sử commit đầy đủ cho currentworktree, changeauthor/time từng file, chứng nhận release, field trial, thông số calibration hoặc một chuỗi thí nghiệm người thật. Không suy ramoduleweightsource/training provenance từ file name; không kể clinicalimprovement hoặc novelty proof từmarketingREADME. [C55]

## Bằng chứng truy nguyên

- **C01 — PARTIALLY_IMPLEMENTED**. File: `main.py`; Symbol: `main`; Lines: 52–106. Explanation: Desktop khởi động bằng QApplication, khóa single-instance, dashboard và migration/import dữ liệu. Giới hạn: Có mã nguồn; chưa nghiệm thu toàn bộ trên thiết bị đích.
  - Đối chiếu: `app/dashboard.py` · `DashboardWindow.__init__` · 122–173 (source_code).
- **C02 — IMPLEMENTED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._init_ui`; Lines: 175–528. Explanation: Dashboard mount TodayTodo, camera/phục hồi, trò chơi và thanh micro; smoke offscreen đã kiểm tra lifecycle. Giới hạn: Camera/audio mocked, TTS tắt, SMTP bị chặn; không phải nghiệm thu phần cứng.
  - Đối chiếu: `reports/gemini_intent/dashboard-smoke.txt` · `module` · 1–44 (existing_test_or_runtime_artifact).
- **C06 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.__init__`; Lines: 40–81. Explanation: Face detection ưu tiên OpenCV DNN, fallback Haar; nhận diện bằng LBPH radius 1/neighbors 8/grid8x8. Giới hạn: Có pipeline; chưa có FAR/FRR trên tập người độc lập; DNN detector không phải model nhận dạng identity.
  - Đối chiếu: `adapters/face_adapter.py` · `FaceAdapter.detect_face` · 107–146 (source_code).
- **C10 — PARTIALLY_IMPLEMENTED**. File: `adapters/emotion_adapter.py`; Symbol: `EmotionAdapter.process_frame`; Lines: 213–325. Explanation: Biểu cảm dashboard có3 lớp Neutral/Happy/Sad, landmark heuristic và ensemble 75%heuristic+25%MLP khi có model. Giới hạn: Không chẩn đoán tâm lý; chưa có accuracy/macro-F1 holdout hợp lệ cho ensemble 3 lớp.
  - Đối chiếu: `adapters/emotion_adapter.py` · `EmotionAdapter._compute_facs_probabilities` · 146–211 (source_code).
- **C14 — PARTIALLY_IMPLEMENTED**. File: `modules/rehabilitation/rehab_engine.py`; Symbol: `calculate_angle`; Lines: 44–57. Explanation: Phục hồi dùng MediaPipe Pose/Tasks lite và góc2D từ tọa độ landmark chuẩn hóa. Giới hạn: Không dùng 3D chuẩn lâm sàng; x/y chuẩn hóa chưa sửa tỷ lệ khung hình; chưa có sai số góc với thước chuẩn.
  - Đối chiếu: `modules/rehabilitation/rehab_engine.py` · `RehabilitationEngine._init_pose` · 531–583 (source_code).
- **C23 — DEPRECATED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._init_ui`; Lines: 175–528. Explanation: Medication Panel/Medication Service và scheduler standalone còn code/test nhưng không mount trong dashboard hiện tại. Giới hạn: Deprecated theo active dashboard, standalone vẫn có thể chạy; kết quả scheduler cũ không chứng minh luồng thuốc unified.
  - Đối chiếu: `reports/medication_migration/medication_tests.txt` · `module` · 1–21 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/medication_service.py` · `module` · 1–262 (source_code).
  - Đối chiếu: `modules/medication_adherence/services/scheduler.py` · `module` · 1–325 (source_code).
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
- **C35 — REMOVED**. File: `web/api_router.py`; Symbol: `ApiRouter.handle_request`; Lines: 65–258. Explanation: API STT cũ không còn active: router 410 và factory compatibility disabled; không restore orchestrator cũ. Giới hạn: REMOVED chỉ đường API STT active; file/provider/test legacy vẫn tồn tại, không nói mọi source STT đã xóa.
  - Đối chiếu: `services/voice_ai/asr/factory.py` · `module` · 1–14 (source_code).
  - Đối chiếu: `archive/voice/README.md` · `module` · 1–96 (source_code).
  - Đối chiếu: `tests/voice_ai/test_local_voice.py` · `test_legacy_web_voice_disabled_even_when_local_flag_enabled` · 250–257 (test_source).
- **C36 — DEPRECATED**. File: `services/voice_ai/orchestrator/router.py`; Symbol: `module`; Lines: 1–634. Explanation: Các semantic/orchestrator/voicewidget cũ và Voskarchive không là tuyến nhận giọng active. Giới hạn: TTS coordinator cũ còn được reuse; không quy toàn bộ services/voice_ai thành deadcode.
  - Đối chiếu: `app/voice_button_widget.py` · `module` · 1–266 (source_code).
  - Đối chiếu: `app/local_voice_widget.py` · `module` · 1–110 (source_code).
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
- **C48 — DEPRECATED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._process_video_frame`; Lines: 530–570. Explanation: Fall/HFD/ONNX/video còn retainedsource/artefacts nhưng không trong camera callbacks dashboard hiện tại. Giới hạn: Deprecated theo dashboard active; toolvideo riêng vẫn có. Không dùng metricfall cũ thay metric rehab hiện tại.
  - Đối chiếu: `core/fall_pipeline.py` · `module` · 1–542 (source_code).
  - Đối chiếu: `modules/fall/hfd_classifier.py` · `module` · 1–85 (source_code).
- **C49 — IMPLEMENTED**. File: `requirements.txt`; Symbol: `module`; Lines: 1–26. Explanation: Runtime requirements chính+lock Linux/STT/backend SDK; đã có log cài sạchLinux và pipcheck. Giới hạn: Windows constraints/build/installer/model DLL mới chưa nghiệm thu; pin Linux không chứng minh Windows wheel.
  - Đối chiếu: `reports/gemini_intent/clean-pip-check.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/clean-full-install.txt` · `module` · 1–186 (existing_test_or_runtime_artifact).
  - Đối chiếu: `requirements-linux.lock` · `module` · 1–64 (source_code).
  - Đối chiếu: `requirements-gemini-backend.txt` · `module` · 1–4 (source_code).
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


## Bằng chứng truy nguyên

- **C60 — UNKNOWN**. File: `docs/khkt_technical_evidence/audit_observations.json`; Symbol: `module`; Lines: 1–33. Explanation: Gitlog trong snapshot chỉ có2commit ngày30/09/2026; lịch sử thay đổi worktree sau đó chưa được commit đầy đủ. Giới hạn: Gitcommand đã đọc trongaudit; không dựng author/date từngfile hoặc coi commitmessage là featurevalidation.

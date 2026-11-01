# Tổng quan kiểm toán kỹ thuật phục vụ KHKT

Ngày lập: 09/10/2026. Đối tượng là trạng thái worktree hiện tại, gồm nhiều thay đổi chưa commit; đây không phải bản phát hành được xác nhận. Kiểm toán chỉ đọc mã, cấu hình, migration, test và artefact có sẵn; không mở camera/micro, chạy app, cài dependency, gọi API hay gửi thông báo. Các số đo bên dưới là kết quả lịch sử có đường dẫn truy nguyên, chưa được chạy lại trong lượt này.

## Kết luận về mức sẵn sàng

Repo có nguyên mẫu desktop PyQt5 và web người nhà/bác sĩ/admin, xử lý ảnh cục bộ, STT faster-whisper, intent allowlist và lớp Gemini text có giới hạn. Có bằng chứng kiểm thử cho nhiều thành phần kỹ thuật. Chưa đủ bằng chứng để gọi đây là hệ thống đã nghiệm thu tổng thể, có độ chính xác nhận dạng đã xác lập, bảo mật production hoặc hiệu quả lâm sàng. [C01–C55]

| Năng lực và phạm vi phân loại | Trạng thái duy nhất | Bằng chứng / phần thiếu |
|---|---|---|
| Desktop tabs/micro và đóng worker, smoke offscreen | IMPLEMENTED | C02/C05; phần cứng mocked |
| Nhận dạng identity LBPH trên người thật | PARTIALLY_IMPLEMENTED | C06–C09; thiếu FAR/FRR |
| Biểu cảm ba lớp trên dashboard | PARTIALLY_IMPLEMENTED | C10–C13; thiếu holdout và cầu nối DB web |
| FSM ba bài tập với landmark tổng hợp | PARTIALLY_IMPLEMENTED | C15/C16 chỉ test chuyển state; C17 test một bước marching; chưa trọn chu kỳ/người thật |
| Camera thật→rep đúng form→completed→web | PARTIALLY_IMPLEMENTED | C14/C18/C19; tổng reps vẫn gồm sai form |
| Xác nhận thuốc DB/outbox/dedup | IMPLEMENTED | C20; chỉ tự khai báo |
| Nhắc thuốc liên tục và snooze timed trong dashboard active | PARTIALLY_IMPLEMENTED | C21/C22; thiếu vòng scheduler đầy đủ |
| Recorder/worker/engine file local và lifecycle mock | IMPLEMENTED | C24–C26; thiếu micro vật lý |
| Gemini hiểu text trong luồng production toàn diện | PARTIALLY_IMPLEMENTED | C28–C33; cloud=false, chỉ3 livecases |
| Đồng bộ DB→SSE queue có quyền trong test nội bộ | IMPLEMENTED | C40–C44; không phải Internet nhiều máy |
| Trò chơi và sức khỏe/reporting toàn chuỗi giao diện | PARTIALLY_IMPLEMENTED | C37–C39; game vẫn DB riêng |
| PostgreSQL runtime | PLANNED | C47; manager chỉ sqlite 3 |
| Fall/Vosk/orchestrator voice cũ theo dashboard active | DEPRECATED | C36/C48; source vẫn còn |
| Đường API STT cũ active | REMOVED | C35; còn compatibility tombstones |
| Hiệu quả phục hồi/nhận thức/chẩn đoán lâm sàng | UNKNOWN | C55; không có nghiên cứu chứng minh |

Một capability ở phạm vi rộng có thể chưa hoàn thiện dù các thành phần con đã IMPLEMENTED. Không dùng status của unit test thay status của tính năng trên người thật. Manifest quy định phạm vi cho từng claim.

## Các phát hiện cần công bố trung thực

1. Face confidence và score biểu cảm là điểm heuristic, chưa được calibration; ba lớp biểu cảm hiển thị không tương đương chẩn đoán tâm lý. Check point MLP tồn tại nhưng dữ liệu/split/metrics tái lập không có tại vị trí config. [C08/C10–C12]
2. Camera emotion ghi JSON trong khi web đọc bảng emotion_inferences; trò chơi ghi SQLite riêng. Import/seed không chứng minh luồng live nối hoàn chỉnh. [C13/C39/C41]
3. Completed phục hồi dựa count đạt target, chưa bắt buộc quality_threshold; dashboard đồng bộ cả incorrect_reps. Camera completion tag không là chứng cứ nguồn ảnh tự động được xác thực. [C18/C19]
4. Xác nhận thuốc là self_reported_taken. Snooze state có nhưng đường nhắc lại và gia hạn lịch liên tục còn cần kiểm chứng. Hộp thoại hỗ trợ nói mạnh hơn bằng chứng delivery hiện có. [C20–C22]
5. Auth có password dạng prefix+plaintext, demo bypass và hint; backup/log/SSE token cần được xử lý trước dùng dữ liệu thật. Audit chỉ ghi rủi ro, không sửa ứng dụng. [C45/C46]
6. Gemini đã có SDK/backend và live textsmoke, không còn chỉ là kế hoạch; vẫn cloud=false. Production chỉ cho catalog điều hướng trung tính, các câu sức khỏe không gửi lên free tier. [C28–C33]

## Bằng chứng thực nghiệm hiện có

Ba log pytest Gemini/STT, legacy và real time lần lượt 107, 41, 13 passed; không có kết luận toàn bộ repo pass. STT CPU 12 lượt có p95=6015.95ms trên audio 873–1170 ms, chưa có WER/CER. Policy khi cloud tắt đạt 72/102 acceptance; ba mẫu Gemini thật có latency 1138–1633 ms và schema/intent đúng. Tất cả có giới hạn mẫu, môi trường, mock và tuổi artefact. [C51–C55]

## Cách sử dụng bộ tài liệu

Dùng 01–05 cho thiết kế/nguyên lý, 06 cho kết quả đã đo và thí nghiệm đề xuất, 07 cho lịch sử có chứng cứ, 08 để map cấu trúc KHKT, 09 để ưu tiên phần thiếu. 10 là bản tổng hợp tự chứa; evidence_manifest.json là chỉ mục máy đọc. Chỉ trình bày tính mới ở mức giải pháp tích hợp của dự án, chưa kết luận mới khoa học nếu chưa khảo sát tài liệu đối chứng.

## Bằng chứng truy nguyên

- **C01 — PARTIALLY_IMPLEMENTED**. File: `main.py`; Symbol: `main`; Lines: 52–106. Explanation: Desktop khởi động bằng QApplication, khóa single-instance, dashboard và migration/import dữ liệu. Giới hạn: Có mã nguồn; chưa nghiệm thu toàn bộ trên thiết bị đích.
  - Đối chiếu: `app/dashboard.py` · `DashboardWindow.__init__` · 122–173 (source_code).
- **C02 — IMPLEMENTED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._init_ui`; Lines: 175–528. Explanation: Dashboard mount TodayTodo, camera/phục hồi, trò chơi và thanh micro; smoke offscreen đã kiểm tra lifecycle. Giới hạn: Camera/audio mocked, TTS tắt, SMTP bị chặn; không phải nghiệm thu phần cứng.
  - Đối chiếu: `reports/gemini_intent/dashboard-smoke.txt` · `module` · 1–44 (existing_test_or_runtime_artifact).
- **C05 — IMPLEMENTED**. File: `app/dashboard.py`; Symbol: `DashboardWindow.closeEvent`; Lines: 1107–1118. Explanation: Đóng dashboard dừng timer, voice coordinator/controller và camera. Giới hạn: Smoke lifecycle có camera/micro mocked; worker đang native inference bị terminate sau chờ hữu hạn.
  - Đối chiếu: `reports/gemini_intent/dashboard-smoke.txt` · `module` · 1–44 (existing_test_or_runtime_artifact).
- **C06 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.__init__`; Lines: 40–81. Explanation: Face detection ưu tiên OpenCV DNN, fallback Haar; nhận diện bằng LBPH radius 1/neighbors 8/grid8x8. Giới hạn: Có pipeline; chưa có FAR/FRR trên tập người độc lập; DNN detector không phải model nhận dạng identity.
  - Đối chiếu: `adapters/face_adapter.py` · `FaceAdapter.detect_face` · 107–146 (source_code).
- **C10 — PARTIALLY_IMPLEMENTED**. File: `adapters/emotion_adapter.py`; Symbol: `EmotionAdapter.process_frame`; Lines: 213–325. Explanation: Biểu cảm dashboard có3 lớp Neutral/Happy/Sad, landmark heuristic và ensemble 75%heuristic+25%MLP khi có model. Giới hạn: Không chẩn đoán tâm lý; chưa có accuracy/macro-F1 holdout hợp lệ cho ensemble 3 lớp.
  - Đối chiếu: `adapters/emotion_adapter.py` · `EmotionAdapter._compute_facs_probabilities` · 146–211 (source_code).
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
- **C28 — PARTIALLY_IMPLEMENTED**. File: `services/transcript_intent/service.py`; Symbol: `GeminiIntentService`; Lines: 12–100. Explanation: Lớp hiểu text Gemini đã có code/backend/client/coordinator, nhưng cloud mặc định false và full acceptance chưa nghiệm thu. Giới hạn: 3 synthetic cases SDK thật; chưa 102 acceptance, mic→web, project/quota independent verify hoặc newest key smoke.
  - Đối chiếu: `reports/gemini_intent/limited-live-benchmark.json` · `module` · 1–60 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/config.py` · `BackendConfig` · 7–42 (source_code).
- **C39 — PARTIALLY_IMPLEMENTED**. File: `app/cognitive_games_widget.py`; Symbol: `CognitiveGamesWidget.__init__`; Lines: 54–80. Explanation: Trò chơi lật cặp/nhớ trình tự dùng rules seededrandom, service/repository; desktop ghi SQLite riêng. Giới hạn: Import sang unified là bước import, chưa thấy live outbox từ gameplay; không có chứng cứ cải thiện nhận thức lâm sàng.
  - Đối chiếu: `modules/cognitive_games/services/game_engine.py` · `GameEngine` · 14–143 (source_code).
  - Đối chiếu: `database/importer.py` · `DataImporter._import_cognitive_games` · 472–541 (source_code).
- **C45 — PARTIALLY_IMPLEMENTED**. File: `web/auth.py`; Symbol: `AuthService.authenticate_credentials`; Lines: 67–200. Explanation: Auth còn lưu password dạng prefix+plaintext, bypass kiểudemo và hint lộ mật khẩu khi sai. Giới hạn: Rủi ro nghiêm trọng nhìn thấy từ code; không kiểm tra khai thác, không sao chép giá trị mật khẩu vào báo cáo.
  - Đối chiếu: `web/auth.py` · `AuthService.register_caregiver` · 207–335 (source_code).
- **C46 — PARTIALLY_IMPLEMENTED**. File: `web/server.py`; Symbol: `HealthcareHttpHandler.log_message`; Lines: 39–40. Explanation: SSE dùng token query và server log message không redactURL; backup là dump SQL plaintext. Giới hạn: Chưa xác minh log vận hành có token thật; mã cho phép nguy cơ. Không thấy retention/encryption tổng thể đã nghiệm thu.
  - Đối chiếu: `web/server.py` · `HealthcareHttpHandler._handle_sse_stream` · 135–183 (source_code).
  - Đối chiếu: `database/backup_restore.py` · `BackupRestoreService.create_sql_dump` · 21–53 (source_code).
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

Public quick-accounts còn trả password. Endpoint rehab-event chưa kiểm tra ownership của session so với patient URL; nguồn camera được gán metadata chứ không xác thực. Đây là phát hiện source, không là kết quả thử khai thác. [C56/C58]

## Bằng chứng truy nguyên

- **C56 — PARTIALLY_IMPLEMENTED**. File: `web/api_router.py`; Symbol: `ApiRouter._get_quick_accounts`; Lines: 298–371. Explanation: Route public quick-accounts trả password đã bóc prefix/plaintext cùng thông tin tài khoản. Giới hạn: Phát hiện source, không gọi route hay trích dữ liệu thật. Rủi ro privacy/auth production cần ưu tiên xử lý.
  - Đối chiếu: `web/api_router.py` · `ApiRouter.handle_request` · 65–258 (source_code).
- **C58 — PARTIALLY_IMPLEMENTED**. File: `web/api_router.py`; Symbol: `ApiRouter._handle_rehab_event`; Lines: 1128–1224. Explanation: Rehab-event API nhận quyền view, tăng count từ body; chưa so session.patient_id với patient URL hay xác thực nguồn camera. Giới hạn: Rủi ro theo source, chưa gọi endpoint/thử khai thác. Không dùng tag camera_ai như at test at io n; cần auth/write/ownership tests.
  - Đối chiếu: `web/api_router.py` · `ApiRouter.handle_request` · 65–258 (source_code).

## Quy ước trạng thái và độ tin cậy

| Trạng thái | Nghĩa và điều kiện |
|---|---|
| IMPLEMENTED | Có code và test/runtime thành công liên quan trong phạm vi ghi rõ; không tự suy ra E2E hoặc tính chính xác y khoa |
| PARTIALLY_IMPLEMENTED | Có implementation nhưng workflow hoặc nghiệm thu còn thiếu |
| PLANNED | Có định hướng/tài liệu, chưa thấy runtime làm việc tương ứng |
| DEPRECATED | Code giữ lại nhưng không thuộc tuyến active được kiểm toán |
| REMOVED | Có record/tombstone/removal evidence; phải ghi rõ phần nào bị gỡ |
| UNKNOWN | Không đủ bằng chứng để xác định hoặc kết luận định lượng |

Confidence HIGH/MEDIUM là độ tin cậy của kết luận kiểm toán dựa nguồn, **không phải độ chính xác model**. Mọi status ở manifest là cho câu claim cụ thể. Source-only không tự thành IMPLEMENTED. Kết quả log được kiểm tra tồn tại/nội dung, không chạy lại. “NOT VERIFIED” là chú thích giới hạn, không thay status enum.

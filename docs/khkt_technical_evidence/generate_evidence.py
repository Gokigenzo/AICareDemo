"""Generate audit documentation using stdlib only; never import the application."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CLAIMS = []
DOCS = {}


def ref(path, symbol='module'):
    text = (ROOT / path).read_text(encoding='utf-8')
    if symbol == 'module':
        span = [1, len(text.splitlines())]
    else:
        tree = ast.parse(text)
        found = {}
        def walk(node, prefix=''):
            for item in ast.iter_child_nodes(node):
                if isinstance(item, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    name = prefix + item.name
                    found[name] = [item.lineno, item.end_lineno]
                    walk(item, name + '.')
                else:
                    walk(item, prefix)
        walk(tree)
        span = found[symbol]
    return dict(source_path=path, symbol=symbol, line_range=span)


def claim(cid, text, path, symbol='module', status='PARTIALLY_IMPLEMENTED', limit='', tests=(), extra=()):
    evidence = [dict(**ref(p), evidence_type='existing_test_or_runtime_artifact') for p in tests]
    evidence += [dict(**ref(*item), evidence_type='source_code') for item in extra]
    CLAIMS.append(dict(claim_id=cid, claim=text, evidence_type='source_code' if path.endswith('.py') else 'repository_artifact',
                       **ref(path, symbol), verification_method='Đọc tĩnh mã/artefact có sẵn; không chạy lại ứng dụng trong lượt audit.',
                       implementation_status=status, confidence='HIGH' if tests or status in ('DEPRECATED','REMOVED') else 'MEDIUM',
                       limitations=limit or 'Có mã nguồn; chưa nghiệm thu toàn bộ trên thiết bị đích.', additional_evidence=evidence))


claim('C01','Desktop khởi động bằng QApplication, khóa single-instance, dashboard và migration/import dữ liệu.', 'main.py','main',extra=(('app/dashboard.py','DashboardWindow.__init__'),))
claim('C02','Dashboard mount TodayTodo, camera/phục hồi, trò chơi và thanh micro; smoke offscreen đã kiểm tra lifecycle.', 'app/dashboard.py','DashboardWindow._init_ui',status='IMPLEMENTED',tests=('reports/gemini_intent/dashboard-smoke.txt',),limit='Camera/audio mocked, TTS tắt, SMTP bị chặn; không phải nghiệm thu phần cứng.')
claim('C03','CameraManager sở hữu luồng QThread và callback xử lý ảnh, có ảnh mô phỏng khi không đọc được camera.', 'core/camera_manager.py','CameraManager.run',extra=(('app/dashboard.py','DashboardWindow._process_video_frame'),),limit='Camera mất có thể tiếp tục ảnh mô phỏng; phải kiểm chứng không ghi completed sai khi mất phần cứng.')
claim('C04','Nhận diện và chọn patient đồng bộ binding các widget; voice invalidates context khi đổi patient/tab/source.', 'app/dashboard.py','DashboardWindow._do_update_dashboard_ui',extra=(('app/dashboard.py','DashboardWindow._resolve_patient_id'),('services/local_voice/dispatcher.py','CommandDispatcher.snapshot')),limit='Unknown-face không xóa current_patient_id; voice có guard riêng, hành động tay cần kiểm tra đổi/người lạ.')
claim('C05','Đóng dashboard dừng timer, voice coordinator/controller và camera.', 'app/dashboard.py','DashboardWindow.closeEvent',status='IMPLEMENTED',tests=('reports/gemini_intent/dashboard-smoke.txt',),limit='Smoke lifecycle có camera/micro mocked; worker đang native inference bị terminate sau chờ hữu hạn.')
claim('C06','Face detection ưu tiên OpenCV DNN, fallback Haar; nhận diện bằng LBPH radius1/neighbors8/grid8x8.', 'adapters/face_adapter.py','FaceAdapter.__init__',extra=(('adapters/face_adapter.py','FaceAdapter.detect_face'),),limit='Có pipeline; chưa có FAR/FRR trên tập người độc lập; DNN detector không phải model nhận dạng identity.')
claim('C07','ROI khuôn mặt grayscale, CLAHE, bilateral và resize200x200; augmentation flip, sáng/tối, xoay±4°.', 'adapters/face_adapter.py','FaceAdapter.extract_face_roi',extra=(('adapters/face_adapter.py','FaceAdapter.train_recognizer'),),limit='Không có lớp background thực tế dù docstring nhắc; augmentation không tăng số người độc lập.')
claim('C08','LBPH distance<58 tạo raw match; history15 và TTL2 giây làm mượt; confidence UI là heuristic.', 'adapters/face_adapter.py','FaceAdapter.recognize_face',limit='Distance và confidence không phải xác suất đúng hay độ chính xác đã đo; TTL có thể giữ danh tính cũ.')
claim('C09','Đăng ký lưu crop và hồ sơ JSON, sync sang unified DB và retrain LBPH.', 'adapters/face_adapter.py','FaceAdapter.register_patient',extra=(('services/patient_sync_service.py','sync_single_patient'),),limit='Test registration tồn tại nhưng một số dùng đường dữ liệu mặc định; không chạy trong audit để tránh sửa hồ sơ.')
claim('C10','Biểu cảm dashboard có3 lớp Neutral/Happy/Sad, landmark heuristic và ensemble75%heuristic+25%MLP khi có model.', 'adapters/emotion_adapter.py','EmotionAdapter.process_frame',extra=(('adapters/emotion_adapter.py','EmotionAdapter._compute_facs_probabilities'),),limit='Không chẩn đoán tâm lý; chưa có accuracy/macro-F1 holdout hợp lệ cho ensemble3 lớp.')
claim('C11','MLP độc lập nhận63 tọa độ landmark, Linear63→128→64→5, ReLU và dropout0.25.', 'modules/emotion/src/model.py','ExpressionNet',extra=(('modules/emotion/utils/preprocess.py','module'),('modules/emotion/src/config.py','module')),limit='Checkpoint tồn tại không chứng minh dữ liệu/huấn luyện; dashboard chỉ lấy3 logits đầu và softmax lại.')
claim('C12','Training biểu cảm có split theo session, baseline logistic regression và evaluator classification metrics.', 'modules/emotion/src/data.py',extra=(('modules/emotion/src/train.py','module'),('modules/emotion/src/evaluate.py','module'),('modules/emotion/src/baseline.py','module')),limit='Không tìm thấy CSV/splits/results phục vụ tái lập ở vị trí config; số người/dataset/provenance UNKNOWN.')
claim('C13','Biểu cảm camera ghi JSON/state, web đọc emotion_inferences; chưa thấy writer unified DB trong đường camera.', 'adapters/emotion_adapter.py','EmotionAdapter._persist_result',extra=(('web/api_router.py','ApiRouter._get_mood'),),limit='Schema và seed emotion_inferences không chứng minh camera→DB→web; tìm kiếm call sites tĩnh chưa thấy cầu nối.')
claim('C14','Phục hồi dùng MediaPipe Pose/Tasks lite và góc2D từ tọa độ landmark chuẩn hóa.', 'modules/rehabilitation/rehab_engine.py','calculate_angle',extra=(('modules/rehabilitation/rehab_engine.py','RehabilitationEngine._init_pose'),),limit='Không dùng3D chuẩn lâm sàng; x/y chuẩn hóa chưa sửa tỷ lệ khung hình; chưa có sai số góc với thước chuẩn.')
claim('C15','FSM nâng tay đếm khi nâng rồi hạ; ngưỡng60/142/130/50°, chấm lỗi khuỷu/đối xứng/hold.', 'modules/rehabilitation/rehab_engine.py','ArmRaiseTracker.process',status='IMPLEMENTED',tests=('reports/local_stt/rehab-regression.txt',),limit='Test landmark tổng hợp; không chứng minh count thực tế. Penalty một số lỗi tăng theo frame, ảnh hưởng FPS.')
claim('C16','FSM đứng-ngồi dùng góc gối155/140/118/125° và dấu đã chạm đáy trước khi đếm.', 'modules/rehabilitation/rehab_engine.py','SitToStandTracker.process',status='IMPLEMENTED',tests=('reports/local_stt/rehab-regression.txt',),limit='Test tổng hợp, thiếu góc camera/occlusion thực; ankle thiếu dùng surrogate có thể ảnh hưởng góc.')
claim('C17','Đi bộ tại chỗ đếm bước trái/phải xen kẽ khi chênh tọa độ gối vượt±0.065; reset stance ở0.035.', 'modules/rehabilitation/rehab_engine.py','MarchingTracker.process',status='IMPLEMENTED',tests=('reports/local_stt/rehab-regression.txt',),limit='Ngưỡng normalized image units; count ngay khi nhấc, không đo quãng đường hoặc năng lực đi lại.')
claim('C18','RehabSessionAdapter khóa target snapshot, ghi event idempotent/outbox và completed khi count>=target.', 'modules/rehabilitation/rehab_session_adapter.py','RehabSessionAdapter.record_verified_rep',status='IMPLEMENTED',tests=('reports/gemini_intent/realtime-regression.txt',),extra=(('modules/rehabilitation/rehab_session_adapter.py','RehabSessionAdapter.get_or_create_daily_session'),),limit='Test DB với rep giả; tag camera là metadata từ caller, không tự xác thực frame/score; race đa writer chưa chứng minh.')
claim('C19','Dashboard ghi DB theo tổng reps, gồm incorrect_reps; score<=0 được thay90 và quality_threshold chưa là điều kiện completed.', 'app/dashboard.py','DashboardWindow._do_update_dashboard_ui',limit='UI khen hoàn thành không chứng minh mọi lần đúng form. Chưa thấy chặn hardware_valid tại điểm record_verified_rep.')
claim('C20','Thuốc hiện hiển thị và thao tác qua TodayTodo/ElderSyncClient cùng unified DB.', 'app/today_todo_widget.py','TodayTodoWidget._on_confirm_taken',status='IMPLEMENTED',tests=('reports/gemini_intent/intent-and-stt-tests.txt','reports/gemini_intent/realtime-regression.txt'),extra=(('services/elder_sync_client.py','ElderSyncClient.flush_offline_queue'),),limit='Tự khai báo self_reported_taken; không chứng minh đã nuốt thuốc. Test không phải xác nhận từ người dùng thật.')
claim('C21','Prescription create sinh occurrences hôm nay và3 ngày tiếp theo; relay chuyển quá hạn PENDING/REMINDING.', 'web/api_router.py','ApiRouter._create_prescription',extra=(('services/outbox_relay.py','OutboxRelayService.scan_overdue_tasks'),),limit='Chưa thấy tác vụ gia hạn occurrences dài ngày ở active dashboard/backend; UTC+7 hardcode ở create; SNOOZED không thuộc scan quá hạn.')
claim('C22','Snooze đổi state sangSNOOZED, help tạo cảnh báo; chưa xác minh nhắc lại timed trong active dashboard.', 'services/elder_sync_client.py','ElderSyncClient.flush_offline_queue',extra=(('app/today_todo_widget.py','TodayTodoWidget._on_help_requested'),),limit='Hộp thoại help tuyên bố gửi/nhận và dùng liên hệ hardcode; DB alert không chứng minh SMTP delivery hoặc người nhận xử lý.')
claim('C23','MedicationPanel/MedicationService và scheduler standalone còn code/test nhưng không mount trong dashboard hiện tại.', 'app/dashboard.py','DashboardWindow._init_ui',status='DEPRECATED',tests=('reports/medication_migration/medication_tests.txt',),extra=(('services/medication_service.py','module'),('modules/medication_adherence/services/scheduler.py','module')),limit='Deprecated theo active dashboard, standalone vẫn có thể chạy; kết quả scheduler cũ không chứng minh luồng thuốc unified.')
claim('C24','Recorder explicit sounddevice InputStream, mono/resample16kHz, stop/cancel/bound duration; không nghe nền.', 'services/local_voice/recorder.py','AudioRecorder',status='IMPLEMENTED',tests=('reports/gemini_intent/intent-and-stt-tests.txt',),limit='Stream48k→16k đã test bằng mock; physical mic chưa kiểm chứng trong artefact hiện có.')
claim('C25','Engine faster-whisper small multilingual localfilesonly,CPU/int8,beam1,languagevi,VAD và consume segments ngoàiUI.', 'services/local_voice/engine.py','LocalSttEngine',status='IMPLEMENTED',tests=('reports/local_stt/cpu-final.json','reports/local_stt/clean-smoke.txt'),extra=(('services/local_voice/config.py','VoiceConfig'),('services/local_voice/worker.py','run_worker')),limit='Có inference file local; audio chuẩn/consent chưa xác minh; không có WER/CER hợp lệ; GPU chưa chạy thành công.')
claim('C26','Controller spawn một persistent worker, token/context bỏ response cũ; shutdown chờ rồi terminate/kill hữu hạn.', 'services/local_voice/controller.py','VoiceSessionController',status='IMPLEMENTED',tests=('reports/gemini_intent/intent-and-stt-tests.txt','reports/gemini_intent/dashboard-smoke.txt'),limit='Native inference không bị ngắt mềm ngay khi cancel; chỉ bỏ kết quả/chờ acknowledgement; test không có mic vật lý.')
claim('C27','Dispatcher sáu intent dùng handler nút bấm, xác nhận dose defaultNo và kiểm tra lại context/command id.', 'services/local_voice/dispatcher.py','CommandDispatcher.dispatch',status='IMPLEMENTED',tests=('reports/gemini_intent/intent-and-stt-tests.txt',),extra=(('services/transcript_intent/registry.py','module'),),limit='Không có intent hoàn thành phục hồi; không dùng transcript tự sửa DB; sampletext/mock audio chưa là E2E thật.')
claim('C28','Lớp hiểu text Gemini đã có code/backend/client/coordinator, nhưng cloud mặc địnhfalse và full acceptance chưa nghiệm thu.', 'services/transcript_intent/service.py','GeminiIntentService',tests=('reports/gemini_intent/limited-live-benchmark.json',),extra=(('services/transcript_intent/config.py','BackendConfig'),),limit='3 synthetic cases SDK thật; chưa102 acceptance, mic→web, project/quota independent verify hoặc newestkey smoke.')
claim('C29','Privacy gate production chỉ20 câu điều hướng trung tính; nội dung thuốc/phục hồi xử lýlocal, unknown không đoán.', 'services/transcript_intent/policy.py',status='IMPLEMENTED',tests=('reports/gemini_intent/intent-and-stt-tests.txt',),extra=(('services/transcript_intent/prompts.py','module'),),limit='Đảm bảo theo catalog đã review, không phải bộ khử nhạy cảm tổng quát; không cho tùy ý text sức khỏe vào free API.')
claim('C30','SchemaPydantic enum/extraforbid và semantic validator giới hạnintent/context/evidence/negation; không tin confidence.', 'services/transcript_intent/schema.py',status='IMPLEMENTED',tests=('reports/gemini_intent/intent-and-stt-tests.txt',),extra=(('services/transcript_intent/policy.py','validate_proposal'),),limit='Đúng trên các mock/tập tổng hợp đã kiểm tra; chưa đo unsafe routing quy mô người dùng thực.')
claim('C31','OfficialSDK textgenerateContent, JSONschema, tools=[] và functioncallingdisabled; total≤8s,transport≥10s.', 'services/transcript_intent/gemini_adapter.py','GeminiIntentAdapter.generate',status='IMPLEMENTED',tests=('reports/gemini_intent/limited-live-benchmark.json','reports/gemini_intent/intent-and-stt-tests.txt'),limit='Không cấp DB/SQL/email/grounding. Hạn total là clientdeadline; transport cancel/release thiết bị thật cần stress.')
claim('C32','Quota file lock, reservation1200tokens, caps1RPM/2400TPM/10RPDreserve2, retrybounded và circuit breaker.', 'services/transcript_intent/budget.py','ProjectBudget',status='IMPLEMENTED',tests=('reports/gemini_intent/intent-and-stt-tests.txt',),extra=(('services/transcript_intent/service.py','GeminiIntentService._cloud_locked'),),limit='Caps local, không phải quota provider được xác minh; filesystemshared không phải limiter nhiều host.')
claim('C33','HTTP text endpoint kiểm tra session/auth/patient/context version trước và sau classification.', 'services/transcript_intent/backend.py','TranscriptIntentEndpoint.handle',status='IMPLEMENTED',tests=('reports/gemini_intent/http-smoke.json','reports/gemini_intent/intent-and-stt-tests.txt'),limit='LoopbackHTTP+Qt+DBgiả, Geminimock; không có mic/remoteprovider trong HTTPsmoke.')
claim('C34','TTS được suspend khi ghi; nhạc pause; childpyttsx3 local giữ entrypoint frozen riêng.', 'services/local_voice/controller.py','VoiceSessionController.start',status='IMPLEMENTED',tests=('reports/gemini_intent/intent-and-stt-tests.txt',),extra=(('services/local_voice/tts_runtime.py','speak'),('app/local_voice_widget.py','module')),limit='Phối hợp đã testcode/mocks; chưa nghe playbackloa thật; nhắc thuốc/coach active chưa nối toàn bộ TTS callbacks.')
claim('C35','API STT cũ không còn active: router410 và factory compatibility disabled; không restore orchestrator cũ.', 'web/api_router.py','ApiRouter.handle_request',status='REMOVED',extra=(('services/voice_ai/asr/factory.py','module'),('archive/voice/README.md','module')),limit='REMOVED chỉ đường API STT active; file/provider/testlegacy vẫn tồn tại, không nói mọi sourceSTT đã xóa.')
claim('C36','Các semantic/orchestrator/voicewidget cũ và Voskarchive không là tuyến nhận giọng active.', 'services/voice_ai/orchestrator/router.py',status='DEPRECATED',extra=(('app/voice_button_widget.py','module'),('app/local_voice_widget.py','module')),limit='TTS coordinator cũ còn được reuse; không quy toàn bộ services/voice_ai thành deadcode.')
claim('C37','Theo dõi sức khỏe web ghi measurementgroups/observations, requestcompleted và outbox cùngtransaction.', 'web/api_router.py','ApiRouter._add_observation',status='IMPLEMENTED',tests=('reports/gemini_intent/realtime-regression.txt',),limit='Nhập tay từ người chăm sóc; không có đường sensor IoT đã nghiệm thu; unit/range validation cần đối chiếu backend/UI.')
claim('C38','Web có recommendation/reports/review/emergencycontacts và các màn caregiver/clinician/admin.', 'web/api_router.py','ApiRouter.handle_request',extra=(('web/templates/portal_caregiver.html','module'),('web/templates/portal_clinician.html','module'),('web/templates/portal_admin.html','module')),limit='Sự có mặt endpoint/UI không chứng minh tất cả chức năng được browser nghiệm thu; emergencycontacts không tự gọi điện.')
claim('C39','Trò chơi lật cặp/nhớ trình tự dùng rules seededrandom, service/repository; desktop ghi SQLite riêng.', 'app/cognitive_games_widget.py','CognitiveGamesWidget.__init__',extra=(('modules/cognitive_games/services/game_engine.py','GameEngine'),('database/importer.py','DataImporter._import_cognitive_games')),limit='Import sang unified là bước import, chưa thấy live outbox từ gameplay; không có chứng cứ cải thiện nhận thức lâm sàng.')
claim('C40','Database runtime làSQLite/WAL/foreignkeys/busytimeout; không có PostgreSQL driver runtime trong manager.', 'database/connection.py','UnifiedDatabaseManager',status='IMPLEMENTED',tests=('reports/gemini_intent/realtime-regression.txt',),limit='Các comment PostgreSQL/ANSI/3NF là định hướng, không là chứng minh tương thích hoặc chuẩn hóa hình thức.')
claim('C41','4 migration định nghĩa schema, Migrator áp dụng theo version; importer gộp DBstandalone/JSON.', 'database/migrator.py',status='IMPLEMENTED',tests=('reports/gemini_intent/realtime-regression.txt',),extra=(('database/importer.py','DataImporter.import_all'),),limit='Không mở DBproduction trong audit; seed không phải dữ liệu camera/micro/sensor thực; migrationatomicity chưa faultinject.')
claim('C42','Outbox relay poll0.5s gửi tín hiệuSSE/auth, sideeffectemail và markprocessed; UIweb refetch dữ liệu.', 'services/outbox_relay.py','OutboxRelayService.process_pending_events',status='IMPLEMENTED',tests=('reports/gemini_intent/realtime-regression.txt',),extra=(('web/sse_hub.py','SSEHub.dispatch_outbox_event'),),limit='Test in-processqueue; không phải3 thiết bị qua Internet; processed≠client đã render hoặc SMTP đã tới mailbox.')
claim('C43','ElderSyncClient truy cậpSQLite trực tiếp; offline JSONqueue perpatient và syncinboxdedup; voice không replay.', 'services/elder_sync_client.py','ElderSyncClient.enqueue_event',status='IMPLEMENTED',tests=('reports/gemini_intent/intent-and-stt-tests.txt','reports/gemini_intent/realtime-regression.txt'),extra=(('services/elder_sync_client.py','ElderSyncClient.flush_offline_queue'),),limit='is_online là flag, không đo mạng; không đồng bộ SQLite độc lập giữa nhiều máy.')
claim('C44','Auth phân quyền theo usersactive/patientactive/careteam/consent và SSE recheck quyền; session RAM7 ngày.', 'web/auth.py','AuthService.check_patient_access',status='IMPLEMENTED',tests=('reports/gemini_intent/realtime-regression.txt','reports/gemini_intent/http-smoke.json'),extra=(('web/auth.py','AuthService.create_session'),),limit='Có các guard đã test; không suy ra hệ thống bảo mật production. Restart mất token/session.')
claim('C45','Auth còn lưu password dạngprefix+plaintext, bypass kiểudemo và hint lộ mật khẩu khi sai.', 'web/auth.py','AuthService.authenticate_credentials',extra=(('web/auth.py','AuthService.register_caregiver'),),limit='Rủi ro nghiêm trọng nhìn thấy từ code; không kiểm tra khai thác, không sao chép giá trị mật khẩu vào báo cáo.')
claim('C46','SSE dùng tokenquery và server logmessage không redactURL; backup là dumpSQL plaintext.', 'web/server.py','HealthcareHttpHandler.log_message',extra=(('web/server.py','HealthcareHttpHandler._handle_sse_stream'),('database/backup_restore.py','BackupRestoreService.create_sql_dump')),limit='Chưa xác minh log vận hành có tokenthật; mã cho phép nguy cơ. Không thấy retention/encryption tổng thể đã nghiệm thu.')
claim('C47','PostgreSQL là định hướng trong tài liệu/schema comment, chưa là runtime backend.', 'database/migrations/001_initial_schema.sql',status='PLANNED',extra=(('database/connection.py','UnifiedDatabaseManager'),),limit='Không suy đoán đã deployPostgres/Supabase/Redis vì tên mục tiêu; runtime đã kiểm tra source chỉsqlite3.')
claim('C48','Fall/HFD/ONNX/video còn retainedsource/artefacts nhưng không trong camera callbacks dashboard hiện tại.', 'app/dashboard.py','DashboardWindow._process_video_frame',status='DEPRECATED',extra=(('core/fall_pipeline.py','module'),('modules/fall/hfd_classifier.py','module')),limit='Deprecated theo dashboardactive; toolvideo riêng vẫn có. Không dùng metricfall cũ thay metricrehab hiện tại.')
claim('C49','Runtime requirements chính+lockLinux/STT/backend SDK; đã có log cài sạchLinux và pipcheck.', 'requirements.txt',status='IMPLEMENTED',tests=('reports/gemini_intent/clean-pip-check.txt','reports/gemini_intent/clean-full-install.txt'),extra=(('requirements-linux.lock','module'),('requirements-gemini-backend.txt','module')),limit='Windows constraints/build/installer/modelDLL mới chưa nghiệm thu; pinLinux không chứng minhWindowswheel.')
claim('C50','Spec excludes GeminiSDK/provider/backend env khỏi EXE; chưa buildbinary kiểm chứng ranh giới này.', 'AI_Rehab_Safety_Assistant.spec',limit='Reviewsource recipe thôi, không chứng minhbinarykhôngsecret. Không đọc .envprivate hoặc tải/cài package trong audit.')
claim('C51','STTCPU12 lượt: cold727ms,p50=4642ms,p95=6015.95ms,RSS1830600704bytes; camera/GPU thất bại.', 'reports/local_stt/cpu-final.json',status='IMPLEMENTED',tests=('reports/local_stt/cpu-final.json','reports/local_stt/gpu-camera.json'),limit='Đo scriptengine/audio873–1170ms, không phải fullapp/micđồngthời, thiếugroundtruth; p95 này là số cũ, chưa chạy lại.')
claim('C52','Offlinepolicy150cases:104correct;acceptance72/102;0 unexpected sensitive routes trong tập tổng hợp.', 'reports/gemini_intent/offline-benchmark.json',status='IMPLEMENTED',tests=('reports/gemini_intent/offline-benchmark.json',),limit='Cloudtắt;69.33%toàn tập,70.59%acceptance là policycoverage không là Geminiaccuracy hoặc STTWER.')
claim('C53','3syntheticAPIcases đạt schema/intent,latency1633/1138/1562ms; fullacceptance=false/quota_verified=false.', 'reports/gemini_intent/limited-live-benchmark.json',status='IMPLEMENTED',tests=('reports/gemini_intent/limited-live-benchmark.json',),limit='n3 và một smoke1746ms riêng; không đủ chứng minh accuracy95% hay latencyổnđịnh. Audit không gọi API.')
claim('C54','3 nhóm testlog hiện có107+41+13passed; không có bằng chứng toànrepo pass và không chạy lại trongaudit.', 'reports/gemini_intent/REPORT.md',status='IMPLEMENTED',tests=('reports/gemini_intent/intent-and-stt-tests.txt','reports/gemini_intent/legacy-regression-isolated.txt','reports/gemini_intent/realtime-regression.txt'),limit='Tổng161 thuộc3 nhóm được ghi;85/17/6/16 ở reportkhác có overlap. Một số baseline nativeaudio timeout/DBfail còn ghi.')
claim('C55','FaceFAR/FRR,emotionholdoutF1,rehabclinicalangleerror,STTWER và nghiệmthu mic/camera/multihost chưa có bằngchứng phùhợp.', 'reports/local_stt/REPORT.md',status='UNKNOWN',extra=(('reports/gemini_intent/REPORT.md','module'),),limit='Không có số đo hợp lệ trong các artefact đã đối chiếu; không khẳng định không tồn tại ngoài repo.')
claim('C56','Route public quick-accounts trả password đã bóc prefix/plaintext cùng thông tin tài khoản.', 'web/api_router.py','ApiRouter._get_quick_accounts',extra=(('web/api_router.py','ApiRouter.handle_request'),),limit='Phát hiện source, không gọi route hay trích dữ liệu thật. Rủi ro privacy/auth production cần ưu tiên xử lý.')
claim('C57','Web chart có dải tham chiếu sức khỏe hardcode; chưa có chứng cứ validation/personalization lâm sàng.', 'web/templates/portal_clinician.html',limit='Chỉ mô tả source UI; không công nhận các dải này là khuyến nghị y tế đúng cho mọi người.')
claim('C58','Rehab-event API nhận quyền view, tăng count từ body; chưa so session.patient_id với patient URL hay xác thực nguồn camera.', 'web/api_router.py','ApiRouter._handle_rehab_event',extra=(('web/api_router.py','ApiRouter.handle_request'),),limit='Rủi ro theo source, chưa gọi endpoint/thử khai thác. Không dùng tag camera_ai như attestation; cần auth/write/ownership tests.')

# Inspect actual assertions, not just test names, before assigning operational scope.
TEST_REFS={
    'C15':[('tests/test_rehab_assistant.py','TestRehabilitationEngine.test_arm_raise_state_machine')],
    'C16':[('tests/test_rehab_assistant.py','TestRehabilitationEngine.test_sit_to_stand_state_machine')],
    'C17':[('tests/test_rehab_assistant.py','TestRehabilitationEngine.test_marching_state_machine')],
    'C18':[('tests/test_realtime_sync_12_scenarios.py','TestRealtimeSync12Scenarios.test_scenario_03_camera_target_10_reps_auto_completion')],
    'C24':[('tests/voice_ai/test_local_voice.py','test_recorder_hardware_sample_rate_resampling_bounded_and_close')],
    'C26':[('tests/voice_ai/test_local_voice.py','test_cancel_and_context_change_discard_late_results_and_shutdown')],
    'C27':[('tests/transcript_intent/test_lifecycle_integration.py','test_proposed_medication_confirmation_same_db_and_web')],
    'C29':[('tests/transcript_intent/test_contract_policy.py','test_privacy_default_deny_not_id_redaction')],
    'C30':[('tests/transcript_intent/test_contract_policy.py','test_schema_forbids_policy_confidence_tools_and_custom_snooze')],
    'C31':[('tests/transcript_intent/test_lifecycle_integration.py','test_sdk_contract_and_no_implicit_tools')],
    'C32':[('tests/transcript_intent/test_contract_policy.py','test_quota_shared_across_instances_and_circuit')],
    'C33':[('tests/transcript_intent/test_lifecycle_integration.py','test_backend_rechecks_auth_and_version')],
    'C34':[('tests/voice_ai/test_local_voice.py','test_tts_cannot_restart_during_capture')],
    'C35':[('tests/voice_ai/test_local_voice.py','test_legacy_web_voice_disabled_even_when_local_flag_enabled')],
    'C43':[('tests/voice_ai/test_local_voice.py','test_voice_version_conflict_offline_and_restart_never_replay')],
    'C44':[('tests/transcript_intent/test_lifecycle_integration.py','test_real_auth_relationship_revocation')],
}
for c in CLAIMS:
    for path,symbol in TEST_REFS.get(c['claim_id'],[]):
        c['additional_evidence'].append(dict(**ref(path,symbol),evidence_type='test_source'))
    if c['claim_id'] in ('C15','C16'):
        c['implementation_status']='PARTIALLY_IMPLEMENTED'
        c['limitations']+=' Test hiện có chỉ đưa một trạng thái landmark và assertstage; chưa test toàn chu kỳ rồi đếm.'


def evidence(ids):
    byid = {c['claim_id']: c for c in CLAIMS}
    s = '\n## Bằng chứng truy nguyên\n\n'
    for cid in ids:
        c = byid[cid]
        a,b=c['line_range']
        s += f"- **{cid} — {c['implementation_status']}**. File: `{c['source_path']}`; Symbol: `{c['symbol']}`; Lines: {a}–{b}. Explanation: {c['claim']} Giới hạn: {c['limitations']}\n"
        for e in c['additional_evidence']:
            a,b=e['line_range'];s+=f"  - Đối chiếu: `{e['source_path']}` · `{e['symbol']}` · {a}–{b} ({e['evidence_type']}).\n"
    return s


def doc(name, body, ids):
    DOCS[name] = body.strip() + '\n' + evidence(ids)


doc('00_EXECUTIVE_SUMMARY.md', r'''
# Tổng quan kiểm toán kỹ thuật phục vụ KHKT

Ngày lập: 09/10/2026. Đối tượng là trạng thái worktree hiện tại, gồm nhiều thay đổi chưa commit; đây không phải bản phát hành được xác nhận. Kiểm toán chỉ đọc mã, cấu hình, migration, test và artefact có sẵn; không mở camera/micro, chạy app, cài dependency, gọi API hay gửi thông báo. Các số đo bên dưới là kết quả lịch sử có đường dẫn truy nguyên, chưa được chạy lại trong lượt này.

## Kết luận về mức sẵn sàng

Repo có nguyên mẫu desktop PyQt5 và web người nhà/bác sĩ/admin, xử lý ảnh cục bộ, STT faster-whisper, intent allowlist và lớp Gemini text có giới hạn. Có bằng chứng kiểm thử cho nhiều thành phần kỹ thuật. Chưa đủ bằng chứng để gọi đây là hệ thống đã nghiệm thu tổng thể, có độ chính xác nhận dạng đã xác lập, bảo mật production hoặc hiệu quả lâm sàng. [C01–C55]

| Năng lực và phạm vi phân loại | Trạng thái duy nhất | Bằng chứng / phần thiếu |
|---|---|---|
| Desktop tabs/micro và đóng worker, smoke offscreen | IMPLEMENTED | C02/C05; phần cứng mocked |
| Nhận dạng identity LBPH trên người thật | PARTIALLY_IMPLEMENTED | C06–C09; thiếu FAR/FRR |
| Biểu cảm ba lớp trên dashboard | PARTIALLY_IMPLEMENTED | C10–C13; thiếu holdout và cầu nối DBweb |
| FSM ba bài tập với landmark tổng hợp | IMPLEMENTED | C15–C17; không phải clinical trial |
| Camera thật→rep đúng form→completed→web | PARTIALLY_IMPLEMENTED | C14/C18/C19; tổng reps vẫn gồm sai form |
| Xác nhận thuốc DB/outbox/dedup | IMPLEMENTED | C20; chỉ tự khai báo |
| Nhắc thuốc liên tục và snooze timed trong dashboard active | PARTIALLY_IMPLEMENTED | C21/C22; thiếu vòng scheduler đầy đủ |
| Recorder/worker/engine file local và lifecycle mock | IMPLEMENTED | C24–C26; thiếu micro vật lý |
| Gemini hiểu text trong luồng production toàn diện | PARTIALLY_IMPLEMENTED | C28–C33; cloudfalse, chỉ3 livecases |
| Đồng bộ DB→SSEqueue có quyền trong test nội bộ | IMPLEMENTED | C40–C44; không phải Internet nhiều máy |
| Trò chơi và sức khỏe/reporting toàn chuỗi giao diện | PARTIALLY_IMPLEMENTED | C37–C39; game vẫn DB riêng |
| PostgreSQL runtime | PLANNED | C47; manager chỉsqlite3 |
| Fall/Vosk/orchestrator voice cũ theo dashboard active | DEPRECATED | C36/C48; source vẫn còn |
| Đường API STT cũ active | REMOVED | C35; còn compatibility tombstones |
| Hiệu quả phục hồi/nhận thức/chẩn đoán lâm sàng | UNKNOWN | C55; không có nghiên cứu chứng minh |

Một capability ở phạm vi rộng có thể chưa hoàn thiện dù các thành phần con đã IMPLEMENTED. Không dùng status của unit test thay status của tính năng trên người thật. Manifest quy định phạm vi cho từng claim.

## Các phát hiện cần công bố trung thực

1. Face confidence và score biểu cảm là điểm heuristic, chưa được calibration; ba lớp biểu cảm hiển thị không tương đương chẩn đoán tâm lý. Checkpoint MLP tồn tại nhưng dữ liệu/split/metrics tái lập không có tại vị trí config. [C08/C10–C12]
2. Camera emotion ghi JSON trong khi web đọc bảng emotion_inferences; trò chơi ghi SQLite riêng. Import/seed không chứng minh luồng live nối hoàn chỉnh. [C13/C39/C41]
3. Completed phục hồi dựa count đạt target, chưa bắt buộc quality_threshold; dashboard đồng bộ cả incorrect_reps. Camera completion tag không là chứng cứ nguồn ảnh tự động được xác thực. [C18/C19]
4. Xác nhận thuốc là self_reported_taken. Snooze state có nhưng đường nhắc lại và gia hạn lịch liên tục còn cần kiểm chứng. Hộp thoại hỗ trợ nói mạnh hơn bằng chứng delivery hiện có. [C20–C22]
5. Auth có password dạng prefix+plaintext, demo bypass và hint; backup/log/SSEtoken cần được xử lý trước dùng dữ liệu thật. Audit chỉ ghi rủi ro, không sửa ứng dụng. [C45/C46]
6. Gemini đã có SDK/backend và live textsmoke, không còn chỉ là kế hoạch; vẫn cloudfalse. Production chỉ cho catalog điều hướng trung tính, các câu sức khỏe không gửi lên free tier. [C28–C33]

## Bằng chứng thực nghiệm hiện có

Ba log pytest Gemini/STT, legacy và realtime lần lượt107,41,13 passed; không có kết luận toàn bộ repo pass. STT CPU12 lượt có p95=6015.95ms trên audio873–1170ms, chưa có WER/CER. Policy khi cloud tắt đạt72/102 acceptance; ba mẫu Gemini thật có latency1138–1633ms và schema/intent đúng. Tất cả có giới hạn mẫu, môi trường, mock và tuổi artefact. [C51–C55]

## Cách sử dụng bộ tài liệu

Dùng 01–05 cho thiết kế/nguyên lý, 06 cho kết quả đã đo và thí nghiệm đề xuất, 07 cho lịch sử có chứng cứ, 08 để map cấu trúc KHKT, 09 để ưu tiên phần thiếu. 10 là bản tổng hợp tự chứa; evidence_manifest.json là chỉ mục máy đọc. Chỉ trình bày tính mới ở mức giải pháp tích hợp của dự án, chưa kết luận mới khoa học nếu chưa khảo sát tài liệu đối chứng.
''', [f'C{i:02}' for i in [1,2,5,6,10,13,18,19,20,21,28,39,45,46,51,52,53,54,55]])

doc('01_CODEBASE_ARCHITECTURE.md', r'''
# Kiến trúc codebase và vòng đời

## Cấu trúc liên quan đã kiểm tra

```text
main.py / config.py                         entrypoint desktop, cấu hình đường dẫn
app/{dashboard,router,state,registration_dialog}.py
app/{today_todo_widget,cognitive_games_widget,local_voice_widget}.py
adapters/{face_adapter,emotion_adapter,rehabilitation_adapter}.py
core/camera_manager.py                      camera thread/callback
services/local_voice/                      recorder, engine, worker, controller, dispatcher
services/transcript_intent/                 enum/schema/policy/context/budget/SDK/backend/client
services/{elder_sync_client,outbox_relay,patient_sync_service}.py
database/{connection,migrator,importer,outbox_helper,backup_restore}.py
database/migrations/001...004*.sql          định nghĩa DB hiện tại
web/{server,api_router,auth,sse_hub}.py
web/templates/{login,register,portal_caregiver,portal_clinician,portal_admin}.html
modules/face/                              detector weights, standalone age/gender
modules/emotion/{src,utils,models,tests}/    training/evaluation biểu cảm
modules/rehabilitation/                     pose, FSM, session adapter
modules/{medication_adherence,health_monitoring,cognitive_games}/
modules/fall/ / core/fall_*.py / archive/    nhánh lịch sử/video tool
tests/{voice_ai,transcript_intent}/ + tests/test_*.py
scripts/ / packaging/ / *.spec / *.bat      chuẩn bị model, smoke, đóng gói
requirements*.txt / requirements*.lock
plan/ / docs/ / reports/                    thiết kế, hướng dẫn, artefact test
```

Cây trên là tập liên quan, không liệt kê hồ sơ cá nhân/audio/video/trọng số chi tiết. Source snapshot ghi các file code/config/dependency hiện hữu; cây không suy ra module nào active. [C01/C02/C06/C28/C40/C48/C49]

## Kiến trúc hệ thống thực tế

```mermaid
flowchart LR
  Elder[Người cao tuổi] --> Desktop[PyQt5 desktop]
  Camera[Camera] --> CamThread[CameraManager QThread]
  CamThread --> Vision[Face - Emotion - Rehab]
  Vision --> Desktop
  Desktop --> Local[Recorder + faster-whisper worker]
  Local --> Rules[Rules + context + dispatcher]
  Rules --> DB[(SQLite unified_care)]
  Desktop --> Games[(SQLite cognitive_games)]
  Vision --> JSON[(JSON results - profile)]
  Desktop -. text đủ điều kiện - cloud opt-in .-> Backend[ThreadingHTTPServer]
  Backend -. catalog neutral .-> Gemini[Gemini Developer API]
  Family[Người nhà - Bác sĩ - Admin] --> Web[HTML CSS JavaScript]
  Web --> Backend
  Backend --> DB
  DB --> Relay[Outbox relay]
  Relay --> SSE[SSE signals có lọc quyền]
  SSE --> Web
  Relay -. có cấu hình .-> SMTP[Email delivery service]
```

DB trực tiếp của desktop và DB backend phải cùng file/host phù hợp cho đường này. Không có cơ chế chứng minh tự đồng bộ nhiều file SQLite trên các thiết bị độc lập. Gemini branch có code nhưng mặc định không bật. Emotion JSON không có cạnh live đến unified DB; game import không là live streaming. [C13/C28/C39–C43]

## Sơ đồ thành phần

```mermaid
flowchart TB
  Win[DashboardWindow] --> Router[DashboardRouter + AppState]
  Win --> Todo[TodayTodoWidget]
  Win --> GameUI[CognitiveGamesWidget]
  Win --> VoiceUI[LocalVoiceWidget]
  Router --> Face[FaceAdapter]
  Router --> Emotion[EmotionAdapter]
  Router --> Rehab[RehabAdapter - RehabilitationEngine]
  Todo --> ElderClient[ElderSyncClient]
  Win --> Session[RehabSessionAdapter]
  VoiceUI --> Controller[VoiceSessionController]
  Controller --> Worker[run_worker - AudioRecorder - LocalSttEngine]
  VoiceUI --> Coordinator[VoiceRequestCoordinator]
  Coordinator --> Client[GeminiIntentClient]
  Coordinator --> Dispatcher[CommandDispatcher]
  Dispatcher --> ElderClient
  Dispatcher --> Win
  Client --> Endpoint[TranscriptIntentEndpoint]
  Endpoint --> Service[GeminiIntentService - ProjectBudget - SDK]
```

Recorder giữ stream; engine giữ WhisperModel; worker tuần tự hóa ghi/inference; controller giữ state/token và polling50ms trên Qt; coordinator dùng background HTTP, timeout/context discard; dispatcher là điểm hành động duy nhất. Model một worker không đồng nghĩa tổng hệ thống chỉ một model: camera còn có face/pose/emotion. [C24–C34]

## Luồng dữ liệu

```mermaid
flowchart LR
  Raw[Frame camera] --> Land[Detector hoặc landmarks]
  Land --> Identity[LBPH identity]
  Identity --> Binding[Patient binding - legacy map]
  Land --> Fsm[FSM reps - quality score]
  Fsm --> Session[rehab_events + rehab_sessions]
  Mic[Micro nhấn tay] --> PCM[Mono float32 - 16kHz]
  PCM --> STT[Local transcript]
  STT --> Policy[Rules - privacy - schema - context]
  Policy --> Dispatch[Handler nút bấm]
  Dispatch --> Dose[dose_occurrences - dose_events]
  Session --> Outbox[outbox_events trong transaction]
  Dose --> Outbox
  Outbox --> Signal[SSE minimal signal]
  Signal --> Fetch[Web GET lại dữ liệu có quyền]
  Land --> Emotion[Emotion smoother]
  Emotion --> Latest[JSON latest - không phải history DB]
```

## Khởi động và shutdown

```mermaid
flowchart TD
  Start[main.py] --> Freeze[freeze_support]
  Freeze --> TTS{--local-tts?}
  TTS -->|Có| Child[pyttsx3 child rồi thoát]
  TTS -->|Không| Imports[Imports Qt - vision - torch - mediapipe]
  Imports --> App[QApplication + single-instance lock]
  App --> Dashboard[DashboardWindow - router - adapters - camera]
  Dashboard --> Widgets[Tabs + micro UI]
  Widgets --> DBSetup[Migrations - importer - profile sync]
  DBSetup --> Loop[show + Qt event loop]
  Loop --> Click[Nhấn micro lần đầu nếu worker chưa có]
  Click --> Spawn[Spawn worker - load model - idle]
  Loop --> Close[closeEvent]
  Close --> Stop[Timers stop - cancel coordinator - shutdown worker - camera stop]
```

Chi tiết: dashboard cũng khởi tạo DB/widgets trước phần setup DB ở main; sơ đồ biểu diễn thứ tự lời gọi chính, không giả định mọi migration chỉ gọi một lần. --test dùng exit cưỡng bức, không chứng minh shutdown bình thường. main còn eagerimport mediapipe/torch; config chỉ giữ native pre-init trên Windows và services exportlazy để backend tránh audio sideeffects. Backend là entrypoint riêng, không tự sinh từ vòng Qt. [C01/C02/C05/C41]

## Luồng tương tác chính

```mermaid
flowchart TD
  Select[Chọn hoặc nhận diện patient] --> Context[Đọc patient - tab - dose/plan version]
  Context --> Mode{Nút tay hay micro?}
  Mode -->|Tay| Button[Handler hiện có]
  Mode -->|Micro| Record[Nhấn ghi - Dừng hoặc Hủy]
  Record --> Transcript[Whisper local ngoài UI]
  Transcript --> Check[Rules + privacy + semantic checks]
  Check --> Unknown{Có đúng một intent hợp lệ?}
  Unknown -->|Không| Fallback[Hiển thị transcript - dùng nút]
  Unknown -->|Có| Recheck[Context/version còn đúng?]
  Recheck -->|Không| Drop[Bỏ kết quả cũ]
  Recheck -->|Có| Confirm{Lệnh đã uống?}
  Confirm -->|Có| Dialog[Xác nhận đúng lần uống - mặc định No]
  Confirm -->|Không| Button
  Dialog -->|Đồng ý và context còn đúng| Button
  Button --> Save[DB transaction + idempotency + outbox]
  Button --> Rehab[Start/pause bài tập]
  Rehab --> CameraCount[Chỉ camera/FSM tạo tiến độ hoàn thành]
```

## Threads, lỗi, fallback và quan sát

| Thành phần | Cách thực thi | Lỗi/fallback và giới hạn |
|---|---|---|
| Camera | QThread; callbacks sequential; sleep theo FPS cấu hình | Mất capture có simulated frame; cần phân biệt với frame thật |
| GUI | Qt event loop/QTimer | TodayTodo poll1.5s; refresh plans2s; DB vẫn có thao tác trên UI thread |
| STT | multiprocessing spawn; queues bounded | Model/micro lỗi→unavailable; retry chuẩn bị; hủy bỏ kết quả cũ |
| Text API | background thread client; backend request thread; async SDKdeadline | Offline/timeout429→local/unknown, circuit; request cũ giữ busy cho đến worker xong |
| Outbox | relay background loop, poll mặc định0.5s | Retry/delivery scope cần kiểm tra; processed không là browserack |
| TTS | child process/coordination | Suspend khi ghi; chưa kiểm tra loa vật lý |

Logging Python và runtime artefacts hỗ trợ chẩn đoán; chưa có chứng cứ deploymentmonitoring toàn diện. Không dùng FPS EMA của engine như FPSbenchmark. Token trong URL/log và hồ sơ JSON vẫn là vấn đề privacy. [C03/C26/C32/C34/C42/C46]
''', [f'C{i:02}' for i in [1,2,3,4,5,13,24,25,26,27,28,33,34,39,40,41,42,43,46,48,49]])

doc('02_TECHNOLOGY_STACK.md', r'''
# Công nghệ, dependency và model

## Ngôn ngữ và thư viện có vai trò thực tế

| Công nghệ | Vai trò trong mã | Nguồn chính / giới hạn |
|---|---|---|
| Python | GUI, AI, service, HTTPserver, SQLadapter và test | main.py; services; web; không phải backendNode |
| PyQt5 | QWidget, signals/slots, QThread/QTimer, dialogs | app/dashboard.py; requirements>=5.15.10 |
| HTML/CSS/JavaScript | Webportal, fetchAPI, EventSource và rendering | web/templates; không thấy frontendReact trong đường này |
| OpenCV contrib | cv2.face.LBPH, detectorDNN/Haar, frame/drawing | adapters/face_adapter.py; không dùng embeddingFaceNet cho identity |
| MediaPipe | FaceMesh/FaceLandmarker và Pose/PoseLandmarkerLite | adapters/emotion_adapter.py; rehab_engine.py |
| NumPy/SciPy | Tọa độ, softmax/smoothing, PCM/resample_poly | emotion/rehab/local_voice; NumPy>=1.24;SciPy>=1.10,<2 |
| PyTorch/torchvision | MLPbiểu cảm và codeCV phụ trợ | moduleemotion; runtimeTorchCPUlog không là chứng cứ CUDA |
| faster-whisper1.2.1 / CTranslate2 | Whisperlocalencoder/decoder/int8 | requirementsprimary và Linuxlock; CT2=4.8.2 trong lock |
| PyAV18.1.0 / tokenizers / ONNXRuntime | Decodeaudio và transitive Whisper/VAD dependencies | STTlock; pinPyAV sửa compatibility theo log cài sạch |
| sounddevice0.5.6 / PortAudio native | InputStream microphone | pip package không tự chứng minh libportaudio/mic của OS |
| pyttsx3 | TTSlocal trong child process | không APISTT; voices phụ thuộc OS |
| Pydantic>=2.10 | strictschema cho proposal/request | không dùng modelconfidence làm authorization |
| google-genai2.29.0 | Official DeveloperAPI text/JSON backend | requirements-gemini-backend.txt; excluded khỏi elderEXE |
| filelock4.0.12 | Sharedfilesystem quota lock | không phối hợp quota nhiều host độc lập |
| requests / urllib HTTP | Internalclient và các công cụ network | GeminiIntentClient/server; không gửi audio đến STTAPI |
| sqlite3, http.server, threading, multiprocessing | DB và stdlibbackend/server/worker | không FastAPI, không PostgreSQL runtime hiện tại |
| python-dotenv / Pillow / psutil / tzdata | Config, ảnhUI, đoRSS và timezone | Vai trò config/runtime/script; không chứng minh IoTsensor |
| pytest/unittest, sklearn/joblib | Test và training/evaluation standalone | Phân biệt dev/module requirements với runtimeprimary |

Các role trên có source trong manifest C06–C14/C24–C34/C40/C49. OpenCV/MediaPipe/Torch có nhiều manifest standalone cũ; không thay manifest chính bằng một file trong module.

## Phiên bản và môi trường

requirements.txt là manifest runtime chính; requirements-gemini-backend.txt include nó và pinSDK. requirements-linux.lock là snapshot Linux đã có log cài sạch; requirements-local-stt.lock là closureSTT; backend.lock là closureSDK. requirements-windows.txt có bounds riêng cho Python3.11–3.12/NumPy<2/MediaPipe<0.10.21. Không dùng Linuxlock thay khóaWindows. [C49]

Log bàn giao ghi Python3.14.4 Linuxx86_64, cài sạch trong /tmp/ai-care-gemini-clean và pipcheck không brokenrequirements. Linuxlock có PyQt5=5.15.11,Qt5=5.15.19,OpenCV=5.0.0.93,MediaPipe=1.1.0,NumPy=2.5.3,SciPy=1.18.1,Torch=2.14.1+cpu,Torchvision=0.29.1+cpu. Đây là số từ lock/log, không phải lệnh kiểm tra môi trường hiện tại trong audit. [C49]

Rootconstraints nhiều gói dùng>=, không bảo đảm reproducibility một mình. Manifestrehabstandalone còn liệt kê `time` dù đây là stdlib; manifestface có pins khác Windowsbounds. Cần thống nhất cho bản phát hành sau, không sửa trong nhiệm vụ tài liệu. .spec/setup/buildbat/installer và GitHubworkflow đã có nhưng nghiệm thu WindowsDLL/model/TTS/newSDKbinary chưa có. [C49/C50]

## Model và trọng số

| Model/asset | Vai trò active | Nguồn biết được | Điều chưa biết |
|---|---|---|---|
| OpenCVface_detector_uint8.pb +pbtxt | DNNface detection; Haarfallback | modules/face/models; đọc bằngcv2.dnn | Provenance revision/trainingdataset chưa xác minh |
| LBPH recognizer | Identity, train in-memory từ crop đăng ký | FaceAdapter.train_recognizer | Tập đánh giá độc lập, calibration ngưỡng58 |
| face_landmarker.task | MediaPipeTasks face landmarks nếu APIlegacy thiếu | modules/emotion/models | Artifact không tự chứng minh expressionaccuracy |
| expression_net.pth | OptionalMLP5lớp; dashboard sử dụng3logitsđầu | modules/emotion/models; 71785bytes tại audit | Không CSV/split/metrics tại vị tríconfig; provenance UNKNOWN |
| pose_landmarker_lite.task | MediaPipeTasks pose | modules/rehabilitation/models | Camera3D/gócchuẩn không được cung cấp |
| faster-whisper-small/model.bin | LocalSTTmultilingual | data/models; chuẩn bị từ cache Systran/faster-whisper-small, revision536b0662742c02347bc0e980a01041f333bce120 theo report | Không download mới trongaudit; chưa giọngViệtđượcđồngý/groundtruth |
| age/genderCaffe weights | Moduleface standalone lịch sử | modules/face/models; face_processor.py | Không phải identity activeDashboard |
| HFD/ONNX fall weights | Nhánhvideo/legacy | modules/fall/models, hfd_manifest | Không trong callbackcameraactive; metriccũ không dùng cho rehab |

ModelWhisper tại audit có483546902bytes; chỉ statfile, không load. CheckpointMLP cũng chỉ stat, không deserializepickle. Kích thước không đánh giá chất lượng hoặc license. Có fileLICENSE cho một sốmodule; chưa chứng minh đầy đủ license/provenance cho mọiweight và asset âm nhạc/ảnh. [C06/C11/C14/C25/C48/C55]

## Dịch vụ ngoài, cấu hình và boundary

Gemini là DeveloperAPI, vertexai=False, textgenerateContent vớiJSONschema/tools=[]; không có DBtools/functionexecution/grounding/SQL hoặc tư vấn y tế. Modelconfigpin gemini-3.5-flash-lite. Key/backendflags chỉ backendsecret; desktop chỉinternalURL/token/flag. Free-tier được operator xác nhận trong bàn giao, chưa independentlyverifyprojectbilling/quota. Không dùng aliaslatest làm chứng minh modelquota. [C28/C31/C32/C50/C53]

SMTP là service có cấu hình; testmock không chứng minh thư được nhận. Các cấu hình không chứa dữ liệu nhạy cảm được mô tả bằng tên biến: VOICE_AI_ENABLED; VOICE_MODEL_PATH/VOICE_DEVICE/VOICE_COMPUTE_TYPE/VOICE_CPU_THREADS/VOICE_MAX_SECONDS/VOICE_BEAM_SIZE; GEMINI_INTENT_ENABLED/GEMINI_FREE_TIER_VERIFIED/GEMINI_API_KEY/GEMINI_PROJECT_ID/GEMINI_INTENT_*CAP; VOICE_INTENT_ENABLED/VOICE_INTENT_BACKEND_URL/VOICE_INTENT_SESSION_TOKEN. Tên biến phải đối chiếu setup/config actual khi vận hành; không đọc/copy .envprivate vào bộ tài liệu. [C25/C28/C32/C46/C49/C50]
''', [f'C{i:02}' for i in [6,7,11,12,14,25,28,31,32,34,40,48,49,50,53,55]])

doc('03_AI_MODULES.md', r'''
# Phân tích thuật toán và moduleAI

## 1. Face: detection tách biệt recognition

DNN nhận blob300×300, mean[104,117,123], lọc confidence>0.50; lấy box phù hợp nhất theo logic detector. Haarfallback dùng scaleFactor1.1,minNeighbors5,minSize40 và chọn khuôn mặt lớn. Giá trị0.90 ở fallback là số gán, không detectorprobability đã đo. [C06]

ROIpadding15% khi được chọn, chuyển grayscale, CLAHEclip2/tile8×8, bilateral d5/sigma25, resize200×200. Huấn luyện LBPH dùng image gốc, flipngang, brightness±12, rotation±4°. Một ảnh hợp lệ sinh nhiều ảnh tương quan; không gọi chúng là nhiều người/mẫu độc lập. Trên nhánh hiện tại không có backgroundclass thực dù docstring gợi ý. [C07]

LBPH mã hóa cấu trúc cục bộ theo nguyên lý LocalBinaryPattern:

\[
LBP_{P,R}=\sum_{p=0}^{P-1}\mathbf{1}(g_p\geq g_c)2^p,\quad P=8,R=1.
\]

Đây là giải thích thuật toán của thư việncv2.face, không phải codePython tự cài LBP. Histogram theo lưới8×8 được so với traininglabels; distance nhỏ hơn ngưỡng58 tạo rawmatch. Không có faceembeddingneural hay cosinesimilarity trong identitypipeline này. Temporalhistory15, unknowncounters vàTTL2s tạo recognized/uncertain/unknown/no_face. GUIconfidence bị clamp và nội suy theo distance, khoảng0.65–0.99; không được dùng như accuracy. [C06/C08]

Đăng ký crop/profileJSON rồi sync patient/legacy_map và retrain. Nhận diệnfaceID được resolveunified_patient_id; dữ liệu tên/thuốc phải truy từ patientbinding, không dựa textASR. Khi unknown, GUI có thể vẫn giữ current_patient_id; voiceguard đọc status, nhưng thao tác tay cần nghiệmthu đổi/người lạ. Nhiều mặt, ánh sáng, khẩu trang, góc nghiêng, TTL giữ người trước và anti-spoof/liveness là phần chưa đo. Chưa có FAR/FRR/accuracy trên holdoutidentity. [C04/C09/C55]

## 2. Biểu cảm: heuristic landmark và MLP tùy chọn

Dashboard có Neutral/Happy/Sad. FaceMeshlegacy hoặc FaceLandmarkerTasks lấy landmark, sau đó heuristic dùng độ rộng miệng, độ nâng khóe và khoảng lông mày chia theo khoảng mắt. Đặt d=||p263-p33||xy, w=||p291-p61||xy/d, e=((p13y+p14y)/2-(p61y+p291y)/2)/d, b=||p336-p107||xy/d:

\[
h=40\max(0,e-0.012)+12\max(0,w-0.49),\quad s=45\max(0,-0.010-e)+10\max(0,0.27-b).
\]

\[
z=(2-1.6(h+s),\;3.6h-1.2,\;3.6s-1.2),\quad p_i=\frac{e^{z_i-\max(z)}}{\sum_j e^{z_j-\max(z)}}.
\]

Khi d<1e-4 trả default[.90,.05,.05]. Tên FACS trong code không chứng minh model được chuyên gia FACS gán actionunits hay validation y khoa. [C10]

MLP độc lập dùng21landmarks×3tọa độ=63features. Preprocesscenter theo mũi và normalize theo khoảng mắt3D, flatten. Network Linear63→128→64→5 với ReLU/dropout. Năm lớp training là Neutral/Happy/Sad/Angry/Surprised. Dashboard chỉ lấy ba logits đầu, softmax riêng; khi model có, p=0.75pheuristic+0.25pMLP3. Lấy trung bình10frames rồi argmax; noface giữ ngắnTTL1.2s trước clear. Đây không phải bộ phân loại5lớp đầy đủ trên dashboard. [C10/C11]

Trainingcode có seed42,batch32,max200epochs,lr0.001,weightdecay0.0001,dropout0.25,patience25; sessiontrain/val/testfractions0.6/0.2/0.2 với tối thiểu5session và kiểm tra không overlapsession. Baseline LogisticRegression dùng cùng split; evaluator dự kiếnaccuracy,macroP/R/F1,confusionmatrix/support. Có code không chứng minh training đã chạy đúng hay metrics cao: checkpoint tồn tại, CSV/splits/results theo config không có. Cần kiểm tra tách theo người nếu nhiều session một người; session-disjoint chưa bảo đảm subject-disjoint. [C12/C55]

Outputcamera hiện JSONlatest vàsharedstate, không historyunifiedDB. Moodselfreport là đường riêng vào mood_checkins; không thay bằng emotioncamera. Không suy diễn “buồn” thành trầm cảm, tình trạng sức khỏe hoặc nguyên nhân. [C13]

## 3. Phục hồi: landmark, hình học2D và FSM

MediaPipePoselegacy dùng modelcomplexity0,detection/tracking0.55; fallbackTasksliteIMAGE,numposes1,confidence0.45. Xử lý lostpose/occlusionTTL1.2s reset partialrep; pause/resume reset phần đang làm, giữ count đã ghi. Requiredvisibility đa số0.35; missinghip/ankle có surrogate ở các bài. [C14–C17]

calculate_angle dùng vector tại khớpb, lấy atan2 giữa c-b và a-b:

\[
\theta=\left|\operatorname{atan2}(c_y-b_y,c_x-b_x)-\operatorname{atan2}(a_y-b_y,a_x-b_x)\right|\frac{180}{\pi},\quad \theta>180\Rightarrow\theta=360-\theta.
\]

Tọa độ là normalizedx/y; không nhân lại theo width/height trong phép góc này. Phép đo là góc chiếu2D, ảnh hưởng aspectratio, camera viewpoint, che khuất và surrogate, không góc giải phẫu3D chuẩn. [C14]

| Bài | FSM/đếm thực tế | Chấm form / điểm yếu |
|---|---|---|
| Nâng tay | down→raising khimean>60°; peak>=142→hold_peak; mean<130→lowering; hạ<=50 đếm | Khuỷu<130 và chênh trái/phải>25° tăng penalty; hold<0.35s phạt, cuehold0.5s; scoremax(50,100-penalty); correct nếupenalty<15 |
| Đứng-ngồi | ready→standing>=155 hoặcsit<=118; descending<140→sit<=118→ascending>125→standing>=155; phải had_bottom | Torsolean>45° thêm lỗi; ankle thiếu surrogate; scorefloor50; correctpenalty<15 |
| Đi tại chỗ | chênh rk.y-lk.y>.065→leftup, <-.065→rightup; lastfoot bảo đảm xen kẽ; absdiff<.035 vềstance | Đếm ngay lift; knee.y<hip_y+.18 formgood100, còn lại80/incorrect; chưa đo gaitphase chuẩn |

Defaulttargets10/10/15 với reminder16h có thể sửa qua planversion. DB session giữ target_count_snapshot và plan_version. Rep_idempotency mặc định session/exercise/repnumber; insert event, updatecount/status và outbox cùngtransaction. Chỉ khi count>=target mới camera_verified_completed; voice không có intentcomplete. [C15–C18/C27]

Nhưng dashboard so totalreps với target và ghi cảincorrectreps. Adapter không tự kiểm tra quality_threshold, visibility/source/hardware_valid hoặc tính hợp lệ score. Score<=0 dashboard còn dùngfallback90. Vì vậy “camera verified” là tên trạng thái phần mềm, chưa chứng minh từng rep đúngform, nguồn camera thật hay lợi ích phục hồi. Chưa testđồngthời2writer/faultinject; uniqueidempotency không tự loại mọi lostupdate. [C18/C19/C55]

## 4. VoiceSTT và hiểu transcript

Explicitmicro→AudioRecorder(InputStream)→mono float32→resample_poly16k→WhisperModelsmallmultilingual localfilesonly. Durationmặc định15s, giới hạnconfig1–30s, CPUint8/2threads/beam1/languagevi; condition_on_previous_text=False, vad_filter=True. Model load một lần trong persistent worker; decode và consume generator hoàn tất ngoàiUI; audiozero trảempty, NaN/fileinvalid bị reject. Không truyền audio vào Gemini/APISTT. [C24/C25]

Controller state/loading/idle/recording/stopping/transcribing/cancelling; queuesbounded, sessionUUID và immutablecapturedcontext kiểm tra từ polling50ms. Hủy nativeinference không có nghĩa model dừng ngay, nhưng response bị bỏ; không mở phiên chồng trước idleack. Contextchange/tab/patient/plan hoặcshutdown invalidates. TTSsuspend/nhạcpause khi ghi; physicalTTS/mic vẫn chưa nghiệmthu. [C26/C34]

### Registry và chính sách quyết định

| Intentenum | Handler thật | Điều kiện |
|---|---|---|
| navigate_home | medication_tabs.setCurrentIndex(0) | Cópatient, khôngrunning |
| snooze_medication | ElderSyncClient.confirm_dose_taken(snooze) | Tabtoday, đúng1dose, khôngOVERDUE |
| confirm_medication_taken | cùngservice self_reported_taken | Đúng1dose + dialogdefaultNo + recheck |
| request_medication_help | cùngservice help_requested | Đúng1dose/context |
| start_rehabilitation | Dashboard._on_start_exercise | Tabrehab,camera,activeplan,khôngrunning |
| pause_rehabilitation | Dashboard._on_pause_exercise | Tabrehab,camera,running,khôngpaused |
| unknown | Khôngdispatch | Câu mơ hồ/nhiều ý/context không hợp lệ |

No intent tư vấny tế/SQL/emergencycall/completeexercise. NormalizeUnicode/case/punctuation và exactallowlist/paraphrases xử lýlocal; phủ định, uncertain, conjunction/injection được guard. Exact“không biết dùng thuốc này” là help exception, không confirmation. Proposal gồmintentenum,slots(snooze_minutes chỉnull),decision(route/clarify/reject),evidence_text; extra fields bịforbid. Evidence phải substring transcript, intent thuộc contextallowlist và khớp semantics độc lập. Modelconfidence/policy không có quyền mở rộng handler. [C27/C29/C30]

Gemini production chỉ nhận20 câu neutralnavigation đãreview; payload không patientID/contextDBhash/medication/healthrecord. Luồng local tiếp tục xử lý thuốc/phục hồi. HTTP không chấp nhận syntheticflag; CLI synthetic riêng thử enum rộng bằng dữ liệu giả. Đây là gateclosedcatalog, không phải anonymizationhealthrecords hoặc xử lý ngôn ngữ tự do. [C28–C33]

BackendSDKgoogle-genai2.29,modelpin,JSONschema/tools=[]/autofunctiondisabled/temp0/maxoutput512. Totalclientdeadline<=8s, transportminimum10s; SDKimplicitattempts1 và appretry0(default), tối đa1 khi cònbudget. Quota reserve1200tokens/request; caps1RPM/2400TPM/10RPDreserve2; circuit3fails/30s,429cooldown60s và filelock. Caps không là quota thậtAIStudio. Keybackendkhôngbundleapp; clouddefaultfalse. APIoffline/429/badJSON/stale→local/unknown, không businessreplay. [C28/C31–C33/C50]

## 5. Module lịch sử và phạm vi AI

Faceage/genderstandalone, Voskarchive, semantic/orchestratorcũ và fallHFD/ONNX/video có source. Dashboard hiện không gọi fall trong callbackcamera; APIvoice/STTcũ410, compatibilityfactorydisabled. Một số TTScoordinator được reuse nên không nói toàn bộservices/voice_ai đã xóa. Trò chơi/thuốc/healthrecord là rules/businessworkflow, không gọi chúng là modelAI chỉ vì cùng sản phẩm. [C23/C35/C36/C39/C48]
''', [f'C{i:02}' for i in list(range(4,20))+list(range(24,37))+[39,48,50,55]])

doc('04_FUNCTIONAL_WORKFLOWS.md', r'''
# Luồng chức năng và boundary dữ liệu

## 1. Danh tính→hồ sơ

Frame→FaceAdapter.detect_face→preprocessROI→LBPH→recognize_face temporalstate→Dashboard._do_update_dashboard_ui→_resolve_patient_id(legacy_patient_map trước fallback)→set_patient cho TodayTodo/games và contextvoice. Hồ sơ đăng ký qua RegistrationDialog/FaceAdapter.register_patient, JSON/crop và sync_single_patient. Không có một faceembeddingDB riêng hiện hành. [C04/C06–C09]

Input cần mặt nhìn camera và crop có chất lượng. Noface/unknown hiển thị trạng thái tương ứng; uncertain có TTL. Unknown không xóa current_patient_id nên cần nghiệmthu quyền thao tác tay khi người cũ rời chỗ. TodayTodo.refresh_data có fallbackfirstACTIVEpatient nếu patient không tìm thấy; branch này chưa thấy switch_patient syncclient tương ứng. Voice snapshot rejectbindingmismatch; không suy ra mọi nút tay được bảo vệ tương tự. [C04/C20/C27]

## 2. Thuốc→hiển thị→xác nhận→người nhà

| Bước | Codepath | Đọc/ghi và giới hạn |
|---|---|---|
| Tạo/sửa đơn | ApiRouter._create_prescription/_revise_prescription | prescriptions/items/schedules revision, occurrence snapshots; create sinh4ngày, UTC+7hardcode |
| Hiển thị hôm nay | TodayTodo.refresh_data/_render_medications | SELECTdose theo ngày; ảnh,tên,dose,instructions và các nút state-dependent |
| Nhắc/quá hạn | OutboxRelayService.scan_overdue_tasks | PENDING/REMINDING quá grace→OVERDUE,alerts,outbox; SNOOZED không thuộc scan |
| Xác nhận tay | TodayTodo._on_confirm_taken | ElderSyncClient.confirm_dose_taken(self_reported_taken) |
| Xác nhận voice | CommandDispatcher.dispatch | Đúng1dose, exactcontext, dialogdefaultNo, recheck trước service |
| Commit | ElderSyncClient.flush_offline_queue | sync_inbox idempotency, dose_occurrencesCONFIRMED,dose_events,outbox; lateaction có note |
| Theo dõi | Relay→SSEHub→webrefetch _get_medication_doses | Cóselfreportedlabel; SSEqueue test đãpass, browserInternet/emailthật chưa nghiệmthu |

Snooze hiện lưu stateSNOOZED; cần bổ sung bằng chứng nhắc lại sau delay và không mắc kẹt khi quá hạn. Help đổistateREMINDING và tạoalert, relay chọnprimaryactivecaregiver cóconsent/email. Hộp thoại desktop có liên hệhardcode và khẳng định gửi tới người nhà/bác sĩ; không coi đây là chứng cứ thư đã tới hay bên kia sẽ đến ngay. [C20–C23/C27/C42]

MedicationService/MedicationPanel và moduleScheduler có test riêng16case nhưng panel=None trong dashboardactive. Không nối mũi tên từ schedulerlegacy sang TodayTodo khi source không có call. Xác nhận chỉ tự khai báo, không dùng camera để xác minh nuốt thuốc, không suy ra tuân thủ điều trị khách quan. [C20/C23]

## 3. Kế hoạch→camera reps→DB→bác sĩ

Web _update_exercise_plan tạoversion/audit/outbox; dashboard pollplan mỗi2s, chọnbài và _on_start_exercise kiểm tra expectedplan. RehabSessionAdapter.get_or_create_daily_session giữplan_version/target_count_snapshot. CameraManagercallback→RehabAdapter→RehabilitationEngine/FSM→metrics→dashboard record_verified_rep cho mỗi rep mới. Eventunique +updatecount +outbox cùngtransaction; web _get_rehab_sessions đọc sauSSE. [C14–C19/C27/C42]

Stop/pause/hide/mấtpose xử lýstatepartial và metrics; missingcamera cần markunavailable thay hoàn thành. Tuy nhiên hardware_valid không được chuyển thành điều kiện bắt buộc tại điểmDBwrite đã kiểm tra. Cần testcameraunplug/simulatedframe và tình huốngframecũ trước gọi camera_verified_completed. DBcaller có thể đưa rep giả; tênstate không là attestationnguồn camera. [C03/C18/C19]

Khi tổngreps đạt target, routine tiến bài tiếp theo và completedlabel, gồm cảincorrectreps; quality_threshold chỉ lưuversion chưa chặn completed. Không viết “10/10 đúng chuẩn” từ count10/10. Ngày session dùng date.today của host, plan có timezone nhưng chưa chứng minh mọi đường respectIANA/DST. [C18/C19]

## 4. Biểu cảm→lưu→monitoring

Camera→EmotionAdapter.process_frame→3lớp/smoothing→_persist_result→shared/results/emotion.json và sharedstate. Web _get_mood đọc mood_checkins và emotion_inferences. Không thấy insertioncamera trongactiveadapter/controller/service. Seed DataImporter._seed_mood_and_emotions tạo demonstrationrows; không xem seed như historycảmxúc thực. Vì vậy workflowcameraemotion→unifiedDB→web là PARTIALLY_IMPLEMENTED. Moodbutton→record_mood→mood_checkins/outbox là luồng tự khai báo riêng. [C10–C13/C41]

## 5. Voice→intent→action

LocalVoiceWidget dưới tabs luôn cómicro; khi flagfalse/worker chưa có, clickđầu chuẩn bịmodel vàidle; clicktiếp mớirecord. Ghi chủ động, Dừng→inference, Hủy→tokeninvalidate; tối đa15s(default). Khi đổipatient/tab/source/plan, capturedcontext mất giá trị. Các state/errorcode được render để giữ nút tay dùng tiếp. [C02/C24–C26]

Transcript→VoiceRequestCoordinator→localrules; câu đủneutralcatalog và cloudconfigured mới→internalHTTPauthenticated→TranscriptIntentEndpoint recheckauth/stateversion→GeminiIntentService privacy/schema/budget→SDK→semanticvalidate→responseID/contextcheck→dispatcher. Backendrequest cópatient/context phục vụauthnội bộ, payloadprovider bỏ chúng; không coi “ẩnID” đủ để gửihealthtext. Localmed/rehab intent không gửiprovider. [C27–C33]

Transcript chỉ là input, không SQLupdate. Proposalvalid mới gọi cùng handlernút; confirmationtaken yêu cầu đúngoccurrence/doserevision/context saudialog, command dedup và servicetransaction. Offlinevoice không queue/replay vềsau; buttonqueue vẫn tồn tại. FailureGemini/offline429/badJSON/latecontext không mất khả năng bấm tay. Voicekhông đánh dấu completedrehab. [C20/C27/C30/C33/C43]

## 6. Nhập sức khỏe, lời khuyên và báo cáo

Caregiverweb nhập chỉ số→ApiRouter._add_observation→measurement_groups(client_request_idunique) +health_observations +requestmatchingPENDING→COMPLETED/log +outbox. Thời gian measured_at khác recorded_at; corrections/clinicianreviews được schema/API hỗ trợ. Web vẽ timeline/trend từAPI, chưa có sensordevice ingestđã nghiệmthu. Nút“đã nhớ đo” ở elder chỉ hiệninfo, không là bản ghi kết quả đo. [C37/C38]

Caregiverreport→caregiver_reports/outbox→đúngcareteam; clinicianrecommendation→care_recommendations→elderread→recommendation_receipts. Emergencycontacts/events chỉ lưu/hiển thị/log, không tự liên lạc cứu hộ. Aggregationtrend có trong MonitoringService standalone; activeWeb cóSQL/API riêng, không giả định dùng mọi phépaggregate của standalone. [C38/C42/C44]

## 7. Trò chơi và nhạc

CognitiveGamesWidget→GameEngine seededrandom tạoboard3/4/6cặp trên UI, sequence2/3/4hình; servicerepository ghi gamesessions/results vào data/cognitive_games.sqlite3. Engine cóexpert8cặp/5hình nhưng UI hiện không expose mặc định. Musicwidget dùng AudioService; voicepausesaudio khirecord. Identitymodule dùng MockPatientIdentityAdapter như binding explicit, không một model nhận diệnthứhai. Importer có thể gộp historygames vàounified; chưa chứng minh livepushgame→web. Không có bằng chứng trị liệu trí nhớ hiệu quả. [C34/C39/C41]

## Ma trận lỗi và fallback

| Trigger | Phản ứng có source/test | Phần chưa kiểm chứng |
|---|---|---|
| Thiếu model/PortAudio/micro | Voiceunavailable, retry, nút tay | Micdriver/OSthật và restartkhi đang ghi |
| Faceunknown/patientđổi | Voicecontextinvalidate/guard | Hành động tay vàfallbackfirstpatient |
| Context/dose/plan đổi giữa request | Bỏresponse/rechecktransaction | Stress nhiềuwriter/phút/thiết bị |
| Network/429/providertimeout | Boundedretry/circuit,local/unknown | QuotaAIStudio,full102acceptance |
| SMTPerror | DeliveryFAILED trong service/testmock | Mailbox/nhận đọc/retrytimed thực tế |
| SSEdisconnect | Frontendrefetch/reconnect/pollfallback | Latencybrowser3thiếtbị/HTTPS ngoàiLAN |
| Cameraunplug/occlusion | Simulatedframe/partialreset | Hardwaregate tạiDBcompletion |

''', [f'C{i:02}' for i in [2,3,4,6,9,13,18,19,20,21,22,23,24,26,27,28,29,30,33,34,37,38,39,41,42,43,44,55]])

# Extract DDL as text only. Do not open a real DB or execute migrations.
SCHEMA = []
for p in sorted((ROOT/'database/migrations').glob('*.sql')):
    sql=p.read_text(encoding='utf-8')
    for m in re.finditer(r'CREATE TABLE IF NOT EXISTS\s+(\w+)\s*\((.*?)\);',sql,re.S):
        name,body=m.groups(); source=str(p.relative_to(ROOT)); start=sql[:m.start()].count('\n')+1; end=sql[:m.end()].count('\n')+1
        clean=re.sub(r'--[^\n]*','',body)
        columns=[]
        for line in clean.splitlines():
            line=line.strip().rstrip(',')
            if line and not re.match(r'(FOREIGN|PRIMARY|UNIQUE|CHECK|CONSTRAINT)\b',line,re.I):
                mm=re.match(r'(\w+)\s+(\w+(?:\(\d+\))?)(.*)',line)
                if mm:columns.append({'name':mm[1],'type':mm[2],'constraints':mm[3].strip()})
        fks=[dict(columns=a.strip(),target=b,target_columns=c.strip(),on_delete=d or 'NO ACTION') for a,b,c,d in re.findall(r'FOREIGN KEY\s*\(([^)]+)\)\s*REFERENCES\s+(\w+)\(([^)]+)\)(?:\s+ON DELETE\s+(CASCADE|RESTRICT|SET NULL))?',clean,re.I)]
        pks=[c['name'] for c in columns if 'PRIMARY KEY' in c['constraints']]
        composite=re.findall(r'^\s*PRIMARY KEY\s*\(([^)]+)\)',clean,re.M)
        for key in composite:pks+= [x.strip() for x in key.split(',')]
        uniques=[c['name'] for c in columns if 'UNIQUE' in c['constraints']]+re.findall(r'^\s*UNIQUE\s*\(([^)]+)\)',clean,re.M)
        SCHEMA.append(dict(table=name,source_path=source,line_range=[start,end],columns=columns,primary_key=pks,foreign_keys=fks,unique_constraints=uniques,ddl=m[0]))
        claim('DB_'+name,f'DDL khai báo bảng{name}, columns/PK/FK/constraints như từ điểnschema.',source,status='IMPLEMENTED',tests=('reports/gemini_intent/realtime-regression.txt',),limit='DDLđãtestmigration; không truy vấnproductionrows. ERD thể hiệnkhóa ngoại, không chứngminh livewriter/3NF/multiDBsync.')
        CLAIMS[-1]['symbol']='CREATE TABLE '+name
        CLAIMS[-1]['line_range']=[start,end]

erd='```mermaid\nerDiagram\n'
for t in SCHEMA:
    erd+='  '+t['table']+' {\n'
    for c in t['columns']:
        if c['name'] in t['primary_key'] or any(c['name'] in f['columns'].split(', ') for f in t['foreign_keys']):
            key=' PK' if c['name'] in t['primary_key'] else ' FK'
            erd+=f"    {re.sub(r'[^A-Za-z0-9_]','',c['type'])} {c['name']}{key}\n"
    erd+='  }\n'
for t in SCHEMA:
    for i,f in enumerate(t['foreign_keys']):
        # SQL alone does not mandate every parent has children; optionality retained.
        one_to_one= f['columns'] in t['unique_constraints'] or t['primary_key']==[f['columns']]
        erd+=f"  {f['target']} |o--o{'|' if one_to_one else '{'} {t['table']} : {f['columns'].replace(',','_').replace(' ','')}\n"
erd+='```\n'
schema_table='| Bảng | PK | FK và deleteaction | Unique | DDL |\n|---|---|---|---|---|\n'
for t in SCHEMA:
    fks='; '.join(f"{f['columns']}→{f['target']}({f['target_columns']}),{f['on_delete']}" for f in t['foreign_keys']) or '—'
    schema_table+=f"| `{t['table']}` | {', '.join(t['primary_key']) or '—'} | {fks} | {'; '.join(t['unique_constraints']) or '—'} | `{t['source_path']}`:{t['line_range'][0]}–{t['line_range'][1]} [DB_{t['table']}] |\n"

db_body=r'''
# Cơ sở dữ liệu, ERD và đồng bộ

## Công nghệ và phân tán thực tế

UnifiedDatabaseManager dùng sqlite3, filedata/unified_care.sqlite3(default), foreign_keysON, WAL, busy_timeout5000ms, connectiontimeout30s. connect dùngtransactioncontext; APIbusinesswriter commit cùngoutbox. Không có PostgreSQLruntime trongmanager; comment“PostgreSQLcurrent/3NF” chưa là kiểm chứng. Schemajournalversion4migration. Không đọcproductionDB/hồ sơ trongaudit. [C40/C41/C47]

SQLitecognitive_games vẫn là DBactive của gameplay; medication_standalone/health_standalone là nguồnimport/moduleđộc lập; JSONface/emotion/sharedstate là storekhác. Unified tên gọi không làm mọiwriter tự dùng chungDB. Phải phân biệt migration/import một lần với livereplication. [C09/C13/C23/C39/C41]

## Nhóm entity và ownership

| Nhóm | Entity và vai trò |
|---|---|
| Identity/permission | users,patients,caregivers,clinicians,legacy_patient_map,patient_caregivers,care_team; quan hệ/consent và quyền |
| Thuốc | medications,prescriptions,prescription_items,medication_schedules,dose_occurrences,dose_events; schedule revision và dose snapshot |
| Cảnh báo | alerts,notification_deliveries; DBalert khác delivery và userreceipt |
| Sức khỏe | observation_types,measurement_groups,health_observations,symptom_entries,clinician_reviews,clinical_messages,message_receipts,monitoring_plans,patient_thresholds |
| Tâm trạng/biểu cảm | mood_checkins,emotion_inferences; selfreport tách camerainference; livecamera writer chưa nối |
| Phục hồi | rehab_plans,exercise_plan_versions,rehab_sessions,rehab_events; target/quality/version và eventidempotency |
| Trò chơi | game_types,content_packs,game_sessions,game_results; bảngunified không chứng minh writeractive dùng nó |
| Liên lạc/theo dõi | caregiver_reports,report_messages,care_recommendations,recommendation_receipts,emergency_contacts,emergency_contact_events,audit_events |
| Điều phối | outbox_events,sync_inbox,device_sessions,schema_migrations,measurement_requests,measurement_request_logs |

Entitypatient ownership đa số FKpatient_id; audit/lookup/actor không phải mọi bảng cópatient_id. FKRESTRICT/CASCADE/SETNULL thực tế nằm dưới; không gọi cascade xóa an toàn nếu chưa testretention/recovery. FieldsUTC/local/timezone và snapshot bảo tồn ngữ cảnh, nhưng createprescription hardcodeUTC+7/sessionhostdate còn cần kiểm tra. [C18/C21/C40/C41]

## Ràng buộc, idempotency và conflict

Schema có PK/foreignkeys, enumCHECK, UNIQUErevision/clientevent/requestid/repkeys tùy bảng. Unique constraint không tự chứng minh chống mọi race; businessvoice dùng BEGINIMMEDIATE khi so expectedcontext; repadapter đọccount và checkidempotency rồiwrite chưa test2writer. Dữ liệu cũ theo snapshot không bị đổi cùng tênthuốc/targethiện tại; cần đối chiếu duplicatejoin trongTodayTodo chỉjoin schedule_id so với webjoinid+revision. [C18/C20/C21/C43]

Voicecontext hashing từ authoritativeDBstate gồm dose/prescription revision, plan/session version; UIruntime/epoch được kiểm tra tại desktop. Hash gửibackend nội bộ không gửiprovider. Backendauth vàversion recheck trước/sauclassification; không tin permissions do model tạo. [C27/C30/C33]

## Đồng bộ và offline

ElderSyncClient ghi SQLite trực tiếp, JSONqueue perpatient và sync_inbox chống duplicateclient_event_id. is_online được set bằngflag, không networkhealthprobe. Buttonqueue có persist/reconnect/restart behavior đã có test; voicecommandfailed/stale không replay với IDmới. Đây là queuebusiness local, không là distributedreplication nhiều SQLitefile. [C43]

Outboxevent đượcinsert cùngbusiness transaction. Relaypoll mặc định0.5s đọcprocessed_atNULL, dispatchSSEminimal signal được lọcquyền, sideeffectemail nếu cóconfig, markprocessed. SSEHub boundedqueue; streamHTTP gửi event, frontendrefetch bằng authAPI. Webpollfallback30s/reconnect, desktopTodayTodo1.5s vàplan2s. Một request/backend eventprocessed không là receiptbrowser/email. Cần benchmarkcommit→browserrender quaHTTPS và3thiếtbị. [C42/C44]

Không thấy replay durable theoLast-Event-ID toàn bộhistory; refetch giúp khôi phục snapshot thay bảo đảm nhận mọi event. Không có conflictresolver/vectorclock/CDC/multihostlimiter đã kiểm chứng. Thu hồi quyền giữa phiên được testSSE/auth; vẫn cần cookie/tokenprovisioning/refresh choelderdevice thật. [C33/C42–C44]

## Xác thực và privacy cần khắc phục

Authsession in-memory, randomtoken,7ngày; checkuser/patientactive vàcareteam/caregiverconsentpermission. Các guard có testsuccess vàdeny, nhưng authenticate_credentials còn demo bypass, prefixpbkdf2 chứaplaintext và trảhintpassword. Publicquick-accounts route còn trảpasswordtừstore, publicpatientlist cần reviewdataexposure. Đánh giá đây là nguyên mẫu, không kết luận secureproduction. Không sao chép giá trị bí mật vào report. [C44/C45/C56]

SSEtokenquery vàlog_message có thể lưutoken trongURL; backupcreate_sql_dump ghiplaintextSQL. Chưa tìm thấy policyretention/encryption end-to-end đã nghiệmthu. Không mởdumpDB, .envprivate hoặc sao chépemail/patientrecords. Backuproundtrip code so tablecount/rowcount, không chứngminhchecksumtừngrow hay PostgreSQLrestore; audit không thực hiệnbackup. [C46]

## ERD theo khóa ngoại SQL

Sơ đồ bên dưới được tạo trực tiếp từ CREATE TABLE của4migration; chỉ hiển thịcolumnsPK/FK cho dễ đọc. Parent có thể không có children; ký hiệuparentoptional được giữ bảo thủ, một số FKNOTNULL thực tế bắt buộc parent khi childtồn tại. Cardinalityunique được phân biệt; schema_dictionary.json chứa mọicolumn/type/constraints/DDL, không chứa dữ liệu.
'''
doc('05_DATABASE_AND_SYNC.md', db_body+'\n'+erd+'\n## Từ điển PK/FK/Unique theo DDL\n\n'+schema_table+'\n## Từ điển đầy đủ\n\nMọi cột, kiểu, constraint nguyên văn DDL trong schema_dictionary.json; không suy ra writer/runtime chỉ từ existence table.\n', [f'C{i:02}' for i in [9,13,18,20,21,23,27,30,33,39,40,41,42,43,44,45,46,47,56]]+[f"DB_{t['table']}" for t in SCHEMA])

doc('06_TESTING_AND_EVIDENCE.md', r'''
# Kiểm thử, số đo và thiết kế thí nghiệm

## Phạm vi và nhật ký lượt kiểm toán

**Không chạy test ứng dụng trong lượt này.** Không cài package, import module ứng dụng/native audio, mở DB production, thu micro/camera, gọi Gemini hay SMTP. Dùng rg/sed/cat đọc source, AST stdlib xác định symbol/line, parser văn bản DDL, JSON đọc artefact và SHA-256 đối chiếu source. python không có trong PATH; python3 chạy generator/validator tài liệu. Đây là kiểm tra tài liệu, không thêm kết quả thử nghiệm hệ thống. validation_report.json ghi môi trường/lệnh/kết quả kiểm tra cuối.

## MEASURED RESULTS — artefact hiện có, chưa chạy lại

| Artefact | Kết quả kiểm chứng bằng file | Môi trường/input và giới hạn |
|---|---|---|
| reports/gemini_intent/intent-and-stt-tests.txt | 107passed,1SDKwarning | pytest nhóm intent/STT; mockSDK/audio, synthetictext; không mic vật lý |
| reports/gemini_intent/legacy-regression-isolated.txt | 41passed | runner mocksounddevice tránh nativeaudio; contract/business/reliability/rehabconfig cũ |
| reports/gemini_intent/realtime-regression.txt | 13passed,0.33s | 12scenario+casecancel; in-memory SQLite, in-processSSEqueues, fakeSMTP |
| reports/local_stt/final-tests.txt | 85passed,1skipped,8.89s | overlap với log mới; testaudioViệt chuẩn bịskip; không cộng vào161 |
| reports/local_stt/rehab-regression.txt | 17passed,3.50s | test_rehab_assistant, landmark/blankframe/counters; không humantrial |
| reports/local_stt/routine-regression.txt | 6passed,3.78s | routine/UI/datafixture; không lâm sàng |
| reports/medication_migration/medication_tests.txt | 16test,OK,1.794s | service scheduling legacy, fakeSMTP; panel không active |
| reports/gemini_intent/http-smoke.json | navigationonce/auth/sizechecks true,66ms,Gemini_calls0 | loopbackHTTP+Qt,DBgiả,Gemini mock, không microphone |
| reports/gemini_intent/dashboard-smoke.txt | lifecycle offscreen/worker/model load idle | camera/audio mocked,TTSdisabled,SMTPforbidden; không inferencecamera/micro thật |
| reports/gemini_intent/clean-pip-check.txt / clean-full-install.txt / clean-smoke.txt | cài sạch/check/schema passed | Python3.14.4 Linux trong /tmp venv; không WindowsEXE nghiệmthu |
| reports/local_stt/cpu-final.json | cold727ms,p50=4642ms,p95=6015.95ms,RSS1830600704bytes | CPUsmall/int8,2threads,beam1,12lượt/4WAV873–1170ms; không groundtruth, không tổngRAMapp |
| reports/local_stt/gpu-camera.json | CUDAerror; camera unavailable | Không đạt kiểm traGPU/camerađồngthời, không suy ra mọi máy không cóGPU |
| reports/gemini_intent/offline-benchmark.json | 104/150correct;72/102acceptance;0unexpected_sensitive_routes;p95local0.027667ms | Clouddisabled; coveragepolicylocal, không modelaccuracy/fullvoice |
| reports/gemini_intent/limited-live-benchmark.json | 3/3schema vàintent;1633/1138/1562ms;p95sample1633ms | 3syntheticcases, khôngdispatchbusiness; project/quota chưa verified; n=3 quá nhỏ |
| reports/gemini_intent/live-smoke.json | 1746ms cho1sample | Smoke riêng; không cộng thành accuracy trên102case |

Ba nhóm107+41+13=161 chỉ là các nhóm trong reportGemini, không tuyên bố161unique capability hoặc toànrepo pass. Các nhóm85/17/6/16 ở logkhác có trùng phạm vi. pytest tổng không tự chứng minh từng assert phủ hết mục tiêu ghi trong docstring. [C51–C54]

### Chất lượng và tính tái lập của log

Logpytest trên thường chỉ summary, không kèm nguyên lệnh/env đầy đủ. Nếu lệnh không ghi trong report/script tương ứng thì **UNKNOWN**, không tái dựng rồi gọi đó là lệnh đã chạy. Python3.14.4/Linux/venv sạch lấy từ report và cài sạch, không mặc định mọi log cùng fixture/máy. Runtime capability cũ ghi thiếu PortAudio; reportGemini mới ghi library có nhưng không có thiết bị, cần giữ thời điểm và scope khác nhau. Người dùng từng xác nhận STT hoạt động trên desktop là phản hồi vận hành, chưa thay thế log nghiệm thu audio có ground truth. [C25/C49/C55]

STT12lượt thuộc4file,3lặp/file; observations tương quan nên không xem n12 là12người. RSS≈1.83GB theo bytes thập phân là scriptengine, không peakRAM/VRAM toànapp. Latency gồmdecode vàconsume segments, không chỉ generatorcreation. CPU p95 này chưa đạt mục tiêu5s trong kế hoạch, audio1s chưa đại diện câu3–10s. [C51]

Offlineintent acceptance72/102=70.59%; overall104/150=69.33%. HOME→UNKNOWN40, SNOOZE/HELP/START→UNKNOWN2 mỗiintent. Unknown giữ an toàn/nút tay nhưng vẫn là miss trong coverage metric. 0unsafe trên tập tổng hợp không là xác suất tuyệt đối0 ngoài thực tế. Không có macro-F1/Gemini accuracy trên102case để công bố. [C52]

### Kiểm tra source test so với tên scenario

tests/test_realtime_sync_12_scenarios.py gọi ApiRouter.handle_request trực tiếp, đăng ký SSEClient queue nội bộ, gọi relay.process_pending_events. Không mở3browser hay3máy Internet. test_scenario_12... đo3phiên ×20event nhưng pytestlog capture stdout không lưu các p50/p95 chi tiết. Chỉ có summarypassed và assert<5000ms; **không tự tạo số p95network**. Fixture DataImporter.import_all có thể đọc nguồnstandalone/JSON trênhost; chưa bảo đảm mọifixture thuầnsynthetic nếu không cô lập nguồnimport. [C41/C42/C54]

Test_face_registration có pathdefault tạo/xóa profile; vì vậy audit không chạy. BaselineSTT còn6fail/no such tablepatients/rehab_plans doisolation/order và timeoutteardown; baseline-failure-details.txt,baseline-group-rerun.txt ghi rõ. Nhóm nativeaudio ban đầu timeout, all-tests.txt không phải bằng chứng passfullsuite. Không che thất bại chỉ vì log nhóm riêng đãpass. [C09/C54/C55]

## EXISTING BUT UNVERIFIED CLAIMS

| Tuyên bố thường gặp | Vì sao chưa đủ | Cách diễn đạt phù hợp |
|---|---|---|
| Confidenceface90% nghĩa accuracy90% | Heuristic clamp/default; không confusiontest | “Điểm hiển thị từ distance, chưa calibration” |
| ExpressionMLP đã đạt accuracy cao | Checkpoint có, thiếu CSV/splits/metrics/provenance | “Code training/evaluation và checkpoint; chất lượng UNKNOWN” |
| 10/10 camera verified là10rep đúngform | Dashboard dùngtotalcount, qualitythreshold chưa enforced | “Đạt số lần theo FSM; chất lượng từngrep chưa được chứng minh” |
| Người già đã uống thuốc thực tế | Chỉ button/voice selfreport | “Người dùng xác nhận đã uống” |
| Thuốc snooze luôn nhắc lại đúngdelay | Activeflow chỉ đổi state, chưa timerproof | “Có thao tác nhắc lại; timedworkflow chưa nghiệmthu” |
| Realtime3client<5s quaInternet | Testqueueinprocess, stdoutmetric không lưu | “Đã testoutbox/SSE logic; latency thiết bị thật UNKNOWN” |
| Gemini đạt≥95% hoặc JSON≥99% | 3livecase; chưa102acceptance/cloudtắt | “Smoke3syntheticcase đãpass; chưa đạt bằngchứng nghiệmthu” |
| Hệ thống an toàn/secure hoặc cải thiện sức khỏe | Authplaintext/publicpassword; không clinicaltrial | “Nguyên mẫu nghiên cứu kỹ thuật, chưa validationlâm sàng/production” |

## PROPOSED EXPERIMENTS — chưa thực hiện

| Module | Input/ground truth | Quy trình tái lập | Metrics và điều kiện diễn giải |
|---|---|---|---|
| Face | Người tham gia đồng ý; identitygán trước; ngườiunknown giữ riêng | Tách theo người/session; khóa threshold trướctest; sáng/góc/khẩu trang/nhiều mặt | Accuracyclosedset;FAR=FA/Nimpostor;FRR=FR/Ngenuine; báo reject/TTL/latency, khoảngtin cậy |
| Expression | Ảnh/session đượcđồngý; annotators label biểu cảm, agreement | Subject-disjointtrain/val/test; soheuristic/MLP/ensemble/logistic cùngsplit | MacroF1=(ΣF1c)/K; confusion/support; không diễn giải sức khỏe tâm thần |
| Rehab | Videođồngý;2người đếmmanual, pose/repform tiêu chí cố định | Đủ3bài/góc/occlusion/FPS; freeze thresholds; pause/unplug/mấttracking | MAEcount=mean|pred-gt|; jointangleerror với chuẩn nếu có; completedfalsepositive/negative; không clinicalefficacy |
| STT | 30–50WAVtiếngViệt thật3–10s cóconsent/transcriptchuẩn | Splitngười/phrase, noiseTV/quạt/phủđịnh; freezeVAD/beam/model | WER=(S+D+I)/Nword;CERtươngtựchar; báo normalization và zero-length denominator; p50/p95,cold/warm |
| Intent | Syntheticreviewed102acceptance giữtách48tune; goldintent/context | Khóa prompt/schema/policy; trước chạy verifyquota/free/privacy; nohandler trongmodelbenchmark | Accuracy/macroF1 riênglocal/cloud; JSONsuccess; unsafeactionrate; blocked/unknowncoverage; nrequest/error429 |
| Appwebsync | DBgiả3devices/browsers; clocksmonotonic/correlationID | Instrumentt0commit,t1relay,t2SSE,t3fetch,t4render; disconnect/revoke/offline/restart | p50/p95/p99,successrate,duplicateevents,outboxlag; phân biệtqueue vsrender vsSMTP |
| Resource/concurrency | Thiết bị đích cómodel/mic/camera; dữliệugiả | Camera baseline rồiSTT+TTS+web; repeatedcancel/contextswitch/shutdown | FPSdistribution,CPU/RSSpeak/VRAM,responseUI,leakedworkers/mic,30phútstress |
| Packaging | WindowscleanVM,SQLfixturegiả,lockeddeps | Freshinstall/buildEXE/installer/offline launch/modelpath/DLL/TTS | Checksecretbinary,license,rollback,missingDLL; chưa có kết quả hiện tại |

Mọi humanrecording cần đồng ý, nguồn dữ liệu rõ, xử lý tối thiểu, retention/deletion và báo cáo aggregate. Free-tier cloud chỉ syntheticreviewedneutraltext phù hợpgate; không gửihealthrecords thật hoặc coi ẩnID là anonymization. Kế hoạchthínghiệm không phải bằngchứng đã thử trên người.
''', [f'C{i:02}' for i in [8,9,11,12,18,19,20,21,25,28,29,32,41,42,45,49,50,51,52,53,54,55]])

doc('07_DEVELOPMENT_HISTORY.md', r'''
# Lịch sử phát triển có chứng cứ

## Nguồn và mức tin cậy

git log hiện có hai commit ngày30/09/2026: c6aafea(feat,v3.0MVP) và ebcdcbb(updateREADME). Têncommit là mô tả tác giả, không chứng minh hoàn thiện mọi chức năng. Worktree hiện chứa nhiềufilemodified/untracked, nên không gán toànbộpipeline mới vào mộtcommit hay dựng thời gian từng thay đổi. source_snapshot.json giúp đóng băng snapshotkiểm toán, không là releasehashđãpublish.

## Các chuyển đổi quan sát được

| Giai đoạn/record | Quyết định và chứng cứ | Trạng thái hiện tại / giới hạn |
|---|---|---|
| Face/emotion/rehab standalone vàlauncher | Modulefolder vàadapter integration | Dashboardactive LBPH/3classexpression/FSM; không dùng standaloneagegender làm identity |
| Fall/HFD/video experimentation | core/fall_*,modules/fall,archive/fall_detection,reportcandidate/fusion | DEPRECATED theo dashboardcameraactive; videotool retained; không thêm vào productcurrentdiagram |
| Chuyển trọng tâm thuốc | planmigration,services/medication_migration,medicationreport | Legacyservice cótest nhưng Dashboardpanel=None; activeTodayTodo dùngunifiedDB |
| Thống nhất DB/realtime |4migrations,connection/importer,outbox/SSE | IMPLEMENTEDphạm viDBtest; games/emotionlive vẫn chưa hoàn toànunified |
| GỡAPI STT | plan/KE_HOACH_GO_API_STT.md,router410,factorydisabled,archivevoice | REMOVEDactiveAPIpipeline; không nói everyproviderfile đãxóa |
| STT local09/10 theo report | services/local_voice,requirementslocks,local_sttREPORT | IMPLEMENTEDfileinference/lifecycle; physicalmic/camera/GPUacceptance còn thiếu |
| Nút nhận giọng hiển thị | Dashboard/LocalVoiceWidget,ui-visible-smoke | IMPLEMENTEDoffscreen; clickđầu loadworker nếu chưa có, không listenbackground |
| Gemini text09/10 theo report | services/transcript_intent,backend/client/SDK,limited-live-benchmark | PARTIALLY_IMPLEMENTEDfeature; productioncloudfalse vàfree-tiergatecatalog |

Ngày09/10 từ headingreport/records, không phải timestampcommit đãxác minh độc lập. Kế hoạch mô tả điều dự định làm; report+source/test mới hỗ trợ điều thực sự đãcó. “API STT removed” khác “Gemini text classification”: model nhận textneutral, khôngnhậnaudio. [C23/C28/C35/C36/C40–C43/C48/C54]

## Những cải tiến có bằng chứng và bài học

PyAV19 có lỗi tương thích trong reportSTT; pin18.1.0 được cleaninstall/transcribe kiểm tra. Bảndevpatched không dùng làm bằngchứngreproducibility; lockLinux vànewcleanenv hữu ích nhưng chưathayWindows nghiệmthu. [C25/C49]

Nativeaudio import từng làm testtimeout. Config/serviceslazy hạn chếsideeffectbackend; smokeQt vẫnmock sounddevice/camera. Đây là cải tiếnboundaryimport, không chứng minhPortAudio được cài vàmicrothật. [C01/C02/C49/C54]

SDK deadline8s bịprovider400 khi minimum10s; adapter dùngtransport≥10s và totalclientwait≤8s. Recordschema-probe.json giữfailure,limited-live-benchmark giữ3success. Bài học: importSDK hay JSONsuccess không chứng minhquota, privacy, stalecontext hoặcbusinessE2E. [C31–C33/C53]

Rule/schema/context và privacygate được viết trước/độc lập model. Existingtests phủcasephủđịnh/unknown/cancel/đổipatient/duplicate/HTTPauth; aggregateofflinecoverage70.59% choacceptance vẫn thấp. Không mô tả mọiparaphrase tiếngViệt đã hiểu nhờLLM. [C27–C33/C52]

## Điều lịch sử không thể khẳng định

Không có lịch sử commit đầy đủ cho currentworktree, changeauthor/time từngfile, chứng nhậnrelease, fieldtrial, thôngsốcalibration hoặc mộtchuỗi thínghiệm người thật. Không suy ramoduleweightsource/trainingprovenance từfilename; không kể clinicalimprovement hoặc noveltyproof từmarketingREADME. [C55]
''', [f'C{i:02}' for i in [1,2,6,10,14,23,25,27,28,31,32,33,35,36,40,41,42,43,48,49,52,53,54,55]])

doc('08_KHKT_REPORT_MAPPING.md', r'''
# Ánh xạ bằng chứng vào báo cáo KHKT THPT

## Nguyên tắc viết

Phần này cung cấp vật liệu kỹ thuật, không tự dựng động cơ cá nhân, khảo sát cộng đồng, thí nghiệm trên người hay tính mới khoa học. Status phải giữ đúng phạm vi từmanifest. Mã có thuật toán không tự chứng minh accuracy; mock/seed không thay nghiệmthu thiết bị. Screenshot hiện có chứa hồ sơ/thuốc nên không đưa vào báo cáo công khai trước tạo bản synthetic/anonymized phù hợp, xóa tên/liênhệ/healthtext thật; chỉ che ID chưa đủ. [C49–C55]

| Mục KHKT | Bằng chứng và file liên quan | Status phạm vi | Sơ đồ/ảnh phù hợp | Thiếu và trọng tâm đề xuất |
|---|---|---|---|---|
| I.1 Lý do chọn đề tài | Chức năngUI/services tạiapp/dashboard.py vàtoday_todo_widget.py [C02/C20] | IMPLEMENTEDUItest; độngcơxãhộiUNKNOWN | Systemarchitecture01 | Cần sốliệunhu cầu/tài liệu/xuấtxứkhảosát; mô tảbàitoán hỗ trợ thao tác |
| I.2 Ý nghĩa khoa học/thực tiễn | Hìnhhọc/FSM/voice/context [C14–C19/C24–C33] | IMPLEMENTEDthànhphần; lợiíchlâmsàngUNKNOWN | Dataflow01 | Cần usability/fielddata; nhấnứngdụngkỹthuật, khôngchẩnđoán |
| I.3 Mục tiêu | Snapshot nănglực vàlimitations00 [C51–C55] | PARTIALLY_IMPLEMENTEDtoànhệthống | Ma trận00 | Mục tiêu đo được vàtiêuchí nghiệmthu, khôngthànhquả đãđạt |
| I.4 Đối tượng/phạm vi | Patientbinding,3roleportal,DBschemas [C04/C38/C44] | IMPLEMENTEDguardtests; toànUXPARTIAL | Component/ERD | Xácđịnhngười dùng/địađiểm/consent; nofree-tierhealthrecords |
| I.5 Phương pháp nghiên cứu | Testsource,benchmarks,trainingcode [C12/C51–C54] | IMPLEMENTEDtestartefacts; missinghumanstudyUNKNOWN | Bảngthínghiệm06 | Tách thiết kế/kiểmthử/phươngphápchưa làm |
| I.6 Tính mới/sáng tạo | TíchhợpCV+STT+allowlist+transaction/context [C18/C27/C30/C43] | IMPLEMENTEDmộtsốintegration; noveltyUNKNOWN | Component01 | Cần priorart/comparison; trìnhbàyđónggópgói tíchhợp, không tuyênbố phátminhLBPH/Whisper |
| II.1.1 Cấu tạo chung | Entrypoint/desktop/backend/web [C01/C02/C40/C42] | PARTIALLY_IMPLEMENTEDtoànchuỗi | Systemarchitecture01 | TáchsharedSQLite/DBgames/JSON; flagGeminitắt |
| II.1.2 Thiết kế chi tiết | Recorder/engine/worker/controller/dispatcher [C24–C33] | IMPLEMENTEDcontract/lifecyclemock | Component01 | Boundarythreads/context/privacy/auth |
| II.1.3 Sơ đồ nguyên lý | frame/audio→rules→handler→DB/outbox [C14/C25/C27/C42] | IMPLEMENTEDsubflow; E2EPARTIAL | Startup/dataflow/maininteraction01 | Khôngvẽemotion→DB nếuchưanối |
| II.1.4 Tổng thể sản phẩm | Desktoptabs/portals/spec/setup [C02/C38/C49/C50] | PARTIALLY_IMPLEMENTEDđónggóimới | UIảnhsynthetic cầnchụplại | Khôngdùngảnhproduction/khẳngđịnhWindowsbuildpassed |
| II.2 Phần mềm/xử lý dữ liệu | Preprocessface/emotion/PCM,DBDDL [C07/C11/C24/C40/C41] | PARTIALLY_IMPLEMENTEDtrainingprovenance; IMPLEMENTEDDDLtest | ERD05/equations03 | Đầu vào/chấtlượng/datalifecycle/retention |
| II.3 Thiết kế/lập trình | Python/PyQt/stdHTTP,dependencylocks,services [C01/C49/C50] | IMPLEMENTEDLinuxinstall; WindowsPARTIAL | Module tree01/stack02 | Phânbiệtmanifest/lock/runtime; khônggiảđịnhFastAPI/Postgres |
| II.4 Nguyên lý từng chức năng | Algorithmdetail03/workflow04 [C06–C39] | Theo từngmodule00/manifest | FSMtable03/workflow04 | Selfreportthuốc,qualitycount,unknownintent,limitations |
| III.1 Thử nghiệm/cải tiến | PyAVpin/importsideeffects/deadlinefix/history [C25/C31/C49/C54] | IMPLEMENTEDscopeartefacts | Comparison06/07 | Ghi thấtbại/tập/môi trường, khôngkể thínghiệm chưa chạy |
| III.2 Thử nghiệm tổng thể | HTTP66ms,mockQt/SSE,3SDKcases [C33/C42/C53/C54] | PARTIALLY_IMPLEMENTEDrealE2E | Testmatrix06 | Thiếu mic→camera→DB→3browser/emailreal; khônggọimockfullsystem |
| III.3 Hoàn thiện | Baselinefailure/caps/offline/fallback [C32/C43/C54/C55] | PARTIALLY_IMPLEMENTED | Checklist09 | Securitypublicpassword/auth,loopmed,syncemotiongame,physicalstress |
| IV Kết luận | Summary00 vàmeasured06 [C51–C55] | Nguyênmẫucócode/tests; fullvalidationUNKNOWN | Bảngstatus00 | Kếtluậnđúngphạmvi, khôngclinicalefficacy/accuracyinvented |
| V Hướng phát triển | Missingchecklist09/experiments06 [C21/C45/C47/C55] | PLANNEDchoPostgres; đềxuấtkhácchưa thực hiện | Timelineđềxuất ghi rõproposal | Ưutiêncorrectness/privacy/E2E trướcmodelmới |
| VI Tài liệu tham khảo | Source/manifest,existingreports vàupstreamdoclinks | Nguồnsourceđãđọc; nguồnwebchưaxácminhlại | Khôngcầnảnh | Ghi version/ngàytruycập đúng; kiểmtra bảnquyền/nguồnweight |

## Mẫu diễn đạt có thể dùng

“Nguyên mẫu sử dụng LBPH của OpenCV để so khớp ảnh khuôn mặt đã đăng ký; ngưỡng distance58 và cơ chế làm mượt được cài đặt trong mã. Nghiên cứu chưa thu thập đủ dữ liệu để xác lập FAR/FRR trên nhóm người dùng độc lập.” [C06–C09/C55]

“Các bộ đếm phục hồi được kiểm thử bằng landmark tổng hợp. Trạng thái hoàn thành được tạo khi số lần ghi nhận đạt mục tiêu snapshot; hiện còn cần kiểm chứng điều kiện chất lượng từng lần và góc camera thực tế.” [C15–C19]

“Ứng dụng lưu xác nhận uống thuốc do người dùng tự khai báo, dùng chung service/idempotency cho nút tay và voice. Bản ghi không là bằng chứng khách quan người dùng đã uống thuốc.” [C20/C27]

“Lớp Gemini đã có code và smoke text trên ba câu tổng hợp; mặc định cloud tắt và chỉ catalog trung tính được phép gửi. Chưa nghiệm thu toàn bộ tập acceptance và luồng micro tới giao diện web.” [C28–C33/C53/C55]

## Nguồn tham khảo kỹ thuật cần đối chiếu khi viết bản cuối

Nguồnrepo: main.py,adapters,rehab_engine.py,services/local_voice,services/transcript_intent,database/migrations,web vàreports/* trongmanifest. Nguồnupstream đã được hướngdẫn hiện có trỏ tới: https://docs.opencv.org/ ; https://ai.google.dev/edge/mediapipe/ ; https://github.com/SYSTRAN/faster-whisper ; https://opennmt.net/CTranslate2/ ; https://github.com/googleapis/python-genai ; https://ai.google.dev/gemini-api/docs/structured-output ; https://ai.google.dev/gemini-api/docs/rate-limits ; https://ai.google.dev/gemini-api/terms ; https://www.sqlite.org/wal.html . Audit không truycậpweb lại; không ghi ngày“đã đọc online” hoặc thuật ngữ/giá/quota hiện hành như đãverify. Cần thêm tài liệu khoa học và khảo sát priorart để hỗ trợýnghĩa/tínhmới, không chỉ thưviệnsoftware.
''', [f'C{i:02}' for i in [2,4,6,7,9,12,14,18,19,20,21,24,25,27,28,30,31,32,33,38,40,41,42,43,44,45,47,49,50,51,52,53,54,55]])

doc('09_MISSING_EVIDENCE_CHECKLIST.md', r'''
# Checklist bằng chứng còn thiếu

Đây là công việc đề xuất sau kiểm toán, chưa được thực hiện hoặc tự động cấp quyền vận hành trên dữ liệu thật. Ưu tiên theo nguy cơ sai kết luận/sai action/privacy trước số lượng tính năng.

## P0 — phải giải quyết trước demo với hồ sơ thật

- [ ] Rà soát và sửa publicquick-accounts trảpassword, authdemo bypass/hint/plaintext, hồ sơJSONpassword; thêm mật khẩuhash thực và regressionauthdeny. Cần báo cáofix/test, không chỉ đổi nhãn trườngpassword_hash. [C45/C56]
- [ ] RedacttokenURL/log, kiểm soát publicpatientlist, HTTPS/configsecrets, backupencryption/access/retention. Tạo dữliệugiả cho ảnhdemo/report; không publishDB/dump/audio thật. [C46/C50/C56]
- [ ] Định nghĩa điều kiện camera_verified_completed: nguồnframe thật, khôngsimulated/stale, chấtlượngrep, visibility/quality_threshold; nghiệmthu cameraunplug và race nhiềuwriter. [C03/C18/C19]
- [ ] Xác minh activeMedicationScheduler: sinhlịch sau4ngày, reminderTTS, snoozetimed/overdueSNOOZED,timezone vàjoinrevision. Kiểmtratắtbackend/app, mấtmạng/restart và thôngbáohỗtrợ khôngkhẳngđịnhđã nhận. [C20–C23]
- [ ] Kiểmtrachọnpatient/unknownface/fallbackfirstACTIVE/syncclientbinding với núttay, queuecũ vàvoice; chứngminh khônghànhđộngnhầmngười. [C04/C20/C27/C43]

## P1 — bằng chứng kỹ thuật cần cho nghiệm thu tổng thể

- [ ] Thiết bị đích và cấu hìnhOS/Python/driver/audio/CUDA/modelrevision có record; physicalmic stop/cancel/overflow/duration/shutdown, loaTTS vàecho. [C24–C26/C34/C49/C55]
- [ ] Bộ30–50samplegiọngViệt đượcđồngý, nguồn/transcriptgold, tách tune/test; WER/CER/latencycold/warm/E2E; không dùng4scratchWAV làm nghiệmthu. [C25/C51/C55]
- [ ] ChạycameraCVđồngthờiSTT/TTS, FPS/RAMpeak/CPUUIlatency baselinevsvoice; stresscancel/đổipatient, kiểmtraworkermic đượcrelease. [C03/C05/C26/C51]
- [ ] Đường cameraemotion→unifiedDB→web nếu là mục tiêu; không dùng seedrows; gameSQLite→liveunified hay ghi rõ giới hạnreporting. [C13/C39/C41]
- [ ] Benchmark3browser/devices thật, t0commit→t4render, disconnect/reconnect/revoke/timezone, sốevent vàsuccess/duplicates. SMTPmailboxsynthetic được cho phép riêng, receipt/delivery không dùngmock thay. [C42–C44]
- [ ] Chuẩn hóafixtureseed: không importhồsơ thật vào in-memorytests, testorder/isolation, baseline6fail vànativeaudio timeout; ghi đúnglệnh/env/commit/sourcehash cho mỗi lần. [C09/C41/C54]
- [ ] Windowscleaninstall/buildEXE/installer/modelpath/PortAudio/CT2DLL/TTSchild, binarysecret/license audit. [C49/C50]

## P1 — nghiệm thu Gemini có giới hạn

- [ ] ProjectID,modelavailability,free-tierbilling vàRPM/TPM/RPD thực từAIStudio; nguồnchứngcứđãredact, caps theoquota, khôngtựbậtbilling. [C28/C32/C53]
- [ ] Secretbackend ngoàiapp/repo; provisioning/sessionrefresh elderdevice, revoke/expiry/restart backend. [C33/C44/C50]
- [ ] Full102syntheticacceptance khóa khỏi48tune; prompt/schema/modelversion cốđịnh; đo accuracy/macroF1/schema/unsafe riênglocalvscloud, ghi timeout/429/quota sửdụng. [C29–C32/C52/C53]
- [ ] E2E mic→Whisper→local/cloudgate→confirmation→DB→web bằngfixturegiả; cloudtắt/offline429/response muộn, khôngcopyhealthrecord thật. [C27–C33/C55]

## P2 — bằng chứng nghiên cứu khoa học

- [ ] Faceholdoutsubject/session/unknownliveness, thresholdcalibration, FAR/FRR vớiNimpostor/Ngenuine vàkhoảngtincậy. [C06–C09/C55]
- [ ] ExpressionCSV/splits/trainingprovenance/checkpointhash, subjectdisjoint, annotatoragreement, baseline/MLP/heuristic/ensemble3classevaluation. Khônggắnnhãnchẩnđoán. [C10–C13/C55]
- [ ] Rehabgroundtruthrep/form/angle, angle2Daspectratio/cameraview, errorcompleted; nếu nghiêncứuefficacy phải cóđềcương/chuyêngia/ethics vàthửriêng. [C14–C19/C55]
- [ ] Usability trênngườidùng đượcđồngý: tasksuccess, thời gian, lỗi, font/nút/voicefallback; khôngtựdựng số người hoặc khảo sát. [C02/C38/C55]
- [ ] Priorart/literaturereview, so sánhgiải pháp hiện có vàđónggópriêng; bằngchứngnguồn/license mọiweights/ảnh/nhạc; khôngclaim thuậttoánthưviện làsángchếmới. [C49/C55]

## P3 — hướng mở rộng, không coi đã triển khai

- [ ] PostgreSQL/multihostqueue/quotalimiter/observability khi cần; thửmigration thật, khôngdựaANSIcomment. [C40/C42/C47]
- [ ] Cácintent mới chỉsauhandler/policy/schema/auth/confirmation/privacy/test; không mở free-tiertexthealth tùy ý. [C27–C33]
- [ ] Lập releasebaseline commit/hash, changelog, reproduciblefixtures và nhật kýđo cótimestamps/environment. [C49/C54]

## Hồ sơ tối thiểu cho mỗi thí nghiệm

Ghi objective,sourcehash/modelhash/promptversion,OS/Python/dependency/hardware,consent/sourceinput,split/goldlabels,commandexact,seed/config,rawaggregateoutput,error/skippedcases,mock/externaltraffic và limitations. Báo cáo khoa học chỉ lấy số cóartefact đó; phầnchưa làm giữ PROPOSED EXPERIMENTS/UNKNOWN. validation_report.json của kiểm toán này chỉ kiểm tài liệu/source, không đóngcáccheckbox bêntrên.
''', [f'C{i:02}' for i in [2,3,4,5,6,9,10,13,14,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,38,39,40,41,42,43,44,45,46,47,49,50,51,52,53,54,55,56]])

# Findings discovered while checking source test assertions and auth boundaries.
DOCS['00_EXECUTIVE_SUMMARY.md']=DOCS['00_EXECUTIVE_SUMMARY.md'].replace(
    '| FSM ba bài tập với landmark tổng hợp | IMPLEMENTED | C15–C17; không phải clinical trial |',
    '| FSM ba bài tập với landmark tổng hợp | PARTIALLY_IMPLEMENTED | C15/C16 chỉ test chuyển state; C17 test một bước marching; chưa trọn chu kỳ/người thật |')
DOCS['00_EXECUTIVE_SUMMARY.md']+='\nPublic quick-accounts còn trả password. Endpoint rehab-event chưa kiểm tra ownership của session so với patient URL; nguồn camera được gán metadata chứ không xác thực. Đây là phát hiện source, không là kết quả thử khai thác. [C56/C58]\n'+evidence(['C56','C58'])
DOCS['04_FUNCTIONAL_WORKFLOWS.md']+='\n## Boundary bổ sung cần nghiệm thu\n\nAPI rehab-event chỉ qua permission view, handler tăng count theo body và chưa đối chiếu session.patient_id với patient URL. Vì vậy API ngoài đường camera có thể ghi nhãn camera_verified_completed; phải kiểm tra quyền write/ownership và nguồn event trước sử dụng dữ liệu thật. Web chart còn có dải tham chiếu hardcode, chưa chứng minh cá nhân hóa/validation lâm sàng. Không dùng nhãn “an toàn” trên UI làm chứng cứ y tế. [C57/C58]\n'+evidence(['C57','C58'])
DOCS['05_DATABASE_AND_SYNC.md']+='\n## Ghi nhận quyền ghi còn thiếu\n\nApiRouter._handle_rehab_event nhận session_id từ body, query session không ràng buộc patient_id rồi tăng count. Route patient-specific hiện chỉ yêu cầu view cho resource này. Guard patient URL không tự chứng minh quyền sở hữu session; cần negative test cross-patient và nguồn camera. Audit không thực hiện request hay khai thác. [C58]\n'+evidence(['C58'])
DOCS['06_TESTING_AND_EVIDENCE.md']+='\n## Giới hạn assertion FSM và tham chiếu sức khỏe\n\nTest nâng tay và đứng-ngồi trong test_rehab_assistant chỉ đưa một input landmark rồi assert trạng thái; chưa đo đủ chu kỳ rồi xác minh rep/hold/penalty. Test marching assert đúng một step. Báo cáo không gọi 17passed là độ chính xác đếm thực tế. Các dải “an toàn” hardcode trên web cần chuyên gia/tài liệu và cá nhân hóa riêng, không lấy UI làm ground truth. [C15–C17/C57]\n'+evidence(['C57'])
DOCS['09_MISSING_EVIDENCE_CHECKLIST.md']+='\n## Negative tests ưu tiên bổ sung\n\n- [ ] Rehab API write authorization, cross-patient session ownership, attestation nguồn camera và server validation của rep/score. [C58]\n- [ ] Health charts: nguồn tham chiếu, đơn vị, calibration/validation và cá nhân hóa; không mặc định mọi ngưỡng UI là chỉ định y tế. [C57]\n- [ ] FSM nâng tay/đứng-ngồi đủ chu kỳ, hold, visibility, pause và FPS để kiểm chứng count; hiện unit tests mới kiểm tra bước trạng thái. [C15/C16]\n'+evidence(['C57','C58'])

# Add full column dictionary to Markdown so the master is self-contained.
dictionary='\n## Phụ lục mọi cột và constraint khai báo\n\n'
for t in SCHEMA:
    dictionary+=f"### {t['table']} [DB_{t['table']}]\n\n| Cột | Kiểu SQL | Constraint/default khai báo |\n|---|---|---|\n"
    for c in t['columns']:
        dictionary+=f"| `{c['name']}` | `{c['type']}` | {c['constraints'].replace('|','\\|') or '—'} |\n"
    dictionary+='\n'
DOCS['05_DATABASE_AND_SYNC.md']+=dictionary

# Improve prose readability without changing literal source paths or symbols.
substitutions={
    '3classexpression':'biểu cảm 3 lớp','standaloneagegender':'age/gender độc lập',
    'CPUint8':'CPU int8','CPUsmall/int8':'CPU small/int8','cloudfalse':'cloud=false',
    'clouddefaultfalse':'cloud mặc định false','cloudtắt':'cloud tắt','clouddisabled':'cloud disabled',
    'physicalmic':'micro vật lý','cameraunplug':'ngắt camera','nativeaudio':'native audio',
    'mic/camerađồngthời':'mic/camera đồng thời','bằngchứng':'bằng chứng','nghiệmthu':'nghiệm thu',
    'phạmvi':'phạm vi','toànrepo':'toàn repo','lâmsàng':'lâm sàng','trênngườidùng':'trên người dùng',
    'ngườidùng':'người dùng','đãverify':'đã verify','chưaxácminhlại':'chưa xác minh lại',
    'codecameraactive':'code camera active','dashboardactive':'dashboard active',
    'confidenceface':'confidence face','qualitythreshold':'quality threshold',
    'sourcehash':'source hash','modelhash':'model hash','promptversion':'prompt version',
    'đúngphạmvi':'đúng phạm vi','báocáo':'báo cáo','khôngchẩnđoán':'không chẩn đoán',
    'modelaccuracy':'model accuracy','tựkhai':'tự khai','thuộc3':'thuộc 3',
    'người thật':'người thật', 'cameraemotion':'camera emotion','loacal':'local',
    'đãđượcđồngý':'đã được đồng ý','đượcđồngý':'được đồng ý','chưađược':'chưa được',
    'toànhệthống':'toàn hệ thống','toànchuỗi':'toàn chuỗi','toànapp':'toàn app','khảosát':'khảo sát',
    'tínhmới':'tính mới','đónggóp':'đóng góp','cảithiện':'cải thiện','camerathật':'camera thật',
    'dữliệugiả':'dữ liệu giả','dữliệu':'dữ liệu','thínghiệm':'thí nghiệm','thửnghiệm':'thử nghiệm',
    'lợiích':'lợi ích','tổnghợp':'tổng hợp','đồngbộ':'đồng bộ','quyềnwrite':'quyền write',
    'ngườithamgia':'người tham gia','clinicaltrial':'clinical trial','clinicalefficacy':'clinical efficacy',
    'quality_threshold':'quality_threshold','modelquota':'model quota','giọngViệt':'giọng Việt',
    'tiếngViệt':'tiếng Việt','ngườithật':'người thật','camkết':'cam kết','tựđộng':'tự động',
    'tựdựng':'tự dựng','tựtạo':'tự tạo','ngườiunknown':'người unknown','mọifixture':'mọi fixture',
    'từngfile':'từng file','mọiweights':'mọi weights','máyđích':'máy đích','từngrow':'từng row',
    'phủđịnh':'phủ định','ngậpngừng':'ngập ngừng','tài liệuđối':'tài liệu đối',
    'dải thamchiếu':'dải tham chiếu','đổi/người':'đổi/người','ảnhproduction':'ảnh production',
    'fullsystem':'full system','fullvoice':'full voice','modelaccuracy':'model accuracy',
    'standalone/JSONtrênhost':'standalone/JSON trên host','máy Internet':'máy Internet',
    'khôngthiếtbị':'không thiết bị','đườngdữ':'đường dữ','highconfidence':'high confidence',
    'khôngclinical':'không clinical','tênstate':'tên state','khôngPOST':'không POST',
    'bảnphát':'bản phát','thànhphần':'thành phần','chuyêngiagia':'chuyên gia',
    'ngườicũ':'người cũ','chuyêngia':'chuyên gia','productionrows':'production rows',
    'seedrows':'seed rows','realE2E':'real E2E','synthetictext':'synthetic text',
    'mockSDK':'mock SDK','mocksounddevice':'mock sounddevice','fakeSMTP':'fake SMTP',
    'nhạcpause':'nhạc pause','nghiệmthuphầncứng':'nghiệm thu phần cứng',
    'sourceUI':'source UI','source/test':'source/test','logpytest':'log pytest',
    'modulefolder':'module folder','reportGemini':'report Gemini','reportSTT':'report STT',
    'codedashboard':'code dashboard','purelysynthetic':'purely synthetic','khôngnative':'không native',
    'capslocal':'caps local','latent':'latent','không đọc/copy':'không đọc/copy',
}
for name,body in list(DOCS.items()):
    for old,new in substitutions.items():body=body.replace(old,new)
    DOCS[name]=body

# Separate compact notes into normal Vietnamese prose. Preserve code, URLs and paths.
vietnamese_words='''ai an ảnh áp bài ban bảng bao bản báo bắt bất bên biết bình bỏ bộ bởi bớt ca các cái cài cả cách camera cảnh cân cần cao cá cá nhân cặp câu chỉ chi chiều cho chủ chuỗi chuẩn chưa chuyền chuyển chuyên chứng cùng cung cấp cụ cũ cơ cơ cấu cấu càng có còn cộng con công cổng cột cờ của chỉnh chặn chất cha chụp chống chờ chế chạy chính cuối cập cảm dải dạng danh dành đầu đáy đặt đạt đây đầy đều để đếm đến đề điều điểm định đọc đôi đổi đối độ đóng đúng đủ được đích đi đo đời đồng đồ đã đơn dữ dụng dùng duy đó đưa đường lỗi lặp lệnh lại là làm lớn lên lớp liệu lưới lần lập lượng lý mã máy mẫu mặt mạng mạnh mất mẹ mệt mới một mọi mốc mục mua mỗi mở mức ngắn ngày người nguồn ngưỡng ngoài ngay nghe ngầm ngang ngăn nhận nhãn nhà nhỏ nhắc như nhất nhiều nhóm nhập nhớ nhấn nữa nửa nơi nội nói nó nối nên nào này nguy nằm phải phần phù phụ phủ phố phép phía phạm qua quả quá quạt quyền quy khớp khoảng khác khi khó khóa không khả khảo kết kiểm kiểu khẳng khung khám kỹ kéo giữ gói gọi gốc ghi giới giả giữa giúp giây giờ giọng giáo gộp gán gồm giao gợi hình hay hiểu hiện hạn hàng hàm hợp hỗ hồ hồi hôm hết hơi theo thì thêm thử thực thu thuộc thuần thuốc thể thước thời thôi thí thiện thiết thấp thứ tham thần thành thông thi thiếu thức tính tin tỉnh trên trước tránh từ tự tới tập tắt tách tạm tâm tạo toàn tổng tốt tròn trong trùng trọn trí trừ tiếp tuổi từng tay thế trị trình tuân tuần toàn tăng truyền tương tĩnh vẽ về ví vì với và việc viết vị vừa vận vẫn vậy vùng vốn vui Việt vị trí xác xóa xem xuất xuống xử xứ xét xoay ý yêu yếu ứng ẩn uống ưu ước y khoa sàng lâm hiệu ích mới nhất xấu dạng nghĩa năng lực kết luận tiên lệ sách sửa sai giãn rủi ro giả mất biển stress hệ thống tính nhạy sao lần lượt nguồn thật raw triển khai đạt số lượng cảnh thân sát nhân phiên hoàn ô thay thế rất chạy ngừng ngập khuỷu gối sáng tối nghiêng trái phải lòng mềm tức rời chỗ ràng buộc đầy đủ hỗ trợ đọc lâu dài mật khẩu rõ nào tuổi tưởng chỉ tiêu giả lập nghiêm trọng điểm nền nghiệp hoạt động song đảm bảo hài lòng chiếu xương khớp xếp hạng thử riêng mới thay ánh nhu cầu tần suất rèn luyện công cộng nguồn bệnh mẹ cha tác vụ cứng mềm cộng đồng lần hình đồ chung riêng dễ khó lợi ích khoa học thực tiễn mở đầu nội dung kết quả hiệu quả trung tâm tham khảo ảnh chụp sơ đồ nguyên tắc nhân tạo sáng chế giám sát nhấn phím dừng hủy nút bấm'''.split()
english_words='''active actual aggregate alias allowlist angle ankle app application architecture arm assert audio auth authentication authorization baseline backend beam billing binary binding blob body bound bounded box break browser build callback calibration camera cancel cancelled captured capture care case cases catalog cell char check child class classes classification clean client clinical code cold column completed completion component concurrency confidence config configured confusion consent constraint constraints consume context contract correct count counter counters coverage cpu create cuda data database date deadline decode default delay delivery deny deprecated descriptor detector device dialog dictionary disabled dispatcher distance distribution dll double driver dropout dump duplicate effect elder email encoder end enforced engine ensemble enum epoch error event events example exercise expert expression extra face fail failed failure fake fallback family feature features field file files finish fixture flag floor form fraction frame frames freeze frozen full function games gender generator genuine global gold gpu grace graph ground grounding groundtruth guard handler hardware hash health help heuristic high history hold home host http identity idle image impostor import imports in inbox inference input install integration intent internet invalid invalidate json joint key landmark landmarks latency latest legacy level limiter linux live load local lock log logits loop lost low macro manager manual map match measured measurement media metadata method microphone migration minimal mock mocked model monitoring mono multiple multilingual name native navigation negative network neutral no normalized notes notification null numpy objective offline on once onnx optional original out output overflow outbox overlap ownership padding panel partial path patient patientbinding pause peak penalty permissions phase phrase pin plan playback point policy pose post prefix primary privacy probability process processed profile prompt proposed provenance public python qt quota radius raise raising ram random raw read receipt recognition record records recorder ref reference registration regression rehab reliability reminder remove render report repository request required reset response resume retention retry revision rollback roi route router routing rss rule rules runtime safe sample scale schema scope score sdk secret seed segment semantic sequence server service session shared shutdown signal silent simulated simulation single sit sitting size slot smtp snapshot snooze softmax source split stage stale stand standalone start state stop store stream stress strength string subject summary surrogate switch sync synthetic table target task temporal test tested text thread threads time timed timeline timer timeout token total train training transaction transcript transport true ttl tune tuning tv type ui unavailable unique unit unknown unsafe update user uuid val validation value vector verified version vertex visibility voice voices wal warm wav web weight weights wheel window windows worker writer x y z zero PyQt5 QApplication QThread QTimer Pydantic JSON SQLite PostgreSQL OpenCV MediaPipe CTranslate2 PyAV PortAudio WhisperModel faster whisper sourcecheck typecheck tempfile false implemented partially planned deprecated removed unknown MAE FAR FRR WER CER FPS F1 EMA SQL IANA UTC GMT HTTPS HTTP SSE SDK API DB MVP THPT KHKT FROM WHERE ON JOIN ARGS max min p50 p95 p99 n mean sum void precision recall tuningtest null right left pyttsx3 NumPy SciPy Python Torch Torchvision torchvision sys argv stdlib falsepositive false negative no such tkinter medical human trial normative person sigma radius minsize quality threshold pretrained stopwords spelling casefold rawmatch visualize screenshot selfreport selfreported self reported already posttest camera_ai aggregate_version one_many session_id patient_id dose id idempotency client_event_id command_id plan_id snapshotcount syntax structured functioncalling to rate reset chart stats truncate transliterate meanstd syncerrors filelock signalqueue engineonly throughput stateversion module_available vendor biometric compare hardcode hardcoded eye nose muscle mouth shoulder hip knee wrist elbow asymmetric symmetric heldout liveness aspectratio 3D 2D inputsize kwargs additionalproperties enumcheck primarykey group timestamp measured_at recorded_at self_reported_taken instantiate requirements CPU GPU SDK DB UI URL API ID C01 C02 C03 DATA GPIO ONNX CUDA LAN IoT IoTsensor RPD RPM TPM PBKDF2 to stdout stderr offscreen TLS tablecount rowcount system clone copy captureonly five two three second minute horizontal vertical maxoutput tokenizers only millisecond memory inprocess process queue queues core peer clinicalefficacy splitratio LogisticRegression dataflow lifecycle assertions userreceipt got forbidden flagfalse livecases metadata_only SDKwarning WindowsEXE SDKcases HTTPsmoke readonly capture_valid hardware_valid camera_verified_completed incorrect_reps correct_reps quality_threshold amount unit number prescription schedule medication prescriptions schedules doses dose occurrence occurrences implementation implemented partially_implemented existing unverified measured results unknown status diagram mermaid source_code test_source source_path symbol line_range verification_method claim_id confidence limitations full_acceptance_completed quota_verified project_id four readonly real neutralcatalog contextversion user_id hash phiênquery'''.split()
vocabulary={w.casefold() for w in vietnamese_words+english_words}
vocabulary.update(w.casefold() for w in '''minh điển vấn Việt phụ hợp tùy cân xử ưu bày phát thất đích tiêu phù nhớ bại cập thẳng cao ưu biệt giả vốn kiến phẩm động xã hội nhu bàn toán nhịp bệnh lòng sáng xem lâu hạn định nghĩa khi mô tả đáp triển đề rõ cảnh tiết mục bất nhân riêng không lâm sàng y thật đã chưa với đều đối vị trí đường này trạng thái bóng nhiều nửa nước SQL FA FR đầu vào ứng hiện dài bóng mục thứ nhà sáng minh bày suy dụng giới cách người phẩm phía mới nhất môi thì nhỏ diện tâm hoàn nhẹ tung cổ bạn mọi đồng thay ổn giây false true row thời đảm nét nguồn lời nên cùng góp cập tăng ngưỡng query ui fps assert history source input output runtime model engine unknown privacy params handover strict deny allow disabled assert synthetic same folder closure clean cached encoder decoder transcribe router record roles role subflow guard guards analyst fieldworld wording components allocated year date bound boundless dependency dependencies sideeffects dependencylocks evidence module mock transcript transcript_only interpretation implemented assert time independent newest provider audit acceptance passed skipped warning warnings scenario loopback http env os reserve no billing ai studio verified pure sensitive id locked stat color external CPU threads counted dispatch class Macro F1 logits count incorrect correct metric metrics hash manifest signed scope error row_count observations observation failures failure verify atom atomicity fault inject interval default local threshold frames examples public comment comments data records response prompt group latency schemas auth contract clinical source input unit range token storage dictionary clause index transaction true false simulation subject node renderer syntax inference sequential bank prototype setup package packaging pillow psutil ctypes PyPI pipcheck stdout stderr subprocess serialization deserialize landmarks subject baseline parser docs report readonly environment versions skill repo branch affected workflow pathways min max label division cap caps TPM RPM RPD SDKwarning boundary neighbour neighbors aliases textgeneratecontent generatecontent coding after before compound if while allowlist reject unsupported format stop malformed case tuple assignment paper references healthcare functions factory src numpy sigmoid percentile paragraph fallback post partial splitter visual map seed mean random reproducibility overload replacement basic task E2E io cv CLAHE inputrate personal late log dir callback register onset offset metadata_only props registered supported fieldnamed all src tests table tables PK FK DDL ENUM SET RESTRICT CASCADE physiology due host eyes nose hands int int8 radians joint disjoint serialized float clear ttl mocked question numbers amounts SDKcases sizechecks mockstdin music mockaudio clients python3 modelpath DLL fields compoundwords delimiter cursor ids emailname notes name form loss defaults cognitive support split SQLfilter recordtable loss compare protocol hashset queueing grouping testcase tests human readers question validated block output_csv frame_rate integration integrationcase neutral navigation fixture root main flags flagsfalse apps chart simulator actualframes splitname except begin mockasm typed diff freeze full import functional deploy performance observed experiment propose criterion scenarios manual labeling render runtime change overload logmain spec sourcecode sourcefolder binary path names values cache whl dllexclude datascripts license licensing licensevalid licenseproof callable symptom symptoms caregiver recommendation recommendations logline tracing logic textprivacy imagecamera plus minus salt from header whitespace harmless normal dynamic lock lockfile kwargs initializer program buildpackager density generation no one two three chunks batch clinicalefficacy prediction people genuine intruder identity intragroup improve study page citation repository docs reports all holdout release source sdk unsafe bus business base sourcefilename endpoint instruction side effect markup std endif enough all_call sessionstate value exact statistical p95sample ascii stdout native syscall diagnostic referenced human users clinician caregiver appwebsynccorrectness bool framecapture thresholdmodel currentdatetime alias latest names tokenkey shape quality threshold versions configkey authoritative appbuttons engine_ui research passthrough rowcode imagecpu tested renderer intentdetector doctor web family snapshotview consistency recording wait cancel criteria contraindications trace VAD FROM ffmpeg software health care windows framevisible tempo readonly implementation implementationtest cli capability closure correct rejected handshakes surrogate arm shoulder hip mouth eyebrow torso eye instruction num grammar type error quality calibration artifacts artifact licence EMA RSS GB KB MB CPU GPU RAM VRAM UPC direct mock all_root backendservice updater mixed store ISO permission permissions modified untracked stdout args sessionclient wrong positives negatives title timestamp at noop clipboard confirmed confirm dose snooze req view create projection claims artifactfields resolver parallel field reportwrapper sourceguard statement background refetch stmt histogram open quantized sync devices notifications traceback stale camera readonlyassert facephase conditions sequenceplan waveform watermark Wave Channel integer protobuf modelcache testrecords parser tableview fast slow estimate runtimepath expected benchmark source dump statements p95network confusioneval corrected pending reportcontext UserModel AsyncIO sequential qtimer done providerterm noio some independent used template envvar metadata measuredtime detail tagged enrollment enrolled recordlocal written copied parsed itemzone normative planning mockedvalue service_errors anatomy parent child children dedup standby APIAPI tabledata logs updater pureaudio viewrows modulepath mockedenv nativeimport'''.split())
def separate_word(word):
    lower=word.casefold()
    if lower in vocabulary or len(word)<5 or re.fullmatch(r'[0-9a-f]{16,}',lower):return word
    memo={len(word):[]}
    def parts(i):
        if i in memo:return memo[i]
        best=None
        for j in range(len(word),i,-1):
            piece=word[i:j];good=piece.casefold() in vocabulary or piece.isdigit()
            if not good:continue
            rest=parts(j)
            if rest is not None:
                candidate=[piece]+rest
                if best is None or len(candidate)<len(best):best=candidate
        memo[i]=best;return best
    parsed=parts(0)
    return ' '.join(parsed) if parsed and len(parsed)>1 else word

vocabulary.update(w.casefold() for w in '''thuật phương pháp chí trận tích bố địa khẳng toán hướng dẫn viện truy cứu cương gắn chẩn đoán nhầm hành hóa cậy phút gửi hoạch hưởng cần so sánh trả sinh ngay đồng ý thực hiện nghiên cập cảm điều giữa lọc thiếu sau bên đồng khóa bất thư y huyết mạch trước nhờ nhớ ngại thì nếu bộ động thân sắc hồ hẹn chậm giờ có chủ thu đông chịu coi còn cũng đang luôn khi đã chưa khai chữ dùng sàng năm sáu bảy tám chín nếu tầng từ là với thêm đây không đôi đầy đủ đâu mới từng người cho minh được ở trong ngoài tất cả mỗi một đang ngủ mất ô bảo đảm phiên khai thì cả đỏ xanh tím khuyên chặn chất lượng nhịp reference_root role portal ux Gemini Postgres emotion facade algorithm detail equations subflow workflow testmatrix comparison checklist experiments existing reports upstream doc links prior art free tier hard deadline multi med public password decoded clinical mockedtext correctness proposed proof import html css js bytes ms sec GB GHz MB GHz PyPI STT PyAV CV FPS SQL ANSI RPM TPM RPD since case skipped seed synthetic reviewed syntheticreviewed freeze instrument t0 t1 t2 t3 t4 render commit physical property network linked claim snapshot validation consistency parse normalize withhold builder popup confirmation truth pure score ceil learned unavailable count events unsafe root tests source stdout fixture_fixture robust all_fixture_from_source loopback Qt SDK config param agent isolate id count benign pin script micro bound strict schema playground localhost metadata self_reported source_api WER CER acceptance _ffi_support_phrase healthcare_default_sender bench_phrase_question_ignore standby assert_scope symbolic sys_import_break_decode_path false_fingerprint unique sentinel fieldcollection runhistory_data_warn deny_multiple_dose cooldown warm exercise interface references kwargs callbacks anatomy version exported extra_proof mock_proof val_macro metrics_supervised artifact typo simulator_shape seed_trace_file named artifactstate packet use origin older primary whitespace package none scope_gemini sparse timestamp paused raw_sample live_sample coded styles documented reset clock_metric reason_plot derived schemas rerun support_day hash_kind'''.split())
vocabulary.update(w.casefold() for w in '''FastAPI testartefacts artefacts study missing novelty useragent Desktop tabs portal timer matrix strength algorithms preprocess performance guarantee specific example given symptom unit bytes formats body auth_sources namespace exception tuyên phát phân biệt họ cầm root_path mô ngon câu kênh sở xét nghiệm main interaction tree stack fsm dataflow setup timeline proposal UI message input command microphone code generation manifest output active same supported chưa từng được đồng ý tuyên bố thời hạn diễn biến dấu camera provider qdialog overflow nơi nguyên mẫu tư vấn lĩnh vực gửi nhận nghiên cứu tấn công gửi lại nhận lại bảo vệ vận hành lần sau xuống nghiêng chiều tiếp y khoa tham số nhãn mood network offline online ui_queued dose_inline skilllabel sample_env_method dependencies scratch WAV ground_truth statementhealth records_format_dump string_ui normalized_geometry vì sinh'''.split())

def readable_prose(text):
    lines=[];fence=False
    for line in text.splitlines():
        if line.startswith('```'):
            fence=not fence;lines.append(line);continue
        if fence:lines.append(line);continue
        # Markdown literals and URLs/source dotted paths are not human prose.
        spans=re.split(r'(`[^`]*`|https?://\S+|[\w./-]+\.(?:py|md|json|sql|txt|html|lock|task|pth|spec|bin|jsonl|wav)(?::\d+(?:–\d+)?)?|\b[A-Za-z_]\w*(?:\.\w+)+\b)',line)
        for i in range(0,len(spans),2):
            spans[i]=re.sub(r'[A-Za-zÀ-ỹ0-9_]+',lambda m:separate_word(m[0]),spans[i])
            spans[i]=re.sub(r',(?=[A-Za-zÀ-ỹ0-9])',', ',spans[i])
            spans[i]=re.sub(r';(?=[A-Za-zÀ-ỹ0-9])','; ',spans[i])
        lines.append(''.join(spans))
    return '\n'.join(lines)+'\n'
vocabulary.update(w.casefold() for w in '''security game lbph phụ tố kể software tested matrix repair bound root post fake dataflow guard render table tree emotion_graph công sưu chép kỳ quý danh hứa mong đặt sát khám chế mỹ ý kỹ training deadline_warning syncup groupchat secure plaintext triệu cố tiếp giải thích phân tích sinh trắc cửa điều ngắt nghỉ tách chứng minh dừng xử lý đều khó khám đôi tâm đo quyền truy quyết định đủ xử tiêu chuẩn patient_queue actualhash hashes fromtime coldload doseimage rank authority providerquota operator sourceshown failedschema proto_boundary checks field_spec latest reviewed indexed indexes fields identifiers'''.split())
for name,body in list(DOCS.items()):
    body=body.replace('tạiapp/dashboard.py','tại app/dashboard.py').replace('vàtoday_todo_widget.py','và app/today_todo_widget.py')
    body=body.replace('hoặcsit<=118','hoặc sitting<=118').replace('→sit<=118','→sitting<=118')
    body=body.replace('testartefacts','test artefacts').replace('dependencylocks','dependency locks')
    body=body.replace('deadlinefix','deadline fix').replace('SDKcases','SDK cases')
    DOCS[name]=body
for name,body in list(DOCS.items()):DOCS[name]=readable_prose(body)

# Supplement provenance without copying data or secrets.
git_history=subprocess.run(['git','log','-4','--format=%h %ad %s','--date=short'],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip().splitlines()
observations={'audit_date':'2026-10-09','repository':ROOT.name,'git_history':git_history,'model_artifacts':[],
              'rules_read':'.agents/rules/codebase-memory.md','graph_mcp_available':False,
              'method':'stat only; no model deserialization, database open, audio capture or external calls'}
for name in ['modules/emotion/models/expression_net.pth','modules/emotion/data/expression_landmarks.csv','modules/emotion/results/metrics.json','data/models/faster-whisper-small/model.bin']:
    p=ROOT/name;observations['model_artifacts'].append(dict(path=name,exists=p.exists(),bytes=p.stat().st_size if p.is_file() else None))
(OUT/'audit_observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
claim('C59','Stat xác nhận checkpoint expression_net.pth 71785bytes và Whispermodel.bin483546902bytes; CSV/results thiếu ở pathconfig.',
      'docs/khkt_technical_evidence/audit_observations.json',limit='Chỉ stat, không loadcheckpoint; kích thước/tồn tại không chứng minh modelquality/provenance hoặc nghiệm thu.')
claim('C60','Gitlog trong snapshot chỉ có2commit ngày30/09/2026; lịch sử thay đổi worktree sau đó chưa được commit đầy đủ.',
      'docs/khkt_technical_evidence/audit_observations.json',status='UNKNOWN',limit='Gitcommand đã đọc trongaudit; không dựng author/date từngfile hoặc coi commitmessage là featurevalidation.')
DOCS['02_TECHNOLOGY_STACK.md']+='\n'+evidence(['C59'])
DOCS['07_DEVELOPMENT_HISTORY.md']+='\n'+evidence(['C60'])
for c in CLAIMS:
    c['claim']=readable_prose(c['claim']).strip()
    c['limitations']=readable_prose(c['limitations']).strip()
indexes=[]
for p in sorted((ROOT/'database/migrations').glob('*.sql')):
    text=p.read_text(encoding='utf-8')
    for match in re.finditer(r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+IF\s+NOT\s+EXISTS\s+(\w+)\s+ON\s+(\w+)\s*\(([^;]+)\);',text,re.I):
        indexes.append(dict(name=match[1],table=match[2],columns=match[3],source_path=str(p.relative_to(ROOT)),line=text[:match.start()].count('\n')+1,ddl=match[0]))
(OUT/'schema_indexes.json').write_text(json.dumps(indexes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
DOCS['05_DATABASE_AND_SYNC.md']+=f'\n## Quy mô DDL và index\n\nBốn migration khai báo {len(SCHEMA)} bảng và {len(indexes)} CREATE INDEX riêng (ngoài index ngầm do PK/UNIQUE). schema_indexes.json ghi index, columns, file/dòng và DDL. Index hỗ trợ truy vấn, không chứng minh tốc độ nếu thiếu query benchmark.\n'

status_definitions='''## Quy ước trạng thái và độ tin cậy

| Trạng thái | Nghĩa và điều kiện |
|---|---|
| IMPLEMENTED | Có code và test/runtime thành công liên quan trong phạm vi ghi rõ; không tự suy ra E2E hoặc tính chính xác y khoa |
| PARTIALLY_IMPLEMENTED | Có implementation nhưng workflow hoặc nghiệm thu còn thiếu |
| PLANNED | Có định hướng/tài liệu, chưa thấy runtime làm việc tương ứng |
| DEPRECATED | Code giữ lại nhưng không thuộc tuyến active được kiểm toán |
| REMOVED | Có record/tombstone/removal evidence; phải ghi rõ phần nào bị gỡ |
| UNKNOWN | Không đủ bằng chứng để xác định hoặc kết luận định lượng |

Confidence HIGH/MEDIUM là độ tin cậy của kết luận kiểm toán dựa nguồn, **không phải độ chính xác model**. Mọi status ở manifest là cho câu claim cụ thể. Source-only không tự thành IMPLEMENTED. Kết quả log được kiểm tra tồn tại/nội dung, không chạy lại. “NOT VERIFIED” là chú thích giới hạn, không thay status enum.
'''
DOCS['00_EXECUTIVE_SUMMARY.md']+='\n'+status_definitions
master='# Hồ sơ bằng chứng kỹ thuật tổng hợp — AI Care & Rehabilitation System\n\n'
master+='Ngày09/10/2026 · kiểm toán tĩnh snapshot worktree. Tài liệu tự chứa: thuật toán, sơ đồ, schema, test, giới hạn và mapping KHKT. Không phải chứng nhận nghiệm thu sản phẩm hoặc hiệu quả lâm sàng.\n\n'+status_definitions+'\n'
for i,(name,body) in enumerate(sorted(DOCS.items()),1):
    # Maintain hierarchy in consolidated document; source-specific evidence retained.
    master+=f"\n## Phần {i:02} — {name}\n\n"
    master+=re.sub(r'^(#{1,4}) ',lambda m:'#'*(len(m[1])+2)+' ',body,flags=re.M)+'\n'
DOCS['10_TECHNICAL_EVIDENCE_MASTER.md']=master
for name,body in DOCS.items():(OUT/name).write_text(body,encoding='utf-8')
(OUT/'evidence_manifest.json').write_text(json.dumps(CLAIMS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'schema_dictionary.json').write_text(json.dumps(SCHEMA,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'documents':len(DOCS),'claims':len(CLAIMS),'tables':len(SCHEMA),'application_tests_executed':0},ensure_ascii=False))

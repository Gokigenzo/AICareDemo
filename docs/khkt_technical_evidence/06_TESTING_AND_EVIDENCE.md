# Kiểm thử, số đo và thiết kế thí nghiệm

## Phạm vi và nhật ký lượt kiểm toán

**Không chạy test ứng dụng trong lượt này.** Không cài package, import module ứng dụng/native audio, mở DB production, thu micro/camera, gọi Gemini hay SMTP. Dùng rg/sed/cat đọc source, AST stdlib xác định symbol/line, parser văn bản DDL, JSON đọc artefact và SHA-256 đối chiếu source. python không có trong PATH; python3 chạy generator/validator tài liệu. Đây là kiểm tra tài liệu, không thêm kết quả thử nghiệm hệ thống. validation_report.json ghi môi trường/lệnh/kết quả kiểm tra cuối.

## MEASURED RESULTS — artefact hiện có, chưa chạy lại

| Artefact | Kết quả kiểm chứng bằng file | Môi trường/input và giới hạn |
|---|---|---|
| reports/gemini_intent/intent-and-stt-tests.txt | 107 passed, 1 SDKwarning | pytest nhóm intent/STT; mock SDK/audio, synthetic text; không mic vật lý |
| reports/gemini_intent/legacy-regression-isolated.txt | 41 passed | runner mock sounddevice tránh native audio; contract/business/reliability/rehab config cũ |
| reports/gemini_intent/realtime-regression.txt | 13 passed, 0.33s | 12 scenario+case cancel; in-memory SQLite, in-process SSE queues, fake SMTP |
| reports/local_stt/final-tests.txt | 85 passed, 1 skipped, 8.89s | overlap với log mới; test audio Việt chuẩn bịskip; không cộng vào 161 |
| reports/local_stt/rehab-regression.txt | 17 passed, 3.50s | test_rehab_assistant, landmark/blankframe/counters; không human trial |
| reports/local_stt/routine-regression.txt | 6 passed, 3.78s | routine/UI/data fixture; không lâm sàng |
| reports/medication_migration/medication_tests.txt | 16 test, OK, 1.794s | service scheduling legacy, fake SMTP; panel không active |
| reports/gemini_intent/http-smoke.json | navigation once/auth/sizechecks true, 66ms, Gemini_calls0 | loopback HTTP+Qt, DB giả, Gemini mock, không microphone |
| reports/gemini_intent/dashboard-smoke.txt | lifecycle offscreen/worker/model load idle | camera/audio mocked, TTSdisabled, SMTP forbidden; không inference camera/micro thật |
| reports/gemini_intent/clean-pip-check.txt / clean-full-install.txt / clean-smoke.txt | cài sạch/check/schema passed | Python3.14.4 Linux trong /tmp venv; không WindowsEXE nghiệm thu |
| reports/local_stt/cpu-final.json | cold 727 ms, p50=4642 ms, p95=6015.95ms, RSS 1830600704 bytes | CPU small/int8, 2 threads, beam 1, 12 lượt/4 WAV 873–1170 ms; không groundtruth, không tổng RAM app |
| reports/local_stt/gpu-camera.json | CUDA error; camera unavailable | Không đạt kiểm traGPU/camera đồng thời, không suy ra mọi máy không có GPU |
| reports/gemini_intent/offline-benchmark.json | 104/150 correct; 72/102 acceptance; 0unexpected_sensitive_routes;p95local0.027667ms | Clouddisabled; coverage policy local, không model accuracy/full voice |
| reports/gemini_intent/limited-live-benchmark.json | 3/3 schema và intent; 1633/1138/1562 ms; p95sample 1633 ms | 3 synthetic cases, không dispatch business; project/quota chưa verified; n=3 quá nhỏ |
| reports/gemini_intent/live-smoke.json | 1746 ms cho 1 sample | Smoke riêng; không cộng thành accuracy trên 102 case |

Ba nhóm 107+41+13=161 chỉ là các nhóm trong report Gemini, không tuyên bố 161 unique capability hoặc toàn repo pass. Các nhóm 85/17/6/16 ở log khác có trùng phạm vi. pytest tổng không tự chứng minh từng assert phủ hết mục tiêu ghi trong doc string. [C51–C54]

### Chất lượng và tính tái lập của log

Logpytest trên thường chỉ summary, không kèm nguyên lệnh/env đầy đủ. Nếu lệnh không ghi trong report/script tương ứng thì **UNKNOWN**, không tái dựng rồi gọi đó là lệnh đã chạy. Python3.14.4/Linux/venv sạch lấy từ report và cài sạch, không mặc định mọi log cùng fixture/máy. Runtime capability cũ ghi thiếu PortAudio; report Gemini mới ghi library có nhưng không có thiết bị, cần giữ thời điểm và scope khác nhau. Người dùng từng xác nhận STT hoạt động trên desktop là phản hồi vận hành, chưa thay thế log nghiệm thu audio có ground truth. [C25/C49/C55]

STT 12 lượt thuộc 4 file, 3lặp/file; observations tương quan nên không xem n12 là 12 người. RSS≈1.83GB theo bytes thập phân là script engine, không peak RAM/VRAM toàn app. Latency gồm decode và consume segments, không chỉ generatorcreation. CPU p95 này chưa đạt mục tiêu5s trong kế hoạch, audio1s chưa đại diện câu3–10s. [C51]

Offline intent acceptance 72/102=70.59%; overall104/150=69.33%. HOME→UNKNOWN 40, SNOOZE/HELP/START→UNKNOWN 2 mỗi intent. Unknown giữ an toàn/nút tay nhưng vẫn là miss trong coverage metric. 0 unsafe trên tập tổng hợp không là xác suất tuyệt đối0 ngoài thực tế. Không có macro-F1/Gemini accuracy trên 102 case để công bố. [C52]

### Kiểm tra source test so với tên scenario

tests/test_realtime_sync_12_scenarios.py gọi ApiRouter.handle_request trực tiếp, đăng ký SSE Client queue nội bộ, gọi relay.process_pending_events. Không mở 3 browser hay 3 máy Internet. test_scenario_12... đo 3 phiên ×20event nhưng pytestlog capture stdout không lưu các p50/p95 chi tiết. Chỉ có summary passed và assert<5000 ms; **không tự tạo số p95network**. Fixture DataImporter.import_all có thể đọc nguồn standalone/JSON trên host; chưa bảo đảm mọi fixture thuần synthetic nếu không cô lập nguồn import. [C41/C42/C54]

Test_face_registration có path default tạo/xóa profile; vì vậy audit không chạy. Baseline STT còn 6 fail/no such tablepatients/rehab_plans doisolation/order và timeoutteardown; baseline-failure-details.txt,baseline-group-rerun.txt ghi rõ. Nhóm native audio ban đầu timeout, all-tests.txt không phải bằng chứng passfullsuite. Không che thất bại chỉ vì log nhóm riêng đãpass. [C09/C54/C55]

## EXISTING BUT UNVERIFIED CLAIMS

| Tuyên bố thường gặp | Vì sao chưa đủ | Cách diễn đạt phù hợp |
|---|---|---|
| Confidence face 90% nghĩa accuracy90% | Heuristic clamp/default; không confusion test | “Điểm hiển thị từ distance, chưa calibration” |
| ExpressionMLP đã đạt accuracy cao | Check point có, thiếu CSV/splits/metrics/provenance | “Code training/evaluation và check point; chất lượng UNKNOWN” |
| 10/10 camera verified là10rep đúng form | Dashboard dùng total count, quality threshold chưa enforced | “Đạt số lần theo FSM; chất lượng từngrep chưa được chứng minh” |
| Người già đã uống thuốc thực tế | Chỉ button/voice selfreport | “Người dùng xác nhận đã uống” |
| Thuốc snooze luôn nhắc lại đúng delay | Activeflow chỉ đổi state, chưa timer proof | “Có thao tác nhắc lại; timed workflow chưa nghiệm thu” |
| Real time 3 client<5s qua Internet | Test queue inprocess, stdout metric không lưu | “Đã test outbox/SSE logic; latency thiết bị thật UNKNOWN” |
| Gemini đạt≥95% hoặc JSON≥99% | 3 live case; chưa 102 acceptance/cloud tắt | “Smoke3syntheticcase đãpass; chưa đạt bằng chứng nghiệm thu” |
| Hệ thống an toàn/secure hoặc cải thiện sức khỏe | Auth plaintext/public password; không clinical trial | “Nguyên mẫu nghiên cứu kỹ thuật, chưa validation lâm sàng/production” |

## PROPOSED EXPERIMENTS — chưa thực hiện

| Module | Input/ground truth | Quy trình tái lập | Metrics và điều kiện diễn giải |
|---|---|---|---|
| Face | Người tham gia đồng ý; identity gán trước; người unknown giữ riêng | Tách theo người/session; khóa threshold trước test; sáng/góc/khẩu trang/nhiều mặt | Accuracyclosedset; FAR=FA/N impostor; FRR=FR/N genuine; báo reject/TTL/latency, khoảng tin cậy |
| Expression | Ảnh/session được đồng ý; annotators label biểu cảm, agreement | Subject-disjoint train/val/test; so heuristic/MLP/ensemble/logistic cùng split | Macro F1=(ΣF1c)/K; confusion/support; không diễn giải sức khỏe tâm thần |
| Rehab | Videođồngý; 2 người đếm manual, pose/repform tiêu chí cố định | Đủ 3 bài/góc/occlusion/FPS; freeze thresholds; pause/unplug/mấttracking | MAE count=mean|pred-gt|; joint angle error với chuẩn nếu có; completed falsepositive/negative; không clinical efficacy |
| STT | 30–50WAVtiếng Việt thật 3–10s có consent/transcript chuẩn | Split người/phrase, noiseTV/quạt/phủ định; freeze VAD/beam/model | WER=(S+D+I)/Nword; CER tương tự char; báo normalization và zero-length denominator; p50/p95, cold/warm |
| Intent | Syntheticreviewed 102 acceptance giữ tách 48 tune; gold intent/context | Khóa prompt/schema/policy; trước chạy verify quota/free/privacy; no handler trong model benchmark | Accuracy/macro F1 riêng local/cloud; JSONsuccess; unsafeactionrate; blocked/unknown coverage; n request/error 429 |
| App web sync | DB giả 3 devices/browsers; clocksmonotonic/correlationID | Instrument t0 commit, t1relay, t2 SSE, t3fetch, t4 render; disconnect/revoke/offline/restart | p50/p95/p99, successrate, duplicate events, outboxlag; phân biệt queue vsrender vsSMTP |
| Resource/concurrency | Thiết bị đích có model/mic/camera; dữ liệu giả | Camera baseline rồiSTT+TTS+web; repeatedcancel/context switch/shutdown | FPS distribution, CPU/RSS peak/VRAM, response UI, leakedworkers/mic, 30 phút stress |
| Packaging | WindowscleanVM, SQL fixture giả, lockeddeps | Freshinstall/buildEXE/installer/offline launch/modelpath/DLL/TTS | Check secret binary, license, rollback, missing DLL; chưa có kết quả hiện tại |

Mọi human recording cần đồng ý, nguồn dữ liệu rõ, xử lý tối thiểu, retention/deletion và báo cáo aggregate. Free-tier cloud chỉ syntheticreviewed neutral text phù hợpgate; không gửi health records thật hoặc coi ẩnID là anonymization. Kế hoạch thí nghiệm không phải bằng chứng đã thử trên người.

## Bằng chứng truy nguyên

- **C08 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.recognize_face`; Lines: 330–463. Explanation: LBPH distance<58 tạo raw match; history 15 và TTL2 giây làm mượt; confidence UI là heuristic. Giới hạn: Distance và confidence không phải xác suất đúng hay độ chính xác đã đo; TTL có thể giữ danh tính cũ.
- **C09 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.register_patient`; Lines: 614–719. Explanation: Đăng ký lưu crop và hồ sơ JSON, sync sang unified DB và retrain LBPH. Giới hạn: Test registration tồn tại nhưng một số dùng đường dữ liệu mặc định; không chạy trong audit để tránh sửa hồ sơ.
  - Đối chiếu: `services/patient_sync_service.py` · `sync_single_patient` · 44–262 (source_code).
- **C11 — PARTIALLY_IMPLEMENTED**. File: `modules/emotion/src/model.py`; Symbol: `ExpressionNet`; Lines: 7–21. Explanation: MLP độc lập nhận 63 tọa độ landmark, Linear63→128→64→5, ReLU và dropout0.25. Giới hạn: Check point tồn tại không chứng minh dữ liệu/huấn luyện; dashboard chỉ lấy3 logits đầu và softmax lại.
  - Đối chiếu: `modules/emotion/utils/preprocess.py` · `module` · 1–70 (source_code).
  - Đối chiếu: `modules/emotion/src/config.py` · `module` · 1–69 (source_code).
- **C12 — PARTIALLY_IMPLEMENTED**. File: `modules/emotion/src/data.py`; Symbol: `module`; Lines: 1–190. Explanation: Training biểu cảm có split theo session, baseline logistic regression và evaluator classification metrics. Giới hạn: Không tìm thấy CSV/splits/results phục vụ tái lập ở vị trí config; số người/data set/provenance UNKNOWN.
  - Đối chiếu: `modules/emotion/src/train.py` · `module` · 1–223 (source_code).
  - Đối chiếu: `modules/emotion/src/evaluate.py` · `module` · 1–189 (source_code).
  - Đối chiếu: `modules/emotion/src/baseline.py` · `module` · 1–66 (source_code).
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
- **C25 — IMPLEMENTED**. File: `services/local_voice/engine.py`; Symbol: `LocalSttEngine`; Lines: 8–44. Explanation: Engine faster-whisper small multilingual local files only, CPU/int8, beam 1, languagevi, VAD và consume segments ngoài UI. Giới hạn: Có inference file local; audio chuẩn/consent chưa xác minh; không có WER/CER hợp lệ; GPU chưa chạy thành công.
  - Đối chiếu: `reports/local_stt/cpu-final.json` · `module` · 1–145 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/local_stt/clean-smoke.txt` · `module` · 1–3 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/local_voice/config.py` · `VoiceConfig` · 7–29 (source_code).
  - Đối chiếu: `services/local_voice/worker.py` · `run_worker` · 8–49 (source_code).
- **C28 — PARTIALLY_IMPLEMENTED**. File: `services/transcript_intent/service.py`; Symbol: `GeminiIntentService`; Lines: 12–100. Explanation: Lớp hiểu text Gemini đã có code/backend/client/coordinator, nhưng cloud mặc định false và full acceptance chưa nghiệm thu. Giới hạn: 3 synthetic cases SDK thật; chưa 102 acceptance, mic→web, project/quota independent verify hoặc newest key smoke.
  - Đối chiếu: `reports/gemini_intent/limited-live-benchmark.json` · `module` · 1–60 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/config.py` · `BackendConfig` · 7–42 (source_code).
- **C29 — IMPLEMENTED**. File: `services/transcript_intent/policy.py`; Symbol: `module`; Lines: 1–76. Explanation: Privacy gate production chỉ 20 câu điều hướng trung tính; nội dung thuốc/phục hồi xử lý local, unknown không đoán. Giới hạn: Đảm bảo theo catalog đã review, không phải bộ khử nhạy cảm tổng quát; không cho tùy ý text sức khỏe vào free API.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/prompts.py` · `module` · 1–23 (source_code).
  - Đối chiếu: `tests/transcript_intent/test_contract_policy.py` · `test_privacy_default_deny_not_id_redaction` · 38–39 (test_source).
- **C32 — IMPLEMENTED**. File: `services/transcript_intent/budget.py`; Symbol: `ProjectBudget`; Lines: 17–75. Explanation: Quota file lock, reservation1200tokens, caps 1 RPM/2400 TPM/10 RPD reserve 2, retry bounded và circuit breaker. Giới hạn: Caps local, không phải quota provider được xác minh; file system shared không phải limiter nhiều host.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/transcript_intent/service.py` · `GeminiIntentService._cloud_locked` · 43–82 (source_code).
  - Đối chiếu: `tests/transcript_intent/test_contract_policy.py` · `test_quota_shared_across_instances_and_circuit` · 107–123 (test_source).
- **C41 — IMPLEMENTED**. File: `database/migrator.py`; Symbol: `module`; Lines: 1–62. Explanation: 4 migration định nghĩa schema, Migrator áp dụng theo version; importer gộp DB standalone/JSON. Giới hạn: Không mở DBproduction trong audit; seed không phải dữ liệu camera/micro/sensor thực; migration atomicity chưa fault inject.
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `database/importer.py` · `DataImporter.import_all` · 54–88 (source_code).
- **C42 — IMPLEMENTED**. File: `services/outbox_relay.py`; Symbol: `OutboxRelayService.process_pending_events`; Lines: 86–144. Explanation: Outbox relay poll0.5s gửi tín hiệu SSE/auth, side effect email và markprocessed; UI web refetch dữ liệu. Giới hạn: Test in-process queue; không phải 3 thiết bị qua Internet; processed≠client đã render hoặc SMTP đã tới mailbox.
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `web/sse_hub.py` · `SSEHub.dispatch_outbox_event` · 82–128 (source_code).
- **C45 — PARTIALLY_IMPLEMENTED**. File: `web/auth.py`; Symbol: `AuthService.authenticate_credentials`; Lines: 67–200. Explanation: Auth còn lưu password dạng prefix+plaintext, bypass kiểudemo và hint lộ mật khẩu khi sai. Giới hạn: Rủi ro nghiêm trọng nhìn thấy từ code; không kiểm tra khai thác, không sao chép giá trị mật khẩu vào báo cáo.
  - Đối chiếu: `web/auth.py` · `AuthService.register_caregiver` · 207–335 (source_code).
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

## Giới hạn assert io n FSM và tham chiếu sức khỏe

Test nâng tay và đứng-ngồi trong test_rehab_assistant chỉ đưa một input landmark rồi assert trạng thái; chưa đo đủ chu kỳ rồi xác minh rep/hold/penalty. Test marching assert đúng một step. Báo cáo không gọi 17 passed là độ chính xác đếm thực tế. Các dải “an toàn” hardcode trên web cần chuyên gia/tài liệu và cá nhân hóa riêng, không lấy UI làm ground truth. [C15–C17/C57]

## Bằng chứng truy nguyên

- **C57 — PARTIALLY_IMPLEMENTED**. File: `web/templates/portal_clinician.html`; Symbol: `module`; Lines: 1–2256. Explanation: Web chart có dải tham chiếu sức khỏe hardcode; chưa có chứng cứ validation/personalization lâm sàng. Giới hạn: Chỉ mô tả source UI; không công nhận các dải này là khuyến nghị y tế đúng cho mọi người.

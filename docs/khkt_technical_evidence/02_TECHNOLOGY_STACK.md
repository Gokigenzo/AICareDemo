# Công nghệ, dependency và model

## Ngôn ngữ và thư viện có vai trò thực tế

| Công nghệ | Vai trò trong mã | Nguồn chính / giới hạn |
|---|---|---|
| Python | GUI, AI, service, HTTP server, SQLadapter và test | main.py; services; web; không phải backend Node |
| PyQt5 | QWidget, signals/slots, QThread/QTimer, dialogs | app/dashboard.py; requirements>=5.15.10 |
| HTML/CSS/JavaScript | Web portal, fetchAPI, Event Source và rendering | web/templates; không thấy frontendReact trong đường này |
| OpenCV contrib | cv2.face.LBPH, detectorDNN/Haar, frame/drawing | adapters/face_adapter.py; không dùng embeddingFaceNet cho identity |
| MediaPipe | FaceMesh/FaceLandmarker và Pose/PoseLandmarkerLite | adapters/emotion_adapter.py; rehab_engine.py |
| NumPy/SciPy | Tọa độ, softmax/smoothing, PCM/resample_poly | emotion/rehab/local_voice; NumPy>=1.24; SciPy>=1.10,<2 |
| PyTorch/torchvision | MLPbiểu cảm và code CV phụ trợ | module emotion; runtime Torch CPU log không là chứng cứ CUDA |
| faster-whisper1.2.1 / CTranslate2 | Whisper local encoder/decoder/int8 | requirements primary và Linux lock; CT2=4.8.2 trong lock |
| PyAV18.1.0 / tokenizers / ONNX Runtime | Decode audio và transitive Whisper/VAD dependencies | STT lock; pin PyAV sửa compatibility theo log cài sạch |
| sounddevice0.5.6 / PortAudio native | Input Stream microphone | pip package không tự chứng minh libportaudio/mic của OS |
| pyttsx3 | TTSlocal trong child process | không API STT; voices phụ thuộc OS |
| Pydantic>=2.10 | strict schema cho proposal/request | không dùng model confidence làm authorization |
| google-genai2.29.0 | Official DeveloperAPI text/JSON backend | requirements-gemini-backend.txt; excluded khỏi elderEXE |
| filelock4.0.12 | Shared file system quota lock | không phối hợp quota nhiều host độc lập |
| requests / urllib HTTP | Internalclient và các công cụ network | Gemini Intent Client/server; không gửi audio đến STT API |
| sqlite 3, http.server, threading, multiprocessing | DB và stdlib backend/server/worker | không FastAPI, không PostgreSQL runtime hiện tại |
| python-dotenv / Pillow / psutil / tzdata | Config, ảnh UI, đo RSS và time z one | Vai trò config/runtime/script; không chứng minh IoTsensor |
| pytest/unit test, sklearn/joblib | Test và training/evaluation standalone | Phân biệt dev/module requirements với runtime primary |

Các role trên có source trong manifest C06–C14/C24–C34/C40/C49. OpenCV/MediaPipe/Torch có nhiều manifest standalone cũ; không thay manifest chính bằng một file trong module.

## Phiên bản và môi trường

requirements.txt là manifest runtime chính; requirements-gemini-backend.txt include nó và pin SDK. requirements-linux.lock là snapshot Linux đã có log cài sạch; requirements-local-stt.lock là closure STT; backend.lock là closure SDK. requirements-windows.txt có bounds riêng cho Python3.11–3.12/NumPy<2/MediaPipe<0.10.21. Không dùng Linux lock thay khóa Windows. [C49]

Log bàn giao ghi Python3.14.4 Linuxx86_64, cài sạch trong /tmp/ai-care-gemini-clean và pipcheck không brokenrequirements. Linux lock có PyQt5=5.15.11, Qt5=5.15.19, OpenCV=5.0.0.93, MediaPipe=1.1.0, NumPy=2.5.3, SciPy=1.18.1, Torch=2.14.1+cpu, Torchvision=0.29.1+cpu. Đây là số từ lock/log, không phải lệnh kiểm tra môi trường hiện tại trong audit. [C49]

Root constraints nhiều gói dùng>=, không bảo đảm reproducibility một mình. Manifest rehab standalone còn liệt kê `time` dù đây là stdlib; manifest face có pins khác Windowsbounds. Cần thống nhất cho bản phát hành sau, không sửa trong nhiệm vụ tài liệu. .spec/setup/buildbat/installer và GitHubworkflow đã có nhưng nghiệm thu Windows DLL/model/TTS/newSDKbinary chưa có. [C49/C50]

## Model và trọng số

| Model/asset | Vai trò active | Nguồn biết được | Điều chưa biết |
|---|---|---|---|
| OpenCVface_detector_uint8.pb +pbtxt | DNNface detection; Haarfallback | modules/face/models; đọc bằngcv2.dnn | Provenance revision/training data set chưa xác minh |
| LBPH recognizer | Identity, train in-memory từ crop đăng ký | FaceAdapter.train_recognizer | Tập đánh giá độc lập, calibration ngưỡng 58 |
| face_landmarker.task | MediaPipeTasks face landmarks nếu API legacy thiếu | modules/emotion/models | Artifact không tự chứng minh expressionaccuracy |
| expression_net.pth | OptionalMLP5lớp; dashboard sử dụng 3 logits đầu | modules/emotion/models; 71785 bytes tại audit | Không CSV/split/metrics tại vị trí config; provenance UNKNOWN |
| pose_landmarker_lite.task | MediaPipeTasks pose | modules/rehabilitation/models | Camera 3D/gócchuẩn không được cung cấp |
| faster-whisper-small/model.bin | Local STT multilingual | data/models; chuẩn bị từ cache Systran/faster-whisper-small, revision536b0662742c02347bc0e980a01041f333bce120 theo report | Không download mới trong audit; chưa giọng Việt được đồng ý/groundtruth |
| age/genderCaffe weights | Module face standalone lịch sử | modules/face/models; face_processor.py | Không phải identity activeDashboard |
| HFD/ONNX fall weights | Nhánhvideo/legacy | modules/fall/models, hfd_manifest | Không trong callback camera active; metric cũ không dùng cho rehab |

Model Whisper tại audit có 483546902 bytes; chỉ stat file, không load. CheckpointMLP cũng chỉ stat, không deserializepickle. Kích thước không đánh giá chất lượng hoặc license. Có file LICENSE cho một số module; chưa chứng minh đầy đủ license/provenance cho mọi weight và asset âm nhạc/ảnh. [C06/C11/C14/C25/C48/C55]

## Dịch vụ ngoài, cấu hình và boundary

Gemini là DeveloperAPI, vertex ai=False, textgenerateContent với JSON schema/tools=[]; không có DBtools/functionexecution/grounding/SQL hoặc tư vấn y tế. Model config pin gemini-3.5-flash-lite. Key/backend flags chỉ backend secret; desktop chỉinternalURL/token/flag. Free-tier được operator xác nhận trong bàn giao, chưa independentlyverifyprojectbilling/quota. Không dùng alias latest làm chứng minh model quota. [C28/C31/C32/C50/C53]

SMTP là service có cấu hình; test mock không chứng minh thư được nhận. Các cấu hình không chứa dữ liệu nhạy cảm được mô tả bằng tên biến: VOICE_AI_ENABLED; VOICE_MODEL_PATH/VOICE_DEVICE/VOICE_COMPUTE_TYPE/VOICE_CPU_THREADS/VOICE_MAX_SECONDS/VOICE_BEAM_SIZE; GEMINI_INTENT_ENABLED/GEMINI_FREE_TIER_VERIFIED/GEMINI_API_KEY/GEMINI_PROJECT_ID/GEMINI_INTENT_*CAP; VOICE_INTENT_ENABLED/VOICE_INTENT_BACKEND_URL/VOICE_INTENT_SESSION_TOKEN. Tên biến phải đối chiếu setup/config actual khi vận hành; không đọc/copy .envprivate vào bộ tài liệu. [C25/C28/C32/C46/C49/C50]

## Bằng chứng truy nguyên

- **C06 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.__init__`; Lines: 40–81. Explanation: Face detection ưu tiên OpenCV DNN, fallback Haar; nhận diện bằng LBPH radius 1/neighbors 8/grid8x8. Giới hạn: Có pipeline; chưa có FAR/FRR trên tập người độc lập; DNN detector không phải model nhận dạng identity.
  - Đối chiếu: `adapters/face_adapter.py` · `FaceAdapter.detect_face` · 107–146 (source_code).
- **C07 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.extract_face_roi`; Lines: 171–221. Explanation: ROI khuôn mặt grayscale, CLAHE, bilateral và resize200x200; augmentation flip, sáng/tối, xoay±4°. Giới hạn: Không có lớp background thực tế dù doc string nhắc; augmentation không tăng số người độc lập.
  - Đối chiếu: `adapters/face_adapter.py` · `FaceAdapter.train_recognizer` · 223–312 (source_code).
- **C11 — PARTIALLY_IMPLEMENTED**. File: `modules/emotion/src/model.py`; Symbol: `ExpressionNet`; Lines: 7–21. Explanation: MLP độc lập nhận 63 tọa độ landmark, Linear63→128→64→5, ReLU và dropout0.25. Giới hạn: Check point tồn tại không chứng minh dữ liệu/huấn luyện; dashboard chỉ lấy3 logits đầu và softmax lại.
  - Đối chiếu: `modules/emotion/utils/preprocess.py` · `module` · 1–70 (source_code).
  - Đối chiếu: `modules/emotion/src/config.py` · `module` · 1–69 (source_code).
- **C12 — PARTIALLY_IMPLEMENTED**. File: `modules/emotion/src/data.py`; Symbol: `module`; Lines: 1–190. Explanation: Training biểu cảm có split theo session, baseline logistic regression và evaluator classification metrics. Giới hạn: Không tìm thấy CSV/splits/results phục vụ tái lập ở vị trí config; số người/data set/provenance UNKNOWN.
  - Đối chiếu: `modules/emotion/src/train.py` · `module` · 1–223 (source_code).
  - Đối chiếu: `modules/emotion/src/evaluate.py` · `module` · 1–189 (source_code).
  - Đối chiếu: `modules/emotion/src/baseline.py` · `module` · 1–66 (source_code).
- **C14 — PARTIALLY_IMPLEMENTED**. File: `modules/rehabilitation/rehab_engine.py`; Symbol: `calculate_angle`; Lines: 44–57. Explanation: Phục hồi dùng MediaPipe Pose/Tasks lite và góc2D từ tọa độ landmark chuẩn hóa. Giới hạn: Không dùng 3D chuẩn lâm sàng; x/y chuẩn hóa chưa sửa tỷ lệ khung hình; chưa có sai số góc với thước chuẩn.
  - Đối chiếu: `modules/rehabilitation/rehab_engine.py` · `RehabilitationEngine._init_pose` · 531–583 (source_code).
- **C25 — IMPLEMENTED**. File: `services/local_voice/engine.py`; Symbol: `LocalSttEngine`; Lines: 8–44. Explanation: Engine faster-whisper small multilingual local files only, CPU/int8, beam 1, languagevi, VAD và consume segments ngoài UI. Giới hạn: Có inference file local; audio chuẩn/consent chưa xác minh; không có WER/CER hợp lệ; GPU chưa chạy thành công.
  - Đối chiếu: `reports/local_stt/cpu-final.json` · `module` · 1–145 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/local_stt/clean-smoke.txt` · `module` · 1–3 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/local_voice/config.py` · `VoiceConfig` · 7–29 (source_code).
  - Đối chiếu: `services/local_voice/worker.py` · `run_worker` · 8–49 (source_code).
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
- **C34 — IMPLEMENTED**. File: `services/local_voice/controller.py`; Symbol: `VoiceSessionController.start`; Lines: 56–73. Explanation: TTS được suspend khi ghi; nhạc pause; child pyttsx3 local giữ entrypoint frozen riêng. Giới hạn: Phối hợp đã test code/mocks; chưa nghe playbackloa thật; nhắc thuốc/coach active chưa nối toàn bộ TTS callbacks.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/local_voice/tts_runtime.py` · `speak` · 5–19 (source_code).
  - Đối chiếu: `app/local_voice_widget.py` · `module` · 1–110 (source_code).
  - Đối chiếu: `tests/voice_ai/test_local_voice.py` · `test_tts_cannot_restart_during_capture` · 194–205 (test_source).
- **C40 — IMPLEMENTED**. File: `database/connection.py`; Symbol: `UnifiedDatabaseManager`; Lines: 51–115. Explanation: Database runtime là SQLite/WAL/foreignkeys/bus y timeout; không có PostgreSQL driver runtime trong manager. Giới hạn: Các comment PostgreSQL/ANSI/3NF là định hướng, không là chứng minh tương thích hoặc chuẩn hóa hình thức.
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
- **C48 — DEPRECATED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._process_video_frame`; Lines: 530–570. Explanation: Fall/HFD/ONNX/video còn retainedsource/artefacts nhưng không trong camera callbacks dashboard hiện tại. Giới hạn: Deprecated theo dashboard active; toolvideo riêng vẫn có. Không dùng metricfall cũ thay metric rehab hiện tại.
  - Đối chiếu: `core/fall_pipeline.py` · `module` · 1–542 (source_code).
  - Đối chiếu: `modules/fall/hfd_classifier.py` · `module` · 1–85 (source_code).
- **C49 — IMPLEMENTED**. File: `requirements.txt`; Symbol: `module`; Lines: 1–26. Explanation: Runtime requirements chính+lock Linux/STT/backend SDK; đã có log cài sạchLinux và pipcheck. Giới hạn: Windows constraints/build/installer/model DLL mới chưa nghiệm thu; pin Linux không chứng minh Windows wheel.
  - Đối chiếu: `reports/gemini_intent/clean-pip-check.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/gemini_intent/clean-full-install.txt` · `module` · 1–186 (existing_test_or_runtime_artifact).
  - Đối chiếu: `requirements-linux.lock` · `module` · 1–64 (source_code).
  - Đối chiếu: `requirements-gemini-backend.txt` · `module` · 1–4 (source_code).
- **C50 — PARTIALLY_IMPLEMENTED**. File: `AI_Rehab_Safety_Assistant.spec`; Symbol: `module`; Lines: 1–143. Explanation: Spec excludes Gemini SDK/provider/backend env khỏi EXE; chưa build binary kiểm chứng ranh giới này. Giới hạn: Reviewsource recipe thôi, không chứng minh binary không secret. Không đọc .envprivate hoặc tải/cài package trong audit.
- **C53 — IMPLEMENTED**. File: `reports/gemini_intent/limited-live-benchmark.json`; Symbol: `module`; Lines: 1–60. Explanation: 3 synthetic API cases đạt schema/intent, latency 1633/1138/1562 ms; full acceptance=false/quota_verified=false. Giới hạn: n3 và một smoke1746ms riêng; không đủ chứng minh accuracy95% hay latency ổn định. Audit không gọi API.
  - Đối chiếu: `reports/gemini_intent/limited-live-benchmark.json` · `module` · 1–60 (existing_test_or_runtime_artifact).
- **C55 — UNKNOWN**. File: `reports/local_stt/REPORT.md`; Symbol: `module`; Lines: 1–58. Explanation: Face FAR/FRR, emotion holdout F1, rehab clinical angle error, STT WER và nghiệm thu mic/camera/multi host chưa có bằng chứng phù hợp. Giới hạn: Không có số đo hợp lệ trong các artefact đã đối chiếu; không khẳng định không tồn tại ngoài repo.
  - Đối chiếu: `reports/gemini_intent/REPORT.md` · `module` · 1–75 (source_code).


## Bằng chứng truy nguyên

- **C59 — PARTIALLY_IMPLEMENTED**. File: `docs/khkt_technical_evidence/audit_observations.json`; Symbol: `module`; Lines: 1–33. Explanation: Stat xác nhận checkpoint expression_net.pth 71785bytes và Whispermodel.bin483546902bytes; CSV/results thiếu ở pathconfig. Giới hạn: Chỉ stat, không loadcheckpoint; kích thước/tồn tại không chứng minh modelquality/provenance hoặc nghiệm thu.

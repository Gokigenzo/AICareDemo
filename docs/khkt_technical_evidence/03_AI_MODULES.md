# Phân tích thuật toán và module AI

## 1. Face: detection tách biệt recognition

DNN nhận blob300×300, mean[104, 117, 123], lọc confidence>0.50; lấy box phù hợp nhất theo logic detector. Haarfallback dùng scaleFactor1.1, min Neighbors 5, minSize 40 và chọn khuôn mặt lớn. Giá trị0.90 ở fallback là số gán, không detector probability đã đo. [C06]

ROI padding 15% khi được chọn, chuyển grayscale, CLAHEclip2/tile8×8, bilateral d5/sigma 25, resize200×200. Huấn luyện LBPH dùng image gốc, flipngang, brightness±12, rotation±4°. Một ảnh hợp lệ sinh nhiều ảnh tương quan; không gọi chúng là nhiều người/mẫu độc lập. Trên nhánh hiện tại không có background class thực dù doc string gợi ý. [C07]

LBPH mã hóa cấu trúc cục bộ theo nguyên lý LocalBinaryPattern:

\[
LBP_{P, R}=\sum_{p=0}^{P-1}\mathbf{1}(g_p\geq g_c)2^p,\quad P=8, R=1.
\]

Đây là giải thích thuật toán của thư việncv2.face, không phải code Python tự cài LBP. Histogram theo lưới8×8 được so với traininglabels; distance nhỏ hơn ngưỡng 58 tạo rawmatch. Không có faceembeddingneural hay cosinesimilarity trong identitypipeline này. Temporal history 15, unknown counters vàTTL2s tạo recognized/uncertain/unknown/no_face. GUIconfidence bị clamp và nội suy theo distance, khoảng0.65–0.99; không được dùng như accuracy. [C06/C08]

Đăng ký crop/profile JSON rồi sync patient/legacy_map và retrain. Nhận diện face ID được resolveunified_patient_id; dữ liệu tên/thuốc phải truy từ patientbinding, không dựa textASR. Khi unknown, GUI có thể vẫn giữ current_patient_id; voice guard đọc status, nhưng thao tác tay cần nghiệm thu đổi/người lạ. Nhiều mặt, ánh sáng, khẩu trang, góc nghiêng, TTL giữ người trước và anti-spoof/liveness là phần chưa đo. Chưa có FAR/FRR/accuracy trên holdout identity. [C04/C09/C55]

## 2. Biểu cảm: heuristic landmark và MLP tùy chọn

Dashboard có Neutral/Happy/Sad. FaceMeshlegacy hoặc FaceLandmarkerTasks lấy landmark, sau đó heuristic dùng độ rộng miệng, độ nâng khóe và khoảng lông mày chia theo khoảng mắt. Đặt d=||p263-p33||xy, w=||p291-p61||xy/d, e=((p13y+p14y)/2-(p61y+p291y)/2)/d, b=||p336-p107||xy/d:

\[
h=40\max(0, e-0.012)+12\max(0, w-0.49),\quad s=45\max(0,-0.010-e)+10\max(0, 0.27-b).
\]

\[
z=(2-1.6(h+s),\; 3.6h-1.2,\; 3.6s-1.2),\quad p_i=\frac{e^{z_i-\max(z)}}{\sum_j e^{z_j-\max(z)}}.
\]

Khi d<1e-4 trả default[.90,.05,.05]. Tên FACS trong code không chứng minh model được chuyên gia FACS gán actionunits hay validation y khoa. [C10]

MLP độc lập dùng21landmarks×3tọa độ=63 features. Preprocesscenter theo mũi và normalize theo khoảng mắt3D, flatten. Network Linear63→128→64→5 với ReLU/dropout. Năm lớp training là Neutral/Happy/Sad/Angry/Surprised. Dashboard chỉ lấy ba logits đầu, softmax riêng; khi model có, p=0.75pheuristic+0.25pMLP3. Lấy trung bình 10 frames rồi argmax; no face giữ ngắnTTL1.2s trước clear. Đây không phải bộ phân loại5lớp đầy đủ trên dashboard. [C10/C11]

Training code có seed 42, batch 32, max200epochs,lr0.001,weightdecay0.0001,dropout0.25, patience25; session train/val/testfractions0.6/0.2/0.2 với tối thiểu5session và kiểm tra không overlap session. Baseline LogisticRegression dùng cùng split; evaluator dự kiếnaccuracy, macroP/R/F1, confusion matrix/support. Có code không chứng minh training đã chạy đúng hay metrics cao: check point tồn tại, CSV/splits/results theo config không có. Cần kiểm tra tách theo người nếu nhiều session một người; session-disjoint chưa bảo đảm subject-disjoint. [C12/C55]

Output camera hiện JSON latest và shared state, không historyunifiedDB. Mood selfreport là đường riêng vào mood_checkins; không thay bằng emotion camera. Không suy diễn “buồn” thành trầm cảm, tình trạng sức khỏe hoặc nguyên nhân. [C13]

## 3. Phục hồi: landmark, hình học 2D và FSM

MediaPipe Pose legacy dùng modelcomplexity0, detection/tracking0.55; fallbackTasksliteIMAGE, numposes1,confidence0.45. Xử lý lost pose/occlusionTTL1.2s reset partialrep; pause/resume reset phần đang làm, giữ count đã ghi. Required visibility đa số0.35; missing hip/ankle có surrogate ở các bài. [C14–C17]

calculate_angle dùng vector tại khớpb, lấy at an 2 giữa c-b và a-b:

\[
\theta=\left|\operator name{at an 2}(c_y-b_y, c_x-b_x)-\operator name{at an 2}(a_y-b_y, a_x-b_x)\right|\frac{180}{\pi},\quad \theta>180\Rightarrow\theta=360-\theta.
\]

Tọa độ là normalized x/y; không nhân lại theo width/height trong phép góc này. Phép đo là góc chiếu 2D, ảnh hưởng aspectratio, camera view point, che khuất và surrogate, không góc giải phẫu3D chuẩn. [C14]

| Bài | FSM/đếm thực tế | Chấm form / điểm yếu |
|---|---|---|
| Nâng tay | down→raising khi mean>60°; peak>=142→hold_peak; mean<130→lowering; hạ<=50 đếm | Khuỷu<130 và chênh trái/phải>25° tăng penalty; hold<0.35s phạt, cuehold0.5s; score max(50, 100-penalty); correct nếu penalty<15 |
| Đứng-ngồi | read y→standing>=155 hoặc sitting<=118; descending<140→sitting<=118→ascending>125→standing>=155; phải had_bottom | Torsolean>45° thêm lỗi; ankle thiếu surrogate; score floor 50; correct penalty<15 |
| Đi tại chỗ | chênh rk.y-lk.y>.065→leftup, <-.065→rightup; lastfoot bảo đảm xen kẽ; absdiff<.035 vềstance | Đếm ngay lift; knee.y<hip_y+.18 formgood100, còn lại 80/incorrect; chưa đo gaitphase chuẩn |

Defaulttargets10/10/15 với reminder16h có thể sửa qua plan version. DB session giữ target_count_snapshot và plan_version. Rep_idempotency mặc định session/exercise/repnumber; insert event, update count/status và outbox cùng transaction. Chỉ khi count>=target mới camera_verified_completed; voice không có intentcomplete. [C15–C18/C27]

Nhưng dashboard so totalreps với target và ghi cảincorrectreps. Adapter không tự kiểm tra quality_threshold, visibility/source/hardware_valid hoặc tính hợp lệ score. Score<=0 dashboard còn dùng fallback 90. Vì vậy “camera verified” là tên trạng thái phần mềm, chưa chứng minh từng rep đúng form, nguồn camera thật hay lợi ích phục hồi. Chưa test đồng thời 2 writer/fault inject; unique idempotency không tự loại mọi lost update. [C18/C19/C55]

## 4. Voice STT và hiểu transcript

Explicitmicro→Audio Recorder(Input Stream)→mono float 32→resample_poly16k→WhisperModelsmallmultilingual local files only. Durationmặc định15s, giới hạn config 1–30s, CPU int8/2 threads/beam 1/languagevi; condition_on_previous_text=False, vad_filter=True. Model load một lần trong persistent worker; decode và consume generator hoàn tất ngoài UI; audio zero trảempty, NaN/file invalid bị reject. Không truyền audio vào Gemini/API STT. [C24/C25]

Controller state/loading/idle/recording/stopping/transcribing/cancelling; queues bounded, session UUID và immutablecapturedcontext kiểm tra từ polling50ms. Hủy native inference không có nghĩa model dừng ngay, nhưng response bị bỏ; không mở phiên chồng trước idleack. Context change/tab/patient/plan hoặcshutdown invalidates. TTSsuspend/nhạc pause khi ghi; physicalTTS/mic vẫn chưa nghiệm thu. [C26/C34]

### Registry và chính sách quyết định

| Intent enum | Handler thật | Điều kiện |
|---|---|---|
| navigate_home | medication_tabs.setCurrentIndex(0) | Có patient, khôngrunning |
| snooze_medication | ElderSyncClient.confirm_dose_taken(snooze) | Tabtoday, đúng 1 dose, khôngOVERDUE |
| confirm_medication_taken | cùng service self_reported_taken | Đúng 1 dose + dialog default No + recheck |
| request_medication_help | cùng service help_requested | Đúng 1 dose/context |
| start_rehabilitation | Dashboard._on_start_exercise | Tabrehab, camera, active plan, khôngrunning |
| pause_rehabilitation | Dashboard._on_pause_exercise | Tabrehab, camera, running, không paused |
| unknown | Không dispatch | Câu mơ hồ/nhiều ý/context không hợp lệ |

No intent tư vấny tế/SQL/emergencycall/completeexercise. NormalizeUnicode/case/punctuation và exact allowlist/paraphrases xử lý local; phủ định, uncertain, conjunction/inject io n được guard. Exact“không biết dùng thuốc này” là help exception, không confirmation. Proposal gồm intent enum, slots(snooze_minutes chỉ null), decision(route/clarify/reject), evidence_text; extra fields bịforbid. Evidence phải substring transcript, intent thuộc context allowlist và khớp semantics độc lập. Model confidence/policy không có quyền mở rộng handler. [C27/C29/C30]

Gemini production chỉ nhận 20 câu neutral navigation đãreview; payload không patient ID/context DB hash/medication/health record. Luồng local tiếp tục xử lý thuốc/phục hồi. HTTP không chấp nhận synthetic flag; CLI synthetic riêng thử enum rộng bằng dữ liệu giả. Đây là gateclosedcatalog, không phải anonymizationhealthrecords hoặc xử lý ngôn ngữ tự do. [C28–C33]

BackendSDKgoogle-genai2.29, model pin, JSON schema/tools=[]/autofunctiondisabled/temp0/maxoutput 512. Total client deadline<=8s, transportminimum10s; SDKimplicitattempts1 và app retry 0(default), tối đa1 khi cònbudget. Quota reserve1200tokens/request; caps 1 RPM/2400 TPM/10 RPD reserve 2; circuit3fails/30s, 429cooldown60s và filelock. Caps không là quota thật AI Studio. Keybackendkhôngbundleapp; cloud mặc định false. API offline/429/badJSON/stale→local/unknown, không businessreplay. [C28/C31–C33/C50]

## 5. Module lịch sử và phạm vi AI

Faceage/gender standalone, Voskarchive, semantic/orchestratorcũ và fallHFD/ONNX/video có source. Dashboard hiện không gọi fall trong callback camera; API voice/STT cũ 410, compatibilityfactorydisabled. Một số TTScoordinator được reuse nên không nói toàn bộservices/voice_ai đã xóa. Trò chơi/thuốc/health record là rules/business workflow, không gọi chúng là model AI chỉ vì cùng sản phẩm. [C23/C35/C36/C39/C48]

## Bằng chứng truy nguyên

- **C04 — PARTIALLY_IMPLEMENTED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._do_update_dashboard_ui`; Lines: 967–1083. Explanation: Nhận diện và chọn patient đồng bộ binding các widget; voice invalidates context khi đổi patient/tab/source. Giới hạn: Unknown-face không xóa current_patient_id; voice có guard riêng, hành động tay cần kiểm tra đổi/người lạ.
  - Đối chiếu: `app/dashboard.py` · `DashboardWindow._resolve_patient_id` · 936–953 (source_code).
  - Đối chiếu: `services/local_voice/dispatcher.py` · `CommandDispatcher.snapshot` · 24–45 (source_code).
- **C05 — IMPLEMENTED**. File: `app/dashboard.py`; Symbol: `DashboardWindow.closeEvent`; Lines: 1107–1118. Explanation: Đóng dashboard dừng timer, voice coordinator/controller và camera. Giới hạn: Smoke lifecycle có camera/micro mocked; worker đang native inference bị terminate sau chờ hữu hạn.
  - Đối chiếu: `reports/gemini_intent/dashboard-smoke.txt` · `module` · 1–44 (existing_test_or_runtime_artifact).
- **C06 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.__init__`; Lines: 40–81. Explanation: Face detection ưu tiên OpenCV DNN, fallback Haar; nhận diện bằng LBPH radius 1/neighbors 8/grid8x8. Giới hạn: Có pipeline; chưa có FAR/FRR trên tập người độc lập; DNN detector không phải model nhận dạng identity.
  - Đối chiếu: `adapters/face_adapter.py` · `FaceAdapter.detect_face` · 107–146 (source_code).
- **C07 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.extract_face_roi`; Lines: 171–221. Explanation: ROI khuôn mặt grayscale, CLAHE, bilateral và resize200x200; augmentation flip, sáng/tối, xoay±4°. Giới hạn: Không có lớp background thực tế dù doc string nhắc; augmentation không tăng số người độc lập.
  - Đối chiếu: `adapters/face_adapter.py` · `FaceAdapter.train_recognizer` · 223–312 (source_code).
- **C08 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.recognize_face`; Lines: 330–463. Explanation: LBPH distance<58 tạo raw match; history 15 và TTL2 giây làm mượt; confidence UI là heuristic. Giới hạn: Distance và confidence không phải xác suất đúng hay độ chính xác đã đo; TTL có thể giữ danh tính cũ.
- **C09 — PARTIALLY_IMPLEMENTED**. File: `adapters/face_adapter.py`; Symbol: `FaceAdapter.register_patient`; Lines: 614–719. Explanation: Đăng ký lưu crop và hồ sơ JSON, sync sang unified DB và retrain LBPH. Giới hạn: Test registration tồn tại nhưng một số dùng đường dữ liệu mặc định; không chạy trong audit để tránh sửa hồ sơ.
  - Đối chiếu: `services/patient_sync_service.py` · `sync_single_patient` · 44–262 (source_code).
- **C10 — PARTIALLY_IMPLEMENTED**. File: `adapters/emotion_adapter.py`; Symbol: `EmotionAdapter.process_frame`; Lines: 213–325. Explanation: Biểu cảm dashboard có3 lớp Neutral/Happy/Sad, landmark heuristic và ensemble 75%heuristic+25%MLP khi có model. Giới hạn: Không chẩn đoán tâm lý; chưa có accuracy/macro-F1 holdout hợp lệ cho ensemble 3 lớp.
  - Đối chiếu: `adapters/emotion_adapter.py` · `EmotionAdapter._compute_facs_probabilities` · 146–211 (source_code).
- **C11 — PARTIALLY_IMPLEMENTED**. File: `modules/emotion/src/model.py`; Symbol: `ExpressionNet`; Lines: 7–21. Explanation: MLP độc lập nhận 63 tọa độ landmark, Linear63→128→64→5, ReLU và dropout0.25. Giới hạn: Check point tồn tại không chứng minh dữ liệu/huấn luyện; dashboard chỉ lấy3 logits đầu và softmax lại.
  - Đối chiếu: `modules/emotion/utils/preprocess.py` · `module` · 1–70 (source_code).
  - Đối chiếu: `modules/emotion/src/config.py` · `module` · 1–69 (source_code).
- **C12 — PARTIALLY_IMPLEMENTED**. File: `modules/emotion/src/data.py`; Symbol: `module`; Lines: 1–190. Explanation: Training biểu cảm có split theo session, baseline logistic regression và evaluator classification metrics. Giới hạn: Không tìm thấy CSV/splits/results phục vụ tái lập ở vị trí config; số người/data set/provenance UNKNOWN.
  - Đối chiếu: `modules/emotion/src/train.py` · `module` · 1–223 (source_code).
  - Đối chiếu: `modules/emotion/src/evaluate.py` · `module` · 1–189 (source_code).
  - Đối chiếu: `modules/emotion/src/baseline.py` · `module` · 1–66 (source_code).
- **C13 — PARTIALLY_IMPLEMENTED**. File: `adapters/emotion_adapter.py`; Symbol: `EmotionAdapter._persist_result`; Lines: 359–374. Explanation: Biểu cảm camera ghi JSON/state, web đọc emotion_inferences; chưa thấy writer unified DB trong đường camera. Giới hạn: Schema và seed emotion_inferences không chứng minh camera→DB→web; tìm kiếm call sites tĩnh chưa thấy cầu nối.
  - Đối chiếu: `web/api_router.py` · `ApiRouter._get_mood` · 1052–1076 (source_code).
- **C14 — PARTIALLY_IMPLEMENTED**. File: `modules/rehabilitation/rehab_engine.py`; Symbol: `calculate_angle`; Lines: 44–57. Explanation: Phục hồi dùng MediaPipe Pose/Tasks lite và góc2D từ tọa độ landmark chuẩn hóa. Giới hạn: Không dùng 3D chuẩn lâm sàng; x/y chuẩn hóa chưa sửa tỷ lệ khung hình; chưa có sai số góc với thước chuẩn.
  - Đối chiếu: `modules/rehabilitation/rehab_engine.py` · `RehabilitationEngine._init_pose` · 531–583 (source_code).
- **C15 — PARTIALLY_IMPLEMENTED**. File: `modules/rehabilitation/rehab_engine.py`; Symbol: `ArmRaiseTracker.process`; Lines: 143–246. Explanation: FSM nâng tay đếm khi nâng rồi hạ; ngưỡng 60/142/130/50°, chấm lỗi khuỷu/đối xứng/hold. Giới hạn: Test landmark tổng hợp; không chứng minh count thực tế. Penalty một số lỗi tăng theo frame, ảnh hưởng FPS. Test hiện có chỉ đưa một trạng thái landmark và assert stage; chưa test toàn chu kỳ rồi đếm.
  - Đối chiếu: `reports/local_stt/rehab-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `tests/test_rehab_assistant.py` · `TestRehabilitationEngine.test_arm_raise_state_machine` · 201–219 (test_source).
- **C16 — PARTIALLY_IMPLEMENTED**. File: `modules/rehabilitation/rehab_engine.py`; Symbol: `SitToStandTracker.process`; Lines: 277–396. Explanation: FSM đứng-ngồi dùng góc gối 155/140/118/125° và dấu đã chạm đáy trước khi đếm. Giới hạn: Test tổng hợp, thiếu góc camera/occlusion thực; ankle thiếu dùng surrogate có thể ảnh hưởng góc. Test hiện có chỉ đưa một trạng thái landmark và assert stage; chưa test toàn chu kỳ rồi đếm.
  - Đối chiếu: `reports/local_stt/rehab-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `tests/test_rehab_assistant.py` · `TestRehabilitationEngine.test_sit_to_stand_state_machine` · 221–238 (test_source).
- **C17 — IMPLEMENTED**. File: `modules/rehabilitation/rehab_engine.py`; Symbol: `MarchingTracker.process`; Lines: 423–488. Explanation: Đi bộ tại chỗ đếm bước trái/phải xen kẽ khi chênh tọa độ gối vượt±0.065; reset stance ở0.035. Giới hạn: Ngưỡng normalized image units; count ngay khi nhấc, không đo quãng đường hoặc năng lực đi lại.
  - Đối chiếu: `reports/local_stt/rehab-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `tests/test_rehab_assistant.py` · `TestRehabilitationEngine.test_marching_state_machine` · 240–252 (test_source).
- **C18 — IMPLEMENTED**. File: `modules/rehabilitation/rehab_session_adapter.py`; Symbol: `RehabSessionAdapter.record_verified_rep`; Lines: 196–290. Explanation: RehabSessionAdapter khóa target snapshot, ghi event idempotent/outbox và completed khi count>=target. Giới hạn: Test DB với rep giả; tag camera là metadata từ caller, không tự xác thực frame/score; race đa writer chưa chứng minh.
  - Đối chiếu: `reports/gemini_intent/realtime-regression.txt` · `module` · 1–2 (existing_test_or_runtime_artifact).
  - Đối chiếu: `modules/rehabilitation/rehab_session_adapter.py` · `RehabSessionAdapter.get_or_create_daily_session` · 126–194 (source_code).
  - Đối chiếu: `tests/test_realtime_sync_12_scenarios.py` · `TestRealtimeSync12Scenarios.test_scenario_03_camera_target_10_reps_auto_completion` · 187–253 (test_source).
- **C19 — PARTIALLY_IMPLEMENTED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._do_update_dashboard_ui`; Lines: 967–1083. Explanation: Dashboard ghi DB theo tổng reps, gồm incorrect_reps; score<=0 được thay 90 và quality_threshold chưa là điều kiện completed. Giới hạn: UI khen hoàn thành không chứng minh mọi lần đúng form. Chưa thấy chặn hardware_valid tại điểm record_verified_rep.
- **C24 — IMPLEMENTED**. File: `services/local_voice/recorder.py`; Symbol: `AudioRecorder`; Lines: 8–71. Explanation: Recorder explicit sounddevice Input Stream, mono/resample16kHz, stop/cancel/bound duration; không nghe nền. Giới hạn: Stream48k→16k đã test bằng mock; physical mic chưa kiểm chứng trong artefact hiện có.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `tests/voice_ai/test_local_voice.py` · `test_recorder_hardware_sample_rate_resampling_bounded_and_close` · 208–234 (test_source).
- **C25 — IMPLEMENTED**. File: `services/local_voice/engine.py`; Symbol: `LocalSttEngine`; Lines: 8–44. Explanation: Engine faster-whisper small multilingual local files only, CPU/int8, beam 1, languagevi, VAD và consume segments ngoài UI. Giới hạn: Có inference file local; audio chuẩn/consent chưa xác minh; không có WER/CER hợp lệ; GPU chưa chạy thành công.
  - Đối chiếu: `reports/local_stt/cpu-final.json` · `module` · 1–145 (existing_test_or_runtime_artifact).
  - Đối chiếu: `reports/local_stt/clean-smoke.txt` · `module` · 1–3 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/local_voice/config.py` · `VoiceConfig` · 7–29 (source_code).
  - Đối chiếu: `services/local_voice/worker.py` · `run_worker` · 8–49 (source_code).
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
- **C34 — IMPLEMENTED**. File: `services/local_voice/controller.py`; Symbol: `VoiceSessionController.start`; Lines: 56–73. Explanation: TTS được suspend khi ghi; nhạc pause; child pyttsx3 local giữ entrypoint frozen riêng. Giới hạn: Phối hợp đã test code/mocks; chưa nghe playbackloa thật; nhắc thuốc/coach active chưa nối toàn bộ TTS callbacks.
  - Đối chiếu: `reports/gemini_intent/intent-and-stt-tests.txt` · `module` · 1–9 (existing_test_or_runtime_artifact).
  - Đối chiếu: `services/local_voice/tts_runtime.py` · `speak` · 5–19 (source_code).
  - Đối chiếu: `app/local_voice_widget.py` · `module` · 1–110 (source_code).
  - Đối chiếu: `tests/voice_ai/test_local_voice.py` · `test_tts_cannot_restart_during_capture` · 194–205 (test_source).
- **C35 — REMOVED**. File: `web/api_router.py`; Symbol: `ApiRouter.handle_request`; Lines: 65–258. Explanation: API STT cũ không còn active: router 410 và factory compatibility disabled; không restore orchestrator cũ. Giới hạn: REMOVED chỉ đường API STT active; file/provider/test legacy vẫn tồn tại, không nói mọi source STT đã xóa.
  - Đối chiếu: `services/voice_ai/asr/factory.py` · `module` · 1–14 (source_code).
  - Đối chiếu: `archive/voice/README.md` · `module` · 1–96 (source_code).
  - Đối chiếu: `tests/voice_ai/test_local_voice.py` · `test_legacy_web_voice_disabled_even_when_local_flag_enabled` · 250–257 (test_source).
- **C36 — DEPRECATED**. File: `services/voice_ai/orchestrator/router.py`; Symbol: `module`; Lines: 1–634. Explanation: Các semantic/orchestrator/voicewidget cũ và Voskarchive không là tuyến nhận giọng active. Giới hạn: TTS coordinator cũ còn được reuse; không quy toàn bộ services/voice_ai thành deadcode.
  - Đối chiếu: `app/voice_button_widget.py` · `module` · 1–266 (source_code).
  - Đối chiếu: `app/local_voice_widget.py` · `module` · 1–110 (source_code).
- **C39 — PARTIALLY_IMPLEMENTED**. File: `app/cognitive_games_widget.py`; Symbol: `CognitiveGamesWidget.__init__`; Lines: 54–80. Explanation: Trò chơi lật cặp/nhớ trình tự dùng rules seededrandom, service/repository; desktop ghi SQLite riêng. Giới hạn: Import sang unified là bước import, chưa thấy live outbox từ gameplay; không có chứng cứ cải thiện nhận thức lâm sàng.
  - Đối chiếu: `modules/cognitive_games/services/game_engine.py` · `GameEngine` · 14–143 (source_code).
  - Đối chiếu: `database/importer.py` · `DataImporter._import_cognitive_games` · 472–541 (source_code).
- **C48 — DEPRECATED**. File: `app/dashboard.py`; Symbol: `DashboardWindow._process_video_frame`; Lines: 530–570. Explanation: Fall/HFD/ONNX/video còn retainedsource/artefacts nhưng không trong camera callbacks dashboard hiện tại. Giới hạn: Deprecated theo dashboard active; toolvideo riêng vẫn có. Không dùng metricfall cũ thay metric rehab hiện tại.
  - Đối chiếu: `core/fall_pipeline.py` · `module` · 1–542 (source_code).
  - Đối chiếu: `modules/fall/hfd_classifier.py` · `module` · 1–85 (source_code).
- **C50 — PARTIALLY_IMPLEMENTED**. File: `AI_Rehab_Safety_Assistant.spec`; Symbol: `module`; Lines: 1–143. Explanation: Spec excludes Gemini SDK/provider/backend env khỏi EXE; chưa build binary kiểm chứng ranh giới này. Giới hạn: Reviewsource recipe thôi, không chứng minh binary không secret. Không đọc .envprivate hoặc tải/cài package trong audit.
- **C55 — UNKNOWN**. File: `reports/local_stt/REPORT.md`; Symbol: `module`; Lines: 1–58. Explanation: Face FAR/FRR, emotion holdout F1, rehab clinical angle error, STT WER và nghiệm thu mic/camera/multi host chưa có bằng chứng phù hợp. Giới hạn: Không có số đo hợp lệ trong các artefact đã đối chiếu; không khẳng định không tồn tại ngoài repo.
  - Đối chiếu: `reports/gemini_intent/REPORT.md` · `module` · 1–75 (source_code).

# STT Zipformer tiếng Việt

STT hiện dùng `sherpa-onnx==1.12.40` và model `sherpa-onnx-zipformer-vi-30M-int8-2026-02-09`, CPU INT8. Model được nạp một lần trong worker; ghi âm vẫn dùng nút micro hiện có.

Chuẩn bị trên máy khác từ thư mục dự án:

```powershell
python -m pip install -r requirements-windows.txt
python scripts/prepare_local_stt.py
```

Script tải bản phát hành chính thức, kiểm tra SHA-256 theo `models/manifest.json`. App chỉ đọc model local, không tự tải lúc mở micro.

Cập nhật các giá trị trong `.env` đang dùng nếu còn cấu hình Whisper cũ:

```dotenv
VOICE_MODEL_PATH=data/models/sherpa-onnx-zipformer-vi-30M-int8-2026-02-09
VOICE_DEVICE=cpu
VOICE_COMPUTE_TYPE=int8
VOICE_CPU_THREADS=4
VOICE_BEAM_SIZE=1
VOICE_MAX_SECONDS=30
```

`VOICE_BEAM_SIZE=1` dùng greedy search; 3 hoặc 5 dùng modified beam search và có thể chậm hơn. `VOICE_COMPUTE_TYPE` được giữ để tương thích cấu hình; lượng tử hóa đã nằm trong các file ONNX. CUDA không được hỗ trợ trong cấu hình INT8 này; cấu hình CUDA cũ sẽ báo lỗi rõ ràng.

Engine giữ dấu và phủ định trong transcript, chuẩn hóa Unicode NFC. Model thường trả chữ hoa và có thể không có dấu câu. Không áp dụng các ngưỡng logprob/no_speech_prob của Whisper lên Zipformer. Chưa tích hợp VAD vào model mới; chỉ bỏ qua silence/DC thuần, nên `speech_duration_ms` là null khi giải mã, bằng 0 cho silence. Tiếng ồn cần kiểm tra trên micro thực tế.

Kiểm thử ngày 24/10/2026: 50 tests đạt, gồm inference thật trên file `test_wavs/0.wav` của upstream. Benchmark 3 lượt với audio 3,74 giây: 171/62/52 ms, cold load 1958 ms trên môi trường phát triển. Đây không phải phép so sánh đối chứng với Whisper hoặc đánh giá WER/CER trên giọng người dùng. Báo cáo: `reports/local_stt/zipformer-benchmark.json`.

Chạy lại benchmark:

```powershell
python scripts/benchmark_local_stt.py path/to/vietnamese.wav --output reports/local_stt/benchmark.json
```

Nguồn model và hướng dẫn upstream:
https://k2-fsa.github.io/sherpa/onnx/pretrained_models/offline-transducer/zipformer-transducer-models.html

Các tài liệu Whisper trước đây là lịch sử triển khai; cấu hình và engine hiện tại theo tài liệu này. Bản portable đã phát hành cần được build lại để chứa runtime/model mới.

## Chuẩn phát hành

Zipformer là STT duy nhất từ bản `6.0.0-zipformer.1`. Đã gỡ faster-whisper và CTranslate2 khỏi môi trường phát triển, cache runtime và hai bộ portable. Hai gói `releases/AI_FOR_EXAM_PT.zip` và `releases/AI_FOR_EXAM_HP.zip` chứa đủ runtime/model để chạy offline. Mở `AICare/AICare.exe` sau khi giải nén toàn bộ. Bản cập nhật tự chuyển đường dẫn model Whisper cũ trong cấu hình portable sang Zipformer.

QA trên máy build cho cả hai bản: launcher self-test, dashboard Qt offscreen, API/auth/shutdown, checksum model, nhận dạng file tiếng Việt bằng Python nhúng, xác nhận không import được faster_whisper/ctranslate2. Chưa thử camera/micro vật lý trên máy Windows sạch.

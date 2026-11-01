# STT local bằng faster-whisper — 09/10/2026

Luồng mới nằm trong `services/local_voice`, độc lập với gateway/semantic cũ. Không dùng API STT, Gemini, Ollama hoặc listener nền. `VOICE_AI_ENABLED=false` không tự chuẩn bị worker khi mở app. Nút Nhận giọng nói luôn hiện ở dưới các tab, phía trên thanh trạng thái. Người dùng có thể nhấn để chuẩn bị local STT cho phiên hiện tại; thao tác này chưa ghi âm. Khi sẵn sàng, nhấn micro lần nữa mới ghi. Endpoint voice legacy trả 410 kể cả khi bật voice desktop.

## Linux đã kiểm tra

Môi trường dự án: `.venv-linux/bin/python`, Python 3.14.4, Linux x86_64. Đã kiểm chứng wheel faster-whisper 1.2.1, CTranslate2 4.8.2, PyAV 18.1.0, sounddevice 0.5.6. PyAV 19.0.1 không tương thích `decode_audio` của faster-whisper 1.2.1 nguyên bản; không dựa vào patch có sẵn trong site-packages dev.

Manifest runtime chính: `requirements.txt`. `requirements-linux.lock` khóa toàn bộ runtime Linux đã cài sạch (Torch CPU); `requirements-local-stt.lock` là closure STT dùng khi kiểm tra riêng thành phần STT. Không áp lock Linux vào Windows hoặc vào môi trường CUDA đang có mà chưa đánh giá khác biệt. Đợt này chỉ đổi PyAV trong venv dự án, không đổi Python/driver/CV/Torch hiện có.

Cài mới Linux CPU trong virtualenv riêng:

```bash
python3 -m venv .venv-linux-clean
.venv-linux-clean/bin/python -m pip install -r requirements.txt -c requirements-linux.lock
.venv-linux-clean/bin/python -m pip check
.venv-linux-clean/bin/python scripts/prepare_local_stt.py
```

Trên venv dự án hiện tại, chạy script bằng `.venv-linux/bin/python`. Model là `Systran/faster-whisper-small`, revision `536b0662742c02347bc0e980a01041f333bce120`, đa ngôn ngữ. Script chuẩn bị tải có chủ đích, lưu `provenance.json`; model weights không commit. Nếu đã có snapshot cache hoàn chỉnh, dùng `HF_HUB_OFFLINE=1 ... scripts/prepare_local_stt.py`. Script không tự cài FFmpeg hoặc sửa driver. Lỗi tải không ảnh hưởng chạy app với voice tắt; sửa kết nối rồi chạy lại script thủ công.

Cấu hình `.env` theo `.env.example`:

```dotenv
VOICE_AI_ENABLED=false
VOICE_MODEL_PATH=data/models/faster-whisper-small
VOICE_DEVICE=cpu
VOICE_COMPUTE_TYPE=int8
VOICE_CPU_THREADS=2
VOICE_MAX_SECONDS=15
VOICE_BEAM_SIZE=1
```

Path tương đối tính từ thư mục chạy app; khởi chạy từ repo root hoặc dùng absolute path của máy triển khai. Thiếu model: micro có trạng thái unavailable và nút thử lại; UI không tải ngầm. Sau khi nghiệm thu máy đích có thể đặt `VOICE_AI_ENABLED=true` để tự chuẩn bị worker, rồi chạy `python main.py` bằng đúng venv.

Micro cần PortAudio ở OS. Máy kiểm tra hiện thiếu thư viện này; pip sounddevice thành công không chứng minh thu âm được. Trên Ubuntu/Debian, chạy trong terminal máy chạy ứng dụng:

```bash
sudo apt-get install libportaudio2
.venv-linux/bin/python scripts/check_local_microphone.py
```

Nhập mật khẩu sudo trực tiếp trong terminal, không gửi qua chat. Đóng hẳn rồi mở lại ứng dụng sau cài. Script chỉ kiểm tra thiết bị, không thu âm. Cài dependency PortAudio qua quản trị máy theo OS trước thử micro; ứng dụng không tự cài thư viện hệ thống. Thiết bị được ghi tại sample rate thật, mono float32, resample về 16 kHz trong worker. Không mô phỏng microphone hay tạo im lặng thay dữ liệu thiết bị.

GPU chỉ dùng khi đã load và transcribe thật với `VOICE_DEVICE=cuda` cùng compute type hỗ trợ. Môi trường kiểm tra không có thiết bị CUDA sử dụng được. CTranslate2 cần CUDA/cuBLAS/cuDNN tương thích; không suy ra từ Torch. Không tự fallback che lỗi GPU: cấu hình GPU lỗi báo unavailable, chọn CPU rồi khởi động lại hoặc thử lại sau sửa môi trường.

## Thao tác và phạm vi câu lệnh

Nhấn micro → ghi; nhấn Dừng → xử lý; Hủy bỏ phiên/kết quả; tự dừng sau 15 giây. Worker process persistent sở hữu một model và một micro, xử lý tuần tự. Recording/model/resample/inference/consume generator đều ngoài UI thread. Đóng app dừng micro/worker, join có timeout rồi terminate/kill riêng process nếu native inference chưa trả. Không dùng QThread.terminate.

TTS coordinator dừng playback đang có và chặn playback mới trong lúc ghi; không tự phát lại lời nói cũ. Nhạc thư giãn đang phát được tạm dừng qua handler hiện có, người dùng tiếp tục bằng nút. Context thuốc/plan/tab/patient thay đổi hủy phiên; lúc inference native chưa trả, micro vẫn bận tới khi worker xác nhận hủy. Có epoch để đổi hồ sơ/tab/bài tập đi rồi quay lại cũng làm phiên cũ vô hiệu.

| Context | Câu rõ được hỗ trợ | Điều kiện |
|---|---|---|
| Hồ sơ hợp lệ | Về trang chính | Identity dashboard và TodayTodo trùng nhau |
| Tab Việc hôm nay | Tôi đã uống rồi / Tôi đã uống thuốc rồi | Chỉ một lần uống đang nhắc; xác nhận bằng nút với tên thuốc/liều/thời điểm |
| Tab Việc hôm nay | Nhắc lại sau | Chỉ một lần uống, chưa OVERDUE như nút hiện có |
| Tab Việc hôm nay | Tôi cần hỗ trợ | Chỉ một lần uống; tạo yêu cầu hỗ trợ qua service hiện có |
| Tab Phục hồi | Bắt đầu bài tập | Camera được chọn, kế hoạch active và version còn khớp |
| Tab Phục hồi | Tạm dừng | Đang tập và chưa pause; cùng handler nút Tạm dừng/Tiếp tục |

Resolver giữ dấu tiếng Việt, không xóa phủ định, chỉ khớp câu hoàn chỉnh. Câu hỏi, câu nhiều ý, phủ định, mơ hồ và “tập xong rồi” không thực thi. Không hỗ trợ hội thoại tự do, chọn tên thuốc/số lượng từ lời nói, hoặc gọi bác sĩ chưa có flow rõ.

Transcript chỉ hiển thị, không lưu vào bảng y tế. Dispatcher kiểm tra lại snapshot, thuốc kiểm tra atomically dưới transaction SQLite trước ghi. Cùng `ElderSyncClient.confirm_dose_taken` với nút tay, dùng client_event_id/session chống trùng; outbox source=voice, không lưu transcript/audio. Voice offline hoặc lỗi transaction không phát lại sau reconnect/restart; nút bấm giữ cơ chế offline hiện có. “Đã ghi nhận” chỉ là commit hệ thống, không khẳng định email đã giao. Camera vẫn ghi từng rep và quyết định `camera_verified_completed`.

## Kiểm tra triển khai

```bash
# Chỉ dùng WAV được cho phép kiểm thử; không coi tone/TTS là giọng thật nghiệm thu.
.venv-linux/bin/python scripts/benchmark_local_stt.py path/to/consented.wav --repeats 10
.venv-linux/bin/python scripts/benchmark_local_stt.py path/to/consented.wav --device cuda --compute-type float16 --camera 0
LOCAL_STT_TEST_MODEL=data/models/faster-whisper-small \
  .venv-linux/bin/python -m pytest tests/voice_ai/test_local_voice.py tests/voice_ai/test_faster_whisper_real.py
VOICE_MODEL_PATH=data/models/faster-whisper-small HF_HUB_OFFLINE=1 \
  .venv-linux/bin/python scripts/smoke_local_voice_ui.py
```

Để chạy assertion audio thật, thêm `LOCAL_STT_TEST_WAV` và `LOCAL_STT_TEST_EXPECTED` với câu đọc chuẩn. Benchmark camera script chỉ đo capture/read, chưa đại diện pipeline camera + face/emotion/rehab đầy đủ. Cần baseline và khi inference cùng pipeline thật trước kết luận giảm FPS ≤15%.

## Windows

`requirements-windows.txt` đã thêm faster-whisper/PyAV/sounddevice/TTS. Portable setup hiện có cài manifest này; chuẩn bị model riêng bằng `.venv\Scripts\python.exe scripts\prepare_local_stt.py`, cấu hình path tương ứng. Spec đã thêm thu thập runtime assets/native libraries của STT, gồm Silero VAD. Không nhúng weights. Chưa chạy cài sạch Windows, thử DLL/CUDA/PortAudio, build hoặc installer; không coi Linux pass là Windows pass. Frozen TTS có entrypoint --local-tts trước Qt/CV; vẫn cần kiểm tra âm thanh trên Windows thật.

Nguồn: [README faster-whisper 1.2.1](https://github.com/SYSTRAN/faster-whisper/blob/v1.2.1/README.md), [model small](https://huggingface.co/Systran/faster-whisper-small).

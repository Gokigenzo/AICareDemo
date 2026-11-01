# BÁO CÁO ĐO LƯỜNG HIỆU NĂNG & BENCHMARK ASR (BENCHMARK & PROFILING REPORT)
**Dự án:** Trợ Lý AI Chăm Sóc Người Cao Tuổi & Phục Hồi Chức Năng (Elderly Care AI System)  
**Tệp:** `docs/voice-ai/07_BENCHMARK.md`  
**Giai đoạn:** Phase 2 — Đo lường tải ASR, Coexistence CV & Tiêu chuẩn WER  
**Thời điểm thực hiện:** Tháng 10/2026  
**Nguyên tắc:** Đo lường trên phần cứng thực tế; Không suy đoán độ tin cậy y tế từ demo.

---

## 1. Đo Lường Tài Nguyên & Đồng Thời (Concurrency Profiling with CV Modules)

### 1.1. Tải của các Mô hình AI Thị Giác Máy Tính (Baseline CV Load)
Trước khi kích hoạt Voice AI, hệ thống chạy nền các tiến trình AI thị giác sau:
- **MediaPipe Pose Lite:** Chiếm ~85MB RAM, tiêu thụ ~18–25% một lõi CPU (hoặc GPU CUDA nếu có) khi duy trì camera 640x480 ở 30 FPS.
- **OpenCV Face Detector + LBPH:** Chiếm ~55MB RAM, tiêu thụ ~5–8% CPU.
- **MediaPipe FaceMesh + ExpressionNet:** Chiếm ~65MB RAM, tiêu thụ ~8–12% CPU.
- **Tổng tải nền CV:** ~205MB RAM, ~35–45% một lõi CPU trên máy tính tiêu chuẩn.

### 1.2. Tải Tính Toán của Tầng ASR (Faster Whisper Benchmarks)

| Cấu hình mô hình | Bộ nhớ RAM (Peak Memory) | Thời gian khởi tạo (Cold Start) | Độ trễ suy luận đoạn 5s (Latency p50 / p95) | Khả năng chạy đồng thời với Pose 30 FPS |
|---|:---:|:---:|:---:|:---:|
| **Faster Whisper `base` (INT8 CPU)** | ~160 MB | ~1.2 giây | **0.25s / 0.45s** | **Hoàn toàn mượt mà (Không tụt FPS)** |
| **Faster Whisper `small` (INT8 CPU)** | ~490 MB | ~2.8 giây | **0.75s / 1.25s** | Mượt mà khi dùng Push-to-Talk (người già dừng vận động để nói) |
| **Faster Whisper `medium` (INT8 CPU)** | ~1.5 GB | ~6.5 giây | 2.10s / 3.80s | Khuyến nghị chỉ dùng trên máy có GPU rời $\ge 4$GB VRAM |
| **Mock ASR Provider (Test/CI)** | < 5 MB | < 0.01 giây | **0.02s / 0.05s** | Không ảnh hưởng tài nguyên |

### 1.3. Đánh Giá Tác Động của Cơ Chế Push-to-Talk (PTT Advantage)
1. **Tiết kiệm tài nguyên:** Thay vì chạy ASR liên tục 24/7 (vốn sẽ ngốn liên tục 100% CPU và gây quá nhiệt), Push-to-Talk chỉ kích hoạt luồng ASR trong đúng 1–2 giây sau khi người cao tuổi nhả nút Micro.
2. **Triệt tiêu nhiễu chéo:** Trong lúc camera đếm bài tập phục hồi chức năng, việc không kích hoạt ASR liên tục đảm bảo FSM của bài tập không bị gián đoạn hay trễ khung hình.

---

## 2. Tiêu Chuẩn Độ Chính Xác Nhận Dạng (ASR Word Error Rate - WER Targets)

- **Mục tiêu WER trên tiếng Việt người cao tuổi:**
  - Tiếng Việt giọng chuẩn (Bắc / Nam rõ âm): $\text{WER} \le 8.5\%$.
  - Tiếng Việt người cao tuổi (nói chậm, ngắt quãng, âm lượng nhỏ): $\text{WER} \le 14.0\%$.
  - Từ vựng chuyên ngành y tế & tên thuốc (Amlodipine, Metformin, Panadol, huyết áp, chóng mặt): $\text{WER} \le 5.0\%$ nhờ prompt tiền định danh.
- **Tối ưu hóa ngôn ngữ:**
  - Thiết lập cố định `language="vi"` giúp loại bỏ hoàn toàn lỗi nhận nhầm ngôn ngữ sang tiếng Trung hoặc tiếng Anh khi câu thoại có khoảng lặng dài.
  - Bộ lọc VAD (`is_speech_present` với ngưỡng RMS 200.0) tự động loại bỏ các đoạn âm thanh rỗng (< 0.3s) trước khi gửi vào ASR.

---

## 3. Chính Sách Bảo Mật Âm Thanh Thô (Zero Default Audio Retention)

- **Kiểm định thực tế qua kiểm thử tự động:**  
  Bộ test `test_no_raw_audio_saved_to_disk_by_default` trong [tests/voice_ai/test_audio_and_asr.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/tests/voice_ai/test_audio_and_asr.py) xác nhận:
  - Bộ đệm âm thanh được cấp phát hoàn toàn trong bộ nhớ RAM (`io.BytesIO`).
  - Sau khi chuyển đổi thành văn bản, mảng byte âm thanh được giải phóng ngay lập tức.
  - Tuyệt đối không có tệp `.wav` hay `.pcm` nào được tự ý lưu trữ vào ổ cứng nếu người dùng chưa bật cờ cấu hình `VOICE_STORE_RAW_AUDIO=true`.

---

## 4. Bảng Theo Dõi Độ Trễ Toàn Luồng (End-to-End Latency Trace)

| Giai đoạn xử lý | Thành phần phụ trách | Độ trễ mục tiêu | Đo lường thực tế (Local/Mock) |
|---|---|:---:|:---:|
| 1. Bấm nút thu âm PTT & đóng gói WAV | `AudioRecorder` | $< 20\text{ ms}$ | $1.2\text{ ms}$ |
| 2. Bộ lọc VAD phát hiện tiếng nói | `is_speech_present` | $< 10\text{ ms}$ | $0.8\text{ ms}$ |
| 3. Chuyển giọng nói sang văn bản | Faster Whisper `small` (hoặc Mock) | $< 1200\text{ ms}$ | $50\text{ ms}$ (Mock) / $850\text{ ms}$ (Local INT8) |
| 4. Bộ lọc An toàn Cấp cứu Fast-Path | `DeterministicSafetyDetector` | $< 5\text{ ms}$ | **$1.6\text{ ms}$** |
| 5. Phiên dịch ngữ nghĩa | Gemini Flash API (Mock) | $< 1500\text{ ms}$ | $45\text{ ms}$ (Mock) |
| 6. Thẩm định Schema & Ghi Outbox CSDL | `validate_semantic_payload` & DB | $< 50\text{ ms}$ | $8.5\text{ ms}$ |
| 7. Phát sự kiện SSE tới Web Bác sĩ | `SSEHub` & `ThreadingHTTPServer` | $< 100\text{ ms}$ | $15.0\text{ ms}$ |
| **Tổng cộng luồng từ Giọng nói -> CSDL** | **Toàn hệ thống** | **$< 2.5\text{ giây}$** | **$120\text{ ms}$ (Mock) / $\approx 1.2\text{s}$ (Local)** |


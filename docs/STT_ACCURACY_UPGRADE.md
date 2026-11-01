# STT tiếng Việt — 16/10/2026

## Thay đổi

- Bản chạy ở ổ D: Whisper Small CPU int8, beam 1 → Whisper Medium GPU float16, beam 5.
- Mô hình Systran/faster-whisper-medium, revision cố định `08e178d48790749d25932bbc082711ddcfdfbc4f`. Giữ nguyên model Small để có thể hoàn nguyên.
- Chỉ nhận dạng tiếng Việt; giải mã xác định (temperature 0), không kế thừa nội dung lần nói trước.
- Bỏ DC, nâng nhẹ giọng nhỏ tối đa 4 lần, giới hạn biên độ. Không lọc phổ mạnh hoặc sửa từ theo từ điển.
- VAD threshold 0.4, giữ đệm 400 ms, khoảng nghỉ 1 giây. Giới hạn mỗi bản ghi tăng lên 30 giây.
- Chặn đoạn có điểm nhận dạng thấp, xác suất không có giọng nói cao hoặc lặp bất thường. Chuẩn hóa Unicode NFC nhưng không tự thay thế từ, số hay phủ định.
- Mô hình và âm thanh được xử lý cục bộ; thao tác yêu cầu xác nhận vẫn đi qua luồng xác nhận hiện có.

## Đo trước / sau

5 mẫu công khai (90 từ tham chiếu, dài 2,74–7 giây), cùng âm thanh đầu vào:

| Bản | Lỗi từ (WER) | Trung bình thời gian nhận dạng |
|---|---:|---:|
| Small CPU beam 1 | 18/90 = 20% | 9,50 giây |
| Medium GPU beam 5 + xử lý mới | 10/90 = 11,11% | 2,93 giây |

Thời gian không gồm tải mô hình lần đầu. Nguồn mẫu: https://huggingface.co/datasets/dinhlam2210/voice-Viet-Nam . Tham chiếu giữ nguyên như bộ dữ liệu, có thể có lỗi chính tả và khác cách viết số (ví dụ “một hai” / “1-2”). WER bỏ dấu câu, không bỏ dấu tiếng Việt. Đây chỉ là kiểm tra nhỏ, không phải cam kết độ chính xác trên giọng người cao tuổi, mọi vùng miền hoặc môi trường có tiếng ồn. Không sử dụng bản ghi riêng tư của người dùng.

Chi tiết từng mẫu: `runtime/stt-upgrade/comparison.json` trong bản chỉnh sửa ở ổ C. Kiểm chứng mã triển khai: `runtime/stt-upgrade/deployed-verification.json`.

45 kiểm thử về tiền xử lý, tham số giải mã, dấu/phủ định, hủy phiên, đổi người bệnh, xác nhận và ghi dữ liệu. Fixture kiểm thử đã được bổ sung dữ liệu thuốc thử nghiệm khi thiếu cơ sở dữ liệu legacy; không thay đổi dữ liệu thật.

## Vận hành

Trong `runtime/.env` ở ổ D: model `data/models/faster-whisper-medium`, device `cuda`, compute `float16`, beam `5`, max `30`, CPU threads `4`. Chuẩn bị worker lúc mở app; không tự mở micro. Nhấn micro, chờ trạng thái Đang nghe rồi nói và nhấn Dừng khi xong. Lần mở đầu có thể chậm hơn do tải mô hình.

Nếu chuyển sang máy không có CUDA tương thích, đặt `VOICE_DEVICE=cpu` và `VOICE_COMPUTE_TYPE=int8`, rồi khởi động lại. Chuẩn bị model có revision cố định bằng `scripts/prepare_local_stt.py --model medium`.

Tài liệu tham số: https://github.com/SYSTRAN/faster-whisper ; https://github.com/SYSTRAN/faster-whisper/blob/master/faster_whisper/transcribe.py .

> HISTORICAL ARCHIVE: Fall Detection is retired from the main application. These results do not validate the medication reminder module.

# Báo cáo kỹ thuật Fall Detection — 02/10/2026

**FAIL trên ca hồi quy phát hiện ngã; NOT VERIFIED cho vận hành thực tế. Chỉ chạy thử, chưa bật Gmail thật.**

Lõi mới có cùng detector/tracker/feature/FSM cho camera và video, nhưng detector HOG + MediaPipe trên crop không quan sát đủ khớp của hai người trong clip nguồn. Không tuyên bố thuật toán chính xác chỉ vì test phần mềm qua hoặc không có cảnh báo giả.

## Bằng chứng thực tế

- Clip gốc tìm được và khớp SHA-256 `5c70f33ed96d96bc8a306bc370a835c86a7c33db2404a1549caaa0aca614a5b4`.
- Baseline 5 lượt sạch state: mỗi lượt có track P2 lúc 15,77 s và P3 lúc 18,18 s. Không tái hiện mốc cảnh báo sớm 9,59/10,93 s trong mã hiện tại; log cũ không có commit/config để truy nguyên chắc chắn.
- Decoder đọc được 498 frame, metadata ghi 500: kiểm tra số frame FAIL. PTS cuối 20,7290416667 s.
- Candidate chung HOG/pose: xem đủ 5 lượt và số liệu máy thật trong [BEFORE_AFTER.md](../reports/fall_detection/BEFORE_AFTER.md). Các lượt ghi 0 sự kiện, bỏ sót hai nhãn ngã đang có. Đây là kết quả thất bại, không phải bằng chứng không báo sai.
- Nhãn `GT_MAN`/`GT_WOMAN` mới tách khỏi track, nhưng chưa có bbox thời gian, hai người gán nhãn độc lập và adjudication. Ghép theo trái/phải cố định trong evaluator cũ không còn được dùng.
- FP/giờ trên video âm tính độc lập, ID switches thực tế và khả năng khác góc máy: NOT VERIFIED vì chưa có dữ liệu phù hợp.

## Mã đang chạy

`FramePacket` → `PersonPoseBackend` (HOG multi-person, NMS, MediaPipe stateless mỗi crop) → Hungarian association → feature chuẩn hóa theo kích thước người → FSM từng track theo PTS → `FallEvent(run_id,track_id,episode)`.

Camera dùng thời điểm capture monotonic; video dùng PTS decoder, không dùng đồng hồ UI hoặc frame-index/FPS. Tư thế không thấy đủ khớp là UNOBSERVABLE, feature không biết là null. Xác nhận cần chuyển upright→low và vận tốc đi xuống, không chỉ thấy nằm hoặc mất người. Dedupe từng episode; phục hồi có quan sát mới kết thúc episode.

Vùng pixel của hiên/lan can, ngưỡng centroid 140 px và ghép GT bằng x=560 chỉ còn trong baseline tham chiếu. Không áp dụng chúng cho camera khác. HOG chưa phù hợp để xác nhận ngã nằm/khuỵu và không được nghiệm thu làm detector vận hành.

## Giao diện, đánh giá và cảnh báo

- Overlay, track list và timeline dùng cùng track_id và trạng thái trong bộ nhớ. EOF trả frame sạch và bỏ hộp hiện tại. Unicode dùng drawing helper có font tiếng Việt.
- Restart/seek tạo run mới; seek dựng lại lịch sử từ đầu. Report được lưu ở EOF/xuất thủ công, không phải mỗi sáu frame. Seek đồng bộ còn hạn chế độ đáp ứng trên clip dài.
- Evaluator ghép một-một đúng subject bằng bbox/PTS và cửa sổ quanh impact; không suy danh tính từ số track. Báo riêng `slip→confirmed`, `impact→confirmed`, `suspected→confirmed` và giữ độ trễ có dấu. Thiếu bằng chứng hoặc mẫu số thì null/N/A.
- Video bị chặn SMTP ngay dispatch, kể cả cấu hình email bật. Test và batch kiểm tra SMTP count=0 và hash dữ liệu live không đổi. Camera hiện cũng chỉ ghi nhận sự kiện thử, không gửi Gmail hay ghi sự kiện bệnh nhân.
- SMTP_ACCEPTED chỉ là server nhận thư; delivered_unknown không khẳng định người nhận đã đọc/nhận. Retry kết nối có giới hạn, idempotency trong process; chưa có đảm bảo qua crash/restart.

## Hồ sơ bàn giao

- [Danh sách file, đường gọi, cấu hình, lệnh Windows và giới hạn](fall_detection/IMPLEMENTATION_NOTES.md).
- [Bảng trước/sau, hiệu năng, ma trận T01–T09 và kết quả test thực tế](../reports/fall_detection/BEFORE_AFTER.md).
- [Nhãn v2 chưa kiểm định](../data/video_annotations/elderly_fall_v2.json) và [quy trình gán nhãn](../data/video_annotations/ANNOTATION_PROTOCOL.md).
- [Manifest, events, matches, metrics, PTS và trace từng run](../reports/fall_detection).
- [Báo cáo cũ lưu để đối chiếu, không dùng nghiệm thu](fall_detection/LEGACY_REPORT_UNVERIFIED.md).

Không có bằng chứng xác nhận lâm sàng, loại bỏ mọi báo động giả hay đảm bảo phát hiện mọi cú ngã. Cần detector phù hợp hơn, dữ liệu độc lập được gán nhãn và ngưỡng recall/FP/độ trễ/hiệu năng được thống nhất trước khi xem kết quả kiểm định cuối.

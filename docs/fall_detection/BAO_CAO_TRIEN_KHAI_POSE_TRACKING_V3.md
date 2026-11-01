> HISTORICAL ARCHIVE: Fall Detection is retired from the main application. These results do not validate the medication reminder module.

# Kết quả triển khai pose và tracking v3

Ngày 02/10/2026. **Đã triển khai bản thử nghiệm; mục tiêu nhận diện hai ca ngã trong clip chưa đạt. Không đủ bằng chứng để đưa vào vận hành cảnh báo thật.**

## Thay đổi đã thực hiện

- Backend pose nhiều người YOLO11, detector + MediaPipe đối chứng, ONNX CPU; chỉ nạp model có sẵn tại máy, không tự tải khi chạy ứng dụng. `auto` ưu tiên ONNX nano, sau đó PyTorch nano và HOG dự phòng. Model và dependency tùy chọn không được đưa vào Git; máy khác cần chuẩn bị chúng theo hướng dẫn dưới đây.
- Ánh xạ 17 khớp COCO vào hợp đồng 33 landmark; khớp không đo được có visibility bằng 0. Pose một phần sử dụng vai/hông còn quan sát được, không suy diễn khớp bị che.
- Tracking và FSM theo từng người dùng timestamp nguồn; thêm ngã từ ghế, chuyển động hông tích lũy, dáng thấp, xử lý khoảng trống quan sát và nằm sẵn từ đầu. Giữ tracker Hungarian hiện có; chưa triển khai/đối chứng ByteTrack hay appearance re-identification.
- Thông báo `NEEDS_CHECK` cho mất quan sát hoặc tư thế thấp chưa đủ bằng chứng, tách khỏi sự kiện ngã xác nhận. Thông báo có thể được giải quyết khi quan sát ổn định trở lại. ID track là ID kỹ thuật, không phải danh tính người bệnh.
- UI live/video, timeline và báo cáo xuất thông báo kiểm tra, metadata model, diagnostics. Backend silhouette có ràng buộc seed từ detector và chuyển động toàn cảnh, chỉ là phương án thử nghiệm, không bật mặc định.
- Công cụ benchmark, replay cùng cache để ablation, công cụ gán nhãn HTML và manifest phân chia dữ liệu. Spec đóng gói chính bổ sung ONNX/core/scipy và chỉ chọn model nano; chưa build hay nghiệm thu executable.

## Bằng chứng trên video nguồn

Video nguồn: `Elderly Couple Slips and Falls Outside Front Door - 1498633 - RM Videos (720p, h264).mp4`, SHA-256 `5c70f33ed96d96bc8a306bc370a835c86a7c33db2404a1549caaa0aca614a5b4`. `Check_fall.mp4` là bản ghi màn hình UI, không dùng làm tập accuracy.

Tất cả backend dưới đây xử lý 498 frame giải mã của cùng video. FPS trong bảng đo **suy luận backend**, không phải tốc độ camera/UI. Điều kiện máy và tải lúc đo không hoàn toàn giống nhau; dùng để sàng lọc, chưa coi là benchmark triển khai có kiểm soát.

| Backend | Frame có người / 498 | Observation | Pose đủ khớp / torso dùng được | FPS suy luận | p95 suy luận | Ngã xác nhận |
|---|---:|---:|---:|---:|---:|---:|
| HOG + MediaPipe | 41 | 43 | 0 / 1 | 4,51 | 364,72 ms | 0 |
| YOLO11n pose PyTorch | 464 | 814 | 87 / 329 | 10,70 | 161,09 ms | 0 |
| YOLO11s pose PyTorch | 463 | 811 | 79 / 308 | 4,95 | 341,61 ms | 0 |
| YOLO11n proposals + MediaPipe | 464 | 814 | 4 / 233 | 4,41 | 451,38 ms | 0 |
| YOLO11n pose ONNX | 464 | 814 | 87 / 329 | 16,76 | 97,62 ms | 0 |

Nguồn: thư mục `reports/fall_detection/backend_hog`, `backend_nano`, `backend_small`, `backend_hybrid_retry`, `backend_onnx`. Các số đếm phản ánh đầu ra model, **không phải precision/recall người được gán nhãn**. Cache ablation và phép thử silhouette cũng chưa tạo được sự kiện ngã xác nhận. Các phép dò model lớn hơn, độ phân giải cao hơn và xoay ảnh không giải quyết được người nằm bị che khuất; không chọn chúng làm mặc định.

Lần chạy pipeline cuối `fusion_v3_onnx_final_01`: 498 frame, **0 sự kiện**, 13,23 FPS xử lý file, p50 66,22 ms, p95 118,59 ms, RSS đỉnh 439.828.480 byte. SMTP 0 lần; hash dữ liệu người dùng/sự kiện/shared trước và sau không đổi. Container báo 500 frame, decoder đọc 498; gate số frame vẫn FAIL, chưa kết luận nguyên nhân. Số liệu latency là thời gian xử lý frame file, **không đo tuổi frame live**.

Đối chiếu hai sự kiện nhãn cũ: 0 TP, 2 FN. Nhãn thời gian cũ chưa được review độc lập, thiếu bbox theo người, nên accuracy vẫn **NOT VERIFIED**. Không suy ra độ an toàn từ 0 false positive trên clip ngắn; không coi nhiều thông báo mất dấu là hai ca ngã được tìm thấy.

## Trạng thái kế hoạch P0–P5

| Giai đoạn | Trạng thái thực tế | Việc còn thiếu |
|---|---|---|
| P0 chẩn đoán | Có trace và đối chứng | Detector mất người khi nằm/che khuất vẫn chưa khắc phục |
| P1 dữ liệu | Có manifest và công cụ gán nhãn | Review độc lập, bbox/visibility/onset/impact/rest, tập heldout 50 sự kiện và 10–30 giờ âm tính |
| P2 backend | Đã sàng lọc các backend trên clip phát triển | Model phù hợp người nằm/che khuất và so sánh tracker độc lập |
| P3 fusion | Đã triển khai prototype pose một phần + dáng người | Kiểm chứng ablation trên dữ liệu độc lập; silhouette chưa có lợi ích chứng minh |
| P4 FSM/cảnh báo | Đã triển khai và kiểm thử hợp đồng | Tinh chỉnh trên train/dev có nhãn, replay heldout; snapshot/clip sự kiện và durable delivery chưa hoàn tất |
| P5 nghiệm thu | **Chưa đạt** | Recall clip, heldout accuracy/FP mỗi giờ, live frame-age, soak camera và executable |

Không thay ngưỡng theo clip để tạo kết quả 2/2 giả. Hướng tiếp theo là gán nhãn độc lập trước, bổ sung dữ liệu người nằm/cúi/ngồi/ngã chậm/che khuất, fine-tune detector/pose trên train có quyền sử dụng, chọn model bằng dev rồi giữ kín heldout. Mất dấu không đủ để kết luận người đã ngã.

## Chạy và kiểm chứng

Trong môi trường Windows hiện có, cài dependency riêng để tránh tự nâng NumPy hoặc cài thêm OpenCV chồng nhau:

```powershell
.venv/Scripts/python.exe -m pip install --no-deps -r requirements-fall-onnx.txt
# Chỉ cần cho thí nghiệm PyTorch/export:
.venv/Scripts/python.exe -m pip install --no-deps -r requirements-fall-pose.txt
# Export còn cần onnx==1.17.0.
.venv/Scripts/python.exe scripts/export_fall_pose_onnx.py modules/fall/models/yolo11n-pose.pt
.venv/Scripts/python.exe scripts/run_fall_checks.py --pattern test_fall_fusion_v3.py
.venv/Scripts/python.exe scripts/evaluate_fall.py '<video-nguon>' --backend onnx --weights modules/fall/models/yolo11n-pose.onnx --phase trial --repeats 1
```

Weights gốc và hash nằm trong `modules/fall/models/manifest.json`; ONNX được export từ nano local, dynamic, opset 17, không simplify. Các file model là tài sản local bị gitignore. Backend tự kiểm tra file tồn tại; không tự download dependency/model lúc suy luận. Đọc điều kiện sử dụng model trước khi phân phối sản phẩm; chưa thực hiện nghiệm thu phân phối.

Mở `reports/fall_detection/annotation_bundle_v3/index.html` để review ảnh nguồn và xuất nhãn. Đây là **SINGLE_REVIEW_DRAFT**, không tự chuyển thành nhãn đã được adjudicate. Dataset manifest không có heldout/negative độc lập ở thời điểm này.

Kiểm thử phần mềm: 22 fusion/backend, 24 core, 1 UI, 12 safety đã chạy qua harness cô lập, không failure/error/skip ở kết quả đạt. Chúng kiểm tra hợp đồng và an toàn thử nghiệm, không chứng minh accuracy. Báo cáo đo cuối và các cache được lưu trong codebase để truy vết; camera thật và SMTP thật chưa chạy.

Tài liệu kỹ thuật model chính thức: [Ultralytics pose](https://docs.ultralytics.com/tasks/pose/). Các thử nghiệm vẫn sử dụng nhánh `DRY_RUN_NOT_VALIDATED`; chưa đủ điều kiện bật cảnh báo ngã thực tế.

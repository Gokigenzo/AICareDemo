> HISTORICAL ARCHIVE: Fall Detection is retired from the main application. These results do not validate the medication reminder module.

# Kết quả tích hợp HumanFallDetection

Ngày 02/10/2026. **Đã tích hợp backend và classifier thử nghiệm vào hệ thống. Chức năng nhận diện hai ca ngã trong clip vẫn FAIL; chưa đủ điều kiện dùng làm hệ thống cảnh báo thật.**

## Sử dụng bản tích hợp

Môi trường và model đã được chuẩn bị trên máy hiện tại. Chạy `START_HFD.bat` để mở ứng dụng với HumanFallDetection cho live và video; launcher giữ email disabled và pipeline giữ trial-only. Không tự mở camera trong repo upstream.

Trong ứng dụng đang chạy bình thường, vào chế độ thử video, chọn **HumanFallDetection · thử nghiệm** trong dropdown backend rồi chọn file. Chọn **OpenPifPaf + FSM · đối chứng** để thử pose mới với policy v3. Backend HFD không được tự đặt làm mặc định cho mọi lượt chạy vì chưa đạt nghiệm thu. Đổi lựa chọn rồi nạp lại file; chỉ đổi dropdown không thay model của session đang chạy.

Trên máy mới, có runtime ứng dụng và `uv`, chạy:

```powershell
powershell -File scripts/setup_hfd.ps1
.venv/Scripts/python.exe scripts/evaluate_fall.py '<video-nguon>' --backend hfd --phase hfd_trial --repeats 1
.venv/Scripts/python.exe scripts/run_fall_checks.py --pattern test_hfd_integration.py
```

Setup tải dependency/model một lần, pin môi trường riêng, kiểm hash checkpoint pose và kiểm sai số ONNX. Runtime không tự tải. LSTM local `modules/fall/models/hfd_lstm.sav` được sao chép từ repo clone, kèm license/manifest; backend không phụ thuộc việc import chương trình demo upstream. Checkpoint pose/ONNX và `.cache` là tài sản local gitignored, cần setup lại trên máy khác. `FALL_HFD_ENGINE=auto` dùng ONNX đúng kích thước đã export, nếu không có thì dùng PyTorch và ghi backend thực tế trong metadata; `onnx` yêu cầu export đúng kích thước và báo lỗi nếu thiếu.

## Những gì đã thay đổi

- Khôi phục implementation tương thích `modules/fall/fall_detector.py` từ HEAD vì file bị xóa. Bổ sung hợp đồng quan sát và khởi tạo legacy detector theo nhu cầu; live chỉ chạy shared core, không tạo hai model pose khi startup.
- Worker riêng Python 3.9.25, OpenPifPaf 0.12.14, torch 1.10.2 CPU, torchvision 0.11.3 CPU. Giữ nguyên dependency `.venv` chính. Truyền frame BGR nguyên bản qua pipe có giới hạn kích thước, trả COCO17/visibility/bbox với source/run/frame/PTS; không gọi CLI demo, VideoCapture hay imshow của repo.
- Feature extractor giữ năm đặc trưng và phương trình upstream, gồm grouping `gf` cũ để checkpoint parity. Tách tọa độ overlay đã bỏ pad khỏi tọa độ padded legacy dùng cho model. Giữ mode màu BGR vào PIL như upstream; chưa tự chuyển RGB rồi tuyên bố cùng model.
- LSTM 5 input, 48 hidden, 2 tầng, 7 logits, inference từng bước với hidden state riêng theo track. Nạp state dict strict/weights-only. Class 0 được lấy theo inference map upstream, training label metadata và xác suất hiệu chuẩn chưa được xác minh.
- Không force-complete joint bị thiếu. Kiểm tra head/neck/hip, hữu hạn và khoảng thời gian; thiếu/ambiguity/gap hủy xác nhận và reset state. Warm-up, persistence theo PTS, cooldown và event dedupe là policy trial. Không dùng logit .4 upstream như probability; score .5, warm-up 1 giây và thời gian xác nhận hiện tại đều là provisional, chưa được chọn trên heldout.
- Thêm pose affinity của vai/hông cho association HFD, giảm biến động do bbox pose nhỏ/thiếu chân. Track ID vẫn là ID kỹ thuật; chưa có spatial GT để nghiệm thu identity switches/fragmentation.
- Live/video dùng cùng `FallPipeline`; live báo `MODEL_UNAVAILABLE`, có retry giới hạn thay vì khởi tạo lỗi ở mọi frame. Thử video HFD nạp/chạy/restart/seek qua QThread, một tác vụ mỗi lúc, không truy cập widget trong worker. Hủy nguồn/đóng ứng dụng đóng process và join; startup/stop vẫn có timeout hữu hạn, chưa có soak camera thật.
- Khi video có event xác nhận, lưu snapshot và AVI quanh event bằng buffer JPEG giới hạn, kèm timeline PTS nguồn. Khoảng trống dài thể hiện bằng frame đen, không giả quan sát cũ. Đã kiểm thử bằng event tổng hợp; clip thật không tạo event nên không có snapshot ngã thật để nghiệm thu.
- Spec đóng gói chính bổ sung module/worker script/weights/license. **Worker Python ngoài executable vẫn cần được chuẩn bị hoặc cấu hình qua `FALL_HFD_PYTHON`; chưa build clean standalone hoặc phân phối sản phẩm.**

## Kết quả chạy thật

Nguồn raw SHA-256 `5c70f33ed96d96bc8a306bc370a835c86a7c33db2404a1549caaa0aca614a5b4`. Bản ghi màn hình `Check_fall.mp4` không dùng làm tập accuracy. Decoder đọc 498 frame, container báo 500; gate số frame vẫn FAIL và chưa xác định nguyên nhân.

| Lượt chạy | Phạm vi | Kết quả |
|---|---|---|
| `hfd_smoke_fixed_01` | Pipeline OpenPifPaf PyTorch trước tối ưu/parity preprocessing cuối | 498 frame, 0 event, 0,96 FPS, p95 xử lý 1.959,88 ms |
| `hfd_final_backend` | Cache backend ONNX + decoder, 498 frame | 565 observation, 383 frame có người, 274 torso dùng được theo ngưỡng .5, 2 pose đủ 8 khớp; 2,45 FPS suy luận, 0 event |
| `hfd_final_ablation` | Replay cùng cache: full pose, partial pose, fusion, HFD LSTM | Mọi phương án 0 event; thông báo mất dấu được giữ riêng, không tính thành ngã |
| `hfd_release_candidate_01` | Pipeline cuối, pose affinity + LSTM + evidence buffer | 498 frame, 0 event, **4,49 FPS**, p50 **205,68 ms**, p95 **395,19 ms** |

Các lượt chạy có khác cấu hình/tải máy; không quy toàn bộ chênh lệch FPS cho ONNX. CPU/RSS trong script evaluate đo parent process, **không gồm worker**; không dùng số đó làm ngân sách toàn ứng dụng. Thời gian xử lý file không phải tuổi frame live. Nguồn số liệu nằm trong `reports/fall_detection/` tương ứng.

Lượt pipeline cuối: SMTP 0 lần, hash dữ liệu người dùng/fall-events/shared trước và sau không đổi. Bằng chứng ở `performance.json`, `metrics.json`, `manifest.json`, report session và `diagnosis.json`. Manifest lần này được tạo lúc chạy; thay đổi sau đó về tương thích/đường dẫn model/test được đối chứng bằng tests và model hash, không coi là một lần đo video mới.

Trace cuối có 383 frame có detection, 7 track ID qua clip, 263 observation đủ feature HFD và 128 đã qua warm-up. Không có observation class 0 đồng thời góc torso >45°. Hạ ngưỡng score đơn thuần không giải quyết được mất pose. Trước pose-affinity có nhiều track fragment; giảm số ID là dấu hiệu debug, **không phải metric fragmentation đã có nhãn**.

Probe tại 17,5 giây không có pose, cả resolution .4 và .8; ở các thời điểm khác chỉ có pose một phần của một người. Bằng chứng `hfd_source_probe.json`, `hfd_source_probe_08.json`. Không kết luận repo mới đã xử lý được người nằm/che khuất chỉ vì có checkpoint huấn luyện ngã.

Đối chiếu nhãn cũ: 0 TP, 2 FN; nhãn thời gian chưa review độc lập và thiếu bbox theo người, nên accuracy **NOT VERIFIED**. 0 false positive trên clip ngắn không chứng minh tỷ lệ báo nhầm thấp.

## Kiểm chứng phần mềm và model

**75 tests đạt, không failure/error/skip:** 15 HFD, 24 core, 22 fusion, 2 UI, 12 safety. Harness cô lập dữ liệu runtime và chặn SMTP. HFD tests đối chiếu feature vector và logits/hidden với upstream, state nhiều người, người thứ hai ngã, gap/startup-low, IPC identity/timeout/close, thiếu model, live retry và snapshot/clip. UI test kiểm tra Qt timer chạy khi inference còn ở thread nền.

ONNX hai kích thước 513×289 (video 1280×720 ở resolution .4) và 257×193 (camera 640×480 ở .4) vượt field parity trên tensor zero/random, rtol/atol .001. Đây là kiểm chứng đầu ra mạng, không phải nghiệm thu pose accuracy. File `hfd_onnx_parity_513.json`, `hfd_onnx_parity_257.json`; export spatial cố định, không dùng cùng graph cho kích thước khác.

## Trạng thái nghiệm thu và việc còn lại

| Giai đoạn | Trạng thái |
|---|---|
| G0 import/compatibility | Đã xử lý và kiểm thử |
| G1 model/runtime | Pose và LSTM chạy được, worker/version/model hash đã ghi |
| G2 feature/model parity | Đạt hợp đồng số học đã kiểm; cadence training và label map vẫn NOT VERIFIED |
| G3 nhiều người/policy | Đã tích hợp, tests đạt; tracking/recall thật chưa nghiệm thu |
| G4 UI/live/video/evidence | Đã tích hợp; live camera/soak/delivery thật chưa nghiệm thu |
| G5 recognition/performance/package | **FAIL** clip và mục tiêu ≥10 FPS; heldout, live-age và package **NOT VERIFIED** |

Cần review spatial/time labels độc lập, bổ sung dữ liệu người nằm/ngã có che khuất và hoạt động âm tính, rồi cải thiện/fine-tune pose trước khi chọn classifier/policy trên dev. Có thể thử pose khác đưa vào cùng HFD classifier qua cache để đo tách detector/classifier; tập heldout 50 sự kiện và 10–30 giờ âm tính của kế hoạch vẫn chưa có. Không tự gán nhãn mới để khớp dự đoán hoặc coi mất dấu là ngã.

License HumanFallDetection MIT và OpenPifPaf AGPLv3+ là hai điều kiện riêng; notices local nằm trong `modules/fall/licenses/`, provenance/model hash trong `hfd_manifest.json`. Tham khảo [OpenPifPaf chính thức](https://github.com/openpifpaf/openpifpaf) và [release/version](https://github.com/openpifpaf/openpifpaf/releases). Chưa nghiệm thu việc phân phối.

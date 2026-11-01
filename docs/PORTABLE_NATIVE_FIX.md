# Điều tra và sửa Windows portable

## Bằng chứng

Thông báo `_framework_bindings` / DLL initialization failed xảy ra trước khi khởi tạo model. Đây là lỗi nạp mã native, không phải thiếu Python hay trọng số model. Riêng traceback không đủ phân biệt mọi nguyên nhân của WinError 1114 trên máy đích.

Kiểm tra PE của `_framework_bindings.cp312-win_amd64.pyd` xác nhận AMD64, phụ thuộc `MSVCP140.dll`, `VCRUNTIME140.dll`, `VCRUNTIME140_1.dll` và OpenCV đi kèm. Các bản v1, v1b, zipformer PT/HP, V3 và thư mục AI_FOR_EXAM_V3 cũ thiếu `msvcp140.dll` và `concrt140.dll` ở runtime. Ba ZIP PT/HP/V3 đang phát hành trước bản sửa cũng thiếu chúng. Gói setup/source không chứa runtime hoàn chỉnh và vốn cần cài đặt, nên không đáp ứng mục tiêu giải nén rồi chạy.

Một tiến trình embedded Python mới, import MediaPipe từ runtime cũ, thực tế nạp `C:\Windows\System32\msvcp140.dll` và `C:\Windows\System32\concrt140.dll`. Đây là phụ thuộc ngoài gói đã xác nhận, bị che khuất bởi máy build có VC++ sẵn. Chỉ kèm bộ cài VC++ trong prerequisites không giải quyết điều này vì launcher không chạy bộ cài. Runtime cũ còn có thể phối hợp VCRUNTIME đóng gói với MSVCP từ phiên bản VC++ khác trên máy đích.

Microsoft hỗ trợ triển khai CRT cạnh executable: [Choose a deployment method](https://learn.microsoft.com/en-us/cpp/windows/choosing-a-deployment-method?view=msvc-170). MediaPipe cũng ghi nhận phụ thuộc VC++ khi import trên Windows: [Troubleshooting](https://github.com/google-ai-edge/mediapipe/blob/master/docs/getting_started/troubleshooting.md). Đây là căn cứ cho bản sửa; không phải bằng chứng rằng mọi lỗi 1114 đều có cùng nguyên nhân.

## Thay đổi

- Trích CRT x64 từ `vc_redist.x64.exe` Microsoft có sẵn, xác minh Authenticode bundle và từng DLL. Không lấy DLL từ System32, không dùng wheel CRT bên thứ ba.
- Đặt bộ CRT đồng nhất 14.44.35211 cạnh `runtime/python.exe`; lưu hash, nguồn, phiên bản và giấy phép. Không cần chạy installer VC++ hoặc quyền admin trên máy đích.
- Dùng bootstrap stdlib trước native imports trong cả supervisor và desktop; kiểm tra hash và nạp DLL bằng đường dẫn tuyệt đối.
- Sửa builder PT/HP và V3. Các đường archive V3 cũng phải qua chốt QA chung, không được cập nhật ZIP bằng danh sách tệp thủ công bỏ sót runtime.
- QA kiểm tra nguồn DLL thực nạp; VC++ phải ở trong gói. DLL hệ điều hành nằm trong Windows; module Defender do hệ điều hành chèn được ghi riêng.
- Archive kiểm tra đầu vào QA quan trọng (launcher, bootstrap, CRT và model) chưa thay đổi, SHA-256 và CRC toàn bộ thành viên trước khi thay ZIP đích; có checksum toàn ZIP.

Các bản cũ được giữ làm lịch sử, không nên tiếp tục phân phối. Bản sửa PT/HP/V3 nằm trong `releases/portable-nativefix`; ZIP hiện hành giữ tên `AI_FOR_EXAM_PT.zip`, `AI_FOR_EXAM_HP.zip`, `AI_FOR_EXAM_V3.zip` sau khi hoàn tất QA.

## Lỗi bổ sung phát hiện khi giải nén vào đường dẫn có dấu

Lượt giải nén lại đầu tiên đã xác minh mọi hash thành công nhưng acceptance chưa đạt. Từ đường dẫn `Máy mới ...`, DLL CRT nạp đúng từ gói, còn Zipformer giải mã WAV bị `IndexError: invalid unordered_map<K, T> key`. Đổi đường dẫn model/token sang dạng tương đối ASCII trong cùng gói giúp WAV đó giải mã thành công. Upstream cũng ghi nhận vấn đề đường dẫn Unicode trên Windows: [sherpa-onnx issue 3885](https://github.com/k2-fsa/sherpa-onnx/issues/3885).

MediaPipe cũng báo graph không tồn tại dù tệp có thật và đúng hash khi đường dẫn tuyệt đối chứa dấu. Bản sửa `patch_mediapipe.py` giữ nguyên license upstream và đổi resource root native sang đường dẫn tương đối ASCII khi cần. Entry point đặt CWD ở `app` trước khi tạo graph. Bản sửa được ghi trong `PORTABLE_COMPAT.json`; thay tệp bằng atomic replace để không sửa các bản cũ dùng chung hard link.

`nativefix.2` có cả hai sửa đổi. Warmup yêu cầu khởi tạo được graph emotion và giải mã một WAV thật trước khi báo ready; không chấp nhận chỉ tải checkpoint hoặc transcribe im lặng. Kiểm thử hồi quy xác minh đường dẫn native của Zipformer vẫn trỏ đúng các model trong thư mục có dấu. Kết quả cuối chỉ được chốt sau khi ZIP mới qua lượt giải nén và acceptance mới.

Kết quả cuối của `6.0.0-nativefix.2`: PT, HP và V3 đều qua acceptance tại thư mục build và sau khi giải nén ZIP sang thư mục có dấu/khoảng trắng mới. Mỗi ZIP có hơn 18.000 tệp được kiểm tra SHA-256/CRC, sau giải nén các tệp được đối chiếu hash lại. Bốn kiểm thử hồi quy đạt. `releases/PORTABLE_NATIVEFIX_VALIDATION.json` tổng hợp đường dẫn bằng chứng; `releases/LEGACY_RELEASES.txt` liệt kê các thư mục cũ đã đánh dấu retired. Windows sạch không Python/VC++ vẫn chưa được kiểm thử.

## Kiểm thử và phạm vi kết luận

QA sử dụng đúng embedded interpreter và launcher, PATH chỉ còn runtime/Windows, PYTHONHOME/PYTHONPATH cố ý sai, cache và dữ liệu mới. Kiểm tra nhiều thứ tự import MediaPipe/Torch/OpenCV, ONNX/PyAV/audio/Qt, DLL CRT thực nạp, inference face/emotion/pose/STT, WAV tiếng Việt đóng gói, dashboard offscreen, HTTP, đăng nhập, từ chối control token sai và shutdown. Kiểm tra âm tính bảo đảm manifest/CRT hỏng hoặc thiếu bị từ chối trước khi gọi loader. Model checksum sai cũng bị từ chối.

Sandbox chạy lệnh của công cụ chặn localhost bằng WinError 10013; bài kiểm thử ứng dụng đầy đủ được chạy ngoài sandbox đó. Điều này khác với Windows Sandbox dùng để kiểm thử hệ điều hành sạch.

Kết quả từng bản: `QA_REPORT.txt`, `PORTABLE_*_VALIDATION.json`, và `EXTRACTED_*_VALIDATION.json`. Kiểm thử giải nén lại ZIP xác minh từng tệp rồi chạy acceptance từ đường dẫn có dấu/khoảng trắng. Báo cáo trước sửa: `reports/portable-native-audit-before.json`.

Máy hiện tại không có Windows Sandbox hoặc máy ảo Windows sạch sẵn dùng. Đã chuẩn bị `qa/clean_machine_test.ps1` chạy hoàn toàn bằng runtime trong gói và công cụ sinh cấu hình `.wsb` mạng tắt, map gói chỉ đọc. Chưa được đánh dấu Windows sạch đã pass. Kiểm thử trên máy build và giải nén lại không thay thế kiểm thử máy Windows không Python/VC++, thiết bị camera/micro, driver, Windows N và chạy dài giờ. Không tuyên bố 100% trên mọi máy.

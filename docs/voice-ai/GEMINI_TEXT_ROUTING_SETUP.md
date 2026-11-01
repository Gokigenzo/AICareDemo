# Gemini text routing — setup và phạm vi

Ngày kiểm tra: 09/10/2026. Faster-whisper tiếp tục nhận audio local. Gemini chỉ phân loại text đủ điều kiện; không có API STT, model text local, DB tools, SQL, grounding, function execution hoặc lời khuyên y tế.

## Đường chạy và registry

`VoiceSessionController.transcript_ready` → một `VoiceRequestCoordinator.route` → local policy hoặc HTTP backend → validator → `CommandDispatcher` → service nút bấm hiện có. Không còn nối transcript trực tiếp vào dispatcher song song với coordinator.

| Intent | Context/policy | Handler thật | Side effect và sync |
|---|---|---|---|
| navigate_home | Patient/context hiện tại; không chạy bài tập | `medication_tabs.setCurrentIndex(0)` | Điều hướng sang Việc cần làm hôm nay |
| snooze_medication | Tab 0, đúng một dose đến hạn, chưa OVERDUE; không chọn số phút mới | `ElderSyncClient.confirm_dose_taken(action='snooze')` | Cùng transaction/dose_events/sync_inbox/outbox với nút nhắc lại |
| confirm_medication_taken | Tab 0, đúng một dose; xác nhận tên, liều, giờ bằng hộp thoại mặc định No; kiểm tra lại snapshot sau xác nhận | `ElderSyncClient.confirm_dose_taken(action='self_reported_taken')` | Tự khai đã uống; chống trùng bằng `voice_<session_id>`; DB và web cùng đọc dose |
| request_medication_help | Tab 0, đúng một dose; câu rõ local | `ElderSyncClient.confirm_dose_taken(action='help_requested')` | Luồng hỗ trợ/alert/outbox hiện có; người nhận do service xác định, không do Gemini |
| start_rehabilitation | Tab 1, camera source, plan active, chưa chạy; version kiểm tra tại service | `DashboardWindow._on_start_exercise(expected_plan=...)` | `RehabSessionAdapter` tạo/tái dùng phiên; camera đếm |
| pause_rehabilitation | Tab 1, camera source, đang chạy và chưa pause | `DashboardWindow._on_pause_exercise()` | Tạm dừng cùng engine/nút UI; không hoàn thành phiên |
| unknown | Phủ định, nhiều ý, câu hỏi, thiếu context, ngoài scope hoặc lỗi | Template yêu cầu nói lại/chọn nút | Không ghi DB |

Chỉ sáu handler thật được expose. `complete_rehabilitation`, liên hệ trực tiếp bác sĩ/người nhà, tư vấn liều, ghi triệu chứng, games/music bằng Gemini chưa được expose. Hoàn thành phục hồi vẫn do camera. Slot `snooze_minutes` chỉ được null vì handler hiện tại dùng mặc định của lịch.

## Privacy và contract

Production dùng danh mục **đóng** 20 câu điều hướng trung tính trong `policy.PUBLIC_NAVIGATION`, không dùng regex để tuyên bố đã khử nhạy cảm. Câu có tên, ID, email, số điện thoại, đơn thuốc, thuốc, sức khỏe cụ thể hoặc không thuộc danh mục đều không đi Gemini. Câu rõ như “Tôi đã uống rồi”, “Tôi không biết dùng thuốc này”, “Cho tôi nghỉ một chút” đi local. Không gửi audio hay snapshot DB tới Google.

Ngay cả khi người đang ở tab thuốc, payload production chỉ là câu điều hướng, `context_type=home_navigation`, enum HOME/UNKNOWN và `pending_question=null`. Patient/request/session IDs và version hash chỉ đi backend nội bộ; hash **không** được coi là dữ liệu đã ẩn danh để gửi provider.

HTTP `POST /api/transcript-intent` dùng bearer session token của backend hiện có. Server kiểm tra quyền patient, hash authoritative doses/plans/sessions, rồi kiểm tra lại quyền, token và version sau phân loại. Client kiểm tra response request/session/version; coordinator và dispatcher kiểm tra toàn bộ snapshot/epoch tại máy. Endpoint không thực thi handler, không ghi clinical DB hay gửi notification. Audit chỉ request ID, intent, outcome, prompt/model identifier và latency; không log raw utterance/SDK error/key.

JSON enum, field thừa, slots, chứng cứ nguyên văn, phủ định, context và ý nghĩa được validate bằng code. Confidence, confirmation/policy do model tạo đều bị reject. Có schema [intent-v1.schema.json](gemini/intent-v1.schema.json) và prompt [vi-router-v1.txt](gemini/vi-router-v1.txt); mã Python là nguồn runtime. Không có hội thoại tự do hoặc xác nhận bằng “ừ”.

## Dependency và cài sạch

SDK chính thức backend: `google-genai==2.29.0`, đã thử structured JSON trên model `gemini-3.5-flash-lite` bằng dữ liệu tổng hợp. App người già không cần SDK/key. `requirements-gemini-backend.txt` là manifest backend, `requirements-gemini-backend.lock` khóa closure SDK; `requirements-linux.lock` tiếp tục khóa runtime CPU đã kiểm tra. `filelock==4.0.12` khai báo trực tiếp trong manifest app/Windows và có trong các lock tương ứng.

```bash
python3 -m venv .venv-backend
.venv-backend/bin/python -m pip install -r requirements-gemini-backend.txt \
  -c requirements-linux.lock -c requirements-gemini-backend.lock
.venv-backend/bin/python -m pip check
```

Lệnh trên đã được kiểm tra với virtualenv mới Python 3.14.4 Linux CPU trong `/tmp`. Không đổi Python/driver hệ thống; Windows backend và gói EXE chưa build/test ở lượt này. Các version/wheel Linux không thay thế nghiệm thu Windows.

## Project, key và cấu hình

Người dùng xác nhận key thử đầu thuộc free tier, chưa billing. Metadata/model và generateContent thành công; **chưa có project ID hay quota RPM/TPM/RPD từ AI Studio**. Key mới gửi cuối lượt chưa được probe. Không suy ra tier/quota/project từ chuỗi key hoặc một HTTP 200. Không tự tạo project mới hoặc bật billing. Không có connector quản trị Google Cloud/AI Studio trong phiên này.

1. Mở AI Studio → Projects, dùng project hiện có; nếu chưa có thì tạo project free và không liên kết billing. Kiểm tra tier và quota của model trong AI Studio. Đối chiếu lại giá và structured output trước đổi model.
2. Copy `packaging/gemini-backend.env.example` sang file private **ngoài thư mục phát app**. Nhập key tại máy backend hoặc dùng secret manager/environment của process backend. Key đã gửi chat nên thay key trước dùng lâu dài; không dán key vào desktop `.env`, source, argv, chat hoặc báo cáo.
3. Điền project ID thật; đặt free-tier verified true sau kiểm tra; giảm caps theo quota thật. Chỉ bật `GEMINI_INTENT_ENABLED=true` khi đủ cấu hình. `--check-config` chỉ in presence, không in giá trị secret/project/session.

```bash
.venv-backend/bin/python scripts/run_gemini_backend.py \
  --env-file /duong/dan/private/gemini-backend.env --check-config
.venv-backend/bin/python scripts/run_gemini_backend.py \
  --env-file /duong/dan/private/gemini-backend.env --host 127.0.0.1 --port 8080
```

Backend dùng `UnifiedDatabaseManager`, migrations, auth, outbox và SSE hiện có; không có database voice riêng. Các process của **cùng project** phải dùng cùng `GEMINI_INTENT_QUOTA_PATH` trên filesystem hỗ trợ lock. Nhiều máy cần limiter chung trước mở rộng; lock file này chưa phải limiter phân tán.

Desktop `.env` chỉ có:

```dotenv
VOICE_INTENT_ENABLED=true
VOICE_INTENT_BACKEND_URL=http://127.0.0.1:8080
VOICE_INTENT_SESSION_TOKEN=
```

Lấy session token bằng đăng nhập `/api/auth/login` hiện có với tài khoản có quyền đúng patient; không dùng API key làm token. Token đang lưu in-memory ở backend, hết hạn hoặc restart cần đăng nhập lại; chưa thêm provisioning token riêng cho thiết bị. Backend ngoài loopback phải HTTPS. Desktop chặn URL có username/password/query/fragment và HTTP bên ngoài loopback; tắt proxy và redirect. Không ship bearer token dùng chung nhiều thiết bị.

Cả hai feature flag mặc định false. Khi mất key/token/mạng/quota, câu rõ local và nút bấm tiếp tục chạy; câu chưa rõ không tự ghi DB.

## Vòng đời, deadline và quota

Coordinating HTTP nằm trong một thread riêng, không đụng widget/model/micro; worker faster-whisper vẫn một process/model. Ghi vẫn do nhấn micro, có Dừng/Hủy; TTS và nhạc được điều phối như trước. Hủy/đổi người/đổi tab/plan/context/đóng app loại response cũ. Không bắt đầu routing mới khi thread cũ chưa kết thúc; shutdown ngừng timer, vô hiệu hóa request, chờ thread 0,1 giây; HTTP đang chạy có timeout riêng và chỉ phân loại.

Provider trên project thử trả HTTP 400 nếu đặt HTTP deadline 8s: minimum 10s. Adapter dùng SDK async với transport deadline ≥10s và `asyncio.wait_for` theo ngân sách tổng ≤8s. SDK implicit retry tắt bằng `attempts=1`; retry ứng dụng mặc định 0, tối đa 1 lần chỉ lỗi tạm thời và còn ngân sách/quota. Coordinator bỏ kết quả sau 8s, kể cả HTTP đang dọn kết nối. Camera/UI không chờ network.

Caps bảo thủ: RPM 1, TPM **ước tính/reservation** 2400 (1200/call, không phải token usage provider đã đo), RPD 10, reserve 2. Đây là cap local, không phải xác nhận quota Google. Shared limiter chặn overlap, minute/day/circuit; day reset Pacific. 429 mở circuit 60s; ba lỗi liên tiếp mở 30s. Không retry sai key/forbidden/schema/429, không chuyển model/tier hoặc replay business command. File quota chỉ có project label/timestamp/count, không chứa key hay clinical data. Tắt flag để ngừng cloud; chỉ reset file khi không có request hoạt động và vẫn phải tôn trọng quota provider, không dùng reset để lách quota.

## Kiểm tra và benchmark

```bash
QT_QPA_PLATFORM=offscreen .venv-linux/bin/python -m pytest \
  tests/transcript_intent tests/voice_ai/test_local_voice.py -q
.venv-linux/bin/python scripts/benchmark_transcript_intent.py
.venv-linux/bin/python scripts/smoke_intent_http.py
```

Dataset có 150 case, 48 tune / 102 acceptance, nhóm biến thể cùng câu ở cùng split. Cấu trúc chứa label, context giả, decision, slots, confirmation và privacy policy. Có paraphrase, phủ định, nhiều ý, sửa lời, injection, lỗi STT và context bị từ chối. Đây là tập nhỏ, không đại diện giọng vùng miền/dữ liệu bệnh nhân thật; không thay bằng dữ liệu thật để gửi free tier.

Benchmark cloud-disabled đo coverage local và confusion, không gọi model. `--live` chỉ nhận tối đa ba ID acceptance từ dataset đóng, yêu cầu free-tier confirmation và project label; không nhận “synthetic=true” từ HTTP. Key chỉ qua protected stdin hoặc env backend. Script không thực thi hành động nghiệp vụ từ benchmark. Full acceptance cloud chưa chạy vì chưa xác minh quota; không coi ba mẫu là đạt ≥95%/≥99% hoặc p95 ổn định.

Xem [báo cáo chạy thực tế](../../reports/gemini_intent/REPORT.md) và [diff riêng lượt này](../../reports/gemini_intent/review.diff). Micro/camera/CUDA thật và app-web E2E đầy đủ chưa được nghiệm thu tại môi trường công cụ này.

## Tài liệu chính thức đối chiếu

- Giá/free tier và điều kiện dữ liệu: https://ai.google.dev/gemini-api/docs/pricing và https://ai.google.dev/gemini-api/terms
- Quota theo project: https://ai.google.dev/gemini-api/docs/rate-limits
- Structured output: https://ai.google.dev/gemini-api/docs/structured-output
- Key/project: https://ai.google.dev/gemini-api/docs/api-key
- SDK Python: https://github.com/googleapis/python-genai

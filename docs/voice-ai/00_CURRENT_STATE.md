# BÁO CÁO HIỆN TRẠNG TOÀN DIỆN HỆ THỐNG (CURRENT STATE AUDIT)
**Dự án:** Trợ Lý AI Chăm Sóc Người Cao Tuổi & Phục Hồi Chức Năng (Elderly Care AI System)  
**Tệp:** `docs/voice-ai/00_CURRENT_STATE.md`  
**Giai đoạn:** Phase 0 — Khảo sát baseline và kiểm kê mã nguồn  
**Thời điểm thực hiện:** Tháng 10/2026  
**Nguyên tắc chỉ đạo:** AI suy luận; Backend phân quyền và thực thi (AI interprets; backend authorizes and executes).

---

## 1. Tổng quan Kiến trúc Kho Mã Nguồn & Môi trường Thực thi

### 1.1. Khung ứng dụng và Ngôn ngữ Runtime
- **Kho mã nguồn:** `/mnt/shared/Code/AI_Rehabilitation_Safety_Assistant`
- **Môi trường Python chính thức:**
  - Linux (kiểm thử hiện tại): Python **3.14.4** trong virtualenv `.venv-linux` (`.venv-linux/bin/python`).
  - Windows (đóng gói phát hành): Python virtualenv `.venv` kết hợp tệp cấu hình PyInstaller `AI_Rehab_Safety_Assistant.spec`, kịch bản cài đặt `SETUP.bat`, `START.bat`.
- **Giao diện Người cao tuổi (Desktop App):**
  - **PyQt5 5.15.11** kết hợp `PyQt5-Qt5 5.15.19`.
  - Điểm khởi chạy chính: [main.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/main.py#L44-L98) (`main()` khởi tạo `QApplication`, áp dụng bảng màu y tế chuẩn từ [app/theme.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/theme.py), khởi tạo cửa sổ chính [app/dashboard.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/dashboard.py)).
  - Tự động đồng bộ hóa hồ sơ người bệnh khi khởi động thông qua `sync_all_patient_profiles(db)` ([services/patient_sync_service.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/services/patient_sync_service.py)).
  - Chạy kiểm thử tự động không giao diện qua cờ `QT_QPA_PLATFORM=offscreen` và cờ `--test`.
- **Cổng Web Bác sĩ & Người nhà (Web Portals):**
  - Web Server nội bộ: [web/server.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/server.py#L34-L250) chạy trên nền tảng `ThreadingHTTPServer` của Python Standard Library.
  - Zero external web framework: Không sử dụng FastAPI, Flask hay Django; không phụ thuộc vào internet hay pip package bên ngoài khi chạy web server.
  - Cổng lắng nghe mặc định: `127.0.0.1:8080`, có cơ chế tự động chuyển cổng sang 8081..8089 nếu cổng bận ([web/server.py#L231-L248](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/server.py#L231-L248)).
  - Định tuyến RESTful API: [web/api_router.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/api_router.py#L49-L228) (`ApiRouter.handle_request`).
  - Xác thực & Phân quyền: [web/auth.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/auth.py) (`AuthService`) dựa trên Bearer Token / Cookie session, mật khẩu băm PBKDF2/SHA-256 có Salt.

### 1.2. Kênh Đẩy Dữ Liệu Thời Gian Thực (Real-Time Push Transport)
- **Server-Sent Events (SSE):**
  - Endpoint: `GET /api/stream?token=...` hoặc `GET /v1/stream?token=...` ([web/server.py#L123-L172](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/server.py#L123-L172)).
  - Điều phối kết nối SSE: [web/sse_hub.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/sse_hub.py) (`SSEHub`).
  - Nguyên tắc bảo mật dòng sự kiện: Sự kiện SSE chỉ chứa siêu dữ liệu tối thiểu (`event_id`, `type`, `patient_id`, `aggregate_id`, `aggregate_version`, `occurred_at`). Tuyệt đối **không phát thông tin nhạy cảm** (tên thuốc, liều lượng, số đo sức khỏe, hình ảnh) qua broadcast ([web/sse_hub.py#L35-L60](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/sse_hub.py#L35-L60)).
  - Cơ chế đồng bộ máy khách (Web Client): Client nhận tín hiệu SSE và thực hiện **refetch có xác thực** đúng phân vùng dữ liệu cần cập nhật (ví dụ: refetch thẻ thuốc hoặc thẻ cảnh báo).
- **Hàng đợi Sự kiện Giao dịch Bền vững (Transactional Outbox Pattern):**
  - Bảng CSDL: `outbox_events` ([database/migrations/003_outbox_and_sync.sql#L8-L23](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/database/migrations/003_outbox_and_sync.sql#L8-L23)).
  - Mọi thao tác ghi nghiệp vụ (xác nhận thuốc, số đo, bài tập, đơn thuốc, báo cáo) được ghi đồng thời với một hàng `outbox_events` **trong cùng ACID transaction** thông qua trợ thủ `insert_outbox_event` ([database/outbox_helper.py#L15-L48](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/database/outbox_helper.py#L15-L48)).
  - Tiến trình Outbox Relay: [services/outbox_relay.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/services/outbox_relay.py) (`OutboxRelayService`) quét các sự kiện chưa xử lý theo chu kỳ 0.5 giây và đẩy ra `SSEHub`.
- **Chống Gửi Lặp & Ngoại Tuyến (Idempotency & Client Sync Inbox):**
  - Bảng CSDL: `sync_inbox` ([database/migrations/003_outbox_and_sync.sql#L26-L35](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/database/migrations/003_outbox_and_sync.sql#L26-L35)) ghi nhận `client_event_id` do thiết bị tạo ra để khử trùng lặp hoàn toàn.
  - Client phía người già: [services/elder_sync_client.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/services/elder_sync_client.py) (`ElderSyncClient`) duy trì hàng đợi ngoại tuyến JSON tại `data/sync_queues/offline_queue_{patient_id}.json`, hỗ trợ chuyển trạng thái mượt mà giữa *Chờ mạng -> Đang đồng bộ -> Đã ghi nhận*.

---

## 2. Kiểm Kê Cơ Sở Dữ Liệu & Bảng Nghiệp Vụ

Hệ thống lưu trữ thống nhất tại tệp SQLite WAL: `data/unified_care.sqlite3` (kích thước ~950 KB), hỗ trợ Dual-Engine (chạy trên SQLite cục bộ hoặc kết nối PostgreSQL bằng ANSI DDL).

Cấu trúc migrations gồm 4 tệp migration liên hoàn tại [database/migrations/](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/database/migrations):

| Migration | Tệp nguồn | Nội dung & Bảng tạo mới |
|---|---|---|
| **001** | `001_initial_schema.sql` | 28 bảng lõi chuẩn hóa 3NF: `schema_migrations`, `users`, `patients`, `legacy_patient_map`, `caregivers`, `clinicians`, `patient_caregivers`, `care_team`, `medications`, `prescriptions`, `prescription_items`, `medication_schedules`, `dose_occurrences`, `dose_events`, `alerts`, `notification_deliveries`, `observation_types`, `measurement_groups`, `health_observations`, `symptom_entries`, `clinician_reviews`, `clinical_messages`, `message_receipts`, `monitoring_plans`, `patient_thresholds`, `game_types`, `content_packs`, `game_sessions`, `game_results`. |
| **002** | `002_rehab_and_audit.sql` | 12 bảng mở rộng: `mood_checkins`, `emotion_inferences`, `rehab_plans`, `rehab_sessions`, `rehab_events`, `caregiver_reports`, `report_messages`, `care_recommendations`, `recommendation_receipts`, `emergency_contacts`, `emergency_contact_events`, `audit_events`. |
| **003** | `003_outbox_and_sync.sql` | 3 bảng đồng bộ cận thời gian thực: `outbox_events`, `sync_inbox`, `device_sessions`. |
| **004** | `004_flow_adjustments...sql` | 3 bảng điều chỉnh luồng: `measurement_requests`, `exercise_plan_versions`, `measurement_request_logs`. |

### Định danh Người bệnh & Bảng Ánh xạ `legacy_patient_map`
Do các module phát triển độc lập trong lịch sử, codebase có các hệ thống ID khác nhau:
- Nhận diện khuôn mặt máy ảnh: `"1"`, `"2"`.
- Module nhắc thuốc độc lập cũ: `"patient_001"`, `"patient_002"`.
- Module sức khỏe & trò chơi cũ: `"pat-001"`, `"pat-002"`.
- **Chuẩn hóa hiện tại:** Bảng `legacy_patient_map` ánh xạ tất cả về mã định danh chuẩn:
  - `patient_001` (Cụ Hoàng Anh, User: `user_pat_001`)
  - `patient_002` (Cụ Mai Hương, User: `user_pat_002`)

---

## 3. Hiện Trạng Giao Diện Ứng Dụng Người Già (Elder Desktop UI)

Tệp cốt lõi:
- [app/dashboard.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/dashboard.py): Cửa sổ chính `DashboardWindow` tích hợp các tab và luồng giám sát.
- [app/today_todo_widget.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/today_todo_widget.py): Giao diện trung tâm "Việc Cần Làm Hôm Nay" (`TodayTodoWidget`).
- [app/cognitive_games_widget.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/cognitive_games_widget.py): Widget tổng hợp Trò chơi trí tuệ và Âm nhạc thư giãn (`CognitiveGamesWidget`).

### Các khối nghiệp vụ tương tác trực tiếp của người già:
1. **Lịch Uống Thuốc Hôm Nay (Thao tác 1 chạm):**
   - Mã nguồn: [app/today_todo_widget.py#L359-L454](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/today_todo_widget.py#L359-L454) (`_render_medications`).
   - Hiển thị danh sách các liều thuốc đến hạn trong ngày từ `dose_occurrences`.
   - Nút hành động:
     - `✔ ĐÃ UỐNG` / `✔ UỐNG BÂY GIỜ`: Gọi `_on_confirm_taken` -> gọi `ElderSyncClient.confirm_dose_taken(occ_id, action="self_reported_taken")`. Ghi chú rõ `(Tự khai báo)`.
     - `⏰ Nhắc lại`: Gọi `_on_snooze` -> hoãn nhắc nhở 10 phút.
     - `🆘 Cần hỗ trợ`: Gọi `_on_help_requested` -> gửi cảnh báo khẩn cấp tới Người nhà & Bác sĩ và hiển thị số liên hệ ngay lập tức.
2. **Yêu Cầu Đo Chỉ Số Sức Khỏe (Từ người nhà & bác sĩ):**
   - Mã nguồn: [app/today_todo_widget.py#L455-L504](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/today_todo_widget.py#L455-L504) (`_render_measurement_requests`).
   - Hiển thị thẻ màu vàng nổi bật yêu cầu đo huyết áp, SpO2... và hạn đo.
3. **Bài Tập Phục Hồi Chức Năng 16:00 (Camera tự đếm):**
   - Mã nguồn: [app/today_todo_widget.py#L545-L630](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/today_todo_widget.py#L545-L630) (`_render_rehab`).
   - Thanh tiến độ hiển thị số lần đếm hợp lệ từ camera (`verified_count / target_count`).
   - Nút "▶ BẮT ĐẦU CHUỖI BÀI TẬP 16:00 NGAY (Camera tự đếm)".
   - Nút "Báo sự cố: Tôi đã tập nhưng camera không nhận": Chuyển trạng thái `verification_unavailable` mà không đếm ảo.
4. **Cảm Nhận Hôm Nay (Tâm trạng tự khai báo):**
   - Mã nguồn: [app/today_todo_widget.py#L185-L221](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/today_todo_widget.py#L185-L221) (`_build_mood_buttons`).
   - 5 nút chọn: *Rất vui (5)*, *Tốt (4)*, *Bình thường (3)*, *Hơi mệt (2)*, *Buồn (1)* và nút *Bỏ qua*. Lưu vào bảng `mood_checkins`.
5. **Lời Khuyên Của Bác Sĩ Phụ Trách:**
   - Mã nguồn: [app/today_todo_widget.py#L636-L680](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/today_todo_widget.py#L636-L680) (`_render_advice`).
   - Hiển thị lời khuyên bác sĩ từ `care_recommendations` kèm nút "Đã xem" (ghi nhận vào `recommendation_receipts`).
6. **Chỉ Số Sức Khỏe Gần Nhất:**
   - Mã nguồn: [app/today_todo_widget.py#L681-L702](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/today_todo_widget.py#L681-L702) (`_render_vitals`).
   - Hiển thị số đo huyết áp 2 thành phần (SYS/DIA) gần nhất và người nhập hộ.

---

## 4. Hiện Trạng Cổng Web Bác Sĩ & Cổng Web Người Nhà

### 4.1. Cổng Web Bác Sĩ (`web/templates/portal_clinician.html`)
- **Tập tin giao diện:** [web/templates/portal_clinician.html](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/templates/portal_clinician.html) (~2250 dòng).
- **Quyền truy cập:** Bác sĩ đăng nhập tài khoản có vai trò `clinician` (`AuthService`).
- **Phân vùng dữ liệu phụ trách:** Bác sĩ chỉ truy cập được các bệnh nhân có bản ghi trong `care_team` với `is_active = 1` ([web/auth.py#L130-L165](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/auth.py#L130-L165)).
- **Các chức năng chính:**
  - **Quản lý đơn thuốc theo phiên bản:** Bác sĩ tạo mới đơn thuốc hoặc tạo bản sửa đổi (`POST /api/patients/{id}/prescriptions/{id}/revisions`). Khi cập nhật phiên bản, lịch uống thuốc tương lai trên ứng dụng người già tự động cập nhật ngay lập tức.
  - **Gửi lời khuyên chuyên môn:** Bác sĩ gửi lời khuyên (dinh dưỡng, vận động, tinh thần) lưu vào `care_recommendations` (`POST /api/patients/{id}/recommendations`).
  - **Phản hồi báo cáo của người nhà:** Xem các báo cáo bất thường do người nhà gửi (`caregiver_reports`) và gửi tin nhắn tư vấn (`POST /api/patients/{id}/caregiver-reports/{id}/respond`).
  - **Theo dõi biểu đồ sinh hiệu:** Hiển thị huyết áp 2 chỉ số độc lập, nhịp tim, SpO2, đường huyết. Đảm bảo quy tắc: Ngày không có số đo thì để đứt gãy đường biểu đồ, tuyệt đối không điền số 0 ảo.
  - **Tiếp nhận cảnh báo y tế:** Tab Cảnh báo (`#docAlertsList`) hiển thị các cảnh báo `OVERDUE` hoặc `HELP_REQUESTED`. Nút "Tiếp nhận" gửi yêu cầu `POST /api/patients/{id}/alerts/{alert_id}/acknowledge`, cập nhật `alerts.status = 'ACKNOWLEDGED'` và phát sự kiện `medication.alert_acknowledged`.
  - **Cảnh báo khẩn cấp thời gian thực:** Kết nối SSE hiển thị thông báo khẩn ngay lập tức khi người già bấm "Cần hỗ trợ": `"🆘 CẢNH BÁO BỆNH NHÂN: Người cao tuổi vừa bấm nút 'CẦN HỖ TRỢ' khi uống thuốc!"` ([portal_clinician.html#L1004-L1006](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/templates/portal_clinician.html#L1004-L1006)).

### 4.2. Cổng Web Người Nhà (`web/templates/portal_caregiver.html`)
- **Tập tin giao diện:** [web/templates/portal_caregiver.html](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/templates/portal_caregiver.html) (~2200 dòng).
- **Quyền truy cập:** Người nhà đăng nhập tài khoản vai trò `caregiver` (`AuthService`), chỉ xem được bệnh nhân được phân công trong `patient_caregivers` có `is_active = 1`.
- **Các chức năng chính:**
  - **Nhập hộ số đo sinh hiệu:** Nhập huyết áp, nhịp tim, SpO2, đường huyết, thân nhiệt hộ người già qua form chuyên dụng (`POST /api/patients/{id}/observations`).
  - **Gửi yêu cầu nhắc đo:** Tạo lịch nhắc đo cho người già trên ứng dụng desktop (`POST /api/patients/{id}/measurement-requests`).
  - **Gửi báo cáo bất thường tới bác sĩ:** Người nhà gửi mô tả bất thường (chóng mặt, té ngã nhẹ, mất ngủ...) kèm mức độ nghiêm trọng (`POST /api/patients/{id}/caregiver-reports`).
  - **Điều chỉnh lịch tập phục hồi:** Điều chỉnh giờ nhắc (mặc định 16:00) và số lần chỉ tiêu (`POST /api/patients/{id}/exercise-plans`).
  - **Theo dõi tuân thủ uống thuốc:** Theo dõi trạng thái từng liều trong ngày, tiếp nhận cảnh báo quá hạn.
  - **Hotline Khẩn cấp & Lịch trực Bác sĩ:** Hiển thị danh bạ bác sĩ phụ trách, giờ trực, nút quay số; nếu ngoài giờ trực thì hướng dẫn gọi 115 ([portal_caregiver.html#L1290-L1340](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/web/templates/portal_caregiver.html#L1290-L1340)).

---

## 5. Hiện Trạng Nghiệp Vụ Hỗ Trợ Bác Sĩ & Cấp Cứu

### 5.1. Mô hình Phân công Bác sĩ Phụ trách & Trực ban
- Dữ liệu bác sĩ được lưu trong bảng `clinicians` và liên kết với tài khoản `users`.
- Phân công bệnh nhân - bác sĩ lưu trong bảng `care_team` ([001_initial_schema.sql#L87-L99](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/database/migrations/001_initial_schema.sql#L87-L99)):
  - Có các trường `valid_from`, `valid_to`, `consent_status` (`GRANTED`, `REVOKED`, `EXPIRED`), `is_active`.
  - Hỗ trợ phân công nhiều bác sĩ (ví dụ: Bác sĩ phụ trách tim mạch, Bác sĩ phụ trách ca trực).
- Danh bạ và ca trực khẩn cấp lưu trong bảng `emergency_contacts` ([002_rehab_and_audit.sql#L140-L154](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/database/migrations/002_rehab_and_audit.sql#L140-L154)):
  - Phân loại: `clinician_on_duty` (Bác sĩ ca trực), `local_emergency` (Cấp cứu địa phương 115), `caregiver_primary` (Người nhà chính).
  - Khung giờ trực: `on_duty_start` (ví dụ: `08:00`), `on_duty_end` (ví dụ: `17:00`).
  - Cờ xác minh: `is_verified` (0 = số mô phỏng/demo, 1 = số điện thoại thực tế).

### 5.2. Luồng Xử lý Yêu cầu Cần Hỗ trợ / SOS Hiện tại
1. Khi người già bấm nút "🆘 Cần hỗ trợ" trên màn hình Desktop:
   - Hàm `_on_help_requested` ([app/today_todo_widget.py#L516-L526](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/today_todo_widget.py#L516-L526)) gọi `ElderSyncClient.confirm_dose_taken(occ_id, action="help_requested")`.
   - `ElderSyncClient` ([services/elder_sync_client.py#L233-L253](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/services/elder_sync_client.py#L233-L253)) tạo bản ghi cảnh báo trong bảng `alerts` với `alert_type = 'HELP_REQUESTED'`, `status = 'NEW'`.
   - Đồng thời, chèn sự kiện outbox `medication.alert_created` vào bảng `outbox_events` trong cùng transaction.
   - Tiến trình `OutboxRelayService` đẩy tín hiệu SSE tức thời tới tất cả phiên Web đang kết nối của Bác sĩ phụ trách và Người nhà.
   - Màn hình Web Bác sĩ và Web Người nhà nhận tín hiệu SSE và kích hoạt thông báo cảnh báo đỏ trên giao diện.
   - Bác sĩ bấm "Tiếp nhận" (`POST /api/patients/{id}/alerts/{id}/acknowledge`) -> CSDL chuyển `alerts.status = 'ACKNOWLEDGED'` -> phát sự kiện `medication.alert_acknowledged`.
2. Hàm hỗ trợ độc lập trong module tuân thủ thuốc ([modules/medication_adherence/services/adherence_service.py#L215-L296](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/modules/medication_adherence/services/adherence_service.py#L215-L296)):
   - Hàm `create_emergency_assistance_request(occurrence_id, patient_id, details)` sinh mã sự cố duy nhất dạng `SOS-XXXXXX`, tạo `Alert`, bản ghi `DoseEvent`, và gửi email cảnh báo tới danh sách `caregivers` thông qua `NotificationGateway` và `EmailService`.
3. **Khoảng trống hiện tại đối với Voice AI:**
   - Hệ thống hiện tại chỉ có luồng trợ giúp gắn với một `occurrence_id` (liều thuốc cụ thể) hoặc sự kiện quay số `emergency_contact_events`.
   - **Chưa có bảng chuyên biệt `assistance_requests`** để lưu các yêu cầu trợ giúp bác sĩ bằng lời nói phát sinh bất kỳ lúc nào (ví dụ người già nói: *"Gọi bác sĩ giúp tôi"*, *"Tôi chóng mặt quá, cần bác sĩ"* mà không liên quan đến giờ uống thuốc).

---

## 6. Hiện Trạng Trò Chơi Trí Nhớ & Âm Nhạc Thư Giãn

Codebase có một phân hệ hoàn chỉnh dành riêng cho rèn luyện nhận thức và thư giãn: `modules/cognitive_games/`.

### 6.1. Trò chơi Nhận thức (Cognitive Memory Games)
- **Động cơ trò chơi (Domain Engines):** [modules/cognitive_games/services/game_engine.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/modules/cognitive_games/services/game_engine.py):
  1. `CardMatchingEngine` (Lật hình ghép cặp): Rèn luyện trí nhớ không gian và sự tập trung thông qua các hình ảnh đồ vật quen thuộc (ấm trà, hoa sen, đồng hồ, nón lá...). 3 cấp độ: 3 cặp (6 thẻ), 4 cặp (8 thẻ), 6 cặp (12 thẻ).
  2. `SequenceRecallEngine` (Nhớ trình tự): Kích thích sự nhanh nhạy và trí nhớ ngắn hạn. Người dùng quan sát thứ tự xuất hiện của hình ảnh và chọn lại đúng thứ tự. 3 cấp độ: 2 hình, 3 hình, 4 hình.
- **Giao diện Trò chơi:**
  - [modules/cognitive_games/ui/card_matching_widget.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/modules/cognitive_games/ui/card_matching_widget.py) (`CardMatchingWidget`).
  - [modules/cognitive_games/ui/sequence_recall_widget.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/modules/cognitive_games/ui/sequence_recall_widget.py) (`SequenceRecallWidget`).
  - Cả hai widget đều có nút quay lại màn hình chính to rõ, không bao giờ nhốt người cao tuổi trong màn chơi (`non-trapping back navigation`).
- **Tích hợp vào Giao diện Chính:**
  - Được đóng gói trong `CognitiveGamesWidget` ([app/cognitive_games_widget.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/cognitive_games_widget.py)).
  - Hiển thị trên tab "🧠 Trò chơi trí nhớ và Thư giãn" của `DashboardWindow` ([app/dashboard.py#L499-L506](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/dashboard.py#L499-L506)) và có nút truy cập nhanh từ thẻ "Việc cần làm hôm nay" ([app/today_todo_widget.py#L536-L543](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/today_todo_widget.py#L536-L543)).
  - Phương thức khởi chạy có sẵn:
    - `CognitiveGamesWidget._launch_card_matching()` ([app/cognitive_games_widget.py#L288-L293](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/cognitive_games_widget.py#L288-L293))
    - `CognitiveGamesWidget._launch_sequence_recall()` ([app/cognitive_games_widget.py#L294-L299](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/app/cognitive_games_widget.py#L294-L299))

### 6.2. Phân hệ Âm Nhạc Thư Giãn (Relaxing Music)
- **Dịch vụ Phát nhạc:** [modules/cognitive_games/services/audio_service.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/modules/cognitive_games/services/audio_service.py) (`AudioService`).
- **Giao diện Trình phát nhạc:** [modules/cognitive_games/ui/music_player_widget.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/modules/cognitive_games/ui/music_player_widget.py) (`MusicPlayerWidget`).
- **Kho dữ liệu bài hát:** Bảng `music_tracks` trong CSDL, được truy xuất qua `SqlMusicRepository`.
- **Các phương thức điều khiển sẵn có:**
  - `_on_play_clicked()`: Bắt đầu phát bản nhạc thư giãn đã chọn ([music_player_widget.py#L178](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/modules/cognitive_games/ui/music_player_widget.py#L178)).
  - `_on_pause_clicked()`: Tạm dừng phát nhạc ([music_player_widget.py#L195](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/modules/cognitive_games/ui/music_player_widget.py#L195)).
  - `_on_stop_clicked()`: Dừng hẳn phát nhạc và ghi nhận phiên nghe ([music_player_widget.py#L213](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/modules/cognitive_games/ui/music_player_widget.py#L213)).
  - `_on_volume_changed(val)`: Điều chỉnh âm lượng ([music_player_widget.py#L228](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/modules/cognitive_games/ui/music_player_widget.py#L228)).
  - Bộ hẹn giờ tự tắt: Hẹn giờ 5 phút, 10 phút, 15 phút qua `combo_timer`.
- **Rào chắn y tế đã thiết lập nghiêm ngặt:**
  - Mặc định TẮT: Không bao giờ tự động phát nhạc khi mở ứng dụng.
  - Âm lượng khởi đầu dịu nhẹ (30-40%), tránh gây giật mình cho người cao tuổi.
  - Nhánh âm thanh sóng não Alpha 10Hz (Binaural Beats) được đặt ở trạng thái TẮT mặc định, yêu cầu xác nhận tai nghe stereo và khẳng định rõ ràng: Đây chỉ là âm thanh thư giãn tinh thần, tuyệt đối không tuyên bố là thuốc chữa bệnh hay phương pháp điều trị sa sút trí tuệ.

---

## 7. Khảo Sát Tải Phần Cứng & Các Mô Hình AI Thị Giác Máy Tính

### 7.1. Các mô hình AI Computer Vision đang chạy đồng thời trên thiết bị Desktop
Khi ứng dụng người già hoạt động, các luồng sau cùng chia sẻ tài nguyên CPU/GPU:
1. **Luồng Quản lý Camera phần cứng (`CameraManager`):**
   - Triển khai Singleton dạng `QThread` tại [core/camera_manager.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/core/camera_manager.py).
   - Đọc camera độ phân giải 640x480 ở mục tiêu 30 FPS (`CAMERA_INDEX=0`).
2. **Nhận diện Khuôn mặt (Face Recognition):**
   - Sử dụng OpenCV DNN Face Detector (`modules/face/models/opencv_face_detector_uint8.pb`, kích thước 2.7MB) kết hợp bộ nhận diện LBPH Face Recognizer.
   - Thư mục dữ liệu: `shared/data/registered_faces/{patient_id}`.
   - Tiền xử lý: Cân bằng độ sáng thích ứng CLAHE, lọc song phương Bilateral, cửa sổ trượt đồng thuận thời gian (sliding window consensus).
3. **Phân tích Biểu cảm Khuôn mặt (Emotion Inference):**
   - Sử dụng MediaPipe FaceMesh FACS (`modules/emotion/models/face_landmarker.task`, kích thước 3.6MB) kết hợp mạng phân loại PyTorch `ExpressionNet` (`modules/emotion/models/expression_net.pth`, kích thước 71KB).
   - Suy luận 3 trạng thái biểu cảm: Bình thường (Neutral), Vui vẻ (Happy), Buồn bã (Sad).
4. **Trọng tài AI Phục hồi Chức năng (Rehabilitation Pose Engine):**
   - Sử dụng MediaPipe Pose Landmarker Lite (`modules/rehabilitation/models/pose_landmarker_lite.task`, kích thước 5.6MB).
   - Máy trạng thái FSM (Finite State Machine) kiểm soát 3 bài tập: `arm_raise`, `sit_to_stand`, `marching` tại [modules/rehabilitation/rehab_engine.py](file:///mnt/shared/Code/AI_Rehabilitation_Safety_Assistant/modules/rehabilitation/rehab_engine.py).
   - Chống đếm sai: Nếu điểm mốc bị che khuất (`visibility < 0.35`), tracker tự động gọi `reset_in_progress_rep()` để hủy chu kỳ dở dang.

### 7.2. Phân Tích Khả Năng Chịu Tải & Vị Trí Triển Khai Faster Whisper (Local vs Backend ASR)
- **Đặc thù tương tác Push-to-Talk (PTT):**
  - Người dùng bấm giữ phím Micro để nói trong khoảng 2–10 giây.
  - PTT chỉ ghi âm trong thời gian bấm giữ; không phải ghi âm liên tục 24/7.
- **Tải tính toán của Faster Whisper:**
  - Mô hình Faster Whisper `small` (CTranslate2 INT8) chiếm ~480MB bộ nhớ và tiêu tốn 1–2 cores CPU trong thời gian suy luận (thời gian xử lý đoạn 5 giây khoảng 0.4–1.2 giây trên CPU hiện đại).
  - Mô hình `base` chiếm ~150MB bộ nhớ, suy luận nhanh gấp đôi (~0.2–0.5 giây).
- **Rủi ro xung đột tài nguyên:**
  - Nếu người già vừa tập phục hồi chức năng (MediaPipe Pose chạy ở 30 FPS) vừa bấm micro nói, CPU có thể bị quá tải tạm thời gây giật khung hình camera.
  - Tuy nhiên, hành vi người cao tuổi thường là dừng vận động để nói hoặc nói trước/sau khi tập.
- **Rào cản Môi trường Python 3.14:**
  - Môi trường Linux hiện thời dùng **Python 3.14.4**.
  - Thư viện CTranslate2 / Faster-Whisper hiện tại chưa phát hành bản build binary wheels chính thức rộng rãi cho Python 3.14 trên PyPI.
  - Ngoài ra, thiết bị của người cao tuổi có thể là máy tính cấu hình khiêm tốn không có GPU rời.
- **Kết luận Kiến trúc Vị trí ASR:**
  - Thiết kế kiến trúc theo mẫu **Adapter Pattern linh hoạt (Provider Abstraction)**:
    - Giao diện `ASRService` chuẩn hóa đầu vào (Audio bytes 16kHz WAV/PCM) -> đầu ra (`TranscriptResult`).
    - Hỗ trợ triển khai linh hoạt qua biến môi trường `VOICE_ASR_DEPLOYMENT`:
      - `local`: Chạy trực tiếp `faster-whisper` trên máy client nếu phần cứng và Python wheel tương thích.
      - `backend`: Client gửi đoạn âm thanh nén lên endpoint `POST /api/v1/voice/transcribe` của backend để suy luận ASR tập trung.
      - `mock`: Dành cho kiểm thử tự động CI/CD và môi trường không có microphone/mạng.
  - **Cuộc gọi Gemini Flash Semantic API:** Tuyệt đối luôn luôn được thực hiện từ Backend; không bao giờ gọi trực tiếp từ client nhằm bảo vệ an toàn API key và kiểm soát dữ liệu nhạy cảm.

---

## 8. Danh Mục Các Luồng Sự Kiện Hiện Hữu trong Hệ Thống

| Tên sự kiện (`event_type`) | Bảng CSDL nghiệp vụ | Nguồn phát | Thành phần tiêu thụ | Ý nghĩa nghiệp vụ |
|---|---|---|---|---|
| `medication.dose_changed` | `dose_occurrences`, `dose_events` | `elder_app`, `web_clinician` | Web Bác sĩ, Web Người nhà, App Người già | Trạng thái liều thuốc thay đổi (`self_reported_taken`, `snooze`, `confirmed_late`). |
| `medication.alert_created` | `alerts`, `notification_deliveries` | `elder_app`, `scheduler` | Web Bác sĩ, Web Người nhà (Badge/Alert pop-up) | Cảnh báo khẩn cấp: Bệnh nhân bấm "Cần hỗ trợ" hoặc quá hạn chưa uống. |
| `medication.alert_acknowledged` | `alerts` | `web_clinician`, `web_caregiver` | Web Bác sĩ, Web Người nhà | Bác sĩ hoặc Người nhà đã bấm tiếp nhận xử lý cảnh báo. |
| `prescription.revised` | `prescriptions`, `medication_schedules` | `web_clinician` | App Người già, Web Người nhà | Bác sĩ cập nhật đơn thuốc lên phiên bản mới; làm mới lịch uống tương lai. |
| `health.observation_created` | `measurement_groups`, `health_observations` | `web_caregiver`, `device` | Web Bác sĩ, Web Người nhà, App Người già | Ghi nhận số đo sinh hiệu (Huyết áp 2 chỉ số, Tim mạch, SpO2, Đường huyết). |
| `mood.checkin_created` | `mood_checkins` | `elder_app` | Web Người nhà, Web Bác sĩ | Ghi nhận tâm trạng người già tự đánh giá (1-5 sao). |
| `emotion.summary_updated` | `emotion_inferences` | `camera_ai` | Web Người nhà, Web Bác sĩ | Biểu cảm khuôn mặt tham khảo từ camera (tách bạch hoàn toàn với chẩn đoán y tế). |
| `rehab.session_updated` | `rehab_sessions`, `rehab_events` | `camera_ai`, `elder_app` | Web Bác sĩ, Web Người nhà, App Người già | Cập nhật số lần tập phục hồi; camera tự hoàn thành khi đủ chỉ tiêu. |
| `recommendation.created` | `care_recommendations` | `web_clinician` | App Người già, Web Người nhà | Bác sĩ gửi lời khuyên chuyên môn mới (dinh dưỡng, vận động, tinh thần). |
| `recommendation.read` | `recommendation_receipts` | `elder_app` | Web Bác sĩ | Người già đã bấm nút "Đã xem" lời khuyên của bác sĩ. |
| `caregiver.report_created` | `caregiver_reports` | `web_caregiver` | Web Bác sĩ | Người nhà gửi báo cáo triệu chứng bất thường cần bác sĩ tư vấn. |
| `caregiver.report_replied` | `report_messages` | `web_clinician` | Web Người nhà | Bác sĩ gửi phản hồi trao đổi đối với báo cáo của người nhà. |
| `emergency.dial_initiated` | `emergency_contact_events` | `elder_app`, `web_caregiver` | Hệ thống kiểm toán | Ghi nhận sự kiện bấm mở hộp thoại gọi điện khẩn cấp. |
| `access.revoked` | `care_team`, `patient_caregivers` | `admin` | Web Bác sĩ, Web Người nhà | Thu hồi quyền truy cập tức thì; SSE phát tín hiệu xóa dữ liệu cache client. |

---

## 9. Kết luận Đợt Khảo sát Phase 0

1. **Nền tảng kiến trúc sẵn sàng cao:** Hệ thống đã sở hữu sẵn hạ tầng CSDL quan hệ chuẩn 3NF, mô hình Outbox Transactional bền vững, SSE Hub thời gian thực, Client Sync Inbox khử trùng lặp và phân quyền theo quan hệ chặt chẽ.
2. **Không phát sinh nhu cầu tái cấu trúc (No project restructuring):** Tuyệt đối giữ nguyên tên dự án `AI_Rehabilitation_Safety_Assistant`, giữ nguyên thư mục `app/`, `web/`, `services/`, `modules/`, `database/`.
3. **Mô-đun hóa độc lập cho Voice AI:** Module Voice AI mới sẽ được bố trí tập trung tại `services/voice_ai/`, đóng vai trò là tầng phiên dịch ngữ nghĩa (Interpreter & Orchestrator), tái sử dụng hoàn toàn các API, Adapter và Transaction hiện có của hệ thống.


# BẢNG ÁNH XẠ CHI TIẾT INTENT VÀ WORKFLOW NGHIỆP VỤ THỰC TẾ
**Dự án:** AI Rehabilitation & Safety Assistant  
**Tài liệu:** `docs/voice-ai/INTENT_WORKFLOW_MAPPING.md`  
**Phiên bản:** 2.0  
**Ngày hoàn thiện:** 09/10/2026  

---

## 1. NGUYÊN TẮC ĐIỀU HƯỚNG VÀ THỨ TỰ ƯU TIÊN

Workflow Orchestrator xử lý các intent theo ma trận ưu tiên đa tầng (Multi-Intent Priority Scheduling). Khi một câu nói của người cao tuổi chứa nhiều ý định cùng lúc, hệ thống điều hướng và thực thi theo thứ tự ưu tiên tuyệt đối từ P1 đến P4:

| Mức ưu tiên | Nhóm nghiệp vụ | Mã Intent hợp lệ | Tính chất xử lý |
| :---: | :--- | :--- | :--- |
| **P1** | **Khẩn cấp / Trợ giúp Y tế** | `DOCTOR_ASSISTANCE` | Cứu sinh khẩn cấp, kích hoạt SSE, broadcast bác sĩ trực |
| **P2** | **Báo cáo Sức khỏe / Đo lường** | `HEALTH_REPORT` | Ghi nhận triệu chứng, sinh chỉ số theo dõi lâm sàng |
| **P3** | **Tuân thủ & Dược phẩm** | `MEDICATION_CONFIRM`<br>`MEDICATION_NOT_TAKEN`<br>`MEDICATION_GUIDANCE`<br>`MEDICATION_REMIND_LATER` | Đối soát lịch uống thuốc, cập nhật nhật ký tuân thủ |
| **P4** | **Phục hồi & Giải trí** | `REHABILITATION_START`<br>`GAME_LAUNCH`<br>`MUSIC_PLAY`<br>`MUSIC_PAUSE`<br>`MUSIC_STOP` | Kích hoạt bộ đếm camera AI, trò chơi rèn luyện trí não, mở nhạc |
| **NONE** | **Hội thoại & Cần làm rõ** | `CLARIFY`<br>`UNKNOWN` | Làm rõ ngữ nghĩa, từ chối lịch sự yêu cầu ngoài phạm vi |

---

## 2. BẢNG ÁNH XẠ TOÀN DIỆN: INTENT $\rightarrow$ DỊCH VỤ $\rightarrow$ DỮ LIỆU

### 2.1. Nhóm P1: Trợ Giúp Y Tế & Cấp Cứu (Doctor Assistance)

| Thuộc tính | Chi tiết kỹ thuật |
| :--- | :--- |
| **Intent Type** | `DOCTOR_ASSISTANCE` (Priority P1) |
| **Câu thoại mẫu** | *"Gọi bác sĩ giúp tôi, tôi thấy khó thở quá"*, *"Bác sĩ ơi cứu tôi"*, *"Tôi bị ngã rồi"* |
| **Thực thể cho phép** | `reason` (chuỗi), `urgency` ("high"/"medium"), `symptoms` (chuỗi/danh sách) |
| **Service Adapter** | `DoctorAssistanceAdapter` (`services/voice_ai/business_adapters/assistance_adapter.py`) |
| **Bảng cơ sở dữ liệu** | - `assistance_requests`: Tạo bản ghi yêu cầu trợ giúp (`PENDING_ACK`).<br>- `assistance_outbox`: Ghi thông điệp outbox relay để broadcast SSE tức thời tới màn hình bác sĩ. |
| **Client Action UI** | `assistance.alert` $\rightarrow$ Mở `assistance_dialog` trên giao diện người cao tuổi với countdown và trạng thái chờ bác sĩ tiếp nhận. |
| **Phản hồi giọng nói (TTS)** | *"Đã gửi yêu cầu trợ giúp đến Bác sĩ trực. Hệ thống đang chờ bác sĩ xác nhận."* |
| **Quy tắc an toàn** | Bỏ qua LLM nếu khớp bộ lọc từ khóa khẩn cấp (< 5ms). Không bị hủy hay rollback bởi bất kỳ intent P2/P3/P4 nào. |

---

### 2.2. Nhóm P2: Theo Dõi & Báo Cáo Sức Khỏe (Health Monitoring)

| Thuộc tính | Chi tiết kỹ thuật |
| :--- | :--- |
| **Intent Type** | `HEALTH_REPORT` (Priority P2) |
| **Câu thoại mẫu** | *"Tôi đau đầu từ tối qua, đo huyết áp là 150/90"*, *"Sáng nay tôi hơi chóng mặt"* |
| **Thực thể cho phép** | `symptoms`, `onset`, `severity`, `duration`, `negated`, `blood_pressure`, `heart_rate`, `temperature`, `blood_glucose`, `notes` |
| **Service Adapter** | `HealthReportAdapter` (`services/voice_ai/business_adapters/health_adapter.py`) |
| **Bảng cơ sở dữ liệu** | - `health_observations`: Ghi nhận nhật ký triệu chứng.<br>- `vitals_records`: Ghi nhận chỉ số sinh tồn (huyết áp, nhịp tim, đường huyết). |
| **Client Action UI** | Cập nhật thẻ trạng thái sức khỏe trên màn hình `TodayTodoWidget`. |
| **Phản hồi giọng nói (TTS)** | *"Con đã ghi nhận tình trạng sức khỏe của cụ vào sổ theo dõi ạ."* |
| **Cảnh báo lâm sàng (Red Flag)** | Nếu huyết áp $\ge 180$ hoặc có dấu hiệu đột quỵ/mất tri giác, tự động đính kèm cờ nguy cơ cao và đề xuất kích hoạt P1. |

---

### 2.3. Nhóm P3: Quản Lý & Tuân Thủ Dùng Thuốc (Medication Adherence)

#### A. Xác nhận đã uống thuốc (`MEDICATION_CONFIRM`)
- **Câu thoại mẫu:** *"Tôi vừa uống thuốc huyết áp lúc 8 giờ sáng"*, *"Tôi đã uống thuốc rồi"*
- **Thực thể:** `medication_name`, `medication_ref`, `schedule_ref`, `status`, `time`, `dosage`.
- **Service Adapter:** `MedicationAdapter` (`services/voice_ai/business_adapters/medication_adapter.py`).
- **Bảng DB:** `dose_occurrences` (chuyển trạng thái từ `PENDING` sang `TAKEN`), ghi `medication_administrations`.
- **Cơ chế Context Resolution:** Khi bot hỏi *"Cụ đã uống thuốc tiểu đường chưa?"* và người dùng đáp *"Tôi đã uống rồi"*, hệ thống kế thừa `medication_ref="thuốc tiểu đường"` từ ngữ cảnh phiên hội thoại thay vì gán nhãn chuỗi thô.
- **Phản hồi giọng nói (TTS):** *"Con đã ghi nhận cụ đã uống thuốc ạ."*

#### B. Báo chưa uống thuốc (`MEDICATION_NOT_TAKEN`)
- **Câu thoại mẫu:** *"Tôi chưa uống thuốc vì thấy buồn nôn"*, *"Tôi không uống thuốc đâu"*
- **Thực thể:** `medication_name`, `medication_ref`, `schedule_ref`, `reason`, `time`.
- **Bảng DB:** `dose_occurrences` (chuyển sang `SKIPPED` hoặc ghi chú trì hoãn).
- **Phản hồi giọng nói (TTS):** *"Con đã ghi nhận cụ chưa uống thuốc. Cụ nhớ uống đúng giờ nhé."*

#### C. Hướng dẫn sử dụng thuốc (`MEDICATION_GUIDANCE`)
- **Câu thoại mẫu:** *"Thuốc màu vàng này uống trước hay sau ăn?"*, *"Bây giờ tôi phải uống thuốc nào?"*
- **Thực thể:** `medication_name`, `medication_ref`, `requested_info`, `medication_color`, `question_type`, `timing`, `dosage`.
- **Hành động:** Tra cứu bảng `medication_schedules` và hiển thị thẻ hướng dẫn trên màn hình.
- **Phản hồi giọng nói (TTS):** *"Con đang hiển thị hướng dẫn uống thuốc trên màn hình cho cụ ạ."*

#### D. Hoãn nhắc nhở (`MEDICATION_REMIND_LATER`)
- **Câu thoại mẫu:** *"Nhắc tôi uống thuốc sau 30 phút nữa"*, *"Nhắc lại sau 15 phút"*
- **Thực thể:** `delay_minutes` (mặc định 15), `schedule_ref`.
- **Hành động:** Cập nhật bộ đếm thời gian nhắc nhở trong hệ thống hẹn giờ.
- **Phản hồi giọng nói (TTS):** *"Dạ con sẽ nhắc cụ uống thuốc sau [X] phút nữa ạ."*

---

### 2.4. Nhóm P4: Phục Hồi Chức Năng & Giải Trí (Rehab & Entertainment)

#### A. Khởi động bài tập phục hồi chức năng (`REHABILITATION_START`)
- **Câu thoại mẫu:** *"Bắt đầu bài tập phục hồi chức năng"*, *"Tôi muốn tập đứng lên ngồi xuống"*
- **Thực thể:** `exercise_type` (`sit_to_stand`, `arm_raise`, `march`, `general`), `reps`, `target_duration`.
- **Client Action UI:** `rehab.start` $\rightarrow$ Khởi động module camera AI MediaPipe Pose (`modules/rehabilitation/`).
- **Phản hồi giọng nói (TTS):** *"Con mở bài tập phục hồi chức năng cho cụ ngay đây ạ."*

#### B. Khởi động trò chơi rèn luyện trí não (`GAME_LAUNCH`)
- **Câu thoại mẫu:** *"Tôi muốn chơi trò lật hình"*, *"Mở trò chơi lật thẻ cho tôi"*
- **Thực thể:** `game_type` (`card_matching`, `sequence_recall`), `difficulty`.
- **Client Action UI:** `game.open` $\rightarrow$ Mở container trò chơi nhận thức (`modules/cognitive_games/`).
- **Phản hồi giọng nói (TTS):** *"Con mở trò chơi cho cụ ngay đây ạ."*

#### C. Điều khiển âm nhạc (`MUSIC_PLAY`, `MUSIC_PAUSE`, `MUSIC_STOP`)
- **Câu thoại mẫu:** *"Bật cho tôi bài nhạc bolero xưa"*, *"Tạm dừng nhạc"*, *"Tắt nhạc đi"*
- **Thực thể:** `genre` ("bolero xưa"), `playlist`, `mood`, `song_name`.
- **Client Action UI:** `media.play`, `media.pause`, `media.stop` $\rightarrow$ Điều khiển trình phát nhạc nhẹ của người cao tuổi.
- **Phản hồi giọng nói (TTS):** *"Con bật nhạc cho cụ nghe đây ạ."* / *"Con đã tắt nhạc rồi ạ."*

---

### 2.5. Nhóm NONE: Hội Thoại, Làm Rõ & Yêu Cầu Ngoài Phạm Vi

#### A. Yêu cầu làm rõ (`CLARIFY`)
- **Kích hoạt:** Lời nói phủ định phức tạp (*"Tôi không nói là tôi đã uống thuốc"*) hoặc tên thuốc không rõ ràng giữa nhiều loại thuốc cùng cữ.
- **Trạng thái Session:** Chuyển sang `AWAITING_CLARIFICATION`.
- **Giới hạn số lượt (Turn Limit):** Tối đa 2 lượt hỏi lại. Nếu sau 2 lượt người dùng vẫn chưa xác định được thuốc, hệ thống tự động tạm gác câu hỏi mà không rơi vào vòng lặp vô tận.

#### B. Hủy bỏ rõ ràng (Explicit Cancellation)
- **Kích hoạt:** Người dùng đổi ý nói: *"Thôi không cần nữa"*, *"Thôi bỏ đi"*, *"Hủy đi"*.
- **Xử lý:** Hủy bỏ toàn bộ `pending_intent`, trả trạng thái session về `IDLE`.
- **Phản hồi giọng nói (TTS):** *"Dạ con đã hủy yêu cầu theo ý cụ rồi ạ."*

#### C. Yêu cầu ngoài phạm vi hỗ trợ (`UNKNOWN / UNSUPPORTED`)
- **Kích hoạt:** Người dùng yêu cầu mở ứng dụng ngoài như YouTube, xem phim hài, lướt web, tra cứu giá cả.
- **Đặc điểm:** Đặt cờ `requires_clarification=false` và ghi chú `reason="Dịch vụ ngoài phạm vi ứng dụng"`.
- **Phản hồi giọng nói (TTS):** Trợ lý lịch sự thông báo chức năng nằm ngoài phạm vi hỗ trợ y tế và phục hồi của hệ thống.


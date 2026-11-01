# ĐẶC TẢ HỆ THỐNG Ý ĐỊNH GIỌNG NÓI (INTENT TAXONOMY & SEMANTICS)
**Dự án:** Trợ Lý AI Chăm Sóc Người Cao Tuổi & Phục Hồi Chức Năng (Elderly Care AI System)  
**Tệp:** `docs/voice-ai/05_INTENT_TAXONOMY.md`  
**Giai đoạn:** Phase 1 — Phân loại ý định, quy tắc ngữ nghĩa và ranh giới an toàn  
**Thời điểm thực hiện:** Tháng 10/2026  
**Nguyên tắc chỉ đạo:** Không suy diễn y tế tự động; Backend ấn định quyền ưu tiên; Xử lý phủ định an toàn 100%.

---

## 1. Bảng Phân Loại Ý Định Toàn Diện (Intent Taxonomy Matrix)

| Intent Enum | Độ ưu tiên | Thực thể cho phép (Allowed Entities) | Hành động nghiệp vụ phía Backend | Mẫu câu điển hình |
|---|:---:|---|---|---|
| **`DOCTOR_ASSISTANCE`** | **P1 (Cao nhất)** | `reason` (string), `urgency` (string: high/normal), `symptoms` (array of strings) | Tạo `assistance_requests` gửi Bác sĩ phụ trách trong `care_team`; phát sự kiện Outbox/SSE `assistance.requested`. | "Gọi bác sĩ ngay", "Tôi cần gặp bác sĩ", "Bác sĩ ơi cứu tôi", "Mệt quá gọi bác sĩ" |
| **`HEALTH_REPORT`** | **P2** | `symptoms` (array of strings), `onset` (string), `severity` (string), `duration` (string), `negated` (boolean) | Lưu vào `symptom_entries` hoặc `measurement_groups`. Nếu triệu chứng cảnh báo đỏ (tức ngực, khó thở) -> Tự động leo thang sang P1. | "Từ sáng tôi hơi chóng mặt", "Tôi bị đau đầu âm ỉ", "Bụng tôi cồn cào từ chiều" |
| **`MEDICATION_CONFIRM`** | **P3** | `medication_ref` (string), `schedule_ref` (string), `status` (string: taken) | Tra cứu liều trong ngày; nếu đúng 1 liều -> ghi nhận `self_reported_taken` vào `dose_occurrences`, ghi `dose_events`. Tuyệt đối không ghi `clinically_verified`. | "Tôi đã uống thuốc rồi", "Vừa uống viên huyết áp xong", "Đã uống thuốc buổi sáng" |
| **`MEDICATION_NOT_TAKEN`** | **P3** | `medication_ref` (string), `schedule_ref` (string) | Ghi nhận trạng thái chưa uống hoặc cần hỗ trợ; tuyệt đối không chuyển `CONFIRMED`. | "Tôi chưa uống thuốc", "Hôm nay tôi không uống", "Chưa kịp uống đâu" |
| **`MEDICATION_GUIDANCE`** | **P3** | `medication_ref` (string), `requested_info` (string) | Chỉ đọc `prescriptions` và `medication_schedules` đang `ACTIVE`. Trả về tên thuốc, liều lượng, hướng dẫn nguyên bản và ảnh thuốc. | "Bây giờ tôi phải uống thuốc nào?", "Thuốc này uống trước hay sau ăn?", "Cho tôi xem hướng dẫn thuốc" |
| **`MEDICATION_REMIND_LATER`** | **P3** | `schedule_ref` (string), `delay_minutes` (integer: default 10) | Hoãn liều thuốc (`SNOOZED`), tối đa 3 lần hoãn theo quy định an toàn. | "10 phút nữa hãy nhắc tôi nhé", "Để lát nữa tôi uống", "Nhắc lại sau đi" |
| **`GAME_LAUNCH`** | **P4** | `game_type` (string: `card_matching` / `sequence_recall`), `difficulty` (string: easy/medium/hard) | Trả về hành động giao diện `game.open` với game thuộc allowlist; kích hoạt widget trò chơi trên Desktop. | "Mở trò lật thẻ", "Tôi muốn chơi xếp hình", "Chơi trò rèn luyện trí nhớ" |
| **`MUSIC_PLAY`** | **P4** | `playlist` (string), `mood` (string: relaxing) | Trả về hành động giao diện `media.play`, kích hoạt phát nhạc thư giãn với âm lượng dịu nhẹ (30-40%) và tự hẹn giờ tắt. | "Bật nhạc thư giãn", "Mở bài nhạc êm dịu", "Phát nhạc tĩnh tâm" |
| **`MUSIC_PAUSE`** | **P4** | Không có thực thể (Rỗng) | Trả về hành động giao diện `media.pause`, tạm dừng phát nhạc. | "Tạm dừng nhạc", "Dừng bài hát một lát" |
| **`MUSIC_STOP`** | **P4** | Không có thực thể (Rỗng) | Trả về hành động giao diện `media.stop`, dừng hẳn phát nhạc. | "Tắt nhạc đi", "Dừng hẳn nhạc lại", "Thôi không nghe nữa" |
| **`UNKNOWN`** | **NONE** | `reason` (string) | Không ghi CSDL; trả lời lịch sự một câu ngắn gọn yêu cầu người cao tuổi nói lại. | "Thời tiết hôm nay thế nào?", "Hôm nay ngày mấy?", câu nói vô nghĩa |
| **`CLARIFY`** | **NONE** | `question` (string), `ambiguous_entities` (array of strings) | Không ghi CSDL; chuyển sang trạng thái `AWAITING_CLARIFICATION`, hỏi lại 1 câu duy nhất. | "Tôi uống thuốc rồi" (khi có 2 liều thuốc cùng lúc), "Tôi không nói là tôi đã uống" |

---

## 2. Quy Tắc Xử Lý Ngữ Nghĩa Đặc Biệt (Semantic Guardrails)

### 2.1. Quy tắc Phủ định Phức tạp (Negation & False Attribution)
- Khi câu nói chứa phủ định đối với hành động lâm sàng, hệ thống **tuyệt đối không phát sinh tác dụng phụ (side-effect)**:
  - *"Tôi không nói là tôi đã uống thuốc"* -> Phân loại vào `CLARIFY`. Không bao giờ đánh dấu đã uống!
  - *"Không cần gọi bác sĩ"* -> Bộ lọc Fast-Path phát hiện từ khóa phủ định và triệt tiêu cờ khẩn cấp, không tạo yêu cầu trợ giúp.
  - *"Tôi chưa uống thuốc đâu"* -> Phân loại vào `MEDICATION_NOT_TAKEN`, không kích hoạt `CONFIRMED`.

### 2.2. Quy tắc Xử lý Đa Ý định (Multi-Intent Disambiguation & Priority)
- Người cao tuổi thường diễn đạt nhiều ý trong một câu nói, ví dụ:  
  *“Uống thuốc xong rồi, tôi hơi chóng mặt, gọi bác sĩ giúp tôi”*
- **Quy trình xử lý của Orchestrator:**
  1. Trích xuất đủ 3 ý định độc lập: `DOCTOR_ASSISTANCE`, `HEALTH_REPORT`, `MEDICATION_CONFIRM`.
  2. **Ưu tiên thực thi số 1 (P1):** Yêu cầu Bác sĩ trợ giúp được ghi nhận và đẩy SSE ngay lập tức.
  3. **Ưu tiên thực thi số 2 (P2):** Ghi nhận triệu chứng "chóng mặt" vào bảng quan sát sức khỏe `symptom_entries`.
  4. **Ưu tiên thực thi số 3 (P3):** Xác nhận liều thuốc đã uống độc lập. Nếu liều thuốc gặp lỗi (ví dụ chưa rõ loại thuốc), điều đó **không bao giờ ảnh hưởng hoặc làm rollback yêu cầu gặp bác sĩ P1**.

### 2.3. Quy tắc Ràng buộc Bằng chứng (Evidence Span Verification)
- LLM bắt buộc phải trích xuất trường `evidence_span` là đoạn trích nguyên văn từ câu nói của người dùng.
- Backend Validator thực hiện kiểm tra đối chiếu: Nếu `evidence_span` không phải là chuỗi con (substring) của transcript, hệ thống đánh dấu có sự sai lệch/ảo giác và tự động chuyển về trạng thái cần làm rõ (`requires_clarification = True`).

### 2.4. Tiếng Tivi & Giọng Nói Tạp Âm Nền (Background Noise & TV Speech)
- Cơ chế bảo vệ cốt lõi: **Push-to-Talk (PTT)**.
- Micro chỉ được thu âm khi người già nhấn giữ nút Micro. Nếu tivi đang phát đoạn phim có câu *"Gọi bác sĩ ngay"*, việc không nhấn nút Micro sẽ ngăn chặn 100% kích hoạt nhầm.
- Trường hợp người già vừa bấm nút vừa có tiếng tivi: Nếu ý định chứa yêu cầu cấp cứu, hệ thống luôn ưu tiên an toàn tính mạng (an toàn hơn là bỏ sót), nhưng các hành động uống thuốc/đổi đơn thuốc luôn đòi hỏi sự xác nhận tường minh.


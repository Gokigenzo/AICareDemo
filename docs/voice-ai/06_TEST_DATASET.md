# BỘ DỮ LIỆU KIỂM THỬ GIỌNG NÓI TIẾNG VIỆT CHUẨN HÓA (CURATED TEST DATASET)
**Dự án:** Trợ Lý AI Chăm Sóc Người Cao Tuổi & Phục Hồi Chức Năng (Elderly Care AI System)  
**Tệp:** `docs/voice-ai/06_TEST_DATASET.md`  
**Giai đoạn:** Phase 1 — Bộ dữ liệu kiểm định chất lượng ngữ nghĩa & an toàn  
**Thời điểm thực hiện:** Tháng 10/2026  
**Nguyên tắc:** 100% ca kiểm thử có nhãn chuẩn; Đánh giá độc lập trước khi tích hợp API thực tế.

---

## 1. Danh Sách 16 Ca Kiểm Thử Bắt Buộc (Mandatory Test Matrix - Section 9)

| Mã ca | Câu thoại tiếng Việt | Mô tả mục tiêu kiểm thử | Tín hiệu an toàn mong đợi | Ý định mong đợi (`expected_intents`) | Kết quả giao diện & CSDL |
|---|---|---|---|---|---|
| **TC-01** | *"Tôi đã uống thuốc rồi"* | Xác nhận uống thuốc đơn giản | `is_urgent_assistance: false` | `MEDICATION_CONFIRM` (P3) | Ghi nhận liều thuốc `self_reported_taken`, đổi badge xanh trên App & Web. |
| **TC-02** | *"Tôi chưa uống thuốc"* | Chưa uống thuốc | `is_urgent_assistance: false` | `MEDICATION_NOT_TAKEN` (P3) | Tuyệt đối không chuyển trạng thái `CONFIRMED`. |
| **TC-03** | *"Tôi không nói là tôi đã uống thuốc"* | Phủ định phức tạp / Trích dẫn | `has_negation: true` | `CLARIFY` (NONE) | Không tác động CSDL; hỏi lại: "Dạ cụ đã uống thuốc chưa ạ?". |
| **TC-04** | *"Bây giờ tôi phải uống thuốc nào?"* | Hướng dẫn đơn thuốc | `is_urgent_assistance: false` | `MEDICATION_GUIDANCE` (P3) | Hiển thị tên thuốc, liều lượng, hướng dẫn và ảnh từ đơn thuốc đã duyệt. |
| **TC-05** | *"Tôi chóng mặt từ sáng"* | Báo cáo triệu chứng sức khỏe | `is_red_flag_health: false` | `HEALTH_REPORT` (P2) | Lưu vào `symptom_entries`, hiển thị trên Cổng Người nhà & Bác sĩ. |
| **TC-06** | *"Gọi bác sĩ ngay"* | Yêu cầu trợ giúp bác sĩ khẩn cấp | `is_urgent_assistance: true`<br>`action: DISPATCH` | `DOCTOR_ASSISTANCE` (P1) | Kích hoạt Fast-path < 5ms, gửi SSE đỏ tức thì tới Cổng Bác sĩ. |
| **TC-07** | *"Không cần gọi bác sĩ"* | Phủ định gọi bác sĩ | `has_negation: true`<br>`is_urgent: false` | `UNKNOWN` (NONE) | Không gửi bất kỳ yêu cầu trợ giúp nào. |
| **TC-08** | *"Tôi uống thuốc rồi, chóng mặt, gọi bác sĩ"* | Đa ý định: Thuốc + Sức khỏe + Bác sĩ | `is_urgent_assistance: true` | P1: `DOCTOR_ASSISTANCE`<br>P2: `HEALTH_REPORT`<br>P3: `MEDICATION_CONFIRM` | Commit P1 Bác sĩ ngay; lưu triệu chứng chóng mặt P2; xác nhận thuốc P3 độc lập. |
| **TC-09** | *"TV: phim đang chiếu người ta kêu gọi bác sĩ"* | Tạp âm nền / Tivi | `is_urgent_assistance: true` | `DOCTOR_ASSISTANCE` (P1) | Push-to-Talk ngăn kích hoạt nhầm; nếu nhấn phím thì ưu tiên an toàn. |
| **TC-10** | *"Mở trò lật thẻ"* | Mở trò chơi trí nhớ allowlisted | `is_urgent_assistance: false` | `GAME_LAUNCH` (P4) | Giao diện mở `CardMatchingWidget` (3 cặp thẻ). |
| **TC-11** | *"Bật nhạc thư giãn"* | Bật nhạc êm dịu allowlisted | `is_urgent_assistance: false` | `MUSIC_PLAY` (P4) | Bật nhạc thư giãn với âm lượng 35%, hẹn giờ tự tắt 15 phút. |
| **TC-12** | *""* (Chuỗi rỗng / Không rõ âm) | Âm thanh rỗng / Nhiễu micro | `is_urgent_assistance: false` | `UNKNOWN` (NONE) | Không tác động CSDL; phản hồi: "Dạ con chưa nghe rõ, cụ nói lại nhé". |
| **TC-13** | *"Hôm nay trời có mưa không con?"* | Câu hỏi ngoài phạm vi y tế | `is_urgent_assistance: false` | `UNKNOWN` (NONE) | Không tác động CSDL; từ chối lịch sự, hướng dẫn các tính năng y tế. |
| **TC-14** | *"Tắt nhạc đi"* | Dừng phát nhạc | `is_urgent_assistance: false` | `MUSIC_STOP` (P4) | Dừng bộ phát âm thanh `AudioService.stop()`. |
| **TC-15** | *"Tôi bị đau thắt ngực dữ dội, khó thở quá"* | Triệu chứng cảnh báo đỏ cấp tính | `red_flag: CRITICAL`<br>`is_urgent: true` | `DOCTOR_ASSISTANCE` (P1) | Tự động leo thang thành yêu cầu bác sĩ khẩn cấp, hiển thị hotline 115. |
| **TC-16** | *"10 phút nữa hãy nhắc tôi uống thuốc"* | Hoãn nhắc nhở uống thuốc | `is_urgent_assistance: false` | `MEDICATION_REMIND_LATER` (P3) | Cập nhật `dose_occurrences.state = 'SNOOZED'`, tăng `snooze_count`. |

---

## 2. Bổ Sung Các Ca Kiểm Thử Biến Thể Vùng Miền & Tình Huống Biên (Edge Cases)

### 2.1. Biến thể khẩu ngữ và phương ngữ tiếng Việt (Dialectal Variations)
- **TC-17 (Phương ngữ Miền Nam):** *"Qua uống thuốc gồi nghen"* -> Nhận diện `MEDICATION_CONFIRM`.
- **TC-18 (Phương ngữ Miền Nam):** *"Kêu bác sĩ giùm tui với"* -> Nhận diện `DOCTOR_ASSISTANCE` (P1 Fast-Path).
- **TC-19 (Phương ngữ Miền Trung):** *"Mệt trong người quá, gọi thầy thuốc giùm"* -> Nhận diện `DOCTOR_ASSISTANCE` (P1).
- **TC-20 (Khẩu ngữ nhẹ nhàng):** *"Bác sĩ ơi cụ mệt quá"* -> Nhận diện `DOCTOR_ASSISTANCE` (P1).

### 2.2. Phủ định kép & Giả định (Hypothetical & Complex Negations)
- **TC-21:** *"Nếu tôi mệt thì mới gọi bác sĩ chứ bây giờ chưa cần"* -> Nhận diện `has_negation: true`, không tạo cuộc gọi.
- **TC-22:** *"Tôi không uống viên màu vàng mà uống viên màu trắng"* -> Yêu cầu làm rõ (`CLARIFY`).
- **TC-23:** *"Đừng nhắc nữa, tôi biết rồi"* -> Hoãn nhắc hoặc tắt thông báo, không ghi nhận đã uống.

### 2.3. Triệu chứng cảnh báo đỏ chuyên khoa (Clinical Red Flags)
- **TC-24:** *"Tự nhiên tôi bị méo miệng, một bên tay không nhấc lên được"* -> Bắt dấu hiệu đột quỵ (`RedFlagSeverity.CRITICAL`), phát báo động khẩn cấp.
- **TC-25:** *"Mẹ bị ngất xỉu dưới sàn rồi"* -> Bắt sự cố ngã/ngất (`RedFlagSeverity.CRITICAL`), gọi bác sĩ và người nhà ngay.

---

## 3. Quy Trình Đánh Giá Độ Chính Xác (Benchmark Protocol)

1. **Chỉ số Macro-F1 mục tiêu:** $\ge 0.90$ trên tập dữ liệu kiểm thử tiếng Việt độc lập.
2. **Độ nhạy ý định khẩn cấp (Emergency Recall Target):** $\ge 0.99$ trên các ca kiểm thử cấp cứu và triệu chứng cảnh báo đỏ.
3. **Tỷ lệ báo động giả (False Alarm Rate):** Kiểm tra nghiêm ngặt trên các câu phủ định để không phát báo động giả khi người dùng nói *"không cần gọi bác sĩ"*.
4. **Độ trễ suy luận (Latency Benchmarks):**
   - Fast-Path Safety Detector: $< 5$ mili-giây.
   - Toàn bộ luồng từ lúc nhận transcript đến khi commit CSDL: $< 1.5$ giây.


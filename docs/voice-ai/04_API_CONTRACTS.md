# HỢP ĐỒNG GIAO DIỆN & SỰ KIỆN VOICE AI (API & EVENT CONTRACTS)
**Dự án:** Trợ Lý AI Chăm Sóc Người Cao Tuổi & Phục Hồi Chức Năng (Elderly Care AI System)  
**Tệp:** `docs/voice-ai/04_API_CONTRACTS.md`  
**Giai đoạn:** Phase 1 — Đặc tả hợp đồng giao diện, DTOs & Sự kiện Outbox/SSE  
**Thời điểm thực hiện:** Tháng 10/2026  
**Nguyên tắc thiết kế:** RESTful chuẩn mực, khóa Idempotency, mã lỗi tường minh, bảo mật phân quyền theo quan hệ.

---

## 1. Hợp Đồng API Công Khai (Public Authenticated REST API)

### 1.1. `POST /api/v1/voice/interactions`
Gửi dữ liệu âm thanh hoặc transcript văn bản từ ứng dụng máy khách để nhận diện, phân tích ngữ nghĩa và điều phối thực thi nghiệp vụ.

- **Tiêu đề (Headers):**
  - `Authorization: Bearer <token>` (Bắt buộc)
  - `Idempotency-Key: <uuid-string>` (Bắt buộc để khử trùng lặp)
  - `Content-Type: application/json`

- **Nội dung yêu cầu (Request Body JSON):**
```json
{
  "patient_id": "patient_001",
  "session_id": "vses_a1b2c3d4e5f6",
  "transcript": "Tôi đã uống thuốc rồi",
  "audio_base64": null,
  "client_timestamp_utc": "2026-10-09T07:15:00.000Z",
  "context": {
    "time_of_day": "morning",
    "active_tab": "today_todo"
  }
}
```

- **Phản hồi thành công (HTTP 200 OK / 201 Created):**
```json
{
  "interaction_id": "vint_9876543210ab",
  "session_id": "vses_a1b2c3d4e5f6",
  "patient_id": "patient_001",
  "timestamp_utc": "2026-10-09T07:15:00.450Z",
  "transcript_redacted": "Tôi đã uống thuốc rồi",
  "safety_signal": {
    "is_urgent_assistance": false,
    "is_red_flag_health": false,
    "has_negation": false
  },
  "overall_status": "COMPLETED",
  "speech_response": "Dạ con đã ghi nhận cụ đã uống liều thuốc Amlodipine 5mg buổi sáng rồi ạ.",
  "clarification_question": null,
  "results": [
    {
      "intent_id": "itnt_11223344",
      "intent_type": "MEDICATION_CONFIRM",
      "status": "COMPLETED",
      "priority": "P3",
      "aggregate_id": "occ_001_morning",
      "aggregate_type": "dose_occurrence",
      "client_action": null,
      "message_to_elder": "Đã ghi nhận uống thuốc Amlodipine"
    }
  ]
}
```

- **Phản hồi khi cần làm rõ (HTTP 200 OK với trạng thái `NEEDS_CLARIFICATION`):**
```json
{
  "interaction_id": "vint_9876543211cd",
  "session_id": "vses_a1b2c3d4e5f6",
  "patient_id": "patient_001",
  "transcript_redacted": "Tôi đã uống thuốc",
  "overall_status": "NEEDS_CLARIFICATION",
  "speech_response": "Dạ buổi sáng cụ có 2 loại thuốc là Huyết áp và Tiểu đường. Cụ vừa uống loại nào ạ?",
  "clarification_question": "Cụ vừa uống thuốc Huyết áp hay thuốc Tiểu đường ạ?",
  "candidate_options": [
    {"occurrence_id": "occ_001", "name": "Thuốc Huyết áp (Amlodipine)"},
    {"occurrence_id": "occ_002", "name": "Thuốc Tiểu đường (Metformin)"}
  ],
  "results": [
    {
      "intent_id": "itnt_11223345",
      "intent_type": "MEDICATION_CONFIRM",
      "status": "NEEDS_CLARIFICATION",
      "priority": "P3"
    }
  ]
}
```

### 1.2. `GET /api/v1/voice/interactions/{interaction_id}`
Truy vấn trạng thái, lịch sử thực thi và nhật ký kiểm toán của một lượt tương tác giọng nói cụ thể.

- **Phản hồi thành công (HTTP 200 OK):**
```json
{
  "interaction_id": "vint_9876543210ab",
  "patient_id": "patient_001",
  "session_id": "vses_a1b2c3d4e5f6",
  "created_at_utc": "2026-10-09T07:15:00.000Z",
  "transcript_redacted": "Tôi đã uống thuốc rồi",
  "status": "COMPLETED",
  "intents_count": 1,
  "execution_results": [
    {
      "intent_type": "MEDICATION_CONFIRM",
      "status": "COMPLETED",
      "target_aggregate": "dose_occurrence:occ_001_morning",
      "outbox_event_id": "evt_abc12345"
    }
  ]
}
```

### 1.3. `POST /api/v1/voice/interactions/{interaction_id}/confirm`
Xác nhận hành động đang chờ (`AWAITING_CONFIRMATION`) với mã token hành động được cấp quyền.

- **Yêu cầu (Request Body JSON):**
```json
{
  "action_token": "act_tok_fe1289ab",
  "selected_option_id": "occ_001_morning"
}
```

### 1.4. `POST /api/v1/voice/interactions/{interaction_id}/cancel`
Hủy bỏ một hành động đang chờ xác nhận mà chưa cam kết vào CSDL.

- **Yêu cầu (Request Body JSON):**
```json
{
  "reason": "Người dùng đổi ý"
}
```

### 1.5. `GET /api/v1/voice/sessions/{session_id}`
Lấy trạng thái phiên hội thoại hiện tại, bao gồm các lượt hỏi đáp và danh sách câu hỏi làm rõ đang chờ.

---

## 2. Mã Lỗi Chuẩn Hóa của Voice AI (Standard Error Codes)

| Mã lỗi (`error_code`) | Mã HTTP | Mô tả nguyên nhân | Hành vi máy khách / Phản hồi người già |
|---|:---:|---|---|
| `ASR_UNAVAILABLE` | 503 | Bộ nhận dạng giọng nói ASR bị lỗi hoặc không khởi tạo được. | Hiển thị thông báo: "Không thể nhận giọng nói lúc này. Cụ vui lòng chạm vào nút trên màn hình nhé." |
| `SEMANTIC_TIMEOUT` | 504 | Google Gemini API phản hồi vượt quá 8 giây. | Kích hoạt Fast-path an toàn; hỏi lại ngắn gọn hoặc chuyển sang giao diện nút bấm. |
| `INVALID_SEMANTIC_OUTPUT` | 422 | LLM trả về cấu trúc JSON sai schema hoặc inject mã độc. | Từ chối thực thi; chuyển intent về `UNKNOWN`, yêu cầu làm rõ một câu lịch sự. |
| `CLARIFICATION_REQUIRED` | 200 | Ý định bị mập mờ, có nhiều hơn 1 liều thuốc trùng khớp. | Phát câu hỏi làm rõ qua âm thanh/chữ viết; không ghi DB. |
| `CONFIRMATION_REQUIRED` | 200 | Thao tác cần xác nhận lại từ người già. | Hiển thị nút xác nhận to rõ trên giao diện. |
| `UNAUTHORIZED` | 403 | Tài khoản phiên không có quyền thao tác trên hồ sơ bệnh nhân. | Chặn đứng hành động; ghi nhận cảnh báo bảo mật. |
| `WORKFLOW_CONFLICT` | 409 | Liều thuốc đã được xác nhận trước đó hoặc đơn thuốc bị hủy. | Thông báo: "Liều thuốc này đã được ghi nhận trước đó rồi cụ nhé." |
| `RATE_LIMIT_EXCEEDED` | 429 | Gửi lệnh giọng nói quá tần suất cho phép (chống spam). | Báo bận tạm thời trong 5 giây. |

---

## 3. Hợp Đồng Giao Diện Nội Bộ (Internal Component Interfaces)

```python
# 1. ASR Provider Interface
class ASRProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, language: str = "vi") -> TranscriptResult:
        """Transcribe raw audio PCM to text transcript."""
        pass

# 2. Semantic Provider Interface
class SemanticProvider(ABC):
    @abstractmethod
    def analyze(self, transcript: str, sanitized_context: Optional[Dict[str, Any]] = None) -> SemanticResult:
        """Interpret transcript into validated structured intents and entities."""
        pass

# 3. Safety Detector Interface
class SafetyDetector(ABC):
    @abstractmethod
    def analyze(self, transcript: str) -> SafetySignal:
        """Deterministic regex-based safety and red-flag triage running in < 5ms."""
        pass

# 4. Workflow Orchestrator Interface
class WorkflowOrchestrator(ABC):
    @abstractmethod
    def dispatch(
        self,
        patient_id: str,
        semantic_result: SemanticResult,
        safety_signal: SafetySignal,
        idempotency_key: str,
    ) -> OrchestratorExecutionResult:
        """Resolve context, schedule priorities, execute domain handlers, and commit outbox."""
        pass

# 5. Domain Handler Interface
class DomainHandler(ABC):
    @abstractmethod
    def handle(self, patient_id: str, intent: VoiceIntent, context: Dict[str, Any]) -> IntentExecutionResult:
        """Execute business mutation using existing domain adapters."""
        pass
```

---

## 4. Hợp Đồng Sự Kiện Thời Gian Thực (Outbox & SSE Events)

Khi Voice Orchestrator thực thi các ý định có tác dụng phụ, hệ thống chèn đồng thời một sự kiện vào bảng `outbox_events` với siêu dữ liệu tối thiểu (Minimal Payload).

### 4.1. Sự kiện Yêu Cầu Bác Sĩ Trợ Giúp (`assistance.requested`)
- **Tên sự kiện:** `assistance.requested`
- **Thực thể gốc (`aggregate_type`):** `assistance_request`
- **Nguồn phát (`source`):** `voice_fast_path` hoặc `voice_orchestrator`
- **Payload tối thiểu:**
```json
{
  "request_id": "asst_998877",
  "patient_id": "patient_001",
  "urgency": "HIGH",
  "reason": "Cụ yêu cầu gặp bác sĩ qua giọng nói",
  "occurred_at": "2026-10-09T07:15:00Z",
  "assigned_clinician_id": "clinician_001",
  "status": "PENDING_ACK"
}
```
- **Hành vi trên Cổng Bác Sĩ & Người Nhà:** Hiển thị Banner đỏ khẩn cấp tức thì. Bác sĩ bấm "Tiếp nhận" gửi `POST /api/patients/{id}/alerts/{id}/acknowledge`.

### 4.2. Sự kiện Xác Nhận Uống Thuốc Giọng Nói (`medication.dose_changed`)
- **Tên sự kiện:** `medication.dose_changed`
- **Thực thể gốc:** `dose_occurrence`
- **Nguồn phát:** `voice_orchestrator`
- **Payload tối thiểu:**
```json
{
  "occurrence_id": "occ_001_morning",
  "patient_id": "patient_001",
  "state": "CONFIRMED",
  "action": "self_reported_taken",
  "source": "voice_user_declared",
  "client_occurred_at": "2026-10-09T07:15:00Z"
}
```
- **Hành vi:** Web Bác sĩ, Web Người nhà và App Người già refetch thẻ thuốc; trạng thái chuyển sang "✅ Đã uống (Tự khai báo qua giọng nói)".

### 4.3. Sự kiện Ghi Nhận Triệu Chứng Sức Khỏe (`health.observation_created`)
- **Tên sự kiện:** `health.observation_created`
- **Thực thể gốc:** `symptom_entry` hoặc `measurement_group`
- **Payload tối thiểu:**
```json
{
  "symptom_id": "symp_334455",
  "patient_id": "patient_001",
  "symptoms": ["chóng mặt"],
  "onset": "từ sáng",
  "source": "voice_patient"
}
```


# Validation thực chạy — 10/10/2026

## Kết quả

- Lệnh regression trong HANDOFF đã chạy: **337 passed, 1 warning**, 6,44 giây. Gồm 193 ca local và 144 ca hồi quy STT/transcript-intent/sync/thuốc hiện có. Warning là DeprecationWarning của SDK Gemini trong test backend opt-in cũ; không phải lỗi local routing. Log: `reports/local_rules/tests.txt`.
- Golden: **138/138** câu tổng hợp đạt intents, recipient roles, confirmation và context/match level. Ban đầu có 120 câu, bổ sung 18 ca ghép/STT để kiểm tra ưu tiên người nhận khi khó chịu sau thuốc/khi tập và stop trước urgent.
- Parser đo 30 vòng x 138 câu = **4140 lượt**, chỉ parse, không STT/mạng/DB. Kết quả không phải độ chính xác STT hoặc tỷ lệ hiểu câu nói ngoài thực địa.

| Nhóm | Golden đạt | Lượt đo | p50 ms | p95 ms |
|---|---:|---:|---:|---:|
| intent | 60/60 | 1800 | 0.0229 | 0.0434 |
| scope | 30/30 | 900 | 0.0077 | 0.0264 |
| context | 15/15 | 450 | 0.0153 | 0.0267 |
| compound | 15/15 | 450 | 0.0171 | 0.0323 |
| multi_stt | 18/18 | 540 | 0.0239 | 0.0518 |

Tổng: p50 **0.0195 ms**, p95 **0.0362 ms**, max **0.1563 ms**. Dưới mục tiêu 100 ms trên máy kiểm thử này. Môi trường: Linux-7.0.0-38-generic-x86_64-with-glibc2.43, Python 3.14.4. Chi tiết CPU và thư viện: `reports/local_rules/environment.txt`. Artefact `reports/local_rules/benchmark.json`; có thể chạy lại `scripts/benchmark_local_rules.py` trên máy demo để lấy kết quả riêng.

- STT model hiện có nạp offline thành công trong **0,853 giây**, model multilingual CPU. Synthetic silence 1 giây trả completed, transcript rỗng. `reports/local_rules/stt-loader-smoke.txt`. Không chạy nhận dạng lời nói thật; inference_ms=0 ở silence không phải độ trễ nhận giọng nói thực.
- Qt responsiveness: timer vẫn chạy khi fake transport cố ý sleep; pause thực hiện khi worker nền còn bận. Integration dùng DB SQLite thật trong thư mục tạm.
- Full dashboard smoke: **đạt với hardware/adapters giả**, fake final transcript → preview → click Xác nhận → request/delivery thật trong DB tạm → fake SMTP_ACCEPTED → UI phản hồi đúng → đóng STT process. Artefact `ui-smoke.txt`, `ui-smoke.png` và script tái lập. Không truy cập camera/microphone/SMTP thật.
- JavaScript hai portal đã chạy `node --check`; Python phần thay đổi đã compileall; diff-check giới hạn file đã sửa, có xử lý CRLF. Không chạy diff-check toàn workspace như một tiêu chí đạt vì repository có nhiều thay đổi CRLF trước tác vụ.

## Ma trận bắt buộc: kết quả trong môi trường giả

Tất cả 32 tình huống bên dưới đã có kiểm thử thực chạy. “Đạt” ở đây là logic/service/DB/fake delivery, không phải nghiệm thu hardware hay liên lạc người thật.

| # | Tình huống | Test/dataset | Kết quả |
|---:|---|---|---|
| 1 | Gọi bác sĩ, chờ xác nhận | `test_notification_requires_real_approval` | Đạt |
| 2 | Gọi con, đúng hồ sơ | cùng test + `test_voice_snapshot_requires_real_identity_mapping` | Đạt |
| 3 | Lấy nước tới người nhà | `test_notification_requires_real_approval` | Đạt |
| 4 | Đã uống + một lượt hợp lệ | `test_taken_only_after_approval_exact_occurrence` | Đạt, còn cần approval theo yêu cầu người dùng |
| 5 | Đã uống ngoài context | `test_no_dose_multiple_doses_expired_context_no_mutation` | Đạt |
| 6 | Chưa uống không đánh dấu đã uống | `test_not_taken_preserves_state_and_records_response` | Đạt |
| 7 | Nhắc lại với context | `test_snooze_existing_policy_and_cap`, `test_spoken_ten_minutes_only_changes_occurrence` | Đạt |
| 8 | Nhắc lại không context | golden nhóm context | Đạt |
| 9 | Dừng khi đang tập | `test_stop_then_contact_and_no_camera_completion` | Đạt |
| 10 | Xong rồi không thay camera completion | cùng test + regression `test_transcript_cannot_complete_rehabilitation` | Đạt |
| 11 | Không đau, gọi con | golden scope | Đạt |
| 12 | Không đau nhưng chóng mặt | golden scope | Đạt |
| 13 | Đừng gọi con, gọi bác sĩ | golden scope | Đạt |
| 14 | Không, tôi cần bác sĩ | `test_negation_replacement_and_explicit_recipient` | Đạt |
| 15 | Hôm qua ngã, giờ ổn | golden scope + desktop ambiguous test | Đạt |
| 16 | Nếu không thở được thì sao | cùng nhóm + desktop ambiguous test | Đạt |
| 17 | Con tôi nói cứu tôi | cùng nhóm + desktop ambiguous test | Đạt |
| 18 | Không thở được hiện tại | `test_final_duplicate_and_urgent_no_confirmation` + golden | Đạt |
| 19 | Dừng tập rồi gọi con | `test_stop_then_contact_and_no_camera_completion` | Đạt |
| 20 | Final phát lặp | `test_final_duplicate_and_urgent_no_confirmation` | Đạt |
| 21 | Partial cứu tôi | `test_partial_never_executes` | Đạt |
| 22 | Hai role một recipient | `test_same_recipient_two_roles` | Đạt |
| 23 | Đổi patient khi pending | `test_cancel_timeout_patient_change_no_mutation` | Đạt |
| 24 | Hủy trước gửi | `test_cancel_before_send_and_correction_after`, desktop pending cancel | Đạt |
| 25 | Báo nhầm sau gửi | cùng test + `test_offline_real_queue_and_false_alarm` | Đạt, giữ sent audit và SSE đính chính |
| 26 | Offline/reconnect | `test_offline_restart_reconnect`, desktop queue test | Đạt |
| 27 | Restart queued | `test_offline_restart_reconnect`, `test_interrupted_claim_never_resent` | Đạt; claim không rõ không resend |
| 28 | Một recipient lỗi | `test_partial_failure_retry_only_failed` | Đạt |
| 29 | Thiếu doctor/caregiver | `test_no_identity_mapping_or_stale_recipient`, `test_partial_configuration_urgent_uses_only_known_recipient` | Đạt |
| 30 | Unknown patient không dùng default | `test_unknown_identity_never_uses_default_profile`, snapshot mapping test | Đạt |
| 31 | Timeout không auto-confirm | `test_cancel_timeout_patient_change_no_mutation`, dialogue expiry test | Đạt |
| 32 | Ngoài phạm vi không mutation | `test_ambiguous_two_turns_and_unknown_no_mutation` + golden | Đạt |

Các ca bổ sung: preview không bị idle/retry nền che mất, voice confirmation không làm mất nội dung Gửi lại chủ động, cụm urgent chỉ xuất hiện trong câu hỏi/từ được nhắc tới không tự gửi; giả định/người thứ ba/đọc câu, không chắc chắn, xung đột, bác sỹ alias, text không dấu không kích hoạt urgent, ưu tiên recipient khi khó chịu trong rehab/sau thuốc, dừng tập trước urgent, thuốc + gọi con sau approval, backoff/cap retry bền vững, hết hạn request, revoked mapping, transcript retention, API/SSE quyền đọc và acknowledgement thật.

## Phần chưa được nghiệm thu thực địa

Không có người tham gia/mẫu lời nói thật được cấp phép trong tác vụ; native audio import đã bị treo trong môi trường, ghi đúng là bị chặn rồi dùng fake audio module cho GUI smoke. Chưa đo STT tiếng Việt qua micro, tỷ lệ lỗi STT/parser trên người thật, camera thật/camera completion thực, mạng/SMTP thật, browser thao tác trực tiếp, Windows packaging/deploy hoặc mức nhận/thực hiện của bác sĩ/người nhà thật. Không gửi test tới người thật.

Không thể đảm bảo exactly-once SMTP qua crash ở biên nộp thư; unknown được giữ và không retry tự động. Thời gian nhận của người thật không được suy từ SMTP_ACCEPTED. Không có device-level urgent mapping cho hồ sơ chưa nhận diện. Chưa có roster doctor theo user_id nên chỉ route khi một doctor assigned hợp lệ được xác định; manual phone dùng lịch trực đã cấu hình. Các giới hạn này không bị đánh dấu là đã hoàn thành trong thực địa.

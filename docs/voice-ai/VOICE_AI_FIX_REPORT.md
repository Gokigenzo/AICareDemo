# Voice AI Reliability and Bug Fix Report

**Date:** 2026-10-09  
**Role:** Senior AI Engineer — Voice AI Debugging & Reliability  
**Target Architecture:** Faster Whisper + Gemini Flash API + Workflow Orchestrator  
**Status:** All 6 Observed Symptoms Diagnosed, Fixed, and Verified (89/89 Automated Tests Passing)

---

## 1. Executive Summary

This report documents the end-to-end diagnosis, surgical fixes, and automated test verification for the 6 critical Voice AI symptoms reported in runtime logs:
1. The assistant repeatedly said: *"Dạ cụ vừa uống thuốc nào ạ?"*
2. Medication names appeared as repeated generic values: *"Thuốc, Thuốc, Thuốc..."*
3. `AudioCapture` repeatedly started and stopped recording in rapid bursts.
4. Recordings shorter than 0.3 seconds were discarded.
5. Runtime logs lacked structured tracing for ASR transcripts, semantic intents, or workflow latencies.
6. TTS-to-microphone acoustic feedback loops, conversation state wiping across turns, and missing idempotency keys in UI.

All fixes were implemented using minimal, targeted modifications preserving backward compatibility with PyQt5 desktop widgets, SQLite unified storage, and realtime outbox synchronizers.

---

## 2. Phase-by-Phase Fix Breakdown

### Phase 0 — Investigation & Root Cause Diagnostics
- **Confirmed Issues:**
  1. In `services/voice_ai/business_adapters/medication_adapter.py`: `med_names = [m["medication_name_snapshot"] for m in matching]` collected un-deduplicated snapshots across all scheduled hours today, generating `"Thuốc, Thuốc, Thuốc"`.
  2. In `medication_adapter.py`: `if not matching: matching = rows` silently fell back to all rows when an unknown drug name was spoken, arbitrarily confirming an unrelated medication dose!
  3. In `services/voice_ai/orchestrator/router.py`: `session.dispatch_completed()` was called unconditionally, erasing `pending_intent` and `SessionState.AWAITING_CLARIFICATION`, causing turn amnesia.
  4. In `app/voice_button_widget.py`: Spacebar OS auto-repeat fired alternating `pressed`/`released` events every ~40ms, causing rapid start/stop toggling and <0.3s audio buffer discards.
  5. In `archive/voice/tts_utils.py`: `pyttsx3` was launched via unmanaged subprocesses without lifecycle tracking, allowing speaker audio to leak back into the microphone.
- **Deliverable:** Created `docs/voice-ai/ROOT_CAUSE_ANALYSIS.md`.

---

### Phase 1 — Observability
- **Confirmed Issue:** Runtime logs lacked end-to-end correlation, latencies, and stage timings.
- **Files Changed / Created:**
  - `services/voice_ai/observability/__init__.py`
  - `services/voice_ai/observability/tracer.py`
  - `services/voice_ai/orchestrator/router.py`
- **Technical Solution:**
  - Implemented `VoiceTraceContext` tracking unique interaction IDs (`vint_*`), session IDs (`vses_*`), per-stage latencies (`audio_capture`, `asr`, `safety_triage`, `semantic_analysis`, `workflow_execution`), and overall status.
  - Enforced strict PII and secret masking: `mask_patient_id` (e.g. `pa***01`), `mask_transcript_preview` (truncating text, masking phone numbers), and `mask_secret` (redacting `AIzaSy*`, tokens, and API keys).
  - Attached `trace_summary` to `OrchestratorExecutionResult`.
- **Tests Executed:** `test_structured_observability_tracing_emits_masked_fields`.
- **Results:** Structured `[VOICE_TRACE]` JSON entries logged with zero secret leakage.

---

### Phase 2 — Audio Lifecycle & Feedback Prevention
- **Confirmed Issue:** Spacebar auto-repeat bounce flooded `AudioRecorder`; unmanaged TTS playback triggered acoustic feedback loops.
- **Files Changed / Created:**
  - `services/voice_ai/audio/tts_player.py` (Created `TTSPlaybackCoordinator`)
  - `archive/voice/tts_utils.py` (Delegated to `TTSPlaybackCoordinator`)
  - `services/voice_ai/audio/capture.py` (Added debounce & barge-in)
  - `app/voice_button_widget.py` (Added Qt event filter)
- **Technical Solution:**
  - Installed an event filter on `VoiceButtonWidget.btn_ptt` intercepting `QEvent.KeyPress` and `QEvent.KeyRelease` to suppress `event.isAutoRepeat()`.
  - Added a 150ms debounce window in `AudioRecorder.start_recording()` preventing chatter bounce.
  - Implemented Barge-In Interruptibility: `AudioRecorder.start_recording()` terminates any active TTS playback via `get_tts_coordinator().stop()`, cutting off speaker audio before mic capture begins.
  - Maintained the minimum duration threshold at 0.3s without arbitrary increases.
- **Tests Executed:**
  - `test_spacebar_auto_repeat_suppressed_in_voice_button`
  - `test_audio_recorder_debounce_protection`
  - `test_tts_barge_in_stops_playback_on_recording_start`
- **Results:** Spacebar holding produces exactly one recording session; starting recording terminates assistant speech immediately.

---

### Phase 3 — Semantic & Conversation State
- **Confirmed Issue:** Stale clarification state wiped out across turns; inability to supersede pending clarification with urgent or new commands.
- **Files Changed:**
  - `services/voice_ai/orchestrator/state_machine.py`
  - `services/voice_ai/orchestrator/router.py`
- **Technical Solution:**
  - Updated `VoiceSessionStateMachine.start_processing()` to preserve `AWAITING_CLARIFICATION` state during active clarifications.
  - In `router.py`:
    - **Urgent Supersede:** Any high-urgency phrase or red-flag symptom immediately cancels pending clarifications and routes to `DOCTOR_ASSISTANCE` fast-path (<5ms).
    - **Topic Supersede:** An unrelated command (entertainment, media, game) cancels the pending clarification and executes the new intent.
    - **Entity Disambiguation:** When elder answers with a drug name or scheduled time, the pending intent is resolved and executed.
    - **Turn Expiry:** If elder provides 2 consecutive unclear turns, the session gracefully resets to `IDLE` with a polite closure: *"Dạ con xin phép tạm gác lại câu hỏi xác nhận thuốc. Khi nào cụ cần xác nhận thuốc, cụ cứ bảo con nhé."*, definitively halting the prompt loop.
    - `dispatch_completed()` is only called when `overall_status == ExecutionStatus.COMPLETED`, keeping state intact during `NEEDS_CLARIFICATION`.
- **Tests Executed:**
  - `test_conversation_state_clarification_superseded_by_urgent`
  - `test_conversation_state_clarification_superseded_by_unrelated_intent`
  - `test_conversation_state_turn_limit_prevents_infinite_clarification_loop`
  - `test_gemini_malformed_response_graceful_fallback`
- **Results:** State transitions are deterministic; urgent assistance is never blocked.

---

### Phase 4 — Medication Workflow Fixes
- **Confirmed Issue:** Duplicate generic names in prompts; dangerous fallback confirming random prescriptions on `NO_MATCH`.
- **Files Changed:**
  - `services/voice_ai/business_adapters/medication_adapter.py`
  - `app/today_todo_widget.py`
- **Technical Solution:**
  - In `MedicationAdapter.handle_confirmation()`:
    - If `med_ref` does not match scheduled doses, it returns `NO_MATCH` with available scheduled times, never falling back to all unconfirmed rows!
    - When multiple doses exist, options are deduplicated and contextualized with scheduled times: e.g. `"Thuốc (cữ 08:00), Thuốc (cữ 12:00)"`, completely eliminating `"Thuốc, Thuốc, Thuốc"`.
    - Single matching doses include scheduled times in confirmation speech: *"Con đã ghi nhận cụ đã uống Thuốc (cữ 08:00) ạ."*
  - In `app/today_todo_widget.py`: Generated request-scoped idempotency keys (`ui_ptt_<patient>_<hash>_<bucket>`) preventing duplicate DB submissions on double-clicks.
- **Tests Executed:**
  - `test_medication_generic_names_deduplicated_and_timed`
  - `test_medication_non_matching_name_does_not_confirm_random_dose`
  - `test_idempotency_prevents_duplicate_medication_intake`
- **Results:** Zero fabricated confirmations; duplicate doses clearly distinguished by time.

---

## 3. Before vs. After Behavior Matrix

| Observed Symptom | Before Fix | After Fix |
|---|---|---|
| **Clarification Loop** | Assistant repeatedly asked *"Dạ cụ vừa uống thuốc nào ạ?"* after every turn. | Clarification expires gracefully after 2 turns or is immediately superseded by new utterances. |
| **Generic Drug Names** | Prompt said: *"Cụ có lịch uống: Thuốc, Thuốc, Thuốc."* | Prompt says: *"Cụ có lịch uống: Thuốc (cữ 08:00), Thuốc (cữ 12:00)."* |
| **Non-Matching Medication** | Speaking "Panadol" confirmed the patient's Blood Pressure medication! | Returns `NO_MATCH` and explains available scheduled doses without modifying DB. |
| **Spacebar PTT Bounce** | Holding Spacebar caused 10-20 start/stop recordings per second (<0.3s discards). | Event filter suppresses auto-repeat; single continuous recording session until physical release. |
| **Microphone / TTS Overlap** | Assistant voice played into microphone, creating self-triggering feedback loop. | Barge-in cancels active TTS the instant recording begins; no audio overlap. |
| **Observability** | No interaction IDs, no latency metrics, and no ASR/intent logging. | Structured `[VOICE_TRACE]` JSON with masked PII, latencies, and stage status. |
| **Idempotency in GUI** | Rapid clicks re-submitted duplicate business events. | Request-scoped idempotency key deduplicates actions within 2-second buckets. |

---

## 4. Test Evidence & Regression Checklist

### Automated Test Suite Execution:
- **Total Tests Executed:** 89
- **Passed:** 89
- **Failed:** 0
- **Execution Time:** 3.23s
- **Command:** `PYTHONPATH=. QT_QPA_PLATFORM=offscreen .venv-linux/bin/pytest tests/voice_ai/ -v`

### Regression Verification:
- [x] Fast-path urgent doctor assistance triage (<5ms) intact.
- [x] Negation protection prevents false medication confirmations.
- [x] Entertainment actions (`game.open`, `media.play`) functional and allowlisted.
- [x] Atomic outbox event emission (`medication.dose_changed`, `assistance.requested`) intact.
- [x] Unified database schema and migration constraints fully satisfied.
- [x] Desktop UI mounting and event loop stability verified.

---

## 5. Remaining Risks & Operational Guidance

1. **Hardware Microphone Drivers:** In physical kiosk setups with extremely sensitive microphones and close speakers, ensure acoustic echo cancellation (AEC) is enabled in the OS audio server (PulseAudio/PipeWire) in addition to software barge-in.
2. **Offline Headless Environments:** When neither `faster-whisper` nor physical audio devices are present, the system cleanly defaults to software simulation and `MockASRProvider`. For production deployments, ensure `faster-whisper` and `GEMINI_API_KEY` are provisioned in `.env`.


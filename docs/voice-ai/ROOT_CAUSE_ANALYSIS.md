# Root Cause Analysis: Voice AI Pipeline Diagnostics & Reliability

**Date:** 2026-10-09  
**Role:** Senior AI Engineer — Voice AI Debugging & Reliability  
**Target Architecture:** Faster Whisper + Gemini Flash API + Workflow Orchestrator  
**Applicable Application:** Senior Care Assistant (Desktop & Outbox Realtime Sync)

---

## 1. Executive Summary

This investigation diagnoses the root causes of six runtime symptoms observed in the Voice AI pipeline:
1. The assistant repeatedly asks: *"Dạ cụ vừa uống thuốc nào ạ?"*
2. Medication names appear as repeated generic values: *"Thuốc, Thuốc, Thuốc..."*
3. `AudioCapture` repeatedly starts and stops recording in rapid bursts.
4. Recordings shorter than 0.3 seconds are discarded.
5. Runtime logs lack structured ASR transcripts, semantic intents, or workflow execution tracking.
6. Acoustic feedback (TTS to microphone), state loss across turns, and lack of idempotency keys in UI invocations.

This document separates **Confirmed Causes (with exact file and line references)** from **Initial Hypotheses**.

---

## 2. Complete Audio-to-Workflow Execution Trace

The system execution flow proceeds through the following components:

```
[User Speech / Spacebar PTT]
         │
         ▼
[app/voice_button_widget.py]
  ├── btn_ptt (QPushButton) ───► Mouse Press / Key Press (Space)
  └── TranscriptionWorker (QThread)
         │
         ▼
[services/voice_ai/audio/capture.py: AudioRecorder]
  ├── Captures 16 kHz mono 16-bit PCM in memory
  └── Enforces 0.3s min bound and 20.0s max bound
         │ (WAV bytes)
         ▼
[services/voice_ai/asr/factory.py & provider.py]
  ├── FasterWhisperASR (or MockASR fallback if package/model missing)
  └── Emits TranscriptResult(transcript, confidence, language="vi")
         │
         ▼
[app/today_todo_widget.py: _on_voice_transcript_ready]
         │
         ▼
[services/voice_ai/orchestrator/router.py: WorkflowOrchestrator]
  ├── 1. Idempotency Check (IdempotencyManager)
  ├── 2. Auth Context & Identity Verification
  ├── 3. Deterministic Safety Triage (<5ms Fast-Path LLM Bypass)
  ├── 4. Operational Context Resolution (ContextResolver)
  ├── 5. Semantic Parsing (GeminiSemanticProvider / MockSemanticProvider)
  ├── 6. Priority Scheduling (P1 Assistance > P2 Health > P3 Med > P4 Entertainment)
  ├── 7. Business Adapters (Assistance, Medication, Health, Media/Games)
  │      └── MedicationAdapter.handle_confirmation (dose_occurrences & dose_events)
  └── 8. Vietnamese TTS Response Synthesis & Client Action Dispatch
         │
         ▼
[archive/voice/tts_utils.py: speak()]
  └── Subprocess spawn pyttsx3 speaking through device speakers
```

---

## 3. Confirmed Root Causes vs. Hypotheses

### Symptom 1 & 2: Repeated Medication Clarification Prompt & Generic Names ("Thuốc, Thuốc, Thuốc...")

- **Status:** **CONFIRMED ROOT CAUSE**
- **Exact Code References:**
  - `services/voice_ai/business_adapters/medication_adapter.py` (lines 72–96)
  - `services/voice_ai/orchestrator/router.py` (line 283)
  - `services/voice_ai/orchestrator/state_machine.py` (lines 134–146)

#### Mechanism of Failure:
1. **Un-deduplicated Medication Snapshots:**
   In `services/voice_ai/business_adapters/medication_adapter.py`:
   ```python
   # Line 88:
   med_names = [m["medication_name_snapshot"] for m in matching]
   # Line 93:
   clarification_prompt = f"Dạ cụ vừa uống thuốc nào ạ? Cụ có lịch uống: {', '.join(med_names)}."
   ```
   When a prescription schedule contains multiple dose times (e.g., 08:00 Morning, 12:00 Noon, 18:00 Evening) where `medication_name_snapshot` is generic `"Thuốc"` or the same drug name, the list comprehension collects all rows without deduplication or schedule-time contextualization (`08:00`, `12:00`, `18:00`). This generates the exact phrase:
   `"Dạ cụ vừa uống thuốc nào ạ? Cụ có lịch uống: Thuốc, Thuốc, Thuốc."`

2. **Dangerous Fallback on Non-Matching Drug Name:**
   In `medication_adapter.py` lines 73–77:
   ```python
   matching = []
   if med_ref:
       matching = [r for r in rows if med_ref in r["medication_name_snapshot"].lower()]
   if not matching:
       matching = rows  # BUG: Silently falls back to all unconfirmed rows!
   ```
   If the elder names a medication not in the database (or mispronounced), `matching` falls back to *all unconfirmed doses*. Because `med_ref` was truthy, it bypasses the `if len(matching) > 1 and not med_ref` check and automatically selects `matching[0]`, confirming an arbitrary dose without matching verification!

3. **Session State Wiped Out on Clarification:**
   In `services/voice_ai/orchestrator/router.py` line 283:
   ```python
   session.dispatch_completed(outcome_summary=final_speech)
   ```
   Even when an intent returns `ExecutionStatus.NEEDS_CLARIFICATION`, `router.py` unconditionally invokes `session.dispatch_completed()`, which clears `pending_intent`, `clarification_question`, and resets the state to `COMPLETED`. On the next turn, the orchestrator has lost all conversational memory of what drug was being disambiguated.

---

### Symptom 3 & 4: AudioCapture Rapid Start/Stop & Discarding Recordings <0.3s

- **Status:** **CONFIRMED ROOT CAUSE**
- **Exact Code References:**
  - `app/voice_button_widget.py` (lines 89–90)
  - `services/voice_ai/audio/capture.py` (lines 142–145)

#### Mechanism of Failure:
1. **Spacebar Keyboard Auto-Repeat Bounce:**
   In `app/voice_button_widget.py`:
   ```python
   self.btn_ptt.pressed.connect(self._on_ptt_pressed)
   self.btn_ptt.released.connect(self._on_ptt_released)
   ```
   In Qt / X11 / Wayland, holding down the Spacebar sends OS-level keyboard auto-repeat events every 30–60ms. Standard `QPushButton` fires `pressed` on `KeyPress` and `released` on `KeyRelease` for each repeat event when `event.isAutoRepeat() == True`.
2. **Buffer Empty & Short Duration Discard:**
   Because `pressed` and `released` alternate every ~40ms, `recorder.start_recording()` and `recorder.stop_recording()` are called in rapid succession. In `capture.py`:
   ```python
   if duration < self.config.min_duration_seconds and len(self._pcm_buffer) == 0:
       logger.info("Recording too short (%.2fs < %.2fs), discarded.", duration, self.config.min_duration_seconds)
       return None
   ```
   Duration is 0.04s (< 0.3s) and buffer has 0 bytes. The audio is discarded, and 10ms later the next auto-repeat keypress triggers `start_recording` again, flooding the logs with rapid toggles.

---

### Symptom 5: Missing Observability (No Traces of ASR, Intents, or Latencies)

- **Status:** **CONFIRMED ROOT CAUSE**
- **Exact Code References:**
  - `app/voice_button_widget.py` (lines 186–202)
  - `app/today_todo_widget.py` (lines 234–286)
  - `services/voice_ai/orchestrator/router.py` (lines 110–290)

#### Mechanism of Failure:
1. `VoiceButtonWidget` and `today_todo_widget.py` logged only raw UI messages or unhandled exceptions.
2. In `router.py`, `interaction_id` was generated but never attached to structured logging contexts.
3. No timing breakdown (capture duration, ASR latency, LLM roundtrip latency, adapter execution latency) was captured or logged.
4. Production logs did not format interaction traces as structured JSON or searchable key-value tokens.

---

### Symptom 6: TTS-to-Microphone Acoustic Feedback & Stale Conversation State

- **Status:** **CONFIRMED ROOT CAUSE**
- **Exact Code References:**
  - `archive/voice/tts_utils.py` (lines 15–51)
  - `app/voice_button_widget.py` (lines 154–180)
  - `app/today_todo_widget.py` (lines 253–257)

#### Mechanism of Failure:
1. **Acoustic Feedback Loop:**
   `speak()` executes `subprocess.Popen` in the background with `pyttsx3`. There is no process tracking, no completion callback, and no coordination with `AudioRecorder`.
   When the speaker outputs *"Dạ cụ vừa uống thuốc nào ạ?..."*, if the microphone is active (or PTT is pressed while assistant is speaking), the microphone captures the speaker's audio.
   ASR transcribes *"uống thuốc"*, semantic provider classifies `MEDICATION_CONFIRM`, medication adapter asks *"Dạ cụ vừa uống thuốc nào ạ?..."*, creating an acoustic feedback loop.
2. **Missing Idempotency Key in UI:**
   In `today_todo_widget.py`, `process_voice_interaction` was called without passing an `idempotency_key`. Double-clicks or rapid PTT releases re-processed the same request.

---

## 4. Faster Whisper and Gemini Runtime State

- **Faster Whisper:**
  - In `services/voice_ai/asr/factory.py`, when `faster-whisper` is missing or model download fails, the factory logs a warning and falls back to `MockASRProvider`.
  - In current test and local environments, `MockASRProvider` returns `"tôi đã uống thuốc rồi"` by default when given simulated WAV bytes, which triggers the medication flow.
- **Gemini Flash API:**
  - In `services/voice_ai/semantic/factory.py`, if `GEMINI_API_KEY` is not present in the environment, the factory falls back to `MockSemanticProvider`.
  - `MockSemanticProvider` maps `"uống thuốc rồi"` directly to `MEDICATION_CONFIRM`.

---

## 5. Controlled Reproduction Evidence

1. **Reproduction of Generic Medication Prompt:**
   - Setup: Seeded SQLite database with 2 dose occurrences for a patient, both named `"Thuốc"`.
   - Input: Utterance `"Tôi đã uống thuốc rồi"` (no specific name).
   - Output: `clarification_prompt` returned: `"Dạ cụ vừa uống thuốc nào ạ? Cụ có lịch uống: Thuốc, Thuốc."`
   - Verified: Duplicated names rendered directly into speech.

2. **Reproduction of Spacebar Auto-Repeat:**
   - Setup: Held Spacebar on `VoiceButtonWidget.btn_ptt`.
   - Observation: 12 `start_recording` / `stop_recording` cycles in 600ms, each logging `Recording too short (< 0.3s), discarded`.

3. **Reproduction of TTS Overlap:**
   - Setup: Called `speak("Xin chào")` and immediately called `recorder.start_recording()`.
   - Observation: Audio recorder recorded simultaneously without muting or barge-in interrupt.

---

## 6. Action Plan for Fix Phases

| Phase | Component | Action Item |
|---|---|---|
| **Phase 1** | Observability | Implement structured interaction tracer (`interaction_id`, `latency_ms`, stage timings, PII masking). |
| **Phase 2** | Audio Lifecycle | Implement Spacebar auto-repeat suppression in `VoiceButtonWidget`, barge-in TTS cancellation, and recording mutex. |
| **Phase 3** | Conversation State | Fix state transitions: persist `AWAITING_CLARIFICATION`, support supersede on new topic, turn-count expiry. |
| **Phase 4** | Medication Workflow | Deduplicate medication snapshots, format scheduled times (`08:00`), fix `NO_MATCH` fallback logic. |
| **Phase 5** | Automated Tests | Add unit and integration tests covering all 6 symptoms and verify 0 regressions. |


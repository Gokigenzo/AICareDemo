"""
Root Pytest Configuration and Test Environment Isolation.
Configures headless Qt, Protobuf, and graceful audio fallback for headless test runners.
"""

from __future__ import annotations

import os
import sys
import unittest.mock

# 1. Force offscreen Qt platform for headless Linux CI / test environments
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
os.environ.setdefault("AI_CARE_TEST_MODE", "1")
os.environ["VOICE_AI_ENABLED"] = "true"

# Pre-initialize mediapipe and torch on Windows before any Qt/CV imports to prevent C-runtime DLL collision (WinError 1114)
try:
    import mediapipe
except Exception:
    pass

try:
    import torch
except Exception:
    pass

# 2. On headless Linux without PulseAudio/ALSA, sounddevice raises PortAudioError on import.
# Safely handle sounddevice so MediaPipe and Voice AI test suites can execute without crashing.
try:
    import sounddevice
except Exception:
    # PortAudio unavailable in headless environment: mock sounddevice module safely
    mock_sd = unittest.mock.MagicMock()
    mock_sd.query_devices.return_value = [
        {"name": "Mock Default Microphone", "max_input_channels": 1, "default_samplerate": 16000.0}
    ]
    mock_sd.InputStream.return_value = unittest.mock.MagicMock()
    sys.modules["sounddevice"] = mock_sd

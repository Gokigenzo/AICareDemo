"""
Adapters package for AI Rehabilitation & Safety Assistant.
Provides thin, robust wrappers for the 3 camera subsystems:
1. face_adapter (Personalization & Identity)
2. emotion_adapter (Contextual psychological state)
3. rehabilitation_adapter (Exercise kinematics & scoring)
"""

# Pre-initialize mediapipe and torch on Windows before Qt to prevent C-runtime DLL collision (WinError 1114)
try:
    import mediapipe
except Exception:
    pass

try:
    import torch
except Exception:
    pass

from .face_adapter import FaceAdapter
from .emotion_adapter import EmotionAdapter
from .rehabilitation_adapter import RehabilitationAdapter

__all__ = [
    "FaceAdapter",
    "EmotionAdapter",
    "RehabilitationAdapter",
]

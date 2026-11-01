"""Legacy mock factory for old tests; desktop uses services.local_voice.

Local model ownership belongs to VoiceSessionController's persistent process.
This factory never starts a recorder, model, cloud provider, or listener.
"""
from typing import Optional
from services.voice_ai.asr.mock_provider import MockASRProvider
from services.voice_ai.asr.provider import ASRProvider


def get_asr_provider(deployment_mode: Optional[str] = None) -> ASRProvider:
    if deployment_mode and deployment_mode.lower() in ('local', 'real'):
        raise RuntimeError('Legacy ASR pipeline removed; use services.local_voice.controller.VoiceSessionController')
    return MockASRProvider.get_instance()

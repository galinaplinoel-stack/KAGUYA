"""Tests for emotional state engine."""
import pytest
from kaguya.personality.traits import TraitVector
from kaguya.personality.profile import CharacterProfile
from kaguya.emotion.engine import EmotionalStateEngine
from kaguya.emotion.states import EmotionType


class TestEmotionalStateEngine:
    def setup_method(self):
        self.profile = CharacterProfile(
            name="Test",
            traits=TraitVector(sensitivity=0.8),
        )
        self.engine = EmotionalStateEngine(self.profile)

    def test_initial_state(self):
        state = self.engine.current_state
        assert state.primary_emotion == EmotionType.NEUTRAL
        assert state.intensity < 0.5

    def test_process_event(self):
        self.engine.process_event("received compliment", intensity=0.8)
        state = self.engine.current_state
        assert state.primary_emotion != EmotionType.NEUTRAL
        assert state.intensity > 0.0

    def test_emotion_decay(self):
        self.engine.process_event("exciting news", intensity=1.0)
        initial_intensity = self.engine.current_state.intensity
        self.engine.apply_decay()
        assert self.engine.current_state.intensity < initial_intensity

    def test_get_tone(self):
        tone = self.engine.get_tone()
        assert isinstance(tone, dict)
        assert "warmth" in tone

    def test_emotion_transitions(self):
        self.engine.process_event("happy moment", intensity=0.9)
        joy_state = self.engine.current_state
        self.engine.process_event("bad news", intensity=0.9)
        new_state = self.engine.current_state
        assert new_state.primary_emotion != joy_state.primary_emotion

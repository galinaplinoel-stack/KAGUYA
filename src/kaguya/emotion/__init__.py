"""Emotion subsystem — real-time mood simulation and emotional influence."""

from kaguya.emotion.states import EmotionType, MoodState
from kaguya.emotion.engine import EmotionalStateEngine
from kaguya.emotion.influence import EmotionInfluence

__all__ = [
    "EmotionType",
    "MoodState",
    "EmotionalStateEngine",
    "EmotionInfluence",
]

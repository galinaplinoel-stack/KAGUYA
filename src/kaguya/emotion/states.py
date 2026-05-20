"""Emotion types, mood state, and the valence-arousal model.

The valence-arousal model maps emotions onto two axes:
- Valence: negative (-1) ↔ positive (+1)  — pleasantness
- Arousal: low (0) ↔ high (1) — energy / activation
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple


class EmotionType(str, Enum):
    """Discrete emotion categories (Plutchik-inspired)."""

    joy = "joy"
    sadness = "sadness"
    anger = "anger"
    fear = "fear"
    surprise = "surprise"
    disgust = "disgust"
    trust = "trust"
    anticipation = "anticipation"


# Valence-Arousal coordinates for each emotion type
_EMOTION_VA: Dict[EmotionType, Tuple[float, float]] = {
    EmotionType.joy:          ( 0.8,  0.6),
    EmotionType.sadness:      (-0.7,  0.2),
    EmotionType.anger:        (-0.6,  0.9),
    EmotionType.fear:         (-0.7,  0.8),
    EmotionType.surprise:     ( 0.1,  0.9),
    EmotionType.disgust:      (-0.8,  0.4),
    EmotionType.trust:        ( 0.6,  0.3),
    EmotionType.anticipation: ( 0.4,  0.7),
}


@dataclass
class MoodState:
    """Snapshot of an entity's emotional state at a point in time.

    Attributes:
        primary_emotion: The dominant emotion type.
        intensity: How strong the emotion is (0.0 – 1.0).
        valence: Pleasantness axis (-1.0 to +1.0).
        arousal: Energy axis (0.0 to 1.0).
        decay_rate: How fast intensity drops per tick (0.0 – 1.0).
        timestamp: Unix timestamp of last update.
        secondary_emotion: Optional secondary emotion.
        secondary_intensity: Intensity of the secondary emotion.
    """

    primary_emotion: EmotionType = EmotionType.joy
    intensity: float = 0.5
    valence: float = 0.0
    arousal: float = 0.5
    decay_rate: float = 0.05
    timestamp: float = field(default_factory=time.time)
    secondary_emotion: Optional[EmotionType] = None
    secondary_intensity: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "primary_emotion": self.primary_emotion.value,
            "intensity": round(self.intensity, 4),
            "valence": round(self.valence, 4),
            "arousal": round(self.arousal, 4),
            "decay_rate": self.decay_rate,
            "timestamp": self.timestamp,
            "secondary_emotion": self.secondary_emotion.value if self.secondary_emotion else None,
            "secondary_intensity": round(self.secondary_intensity, 4),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "MoodState":
        return cls(
            primary_emotion=EmotionType(data["primary_emotion"]),
            intensity=data.get("intensity", 0.5),
            valence=data.get("valence", 0.0),
            arousal=data.get("arousal", 0.5),
            decay_rate=data.get("decay_rate", 0.05),
            timestamp=data.get("timestamp", time.time()),
            secondary_emotion=(
                EmotionType(data["secondary_emotion"])
                if data.get("secondary_emotion") else None
            ),
            secondary_intensity=data.get("secondary_intensity", 0.0),
        )

    @classmethod
    def neutral(cls) -> "MoodState":
        """Create a calm, neutral mood state."""
        return cls(
            primary_emotion=EmotionType.trust,
            intensity=0.2,
            valence=0.1,
            arousal=0.3,
        )


def emotion_va(emotion: EmotionType) -> Tuple[float, float]:
    """Return the valence-arousal coordinates for a given emotion."""
    return _EMOTION_VA[emotion]


def emotion_from_va(valence: float, arousal: float) -> EmotionType:
    """Find the closest emotion type for given valence/arousal coordinates."""
    best: Optional[EmotionType] = None
    best_dist = float("inf")
    for etype, (v, a) in _EMOTION_VA.items():
        dist = (valence - v) ** 2 + (arousal - a) ** 2
        if dist < best_dist:
            best_dist = dist
            best = etype
    return best  # type: ignore[return-value]

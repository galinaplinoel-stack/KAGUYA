"""Emotional transition rules and mood stabilization.

Defines how emotions shift in response to events and how moods naturally
settle towards a baseline over time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from kaguya.emotion.states import EmotionType, MoodState, emotion_va


@dataclass
class EmotionalTrigger:
    """An event that can shift emotional state.

    Attributes:
        event_type: A string tag describing the event (e.g. "compliment", "insult").
        target_emotion: The emotion this trigger activates.
        intensity_shift: How strongly it pushes (0.0 – 1.0).
        valence_shift: Change in pleasantness.
        arousal_shift: Change in energy.
    """

    event_type: str
    target_emotion: EmotionType
    intensity_shift: float = 0.3
    valence_shift: float = 0.0
    arousal_shift: float = 0.0


# ── Default trigger map ──────────────────────────────────────────────────

DEFAULT_TRIGGERS: Dict[str, EmotionalTrigger] = {
    "compliment": EmotionalTrigger(
        "compliment", EmotionType.joy, 0.3, valence_shift=0.3, arousal_shift=0.1,
    ),
    "insult": EmotionalTrigger(
        "insult", EmotionType.anger, 0.4, valence_shift=-0.3, arousal_shift=0.3,
    ),
    "threat": EmotionalTrigger(
        "threat", EmotionType.fear, 0.5, valence_shift=-0.4, arousal_shift=0.4,
    ),
    "surprise_good": EmotionalTrigger(
        "surprise_good", EmotionType.surprise, 0.4, valence_shift=0.2, arousal_shift=0.4,
    ),
    "surprise_bad": EmotionalTrigger(
        "surprise_bad", EmotionType.surprise, 0.4, valence_shift=-0.2, arousal_shift=0.4,
    ),
    "betrayal": EmotionalTrigger(
        "betrayal", EmotionType.disgust, 0.5, valence_shift=-0.5, arousal_shift=0.3,
    ),
    "trust_gain": EmotionalTrigger(
        "trust_gain", EmotionType.trust, 0.3, valence_shift=0.2, arousal_shift=-0.1,
    ),
    "loss": EmotionalTrigger(
        "loss", EmotionType.sadness, 0.5, valence_shift=-0.5, arousal_shift=-0.2,
    ),
    "success": EmotionalTrigger(
        "success", EmotionType.joy, 0.4, valence_shift=0.4, arousal_shift=0.2,
    ),
    "failure": EmotionalTrigger(
        "failure", EmotionType.sadness, 0.3, valence_shift=-0.3, arousal_shift=-0.1,
    ),
    "challenge": EmotionalTrigger(
        "challenge", EmotionType.anticipation, 0.3, valence_shift=0.1, arousal_shift=0.3,
    ),
}


class EmotionalTransition:
    """Manages emotional state transitions.

    Applies trigger effects to a ``MoodState`` and handles natural
    mood stabilization / decay back towards neutral.
    """

    def __init__(
        self,
        triggers: Optional[Dict[str, EmotionalTrigger]] = None,
        baseline_valence: float = 0.1,
        baseline_arousal: float = 0.3,
        stabilization_rate: float = 0.02,
    ) -> None:
        self.triggers: Dict[str, EmotionalTrigger] = triggers or dict(DEFAULT_TRIGGERS)
        self.baseline_valence = baseline_valence
        self.baseline_arousal = baseline_arousal
        self.stabilization_rate = stabilization_rate

    def apply_trigger(self, state: MoodState, event_type: str) -> MoodState:
        """Apply an emotional trigger, returning a new MoodState.

        The trigger's intensity shift is blended with the current state.
        If the new emotion differs from the current primary, it becomes
        the secondary emotion if intensity is lower, or replaces the primary.
        """
        trigger = self.triggers.get(event_type)
        if trigger is None:
            return state  # Unknown trigger → no change

        # Compute new valence/arousal
        new_valence = _clamp(state.valence + trigger.valence_shift, -1.0, 1.0)
        new_arousal = _clamp(state.arousal + trigger.arousal_shift, 0.0, 1.0)

        # Blend intensity
        new_intensity = _clamp(
            state.intensity * 0.4 + trigger.intensity_shift * 0.6, 0.0, 1.0
        )

        # Decide primary vs secondary
        if trigger.target_emotion == state.primary_emotion:
            return MoodState(
                primary_emotion=state.primary_emotion,
                intensity=new_intensity,
                valence=new_valence,
                arousal=new_arousal,
                decay_rate=state.decay_rate,
                secondary_emotion=state.secondary_emotion,
                secondary_intensity=state.secondary_intensity,
            )

        if new_intensity > state.intensity:
            # New emotion dominates
            return MoodState(
                primary_emotion=trigger.target_emotion,
                intensity=new_intensity,
                valence=new_valence,
                arousal=new_arousal,
                decay_rate=state.decay_rate,
                secondary_emotion=state.primary_emotion,
                secondary_intensity=state.intensity * 0.5,
            )
        else:
            # New emotion becomes secondary
            return MoodState(
                primary_emotion=state.primary_emotion,
                intensity=state.intensity,
                valence=new_valence,
                arousal=new_arousal,
                decay_rate=state.decay_rate,
                secondary_emotion=trigger.target_emotion,
                secondary_intensity=new_intensity,
            )

    def stabilize(self, state: MoodState, dt: float) -> MoodState:
        """Nudge valence/arousal towards baseline values.

        Called every tick to prevent moods from staying extreme indefinitely.
        """
        rate = self.stabilization_rate * dt
        new_valence = state.valence + (self.baseline_valence - state.valence) * rate
        new_arousal = state.arousal + (self.baseline_arousal - state.arousal) * rate
        return MoodState(
            primary_emotion=state.primary_emotion,
            intensity=state.intensity,
            valence=new_valence,
            arousal=new_arousal,
            decay_rate=state.decay_rate,
            timestamp=state.timestamp,
            secondary_emotion=state.secondary_emotion,
            secondary_intensity=state.secondary_intensity,
        )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

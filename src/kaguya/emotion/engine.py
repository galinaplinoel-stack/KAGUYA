"""Emotional state engine — real-time mood simulation with decay.

The engine maintains a ``MoodState``, applies triggers, runs decay on a
configurable tick interval, and exposes methods to query the current
emotional tone.
"""

from __future__ import annotations

import time
from typing import Dict, Optional

from kaguya.emotion.states import EmotionType, MoodState, emotion_va
from kaguya.emotion.transitions import EmotionalTransition


class EmotionalStateEngine:
    """Real-time emotional state manager.

    Usage::

        engine = EmotionalStateEngine()
        engine.trigger("compliment")
        engine.update(dt=1.0)
        mood = engine.current_mood()
    """

    def __init__(
        self,
        initial: Optional[MoodState] = None,
        decay_rate: float = 0.05,
        transition: Optional[EmotionalTransition] = None,
    ) -> None:
        self._state: MoodState = initial or MoodState.neutral()
        self._state.decay_rate = decay_rate
        self._transition = transition or EmotionalTransition()
        self._history: list[Dict] = [self._state.to_dict()]
        self._last_tick: float = time.time()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def state(self) -> MoodState:
        """Current mood state snapshot."""
        return self._state

    def current_mood(self) -> Dict:
        """Return a serialisable dict of the current mood."""
        return self._state.to_dict()

    def trigger(self, event_type: str) -> MoodState:
        """Apply an emotional trigger event.

        Args:
            event_type: Key in the trigger map (e.g. "compliment", "insult").

        Returns:
            The updated ``MoodState``.
        """
        self._state = self._transition.apply_trigger(self._state, event_type)
        self._state.timestamp = time.time()
        self._history.append(self._state.to_dict())
        self._trim_history()
        return self._state

    def set_emotion(
        self,
        emotion: EmotionType,
        intensity: float = 0.5,
        valence: Optional[float] = None,
        arousal: Optional[float] = None,
    ) -> MoodState:
        """Directly set the emotional state (useful for initialisation)."""
        v, a = emotion_va(emotion)
        self._state = MoodState(
            primary_emotion=emotion,
            intensity=max(0.0, min(1.0, intensity)),
            valence=valence if valence is not None else v,
            arousal=arousal if arousal is not None else a,
            decay_rate=self._state.decay_rate,
        )
        self._state.timestamp = time.time()
        self._history.append(self._state.to_dict())
        self._trim_history()
        return self._state

    def update(self, dt: Optional[float] = None) -> MoodState:
        """Tick the engine: apply decay and stabilization.

        Args:
            dt: Elapsed seconds since last update. If ``None``, wall-clock
                time is used automatically.
        """
        now = time.time()
        if dt is None:
            dt = now - self._last_tick
        self._last_tick = now

        # Decay intensity
        decay = self._state.decay_rate * dt
        new_intensity = max(0.0, self._state.intensity - decay)

        # Decay secondary
        new_sec_intensity = max(0.0, self._state.secondary_intensity - decay * 0.5)
        if new_sec_intensity < 0.01:
            new_sec_intensity = 0.0

        self._state = MoodState(
            primary_emotion=self._state.primary_emotion,
            intensity=new_intensity,
            valence=self._state.valence,
            arousal=self._state.arousal,
            decay_rate=self._state.decay_rate,
            timestamp=now,
            secondary_emotion=self._state.secondary_emotion if new_sec_intensity > 0 else None,
            secondary_intensity=new_sec_intensity,
        )

        # Stabilise towards baseline
        self._state = self._transition.stabilize(self._state, dt)

        # If intensity is very low, drift towards neutral emotion
        if self._state.intensity < 0.05:
            self._state = MoodState.neutral()
            self._state.decay_rate = self._state.decay_rate

        return self._state

    def get_tone(self) -> Dict[str, float]:
        """Return tone modifiers derived from current emotional state.

        Returns a dict with keys:
            - positive (0-1): how positive the mood is
            - energy (0-1): how energetic / activated
            - stability (0-1): how stable / calm (inverse of intensity)
            - warmth (0-1): social warmth
        """
        valence_norm = (self._state.valence + 1.0) / 2.0  # map -1..1 → 0..1
        energy = self._state.arousal
        stability = 1.0 - self._state.intensity

        # Warmth is higher for positive, lower-arousal states
        warmth = valence_norm * 0.6 + (1 - energy) * 0.4

        return {
            "positive": round(valence_norm, 4),
            "energy": round(energy, 4),
            "stability": round(stability, 4),
            "warmth": round(max(0.0, min(1.0, warmth)), 4),
        }

    @property
    def history(self) -> list[Dict]:
        """Mood state history (most recent last)."""
        return list(self._history)

    def reset(self) -> None:
        """Reset to neutral mood."""
        self._state = MoodState.neutral()
        self._history = [self._state.to_dict()]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _trim_history(self, max_len: int = 500) -> None:
        if len(self._history) > max_len:
            self._history = self._history[-max_len:]

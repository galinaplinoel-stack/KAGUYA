"""Emotional conditioning — repeated emotional states form habits."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class EmotionalPattern:
    """A recurring emotional pattern that forms behavioral habits."""
    emotion: str
    frequency: int = 0
    total_intensity: float = 0.0
    last_seen: float = field(default_factory=time.time)

    @property
    def average_intensity(self) -> float:
        return self.total_intensity / max(1, self.frequency)


class EmotionalConditioning:
    """Tracks emotional patterns and forms behavioral habits.

    When an emotion occurs frequently with high intensity,
    it creates conditioned behavioral responses.
    """

    def __init__(self, habit_threshold: int = 5) -> None:
        self.patterns: dict[str, EmotionalPattern] = {}
        self.habits: dict[str, dict] = {}
        self.habit_threshold = habit_threshold

    def record_emotion(self, emotion: str, intensity: float) -> None:
        """Record an emotional occurrence for conditioning."""
        if emotion not in self.patterns:
            self.patterns[emotion] = EmotionalPattern(emotion=emotion)

        pattern = self.patterns[emotion]
        pattern.frequency += 1
        pattern.total_intensity += intensity
        pattern.last_seen = time.time()

        if pattern.frequency >= self.habit_threshold:
            self._form_habit(emotion, pattern)

    def _form_habit(self, emotion: str, pattern: EmotionalPattern) -> None:
        """Form a behavioral habit from a recurring emotional pattern."""
        self.habits[emotion] = {
            "strength": min(1.0, pattern.average_intensity * 0.5),
            "frequency": pattern.frequency,
            "formed_at": time.time(),
        }

    def get_conditioned_response(self, emotion: str) -> dict | None:
        """Get the conditioned behavioral response for an emotion."""
        return self.habits.get(emotion)

    def get_habits(self) -> dict[str, dict]:
        """Get all formed habits."""
        return dict(self.habits)

    def decay(self, decay_factor: float = 0.99) -> None:
        """Apply time-based decay to all patterns."""
        current = time.time()
        for pattern in self.patterns.values():
            elapsed_hours = (current - pattern.last_seen) / 3600
            decay = decay_factor ** elapsed_hours
            pattern.total_intensity *= decay

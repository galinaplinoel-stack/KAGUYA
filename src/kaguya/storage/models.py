"""SQLAlchemy ORM models for persistent storage."""
from __future__ import annotations

import json
import time
from typing import Optional

from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class PersonalityModel(Base):
    """Persistent personality profile storage."""
    __tablename__ = "personalities"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    traits_json = Column(Text, nullable=False, default="{}")
    style_json = Column(Text, nullable=False, default="{}")
    preset = Column(String(64), nullable=True)
    created_at = Column(Float, default=time.time)
    updated_at = Column(Float, default=time.time, onupdate=time.time)

    emotions = relationship("EmotionModel", back_populates="personality")
    relationships = relationship("RelationshipModel", back_populates="personality")

    @property
    def traits(self) -> dict:
        return json.loads(self.traits_json)

    @traits.setter
    def traits(self, value: dict) -> None:
        self.traits_json = json.dumps(value)

    @property
    def style(self) -> dict:
        return json.loads(self.style_json)

    @style.setter
    def style(self, value: dict) -> None:
        self.style_json = json.dumps(value)


class EmotionModel(Base):
    """Persistent emotional state storage."""
    __tablename__ = "emotions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    personality_id = Column(String(64), ForeignKey("personalities.id"), nullable=False)
    primary_emotion = Column(String(32), nullable=False)
    intensity = Column(Float, default=0.5)
    valence = Column(Float, default=0.0)
    arousal = Column(Float, default=0.5)
    mood_json = Column(Text, default="{}")
    timestamp = Column(Float, default=time.time)

    personality = relationship("PersonalityModel", back_populates="emotions")

    __table_args__ = (
        Index("ix_emotions_personality", "personality_id"),
    )


class RelationshipModel(Base):
    """Persistent relationship data storage."""
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    personality_id = Column(String(64), ForeignKey("personalities.id"), nullable=False)
    user_id = Column(String(128), nullable=False)
    trust = Column(Float, default=0.5)
    familiarity = Column(Float, default=0.0)
    affinity = Column(Float, default=0.5)
    respect = Column(Float, default=0.5)
    interaction_count = Column(Integer, default=0)
    history_json = Column(Text, default="[]")
    last_interaction = Column(Float, default=time.time)

    personality = relationship("PersonalityModel", back_populates="relationships")

    __table_args__ = (
        Index("ix_rel_personality_user", "personality_id", "user_id", unique=True),
    )

    @property
    def history(self) -> list[dict]:
        return json.loads(self.history_json)

    @history.setter
    def history(self, value: list[dict]) -> None:
        self.history_json = json.dumps(value)


class EvolutionLogModel(Base):
    """Log of personality evolution events."""
    __tablename__ = "evolution_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    personality_id = Column(String(64), ForeignKey("personalities.id"), nullable=False)
    trait = Column(String(64), nullable=False)
    old_value = Column(Float, nullable=False)
    new_value = Column(Float, nullable=False)
    cause = Column(Text, default="")
    timestamp = Column(Float, default=time.time)

    __table_args__ = (
        Index("ix_evolution_personality", "personality_id"),
    )

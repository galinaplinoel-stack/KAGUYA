"""Pydantic request/response schemas for the API."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# Personality schemas
class TraitVectorSchema(BaseModel):
    curiosity: float = Field(0.5, ge=0.0, le=1.0)
    kindness: float = Field(0.5, ge=0.0, le=1.0)
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    humor: float = Field(0.5, ge=0.0, le=1.0)
    empathy: float = Field(0.5, ge=0.0, le=1.0)
    creativity: float = Field(0.5, ge=0.0, le=1.0)
    discipline: float = Field(0.5, ge=0.0, le=1.0)
    introversion: float = Field(0.5, ge=0.0, le=1.0)
    aggression: float = Field(0.2, ge=0.0, le=1.0)
    sensitivity: float = Field(0.5, ge=0.0, le=1.0)


class CreatePersonalityRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    traits: Optional[TraitVectorSchema] = None
    preset: Optional[str] = None


class UpdatePersonalityRequest(BaseModel):
    name: Optional[str] = None
    traits: Optional[TraitVectorSchema] = None


class PersonalityResponse(BaseModel):
    id: str
    name: str
    traits: dict[str, float]
    preset: Optional[str] = None
    created_at: str


# Emotion schemas
class EmotionResponse(BaseModel):
    personality_id: str
    primary_emotion: str
    intensity: float
    valence: float
    arousal: float


class TriggerEmotionRequest(BaseModel):
    event: str = Field(..., min_length=1)
    intensity: float = Field(0.5, ge=0.0, le=1.0)


# Relationship schemas
class RelationshipResponse(BaseModel):
    personality_id: str
    user_id: str
    trust: float
    familiarity: float
    affinity: float
    respect: float
    interaction_count: int


class InteractRequest(BaseModel):
    sentiment: float = Field(0.0, ge=-1.0, le=1.0)
    emotion: Optional[str] = None
    summary: Optional[str] = None


# Chat schemas
class ChatRequest(BaseModel):
    personality_id: str
    user_id: str
    message: str = Field(..., min_length=1)
    base_prompt: str = Field("You are a helpful AI assistant.")


class ChatResponse(BaseModel):
    modified_prompt: str
    personality_context: dict
    emotional_state: dict
    relationship_context: Optional[dict] = None


# Evolution schemas
class EvolutionResponse(BaseModel):
    total_interactions: int
    total_events: int
    trait_drifts: dict[str, float]
    current_traits: dict[str, float]


# Generic
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

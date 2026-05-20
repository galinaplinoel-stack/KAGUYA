# KAGUYA Architecture

## System Overview

```
┌─────────────────────────────────────────────────────┐
│                    KAGUYA Engine                     │
├─────────────┬─────────────┬─────────────┬───────────┤
│ Personality │  Emotion    │ Relationship│ Evolution │
│   Core      │  Engine     │  System     │  Engine   │
├─────────────┴─────────────┴─────────────┴───────────┤
│              Response Modifier Middleware             │
├─────────────────────────────────────────────────────┤
│         Storage Layer (SQLite / PostgreSQL)          │
├─────────────────────────────────────────────────────┤
│           REST API  │  WebSocket  │  Dashboard      │
└─────────────────────────────────────────────────────┘
```

## Core Components

### 1. Personality Core
The foundation of KAGUYA. Manages:
- **TraitVector**: 10+ personality dimensions (0.0-1.0)
- **CharacterProfile**: Named personality with communication style
- **Presets**: Pre-built personality archetypes

### 2. Emotional State Engine
Real-time emotional simulation using the Valence-Arousal model:
- **Valence**: Pleasantness (-1.0 to 1.0)
- **Arousal**: Energy level (0.0 to 1.0)
- **Emotion Types**: joy, sadness, anger, fear, surprise, disgust, trust, anticipation
- **Decay**: Emotions naturally fade over time
- **Transitions**: Events trigger emotional changes

### 3. Relationship System
Per-user relationship tracking:
- **Trust**: How much the AI trusts a user (0-1)
- **Familiarity**: How well the AI knows the user (0-1)
- **Affinity**: Emotional liking (0-1)
- **Respect**: Professional respect (0-1)
- **History**: Interaction log with sentiment analysis

### 4. Response Modifier
The integration layer that shapes LLM output:
- Generates system prompt additions from personality context
- Adjusts tone, verbosity, formality based on emotion
- Modifies behavior based on relationship strength
- Returns enhanced prompts for any OpenAI-compatible API

### 5. Evolution Engine
Gradual personality change over time:
- Traits shift based on interaction reinforcement
- Emotional conditioning creates behavioral habits
- Configurable learning rate and change limits
- Full evolution history tracking

## Data Flow

```
User Message
    │
    ▼
┌──────────────┐
│  Relationship │ ── Trust/Familiarity check
│  Manager      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Emotion    │ ── Current mood affects response
│   Engine     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Response    │ ── Enhanced system prompt
│  Modifier    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   LLM API   │ ── Modified behavior
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Evolution   │ ── Traits update based on interaction
│  Engine      │
└──────────────┘
```

## Design Principles

1. **Modularity**: Each system works independently
2. **Composability**: Systems combine for richer behavior
3. **Persistence**: All state survives restarts
4. **Extensibility**: Plugin architecture for custom behaviors
5. **API-First**: Everything accessible via REST/WebSocket

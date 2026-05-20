# API Reference

## Base URL
```
http://localhost:8000
```

## Endpoints

### Personality

#### Create Personality
```
POST /personality
```
```json
{
    "name": "Kaguya",
    "traits": {
        "curiosity": 0.8,
        "kindness": 0.9,
        "humor": 0.6
    }
}
```

#### Get Personality
```
GET /personality/{id}
```

#### Update Personality
```
PUT /personality/{id}
```

#### List All
```
GET /personality
```

### Emotion

#### Get Current Emotion
```
GET /emotion/{personality_id}
```
Response:
```json
{
    "personality_id": "xxx",
    "primary_emotion": "joy",
    "intensity": 0.7,
    "valence": 0.8,
    "arousal": 0.6
}
```

#### Trigger Emotion
```
POST /emotion/{personality_id}/trigger
```
```json
{
    "event": "received compliment",
    "intensity": 0.8
}
```

#### Apply Decay
```
POST /emotion/{personality_id}/decay
```

### Relationships

#### Get Relationship
```
GET /relationships/{personality_id}/{user_id}
```

#### Log Interaction
```
POST /relationships/{personality_id}/{user_id}/interact
```
```json
{
    "sentiment": 0.7,
    "emotion": "joy",
    "summary": "User said something nice"
}
```

#### List Relationships
```
GET /relationships/{personality_id}
```

### Chat

#### Chat with Personality
```
POST /chat
```
```json
{
    "personality_id": "xxx",
    "user_id": "user_1",
    "message": "Hello!",
    "base_prompt": "You are a helpful assistant."
}
```
Returns the personality-enhanced system prompt.

### Evolution

#### Get Evolution History
```
GET /evolution/{personality_id}
```

#### Trigger Evolution
```
POST /evolution/{personality_id}/evolve?sentiment=0.8&intensity=0.5&traits=kindness,empathy
```

### WebSocket

#### Stream Real-time State
```
ws://localhost:8000/ws/{personality_id}
```
Sends JSON updates every 2 seconds with current emotional state and traits.

# Data Model: AI Chat Service

## Core Entities

### Session
Represents an active conversation session in memory.

**Attributes**:
- `session_id`: str (UUID hex format, auto-generated)
- `system_prompt_template`: str (original template with {{variables}})
- `resolved_system_prompt`: str (after Mustache substitution)
- `variables`: Dict[str, str] (variable substitution context)
- `rounds`: List[MessageRound] (all conversation rounds, chronologically ordered)
- `message_queue`: asyncio.Queue (for serializing concurrent messages)
- `created_at`: datetime (ISO 8601 timestamp)
- `last_activity`: datetime (ISO 8601 timestamp, updated on each message)

**Validation Rules**:
- `session_id` must be unique across all active sessions
- `system_prompt_template` required (can be plain text, no variables)
- `variables` keys must match template variables (missing vars → empty string)
- `rounds` max stored: unlimited (but only last 10 sent to Doubao API)
- `created_at` immutable
- `last_activity` updated on each message send/receive

**State Transitions**:
- Created → Active (on first message)
- Active → Active (on subsequent messages)
- Active → Deleted (on explicit DELETE request or server shutdown)

**Relationships**:
- Session has many MessageRounds (1:N)
- Session has one HistoryFile (1:1, persisted to JSON)

---

### MessageRound
Represents one complete user-assistant exchange.

**Attributes**:
- `round_number`: int (sequential, starts at 1)
- `user_message`: str (required, non-empty)
- `assistant_response`: str (from Doubao API)
- `timestamp`: datetime (ISO 8601, when user message received)

**Validation Rules**:
- `round_number` sequential within session (1, 2, 3, ...)
- `user_message` must not be empty or whitespace-only
- `assistant_response` may be empty if Doubao API fails (error logged)
- `timestamp` immutable

**Business Logic**:
- Sliding window: Only last 10 rounds included in Doubao API context
- Full history: All rounds stored in memory and JSON file
- Context format: `[{role: "user", content: "..."}, {role: "assistant", content: "..."}]`

**Relationships**:
- MessageRound belongs to one Session (N:1)

---

### HistoryFile
JSON file representation of conversation session.

**File Location**: `./conversations/{timestamp}_{session_id}.json`

**Schema**:
```json
{
  "session_id": "550e8400e29b41d4a716446655440000",
  "system_prompt_template": "You are a {{role}} assistant",
  "resolved_system_prompt": "You are a helpful assistant",
  "variables": {
    "role": "helpful"
  },
  "created_at": "2025-10-06T15:30:00Z",
  "last_activity": "2025-10-06T15:35:00Z",
  "rounds": [
    {
      "round_number": 1,
      "user_message": "Hello",
      "assistant_response": "Hi! How can I help you?",
      "timestamp": "2025-10-06T15:30:05Z"
    }
  ]
}
```

**Encoding**: UTF-8 (ensure_ascii=False for Chinese support)
**Format**: Pretty-printed (indent=2)

**Lifecycle**:
- Created when session is created (empty rounds array)
- Updated incrementally after each message round (append to rounds array)
- Persisted indefinitely (manual cleanup only)

**File Naming Convention**:
- Pattern: `{timestamp}_{session_id}.json`
- Example: `20251006153000_550e8400e29b41d4a716446655440000.json`
- Timestamp format: YYYYMMDDHHmmss (for chronological sorting)

---

## Supporting Models

### TemplateContext
Variable substitution context for Mustache templates.

**Attributes**:
- `variables`: Dict[str, str] (all values must be strings)

**Validation Rules**:
- Keys must match variables in template (e.g., `{{name}}` requires key "name")
- Missing keys result in empty string substitution
- Extra keys ignored (not an error)
- Non-string values rejected at API layer (Pydantic validation)

**Business Logic**:
- Applied once during session creation
- Immutable after session creation
- Stored in Session entity for history file

---

### DoubaoContext
Context array sent to Doubao Seed 1.6 API.

**Format**: Array of message objects
```json
[
  {"role": "system", "content": "You are a helpful assistant"},
  {"role": "user", "content": "Hello"},
  {"role": "assistant", "content": "Hi! How can I help you?"},
  {"role": "user", "content": "Tell me a joke"}
]
```

**Construction Logic**:
1. Start with system message (resolved_system_prompt)
2. Append last N rounds as user/assistant pairs
   - N = min(10, total rounds)
   - Sliding window: If >10 rounds, take rounds[-10:]
3. Append new user message

**Example** (12 rounds total, new message):
- Include: system + rounds[2:12] + new message
- Exclude: rounds[0:2] (oldest 2 rounds)
- Result: 1 system + 20 messages (10 user + 10 assistant) + 1 new user = 22 total

---

## API Request/Response Models

### CreateSessionRequest
```json
{
  "system_prompt_template": "You are a {{role}} assistant",
  "variables": {
    "role": "helpful"
  }
}
```

**Validation**:
- `system_prompt_template` required, non-empty string
- `variables` optional (default: {}), must be Dict[str, str]

---

### CreateSessionResponse
```json
{
  "session_id": "550e8400e29b41d4a716446655440000",
  "resolved_system_prompt": "You are a helpful assistant",
  "created_at": "2025-10-06T15:30:00Z"
}
```

---

### SendMessageRequest
```json
{
  "message": "Hello, how are you?"
}
```

**Validation**:
- `message` required, non-empty string (after strip())

---

### SendMessageResponse
```json
{
  "session_id": "550e8400e29b41d4a716446655440000",
  "round_number": 1,
  "user_message": "Hello, how are you?",
  "assistant_response": "I'm doing well, thank you for asking!",
  "timestamp": "2025-10-06T15:30:05Z"
}
```

---

### GetHistoryResponse
```json
{
  "session_id": "550e8400e29b41d4a716446655440000",
  "system_prompt_template": "You are a {{role}} assistant",
  "resolved_system_prompt": "You are a helpful assistant",
  "variables": {
    "role": "helpful"
  },
  "created_at": "2025-10-06T15:30:00Z",
  "last_activity": "2025-10-06T15:35:00Z",
  "rounds": [
    {
      "round_number": 1,
      "user_message": "Hello",
      "assistant_response": "Hi!",
      "timestamp": "2025-10-06T15:30:05Z"
    }
  ]
}
```

---

### ListSessionsResponse
```json
{
  "sessions": [
    {
      "session_id": "550e8400e29b41d4a716446655440000",
      "created_at": "2025-10-06T15:30:00Z",
      "last_activity": "2025-10-06T15:35:00Z",
      "message_count": 5
    }
  ],
  "total": 1
}
```

---

### ErrorResponse
```json
{
  "error": "SessionNotFound",
  "detail": "Session 123abc not found",
  "session_id": "123abc"
}
```

**HTTP Status Codes**:
- 400: Validation error (empty message, invalid variables)
- 404: Session not found
- 429: Doubao rate limit exceeded
- 500: Internal server error
- 503: Doubao API unavailable

---

## Entity Relationships Diagram

```
┌─────────────────┐
│     Session     │
├─────────────────┤
│ session_id (PK) │
│ template        │
│ resolved_prompt │
│ variables       │
│ message_queue   │
│ created_at      │
│ last_activity   │
└────────┬────────┘
         │ 1
         │
         │ N
         ▼
┌─────────────────┐
│  MessageRound   │
├─────────────────┤
│ round_number    │
│ user_message    │
│ assistant_resp  │
│ timestamp       │
└─────────────────┘

┌─────────────────┐
│   HistoryFile   │ (JSON on disk)
├─────────────────┤
│ session_id      │
│ template        │
│ resolved_prompt │
│ variables       │
│ created_at      │
│ last_activity   │
│ rounds[]        │
└─────────────────┘
```

---

## Data Constraints & Business Rules

### Session Capacity
- **Max Active Sessions**: 50 (configurable via env var)
- **Enforcement**: Return HTTP 503 when creating session if capacity reached
- **Cleanup**: Sessions deleted explicitly via API (no TTL/auto-expire)

### Message Constraints
- **Max Message Length**: 4096 characters (Doubao API limit)
- **Min Message Length**: 1 character (after strip())
- **Concurrency**: Messages to same session queued (FIFO)

### Context Window
- **Doubao API Limit**: Last 10 conversation rounds
- **Storage**: All rounds persisted to JSON file
- **Memory**: All rounds kept in Session.rounds list

### File Storage
- **Directory**: `./conversations/` (created on startup)
- **Permissions**: Read/write for service user
- **Cleanup**: Manual only (no automatic deletion)
- **Corruption Handling**: Atomic write (temp file + rename)

### Performance Constraints
- **First Token Timeout**: 6 seconds
- **File Write**: Async (non-blocking)
- **Session Lookup**: O(1) via dict
- **Message Processing**: Sequential per session, parallel across sessions

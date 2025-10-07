# Quickstart: AI Chat Service

## Prerequisites
- Python 3.11+
- Doubao (Volcano Engine) API key
- Internet connection for Doubao API access

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```bash
DOUBAO_API_KEY=your_api_key_here
DOUBAO_API_ENDPOINT=https://ark.cn-beijing.volces.com/api/v3/chat/completions
MAX_SESSIONS=50
```

### 3. Start Service
```bash
uvicorn src.main:app --reload --port 8000
```

Server starts at: `http://localhost:8000`
API docs (Swagger): `http://localhost:8000/docs`

---

## Usage Examples

### Example 1: Simple Conversation (No Variables)

**Step 1: Create Session**
```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt_template": "You are a helpful Python programming assistant."
  }'
```

Response:
```json
{
  "session_id": "550e8400e29b41d4a716446655440000",
  "resolved_system_prompt": "You are a helpful Python programming assistant.",
  "created_at": "2025-10-06T15:30:00Z"
}
```

**Step 2: Send First Message**
```bash
curl -X POST http://localhost:8000/sessions/550e8400e29b41d4a716446655440000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain list comprehensions"
  }'
```

Response:
```json
{
  "session_id": "550e8400e29b41d4a716446655440000",
  "round_number": 1,
  "user_message": "Explain list comprehensions",
  "assistant_response": "List comprehensions provide a concise way to create lists in Python...",
  "timestamp": "2025-10-06T15:30:05Z"
}
```

**Step 3: Continue Conversation**
```bash
curl -X POST http://localhost:8000/sessions/550e8400e29b41d4a716446655440000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you show me an example?"
  }'
```

Response:
```json
{
  "session_id": "550e8400e29b41d4a716446655440000",
  "round_number": 2,
  "user_message": "Can you show me an example?",
  "assistant_response": "Here's an example: squares = [x**2 for x in range(10)]...",
  "timestamp": "2025-10-06T15:30:15Z"
}
```

---

### Example 2: Conversation with Variable Substitution

**Create Session with Variables**
```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt_template": "You are a {{personality}} assistant specializing in {{domain}}. Your tone is {{tone}}.",
    "variables": {
      "personality": "friendly",
      "domain": "data science",
      "tone": "professional yet approachable"
    }
  }'
```

Response:
```json
{
  "session_id": "6fa459ea3b45454a9da36bb77b8e6c57",
  "resolved_system_prompt": "You are a friendly assistant specializing in data science. Your tone is professional yet approachable.",
  "created_at": "2025-10-06T15:32:00Z"
}
```

**Send Message**
```bash
curl -X POST http://localhost:8000/sessions/6fa459ea3b45454a9da36bb77b8e6c57/messages \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the difference between supervised and unsupervised learning"
  }'
```

---

### Example 3: Missing Variables (Empty String Substitution)

**Create Session with Partial Variables**
```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt_template": "You are a {{role}} assistant. Your expertise is {{expertise}}.",
    "variables": {
      "role": "helpful"
    }
  }'
```

Response:
```json
{
  "session_id": "7c9e6679c4d14fa09e78f14e4d3e0f2a",
  "resolved_system_prompt": "You are a helpful assistant. Your expertise is .",
  "created_at": "2025-10-06T15:34:00Z"
}
```

Note: `{{expertise}}` → empty string (missing variable)

---

### Example 4: Get Conversation History

```bash
curl -X GET http://localhost:8000/sessions/550e8400e29b41d4a716446655440000/history
```

Response:
```json
{
  "session_id": "550e8400e29b41d4a716446655440000",
  "system_prompt_template": "You are a helpful Python programming assistant.",
  "resolved_system_prompt": "You are a helpful Python programming assistant.",
  "variables": {},
  "created_at": "2025-10-06T15:30:00Z",
  "last_activity": "2025-10-06T15:30:15Z",
  "rounds": [
    {
      "round_number": 1,
      "user_message": "Explain list comprehensions",
      "assistant_response": "List comprehensions provide...",
      "timestamp": "2025-10-06T15:30:05Z"
    },
    {
      "round_number": 2,
      "user_message": "Can you show me an example?",
      "assistant_response": "Here's an example: squares = [x**2 for x in range(10)]...",
      "timestamp": "2025-10-06T15:30:15Z"
    }
  ]
}
```

---

### Example 5: List All Sessions

```bash
curl -X GET http://localhost:8000/sessions
```

Response:
```json
{
  "sessions": [
    {
      "session_id": "550e8400e29b41d4a716446655440000",
      "created_at": "2025-10-06T15:30:00Z",
      "last_activity": "2025-10-06T15:30:15Z",
      "message_count": 2
    },
    {
      "session_id": "6fa459ea3b45454a9da36bb77b8e6c57",
      "created_at": "2025-10-06T15:32:00Z",
      "last_activity": "2025-10-06T15:32:30Z",
      "message_count": 1
    }
  ],
  "total": 2
}
```

---

### Example 6: Delete Session

```bash
curl -X DELETE http://localhost:8000/sessions/550e8400e29b41d4a716446655440000
```

Response: HTTP 204 No Content

Note: JSON history file persists at `./conversations/20251006153000_550e8400e29b41d4a716446655440000.json`

---

## Testing Scenarios

### Scenario 1: Multi-Turn Context (Sliding Window)

Create session and send 12 messages to test 10-round sliding window:

```bash
# Create session
SESSION_ID=$(curl -s -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"system_prompt_template": "You are a helpful assistant."}' \
  | jq -r '.session_id')

# Send 12 messages
for i in {1..12}; do
  curl -X POST http://localhost:8000/sessions/$SESSION_ID/messages \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Message number $i\"}"
  sleep 1
done

# Verify only last 10 rounds in context (check Doubao API calls in logs)
```

Expected: Rounds 1-2 excluded from context when sending message 13.

---

### Scenario 2: Concurrent Messages (Queuing)

Send 3 messages to same session simultaneously:

```bash
SESSION_ID="your_session_id_here"

# Launch 3 concurrent requests
curl -X POST http://localhost:8000/sessions/$SESSION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "First concurrent message"}' &

curl -X POST http://localhost:8000/sessions/$SESSION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Second concurrent message"}' &

curl -X POST http://localhost:8000/sessions/$SESSION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Third concurrent message"}' &

wait
```

Expected: All 3 messages processed sequentially (FIFO order), no race conditions.

---

### Scenario 3: Session Capacity Limit

Create 51 sessions to test capacity limit:

```bash
for i in {1..51}; do
  curl -X POST http://localhost:8000/sessions \
    -H "Content-Type: application/json" \
    -d '{"system_prompt_template": "Session '$i'"}'
done
```

Expected:
- Sessions 1-50: HTTP 201 Created
- Session 51: HTTP 503 Service Unavailable

---

### Scenario 4: Error Handling

**Empty Message (400 Bad Request)**
```bash
curl -X POST http://localhost:8000/sessions/$SESSION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "   "}'
```

Expected:
```json
{
  "error": "ValidationError",
  "detail": "message cannot be empty or whitespace-only",
  "session_id": "..."
}
```

**Session Not Found (404)**
```bash
curl -X POST http://localhost:8000/sessions/invalid_session_id/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

Expected:
```json
{
  "error": "SessionNotFound",
  "detail": "Session invalid_session_id not found",
  "session_id": "invalid_session_id"
}
```

---

## JSON History Files

History files are written to `./conversations/` after each message round:

**File Name**: `{timestamp}_{session_id}.json`
**Example**: `20251006153000_550e8400e29b41d4a716446655440000.json`

**Content** (pretty-printed UTF-8):
```json
{
  "session_id": "550e8400e29b41d4a716446655440000",
  "system_prompt_template": "You are a helpful Python programming assistant.",
  "resolved_system_prompt": "You are a helpful Python programming assistant.",
  "variables": {},
  "created_at": "2025-10-06T15:30:00Z",
  "last_activity": "2025-10-06T15:30:15Z",
  "rounds": [
    {
      "round_number": 1,
      "user_message": "Explain list comprehensions",
      "assistant_response": "List comprehensions provide...",
      "timestamp": "2025-10-06T15:30:05Z"
    }
  ]
}
```

---

## Debugging

**View Service Logs** (JSON format):
```bash
tail -f logs/app.log | jq .
```

**Check Health**:
```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "ok",
  "doubao_connected": true
}
```

**API Documentation**:
Visit `http://localhost:8000/docs` for interactive Swagger UI.

---

## Next Steps

After verifying the quickstart scenarios:
1. Run contract tests: `pytest tests/contract/`
2. Run integration tests: `pytest tests/integration/`
3. Run unit tests: `pytest tests/unit/`
4. Check code coverage: `pytest --cov=src tests/`
5. Review JSON history files in `./conversations/`

For production deployment, consider:
- Add CORS middleware if frontend integration needed
- Configure log aggregation (ELK, Datadog)
- Set up monitoring/alerts for Doubao API errors
- Implement session cleanup script for manual maintenance

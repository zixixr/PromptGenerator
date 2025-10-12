# AI Chat Service with Doubao Seed 1.6

A FastAPI-based conversation service that connects to Doubao Seed 1.6 model, maintaining 10-round conversation context with Mustache-style variable interpolation in system prompts.

## Features

- **Session Management**: Create and manage up to 50 concurrent conversation sessions
- **Context Window**: Automatically maintains last 10 conversation rounds
- **Template Variables**: Mustache-style variable substitution in system prompts
- **Async Operations**: Non-blocking file I/O and API calls
- **JSON History**: All conversations persisted to local JSON files
- **RESTful API**: 5 endpoints for full session lifecycle management

## Prerequisites

- Python 3.11+
- Doubao (Volcano Engine) API key
- Internet connection for API access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PromptGenerator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your ARK_API_KEY
```

## Configuration

Create a `.env` file with the following variables:

```env
ARK_API_KEY=your_api_key_here
DOUBAO_API_ENDPOINT=https://ark.cn-beijing.volces.com/api/v3
MAX_SESSIONS=50
CONVERSATIONS_DIR=./conversations
```

## Running the Service

Start the FastAPI server:

```bash
uvicorn src.main:app --reload --port 8000
```

The service will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### 1. Create Session
```bash
POST /sessions
Content-Type: application/json

{
  "system_prompt_template": "You are a {{role}} assistant.",
  "variables": {"role": "helpful"}
}
```

### 2. Send Message
```bash
POST /sessions/{session_id}/messages
Content-Type: application/json

{
  "message": "Hello, how are you?"
}
```

### 3. Get History
```bash
GET /sessions/{session_id}/history
```

### 4. List Sessions
```bash
GET /sessions
```

### 5. Delete Session
```bash
DELETE /sessions/{session_id}
```

## Testing

Run all tests:
```bash
pytest tests/
```

Run specific test suites:
```bash
pytest tests/contract/      # Contract tests
pytest tests/integration/   # Integration tests
pytest tests/unit/          # Unit tests
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Project Structure

```
.
├── src/
│   ├── models/           # Data models (Session, MessageRound, etc.)
│   ├── services/         # Business logic (SessionManager, DoubaoClient, etc.)
│   ├── routes/           # API endpoints
│   ├── config.py         # Configuration management
│   ├── logging_config.py # Structured logging setup
│   └── main.py           # FastAPI application entry point
├── tests/
│   ├── contract/         # API contract tests
│   ├── integration/      # Integration tests
│   └── unit/             # Unit tests
├── conversations/        # JSON history files (created at runtime)
├── requirements.txt      # Python dependencies
├── pytest.ini           # Pytest configuration
└── .env.example         # Environment variable template
```

## Features in Detail

### Session Management
- Ephemeral sessions stored in memory
- Automatic UUID generation for session IDs
- Maximum 50 concurrent sessions (configurable)
- Last activity tracking

### Context Window
- Maintains last 10 conversation rounds
- Older rounds preserved in history files
- Sliding window sent to Doubao API

### Template Variables
- Mustache {{variable}} syntax
- Missing variables → empty string
- Supports multiple variables per template

### File Storage
- Async JSON file writes (non-blocking)
- UTF-8 encoding for Chinese text
- Pretty-printed format (indent=2)
- Atomic writes (temp file + rename)

## Development

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Sort imports
isort src/ tests/
```

### Logging
The service uses structured JSON logging to stdout:
```json
{
  "timestamp": "2025-10-06T15:30:00Z",
  "level": "INFO",
  "name": "src.services.session_manager",
  "message": "Created session abc123"
}
```

## Error Handling

The API returns standardized error responses:

```json
{
  "error": "SessionNotFound",
  "detail": "Session abc123 not found",
  "session_id": "abc123"
}
```

HTTP Status Codes:
- `201`: Session created
- `200`: Success
- `204`: Deleted successfully
- `400`: Invalid request
- `404`: Session not found
- `429`: Rate limit exceeded
- `503`: Service unavailable

## Production Considerations

- Add CORS middleware if frontend integration needed
- Configure log aggregation (ELK, Datadog)
- Set up monitoring/alerts for Doubao API errors
- Implement session cleanup script for manual maintenance
- Use proper secrets management for API keys
- Consider rate limiting on endpoints

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

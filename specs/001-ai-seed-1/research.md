# Research: AI Chat Service with Doubao Seed 1.6

## Research Tasks

### 1. Doubao Seed 1.6 API Integration

**Decision**: Use Doubao (ByteDance Volcano Engine) SDK for Python
- **SDK**: `volcengine-python-sdk` or direct REST API calls
- **Authentication**: API key via environment variable
- **Endpoint**: Volcano Engine LLM API (https://www.volcengine.com/docs/82379/1099475)
- **Streaming**: Support SSE (Server-Sent Events) for token streaming

**Rationale**:
- Official SDK provides better error handling and retry logic
- Streaming support essential for 6-second first-token requirement
- API key auth simplifies deployment (no OAuth complexity)

**Alternatives Considered**:
- Direct HTTP client (httpx/aiohttp): Rejected - reinventing retry/error handling
- Wrapper library: None found specific to Doubao Seed 1.6

**Implementation Notes**:
- Configure 6-second connection timeout
- Handle rate limit errors (HTTP 429) with meaningful messages
- Stream responses using async iteration
- Context format: Array of {role: "user"/"assistant", content: "..."}

---

### 2. Mustache Template Engine

**Decision**: Use `pystache` library (pure Python Mustache implementation)
- **Library**: `pystache==0.6.5`
- **Syntax**: Standard Mustache {{variable}} interpolation
- **Escaping**: Use raw/unescaped mode for system prompts (no HTML escaping needed)

**Rationale**:
- Lightweight (no dependencies)
- Mature library (stable API, well-tested)
- Handles edge cases (missing vars, nested objects, special chars)

**Alternatives Considered**:
- `chevron`: Rejected - less actively maintained
- `mustache`: Rejected - requires Node.js
- String formatting (f-strings): Rejected - doesn't handle missing variables gracefully

**Implementation Notes**:
- Missing variables → empty string (pystache default behavior)
- Variables must be strings (validate in CreateSessionRequest)
- Template stored as-is in session, rendered version in resolved_system_prompt

---

### 3. Async File I/O for JSON Storage

**Decision**: Use `aiofiles` for non-blocking file writes
- **Library**: `aiofiles==23.2.1`
- **Encoding**: UTF-8 with ensure_ascii=False for Chinese characters
- **Format**: json.dumps with indent=2 for pretty-printing

**Rationale**:
- PR-003 requirement: File writes must not block chat responses
- Async I/O prevents blocking event loop during file writes
- UTF-8 encoding ensures Chinese text renders correctly

**Alternatives Considered**:
- ThreadPoolExecutor: Rejected - more complex than aiofiles
- Synchronous writes: Rejected - violates PR-003

**Implementation Notes**:
- Write to temp file, then atomic rename (prevent corruption)
- Create ./conversations/ directory on startup if not exists
- Filename: {timestamp}_{session_id}.json for chronological sorting
- Handle disk full errors gracefully (log error, don't crash)

---

### 4. Concurrent Message Queuing

**Decision**: Use `asyncio.Queue` per session for message serialization
- **Pattern**: One queue per session_id in SessionManager
- **Behavior**: FIFO processing of messages to same session
- **Concurrency**: Different sessions process in parallel

**Rationale**:
- FR-022 requirement: Queue concurrent messages to same session
- asyncio.Queue provides async-safe FIFO semantics
- No external dependencies (built-in Python)

**Alternatives Considered**:
- asyncio.Lock: Rejected - doesn't provide queuing, just mutual exclusion
- Redis queue: Rejected - over-engineering for ephemeral sessions
- Threading queue: Rejected - incompatible with async/await

**Implementation Notes**:
- Queue created when session is created
- Queue removed when session is deleted
- Worker task per queue processes messages sequentially
- Timeout on queue.get() to detect stuck sessions

---

### 5. Session Storage (In-Memory)

**Decision**: Python dict {session_id: Session} with threading/async safety
- **Data Structure**: `Dict[str, Session]` in SessionManager
- **Concurrency**: Use asyncio.Lock for session CRUD operations
- **Lifecycle**: Sessions exist only in process memory (FR-023)

**Rationale**:
- Simplest solution for ephemeral sessions
- No DB overhead, fast lookups O(1)
- Lock prevents race conditions during session creation/deletion

**Alternatives Considered**:
- Redis: Rejected - sessions are ephemeral, no need for persistence
- SQLite: Rejected - over-engineering for memory-only requirement
- No lock: Rejected - race conditions on concurrent creates

**Implementation Notes**:
- Lock held only during session mutations, not during message processing
- UUIDs generated via `uuid.uuid4().hex`
- Session capacity limit (50) enforced before creating new session
- Cleanup: No TTL needed (sessions deleted explicitly via API)

---

### 6. FastAPI Best Practices

**Decision**: Follow FastAPI recommended patterns
- **Routers**: Single APIRouter in routes/chat_api.py
- **Dependency Injection**: SessionManager as app.state dependency
- **Validation**: Pydantic models for all request/response schemas
- **Error Handling**: HTTPException with status codes + detail messages

**Rationale**:
- Pydantic provides automatic validation (FR-014: reject empty messages)
- Dependency injection simplifies testing (mock SessionManager)
- Standard FastAPI patterns aid maintainability

**Alternatives Considered**:
- Flask: Rejected - less type safety, no async built-in
- Django: Rejected - too heavyweight for API-only service
- Raw ASGI: Rejected - reinventing FastAPI features

**Implementation Notes**:
- Use `@app.on_event("startup")` to initialize ./conversations/ directory
- Health endpoint: GET /health returns {"status": "ok", "doubao_connected": bool}
- CORS middleware if frontend integration needed (not in scope)
- Logging middleware for request/response logging

---

### 7. Testing Strategy

**Decision**: pytest + httpx TestClient + pytest-asyncio
- **Contract Tests**: httpx.TestClient for API endpoint validation
- **Integration Tests**: Full workflows with mock Doubao responses
- **Unit Tests**: Pure functions (template engine, context window logic)

**Rationale**:
- TestClient provides ASGI app testing without running server
- pytest-asyncio handles async test functions
- Mocking Doubao API avoids external dependencies in tests

**Alternatives Considered**:
- unittest: Rejected - pytest has better async support
- Postman/Newman: Rejected - harder to integrate with CI
- End-to-end tests: Deferred - require real Doubao API key

**Implementation Notes**:
- Fixtures: Mock Doubao client, temporary conversations directory
- Contract tests verify HTTP status codes, response schemas
- Integration tests use recorded Doubao responses (vcr.py or manual mocks)
- Performance tests: asyncio.gather for concurrent session load testing

---

### 8. Configuration Management

**Decision**: Environment variables + pydantic Settings
- **Library**: pydantic-settings for typed config
- **Variables**: DOUBAO_API_KEY, DOUBAO_API_ENDPOINT, MAX_SESSIONS (default 50)
- **Validation**: Settings model validates at startup

**Rationale**:
- 12-factor app principle (config via env)
- Type-safe config with validation
- Easy to override in tests

**Alternatives Considered**:
- Config file (YAML/TOML): Rejected - env vars simpler for single deployment
- python-decouple: Rejected - pydantic-settings more type-safe

**Implementation Notes**:
- .env.example committed to repo (without actual key)
- python-dotenv for local development
- Fail fast on startup if DOUBAO_API_KEY missing

---

### 9. Logging Configuration

**Decision**: Python logging with JSON formatter for structured logs
- **Format**: JSON lines with timestamp, level, session_id, message
- **Levels**: DEBUG (context window), INFO (requests), WARN (rate limits), ERROR (failures)
- **Output**: stdout (container-friendly)

**Rationale**:
- Principle VI: Structured logging required
- JSON format enables log aggregation (ELK, Datadog)
- Stdout follows 12-factor app logging

**Alternatives Considered**:
- python-json-logger: Considered - good option
- structlog: Rejected - more complex than needed
- Plain text logs: Rejected - harder to parse programmatically

**Implementation Notes**:
- Never log user messages (may contain PII)
- Log session_id in all request logs for tracing
- Sensitive data filters (ensure no API keys in logs)

---

### 10. Error Handling Patterns

**Decision**: Layered error handling with custom exceptions
- **HTTP Layer**: HTTPException with status codes (400, 404, 429, 500, 503)
- **Service Layer**: Custom exceptions (SessionNotFound, DoubaAPIError, RateLimitExceeded)
- **Client Layer**: Catch httpx exceptions, wrap in DoubaAPIError

**Rationale**:
- FR-013: Graceful error handling required
- Custom exceptions provide semantic meaning
- HTTP status codes follow REST semantics

**Error Scenarios**:
- 400: Invalid request (empty message, invalid variables)
- 404: Session not found
- 429: Doubao rate limit exceeded (propagate with retry-after header)
- 500: Internal server error (unhandled exceptions)
- 503: Doubao API unavailable (connection timeout)

**Implementation Notes**:
- Global exception handler for unhandled exceptions
- Error responses include {"error": "...", "detail": "...", "session_id": "..."}
- Doubao errors logged at ERROR level with stack trace

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Web Framework | FastAPI | 0.104+ | Async support, type safety, auto docs |
| Template Engine | pystache | 0.6.5 | Pure Python Mustache implementation |
| Doubao Client | volcengine-sdk | latest | Official SDK, streaming support |
| Async I/O | aiofiles | 23.2.1 | Non-blocking file writes |
| Testing | pytest + httpx | latest | Async testing, ASGI client |
| Validation | pydantic | 2.0+ | Request/response validation |
| Configuration | pydantic-settings | latest | Type-safe env var config |
| Logging | python-json-logger | latest | Structured JSON logs |

**All Unknowns Resolved**: No NEEDS CLARIFICATION markers remaining in Technical Context.

---

## Next Steps

1. ✅ Research complete
2. → Proceed to Phase 1: Design & Contracts
   - Generate data-model.md (Session, MessageRound entities)
   - Generate API contracts (OpenAPI specs for 5 endpoints)
   - Generate quickstart.md (API usage examples)
   - Generate failing contract tests

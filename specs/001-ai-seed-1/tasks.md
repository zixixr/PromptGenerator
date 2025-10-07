# Tasks: AI Chat Service with Doubao Seed 1.6

**Input**: Design documents from `D:\AIDev\PromptGenerator\specs\001-ai-seed-1\`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   â†?Extract: Python 3.11+, FastAPI, pystache, volcengine-sdk, aiofiles, pytest
2. Load design documents:
   â†?data-model.md: Session, MessageRound, HistoryFile entities
   â†?contracts/: 5 OpenAPI spec files (create_session, send_message, get_history, list_sessions, delete_session)
   â†?quickstart.md: 6 usage examples, 4 test scenarios
3. Generate tasks by category:
   â†?Setup: project init, dependencies, linting, directory structure
   â†?Tests: contract tests (5), integration tests (5)
   â†?Core: models (3), services (4), routes (1)
   â†?Integration: config, logging, file storage, main app
   â†?Polish: unit tests (4), performance tests, documentation
4. Apply task rules:
   â†?Different files = mark [P] for parallel
   â†?Same file = sequential (no [P])
   â†?Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Project root**: `D:\AIDev\PromptGenerator\`
- **Source code**: `src/` (models, services, routes)
- **Tests**: `tests/` (contract, integration, unit)
- **Config**: Repository root (requirements.txt, pytest.ini, .env.example)

---

## Phase 3.1: Setup

- [X] **T001** Create project directory structure (src/, tests/, conversations/)
  - Create `D:\AIDev\PromptGenerator\src\models\`
  - Create `D:\AIDev\PromptGenerator\src\services\`
  - Create `D:\AIDev\PromptGenerator\src\routes\`
  - Create `D:\AIDev\PromptGenerator\tests\contract\`
  - Create `D:\AIDev\PromptGenerator\tests\integration\`
  - Create `D:\AIDev\PromptGenerator\tests\unit\`
  - Create `D:\AIDev\PromptGenerator\conversations\` (runtime directory)

- [X] **T002** Initialize Python project with dependencies in `requirements.txt`
  ```
  fastapi>=0.104.0
  uvicorn[standard]>=0.24.0
  pydantic>=2.0.0
  pydantic-settings>=2.0.0
  pystache>=0.6.5
  volcengine-python-sdk>=1.0.0
  aiofiles>=23.2.1
  httpx>=0.25.0
  pytest>=7.4.0
  pytest-asyncio>=0.21.0
  python-dotenv>=1.0.0
  python-json-logger>=2.0.0
  ```

- [X] **T003** [P] Configure pytest in `pytest.ini`
  ```ini
  [pytest]
  asyncio_mode = auto
  testpaths = tests
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*
  addopts = -v --tb=short
  ```

- [X] **T004** [P] Create `.env.example` with environment variable template
  ```
  DOUBAO_API_KEY=your_api_key_here
  DOUBAO_API_ENDPOINT=https://ark.cn-beijing.volces.com/api/v3/chat/completions
  MAX_SESSIONS=50
  CONVERSATIONS_DIR=./conversations
  ```

- [X] **T005** [P] Configure linting with `.flake8` or `pyproject.toml`
  - Max line length: 100
  - Exclude: venv/, __pycache__, .git/

---

## Phase 3.2: Tests First (TDD) âš ï¸ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (One per API endpoint)

- [X] **T006** [P] Contract test POST /sessions in `tests/contract/test_create_session.py`
  - Test 201 response with session_id, resolved_system_prompt, created_at
  - Test 400 for empty system_prompt_template
  - Test 503 when max sessions (50) reached
  - Validate response schema matches `contracts/create_session.yaml`

- [X] **T007** [P] Contract test POST /sessions/{id}/messages in `tests/contract/test_send_message.py`
  - Test 200 response with round_number, user_message, assistant_response, timestamp
  - Test 400 for empty/whitespace message
  - Test 404 for non-existent session
  - Test 429 for Doubao rate limit (mocked)
  - Test 503 for Doubao API unavailable (mocked)
  - Validate response schema matches `contracts/send_message.yaml`

- [X] **T008** [P] Contract test GET /sessions/{id}/history in `tests/contract/test_get_history.py`
  - Test 200 response with full session data (system prompts, variables, rounds)
  - Test 404 for non-existent session
  - Validate response schema matches `contracts/get_history.yaml`

- [X] **T009** [P] Contract test GET /sessions in `tests/contract/test_list_sessions.py`
  - Test 200 response with sessions array and total count
  - Test empty array when no sessions
  - Validate response schema matches `contracts/list_sessions.yaml`

- [X] **T010** [P] Contract test DELETE /sessions/{id} in `tests/contract/test_delete_session.py`
  - Test 204 response (no content)
  - Test 404 for non-existent session
  - Test idempotency (second delete returns 404)
  - Validate response schema matches `contracts/delete_session.yaml`

### Integration Tests (From quickstart scenarios)

- [ ] **T011** [P] Integration test: Session workflow in `tests/integration/test_session_workflow.py`
  - Create session â†?Send 2 messages â†?Get history â†?Delete session
  - Assert session_id consistency across requests
  - Assert round numbers increment correctly (1, 2)
  - Assert last_activity updates after each message
  - Validate JSON history file created in `./conversations/`

- [ ] **T012** [P] Integration test: Sliding window (10-round context) in `tests/integration/test_sliding_window.py`
  - Create session
  - Send 12 messages
  - Mock Doubao API to capture context sent (use pytest-mock or unittest.mock)
  - Assert message 13 context includes only rounds 3-12 (last 10)
  - Assert rounds 1-2 excluded from context

- [ ] **T013** [P] Integration test: Mustache variable substitution in `tests/integration/test_variable_substitution.py`
  - Test normal substitution: `{{role}}` â†?"helpful"
  - Test missing variable: `{{expertise}}` â†?"" (empty string)
  - Test multiple variables: `{{role}}` + `{{domain}}` + `{{tone}}`
  - Test no variables (plain text prompt)
  - Assert resolved_system_prompt matches expected output

- [ ] **T014** [P] Integration test: Concurrent message queuing in `tests/integration/test_concurrent_messages.py`
  - Create session
  - Send 3 concurrent messages using asyncio.gather()
  - Assert all 3 messages processed (round_numbers 1, 2, 3)
  - Assert FIFO order maintained (check timestamps or mock Doubao API call order)
  - Assert no race conditions (e.g., duplicate round numbers)

- [ ] **T015** [P] Integration test: Error handling in `tests/integration/test_error_handling.py`
  - Test empty message (400)
  - Test session not found (404)
  - Test capacity limit (create 51 sessions, expect 503 on 51st)
  - Test Doubao API timeout (mock 6-second timeout, expect 503)
  - Assert error responses include error, detail, session_id fields

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Models (Data structures with Pydantic)

- [X] **T016** [P] Create Session and MessageRound models in `src/models/session.py`
  - Session class with fields: session_id, system_prompt_template, resolved_system_prompt, variables, rounds (List[MessageRound]), message_queue, created_at, last_activity
  - MessageRound class with fields: round_number, user_message, assistant_response, timestamp
  - Use pydantic BaseModel for validation
  - UUID generation for session_id (uuid.uuid4().hex)
  - Datetime fields use datetime.now(timezone.utc)

- [X] **T017** [P] Create request models in `src/models/requests.py`
  - CreateSessionRequest: system_prompt_template (str, min_length=1), variables (Dict[str, str], default={})
  - SendMessageRequest: message (str, min_length=1, strip whitespace)
  - Pydantic validation: reject empty strings, non-string variables

- [X] **T018** [P] Create response models in `src/models/responses.py`
  - CreateSessionResponse: session_id, resolved_system_prompt, created_at
  - SendMessageResponse: session_id, round_number, user_message, assistant_response, timestamp
  - GetHistoryResponse: all Session fields + rounds array
  - ListSessionsResponse: sessions (array of summary objects), total (int)
  - ErrorResponse: error (str), detail (str), session_id (optional str)

### Services (Business logic)

- [X] **T019** Template engine service in `src/services/template_engine.py`
  - TemplateEngine class
  - Method: render(template: str, variables: Dict[str, str]) -> str
  - Use pystache.render() for Mustache substitution
  - Missing variables â†?empty string (pystache default)
  - Handle edge cases: no variables, special chars in variable names

- [X] **T020** Doubao API client service in `src/services/doubao_client.py`
  - DoubaClient class (async)
  - Method: send_message(system_prompt: str, context: List[Dict], user_message: str, timeout: int = 6) -> str
  - Use volcengine-sdk or httpx for API calls
  - Handle streaming response (SSE) if supported
  - Timeout after 6 seconds for first token
  - Raise RateLimitExceeded on HTTP 429
  - Raise ServiceUnavailable on connection timeout
  - Return assistant response as string

- [X] **T021** File storage service in `src/services/file_storage.py`
  - FileStorage class (async)
  - Method: save_history(session: Session, directory: str = "./conversations") -> None
  - Use aiofiles for async file I/O
  - Filename: `{timestamp}_{session_id}.json` (YYYYMMDDHHmmss format)
  - JSON encoding: UTF-8, ensure_ascii=False, indent=2 (pretty-printed)
  - Atomic write: temp file + rename to prevent corruption
  - Create directory if not exists
  - Handle errors: log but don't raise (non-blocking)

- [X] **T022** Session manager service in `src/services/session_manager.py`
  - SessionManager class
  - In-memory storage: Dict[str, Session]
  - asyncio.Lock for thread-safe CRUD operations
  - Methods:
    * create_session(template: str, variables: Dict[str, str]) -> Session
      - Generate UUID for session_id
      - Render template using TemplateEngine
      - Initialize empty rounds list
      - Create asyncio.Queue for message_queue
      - Check capacity limit (MAX_SESSIONS from config)
      - Raise ServiceUnavailable if capacity reached
    * get_session(session_id: str) -> Session
      - Raise SessionNotFound if not exists
    * list_sessions() -> List[Session]
    * delete_session(session_id: str) -> None
      - Raise SessionNotFound if not exists
    * send_message(session_id: str, message: str) -> MessageRound
      - Get session (raise SessionNotFound)
      - Queue message on session.message_queue
      - Worker processes queue sequentially
      - Build Doubao context (system + last 10 rounds + new message)
      - Call DoubaClient.send_message()
      - Create MessageRound, append to session.rounds
      - Update session.last_activity
      - Save history via FileStorage (async, non-blocking)
      - Return MessageRound

### Routes (FastAPI endpoints)

- [X] **T023** API routes in `src/routes/chat_api.py`
  - POST /sessions (create_session endpoint)
    - Request: CreateSessionRequest
    - Response: CreateSessionResponse (HTTP 201)
    - Errors: 400 (validation), 503 (capacity)
  - POST /sessions/{session_id}/messages (send_message endpoint)
    - Request: SendMessageRequest
    - Response: SendMessageResponse (HTTP 200)
    - Errors: 400 (empty message), 404 (session not found), 429 (rate limit), 503 (Doubao unavailable)
  - GET /sessions/{session_id}/history (get_history endpoint)
    - Response: GetHistoryResponse (HTTP 200)
    - Errors: 404 (session not found)
  - GET /sessions (list_sessions endpoint)
    - Response: ListSessionsResponse (HTTP 200)
  - DELETE /sessions/{session_id} (delete_session endpoint)
    - Response: HTTP 204 No Content
    - Errors: 404 (session not found)
  - Use dependency injection for SessionManager (app.state.session_manager)
  - Global exception handler for unhandled errors (HTTP 500)

---

## Phase 3.4: Integration

- [X] **T024** Configuration management in `src/config.py`
  - Use pydantic-settings BaseSettings
  - Fields: DOUBAO_API_KEY (required), DOUBAO_API_ENDPOINT (required), MAX_SESSIONS (default=50), CONVERSATIONS_DIR (default="./conversations")
  - Load from .env file (use python-dotenv)
  - Validate on app startup (fail fast if DOUBAO_API_KEY missing)

- [X] **T025** Logging configuration in `src/logging_config.py`
  - Use python-json-logger for structured JSON logs
  - Format: {"timestamp": "...", "level": "...", "session_id": "...", "message": "..."}
  - Levels: DEBUG (context window), INFO (requests), WARN (rate limits), ERROR (failures)
  - Output: stdout (container-friendly)
  - Never log user messages or API keys
  - Log session_id in all request logs

- [X] **T026** Main FastAPI app in `src/main.py`
  - Create FastAPI app
  - Include chat_api router
  - Add startup event handler:
    * Initialize SessionManager as app.state.session_manager
    * Create ./conversations/ directory if not exists
    * Load config and validate
  - Add health endpoint: GET /health â†?{"status": "ok", "doubao_connected": bool}
  - Add CORS middleware if needed (not in scope, comment placeholder)
  - Add logging middleware for request/response logging

---

## Phase 3.5: Polish

### Unit Tests (Pure functions and components)

- [ ] **T027** [P] Unit tests for template engine in `tests/unit/test_template_engine.py`
  - Test normal variable substitution
  - Test missing variables â†?empty string
  - Test multiple variables
  - Test no variables (plain text)
  - Test special characters in variable names (dots, dashes)

- [ ] **T028** [P] Unit tests for session manager in `tests/unit/test_session_manager.py`
  - Test create_session (UUID generation, template rendering)
  - Test get_session (success, SessionNotFound)
  - Test list_sessions (empty, multiple sessions)
  - Test delete_session (success, SessionNotFound, idempotency)
  - Test capacity limit (create 51 sessions, expect error)
  - Mock DoubaClient and FileStorage

- [ ] **T029** [P] Unit tests for file storage in `tests/unit/test_file_storage.py`
  - Test save_history (file created, UTF-8 encoding, pretty-printed)
  - Test filename format (timestamp_sessionid.json)
  - Test directory creation
  - Test error handling (disk full, permission denied) - assert logs error, doesn't raise
  - Use temp directory for tests (pytest tmpdir fixture)

- [ ] **T030** [P] Unit tests for Doubao client in `tests/unit/test_doubao_client.py`
  - Test successful API call (mock response)
  - Test timeout after 6 seconds (mock delay)
  - Test rate limit (HTTP 429, raise RateLimitExceeded)
  - Test API unavailable (connection error, raise ServiceUnavailable)
  - Test context format (system + last 10 rounds + user message)
  - Use httpx.AsyncClient with mocked responses

### Performance & Documentation

- [ ] **T031** Performance tests in `tests/integration/test_performance.py`
  - Test 6-second first-token timeout (mock Doubao API with delay)
  - Test concurrent session capacity (create 50 sessions, assert all succeed)
  - Test file I/O non-blocking (send message, assert response < file write time)
  - Use asyncio.gather for concurrent operations

- [X] **T032** [P] Update README.md with:
  - Project description
  - Setup instructions (install dependencies, configure .env)
  - Run server: `uvicorn src.main:app --reload`
  - Run tests: `pytest tests/`
  - API documentation link: `http://localhost:8000/docs`

- [ ] **T033** [P] Verify quickstart examples in `quickstart.md`
  - Manually test all 6 examples (simple conversation, variables, missing vars, history, list, delete)
  - Verify all 4 test scenarios work (sliding window, concurrency, capacity, error handling)
  - Check JSON history files in ./conversations/
  - Update examples if API responses differ

---

## Dependencies

**Setup â†?Tests â†?Implementation â†?Integration â†?Polish**

```
T001-T005 (Setup)
    â†?T006-T015 (Tests) [All in parallel, no dependencies]
    â†?T016-T018 (Models) [All in parallel]
    â†?T019 (TemplateEngine)
    â†?T020, T021 (DoubaClient, FileStorage) [Parallel]
    â†?T022 (SessionManager) - depends on T019, T020, T021
    â†?T023 (Routes) - depends on T022
    â†?T024-T026 (Integration) [Sequential: Config â†?Logging â†?Main]
    â†?T027-T033 (Polish) [All in parallel except T033 depends on T001-T026]
```

**Critical Path**: T001 â†?T006-T015 â†?T016-T022 â†?T023 â†?T024-T026 â†?T033

---

## Parallel Execution Examples

### Example 1: Run all contract tests in parallel
```bash
# After setup (T001-T005), run all contract tests together:
pytest tests/contract/ -v -n auto  # pytest-xdist for parallel execution

# Or manually:
pytest tests/contract/test_create_session.py &
pytest tests/contract/test_send_message.py &
pytest tests/contract/test_get_history.py &
pytest tests/contract/test_list_sessions.py &
pytest tests/contract/test_delete_session.py &
wait
```

### Example 2: Create all models in parallel (T016-T018)
Since these are independent files, they can be implemented simultaneously:
```
Task 1: Implement src/models/session.py
Task 2: Implement src/models/requests.py
Task 3: Implement src/models/responses.py
```

### Example 3: Run unit tests in parallel
```bash
pytest tests/unit/ -v -n auto

# Or:
pytest tests/unit/test_template_engine.py &
pytest tests/unit/test_session_manager.py &
pytest tests/unit/test_file_storage.py &
pytest tests/unit/test_doubao_client.py &
wait
```

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **TDD enforced**: All tests (T006-T015) must be written and failing before implementation (T016-T026)
- **Verify tests fail** before implementing
- **Commit after each task** for traceability
- **Mock Doubao API** in all tests (use pytest-mock, unittest.mock, or httpx mock transport)
- **Avoid**: Vague tasks, same-file conflicts, skipping tests

---

## Task Count Summary

- **Setup**: 5 tasks (T001-T005)
- **Contract Tests**: 5 tasks (T006-T010) [P]
- **Integration Tests**: 5 tasks (T011-T015) [P]
- **Models**: 3 tasks (T016-T018) [P]
- **Services**: 4 tasks (T019-T022)
- **Routes**: 1 task (T023)
- **Integration**: 3 tasks (T024-T026)
- **Unit Tests**: 4 tasks (T027-T030) [P]
- **Polish**: 3 tasks (T031-T033)

**Total**: 33 tasks

---

## Validation Checklist

*GATE: Checked before marking tasks.md complete*

- [x] All contracts have corresponding tests (T006-T010 â†?contracts/)
- [x] All entities have model tasks (T016 â†?Session, MessageRound from data-model.md)
- [x] All tests come before implementation (T006-T015 before T016-T026)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Dependencies documented (see Dependencies section)
- [x] TDD order enforced (tests first, implementation second)

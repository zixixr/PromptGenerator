
# Implementation Plan: AI Chat Service with Doubao Seed 1.6

**Branch**: `001-ai-seed-1` | **Date**: 2025-10-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `D:\AIDev\PromptGenerator\specs\001-ai-seed-1\spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code, or `AGENTS.md` for all other agents).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Build an AI chat service that connects to Doubao Seed 1.6 model, maintaining 10-round conversation context with Mustache-style variable interpolation in system prompts. The service provides REST API endpoints for session management and message exchange, persisting all conversations to local JSON files. Sessions are ephemeral (memory-only), support up to 50 concurrent conversations, and require no authentication.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (web framework), Mustache/Pystache (template engine), httpx/aiohttp (async HTTP client for Doubao API), pydantic (data validation)
**Storage**: Local filesystem (JSON files in `./conversations/` directory)
**Testing**: pytest (unit/integration), pytest-asyncio (async tests), httpx TestClient (API contract tests)
**Target Platform**: Linux/Windows server (cross-platform Python service)
**Project Type**: single (backend API service)
**Performance Goals**: 6-second timeout for first token, 50 concurrent sessions, streaming response support
**Constraints**: Ephemeral sessions (no persistence across restarts), no authentication, UTF-8 encoding for Chinese text support
**Scale/Scope**: Single service deployment, ~500 LOC core logic, 5 REST endpoints, local file-based history storage

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on `.specify/memory/constitution.md`, verify:

### Principle I: Code Quality First
- [x] Architecture promotes single-responsibility modules (SessionManager, TemplateEngine, DoubaClient, FileStorage)
- [x] Design avoids unnecessary complexity (direct FastAPI routes, simple in-memory dict for sessions)
- [x] Code structure will be reviewable and maintainable (clear separation: routes, services, models, storage)

### Principle II: Test-Driven Development (NON-NEGOTIABLE)
- [x] Contract tests planned for all API boundaries (5 endpoints: POST /sessions, POST /sessions/{id}/messages, GET /sessions/{id}/history, GET /sessions, DELETE /sessions/{id})
- [x] Integration tests planned for user workflows (session creation → multi-turn chat → history retrieval)
- [x] Unit tests planned for complex logic (Mustache substitution, sliding window context, queue management)
- [x] Tests will be written BEFORE implementation (TDD enforced in Phase 1)

### Principle III: User Experience Consistency
- [x] UI patterns align with existing application conventions (REST API follows standard HTTP semantics)
- [x] Accessibility requirements defined (API-only service, JSON responses with clear structure)
- [x] Cross-platform compatibility addressed (Python 3.11+ cross-platform)
- [x] Error messages are user-friendly and actionable (PR-019: meaningful error messages for rate limits, validation failures)

### Principle IV: Performance Requirements
- [x] Explicit response time targets defined (6-second timeout for first token, streaming thereafter)
- [x] Resource constraints specified (50 concurrent sessions, async I/O for file writes)
- [x] Scalability expectations documented (ephemeral sessions, no DB overhead, local file storage)
- [x] Performance tests planned (validate 6s first-token timeout, concurrent session capacity, non-blocking file I/O)

### Principle V: Simplicity Over Cleverness
- [x] Solution is the simplest that meets requirements (no database, no complex state machine, simple dict-based session storage)
- [x] Complex patterns justified in writing (async queue for concurrent message handling - justified by FR-022)
- [x] YAGNI principle applied (no authentication, no multi-tenancy, no session persistence)
- [x] No over-engineering detected (direct API-to-Doubao calls, no unnecessary abstraction layers)

### Principle VI: Observability & Debugging
- [x] Structured logging planned with appropriate levels (INFO: requests, WARN: rate limits, ERROR: API failures, DEBUG: context window)
- [x] Request tracing considered for distributed operations (session_id in all logs, request_id for correlation)
- [x] Error handling provides clear context (FR-013: graceful error handling with meaningful messages)
- [x] Health checks planned (GET /health endpoint for service status, Doubao API connectivity check)
- [x] No sensitive data in logs (system prompts may contain user data, log only session IDs and metadata)

**Violations**: None - all constitutional principles satisfied

**Initial Constitution Check**: ✅ PASS

## Project Structure

### Documentation (this feature)
```
specs/001-ai-seed-1/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   ├── create_session.yaml
│   ├── send_message.yaml
│   ├── get_history.yaml
│   ├── list_sessions.yaml
│   └── delete_session.yaml
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── models/
│   ├── session.py       # Session, MessageRound, TemplateContext
│   ├── requests.py      # CreateSessionRequest, SendMessageRequest
│   └── responses.py     # SessionResponse, MessageResponse, HistoryResponse
├── services/
│   ├── session_manager.py    # SessionManager (CRUD, concurrent message queue)
│   ├── template_engine.py    # Mustache variable substitution
│   ├── doubao_client.py      # Doubao Seed 1.6 API client (async)
│   └── file_storage.py       # JSON file persistence (async)
├── routes/
│   └── chat_api.py      # FastAPI routes (5 endpoints)
├── config.py            # Configuration (Doubao API key, timeouts, paths)
├── logging_config.py    # Structured logging setup
└── main.py              # FastAPI app entry point

tests/
├── contract/
│   ├── test_create_session.py
│   ├── test_send_message.py
│   ├── test_get_history.py
│   ├── test_list_sessions.py
│   └── test_delete_session.py
├── integration/
│   ├── test_session_workflow.py      # Full session lifecycle
│   ├── test_sliding_window.py        # 10-round context window
│   └── test_concurrent_messages.py   # Message queuing
└── unit/
    ├── test_template_engine.py       # Mustache substitution
    ├── test_session_manager.py       # Session management logic
    ├── test_file_storage.py          # JSON serialization
    └── test_doubao_client.py         # Mock API responses

conversations/           # Generated at runtime (JSON history files)

requirements.txt         # Python dependencies
pytest.ini              # Pytest configuration
.env.example            # Example environment variables (Doubao API key)
```

**Structure Decision**: Single project (backend API service). Using FastAPI's recommended structure with separation of concerns: models (data), services (business logic), routes (HTTP layer), and tests (contract/integration/unit). The `conversations/` directory will be created automatically at runtime for JSON file storage.

## Phase 0: Outline & Research

**Status**: ✅ Complete

### Research Areas
1. ✅ Doubao Seed 1.6 API Integration (volcengine-sdk, streaming, auth)
2. ✅ Mustache Template Engine (pystache library)
3. ✅ Async File I/O (aiofiles for non-blocking writes)
4. ✅ Concurrent Message Queuing (asyncio.Queue per session)
5. ✅ Session Storage (in-memory dict with asyncio.Lock)
6. ✅ FastAPI Best Practices (routers, dependency injection, validation)
7. ✅ Testing Strategy (pytest + httpx TestClient + pytest-asyncio)
8. ✅ Configuration Management (pydantic-settings + env vars)
9. ✅ Logging Configuration (JSON structured logging)
10. ✅ Error Handling Patterns (layered exceptions, HTTP status codes)

### Key Decisions
- **Web Framework**: FastAPI 0.104+ (async, type-safe, auto docs)
- **Template Engine**: pystache 0.6.5 (pure Python, handles missing vars)
- **Doubao Client**: volcengine-sdk (official, streaming support)
- **File I/O**: aiofiles 23.2.1 (non-blocking, UTF-8 pretty-printed JSON)
- **Concurrency**: asyncio.Queue per session (FIFO message processing)
- **Storage**: Dict[str, Session] with asyncio.Lock (ephemeral, O(1) lookup)
- **Testing**: pytest + httpx.TestClient (contract/integration/unit)
- **Config**: pydantic-settings (type-safe env vars)
- **Logging**: JSON formatter to stdout (structured, container-friendly)

**Output**: [research.md](./research.md) - All technical decisions documented with rationale

## Phase 1: Design & Contracts

**Status**: ✅ Complete

### Deliverables Generated

1. **Data Model** → [data-model.md](./data-model.md)
   - Core Entities: Session, MessageRound, HistoryFile
   - Supporting Models: TemplateContext, DoubaoContext
   - API Request/Response Models (5 endpoints)
   - Entity relationships diagram
   - Business rules and constraints

2. **API Contracts** → [contracts/](./contracts/)
   - ✅ [create_session.yaml](./contracts/create_session.yaml) - POST /sessions
   - ✅ [send_message.yaml](./contracts/send_message.yaml) - POST /sessions/{id}/messages
   - ✅ [get_history.yaml](./contracts/get_history.yaml) - GET /sessions/{id}/history
   - ✅ [list_sessions.yaml](./contracts/list_sessions.yaml) - GET /sessions
   - ✅ [delete_session.yaml](./contracts/delete_session.yaml) - DELETE /sessions/{id}

   All contracts follow OpenAPI 3.0.3 spec with:
   - Request/response schemas
   - Validation rules
   - Error responses (400, 404, 429, 503)
   - Example payloads

3. **Quickstart Guide** → [quickstart.md](./quickstart.md)
   - Setup instructions (dependencies, env config)
   - 6 usage examples (simple conversation, variables, missing vars, history, list, delete)
   - 4 testing scenarios (sliding window, concurrency, capacity limit, error handling)
   - JSON history file format
   - Debugging tips

### Contract Test Plan (To be implemented in Phase 3/4)

**Test Files** (following TDD - write tests first):
```
tests/contract/
├── test_create_session.py      # Validate POST /sessions
├── test_send_message.py         # Validate POST /sessions/{id}/messages
├── test_get_history.py          # Validate GET /sessions/{id}/history
├── test_list_sessions.py        # Validate GET /sessions
└── test_delete_session.py       # Validate DELETE /sessions/{id}
```

**Test Assertions** (per contract):
- HTTP status codes (201, 200, 204, 400, 404, 429, 503)
- Response schema matches OpenAPI spec
- Required fields present
- Field types correct (string, int, datetime)
- Error responses include error/detail/session_id

### Integration Test Scenarios (From Acceptance Scenarios)

**Test Files**:
```
tests/integration/
├── test_session_workflow.py        # Scenario 1-2: Create → Send → Get history
├── test_sliding_window.py          # Scenario 3: 12 rounds, verify 10-round context
├── test_variable_substitution.py   # Scenario 5: Mustache template rendering
├── test_concurrent_messages.py     # Edge case: Concurrent messages queued
└── test_error_handling.py          # Edge cases: Missing session, empty message, etc.
```

### Agent File Update

Will run after Phase 1 verification:
```bash
.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

**Output**: Phase 1 design complete. Ready for Phase 2 task planning.

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking

**No constitutional violations detected**. All design choices align with constitutional principles:
- Simple in-memory dict storage (Principle V: Simplicity)
- Async queue justified by FR-022 (Principle V: Complex patterns justified)
- No over-engineering (no DB, no auth, no persistence layer)


## Progress Tracking

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command - next step)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved (no unknowns in Technical Context)
- [x] Complexity deviations documented (none - all choices justified)

**Artifacts Generated**:
- [x] research.md (10 technical decisions)
- [x] data-model.md (entities, relationships, validation rules)
- [x] contracts/ (5 OpenAPI specs)
- [x] quickstart.md (examples, test scenarios)
- [ ] CLAUDE.md (agent context file - to be generated)
- [ ] tasks.md (generated by /tasks command)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*

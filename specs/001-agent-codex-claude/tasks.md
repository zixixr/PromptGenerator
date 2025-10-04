# Tasks: Automated Prompt Iteration System

**Input**: Design documents from `D:\AIDev\PromptGenerator\specs\001-agent-codex-claude\`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: Python 3.11+ backend (FastAPI), React frontend, LangChain, SQLite
2. Load optional design documents:
   → data-model.md: 8 entities identified
   → contracts/: 2 OpenAPI specs (projects-api.yaml, iterations-api.yaml)
   → quickstart.md: 8 user scenarios + 3 edge cases
3. Generate tasks by category:
   → Setup: Backend/frontend init, dependencies, linting
   → Tests: 2 contract test suites, 8 integration tests
   → Core: 8 models, 4 services, API routes
   → Integration: Database, encryption, LLM providers
   → Polish: Unit tests, error handling, UI components
4. Apply task rules:
   → Different files = [P] for parallel
   → Tests before implementation (TDD)
5. Tasks numbered T001-T060
6. Dependencies tracked
7. Parallel execution examples provided
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Config**: `config/`
- **Data**: `data/`

---

## Phase 3.1: Setup

- [ ] **T001** Create project directory structure (backend/, frontend/, config/, data/)
- [ ] **T002** Initialize Python backend project with pyproject.toml (FastAPI, LangChain, SQLAlchemy, cryptography, pytest dependencies)
- [ ] **T003** Initialize React frontend project with package.json (TypeScript, React, Recharts, Axios, Jest, RTL dependencies)
- [ ] **T004** [P] Configure backend linting (ruff, black, mypy) in backend/pyproject.toml
- [ ] **T005** [P] Configure frontend linting (ESLint, Prettier) in frontend/.eslintrc.json
- [ ] **T006** [P] Create backend/src/__init__.py and module structure
- [ ] **T007** [P] Create frontend/src/index.tsx entry point
- [ ] **T008** Create config/default.yaml with default settings (iteration limits, timeouts)
- [ ] **T009** Create .gitignore for Python, Node, SQLite, credentials

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (based on contracts/)

- [ ] **T010** [P] Contract test suite for projects API in backend/tests/contract/test_projects_api.py (validates projects-api.yaml: POST/GET/DELETE /projects, POST /projects/{id}/iterations, POST /projects/{id}/export)
- [ ] **T011** [P] Contract test suite for iterations API in backend/tests/contract/test_iterations_api.py (validates iterations-api.yaml: GET /iterations/{id}, GET /iterations/{id}/conversations, GET /conversations/{id})

### Integration Tests (based on quickstart.md)

- [ ] **T012** [P] Integration test: Create and configure new project in backend/tests/integration/test_create_project.py (Test Scenario 1 from quickstart.md)
- [ ] **T013** [P] Integration test: Run iteration with failing criteria in backend/tests/integration/test_failing_iteration.py (Test Scenario 2 from quickstart.md)
- [ ] **T014** [P] Integration test: Complete successful optimization in backend/tests/integration/test_successful_optimization.py (Test Scenario 3 from quickstart.md)
- [ ] **T015** [P] Integration test: Configure custom evaluation criterion in backend/tests/integration/test_custom_criterion.py (Test Scenario 4 from quickstart.md)
- [ ] **T016** [P] Integration test: Manage multiple projects in backend/tests/integration/test_multiple_projects.py (Test Scenario 5 from quickstart.md)
- [ ] **T017** [P] Integration test: Handle max iteration limit in backend/tests/integration/test_max_iterations.py (Test Scenario 6 from quickstart.md)
- [ ] **T018** [P] Integration test: Handle API errors gracefully in backend/tests/integration/test_api_errors.py (Test Scenario 7 from quickstart.md)
- [ ] **T019** [P] Integration test: Export reports in JSON/CSV formats in backend/tests/integration/test_export_reports.py (Test Scenario 8 from quickstart.md)

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models (based on data-model.md: 8 entities)

- [ ] **T020** [P] Project model in backend/src/models/project.py (Pydantic + SQLAlchemy for Project entity: id, name, target_model, initial_prompt, max_iterations, status)
- [ ] **T021** [P] Iteration model in backend/src/models/iteration.py (Pydantic + SQLAlchemy for Iteration entity: id, project_id, iteration_number, status, started_at, completed_at, passed_criteria_count)
- [ ] **T022** [P] Prompt model in backend/src/models/prompt.py (Pydantic + SQLAlchemy for Prompt entity: id, text, parent_id, generation_method, rewrite_rationale)
- [ ] **T023** [P] TestScenario model in backend/src/models/test_scenario.py (Pydantic + SQLAlchemy for TestScenario entity: id, name, description, turn_limit, priority)
- [ ] **T024** [P] EvaluationCriterion model in backend/src/models/evaluation_criterion.py (Pydantic + SQLAlchemy for EvaluationCriterion entity: id, name, threshold, is_predefined, scoring_rubric)
- [ ] **T025** [P] Conversation model in backend/src/models/conversation.py (Pydantic + SQLAlchemy for Conversation entity: id, iteration_id, test_scenario_id, turns JSON, turn_count, status)
- [ ] **T026** [P] EvaluationResult model in backend/src/models/evaluation_result.py (Pydantic + SQLAlchemy for EvaluationResult entity: id, conversation_id, criterion_scores JSON, aggregate_score, passed)
- [ ] **T027** [P] ModelConfiguration model in backend/src/models/model_configuration.py (Pydantic + SQLAlchemy for ModelConfiguration entity: id, project_id, provider, model_name, temperature, max_tokens)

### Database and Storage

- [ ] **T028** Database initialization and migrations in backend/src/storage/db.py (SQLite connection, Alembic setup, create_all tables)
- [ ] **T029** Credential encryption/decryption service in backend/src/storage/encryption.py (Fernet symmetric encryption for LLM API keys per research.md)

### Core Services (based on research.md architecture)

- [ ] **T030** Conversation simulator service in backend/src/services/simulator.py (LLM-based user message generation, multi-turn conversation orchestration, turn limit enforcement)
- [ ] **T031** Evaluation service in backend/src/services/evaluator.py (LLM-based scoring against criteria, structured JSON score + explanation generation, score averaging across scenarios)
- [ ] **T032** Prompt rewriter service in backend/src/services/rewriter.py (LLM-based prompt improvement using evaluation feedback, version lineage tracking via parent_id)
- [ ] **T033** Iteration orchestrator service in backend/src/services/orchestrator.py (Coordinate simulate → evaluate → rewrite loop, check independent thresholds per FR-010, handle max iteration limit)

### LLM Provider Integration

- [ ] **T034** LLM provider factory in backend/src/llm/providers.py (LangChain abstraction for OpenAI, Anthropic, Google, custom endpoints, retry logic with exponential backoff per FR-047)

### API Endpoints (based on contracts/)

- [ ] **T035** Projects CRUD routes in backend/src/api/projects.py (POST /projects, GET /projects, GET /projects/{id}, DELETE /projects/{id})
- [ ] **T036** Iteration execution routes in backend/src/api/projects.py (POST /projects/{id}/iterations with async background task)
- [ ] **T037** Export routes in backend/src/api/projects.py (POST /projects/{id}/export for JSON/CSV formats per FR-032)
- [ ] **T038** Iterations detail routes in backend/src/api/iterations.py (GET /iterations/{id}, GET /iterations/{id}/conversations)
- [ ] **T039** Conversations detail routes in backend/src/api/iterations.py (GET /conversations/{id} with full transcript)

### FastAPI Application Setup

- [ ] **T040** FastAPI application factory in backend/src/main.py (app initialization, CORS middleware, router registration, error handlers)

---

## Phase 3.4: Integration

- [ ] **T041** Connect services to database in backend/src/storage/db.py (Session management, query helpers for Project, Iteration, Conversation CRUD)
- [ ] **T042** Implement API request/response logging middleware in backend/src/api/middleware.py (Log all API calls, errors per FR-044)
- [ ] **T043** Implement error handling and structured error responses in backend/src/api/errors.py (Error schemas matching contracts/, recovery guidance)
- [ ] **T044** Implement background task execution for iterations in backend/src/api/projects.py (FastAPI BackgroundTasks integration for async iteration execution)
- [ ] **T045** Implement credential storage and retrieval in backend/src/storage/encryption.py (Save/load encrypted LLM API keys to data/credentials.enc per FR-050)

---

## Phase 3.5: Frontend Implementation

### Pages

- [ ] **T046** [P] ProjectList page in frontend/src/pages/ProjectList.tsx (Display projects table, status filtering, sorting by date/model, navigate to details)
- [ ] **T047** [P] ProjectConfig page in frontend/src/pages/ProjectConfig.tsx (Project creation form with validation, test scenarios input, evaluation criteria configuration)
- [ ] **T048** [P] ProjectDashboard page in frontend/src/pages/ProjectDashboard.tsx (Real-time iteration status, score trends chart, iteration history, start/stop controls per FR-035, FR-039)

### Components

- [ ] **T049** [P] ProjectForm component in frontend/src/components/ProjectForm.tsx (Reusable form for project config, validation, model selection)
- [ ] **T050** [P] IterationChart component in frontend/src/components/IterationChart.tsx (Score trend visualization using Recharts, display per-criterion scores over iterations per FR-036)
- [ ] **T051** [P] ConversationView component in frontend/src/components/ConversationView.tsx (Display conversation transcript with user/assistant distinction per FR-038, show evaluation scores)

### Services

- [ ] **T052** API client service in frontend/src/services/api.ts (Axios-based REST client, typed request/response based on OpenAPI schemas, error handling)
- [ ] **T053** State management in frontend/src/services/store.ts (Zustand store for projects, iterations, UI state)

---

## Phase 3.6: Polish

### Unit Tests

- [ ] **T054** [P] Unit tests for evaluation scoring logic in backend/tests/unit/test_evaluator.py (Test score averaging per FR-019, independent threshold checking per FR-020)
- [ ] **T055** [P] Unit tests for credential encryption in backend/tests/unit/test_encryption.py (Test Fernet encrypt/decrypt, key derivation)
- [ ] **T056** [P] Unit tests for LLM provider retry logic in backend/tests/unit/test_providers.py (Test exponential backoff, rate limit handling per FR-047)

### Error Handling and Validation

- [ ] **T057** Input validation for all API endpoints in backend/src/api/validation.py (Pydantic models enforce OpenAPI schema constraints, max lengths, ranges)
- [ ] **T058** Graceful error handling for edge cases in backend/src/services/ (Handle API unavailability, credential expiration, conversation truncation per quickstart.md edge cases)

### Performance and Observability

- [ ] **T059** Implement structured JSON logging in backend/src/utils/logging.py (Log LLM API calls, latency, iteration events per FR-044)
- [ ] **T060** Frontend component tests in frontend/tests/component/ (Jest + RTL tests for ProjectForm, IterationChart, ConversationView)

---

## Dependencies

### Critical Path
1. **Setup (T001-T009)** before all other tasks
2. **Contract Tests (T010-T011)** before API endpoints (T035-T039)
3. **Integration Tests (T012-T019)** before services (T030-T033)
4. **Models (T020-T027)** before services (T030-T033) and API routes (T035-T039)
5. **Database (T028)** before models can persist
6. **Services (T030-T033)** before orchestrator (T033) and API routes (T035-T039)
7. **LLM Provider (T034)** before services (T030-T032)
8. **API Routes (T035-T039)** before FastAPI app (T040)
9. **Backend Complete (T001-T045)** before frontend integration (T052)

### Blocking Relationships
- T028 (database) blocks T020-T027 (models)
- T020-T027 (models) block T030-T033 (services), T035-T039 (API routes), T041 (DB integration)
- T029 (encryption) blocks T045 (credential storage)
- T034 (LLM providers) blocks T030-T032 (services using LLMs)
- T030-T033 (services) block T036 (iteration execution), T044 (background tasks)
- T035-T039 (API routes) block T040 (FastAPI app)
- T040 (backend app) blocks T052 (frontend API client)
- T052 (API client) blocks T046-T048 (pages using API)

---

## Parallel Execution Examples

### Setup Phase (can run concurrently after T001-T003)
```bash
# Launch T004-T007 together:
Task: "Configure backend linting (ruff, black, mypy) in backend/pyproject.toml"
Task: "Configure frontend linting (ESLint, Prettier) in frontend/.eslintrc.json"
Task: "Create backend/src/__init__.py and module structure"
Task: "Create frontend/src/index.tsx entry point"
```

### Contract Tests (after setup, before implementation)
```bash
# Launch T010-T011 together:
Task: "Contract test suite for projects API in backend/tests/contract/test_projects_api.py"
Task: "Contract test suite for iterations API in backend/tests/contract/test_iterations_api.py"
```

### Integration Tests (after setup, before services)
```bash
# Launch T012-T019 together (8 tests):
Task: "Integration test: Create and configure new project in backend/tests/integration/test_create_project.py"
Task: "Integration test: Run iteration with failing criteria in backend/tests/integration/test_failing_iteration.py"
Task: "Integration test: Complete successful optimization in backend/tests/integration/test_successful_optimization.py"
Task: "Integration test: Configure custom evaluation criterion in backend/tests/integration/test_custom_criterion.py"
Task: "Integration test: Manage multiple projects in backend/tests/integration/test_multiple_projects.py"
Task: "Integration test: Handle max iteration limit in backend/tests/integration/test_max_iterations.py"
Task: "Integration test: Handle API errors gracefully in backend/tests/integration/test_api_errors.py"
Task: "Integration test: Export reports in JSON/CSV formats in backend/tests/integration/test_export_reports.py"
```

### Data Models (after database setup)
```bash
# Launch T020-T027 together (8 models):
Task: "Project model in backend/src/models/project.py"
Task: "Iteration model in backend/src/models/iteration.py"
Task: "Prompt model in backend/src/models/prompt.py"
Task: "TestScenario model in backend/src/models/test_scenario.py"
Task: "EvaluationCriterion model in backend/src/models/evaluation_criterion.py"
Task: "Conversation model in backend/src/models/conversation.py"
Task: "EvaluationResult model in backend/src/models/evaluation_result.py"
Task: "ModelConfiguration model in backend/src/models/model_configuration.py"
```

### Frontend Pages (after API client ready)
```bash
# Launch T046-T048 together:
Task: "ProjectList page in frontend/src/pages/ProjectList.tsx"
Task: "ProjectConfig page in frontend/src/pages/ProjectConfig.tsx"
Task: "ProjectDashboard page in frontend/src/pages/ProjectDashboard.tsx"
```

### Frontend Components (after state management)
```bash
# Launch T049-T051 together:
Task: "ProjectForm component in frontend/src/components/ProjectForm.tsx"
Task: "IterationChart component in frontend/src/components/IterationChart.tsx"
Task: "ConversationView component in frontend/src/components/ConversationView.tsx"
```

### Unit Tests (after services implemented)
```bash
# Launch T054-T056 together:
Task: "Unit tests for evaluation scoring logic in backend/tests/unit/test_evaluator.py"
Task: "Unit tests for credential encryption in backend/tests/unit/test_encryption.py"
Task: "Unit tests for LLM provider retry logic in backend/tests/unit/test_providers.py"
```

---

## Notes

- **[P] tasks** = different files, no dependencies, safe to run in parallel
- **TDD compliance**: All test tasks (T010-T019, T054-T056) must be written and verified to fail before implementing corresponding functionality
- **File size constraint**: Each module <500 lines per Constitutional Principle IV (already designed in research.md module boundaries)
- **Commit after each task**: Maintain clean git history for traceability
- **Constitutional compliance**: Verify each task follows all 5 core principles (code quality, TDD, UX consistency, file size, configuration over hardcoding)

---

## Task Generation Summary

**Total Tasks**: 60
**Parallel Tasks**: 32 (marked with [P])
**Sequential Tasks**: 28

**By Phase**:
- Setup: 9 tasks (T001-T009)
- Tests: 10 tasks (T010-T019)
- Core Implementation: 26 tasks (T020-T045)
- Frontend: 9 tasks (T046-T054)
- Polish: 6 tasks (T054-T060)

**Validation Checklist**:
- [x] All contracts have corresponding tests (T010-T011 cover projects-api.yaml, iterations-api.yaml)
- [x] All entities have model tasks (T020-T027 cover all 8 entities from data-model.md)
- [x] All tests come before implementation (Phase 3.2 before Phase 3.3)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task

---

**Tasks Ready for Execution**: Proceed with Phase 3.1 setup, then TDD cycle (write tests → verify failure → implement → verify pass → refactor)


# Implementation Plan: Automated Prompt Iteration System

**Branch**: `001-agent-codex-claude` | **Date**: 2025-10-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `D:\AIDev\PromptGenerator\specs\001-agent-codex-claude\spec.md`

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
Build an automated prompt optimization system that iteratively improves LLM prompts through simulated conversations, evaluation, and rewriting. Single-user local web application with configurable models, test scenarios, evaluation criteria (independent thresholds), and iterative refinement loop (max 20 iterations default). Outputs optimized prompts, evaluation reports (JSON/CSV), and conversation examples.

## Technical Context
**Language/Version**: Python 3.11+ (backend), JavaScript/TypeScript (frontend)
**Primary Dependencies**: FastAPI (backend API), React (frontend UI), LangChain (LLM orchestration), SQLite (local storage)
**Storage**: SQLite for project data, local file system for credentials (encrypted), conversation transcripts, reports
**Testing**: pytest (backend), Jest/React Testing Library (frontend), contract tests for API endpoints
**Target Platform**: Local desktop (Windows/macOS/Linux), localhost web server
**Project Type**: web (frontend + backend)
**Performance Goals**: Single iteration <5 minutes (model-dependent), UI responsive <100ms, support 20+ iterations
**Constraints**: Local-only operation, no cloud deployment required, secure credential storage, handle API rate limits
**Scale/Scope**: Single user, 10-50 projects, 5-10 test scenarios per project, conversation history retention

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Code Quality Standards
✅ **PASS** - Design follows separation of concerns (backend/frontend, models/services/API layers), modular structure enforced

### Principle II: Testing Discipline (TDD) - NON-NEGOTIABLE
✅ **PASS** - Contract tests for API endpoints, integration tests for optimization workflow, unit tests for evaluation logic. TDD workflow enforced.

### Principle III: User Experience Consistency
✅ **PASS** - Consistent web UI patterns, standard REST API conventions, uniform error messaging, predictable project workflow

### Principle IV: File Size Constraints (500 lines max)
✅ **PASS** - Modular design prevents large files: separate modules for conversation simulation, evaluation, prompt rewriting, storage, API routes

### Principle V: Configuration over Hardcoding
✅ **PASS** - LLM credentials externalized, model endpoints configurable, iteration limits user-configurable, no hardcoded API keys or thresholds

**Initial Assessment**: No constitutional violations. Design aligns with all core principles.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
backend/
├── src/
│   ├── models/              # Data models (Project, Iteration, Conversation, etc.)
│   ├── services/            # Business logic (conversation simulator, evaluator, rewriter)
│   ├── api/                 # FastAPI routes and endpoints
│   ├── storage/             # SQLite database access, credential encryption
│   └── llm/                 # LLM provider integrations (OpenAI, Anthropic, custom)
└── tests/
    ├── contract/            # API contract tests per endpoint
    ├── integration/         # End-to-end optimization workflow tests
    └── unit/                # Service and model unit tests

frontend/
├── src/
│   ├── components/          # Reusable UI components
│   ├── pages/               # Page components (ProjectList, ProjectConfig, Dashboard)
│   ├── services/            # API client, state management
│   └── utils/               # Formatting, charting helpers
└── tests/
    ├── component/           # Component tests
    └── integration/         # User interaction flow tests

config/                      # Configuration templates and schemas
data/                        # Local SQLite database, encrypted credentials
```

**Structure Decision**: Web application structure selected. Backend provides REST API for all operations (project CRUD, iteration execution, evaluation). Frontend is a React SPA served locally. Clear separation allows independent testing and follows constitutional modularity principles.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType codex`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 1 Completion Summary

**Artifacts Generated**:
- ✅ `research.md`: Technology stack decisions (FastAPI, React, LangChain, SQLite, Fernet encryption)
- ✅ `data-model.md`: 8 entities with fields, relationships, validation rules, state transitions
- ✅ `contracts/projects-api.yaml`: OpenAPI spec for project CRUD and iteration execution endpoints
- ✅ `contracts/iterations-api.yaml`: OpenAPI spec for iteration details and conversation viewing
- ✅ `quickstart.md`: 8 user story tests + 3 edge case tests with verification steps

**Constitution Re-Check** (Post-Design):
- ✅ **Principle I**: Modular architecture with clear separation (models, services, API, storage, LLM)
- ✅ **Principle II**: Contract-first TDD approach with OpenAPI schemas, comprehensive test scenarios
- ✅ **Principle III**: Consistent REST API patterns, uniform error responses, clear UI state management
- ✅ **Principle IV**: Module boundaries designed for <500 lines (9 backend modules, 6 frontend modules)
- ✅ **Principle V**: Configuration externalized (YAML, .env), credentials encrypted, no hardcoded values

**No new constitutional violations introduced during design phase.**

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- **Contract Tests**: 2 OpenAPI specs → 8 contract test files (one per major endpoint group)
- **Data Models**: 8 entities → 8 Pydantic + SQLAlchemy model files
- **Integration Tests**: 8 user scenarios → 8 integration test files
- **Implementation**: Backend services (simulator, evaluator, rewriter, orchestrator), API routes, frontend pages/components

**Ordering Strategy**:
- **Phase 3.1 Setup**: Project initialization, dependencies, linting configuration
- **Phase 3.2 Tests First** (TDD): Contract tests, integration tests (must fail before implementation)
- **Phase 3.3 Core Implementation**: Models, services, API endpoints (make tests pass)
- **Phase 3.4 Integration**: Database setup, encryption, LLM provider connections
- **Phase 3.5 Polish**: UI components, error handling, logging, performance optimization

**Dependency Order**:
- Models before services
- Services before API routes
- Backend API before frontend integration
- Contract tests before implementation
- Mark [P] for parallel execution (different files, independent tasks)

**Estimated Output**: 40-50 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md created
- [x] Phase 1: Design complete (/plan command) - data-model.md, contracts/, quickstart.md created
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command) - tasks.md created with 60 tasks
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS - All 5 principles compliant
- [x] Post-Design Constitution Check: PASS - No new violations
- [x] All NEEDS CLARIFICATION resolved - Spec clarification session completed
- [x] Complexity deviations documented - None (no violations)

**Artifacts Generated**:
- `D:\AIDev\PromptGenerator\specs\001-agent-codex-claude\research.md`
- `D:\AIDev\PromptGenerator\specs\001-agent-codex-claude\data-model.md`
- `D:\AIDev\PromptGenerator\specs\001-agent-codex-claude\contracts\projects-api.yaml`
- `D:\AIDev\PromptGenerator\specs\001-agent-codex-claude\contracts\iterations-api.yaml`
- `D:\AIDev\PromptGenerator\specs\001-agent-codex-claude\quickstart.md`
- `D:\AIDev\PromptGenerator\specs\001-agent-codex-claude\tasks.md`

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*

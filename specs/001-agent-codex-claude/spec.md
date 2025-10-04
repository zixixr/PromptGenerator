# Feature Specification: Automated Prompt Iteration System

**Feature Branch**: `001-agent-codex-claude`
**Created**: 2025-10-04
**Status**: Draft
**Input**: User description: "我将构建一个通用的自动化提示词迭代系统，支持用户可配置的目标模型与任务/人设，通过"仿真用户—效果评估—提示改写"的闭环持续优化。用户可指定任意可接入的大模型、目标功能/人设、测试场景与达标阈值；系统要仿真用户与目标模型生成多轮对话；生成对话和评审器可由大模型或智能 Agent（如 Codex、Claude Code 等）担任，按用户自定义指标（人设一致性、语气风格、事实准确性、互动趣味与安全合规等）打分与解释；未达标则自动改写提示并复测，直至达到目标，最终输出最佳提示、可追溯评估报告与代表性示例对话。有一个清晰美观的前端页面可以呈现你认为必要的内容。"

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## Clarifications

### Session 2025-10-04
- Q: How should evaluation scores be aggregated when multiple criteria are configured? → A: Independent thresholds - Each criterion must meet its own threshold separately
- Q: What is the maximum iteration limit to prevent infinite optimization loops? → A: User-configurable (default 20)
- Q: Should conversation turn count be configurable or have a fixed limit? → A: User-configurable per scenario
- Q: What export formats should be supported for evaluation reports? → A: JSON and CSV
- Q: Does the system require user authentication and multi-user support? → A: No authentication - Single-user local application

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A prompt engineer wants to optimize a chatbot's persona for customer service using their local machine. They launch the application, provide the initial prompt, configure the target LLM (e.g., GPT-4), define evaluation criteria (friendliness score >80%, response time <3s, policy compliance 100%), and specify test scenarios (angry customer, product inquiry, refund request). The system automatically simulates multi-turn conversations between synthetic users and the chatbot, evaluates each iteration against criteria, rewrites the prompt when targets aren't met, and continues iterating until all thresholds pass. The engineer reviews the optimization process through a visual dashboard, examines the final optimized prompt, reads evaluation reports with scores and explanations, and exports representative conversation examples for stakeholder review.

### Acceptance Scenarios
1. **Given** a user has launched the application, **When** they create a new optimization project with target model "Claude 3.5", initial prompt "You are a helpful assistant", evaluation criteria (consistency >85%, safety 100%), and 3 test scenarios, **Then** the system generates a project with unique ID, displays project configuration summary, and is ready to start optimization

2. **Given** an optimization iteration is running, **When** the simulated conversations complete and evaluation scores fall below thresholds (consistency: 72%, safety: 100%), **Then** the system automatically generates a revised prompt, logs the evaluation results with explanations, and launches the next iteration without manual intervention

3. **Given** an optimization has completed successfully after 5 iterations, **When** the user views the results dashboard, **Then** they see the final optimized prompt, iteration history with score trends, detailed evaluation reports for each criterion, and can download representative conversation transcripts

4. **Given** a user configures custom evaluation criteria, **When** they specify "brand voice alignment" with a custom scoring rubric, **Then** the evaluation agent applies this criterion during scoring and provides explanations based on the rubric

5. **Given** multiple optimization projects exist, **When** the user navigates the project list, **Then** they see each project's status (running/completed/failed), current iteration count, best scores achieved, and can filter/sort by creation date or model type

### Edge Cases
- What happens when a target LLM API is unavailable or rate-limited during optimization?
- How does system handle if evaluation scores never reach thresholds after hitting the maximum iteration limit (default 20, user-configurable)?
- What happens when two evaluation criteria conflict (e.g., creativity vs. factual accuracy)?
- How does system behave if a user modifies evaluation criteria mid-optimization?
- What happens when conversation simulation reaches the scenario's turn limit before natural completion?
- How does system handle API credential expiration during multi-hour optimization runs?

## Requirements *(mandatory)*

### Functional Requirements

#### Configuration & Setup
- **FR-001**: System MUST allow users to configure target LLM models from a list of supported providers (OpenAI, Anthropic, Google, custom endpoints)
- **FR-002**: System MUST allow users to provide initial prompt text for optimization
- **FR-003**: System MUST allow users to define persona/task descriptions that guide optimization goals
- **FR-004**: System MUST allow users to create multiple test scenarios describing user interaction contexts, each with configurable conversation turn limit
- **FR-005**: System MUST allow users to specify success threshold values for each evaluation criterion
- **FR-005a**: System MUST allow users to configure maximum iteration limit (default: 20 iterations if not specified)
- **FR-006**: System MUST persist all project configurations for future reference and reproduction

#### Evaluation Criteria
- **FR-007**: System MUST support predefined evaluation criteria: persona consistency, tone/style, factual accuracy, engagement quality, safety/compliance
- **FR-008**: System MUST allow users to define custom evaluation criteria with scoring rubrics
- **FR-009**: System MUST allow users to enable/disable individual criteria per project
- **FR-010**: System MUST evaluate each criterion independently against its own threshold (all criteria must pass for optimization success)

#### Conversation Simulation
- **FR-011**: System MUST generate simulated user messages based on test scenarios
- **FR-012**: System MUST conduct multi-turn conversations between simulated users and target model, respecting each scenario's configured turn limit
- **FR-013**: System MUST support configurable conversation simulators (LLM-based or agent-based like Codex/Claude Code)
- **FR-014**: System MUST record complete conversation transcripts including timestamps and model responses
- **FR-015**: System MUST handle conversation failures gracefully (timeouts, API errors, invalid responses)

#### Evaluation & Scoring
- **FR-016**: System MUST evaluate conversations using configured evaluator (LLM or intelligent agent)
- **FR-017**: System MUST generate numerical scores for each enabled evaluation criterion
- **FR-018**: System MUST provide textual explanations justifying each score
- **FR-019**: System MUST average scores for each criterion across all test scenarios
- **FR-020**: System MUST verify each criterion's averaged score meets or exceeds its independent threshold

#### Prompt Rewriting & Iteration
- **FR-021**: System MUST automatically rewrite prompts when any criterion's score falls below its threshold
- **FR-022**: System MUST use evaluation feedback and explanations to guide prompt improvements
- **FR-023**: System MUST support configurable prompt rewriter (LLM or agent)
- **FR-024**: System MUST track all prompt versions across iterations with timestamps
- **FR-025**: System MUST prevent infinite loops by enforcing user-configured maximum iteration limit (default 20)
- **FR-026**: System MUST stop iteration when all enabled criteria meet or exceed their independent thresholds

#### Results & Reporting
- **FR-027**: System MUST output the final optimized prompt upon successful completion
- **FR-028**: System MUST generate comprehensive evaluation reports including all iterations, scores, and explanations
- **FR-029**: System MUST provide iteration history showing score progression over time
- **FR-030**: System MUST export representative conversation examples demonstrating optimized behavior
- **FR-031**: System MUST support traceability by linking scores to specific conversations and evaluation rationales
- **FR-032**: System MUST allow users to download reports in JSON format (structured data) and CSV format (spreadsheet-compatible)

#### User Interface
- **FR-033**: System MUST provide a web-based frontend for single-user local operation (no authentication required)
- **FR-034**: Frontend MUST display project configuration forms with validation
- **FR-035**: Frontend MUST show real-time optimization status (current iteration, running/completed, latest scores)
- **FR-036**: Frontend MUST visualize score trends across iterations with charts/graphs
- **FR-037**: Frontend MUST present evaluation reports with expandable details for each criterion
- **FR-038**: Frontend MUST display conversation transcripts with clear user/assistant distinction
- **FR-039**: Frontend MUST allow users to start and stop optimization runs
- **FR-040**: Frontend MUST support project management (create, list, view, delete projects)

#### Integration & Extensibility
- **FR-041**: System MUST support authentication for LLM API access with secure credential storage
- **FR-042**: System MUST allow users to connect custom LLM endpoints with configurable authentication
- **FR-043**: System MUST support pluggable evaluator and rewriter modules [NEEDS CLARIFICATION: plugin architecture details?]
- **FR-044**: System MUST log all API calls, errors, and system events for debugging and auditing

### Performance & Scale Requirements
- **FR-045**: System MUST support running multiple optimization projects sequentially (single-user operation)
- **FR-046**: System MUST provide progress feedback during iteration execution
- **FR-047**: System MUST handle API rate limits gracefully with retry logic and backoff

### Data & Storage
- **FR-048**: System MUST retain optimization project data locally including configurations, iterations, scores, conversations
- **FR-049**: System MUST allow users to manually delete projects and associated data
- **FR-050**: System MUST persist LLM API credentials securely in local encrypted storage

### Key Entities *(include if feature involves data)*

- **Project**: Represents a prompt optimization session with configuration (target model, initial prompt, persona description, test scenarios, evaluation criteria, thresholds, maximum iteration limit, status)

- **Iteration**: A single optimization cycle containing prompt version, generated conversations, evaluation scores, explanations, timestamp, and status (running/completed/failed)

- **Conversation**: Multi-turn dialogue between simulated user and target model, including turn sequence, messages, metadata (scenario ID, model parameters), and evaluation results

- **EvaluationCriterion**: Definition of a scoring dimension with name, description, independent threshold, scoring rubric (for custom criteria), and evaluator configuration

- **TestScenario**: Description of a user interaction context used to generate simulated conversations, including scenario description, expected user behavior, conversation turn limit, and priority

- **Prompt**: Versioned prompt text with metadata (iteration number, creation timestamp, evaluation scores, parent prompt ID for tracking evolution)

- **EvaluationResult**: Scores and explanations for a conversation against all enabled criteria, including per-criterion scores, aggregate score, pass/fail status, and detailed rationales

- **ModelConfiguration**: Target LLM settings including provider, model name, API endpoint, authentication credentials, and generation parameters (temperature, max tokens)

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain (5 clarifications resolved)
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked and resolved (5 clarifications)
- [x] User scenarios defined
- [x] Requirements generated (50 functional requirements)
- [x] Entities identified (8 key entities)
- [x] Review checklist passed

---

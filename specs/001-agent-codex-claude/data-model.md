# Data Model: Automated Prompt Iteration System

## Entity Relationship Overview

```
Project (1) ──< (N) Iteration
Project (1) ──< (N) TestScenario
Project (1) ──< (N) EvaluationCriterion
Project (1) ──< (1) ModelConfiguration

Iteration (1) ──< (N) Conversation
Iteration (1) ──< (1) Prompt

Conversation (1) ──< (1) EvaluationResult
Conversation (N) ──> (1) TestScenario
```

## Entities

### Project
Represents a prompt optimization session.

**Fields**:
- `id`: UUID (primary key)
- `name`: String (user-defined project name)
- `description`: Text (optional project description)
- `target_model`: String (model identifier, e.g., "gpt-4", "claude-3-5-sonnet")
- `initial_prompt`: Text (starting prompt to optimize)
- `persona_description`: Text (optimization goal/persona guidance)
- `max_iterations`: Integer (default 20, user-configurable per FR-005a)
- `status`: Enum["draft", "running", "completed", "failed", "stopped"]
- `created_at`: DateTime
- `updated_at`: DateTime
- `best_iteration_id`: UUID (nullable, foreign key to Iteration)

**Relationships**:
- Has many `TestScenario`
- Has many `EvaluationCriterion`
- Has many `Iteration`
- Has one `ModelConfiguration`
- Belongs to one `Iteration` (best result)

**Validation Rules**:
- `name` required, 1-200 characters
- `target_model` required, must match supported provider pattern
- `initial_prompt` required, 1-10000 characters
- `max_iterations` range: 1-100
- `status` transitions: draft → running → {completed|failed|stopped}

**State Transitions**:
- **draft**: Project created, not yet started
- **running**: Iteration loop executing
- **completed**: All criteria met thresholds
- **failed**: Max iterations reached without success or error occurred
- **stopped**: User manually stopped optimization

### Iteration
A single optimization cycle.

**Fields**:
- `id`: UUID (primary key)
- `project_id`: UUID (foreign key to Project)
- `iteration_number`: Integer (1-indexed sequence)
- `prompt_id`: UUID (foreign key to Prompt)
- `status`: Enum["running", "completed", "failed"]
- `started_at`: DateTime
- `completed_at`: DateTime (nullable)
- `duration_seconds`: Integer (nullable, calculated)
- `passed_criteria_count`: Integer
- `total_criteria_count`: Integer
- `all_criteria_passed`: Boolean

**Relationships**:
- Belongs to one `Project`
- Has one `Prompt`
- Has many `Conversation` (one per test scenario)

**Validation Rules**:
- `iteration_number` must be unique within project
- `iteration_number` = previous max + 1
- `status` cannot transition back from completed/failed to running

**Derived Fields**:
- `duration_seconds` = completed_at - started_at
- `all_criteria_passed` = passed_criteria_count == total_criteria_count

### Prompt
Versioned prompt text with evaluation metadata.

**Fields**:
- `id`: UUID (primary key)
- `text`: Text (the prompt content)
- `parent_id`: UUID (nullable, foreign key to Prompt for lineage tracking)
- `iteration_id`: UUID (foreign key to Iteration)
- `created_at`: DateTime
- `generation_method`: Enum["initial", "llm_rewrite", "manual_edit"]
- `rewrite_rationale`: Text (nullable, explanation from rewriter LLM)

**Relationships**:
- Belongs to one `Iteration`
- May have one parent `Prompt`
- May have many child `Prompt` instances

**Validation Rules**:
- `text` required, 1-50000 characters
- `parent_id` must not create cycles
- First iteration prompt has `parent_id` = null, `generation_method` = "initial"

**Lineage Tracking**:
- Track prompt evolution via `parent_id` chain
- Enables traceability per FR-024, FR-031

### TestScenario
Description of a user interaction context for conversation simulation.

**Fields**:
- `id`: UUID (primary key)
- `project_id`: UUID (foreign key to Project)
- `name`: String (scenario name, e.g., "Angry Customer")
- `description`: Text (detailed scenario context)
- `expected_user_behavior`: Text (optional persona hints for simulator)
- `turn_limit`: Integer (max conversation turns per FR-012)
- `priority`: Integer (1-10, for future weighted sampling)
- `created_at`: DateTime

**Relationships**:
- Belongs to one `Project`
- Has many `Conversation` (one per iteration)

**Validation Rules**:
- `name` required, 1-100 characters, unique within project
- `description` required, 1-2000 characters
- `turn_limit` range: 1-50
- `priority` range: 1-10, default 5

### EvaluationCriterion
Definition of a scoring dimension.

**Fields**:
- `id`: UUID (primary key)
- `project_id`: UUID (foreign key to Project)
- `name`: String (criterion name, e.g., "Persona Consistency")
- `description`: Text (what this criterion measures)
- `threshold`: Float (0-100, minimum score for success per FR-005)
- `is_predefined`: Boolean (true for built-in criteria, false for custom)
- `scoring_rubric`: Text (nullable, detailed scoring instructions for custom criteria per FR-008)
- `evaluator_config`: JSON (nullable, evaluator-specific settings)
- `is_enabled`: Boolean (default true, per FR-009)
- `created_at`: DateTime

**Relationships**:
- Belongs to one `Project`
- Related to many `EvaluationResult` through conversations

**Validation Rules**:
- `name` required, 1-100 characters, unique within project
- `threshold` range: 0-100
- `scoring_rubric` required if `is_predefined` = false
- Predefined criteria names: "persona_consistency", "tone_style", "factual_accuracy", "engagement_quality", "safety_compliance" (per FR-007)

**Built-in Criteria**:
1. **persona_consistency**: How well responses match defined persona
2. **tone_style**: Appropriate tone for context
3. **factual_accuracy**: Correctness of information
4. **engagement_quality**: Conversational quality, helpfulness
5. **safety_compliance**: Adherence to safety policies

### Conversation
Multi-turn dialogue between simulated user and target model.

**Fields**:
- `id`: UUID (primary key)
- `iteration_id`: UUID (foreign key to Iteration)
- `test_scenario_id`: UUID (foreign key to TestScenario)
- `turns`: JSON (array of {role, message, timestamp} objects)
- `turn_count`: Integer (calculated from turns array)
- `started_at`: DateTime
- `completed_at`: DateTime
- `status`: Enum["running", "completed", "failed", "truncated"]
- `failure_reason`: Text (nullable, if status = failed)
- `metadata`: JSON (model params, API call info)

**Relationships**:
- Belongs to one `Iteration`
- Belongs to one `TestScenario`
- Has one `EvaluationResult`

**Validation Rules**:
- `turns` format: `[{role: "user"|"assistant", message: string, timestamp: ISO8601}, ...]`
- `turn_count` = length of turns array
- `turn_count` ≤ test_scenario.turn_limit
- `status` = "truncated" if turn_limit reached before natural end

**Turn Format**:
```json
[
  {"role": "user", "message": "Hello", "timestamp": "2025-10-04T10:00:00Z"},
  {"role": "assistant", "message": "Hi!", "timestamp": "2025-10-04T10:00:01Z"}
]
```

### EvaluationResult
Scores and explanations for a conversation.

**Fields**:
- `id`: UUID (primary key)
- `conversation_id`: UUID (foreign key to Conversation)
- `criterion_scores`: JSON (map of criterion_id → {score, explanation})
- `aggregate_score`: Float (average across all criteria per FR-019)
- `passed`: Boolean (all criteria met thresholds per FR-020)
- `evaluated_at`: DateTime
- `evaluator_model`: String (LLM model used for evaluation)
- `evaluation_duration_seconds`: Float

**Relationships**:
- Belongs to one `Conversation`

**Validation Rules**:
- `criterion_scores` keys must match enabled project criteria IDs
- Each score value: 0-100
- `aggregate_score` = average of all criterion scores
- `passed` = true if all criterion scores ≥ their thresholds

**Criterion Scores Format**:
```json
{
  "criterion_id_1": {
    "score": 85.5,
    "explanation": "Response maintained persona..."
  },
  "criterion_id_2": {
    "score": 72.0,
    "explanation": "Tone was slightly inconsistent..."
  }
}
```

### ModelConfiguration
Target LLM settings for a project.

**Fields**:
- `id`: UUID (primary key)
- `project_id`: UUID (foreign key to Project)
- `provider`: String (e.g., "openai", "anthropic", "custom")
- `model_name`: String (e.g., "gpt-4", "claude-3-5-sonnet")
- `api_endpoint`: String (nullable, for custom endpoints per FR-042)
- `temperature`: Float (0-2, default 0.7)
- `max_tokens`: Integer (default 2000)
- `additional_params`: JSON (nullable, provider-specific settings)

**Relationships**:
- Belongs to one `Project`

**Validation Rules**:
- `provider` enum: ["openai", "anthropic", "google", "custom"]
- `model_name` required
- `api_endpoint` required if provider = "custom"
- `temperature` range: 0-2
- `max_tokens` range: 1-128000

**Provider-Specific Validation**:
- OpenAI models: gpt-4, gpt-4-turbo, gpt-3.5-turbo, etc.
- Anthropic models: claude-3-5-sonnet, claude-3-opus, etc.
- Custom: validate endpoint URL format

## Indexes

**Performance Indexes**:
- `projects.status` (filter active/completed projects)
- `iterations.project_id, iterations.iteration_number` (composite, iteration lookup)
- `conversations.iteration_id` (join conversations to iterations)
- `conversations.test_scenario_id` (join conversations to scenarios)
- `evaluation_results.conversation_id` (1:1 join)

**Uniqueness Constraints**:
- `test_scenarios.project_id, test_scenarios.name` (unique scenario names per project)
- `evaluation_criteria.project_id, evaluation_criteria.name` (unique criteria names per project)
- `iterations.project_id, iterations.iteration_number` (unique iteration sequence)

## Data Retention

**Storage Strategy** (per FR-048, FR-049):
- All project data retained indefinitely until user manually deletes
- Large conversation transcripts stored as JSON files, referenced by conversation.id
- SQLite database stores structured metadata, file paths

**Delete Cascade**:
- Deleting Project → cascade deletes Iterations, TestScenarios, EvaluationCriteria, ModelConfiguration
- Deleting Iteration → cascade deletes Conversations, Prompts
- Deleting Conversation → cascade deletes EvaluationResult
- Also delete associated JSON transcript files

## Migration Strategy

**Schema Versioning**:
- Use Alembic for SQLite schema migrations
- Version schema changes for future enhancements
- Backwards-compatible JSON field extensions

**Future Extensions**:
- Add cost tracking fields (tokens used, API costs)
- Add caching fields (cached LLM response references)
- Add collaboration fields (shared projects, multi-user support)

---
**Data Model Complete**: All entities defined with fields, relationships, validation rules, and state transitions.

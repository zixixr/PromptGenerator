# Quickstart: Automated Prompt Iteration System

## User Story Validation Tests

This document defines integration test scenarios derived from the feature specification's acceptance scenarios. These tests validate the complete user workflows and serve as executable documentation.

### Test Scenario 1: Create and Configure New Project

**Given**: User launches the application for the first time

**When**: User creates a new optimization project with:
- Name: "Customer Service Bot Optimization"
- Target Model: "claude-3-5-sonnet"
- Initial Prompt: "You are a helpful customer service assistant."
- Evaluation Criteria:
  - Persona Consistency (threshold: 85%)
  - Safety Compliance (threshold: 100%)
- Test Scenarios:
  1. Angry Customer (description: "User is frustrated about delayed order", turn limit: 5)
  2. Product Inquiry (description: "User asks about product features", turn limit: 4)
  3. Refund Request (description: "User wants to return an item", turn limit: 6)

**Then** the system should:
1. Generate a unique project ID (UUID format)
2. Display project configuration summary showing:
   - Project name
   - Target model
   - 3 test scenarios
   - 2 evaluation criteria with thresholds
   - Max iterations: 20 (default)
   - Status: "draft"
3. Enable "Start Optimization" button
4. Persist project to database

**Verification Steps**:
```
1. POST /api/projects with request body
2. Assert response status = 201
3. Assert response.id is UUID
4. Assert response.status = "draft"
5. Assert response.test_scenarios.length = 3
6. Assert response.evaluation_criteria.length = 2
7. Assert response.max_iterations = 20
8. GET /api/projects and verify new project appears in list
```

### Test Scenario 2: Run Iteration with Failing Criteria

**Given**: Project created with status "draft" (from Test Scenario 1)

**When**: User clicks "Start Optimization"

**Then** the system should:
1. Start iteration #1
2. Simulate 3 conversations (one per test scenario)
3. Evaluate each conversation against both criteria
4. Calculate averaged scores across scenarios:
   - Persona Consistency: 72% (below 85% threshold)
   - Safety Compliance: 100% (meets threshold)
5. Detect that Persona Consistency failed
6. Automatically generate revised prompt using evaluator feedback
7. Log evaluation results with explanations
8. Prepare for iteration #2 (do not auto-start)

**Verification Steps**:
```
1. POST /api/projects/{id}/iterations
2. Assert response status = 202 (async operation accepted)
3. Poll GET /api/iterations/{iteration_id} until status = "completed"
4. Assert iteration_number = 1
5. Assert all_criteria_passed = false
6. Assert passed_criteria_count = 1
7. Assert total_criteria_count = 2
8. GET /api/iterations/{iteration_id}/conversations
9. Assert conversations.length = 3
10. For each conversation, assert evaluation_result exists
11. Verify criterion_scores contains both criteria
12. Assert aggregated Persona Consistency score < 85
13. Assert aggregated Safety Compliance score = 100
14. GET /api/projects/{id} and verify status = "running"
15. Verify new prompt generated with parent_id = initial_prompt.id
```

### Test Scenario 3: Complete Successful Optimization

**Given**: Project has run 4 iterations, none meeting all criteria thresholds

**When**: Iteration #5 completes with all criteria passing:
- Persona Consistency: 88% (≥85% threshold)
- Safety Compliance: 100% (≥100% threshold)

**Then** the system should:
1. Mark iteration #5 as all_criteria_passed = true
2. Update project status to "completed"
3. Set project.best_iteration_id to iteration #5 ID
4. Display success message in UI
5. Show final optimized prompt
6. Display iteration history with score trends (5 iterations)
7. Show detailed evaluation reports for each criterion
8. Enable download of conversation transcripts

**Verification Steps**:
```
1. Given 5 iterations exist via repeated POST /api/projects/{id}/iterations
2. Assert iteration 5 has all_criteria_passed = true
3. GET /api/projects/{id}
4. Assert status = "completed"
5. Assert best_iteration_id = iteration_5.id
6. GET /api/iterations/{iteration_5_id}
7. Assert passed_criteria_count = 2
8. Assert total_criteria_count = 2
9. Verify aggregated_scores shows both criteria ≥ thresholds
10. GET /api/projects/{id}/iterations
11. Assert iterations.length = 5
12. Verify score progression across iterations (trending upward)
13. POST /api/projects/{id}/export with format="json"
14. Assert response contains all iterations, scores, explanations
```

### Test Scenario 4: Configure Custom Evaluation Criterion

**Given**: User creating new project

**When**: User adds custom criterion "Brand Voice Alignment" with:
- Description: "Responses align with our friendly, casual brand voice"
- Threshold: 80%
- Scoring Rubric: "Score based on: use of contractions, casual greetings, emoji appropriateness (when applicable), warmth of language. Deduct points for overly formal language."

**Then** the system should:
1. Create EvaluationCriterion with is_predefined = false
2. Store custom scoring_rubric text
3. Use rubric during evaluation to guide LLM scorer
4. Generate score (0-100) and explanation for this criterion
5. Include in independent threshold checking (FR-010)

**Verification Steps**:
```
1. POST /api/projects with evaluation_criteria containing custom criterion
2. Assert response.evaluation_criteria includes custom criterion
3. Assert custom criterion has is_predefined = false
4. Assert scoring_rubric matches provided text
5. Start iteration and verify conversations are evaluated
6. GET /api/iterations/{id}/conversations
7. For each conversation.evaluation_result.criterion_scores
8. Assert custom criterion ID exists in scores
9. Assert score is 0-100 number
10. Assert explanation references rubric elements
```

### Test Scenario 5: Manage Multiple Projects

**Given**: User has created 3 projects:
1. "Customer Service Bot" (status: completed, 5 iterations, best score: 90%)
2. "Sales Assistant" (status: running, 3 iterations, current best: 78%)
3. "FAQ Chatbot" (status: draft, 0 iterations)

**When**: User navigates to project list page

**Then** the system should display:
1. Table with 3 projects
2. For each project show:
   - Name
   - Status (with status badge color)
   - Current iteration count
   - Best scores achieved (if any iterations completed)
   - Created date
3. Allow filtering by status (dropdown: all/draft/running/completed/failed/stopped)
4. Allow sorting by creation date or model type
5. Enable clicking project to view details

**Verification Steps**:
```
1. Create 3 projects via POST /api/projects (varying configurations)
2. Start iterations on project 2 (3 times)
3. Complete all iterations on project 1 until success
4. GET /api/projects
5. Assert response.total = 3
6. Assert projects array contains all 3 with correct statuses
7. GET /api/projects?status=running
8. Assert response.total = 1
9. Assert returned project is "Sales Assistant"
10. Verify each ProjectSummary includes iteration_count, best_score
11. Click through to GET /api/projects/{id} for details
```

### Test Scenario 6: Handle Max Iteration Limit

**Given**: Project configured with max_iterations = 20

**When**: Project runs 20 iterations without all criteria meeting thresholds

**Then** the system should:
1. Complete iteration #20
2. Mark project status as "failed"
3. Set best_iteration_id to iteration with highest aggregate score
4. Display message: "Max iterations reached. Optimization incomplete."
5. Show best attempt details
6. Allow user to export partial results
7. Prevent starting new iterations

**Verification Steps**:
```
1. Create project with max_iterations = 3 (for faster testing)
2. Mock evaluator to always return scores below thresholds
3. Start 3 iterations sequentially
4. After iteration 3, GET /api/projects/{id}
5. Assert status = "failed"
6. Assert best_iteration_id is set (highest score among 3)
7. POST /api/projects/{id}/iterations (attempt 4th)
8. Assert response status = 400
9. Assert error message indicates max iterations reached
10. Verify project data still accessible for export
```

### Test Scenario 7: Handle API Errors Gracefully

**Given**: Project is running iteration with LLM API calls

**When**: Target LLM API becomes unavailable (rate limit or service outage)

**Then** the system should:
1. Detect API error during conversation simulation
2. Retry with exponential backoff (per FR-047)
3. After max retries, mark conversation as "failed"
4. Log failure reason
5. Continue with other test scenarios if possible
6. Mark iteration as "failed" if all conversations fail
7. Display user-friendly error message with recovery guidance

**Verification Steps**:
```
1. Mock LLM provider to return 429 (rate limit) or 503 (unavailable)
2. Start iteration
3. Monitor logs for retry attempts
4. Verify exponential backoff timing (1s, 2s, 4s, etc.)
5. After max retries, GET /api/iterations/{id}
6. Assert status = "failed"
7. Assert conversation.status = "failed"
8. Assert conversation.failure_reason describes error
9. Verify error surfaced in UI with actionable guidance
10. Verify project can be resumed after API recovers
```

### Test Scenario 8: Export Reports in Multiple Formats

**Given**: Project completed with 5 iterations

**When**: User requests report export in JSON format

**Then** the system should return:
1. Project metadata (name, target model, criteria, scenarios)
2. All iterations with iteration number, prompt text, scores
3. Aggregated scores for each iteration
4. Individual conversation details with turns (optional, based on export config)
5. Traceability: link scores to specific conversations and explanations

**When**: User requests report export in CSV format

**Then** the system should return:
1. Tabular format with columns:
   - iteration_number, prompt_preview, criterion_1_score, criterion_2_score, ..., aggregate_score, passed
2. One row per iteration
3. Criteria scores as numeric columns
4. Separate CSV for conversation transcripts (optional)

**Verification Steps**:
```
1. Complete project with multiple iterations
2. POST /api/projects/{id}/export with format="json"
3. Assert Content-Type = application/json
4. Parse JSON and verify structure:
   - assert json.project.id exists
   - assert json.iterations is array
   - for each iteration: assert scores, prompt, timestamp
5. POST /api/projects/{id}/export with format="csv"
6. Assert Content-Type = text/csv
7. Parse CSV rows
8. Assert header row contains criterion names
9. Assert data rows match iteration count
10. Verify numeric scores are parseable
```

## Edge Case Tests

### Edge Case 1: Conversation Reaches Turn Limit Before Completion

**Scenario**: Test scenario configured with turn_limit = 3

**Expected Behavior**:
- Conversation stops after 3 user-assistant turn pairs
- Status marked as "truncated" (not "failed")
- Evaluation still performed on truncated conversation
- Score may be lower due to incomplete interaction

**Verification**:
```
1. Create project with test scenario turn_limit = 3
2. Start iteration
3. GET /api/conversations/{id}
4. Assert turn_count = 3
5. Assert status = "truncated"
6. Assert evaluation_result exists (evaluation still performed)
```

### Edge Case 2: User Modifies Criteria Mid-Optimization

**Scenario**: User attempts to edit evaluation criteria while project status = "running"

**Expected Behavior**:
- API rejects modification with 400 error
- Error message: "Cannot modify criteria while optimization is running"
- Suggest stopping optimization first

**Verification**:
```
1. Start iteration (project status = "running")
2. Attempt PUT /api/projects/{id} to update criteria
3. Assert response status = 400
4. Assert error message guides user to stop first
```

### Edge Case 3: Conflicting Criteria Thresholds

**Scenario**: Criteria "Creativity" (threshold: 90%) and "Factual Accuracy" (threshold: 95%) may inherently conflict

**Expected Behavior**:
- System attempts optimization without bias
- If conflict prevents success, iterations reach max limit
- User receives partial results showing tension between criteria
- Traceability shows which criterion is harder to satisfy

**Verification**:
```
1. Create project with potentially conflicting criteria
2. Run optimization to completion or max iterations
3. Review iteration history
4. Identify if one criterion consistently scores lower
5. Export report showing score distributions
```

## Performance Benchmarks

### Benchmark 1: Single Iteration Latency
- **Target**: <5 minutes for 3 test scenarios (model-dependent)
- **Measurement**: iteration.duration_seconds
- **Acceptable Range**: 60-300 seconds (varies by LLM provider latency)

### Benchmark 2: UI Responsiveness
- **Target**: <100ms for page load and interactions
- **Measurement**: Frontend performance profiling
- **Pages to Test**: ProjectList, ProjectDashboard, ConversationView

### Benchmark 3: Database Query Performance
- **Target**: <50ms for project list query (10-50 projects)
- **Measurement**: SQLite query execution time
- **Query**: `GET /api/projects` with status filter

---

## Test Execution Order

**Recommended Sequence** (for TDD):
1. Write contract tests for all endpoints (based on OpenAPI specs)
2. Run contract tests → verify they fail (no implementation)
3. Implement API endpoints to pass contract tests
4. Write integration tests (Test Scenarios 1-8)
5. Run integration tests → verify they fail
6. Implement business logic (simulators, evaluators, rewriters)
7. Run integration tests → verify they pass
8. Write unit tests for edge cases and complex logic
9. Refactor while keeping all tests green

---
**Quickstart Complete**: All user scenarios and edge cases defined with verification steps.

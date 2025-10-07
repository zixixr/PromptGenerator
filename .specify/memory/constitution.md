<!--
Sync Impact Report:
- Version change: N/A (initial version) → 1.0.0
- Modified principles: N/A (initial creation)
- Added sections: All core principles, Development Standards, Governance
- Removed sections: None
- Templates requiring updates:
  ✅ plan-template.md - Constitution Check section already references this file
  ✅ spec-template.md - No updates needed (focuses on requirements, not implementation)
  ✅ tasks-template.md - TDD principles align with constitution
  ✅ agent-file-template.md - Reviewed, no updates needed
- Follow-up TODOs: None
-->

# PromptGenerator Constitution

## Core Principles

### I. Code Quality First
Code MUST be readable, maintainable, and self-documenting. Every module, function, and class MUST have a single, clear purpose. Code reviews MUST verify that implementations are straightforward and well-structured.

**Rationale**: Quality code reduces bugs, accelerates onboarding, and minimizes technical debt. Clear code is faster to debug and easier to extend.

### II. Test-Driven Development (NON-NEGOTIABLE)
Tests MUST be written before implementation. The TDD cycle is strictly enforced:
1. Write failing test
2. Implement minimal code to pass
3. Refactor while keeping tests green

All features MUST have:
- Contract tests for API boundaries
- Integration tests for user workflows
- Unit tests for complex logic

**Rationale**: TDD prevents defects, validates requirements early, and creates executable documentation. Tests written after implementation often miss edge cases.

### III. User Experience Consistency
User-facing interfaces MUST maintain consistent patterns across the application. Similar actions MUST behave similarly. Error messages MUST be clear, actionable, and user-friendly.

Design changes MUST be validated against:
- Accessibility standards (WCAG 2.1 AA minimum)
- Cross-platform compatibility
- Existing UI/UX patterns in the codebase

**Rationale**: Consistency reduces cognitive load, improves learnability, and builds user trust. Inconsistent experiences frustrate users and increase support burden.

### IV. Performance Requirements
Performance MUST be measured, not assumed. Every feature MUST define explicit performance targets before implementation:
- Response time targets (e.g., <200ms p95 for API calls)
- Resource constraints (e.g., memory, CPU usage)
- Scalability expectations (e.g., concurrent users, data volume)

Performance regressions MUST be caught by automated tests before merging.

**Rationale**: Performance directly impacts user satisfaction and operational costs. Late-stage performance fixes are expensive and risky.

### V. Simplicity Over Cleverness
Choose the simplest solution that meets requirements. Complex patterns (factories, repositories, elaborate inheritance) MUST be justified in writing before adoption.

Apply YAGNI (You Aren't Gonna Need It):
- Build for current requirements, not hypothetical future needs
- Start with straightforward implementations
- Refactor toward patterns only when complexity justifies it

**Rationale**: Over-engineering increases maintenance burden, slows development, and introduces bugs. Simple code is easier to understand, test, and modify.

### VI. Observability & Debugging
All production code MUST be debuggable. Implement:
- Structured logging with appropriate levels (ERROR, WARN, INFO, DEBUG)
- Request tracing for distributed operations
- Clear error messages with context (not just stack traces)
- Health checks and readiness probes

Logs MUST NOT contain sensitive data (passwords, tokens, PII).

**Rationale**: Without observability, production issues are impossible to diagnose. Good logging reduces mean time to resolution (MTTR) dramatically.

## Development Standards

### Code Review Requirements
All code changes MUST:
- Pass automated tests (contract, integration, unit)
- Meet performance targets defined in requirements
- Follow established code style (enforced by linters)
- Include documentation for public APIs
- Be reviewed by at least one other developer

Reviews MUST verify:
- Constitutional compliance (principles followed)
- Test coverage for new/changed code
- No introduction of technical debt
- Clear commit messages explaining "why" not just "what"

### Testing Gates
Code CANNOT be merged unless:
- All tests pass in CI pipeline
- Code coverage meets project minimum (define per project, suggest 80%+)
- Performance tests validate response time targets
- No critical security vulnerabilities (per static analysis)

### Documentation Standards
Documentation MUST be:
- Co-located with code (e.g., inline comments, README in module directory)
- Updated atomically with code changes
- Focused on "why" and "how to use", not "what" (code shows "what")

API documentation MUST include:
- Purpose and use cases
- Request/response examples
- Error scenarios and handling
- Performance characteristics

## Governance

### Constitutional Authority
This constitution supersedes all other development practices. When conflicts arise between this document and other guidelines, this document prevails.

### Amendment Process
Constitution changes require:
1. Written proposal with rationale
2. Team review and approval
3. Version increment following semantic versioning:
   - **MAJOR**: Breaking changes to governance or principle removal
   - **MINOR**: New principles or significant expansions
   - **PATCH**: Clarifications and refinements
4. Migration plan for existing code (if applicable)

### Compliance Review
All pull requests MUST verify constitutional compliance. Reviewers MUST challenge:
- Unnecessary complexity (Principle V)
- Missing tests (Principle II)
- Undefined performance targets (Principle IV)
- Inconsistent UX patterns (Principle III)

When deviations are necessary, they MUST be documented in implementation plans with explicit justification.

### Living Document
This constitution evolves with project needs. Teams SHOULD propose amendments when:
- Principles prove inadequate for new domains
- Better practices emerge
- Existing rules create unintended obstacles

Amendments MUST maintain focus on quality, testing, UX consistency, and performance.

**Version**: 1.0.0 | **Ratified**: 2025-10-06 | **Last Amended**: 2025-10-06

<!--
Sync Impact Report - Constitution Update
========================================
Version Change: [new constitution] → 1.0.0
Change Type: MINOR (Initial constitution creation)

Principles Defined:
- I. Code Quality Standards
- II. Testing Discipline (TDD)
- III. User Experience Consistency
- IV. File Size Constraints
- V. Configuration over Hardcoding

Added Sections:
- Core Principles (5 principles)
- Development Standards
- Quality Gates
- Governance

Templates Status:
✅ plan-template.md - reviewed, Constitution Check section exists at line 47-50
✅ spec-template.md - reviewed, no constitutional references needed (pre-planning phase)
✅ tasks-template.md - reviewed, TDD ordering aligns with Principle II
✅ agent-file-template.md - reviewed (template only, no updates needed)

Follow-up TODOs:
- None - all placeholders filled

Rationale:
This is the initial constitution creation based on user requirements for code quality,
testing standards, UX consistency, file size limits, and avoiding hardcoding. Version
starts at 1.0.0 following semantic versioning (initial stable release).
-->

# PromptGenerator Constitution

## Core Principles

### I. Code Quality Standards
Code MUST be maintainable, readable, and follow established best practices. All code MUST:
- Follow consistent naming conventions throughout the codebase
- Include meaningful comments for complex logic
- Use descriptive variable and function names that convey intent
- Avoid code duplication (DRY principle)
- Maintain clear separation of concerns
- Follow language-specific style guides and linting rules

**Rationale**: High-quality code reduces bugs, accelerates onboarding, and enables long-term
maintainability. Technical debt compounds exponentially; preventing it at the source is more
efficient than remediation.

### II. Testing Discipline (TDD) - NON-NEGOTIABLE
Test-Driven Development is MANDATORY for all features. The workflow is strictly enforced:
1. Write tests first based on requirements
2. User reviews and approves test scenarios
3. Verify tests fail (red state)
4. Implement minimum code to pass tests (green state)
5. Refactor while maintaining green state

**Test Coverage Requirements**:
- Contract tests for all API endpoints and public interfaces
- Integration tests for user workflows and cross-component interactions
- Unit tests for complex business logic and edge cases
- All tests MUST be automated and run in CI/CD pipeline

**Rationale**: TDD prevents regressions, documents intended behavior, enables confident
refactoring, and ensures features meet requirements before implementation begins. Tests
written after code are biased toward existing implementation rather than requirements.

### III. User Experience Consistency
User-facing features MUST provide a consistent, predictable experience:
- Consistent terminology, naming, and messaging across all interfaces
- Uniform interaction patterns (keyboard shortcuts, navigation, error handling)
- Predictable behavior across similar operations
- Clear, actionable error messages with recovery guidance
- Responsive feedback for all user actions

**Platform-Specific Requirements**:
- CLI tools: consistent flag naming, help text formatting, exit codes
- Web interfaces: consistent component styling, navigation patterns, loading states
- APIs: consistent endpoint naming, response formats, error structures

**Rationale**: Consistency reduces cognitive load, accelerates user proficiency, and minimizes
support costs. Inconsistent UX creates friction, confusion, and erosion of user trust.

### IV. File Size Constraints
No single source code file SHALL exceed 500 lines (excluding blank lines and comments).
Files approaching this limit MUST be refactored:
- Extract related functions into separate modules
- Separate concerns into distinct files (models, services, utilities)
- Create focused, single-responsibility modules
- Maintain logical grouping when splitting files

**Exceptions**: Configuration files, generated code, or data files are exempt. Source code
exceptions require explicit justification in code review.

**Rationale**: Large files indicate poor separation of concerns, are harder to navigate and
test, create merge conflicts, and slow down IDE performance. The 500-line limit forces
modular design and improves code organization.

### V. Configuration over Hardcoding
All environment-specific, deployment-specific, or variable values MUST be externalized:
- Use configuration files (.env, config.json, settings.yaml)
- Support environment variable overrides
- Provide sensible defaults for development
- Document all configuration options
- Never commit secrets or credentials to version control

**Prohibited Hardcoding**:
- API endpoints, URLs, connection strings
- File paths outside project structure
- Feature flags and toggles
- Third-party service credentials
- Environment-specific values (ports, timeouts, limits)

**Allowed Hardcoding**:
- True constants (mathematical values, protocol definitions)
- Internal defaults overridable by configuration

**Rationale**: Hardcoded values create environment-specific bugs, complicate deployment,
prevent testing, and expose security risks. Configuration enables portability, testability,
and secure credential management.

## Development Standards

### Code Review Requirements
All code changes MUST pass review before merging:
- At least one approval from a qualified reviewer
- All automated tests passing
- No unresolved review comments
- Compliance with all constitutional principles verified
- Documentation updated for API/behavior changes

### Versioning and Breaking Changes
Follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes, incompatible API changes
- MINOR: New features, backward-compatible additions
- PATCH: Bug fixes, backward-compatible corrections

Breaking changes MUST include:
- Migration guide for users
- Deprecation warnings in preceding minor version
- Clear changelog entry with migration steps

### Documentation Standards
All public interfaces MUST be documented:
- API contracts (request/response schemas, error codes)
- User-facing features (usage examples, configuration options)
- Development setup (dependencies, build steps, testing)
- Architecture decisions (ADRs for significant choices)

## Quality Gates

All features MUST pass these gates before release:

1. **Constitutional Compliance**: No violations of core principles without documented justification
2. **Test Coverage**: All tests passing, coverage meeting project standards
3. **Code Review**: Approved by qualified reviewer(s)
4. **Documentation**: Public interfaces documented, changelog updated
5. **Security**: No hardcoded secrets, dependencies scanned for vulnerabilities
6. **Performance**: Meets defined performance criteria for the feature domain

## Governance

### Amendment Process
Constitutional amendments require:
1. Proposal documenting rationale and impact
2. Review and approval from project maintainers
3. Version increment following semantic versioning rules
4. Update to all dependent templates and documentation
5. Communication to all contributors

### Compliance and Review
- All PRs MUST verify constitutional compliance in review checklist
- Quarterly constitution review to assess effectiveness
- Violations tracked and addressed in retrospectives
- Constitutional principles supersede other practices in case of conflict

### Complexity Justification
Deviations from constitutional principles MUST be justified in implementation plans with:
- Specific principle(s) violated
- Why deviation is necessary
- What simpler alternative was considered and rejected
- Mitigation strategy to minimize impact

**Version**: 1.0.0 | **Ratified**: 2025-10-04 | **Last Amended**: 2025-10-04

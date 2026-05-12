<!--
Sync Impact Report
- Version change: 0.0.0-template -> 1.0.0
- Modified principles:
	- Template Principle 1 -> I. Beyond Vibe Coding (Specification-Grounded Decisions)
	- Template Principle 2 -> II. Primary Tech Stack Authority
	- Template Principle 3 -> III. Testing Authority (NON-NEGOTIABLE)
	- Template Principle 4 -> IV. Architecture and Security Discipline
	- Template Principle 5 -> V. Documentation and Traceability Discipline
- Added sections:
	- Operational Constraints
	- Delivery Workflow and Quality Gates
- Removed sections:
	- None
- Templates requiring updates:
	- ✅ updated: .specify/templates/tasks-template.md
	- ✅ updated: .specify/templates/plan-template.md
	- ✅ no changes needed: .specify/templates/spec-template.md
	- ✅ no changes needed: .specify/templates/checklist-template.md
	- ✅ no changes needed: README.md.txt (empty)
- Follow-up TODOs:
	- None
-->

# InnovatEPAM Portal Constitution

## Core Principles

### I. Beyond Vibe Coding (Specification-Grounded Decisions)
Every technical decision MUST be grounded in approved specifications and MUST be documented.
Implementation MUST trace to PRD, Epic, and Story artifacts before coding begins.
Changes that alter behavior or scope MUST update specification artifacts first.
Rationale: This prevents ad hoc implementation drift and preserves decision clarity.

### II. Primary Tech Stack Authority
The project MUST use Python with FastAPI for backend APIs, MongoDB Atlas for persistence,
and Pydantic for data validation and schema contracts unless superseded by a new ADR.
Service boundaries, contracts, and validation models MUST align with this stack.
Rationale: Stack consistency reduces integration risk and increases implementation speed.

### III. Testing Authority (NON-NEGOTIABLE)
TDD is mandatory for all feature work.
Teams MUST execute Red-Green-Refactor for each story slice.
Any tooling defaults that skip or de-prioritize tests are overridden by this constitution.
A minimum mutation testing score of 75% MUST be met for covered business logic.
Rationale: Test-first delivery reduces regressions and verifies behavior, not assumptions.

### IV. Architecture and Security Discipline
ADR-001 is authoritative for Phase 1 architectural direction.
Any deviation from ADR-001 MUST be proposed in a new ADR before implementation.
Password handling MUST use passlib with bcrypt for secure hashing.
Sensitive fields (passwords, hashes, secrets) MUST NOT be returned in API responses.
Rationale: Explicit architecture and secure defaults are required for safe delivery.

### V. Documentation and Traceability Discipline
Every feature MUST maintain a story document in specs/stories/ with acceptance criteria,
technical plan, and definition of done.
The Memory Bank MUST be updated after each story completion to reflect current state.
Traceability from code and tests back to story and PRD MUST remain intact.
Rationale: Persistent context is required for reliable AI-native engineering workflows.

## Operational Constraints

- Requirements hierarchy is mandatory: PRD -> Epic -> Story.
- Development artifacts MUST remain source-of-truth aligned with:
	- docs/memory-bank/projectBrief.md
	- docs/memos/engineering_standards.md
	- specs/adrs/ADR-001-tech-stack.md
- Data contracts MUST be represented via explicit Pydantic schemas.
- Database operations MUST target MongoDB Atlas-compatible patterns.

## Delivery Workflow and Quality Gates

- Standard workflow MUST be followed: Specify -> Plan -> Tasks -> Implement.
- Clarification MUST be performed when requirements are ambiguous.
- Story implementation MUST begin with failing tests (RED) and conclude with passing tests.
- Completion gate per story MUST include:
	- Acceptance criteria passing
	- Test suite passing
	- Mutation score >= 75% on relevant business logic
	- Memory Bank updates recorded

## Governance

This constitution supersedes local practices and template defaults when conflicts occur.

Amendment procedure:
- Propose change with explicit rationale and affected sections.
- Classify version bump using semantic versioning policy.
- Update dependent templates and guidance in the same amendment.
- Record amendment date and impact summary.

Versioning policy:
- MAJOR: Backward-incompatible governance changes or principle removals/redefinitions.
- MINOR: New principle/section added or materially expanded guidance.
- PATCH: Clarifications, wording improvements, and non-semantic edits.

Compliance review expectations:
- Every plan MUST pass a constitution check before implementation begins.
- Every tasks file MUST reflect constitution testing authority and documentation duties.
- Reviews MUST block merges that violate mandatory principles.

**Version**: 1.0.0 | **Ratified**: 2026-05-12 | **Last Amended**: 2026-05-12

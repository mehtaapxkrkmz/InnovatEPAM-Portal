# Engineering Standards - Beyond Vibe Coding

This file consolidates the mandatory engineering rules for InnovatEPAM Portal.

Project implementation baseline for this phase:
- Backend/API: Python + FastAPI
- Data store: MongoDB Atlas

## 1. Requirements Hierarchy (Non-Negotiable)
All feature work must follow this hierarchy:
- PRD -> Epics -> User Stories

Rules:
- No implementation starts without requirements context.
- Every Epic must map to clear user value from the PRD.
- Every Story must include testable acceptance criteria.
- Stories should follow INVEST and be small enough for focused delivery.

## 2. Memory Discipline (Memory Bank Required)
Project context must be maintained in a structured Memory Bank and kept current.

Required structure:
- docs/memory-bank/ (project-level context)
- architecture overview
- coding conventions
- domain glossary
- development workflow

Rules:
- Update memory artifacts whenever scope, architecture, or workflow changes.
- Treat stale memory as a defect: if docs and reality diverge, fix docs immediately.
- AI prompts must reference current memory artifacts, not assumptions.

## 3. Architecture Governance (ADR Mandatory)
Every significant architecture or technical decision requires an ADR (Architecture Decision Record).

Minimum ADR content:
- Context
- Decision
- Alternatives considered
- Consequences/trade-offs

Rules:
- No silent architecture decisions.
- If a decision impacts stack, boundaries, data model, security, or deployment, write/update an ADR first.
- Implementation must align with accepted ADRs.

## 4. Delivery Workflow (SpecKit Style)
Default delivery path:
- Specify -> Plan -> Tasks

Operational interpretation:
- Specify: define feature intent, user stories, acceptance criteria, success metrics.
- Plan: document implementation approach, architecture details, and constraints.
- Tasks: produce actionable execution tasks mapped to stories.

Quality reinforcement from lab guidance:
- Constitution should be defined early and treated as guardrails.
- Clarification of ambiguities is required before deep implementation.
- Checklist validation is recommended before planning/implementation.

## 5. Testing Standards (Constitution-Aligned)
Testing is test-first and constitution-driven.

Mandatory rules:
- TDD workflow: RED -> GREEN -> REFACTOR.
- Tests are generated from specs/stories, not from implementation details.
- Testing Constitution rules are binding for test structure, naming, quality, and tooling.
- Mutation testing target: 75% or higher.

Recommended quantitative baseline:
- Testing Pyramid distribution near 70% unit / 20% integration / 10% E2E.
- Coverage expectations should be explicitly defined in constitution and enforced in CI.

Quality gates:
- Reject tautological or non-deterministic tests.
- Favor observable behavior over private implementation details.
- Keep tests independent, fast, and meaningful.

## 6. Execution Rule for This Project
For each feature slice, enforce this sequence:
1. Confirm PRD -> Epic -> Story traceability.
2. Verify memory bank and ADRs are up to date.
3. Run Specify -> Plan -> Tasks.
4. Write/execute tests in TDD flow.
5. Implement and validate against acceptance criteria.
6. Commit with meaningful message and keep delivery traceable.

## 7. Source of Truth Policy
For this project phase, implementation must follow these files as authoritative references:
- docs/memory-bank/projectBrief.md
- docs/memos/engineering_standards.md
- specs/adrs/ADR-001-tech-stack.md

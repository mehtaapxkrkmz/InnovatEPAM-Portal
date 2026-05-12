# ADR-001: Technology Stack for InnovatEPAM Portal Phase 1 MVP

## Status
Accepted

## Date
2026-05-12

## Context
Module 08 requires delivery of the InnovatEPAM Portal Phase 1 MVP with three feature groups:
- User Management: register/login/logout with role distinction (submitter, admin)
- Idea Submission: title, description, category, single file attachment, list/view
- Evaluation Workflow: status lifecycle (submitted, under review, accepted, rejected) with admin comments

The team is applying Beyond Vibe Coding principles, which require:
- Requirement traceability (PRD -> Epic -> Story)
- Explicit architecture decisions via ADRs
- Test-first development and constitution-driven quality gates

The platform must support rapid MVP iteration with clear API contracts, straightforward role checks, and flexible document-style storage for idea and evaluation data.

## Decision
Use the following stack for Phase 1:
- Language: Python
- Web framework: FastAPI
- Database: MongoDB Atlas

Supporting decision notes:
- FastAPI will provide REST endpoints for authentication, idea lifecycle, and admin evaluation actions.
- MongoDB Atlas will store users, ideas, evaluation comments, and status transitions in document collections.
- Phase 1 authorization model will enforce submitter vs admin behavior at API/service boundaries.

## Alternatives Considered
### Alternative A: Node.js + Express + MongoDB
Pros:
- Popular web stack for API services
- Large ecosystem and broad familiarity

Cons:
- Less built-in request modeling and typed validation than FastAPI defaults
- Lower out-of-the-box API documentation experience

Reason not selected:
- FastAPI better matches rapid, explicit API modeling for this MVP.

### Alternative B: Python + Django + PostgreSQL
Pros:
- Mature framework with batteries-included features
- Strong relational modeling support

Cons:
- Heavier framework footprint for a focused API-first MVP
- Higher upfront modeling and migration overhead for rapid iteration

Reason not selected:
- FastAPI + MongoDB Atlas allows faster iteration for document-centric idea workflows in Phase 1.

## Consequences
Positive:
- Fast API delivery cadence with clear endpoint contracts
- Flexible schema evolution for MVP changes in submissions and evaluation metadata
- Strong alignment with Python ecosystem for test tooling and service layering

Trade-offs / Risks:
- Document model requires disciplined validation to prevent inconsistent shapes
- Role and status transitions must be explicitly guarded in service logic
- Attachment handling and storage strategy must be implemented carefully to avoid security and size issues

## Guardrails
- Any change to language, framework, database, or persistence strategy requires a new ADR or ADR supersession.
- Implementation must remain traceable to PRD, Epics, and Stories.
- Testing must follow TDD with constitution-defined standards and maintain at least 75% mutation score target.

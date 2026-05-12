# Implementation Plan: InnovatEPAM Portal Phase 1 MVP

**Branch**: `main` | **Date**: 2026-05-12  
**Spec**: [specs/003-phase1-mvp-canonical/spec.md](specs/003-phase1-mvp-canonical/spec.md)  
**Input**: Canonical specification + research + design artifacts

## Summary

InnovatEPAM Portal Phase 1 MVP is a **secure innovation idea submission and governance platform** for employees. The implementation strategy is:

1. **Specification-first** (Constitution Principle I): All code traces to approved requirements
2. **TDD-first** (Constitution Principle III): Red-Green-Refactor with 75% mutation testing
3. **MongoDB + FastAPI + Pydantic stack** (Constitution Principle II): Proven, scalable architecture
4. **Three core stories** implemented sequentially with clear integration points

**Estimated effort**: 3 weeks (1 week per story + hardening)

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Motor (async MongoDB driver), Pydantic  
**Storage**: MongoDB Atlas (document database) + GridFS for files  
**Testing**: pytest + mutmut (TDD with 75% minimum mutation score)  
**Target Platform**: Linux/Windows server (ASGI via Uvicorn)  
**Project Type**: Web service (REST API backend)  
**Performance Goals**: Handle 1000+ concurrent idea submissions without degradation  
**Constraints**: <200ms p95 latency for list/retrieve operations, <500ms for uploads  
**Scale/Scope**: Phase 1 MVP for <1000 employees  

## Constitution Check

**Status**: ✅ All gates PASSED

| Gate | Principle | Check | Status |
|------|-----------|-------|--------|
| Stack | II. Primary Tech Stack Authority | Python + FastAPI + MongoDB + Pydantic mandated | ✅ PASS |
| TDD | III. Testing Authority (NON-NEGOTIABLE) | TDD workflow enforced; 75% mutation minimum | ✅ PASS |
| Mutation | III. Testing Authority | Mutation testing framework (mutmut) configured | ✅ PASS |
| Security | IV. Architecture and Security Discipline | ADR-001 & ADR-002 define persistence & auth | ✅ PASS |
| Docs | V. Documentation and Traceability | All decisions traced to specification | ✅ PASS |
| ADRs | IV. Architecture Discipline | Three ADRs covering data, auth, testing | ✅ PASS |

**Re-evaluation after Phase 1 design**: All principles remain aligned. No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/003-phase1-mvp-canonical/
├── spec.md                          # Canonical specification (single source of truth)
├── plan.md                          # This file (implementation roadmap)
├── research.md                      # Phase 0 research (resolved clarifications)
├── data-model.md                    # Phase 1 design (MongoDB collections + Pydantic)
├── quickstart.md                    # Phase 1 design (developer onboarding)
├── contracts/
│   └── api-rest.md                  # Phase 1 design (12 REST endpoints + contracts)
└── checklists/
    └── requirements.md              # Requirements traceability
```

### Source Code (repository root)

```text
src/
└── app/
    ├── __init__.py
    ├── main.py                      # FastAPI app entry point
    ├── core/                        # Configuration and security
    │   ├── __init__.py
    │   ├── config.py                # Settings, environment variables
    │   ├── security.py              # JWT, password utilities (passlib/bcrypt)
    │   └── constants.py             # Application constants
    ├── models/                      # Pydantic request/response schemas
    │   ├── __init__.py
    │   ├── user.py                  # User registration, profile
    │   ├── idea.py                  # Idea submission, update
    │   ├── governance.py            # Decision, evaluation
    │   ├── audit.py                 # Audit log entries
    │   └── token.py                 # JWT token payloads
    ├── db/                          # Database layer
    │   ├── __init__.py
    │   ├── client.py                # Motor (async MongoDB) connection setup
    │   ├── repositories/            # Data access objects (DAOs)
    │   │   ├── __init__.py
    │   │   ├── user_repo.py         # User CRUD + queries
    │   │   ├── idea_repo.py         # Idea CRUD + queries
    │   │   ├── audit_repo.py        # Audit log creation
    │   │   └── attachment_repo.py   # GridFS file operations
    │   └── schemas.py               # MongoDB collection validation (JSON Schema)
    ├── api/                         # HTTP API layer
    │   ├── __init__.py
    │   ├── router.py                # Include all route handlers
    │   ├── endpoints/
    │   │   ├── __init__.py
    │   │   ├── auth.py              # POST /auth/register, /auth/login, /auth/logout
    │   │   ├── ideas.py             # GET/POST /ideas, GET/POST /ideas/{id}/attachment
    │   │   └── governance.py        # PUT /ideas/{id}/review, /ideas/{id}/decision
    │   └── dependencies.py          # Dependency injection (get_current_user, require_evaluator)
    └── services/                    # Business logic layer
        ├── __init__.py
        ├── auth_service.py          # Authentication logic (register, login, token refresh)
        ├── idea_service.py          # Idea submission logic (create, validate, list)
        ├── governance_service.py    # Evaluation logic (review, decide, audit)
        └── attachment_service.py    # File handling (upload, download, validate)

tests/
├── __init__.py
├── conftest.py                      # Pytest fixtures and configuration
├── unit/                            # Fast, isolated tests (mock DB)
│   ├── __init__.py
│   ├── test_auth_service.py         # Auth business logic
│   ├── test_idea_service.py         # Idea business logic
│   ├── test_governance_service.py   # Decision logic
│   ├── test_validation.py           # Input validation
│   └── test_security.py             # Password hashing, JWT
├── integration/                     # Slower, realistic tests (real DB)
│   ├── __init__.py
│   ├── test_auth_flow.py            # Register → Login → Use token → Logout
│   ├── test_idea_submission_flow.py # Create idea → Attach file → List → Retrieve
│   └── test_evaluation_flow.py      # Start review → Make decision → Audit trail
└── contract/                        # API endpoint specifications
    ├── __init__.py
    ├── test_auth_contracts.py       # /auth/* endpoints match spec
    ├── test_ideas_contracts.py      # /ideas/* endpoints match spec
    └── test_governance_contracts.py # /ideas/{id}/decision match spec

docs/
├── adrs/                            # Architectural Decision Records
│   ├── ADR-001-data-persistence.md  # MongoDB + Pydantic + GridFS decision
│   ├── ADR-002-authentication.md    # OAuth2 + JWT + passlib/bcrypt
│   └── ADR-003-testing.md           # TDD + pytest + mutmut
├── memory-bank/
│   └── projectBrief.md              # Project context and history
└── memos/
    └── engineering_standards.md     # Coding standards

.env                                 # Local configuration (not committed)
.gitignore
requirements.txt
pytest.ini
```

**Structure Decision**: FastAPI layered architecture with clear separation of concerns (web layer → service layer → data layer) enabling testability, maintainability, and independent scaling of business logic.

## Implementation Roadmap Summary

**Phase 1a**: Story-001 (User Identity) - 3-4 days  
**Phase 1b**: Story-002 (Idea Submission) - 3-4 days  
**Phase 1c**: Story-003 (Evaluation Governance) - 3-4 days  
**Phase 1d**: Hardening & Polish - 2-3 days  

**Total**: ~3 weeks from RED tests to production-ready Phase 1 MVP

### Key Milestones

- **Day 3**: Story-001 DONE (registration, login, RBAC working)
- **Day 7**: Story-002 DONE (idea submission, attachments working)
- **Day 11**: Story-003 DONE (evaluation workflow, audit trail complete)
- **Day 14**: All tests passing, 95%+ coverage, 75%+ mutation score
- **Day 15**: Hardening complete, documentation final, deployment ready

## Success Criteria

✅ All three stories DONE (acceptance criteria met)  
✅ All endpoints tested (contract tests passing)  
✅ 95%+ code coverage on services layer  
✅ 75%+ mutation testing score on services layer  
✅ All specification requirements (FR-001 through FR-020) implemented  
✅ Audit trail captures all governance events  
✅ RBAC enforced (submitter vs evaluator/admin)  
✅ File attachments handle validation and size constraints  
✅ Concurrent evaluation conflicts handled gracefully  
✅ Passwords hashed with bcrypt (never exposed)  
✅ Documentation complete and accurate  
✅ Performance meets <200ms p95 for list/retrieve  

## Related Documentation

- **research.md** - Phase 0 research and all technical clarifications resolved
- **data-model.md** - MongoDB collections, Pydantic schemas, indexes, relationships
- **contracts/api-rest.md** - 12 REST endpoints with full request/response contracts
- **quickstart.md** - Developer setup, environment configuration, first steps
- **docs/adrs/ADR-001-data-persistence.md** - Data persistence architecture decision
- **docs/adrs/ADR-002-authentication.md** - Auth & authorization architecture decision
- **docs/adrs/ADR-003-testing.md** - Testing & quality assurance architecture decision

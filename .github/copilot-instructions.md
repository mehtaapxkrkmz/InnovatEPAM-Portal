<!-- SPECKIT START -->

## Project Context & Technical Blueprint

**Phase 1 MVP Implementation Plan**: [specs/003-phase1-mvp-canonical/plan.md](specs/003-phase1-mvp-canonical/plan.md)

**Canonical Specification** (single source of truth): [specs/003-phase1-mvp-canonical/spec.md](specs/003-phase1-mvp-canonical/spec.md)

**Core Design Artifacts**:
- **Data Model**: [specs/003-phase1-mvp-canonical/data-model.md](specs/003-phase1-mvp-canonical/data-model.md) - MongoDB collections, Pydantic schemas, indexes
- **API Contracts**: [specs/003-phase1-mvp-canonical/contracts/api-rest.md](specs/003-phase1-mvp-canonical/contracts/api-rest.md) - 12 REST endpoints with full specifications
- **Developer Quickstart**: [specs/003-phase1-mvp-canonical/quickstart.md](specs/003-phase1-mvp-canonical/quickstart.md) - Setup, testing, first steps

**Architectural Decisions**:
- **ADR-001**: [docs/adrs/ADR-001-data-persistence.md](docs/adrs/ADR-001-data-persistence.md) - MongoDB Atlas + Pydantic + GridFS
- **ADR-002**: [docs/adrs/ADR-002-authentication.md](docs/adrs/ADR-002-authentication.md) - OAuth2 + JWT + passlib/bcrypt
- **ADR-003**: [docs/adrs/ADR-003-testing.md](docs/adrs/ADR-003-testing.md) - TDD + pytest + mutmut (75% mutation minimum)

**Tech Stack**: Python 3.11+ | FastAPI | Motor (async MongoDB) | Pydantic | pytest + mutmut

**Key Principles**:
1. **Specification-first**: Every decision and implementation traces to canonical spec
2. **TDD mandatory**: Red-Green-Refactor workflow with 75% mutation testing minimum
3. **Consistent stack**: Python + FastAPI + MongoDB + Pydantic (Constitution Principle II)
4. **Secure by default**: OAuth2 + JWT + bcrypt + RBAC (Constitution Principle IV)

<!-- SPECKIT END -->

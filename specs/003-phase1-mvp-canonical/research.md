# Phase 0 Research: InnovatEPAM Portal Phase 1 MVP

**Date**: 2026-05-12  
**Status**: Complete  
**Input**: Canonical specification from `specs/003-phase1-mvp-canonical/spec.md`

## Research Summary

This document resolves technical clarifications required before detailed design and implementation begin. All findings below are grounded in:
- Constitution principles (III. Testing Authority, II. Primary Tech Stack Authority, IV. Architecture and Security Discipline)
- Canonical specification requirements (FR-001 through FR-020)
- Phase 1 MVP scope constraints

---

## R-001: MongoDB Connection Pooling Strategy

**Decision**: Use Motor (Async MongoDB driver) with connection pooling via Uvicorn worker concurrency.

**Rationale**:
- FastAPI with Uvicorn runs ASGI workers; each worker maintains a Motor client pool
- Motor handles connection pooling natively (default pool size: 50 connections)
- Eliminates complexity of manual connection lifecycle management
- Recommended for Phase 1: 10-50 connection pool size depending on worker count

**Implementation Details**:
- Motor client instantiated once per Uvicorn worker and reused
- Connection string stored in environment variables (MongoDB URI with auth)
- Timeout: 30 seconds for connection acquisition
- Retries: 3 attempts on transient network failures

**Alternatives Considered**:
- Raw PyMongo (synchronous): Rejected because FastAPI best practice is async I/O
- Manual connection per request: Rejected due to connection overhead

---

## R-002: JWT Token Structure and Expiration Windows

**Decision**: Implement OAuth2 with JWT using short-lived access tokens + refresh token flow.

**Token Structure**:
```json
{
  "access_token": {
    "sub": "user_id_uuid",
    "email": "employee@company.com",
    "role": "submitter|evaluator|admin",
    "iat": 1715500000,
    "exp": 1715503600,
    "type": "access"
  },
  "refresh_token": {
    "sub": "user_id_uuid",
    "iat": 1715500000,
    "exp": 1715586400,
    "type": "refresh"
  }
}
```

**Expiration Windows**:
- Access token: 1 hour (3600 seconds)
- Refresh token: 24 hours (86400 seconds)
- Phase 1 default: No forced logout; tokens expire naturally

**Rationale**:
- Short access window minimizes exposure if token compromised
- Refresh token allows seamless re-authentication without user interaction
- Aligns with OAuth2 best practices for web APIs
- Constitution Principle IV mandates secure token handling

**Alternatives Considered**:
- Long-lived single tokens: Rejected due to security exposure window
- Session-based (cookies): Rejected in favor of stateless JWT for horizontal scaling

---

## R-003: Password Hashing Strategy

**Decision**: Use `passlib[bcrypt]` with bcrypt algorithm for password hashing.

**Implementation Details**:
- Algorithm: bcrypt with cost factor 12 (recommended for 2026 security standards)
- Fallback: scrypt or argon2 if bcrypt unavailable
- Password minimum: 8 characters (enforced at registration)
- Password maximum: 128 characters (safety limit)

**Rationale**:
- Constitution Principle IV requires passlib with bcrypt
- bcrypt is GPU-resistant and adaptive to hardware improvements
- Cost factor 12 provides ~0.3 second hash time per attempt (acceptable for login)

**Implementation Pattern**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# During registration
hashed_pwd = pwd_context.hash(password)

# During login
is_correct = pwd_context.verify(submitted_pwd, hashed_pwd)
```

---

## R-004: Mutation Testing Framework Configuration

**Decision**: Use `mutmut` with pytest for mutation testing and enforce 75% mutation score on business logic.

**Configuration**:
- Mutation tool: `mutmut` (Python mutation framework)
- Coverage baseline: 95% code coverage (using pytest-cov)
- Mutation score target: >= 75% on `app/services/` business logic
- Out of scope for mutation: Direct DB operations, external API calls

**Rationale**:
- Constitution Principle III (Testing Authority) mandates 75% minimum mutation score
- mutmut integrates with pytest test suite
- Focuses mutation testing on services layer where business logic lives
- Ignores infrastructure and integration layers

**Implementation Workflow**:
1. Run pytest with coverage: `pytest --cov=app/services --cov-report=xml tests/`
2. Generate mutations: `mutmut run --paths app/services --tests-dir tests/`
3. Report mutation score: `mutmut results`
4. CI gate: Fail if mutation score < 75%

**Alternatives Considered**:
- Coverage alone: Rejected because code coverage doesn't verify correctness
- Manual testing: Rejected due to non-scalability and lack of reproducibility

---

## R-005: File Attachment Storage Strategy

**Decision**: Store files in MongoDB GridFS (embedded in Atlas) for Phase 1 MVP.

**Rationale**:
- GridFS handles files up to 5MB natively within MongoDB Atlas cluster
- Eliminates external S3 dependency for MVP
- Audit trail and access control tied to MongoDB documents
- Simplifies backup and disaster recovery (single database)

**Implementation Details**:
- File stored in GridFS with metadata: filename, content-type, upload_timestamp
- Retrieve file: Query GridFS by file_id associated with idea
- Size limit enforced at upload: Reject >5MB files before storage
- Content-type validation: Only PDF, PNG, JPG accepted

**Transition Path to Phase 2**:
- Evaluate S3/Azure Blob Storage if attachment volume >1GB/month
- GridFS remains suitable for <500 attachments

**Alternatives Considered**:
- Local filesystem: Rejected due to horizontal scaling complexity
- S3 from start: Rejected due to MVP simplicity goals

---

## R-006: Refresh Token Rotation Strategy

**Decision**: Implement optional refresh token rotation (not mandatory in Phase 1).

**Rationale**:
- Phase 1 MVP does not require forced token rotation
- Access tokens are short-lived (1 hour) providing natural refresh boundary
- Rotation can be added in Phase 2 if audit requirements increase

**If Rotation Added Later**:
- Invalidate old refresh token immediately upon refresh
- Issue new refresh token with same expiration
- Track refresh token generation version to prevent replay

---

## R-007: Session Invalidation on Logout

**Decision**: Implement token blacklist (in-memory cache) for Phase 1 logout enforcement.

**Rationale**:
- Phase 1 requirement (FR-006): "System MUST allow authenticated users to log out and invalidate the active session"
- JWT tokens are stateless; blacklist provides logout capability without database query per request
- In-memory cache (Redis or local store) is acceptable for MVP scale

**Implementation**:
- Upon logout: Add token's `jti` (token ID) and expiration time to blacklist
- On each request: Check if token jti is in blacklist
- Cleanup: Blacklist entries auto-expire when token exp time reached

**Alternatives Considered**:
- Database query per request: Rejected due to performance overhead
- No logout support: Rejected due to specification requirement FR-006

---

## R-008: Concurrent Evaluation Prevention Strategy

**Decision**: Use MongoDB optimistic concurrency control with version field (not pessimistic locking in Phase 1).

**Rationale**:
- Phase 1 has low concurrent evaluator count (acceptable conflict rate)
- Specification edge case: "Two evaluators/admins attempt governance actions on the same idea at nearly the same time" must be handled
- Optimistic locking simpler to implement and debug
- Phase 2 can add distributed locks (Redis) if contention increases

**Implementation**:
- Add `_version` field to idea document
- On update: Compare `_version` in filter; if mismatch, return conflict error
- Client retries update if version conflict detected

**Example**:
```python
result = ideas_collection.update_one(
    {"_id": idea_id, "_version": current_version},
    {"$set": {"status": new_status, "_version": current_version + 1}}
)
if result.matched_count == 0:
    raise ConcurrencyError("Idea was modified; please refresh and try again")
```

---

## R-009: TDD Workflow and Test Structure

**Decision**: Implement Red-Green-Refactor with test organization by concern (unit, integration, contract).

**Test Directory Structure**:
```
tests/
├── unit/
│   ├── test_services_auth.py
│   ├── test_services_ideas.py
│   └── test_validation.py
├── integration/
│   ├── test_auth_flow.py
│   ├── test_idea_submission_flow.py
│   └── test_evaluation_flow.py
├── contract/
│   └── test_api_contracts.py
└── conftest.py
```

**Rationale**:
- Unit tests exercise business logic in isolation (services layer)
- Integration tests verify end-to-end flows with real MongoDB
- Contract tests ensure API responses match specification
- Constitution Principle III mandates TDD red-green-refactor for each story

**Execution**:
1. RED: Write test for new requirement; watch it fail
2. GREEN: Write minimal implementation; watch test pass
3. REFACTOR: Improve code while tests remain green
4. MUTATION: Run mutation testing; fix tests to increase mutation score

---

## Technical Stack Confirmation

**Confirmed Stack** (per Constitution Principle II):
- **Language**: Python 3.11+
- **Web Framework**: FastAPI (async ASGI)
- **Database**: MongoDB Atlas (document storage)
- **Validation**: Pydantic (data validation and schema)
- **Authentication**: fastapi-jwt-extended (OAuth2 + JWT)
- **Password Hashing**: passlib[bcrypt]
- **Async Driver**: Motor (async MongoDB)
- **Testing**: pytest, pytest-cov, mutmut
- **File Handling**: MongoDB GridFS

---

## Phase 1 Technical Constraints

| Constraint | Value | Justification |
|------------|-------|---------------|
| Connection Pool | 10-50 | Per worker concurrency |
| Access Token TTL | 1 hour | OAuth2 best practice |
| Refresh Token TTL | 24 hours | Reasonable re-auth window |
| Max Attachment Size | 5 MB | Specification FR-011 |
| Accepted Attachment Types | PDF, PNG, JPG | Specification FR-011 |
| Password Hashing Algorithm | bcrypt (cost 12) | Constitution requirement |
| Minimum Code Coverage | 95% | Pre-mutation baseline |
| Minimum Mutation Score | 75% | Constitution requirement |
| Concurrent Evaluator Strategy | Optimistic locks | Phase 1 simplicity |

---

## Open Items (Deferred to Phase 2)

1. **Email notification system**: Not in Phase 1 scope; defer to Phase 2
2. **Analytics/dashboards**: Beyond Phase 1 MVP; defer to Phase 2
3. **Automated login lockout**: Specification FR-004 explicitly defers this
4. **Multi-file attachments**: Specification supports single file only in Phase 1
5. **Distributed session invalidation**: Single-instance Phase 1; upgrade to Redis in Phase 2 if needed
6. **Audit log retention policy**: Not specified; retain indefinitely in Phase 1

---

## Resolved Clarifications Summary

| Item | Resolution |
|------|-----------|
| MongoDB connection pooling | Motor with default pool, 30s timeout, 3 retries |
| Token structure | JWT with access (1h) + refresh (24h) tokens |
| Password hashing | passlib[bcrypt] with cost 12 |
| Mutation testing | mutmut on services layer, 75% minimum |
| File storage | MongoDB GridFS (phase 1), upgrade to S3 in phase 2 |
| Refresh token rotation | Optional; not mandatory in phase 1 |
| Logout enforcement | Token blacklist in-memory cache |
| Concurrent evaluation | Optimistic locking with _version field |
| TDD structure | Red-green-refactor per story with unit/integration/contract tests |

---

**Research Completion**: All NEEDS CLARIFICATION items from Technical Context resolved.  
**Next Phase**: Phase 1 Design (data-model.md, contracts/, quickstart.md)

---
title: "Story-001: Register Account"
type: story
status: draft
---

# Story-001: Register Account

## Epic
Epic 1 - Authentication and Access Control

## User Story
As a potential submitter, I want to register with email/password so that I can access the portal.

## Scope
Implement account registration only (no login/logout in this story), with secure password hashing and default role assignment.

## Acceptance Criteria (from PRD + Story-001)

### AC-001 Register Success
- Given a new email and valid password
- When client calls `POST /auth/register`
- Then a new user record is created
- And role is set to `submitter` by default
- And response excludes raw password fields.

### AC-002 Duplicate Email Rejected
- Given an email already registered
- When client calls `POST /auth/register`
- Then API returns conflict error (HTTP 409)
- And no second user is created.

### AC-003 Input Validation
- Given invalid email or weak/missing password
- When client calls `POST /auth/register`
- Then API returns validation error (HTTP 422).

### AC-004 Password Security
- Given successful registration
- When user document is persisted
- Then password is stored as a hash (never plaintext).

## Technical Plan

### API Endpoint
- Method: `POST`
- Path: `/auth/register`
- Auth required: No (public endpoint)

### Request Schema (Pydantic)
```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
```

### Response Schema (Pydantic)
```python
class RegisterResponse(BaseModel):
    id: str
    email: EmailStr
    role: Literal["submitter", "admin"]
    created_at: datetime
```

### Persistence Schema (Pydantic + MongoDB-oriented)
```python
class UserInDB(BaseModel):
    id: PyObjectId = Field(alias="_id")
    email: EmailStr
    password_hash: str
    role: Literal["submitter", "admin"] = "submitter"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
```

### Encryption Strategy (passlib)
- Use `passlib.context.CryptContext` with bcrypt scheme.
- Example configuration:
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```
- Hash generation at registration:
```python
password_hash = pwd_context.hash(request.password)
```

### Repository/Service Behavior
- `users` collection must have unique index on `email`.
- Registration flow:
  1. Validate request payload.
  2. Check existing user by email.
  3. Hash password with passlib.
  4. Insert user with default role `submitter`.
  5. Return safe response model (exclude `password_hash`).

### Error Contract (initial)
- `409 Conflict`: email already exists.
- `422 Unprocessable Entity`: validation errors.
- `500 Internal Server Error`: unexpected persistence failure.

## TDD Micro-Plan (RED -> GREEN -> REFACTOR)

### RED (tests first)
1. Add failing test: register with valid payload returns `201` and `submitter` role.
2. Add failing test: duplicate email returns `409`.
3. Add failing test: invalid email returns `422`.
4. Add failing test: short password returns `422`.
5. Add failing test: stored password is hashed (not equal to plaintext).

### GREEN (minimal implementation)
1. Implement request/response schemas.
2. Implement `POST /auth/register` route.
3. Implement user lookup + insert in repository.
4. Implement passlib hashing integration.
5. Return minimal successful response for tests.

### REFACTOR
1. Extract hashing utility/service.
2. Centralize error mapping.
3. Improve naming and test fixture reuse.
4. Keep all tests green.

## Dependencies
- FastAPI
- Pydantic
- pymongo or motor
- passlib[bcrypt]
- pytest + httpx (for API tests)

## Definition of Done (Story-001)
- All acceptance criteria (AC-001 to AC-004) are implemented and passing.
- `POST /auth/register` is implemented with request validation and documented schema.
- Duplicate email detection works with unique email constraint.
- Passwords are hashed using passlib (no plaintext persistence).
- Story tests are written first and passing (TDD evidence in commit history).
- No regressions in existing tests.
- Traceability is preserved to PRD Story-001.

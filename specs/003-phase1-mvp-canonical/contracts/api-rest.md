# API Contracts: InnovatEPAM Portal Phase 1 MVP

**Date**: 2026-05-12  
**Input**: Canonical specification + data-model.md  
**Scope**: FastAPI REST API endpoints and response schemas

---

## Contract Overview

InnovatEPAM Portal exposes a REST API for three primary concerns:
1. **Authentication**: Registration, login, logout, token refresh
2. **Idea Management**: Create, list, retrieve, update status
3. **Governance**: Evaluate, make decisions, record audit

All responses use JSON and include standard HTTP status codes. Authentication is via Bearer tokens in the `Authorization` header.

---

## Authentication API

### 1. Register New User

**Endpoint**: `POST /auth/register`

**Request**:
```json
{
  "email": "alice@company.com",
  "first_name": "Alice",
  "last_name": "Smith",
  "password": "SecurePassword123!"
}
```

**Validation**:
- `email`: Valid email format, must not already exist
- `password`: Minimum 8 characters

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@company.com",
  "first_name": "Alice",
  "last_name": "Smith",
  "role": "submitter",
  "created_at": "2026-05-12T10:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Email already exists, password too weak
- `422 Unprocessable Entity`: Missing fields or invalid format

**Trace**: FR-001 (registration)

---

### 2. Login

**Endpoint**: `POST /auth/login`

**Request**:
```json
{
  "email": "alice@company.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Token Contents** (JWT):
- Access token: Valid for 1 hour
- Refresh token: Valid for 24 hours
- Both tokens contain: `sub` (user_id), `email`, `role`, `iat`, `exp`

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `422 Unprocessable Entity`: Missing email or password

**Logging**:
- Every login attempt (success and failure) logged to audit_logs (FR-003)
- Audit entry includes: actor_id, timestamp, result (success/failure)

**Trace**: FR-002 (login), FR-003 (logging), FR-005 (token issuance)

---

### 3. Refresh Token

**Endpoint**: `POST /auth/refresh`

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Validation**:
- Refresh token must be valid and not expired
- Refresh token must not be revoked

**Error Responses**:
- `401 Unauthorized`: Invalid or expired refresh token

**Trace**: FR-005 (refresh credentials)

---

### 4. Logout

**Endpoint**: `POST /auth/logout`

**Request**:
```
Header: Authorization: Bearer <access_token>
Body: (empty)
```

**Response** (200 OK):
```json
{
  "message": "Logout successful"
}
```

**Action**:
- Revoke the refresh token (mark as revoked in refresh_tokens collection)
- Access token remains valid until expiration (1 hour)
- Client must discard tokens

**Error Responses**:
- `401 Unauthorized`: Invalid or missing access token

**Trace**: FR-006 (logout and session invalidation)

---

## Ideas API

### 5. Create Idea (Submitter)

**Endpoint**: `POST /ideas`

**Request**:
```json
{
  "title": "Improve employee onboarding process",
  "description": "Implement automated checklist system for new hire onboarding with role-based task assignments to reduce time-to-productivity by 30%.",
  "category": "process-improvement"
}
```

**Authentication**: Required (submitter or evaluator/admin)

**Request Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Validation**:
- `title`: 1-500 characters, required
- `description`: 10-5000 characters, required
- `category`: 1-100 characters, required
- User must be authenticated

**Response** (201 Created):
```json
{
  "id": "660f7a40-a5b9-41d4-b836-557755440001",
  "submitter_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Improve employee onboarding process",
  "description": "Implement automated checklist system...",
  "category": "process-improvement",
  "status": "submitted",
  "attachment_id": null,
  "created_at": "2026-05-12T11:30:00Z",
  "updated_at": "2026-05-12T11:30:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Title/description/category missing or too short/long
- `401 Unauthorized`: Not authenticated
- `422 Unprocessable Entity`: Invalid format

**Trace**: FR-008 (create idea), FR-009 (initial status), FR-001 (user acts as submitter)

---

### 6. List Ideas

**Endpoint**: `GET /ideas`

**Request**:
```
Header: Authorization: Bearer <access_token>
Query Parameters:
  - skip: 0 (pagination)
  - limit: 20 (pagination)
  - status: submitted,under_review,accepted,rejected (optional filter)
```

**Authentication**: Required

**Response** (200 OK):

**For Submitter**:
```json
{
  "ideas": [
    {
      "id": "660f7a40-a5b9-41d4-b836-557755440001",
      "submitter_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Improve employee onboarding process",
      "description": "...",
      "category": "process-improvement",
      "status": "submitted",
      "attachment_id": null,
      "created_at": "2026-05-12T11:30:00Z",
      "updated_at": "2026-05-12T11:30:00Z"
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 20
}
```

**For Evaluator/Admin**:
```json
{
  "ideas": [
    // All ideas in system (not filtered by submitter_id)
  ],
  "total": 127,
  "skip": 0,
  "limit": 20
}
```

**Access Control**:
- Submitters see only own ideas (filtered by submitter_id)
- Evaluators/admins see all ideas

**Trace**: FR-013 (submitter visibility), FR-014 (evaluator visibility)

---

### 7. Get Idea Details

**Endpoint**: `GET /ideas/{idea_id}`

**Request**:
```
Header: Authorization: Bearer <access_token>
```

**Authentication**: Required

**Response** (200 OK):
```json
{
  "id": "660f7a40-a5b9-41d4-b836-557755440001",
  "submitter_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Improve employee onboarding process",
  "description": "...",
  "category": "process-improvement",
  "status": "submitted",
  "attachment_id": "507f1f77bcf86cd799439011",
  "created_at": "2026-05-12T11:30:00Z",
  "updated_at": "2026-05-12T11:30:00Z"
}
```

**Access Control**:
- Submitters can only view their own ideas
- Evaluators/admins can view any idea

**Error Responses**:
- `403 Forbidden`: Submitter trying to view another user's idea
- `404 Not Found`: Idea does not exist

**Trace**: FR-013 (submitter ownership), FR-014 (evaluator access)

---

### 8. Upload Attachment

**Endpoint**: `POST /ideas/{idea_id}/attachment`

**Request**:
```
Header: Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Body:
  - file: <binary file data>
```

**File Constraints**:
- Accepted types: PDF, PNG, JPG (validated by MIME type and magic bytes)
- Max size: 5 MB
- Only 1 file allowed per idea

**Response** (200 OK):
```json
{
  "attachment_id": "507f1f77bcf86cd799439011",
  "filename": "proposal_v2.pdf",
  "content_type": "application/pdf",
  "size": 1024000,
  "uploaded_at": "2026-05-12T11:35:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: File type not supported, file size >5MB, attachment already exists
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: User is not idea submitter or evaluator/admin
- `404 Not Found`: Idea does not exist
- `413 Payload Too Large`: File exceeds 5 MB

**Validation Logic**:
1. Check file MIME type (must be application/pdf, image/png, or image/jpeg)
2. Check file magic bytes to prevent spoofed types
3. Check file size <= 5 MB
4. Check idea doesn't already have attachment
5. Check user is submitter of idea (or evaluator/admin in later phases)

**Trace**: FR-010 (attachment support), FR-011 (type/size constraints), FR-012 (validation feedback)

---

### 9. Download Attachment

**Endpoint**: `GET /ideas/{idea_id}/attachment`

**Request**:
```
Header: Authorization: Bearer <access_token>
```

**Response** (200 OK):
```
Content-Type: application/pdf (or image/png, image/jpeg)
Content-Disposition: attachment; filename="proposal_v2.pdf"

[binary file data]
```

**Access Control**:
- Submitters can download their own idea's attachment
- Evaluators/admins can download any idea's attachment

**Error Responses**:
- `403 Forbidden`: Access denied
- `404 Not Found`: Idea or attachment not found

**Trace**: FR-013, FR-014 (access control)

---

## Governance API

### 10. Start Review (Evaluator/Admin)

**Endpoint**: `PUT /ideas/{idea_id}/review`

**Request**:
```json
{
  "action": "start_review"
}
```

**Authentication**: Required, role must be evaluator or admin

**Response** (200 OK):
```json
{
  "id": "660f7a40-a5b9-41d4-b836-557755440001",
  "status": "under_review",
  "updated_at": "2026-05-12T14:00:00Z"
}
```

**Validation**:
- Current status must be "submitted"
- User role must be evaluator or admin
- Audit entry created automatically

**Error Responses**:
- `400 Bad Request`: Invalid status transition
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: User is not evaluator/admin

**Trace**: FR-016 (valid transitions)

---

### 11. Make Decision (Evaluator/Admin)

**Endpoint**: `PUT /ideas/{idea_id}/decision`

**Request**:
```json
{
  "decision": "accepted",
  "comment": "Excellent idea with high impact. Recommend implementation in Q3."
}
```

**Valid decisions**: `accepted`, `rejected`

**Validation**:
- `decision`: Must be "accepted" or "rejected"
- `comment`: Required, non-empty, non-whitespace only
- Current status must be "under_review"
- User role must be evaluator or admin

**Response** (200 OK):
```json
{
  "id": "660f7a40-a5b9-41d4-b836-557755440001",
  "status": "accepted",
  "updated_at": "2026-05-12T14:15:00Z",
  "audit_entry_id": "880h9c62-g51d-63f6-d048-779977662223"
}
```

**Error Responses**:
- `400 Bad Request`: Comment missing, invalid decision, invalid transition
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: User is not evaluator/admin
- `409 Conflict`: Concurrent modification (another evaluator updated idea; refresh and retry)

**Side Effects**:
- Creates audit_logs entry with decision details (FR-018)
- Increments idea._version for concurrency control
- Updates idea.status

**Trace**: FR-015 (lifecycle), FR-016 (valid transitions), FR-017 (comment required), FR-018 (audit trail)

---

### 12. Get Audit History

**Endpoint**: `GET /ideas/{idea_id}/audit`

**Request**:
```
Header: Authorization: Bearer <access_token>
Query Parameters:
  - skip: 0
  - limit: 50
```

**Authentication**: Required, evaluator/admin only

**Response** (200 OK):
```json
{
  "audit_entries": [
    {
      "id": "770g8b51-f40c-52e5-c937-668866551112",
      "actor_id": "550e8400-e29b-41d4-a716-446655440000",
      "actor_role": "submitter",
      "action": "idea_create",
      "timestamp": "2026-05-12T11:30:00Z",
      "result": "success"
    },
    {
      "id": "880h9c62-g51d-63f6-d048-779977662223",
      "actor_id": "550e8400-e29b-41d4-a716-446655440011",
      "actor_role": "evaluator",
      "action": "decision_make",
      "timestamp": "2026-05-12T14:15:00Z",
      "result": "success",
      "comment": "Excellent idea with high impact. Recommend implementation in Q3."
    }
  ],
  "total": 3,
  "skip": 0,
  "limit": 50
}
```

**Access Control**:
- Only evaluators/admins can retrieve audit history

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: User is not evaluator/admin
- `404 Not Found`: Idea does not exist

**Trace**: FR-018 (audit trail), FR-020 (historical preservation)

---

## Error Response Format

All error responses follow this standard format:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 character",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 1}
    }
  ]
}
```

Or for application-level errors:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "File type must be PDF, PNG, or JPG",
  "details": {
    "submitted_type": "text/plain",
    "allowed_types": ["application/pdf", "image/png", "image/jpeg"]
  }
}
```

---

## Authentication & Security Headers

All requests (except `/auth/register` and `/auth/login`) must include:

```
Authorization: Bearer <access_token>
```

**Token Validation**:
- Decode JWT and verify signature
- Check token type = "access"
- Check token exp > current timestamp
- If token invalid, return 401 Unauthorized

**CORS Policy** (Phase 1):
- Allow-Origin: * (development only; restrict to domain in production)
- Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
- Allow-Headers: Authorization, Content-Type

---

## Pagination Standard

List endpoints support:
```
skip: number (default 0)
limit: number (default 20, max 100)
```

Response includes:
```json
{
  "items": [...],
  "total": 127,
  "skip": 0,
  "limit": 20
}
```

---

## Status Code Summary

| Code | Meaning |
|------|---------|
| 200 | OK - successful request |
| 201 | Created - resource successfully created |
| 400 | Bad Request - validation error |
| 401 | Unauthorized - authentication required or invalid |
| 403 | Forbidden - authenticated but not authorized |
| 404 | Not Found - resource does not exist |
| 409 | Conflict - concurrent modification detected |
| 413 | Payload Too Large - file exceeds size limit |
| 422 | Unprocessable Entity - invalid data format |
| 500 | Internal Server Error - server error |

---

## Testing Contracts

All endpoints MUST have corresponding contract tests in `tests/contract/`:

```python
# tests/contract/test_auth_contracts.py
def test_register_creates_user_with_submitter_role():
    """Verify FR-001 contract: registration creates submitter role"""
    ...

def test_login_returns_access_and_refresh_tokens():
    """Verify FR-005 contract: tokens issued on successful login"""
    ...
```

Each contract test verifies:
1. Request format validation
2. Response schema compliance
3. Status code correctness
4. Error message formatting

---

**Contract Completion**: All 12 endpoints defined with request/response formats, validation rules, access control, and traceability to specification requirements.

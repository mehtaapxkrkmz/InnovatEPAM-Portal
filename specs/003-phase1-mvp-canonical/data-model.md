# Phase 1 Design: Data Model

**Date**: 2026-05-12  
**Status**: Complete  
**Input**: Canonical specification + research.md findings

---

## Data Model Overview

InnovatEPAM Portal Phase 1 MVP requires four primary collections in MongoDB Atlas with Pydantic validation, comprehensive indexing, and explicit validation rules grounded in specification requirements.

---

## Collection: `users`

**Purpose**: Store employee identity, authentication credentials, and role assignment.

**Pydantic Schema**:

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Literal

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    hashed_password: str
    role: Literal["submitter", "evaluator", "admin"] = "submitter"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
```

**MongoDB Document Structure**:

```json
{
  "_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@company.com",
  "first_name": "Alice",
  "last_name": "Smith",
  "hashed_password": "$2b$12$abcdefghijklmnopqrstuvwxyz...",
  "role": "submitter",
  "is_active": true,
  "created_at": ISODate("2026-05-12T10:00:00Z"),
  "updated_at": ISODate("2026-05-12T10:00:00Z")
}
```

**Validation Rules**:
- `email`: Must be unique per user (unique index enforced)
- `email`: Valid email format (EmailStr validates)
- `first_name`, `last_name`: Non-empty, max 255 characters
- `hashed_password`: Never returned in API responses (validation rule in schema)
- `role`: Must be one of: submitter, evaluator, admin
- `is_active`: Default true; soft-delete by setting false

**Indexes**:
```javascript
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "created_at": -1 })
db.users.createIndex({ "role": 1 })
```

**Traceability**:
- Addresses FR-001 (registration), FR-002 (login), FR-007 (role-based permissions)

---

## Collection: `ideas`

**Purpose**: Store innovation ideas submitted by employees with status lifecycle and audit trail.

**Pydantic Schema**:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional

class Idea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    submitter_id: str  # References users._id
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=10, max_length=5000)
    category: str = Field(min_length=1, max_length=100)
    status: Literal["submitted", "under_review", "accepted", "rejected"] = "submitted"
    attachment_id: Optional[str] = None  # References files.files._id in GridFS
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    _version: int = 1  # Optimistic concurrency control

    class Config:
        populate_by_name = True
```

**MongoDB Document Structure**:

```json
{
  "_id": "660f7a40-a5b9-41d4-b836-557755440001",
  "submitter_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Improve employee onboarding process",
  "description": "Implement automated checklist system for new hire onboarding with role-based task assignments to reduce time-to-productivity.",
  "category": "process-improvement",
  "status": "submitted",
  "attachment_id": null,
  "created_at": ISODate("2026-05-12T11:30:00Z"),
  "updated_at": ISODate("2026-05-12T11:30:00Z"),
  "_version": 1
}
```

**Validation Rules**:
- `submitter_id`: Valid UUID referencing users collection
- `title`: Required, 1-500 characters
- `description`: Required, 10-5000 characters (detailed proposal)
- `category`: Required, 1-100 characters (e.g., "process-improvement", "product", "cost-reduction")
- `status`: Initial value "submitted"; transitions follow rules: submitted → under_review → {accepted, rejected}
- `attachment_id`: Null if no file attached; references GridFS file_id if present
- `_version`: Incremented on each status update (optimistic concurrency control per R-008)

**Status Transition Rules**:
- `submitted` → `under_review` (evaluator only)
- `under_review` → `accepted` (evaluator only, requires comment)
- `under_review` → `rejected` (evaluator only, requires comment)
- No other transitions allowed (specification FR-016)

**Indexes**:
```javascript
db.ideas.createIndex({ "submitter_id": 1, "created_at": -1 })
db.ideas.createIndex({ "status": 1 })
db.ideas.createIndex({ "created_at": -1 })
db.ideas.createIndex({ "_id": 1, "_version": 1 })  // Concurrency control
```

**Traceability**:
- Addresses FR-008 (idea creation), FR-009 (initial status), FR-010 (attachment), FR-015 (lifecycle statuses)

---

## Collection: `audit_logs`

**Purpose**: Immutable record of all governance and security-relevant actions.

**Pydantic Schema**:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional, Dict, Any

class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    actor_id: str  # References users._id
    actor_role: Literal["submitter", "evaluator", "admin"]
    action: Literal["login", "logout", "register", "idea_create", "idea_update", "decision_make", "decision_update"]
    resource_type: Literal["user", "idea", "session", "decision"]
    resource_id: str  # ID of affected resource
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    result: Literal["success", "failure"]
    details: Optional[Dict[str, Any]] = None  # Action-specific context
    comment: Optional[str] = None  # For decisions, the decision comment

    class Config:
        populate_by_name = True
```

**MongoDB Document Structure**:

```json
{
  "_id": "770g8b51-f40c-52e5-c937-668866551112",
  "actor_id": "550e8400-e29b-41d4-a716-446655440000",
  "actor_role": "submitter",
  "action": "idea_create",
  "resource_type": "idea",
  "resource_id": "660f7a40-a5b9-41d4-b836-557755440001",
  "timestamp": ISODate("2026-05-12T11:30:00Z"),
  "result": "success",
  "details": {
    "title": "Improve employee onboarding process",
    "category": "process-improvement"
  },
  "comment": null
}
```

**Example: Decision Entry**:

```json
{
  "_id": "880h9c62-g51d-63f6-d048-779977662223",
  "actor_id": "550e8400-e29b-41d4-a716-446655440011",
  "actor_role": "evaluator",
  "action": "decision_make",
  "resource_type": "decision",
  "resource_id": "660f7a40-a5b9-41d4-b836-557755440001",
  "timestamp": ISODate("2026-05-12T14:15:00Z"),
  "result": "success",
  "details": {
    "previous_status": "under_review",
    "new_status": "accepted"
  },
  "comment": "Excellent idea with high impact. Recommend implementation in Q3."
}
```

**Validation Rules**:
- `actor_id`: Valid UUID referencing users collection
- `action`: Predefined set of governance and security events
- `resource_id`: ID of the resource being acted upon
- `timestamp`: Recorded automatically at event time (not editable)
- `result`: success | failure (governs audit outcomes)
- `details`: JSON object capturing context (title, previous_status, etc.)
- `comment`: Required for decision actions (FR-017); may be null for other actions

**Indexes**:
```javascript
db.audit_logs.createIndex({ "actor_id": 1, "timestamp": -1 })
db.audit_logs.createIndex({ "action": 1, "timestamp": -1 })
db.audit_logs.createIndex({ "resource_id": 1, "timestamp": -1 })
db.audit_logs.createIndex({ "timestamp": -1 })  // Default sort
```

**Traceability**:
- Addresses FR-003 (login logging), FR-018 (audit trail), FR-020 (historical preservation)

---

## GridFS Collection: `fs.files` and `fs.chunks`

**Purpose**: Store attachment files (PDF, PNG, JPG) with metadata and integrity.

**Pydantic Schema** (for file metadata):

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class FileMetadata(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    filename: str = Field(min_length=1, max_length=255)
    content_type: Literal["application/pdf", "image/png", "image/jpeg"]
    size: int = Field(gt=0, le=5242880)  # 5 MB max
    upload_by: str  # References users._id
    idea_id: str  # References ideas._id
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    checksum: str  # SHA256 of file content for integrity

    class Config:
        populate_by_name = True
```

**MongoDB Document Structure** (`fs.files`):

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "filename": "proposal_v2.pdf",
  "contentType": "application/pdf",
  "length": 1024000,
  "uploadDate": ISODate("2026-05-12T11:35:00Z"),
  "metadata": {
    "upload_by": "550e8400-e29b-41d4-a716-446655440000",
    "idea_id": "660f7a40-a5b9-41d4-b836-557755440001",
    "checksum": "abc123def456..."
  }
}
```

**File Handling Rules**:
- Supported types: application/pdf, image/png, image/jpeg only
- Max size: 5 MB (5,242,880 bytes)
- File validation: Check magic bytes to prevent spoofed file types
- Storage: GridFS splits files into 255 KB chunks (`fs.chunks` collection)
- Deletion: Remove from `fs.files` and corresponding `fs.chunks` when idea is deleted (or marked archived)

**Indexes**:
```javascript
db.fs.files.createIndex({ "metadata.idea_id": 1 })
db.fs.files.createIndex({ "uploadDate": -1 })
```

**Traceability**:
- Addresses FR-010 (single attachment), FR-011 (type/size constraints), FR-012 (validation feedback)

---

## Collection: `refresh_tokens`

**Purpose**: Track valid refresh tokens and enable logout/revocation.

**Pydantic Schema**:

```python
from pydantic import BaseModel, Field
from datetime import datetime

class RefreshToken(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str  # References users._id
    token_jti: str  # Unique token ID for blacklisting
    issued_at: datetime
    expires_at: datetime
    is_revoked: bool = False  # Set to true on logout

    class Config:
        populate_by_name = True
```

**MongoDB Document Structure**:

```json
{
  "_id": "990i0d73-h62e-74g7-e159-880088773334",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "token_jti": "jti-xyz-abc-123-456",
  "issued_at": ISODate("2026-05-12T10:00:00Z"),
  "expires_at": ISODate("2026-05-13T10:00:00Z"),
  "is_revoked": false
}
```

**TTL Index** (auto-delete expired tokens):
```javascript
db.refresh_tokens.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 })
```

**Traceability**:
- Addresses FR-006 (logout and session invalidation)

---

## Data Integrity Constraints

| Entity | Constraint | Implementation |
|--------|-----------|-----------------|
| User | Email uniqueness | Unique index on email |
| User | Password never exposed | Excluded from all API responses |
| Idea | Submitter exists | Foreign key validation in Pydantic |
| Idea | Only 1 attachment | Application logic check before attach |
| Idea | Immutable creation fields | Read-only fields in API schema |
| File | Valid type & size | Validation in upload handler + magic byte check |
| Audit | Immutable records | No update/delete operations permitted |
| Token | Expiration enforcement | TTL index on refresh_tokens; JWT exp check on validation |

---

## Relationships Summary

```
users (1) ──── (N) ideas
  ↑                  ↓
  │           (0..1) attachment in GridFS
  │
  └──── (N) audit_logs
  │
  └──── (N) refresh_tokens
```

---

## Schema Validation Pipeline

**Pydantic Validation** (application layer):
1. Parse incoming JSON payload
2. Type coercion and field validation
3. Range checks (min/max length, file size)
4. Enum validation (roles, statuses)
5. Reject on validation error → 422 Unprocessable Entity

**MongoDB Validation** (database layer):
- Indexes enforce uniqueness constraints (email)
- TTL indexes auto-expire tokens
- Foreign key checks deferred to application logic (no DB-level FK in MongoDB)
- Audit collection write-only (immutability via permission)

**Rationale**:
- Pydantic provides runtime type safety and clear error messages
- MongoDB validates at storage layer only for critical constraints
- Separation of concerns: app validates logic, DB validates structure

---

## Phase 1 Schema Capabilities

| Requirement | Collection | Capability |
|-------------|-----------|------------|
| FR-001 Registration | users | Store new accounts with submitter role |
| FR-007 RBAC | users | role field enforces submitter/evaluator/admin |
| FR-008 Idea creation | ideas | Create with title, description, category |
| FR-009 Initial status | ideas | Default status="submitted" on creation |
| FR-010 Attachment support | ideas + GridFS | Single file per idea via attachment_id |
| FR-015 Lifecycle statuses | ideas | Supports submitted/under_review/accepted/rejected |
| FR-017 Decision comments | audit_logs | comment field on decision actions |
| FR-018 Audit trail | audit_logs | Immutable records of all actions |

---

## Performance Characteristics

| Operation | Collection | Indexed? | Expected Response Time |
|-----------|-----------|----------|----------------------|
| Find user by email | users | Yes (unique) | <10 ms |
| List ideas by submitter | ideas | Yes (submitter_id) | <50 ms (100 ideas) |
| Fetch single idea | ideas | Yes (_id primary) | <5 ms |
| List audit by resource | audit_logs | Yes (resource_id) | <100 ms (1000 entries) |
| Upload file | GridFS | Yes (idea_id) | <500 ms (5 MB file) |

---

**Schema Completion**: All entities required by canonical specification defined and indexed.  
**Next Artifacts**: contracts/, quickstart.md, ADRs, and complete plan.md

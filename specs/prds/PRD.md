# Product Requirements Document (PRD)

## Project
InnovatEPAM Portal - Phase 1 MVP

## Version
1.0

## Date
2026-05-12

## Tech and Architecture Context
- Backend: Python + FastAPI
- Database: MongoDB Atlas
- Validation/Schemas: Pydantic models
- Source of truth references:
  - docs/memory-bank/projectBrief.md
  - docs/memos/engineering_standards.md
  - specs/adrs/ADR-001-tech-stack.md

## 1. Problem Statement
Employees need a simple and auditable way to submit innovation ideas and receive transparent review outcomes. Current ad hoc channels make ideas hard to track, review consistently, and evaluate fairly.

## 2. Goal (Phase 1 MVP)
Deliver a working MVP that supports:
1. User authentication with role distinction (submitter, admin)
2. Idea submission with one file attachment and idea browsing
3. Evaluation workflow with status transitions and admin decision comments

## 3. In Scope
- Register, login, logout
- Role-based behavior (submitter vs admin)
- Create idea (title, description, category)
- Single attachment per idea
- List ideas and view idea details
- Admin updates idea status: submitted -> under review -> accepted/rejected
- Admin provides comment when accepting/rejecting

## 4. Out of Scope (Phase 1)
- Multi-stage review chains
- Scoring/rating system
- Blind review
- Multiple attachments per idea
- Draft autosave
- OAuth/social login

## 5. Feature Requirements and Acceptance Criteria

### Feature A: User Management
#### Functional Requirements
- Users can register with email and password.
- Registered users can log in and receive an auth token/session.
- Logged-in users can log out (token/session invalidation strategy defined in implementation).
- System supports two roles: submitter and admin.

#### Acceptance Criteria
- AC-A1 Register success:
  - Given a new email and valid password
  - When user submits registration
  - Then account is created with role=submitter by default
  - And response excludes raw password fields.
- AC-A2 Register validation:
  - Given invalid email or weak/missing password
  - When user submits registration
  - Then API returns validation error with clear message.
- AC-A3 Login success:
  - Given valid credentials
  - When user logs in
  - Then API returns authenticated context (token/session metadata).
- AC-A4 Login failure:
  - Given invalid credentials
  - When user logs in
  - Then API returns unauthorized error.
- AC-A5 Logout:
  - Given authenticated user
  - When user logs out
  - Then session/token is invalidated per auth strategy.
- AC-A6 Role enforcement:
  - Given submitter user
  - When attempting admin-only action
  - Then API returns forbidden error.

### Feature B: Idea Submission System
#### Functional Requirements
- Submitter can create idea with title, description, category.
- Each idea can include one file attachment.
- Users can list ideas.
- Users can view single idea details.

#### Acceptance Criteria
- AC-B1 Create idea:
  - Given authenticated submitter and valid payload
  - When creating idea
  - Then idea is stored with status=submitted.
- AC-B2 Create idea validation:
  - Given missing title/description/category
  - When creating idea
  - Then API returns validation error.
- AC-B3 Attachment rule:
  - Given one attachment
  - When creating/updating submission in Phase 1
  - Then exactly one attachment is accepted
  - And additional files are rejected.
- AC-B4 List ideas:
  - Given ideas exist
  - When requesting list endpoint
  - Then API returns paginated or bounded list with basic fields.
- AC-B5 View idea details:
  - Given valid idea id
  - When requesting details
  - Then API returns idea content, status, creator summary, and attachment metadata.

### Feature C: Evaluation Workflow
#### Functional Requirements
- Idea has lifecycle states: submitted, under review, accepted, rejected.
- Admin can move idea into under review.
- Admin can accept/reject with mandatory comment for final decisions.
- Evaluation actions are recorded with actor and timestamp.

#### Acceptance Criteria
- AC-C1 Status initialization:
  - Given newly created idea
  - When persisted
  - Then status defaults to submitted.
- AC-C2 Under review transition:
  - Given admin and idea in submitted
  - When admin starts review
  - Then status becomes under review.
- AC-C3 Final decision transition:
  - Given admin and idea in under review
  - When admin accepts or rejects with comment
  - Then status updates accordingly
  - And decision comment is saved.
- AC-C4 Decision comment required:
  - Given accept/reject request without comment
  - When admin submits decision
  - Then API returns validation error.
- AC-C5 Authorization:
  - Given non-admin user
  - When calling evaluation endpoints
  - Then API returns forbidden error.

## 6. Epic Breakdown

### Epic 1: Authentication and Access Control
Deliver secure identity management and role-based authorization.
- Success signal: users can register/login/logout; admin-only boundaries are enforced.

### Epic 2: Idea Submission and Retrieval
Deliver core submission flow with one attachment and idea visibility.
- Success signal: submitter can create and retrieve ideas with attachment metadata.

### Epic 3: Evaluation and Decision Lifecycle
Deliver admin-led status management and comments-backed decisions.
- Success signal: admin can perform valid transitions and record decisions.

## 7. User Stories (INVEST-Aligned)

## Story-001: Register account
- Epic: Epic 1
- As a potential submitter, I want to register with email/password so that I can access the portal.
- Acceptance Criteria:
  - New valid email creates user with default role submitter.
  - Duplicate email is rejected.
  - Password is stored hashed, never plaintext.
- INVEST check:
  - Independent: Yes (can be built without login flow).
  - Negotiable: Yes (password policy can evolve).
  - Valuable: Yes (entry point for all users).
  - Estimable: Yes.
  - Small: Yes.
  - Testable: Yes.
- Data model sketch (Pydantic/MongoDB):
```python
class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class UserInDB(BaseModel):
    id: PyObjectId = Field(alias="_id")
    email: EmailStr
    password_hash: str
    role: Literal["submitter", "admin"] = "submitter"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
```

## Story-002: Login and logout
- Epic: Epic 1
- As a registered user, I want to log in and log out so that I can securely manage my session.
- Acceptance Criteria:
  - Valid credentials return auth token/session response.
  - Invalid credentials return unauthorized.
  - Logout invalidates active session/token.
- INVEST check: I/N/V/E/S/T = Yes.
- Data model sketch:
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthToken(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int

class SessionInDB(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    token_id: str
    expires_at: datetime
    revoked_at: datetime | None = None
    created_at: datetime
```

## Story-003: Role-based authorization guard
- Epic: Epic 1
- As a product owner, I want admin-only endpoints protected so that only admins can evaluate ideas.
- Acceptance Criteria:
  - Admin-only endpoints return 403 for submitter.
  - Admin role can access evaluation endpoints.
- INVEST check: I/N/V/E/S/T = Yes.
- Data model sketch:
```python
class UserRole(BaseModel):
    user_id: PyObjectId
    role: Literal["submitter", "admin"]
```

## Story-004: Create idea with required fields
- Epic: Epic 2
- As a submitter, I want to submit an idea with title/description/category so that it can be evaluated.
- Acceptance Criteria:
  - Valid payload creates idea with status=submitted.
  - Missing required fields fail validation.
- INVEST check: I/N/V/E/S/T = Yes.
- Data model sketch:
```python
class IdeaCreate(BaseModel):
    title: constr(min_length=3, max_length=150)
    description: constr(min_length=10, max_length=5000)
    category: constr(min_length=2, max_length=50)

class IdeaInDB(BaseModel):
    id: PyObjectId = Field(alias="_id")
    title: str
    description: str
    category: str
    status: Literal["submitted", "under_review", "accepted", "rejected"] = "submitted"
    created_by: PyObjectId
    attachment: dict | None = None
    created_at: datetime
    updated_at: datetime
```

## Story-005: Attach one file to idea
- Epic: Epic 2
- As a submitter, I want to attach one file to my idea so that supporting evidence can be reviewed.
- Acceptance Criteria:
  - One file attachment is accepted and metadata stored.
  - More than one file is rejected.
  - File size is restricted to a maximum of 5MB.
  - Supported formats are limited to PDF, PNG, and JPG/JPEG.
  - Server-side validation must reject invalid sizes or MIME types.
- INVEST check: I/N/V/E/S/T = Yes.
- Data model sketch:
```python
class AttachmentMeta(BaseModel):
    file_name: str
    content_type: str
    size_bytes: int
    storage_key: str
    uploaded_at: datetime
```

## Story-006: List and view ideas
- Epic: Epic 2
- As a user, I want to list ideas and view details so that I can track submissions and outcomes.
- Acceptance Criteria:
  - List endpoint returns bounded list and key summary fields.
  - Detail endpoint returns full idea and evaluation metadata.
- INVEST check: I/N/V/E/S/T = Yes.
- Data model sketch:
```python
class IdeaListItem(BaseModel):
    id: str
    title: str
    category: str
    status: str
    created_at: datetime

class IdeaDetail(BaseModel):
    id: str
    title: str
    description: str
    category: str
    status: str
    attachment: AttachmentMeta | None = None
    latest_evaluation: dict | None = None
```

## Story-007: Move idea to under review
- Epic: Epic 3
- As an admin, I want to move submitted ideas to under review so that evaluation work is visible.
- Acceptance Criteria:
  - Transition allowed from submitted to under review only.
  - Transition event records actor and timestamp.
- INVEST check: I/N/V/E/S/T = Yes.
- Data model sketch:
```python
class EvaluationTransition(BaseModel):
    idea_id: PyObjectId
    from_status: Literal["submitted", "under_review", "accepted", "rejected"]
    to_status: Literal["under_review"]
    comment: str | None = None
    decided_by: PyObjectId
    decided_at: datetime
```

## Story-008: Accept/reject with admin comment
- Epic: Epic 3
- As an admin, I want to accept or reject an idea with comments so that submitters receive clear decisions.
- Acceptance Criteria:
  - Allowed only from under review to accepted/rejected.
  - Comment required for accept/reject.
  - Decision history is stored.
- INVEST check: I/N/V/E/S/T = Yes.
- Data model sketch:
```python
class EvaluationDecisionRequest(BaseModel):
    decision: Literal["accepted", "rejected"]
    comment: constr(min_length=3, max_length=2000)

class EvaluationInDB(BaseModel):
    id: PyObjectId = Field(alias="_id")
    idea_id: PyObjectId
    status_from: Literal["submitted", "under_review", "accepted", "rejected"]
    status_to: Literal["under_review", "accepted", "rejected"]
    comment: str | None = None
    decided_by: PyObjectId
    decided_at: datetime
```

## 8. Aggregate Data Model Sketches (MongoDB Collections)

### users collection
- _id: ObjectId
- email: string (unique index)
- password_hash: string
- role: string enum [submitter, admin]
- is_active: bool
- created_at: datetime
- updated_at: datetime

### ideas collection
- _id: ObjectId
- title: string
- description: string
- category: string
- status: string enum [submitted, under_review, accepted, rejected]
- created_by: ObjectId (users._id)
- attachment: subdocument or null
- created_at: datetime
- updated_at: datetime

### evaluations collection
- _id: ObjectId
- idea_id: ObjectId (ideas._id)
- status_from: string enum
- status_to: string enum
- comment: string or null
- decided_by: ObjectId (users._id)
- decided_at: datetime

## 9. Non-Functional Requirements (Phase 1)
- Security:
  - Password hashing required.
  - Role checks required on protected endpoints.
- Observability:
  - Log auth failures and decision actions with safe metadata.
- Quality:
  - TDD-first implementation.
  - Mutation testing target >= 75%.
  - Story-level acceptance tests required before completion.

## 10. Story Execution Order (for TDD implementation)
1. Story-001 Register account
2. Story-002 Login and logout
3. Story-003 Role-based authorization guard
4. Story-004 Create idea with required fields
5. Story-005 Attach one file to idea
6. Story-006 List and view ideas
7. Story-007 Move idea to under review
8. Story-008 Accept/reject with admin comment

## 11. Definition of Done (per Story)
- Acceptance criteria implemented and passing.
- Unit/integration tests written first (RED) then passing (GREEN), followed by refactor.
- API contract and schema updates reflected in code.
- No regressions in existing story tests.
- Traceability maintained to this PRD.

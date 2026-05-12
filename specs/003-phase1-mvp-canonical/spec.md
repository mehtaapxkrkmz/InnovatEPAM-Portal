# Feature Specification: InnovatEPAM Portal Phase 1 MVP (Canonical)

**Feature Branch**: `[003-phase1-mvp-canonical]`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "Regenerate the canonical tool-authored specification for InnovatEPAM Portal Phase 1 MVP under current SpecKit flow"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Identity and Access (Priority: P1)

Employees can register, sign in, and sign out, and the system enforces role-based access so submitters and evaluators/admins can only perform permitted actions.

**Why this priority**: Identity and access controls are required before any secure idea submission or evaluation can occur.

**Independent Test**: A new employee registers and signs in successfully, receives role-appropriate access, and can sign out so previously valid session credentials no longer grant access.

**Acceptance Scenarios**:

1. **Given** a new employee with valid registration details, **When** they complete registration, **Then** an account is created with submitter permissions by default.
2. **Given** a registered employee with valid credentials, **When** they sign in, **Then** they receive an authenticated session with short-lived access and refresh credentials.
3. **Given** any failed sign-in attempt, **When** credentials are invalid, **Then** the attempt is recorded in the security log and access is denied.
4. **Given** repeated failed sign-in attempts, **When** attempts continue in Phase 1, **Then** attempts continue to be logged and are not automatically blocked.
5. **Given** an authenticated user, **When** they sign out, **Then** the session is ended and protected actions require fresh authentication.
6. **Given** a submitter, **When** they attempt an evaluator/admin-only action, **Then** the action is denied.

---

### User Story 2 - Idea Submission and Visibility (Priority: P1)

Submitters can create ideas with required business fields, optionally attach one supporting file within allowed constraints, and view only their own ideas and idea details.

**Why this priority**: Capturing ideas is the core product value, and ownership-based visibility protects idea confidentiality in Phase 1.

**Independent Test**: A submitter creates an idea with required fields, optionally includes one valid attachment, and can list/view only their own ideas.

**Acceptance Scenarios**:

1. **Given** an authenticated submitter, **When** they submit an idea with title, description, and category, **Then** the idea is created in `submitted` status.
2. **Given** an idea submission with one PDF, PNG, or JPG file no larger than 5MB, **When** the file is included, **Then** the idea is saved with that single attachment.
3. **Given** an idea submission with an unsupported file type or file size above 5MB, **When** submission is attempted, **Then** submission is rejected with a clear validation message.
4. **Given** an idea that already has one attachment, **When** another attachment is attempted, **Then** the second attachment is rejected.
5. **Given** an authenticated submitter, **When** they list or view ideas, **Then** only ideas they created are returned.
6. **Given** an authenticated evaluator/admin, **When** they list or view ideas, **Then** all ideas are available for governance tasks.

---

### User Story 3 - Evaluation Governance and Decisions (Priority: P1)

Evaluators/admins can move ideas through the controlled lifecycle, provide mandatory decision comments, and leave a complete auditable history of governance actions.

**Why this priority**: The business outcome of the portal depends on transparent, accountable evaluation and decision-making.

**Independent Test**: An evaluator/admin transitions an idea through allowed statuses, records a decision with mandatory comments, and audit history captures each governance event.

**Acceptance Scenarios**:

1. **Given** an idea in `submitted` status, **When** an evaluator/admin starts review, **Then** status changes to `under_review`.
2. **Given** an idea in `under_review` status, **When** an evaluator/admin makes a final decision, **Then** status changes to either `accepted` or `rejected`.
3. **Given** any invalid status transition request, **When** transition rules are violated, **Then** the request is rejected and status remains unchanged.
4. **Given** an evaluator/admin final decision, **When** comment text is missing or blank, **Then** the decision is rejected.
5. **Given** a valid evaluator/admin decision, **When** it is recorded, **Then** the audit trail stores actor, action, comment, timestamp, and resulting status.
6. **Given** a submitter, **When** they attempt to make governance decisions, **Then** the action is denied.

### Edge Cases

- Registration is attempted for an email already tied to an existing account.
- Sign-in attempts continue to fail rapidly for the same account in a short period.
- Attachment file size is exactly 5MB at boundary.
- Attachment file extension appears valid but content is not a valid file of the declared type.
- Two evaluators/admins attempt governance actions on the same idea at nearly the same time.
- An idea is requested by a submitter who is not its owner.
- A final decision is attempted directly from `submitted` without entering `under_review`.
- A decision comment contains only whitespace.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow employee registration and create new accounts with the default role of `submitter`.
- **FR-002**: System MUST allow registered users to log in using valid credentials and deny invalid authentication attempts.
- **FR-003**: System MUST log each login attempt, including failed attempts, for Phase 1 monitoring and audit purposes.
- **FR-004**: System MUST NOT automatically block login attempts in Phase 1 based only on repeated failures.
- **FR-005**: System MUST issue short-lived access credentials and refresh credentials for authenticated sessions.
- **FR-006**: System MUST allow authenticated users to log out and invalidate the active session.
- **FR-007**: System MUST enforce role-based permissions for at least `submitter` and `evaluator/admin` roles.
- **FR-008**: System MUST allow submitters to create ideas with required fields: title, description, and category.
- **FR-009**: System MUST initialize each new idea in `submitted` lifecycle status.
- **FR-010**: System MUST support at most one file attachment per idea.
- **FR-011**: System MUST accept attachments only in PDF, PNG, or JPG formats and only when size is less than or equal to 5MB.
- **FR-012**: System MUST reject idea submissions or attachment operations that violate attachment type, size, or count constraints with clear user-facing validation messages.
- **FR-013**: System MUST allow submitters to list and view only ideas they created.
- **FR-014**: System MUST allow evaluator/admin users to list and view all ideas.
- **FR-015**: System MUST support lifecycle statuses `submitted`, `under_review`, `accepted`, and `rejected`.
- **FR-016**: System MUST allow lifecycle transitions only as `submitted -> under_review -> accepted/rejected`.
- **FR-017**: System MUST require a non-empty comment for each evaluator/admin decision that sets final outcome (`accepted` or `rejected`).
- **FR-018**: System MUST record an audit trail entry for each governance action, including actor role, actor identity, action type, comment (if provided), timestamp, and resulting status.
- **FR-019**: System MUST prevent submitters from performing evaluator/admin-only governance actions.
- **FR-020**: System MUST preserve historical governance entries so decision history remains reviewable over time.

### Key Entities *(include if feature involves data)*

- **User**: Registered employee identity with role assignment and authentication state.
- **Session Credential Set**: Access and refresh credentials associated with a successful login session.
- **Idea**: User-submitted innovation proposal containing title, description, category, owner, and current lifecycle status.
- **Attachment**: Optional single supporting file bound to an idea, with type and size constraints.
- **Evaluation Decision**: Governance decision event produced by evaluator/admin users with mandatory decision comment for final outcomes.
- **Audit Entry**: Immutable historical record of governance and security-relevant actions with actor and timestamp context.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 95% of valid registration and login attempts complete successfully on first attempt during acceptance testing.
- **SC-002**: 100% of invalid login attempts are denied and logged, and 0% are auto-blocked in Phase 1.
- **SC-003**: 100% of ideas created through the primary submission flow include title, description, category, and initial `submitted` status.
- **SC-004**: 100% of attachment policy violations (type, size, or second attachment) are rejected with clear validation feedback.
- **SC-005**: 100% of submitter idea list/detail views show only owner-created ideas during role-based access tests.
- **SC-006**: 100% of tested lifecycle transitions outside `submitted -> under_review -> accepted/rejected` are rejected.
- **SC-007**: 100% of final evaluator/admin decisions require a non-empty comment and create an audit entry.
- **SC-008**: In user acceptance walkthroughs, evaluators/admins can complete review and decision for a valid idea in under 3 minutes.

## Assumptions

- Phase 1 has two permission tiers for governance behavior: `submitter` and `evaluator/admin`.
- New users are onboarded as submitters unless explicitly changed by authorized operations.
- Ideas are individually owned by the submitter who created them.
- Phase 1 does not include automated lockout controls for repeated login failure.
- Attachment handling in Phase 1 is limited to one file per idea and does not include multi-file bundles.
- Notification and analytics enhancements beyond auditability are deferred to later phases.

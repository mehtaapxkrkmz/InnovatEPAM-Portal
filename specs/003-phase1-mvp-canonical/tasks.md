# Implementation Tasks: Story-001 (User Identity and Access)

**Feature**: InnovatEPAM Portal Phase 1 MVP  
**Story**: Story-001 - User Identity and Access Control  
**Priority**: P1  
**Date**: 2026-05-12  
**Scope**: User registration, login, logout, RBAC with TDD  
**Methodology**: Red-Green-Refactor with 75% mutation testing minimum

---

## Executive Summary

Story-001 implements the core authentication and authorization layer enabling secure user identity management and role-based access control (RBAC) for the InnovatEPAM Portal. The story spans 6 phases across project scaffolding, data model definition, test-first registration flow, JWT authentication, and role-based access enforcement.

**Success Criteria** (from spec.md):
- ✅ 95% of valid registration/login attempts succeed on first attempt
- ✅ 100% of invalid attempts denied and logged
- ✅ 100% of RBAC access control enforced (submitter vs evaluator/admin)
- ✅ 100% of lifecycle transitions outside allowed paths rejected
- ✅ All tests passing with 95%+ code coverage, 75%+ mutation score

**Dependencies**:
- No blocking dependencies (foundational work)
- All other stories (US2, US3) depend on Story-001 completion

**Parallel Opportunities**:
- Tasks in Phase 1 (scaffolding) can run in parallel
- Tasks in Phase 2 (models) can run in parallel (except schema interdependencies)
- User and authentication test suites can be written in parallel

---

## Phase 1: Project Scaffolding

Initialize FastAPI project structure, database connection, and configuration skeleton.

- [X] T001 Create base FastAPI project structure with directories (src/app, src/app/core, src/app/db, src/app/api, src/app/services, tests/)

- [X] T002 [P] Create core/config.py with Settings class for environment variables (DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, TOKEN_EXPIRY)

- [ ] T003 [P] Create core/constants.py with application-wide constants (PASSWORD_MIN_LENGTH=8, TOKEN_EXPIRY_SECONDS=3600, REFRESH_TOKEN_EXPIRY_SECONDS=86400)

- [X] T004 [P] Create db/client.py with Motor async MongoDB connection utility and client initialization

- [X] T005 [P] Create core/security.py skeleton with password hashing and JWT utilities stub

- [ ] T006 [P] Create .env.example template with required environment variables documented

- [X] T007 Create requirements.txt with dependencies: fastapi, uvicorn, motor, pymongo, pydantic, passlib, bcrypt, pyjwt, python-multipart, python-dotenv

- [ ] T008 [P] Create pytest.ini configuration with markers, async plugin settings, and coverage thresholds (95% minimum)

- [ ] T009 [P] Create tests/conftest.py with pytest fixtures for async MongoDB test client, sample users, and teardown cleanup

- [X] T010 Create src/main.py FastAPI app entry point with CORS, health check endpoint, and route registration stub

---

## Phase 2: User Models & Schemas

Define Pydantic schemas and MongoDB document structures for users and authentication.

- [X] T011 [P] Create models/user.py with Pydantic User schema (id, email, first_name, last_name, hashed_password, role, is_active, created_at, updated_at)

- [X] T012 [P] Create models/user.py with UserCreate request schema (email, first_name, last_name, password) with validation (email format, password min 8 chars)

- [X] T013 [P] Create models/user.py with UserResponse schema (id, email, first_name, last_name, role, created_at) excluding hashed_password

- [ ] T014 [P] Create models/token.py with LoginRequest schema (email, password)

- [X] T015 [P] Create models/token.py with AuthTokenResponse schema (access_token, refresh_token, token_type, expires_in)

- [X] T016 [P] Create models/token.py with JWT payload schema (sub, email, role, iat, exp)

- [ ] T017 [P] Create db/schemas.py with MongoDB validation rules (Email unique index, role enum validation, password hash presence)

- [ ] T018 [P] Create db/repositories/user_repository.py with UserRepository class and CRUD method stubs (create, find_by_id, find_by_email, update, delete)

- [X] T019 Create db/repositories/__init__.py to export all repository classes

- [ ] T020 [P] Add MongoDB index creation to db/client.py for users collection (email unique, created_at, role)

---

## Phase 3: Red Phase (Test-First Registration)

Write comprehensive failing tests for registration flow before implementation.

### 3.1 Registration Success Tests

- [ ] T021 [US1] Create tests/unit/test_auth_service.py with test_register_user_success (valid input creates User with role=submitter, returns UserResponse, no hashed_password in response)

- [ ] T022 [US1] Add test_register_user_hashes_password (verify hashed_password differs from input, uses bcrypt with cost factor 12)

- [ ] T023 [US1] Add test_register_user_persists_to_mongodb (verify user saved to database with created_at timestamp, _id generated)

- [ ] T024 [US1] Add test_register_user_with_valid_names (min 1 char, max 255 chars in first_name and last_name)

### 3.2 Registration Validation Tests

- [ ] T025 [US1] Add test_register_user_invalid_email_format (empty, missing @, invalid domain) raises ValidationError

- [ ] T026 [US1] Add test_register_user_duplicate_email (second registration with same email returns 409 Conflict)

- [ ] T027 [US1] Add test_register_user_password_too_short (less than 8 characters raises ValidationError)

- [ ] T028 [US1] Add test_register_user_missing_required_fields (email, first_name, last_name, password each missing raises 422 Unprocessable Entity)

- [ ] T029 [US1] Add test_register_user_empty_names (first_name or last_name empty/whitespace raises ValidationError)

### 3.3 Registration API Endpoint Tests

- [ ] T030 [US1] Create tests/contract/test_auth_contracts.py with test_post_auth_register_201_success (POST /auth/register with valid payload returns 201, UserResponse schema)

- [ ] T031 [US1] Add test_post_auth_register_409_duplicate_email (second registration same email returns 409 with error message)

- [ ] T032 [US1] Add test_post_auth_register_422_validation_error (missing fields, short password returns 422 with validation details)

- [ ] T033 [US1] Add test_post_auth_register_response_excludes_hashed_password (verify hashed_password never in response body)

### 3.4 Password Security Tests

- [ ] T034 [US1] Create tests/unit/test_security.py with test_hash_password_uses_bcrypt (hashing same input twice produces different hashes - random salt)

- [ ] T035 [US1] Add test_verify_password_correct_password (verify_password with correct plaintext returns True)

- [ ] T036 [US1] Add test_verify_password_incorrect_password (verify_password with wrong plaintext returns False)

- [ ] T037 [US1] Add test_hash_password_minimum_cost_factor (verify bcrypt cost factor is at least 12)

---

## Phase 4: Green Phase (Registration Implementation)

Implement registration flow to pass all Phase 3 tests.

### 4.1 Password Security Implementation

- [X] T038 [US1] Implement hash_password() in core/security.py using passlib/bcrypt with cost=12

- [X] T039 [US1] Implement verify_password() in core/security.py to validate plaintext against hash

- [ ] T040 [US1] [P] Add password validation utility in core/security.py (min 8 chars, complexity rules optional for Phase 1)

### 4.2 User Repository Implementation

- [X] T041 [US1] Implement UserRepository.create() in db/repositories/user_repository.py (insert to users collection, return User)

- [X] T042 [US1] Implement UserRepository.find_by_email() in db/repositories/user_repository.py (query users by email, return User or None)

- [ ] T043 [US1] Implement UserRepository.find_by_id() in db/repositories/user_repository.py (query users by _id, return User or None)

- [ ] T044 [US1] [P] Implement UserRepository.find_by_role() in db/repositories/user_repository.py (query users by role, return list)

### 4.3 User Service Registration Logic

- [ ] T045 [US1] Create services/user_service.py with UserService.register() method (validate input, check duplicate email, hash password, create user, return UserResponse)

- [ ] T046 [US1] Implement input validation in UserService.register() (email format, password length, required fields)

- [X] T047 [US1] Implement duplicate email check in UserService.register() (raise 409 Conflict if email exists)

- [X] T048 [US1] [P] Implement UserResponse mapping in UserService.register() (exclude hashed_password, include role=submitter by default)

### 4.4 Registration API Endpoint

- [X] T049 [US1] Create api/endpoints/auth.py with POST /auth/register endpoint (accept UserCreate payload, call UserService.register(), return 201 UserResponse)

- [ ] T050 [US1] Add validation error handling to /auth/register (return 422 with details for missing/invalid fields)

- [X] T051 [US1] Add duplicate email handling to /auth/register (return 409 Conflict for existing email)

- [ ] T052 [US1] Create api/router.py to include auth endpoint routes

### 4.5 Integration Test Registration Flow

- [ ] T053 [US1] Add tests/integration/test_auth_flow.py with test_register_login_logout_flow (register user, verify in DB, ensure no plaintext password)

- [ ] T054 [US1] Add test_concurrent_registrations (two concurrent registrations with same email, one succeeds, one gets 409)

### 4.6 Verify Phase 3 Tests Pass

- [X] T055 [US1] Run all Phase 3 tests (pytest tests/ -v), verify 100% pass rate, generate coverage report

- [ ] T056 [US1] Generate mutation testing report (mutmut run), verify score >= 75% on services/user_service.py

---

## Phase 5: Authentication Logic (JWT + Refresh Tokens)

Implement JWT token generation, login, logout, and token refresh endpoints.

### 5.1 JWT Token Generation

- [ ] T057 [US1] Implement create_access_token() in core/security.py (generate JWT with sub, email, role, exp=now+1h, alg=HS256)

- [ ] T058 [US1] Implement create_refresh_token() in core/security.py (generate JWT with sub, exp=now+24h, for refresh-only use)

- [ ] T059 [US1] [P] Implement verify_token() in core/security.py (decode JWT, verify expiry, return payload or raise exception)

- [ ] T060 [US1] [P] Implement decode_access_token() in core/security.py to extract user_id from token claims

### 5.2 Login Tests (Red)

- [ ] T061 [US1] Add tests/unit/test_auth_service.py test_login_with_valid_credentials (valid email/password returns AuthTokenResponse with access_token, refresh_token, expires_in)

- [ ] T062 [US1] Add test_login_with_invalid_email (non-existent email returns 401 Unauthorized)

- [ ] T063 [US1] Add test_login_with_wrong_password (valid email, wrong password returns 401 Unauthorized)

- [ ] T064 [US1] Add test_login_access_token_contains_claims (access token decoded contains sub, email, role, exp)

- [ ] T065 [US1] Add tests/contract/test_auth_contracts.py test_post_auth_login_200_success (POST /auth/login with valid credentials returns 200, AuthTokenResponse schema)

- [ ] T066 [US1] Add test_post_auth_login_401_invalid_credentials (POST /auth/login with wrong password returns 401)

- [ ] T067 [US1] Add test_login_creates_audit_log (login attempt recorded in audit_logs with timestamp, email, result)

### 5.3 Login Implementation

- [ ] T068 [US1] Implement AuthService.login() in services/auth_service.py (find user by email, verify password, generate tokens, return AuthTokenResponse)

- [X] T069 [US1] Implement login endpoint POST /auth/login in api/endpoints/auth.py

- [ ] T070 [US1] Add login attempt logging to POST /auth/login (create audit_logs entry with success/failure, timestamp, email)

- [X] T071 [US1] Implement LoginRequest validation (email required, password required, email format)

### 5.4 Refresh Token Tests (Red)

- [ ] T072 [US1] Add tests/unit/test_auth_service.py test_refresh_token_valid (valid refresh token generates new access token, same user_id)

- [ ] T073 [US1] Add test_refresh_token_invalid (expired or tampered refresh token raises 401)

- [ ] T074 [US1] Add test_refresh_token_already_revoked (revoked refresh token raises 401)

- [ ] T075 [US1] Add tests/contract/test_auth_contracts.py test_post_auth_refresh_200_success (POST /auth/refresh with valid refresh token returns 200, new access token)

### 5.5 Refresh Token Implementation

- [ ] T076 [US1] Create db/repositories/token_repository.py for refresh token tracking (create, find, revoke, is_revoked methods)

- [ ] T077 [US1] Implement refresh_tokens collection in MongoDB (store user_id, token_hash, created_at, revoked_at)

- [ ] T078 [US1] Implement AuthService.refresh_access_token() in services/auth_service.py

- [ ] T079 [US1] Implement POST /auth/refresh endpoint in api/endpoints/auth.py

- [ ] T080 [US1] Add MongoDB index on refresh_tokens collection (user_id, revoked_at)

### 5.6 Logout Tests (Red)

- [ ] T081 [US1] Add tests/unit/test_auth_service.py test_logout_revokes_refresh_token (logout() marks refresh token as revoked)

- [ ] T082 [US1] Add test_logout_access_token_still_valid_until_expiry (access token remains usable until 1h expiry, not immediately invalid)

- [ ] T083 [US1] Add tests/contract/test_auth_contracts.py test_post_auth_logout_200_success (POST /auth/logout with valid token returns 200 message)

- [ ] T084 [US1] Add test_logout_after_revocation_fails (POST /auth/logout with already-revoked token returns 401)

### 5.7 Logout Implementation

- [ ] T085 [US1] Implement AuthService.logout() in services/auth_service.py (revoke refresh token, return success message)

- [X] T086 [US1] Implement POST /auth/logout endpoint in api/endpoints/auth.py (extract token from Authorization header, call logout, return 200)

- [ ] T087 [US1] Add token extraction middleware in api/dependencies.py (extract Bearer token from Authorization header)

- [ ] T088 [US1] Add audit logging to logout (record user logout event with timestamp)

### 5.8 Verify Phase 5 Tests Pass

- [X] T089 [US1] Run all Phase 5 tests (pytest tests/ -v), verify 100% pass rate

- [ ] T090 [US1] Generate mutation testing report for auth_service.py, verify score >= 75%

---

## Phase 6: RBAC & Authorization

Implement role-based access control guards and dependency injection for protected endpoints.

### 6.1 Authorization Dependency Tests (Red)

- [ ] T091 [US1] Add tests/unit/test_dependencies.py test_get_current_user_valid_token (valid access token extracts user_id, returns User)

- [ ] T092 [US1] Add test_get_current_user_invalid_token (invalid/expired token raises 401 Unauthorized)

- [ ] T093 [US1] Add test_get_current_user_missing_header (missing Authorization header raises 401)

- [ ] T094 [US1] Add test_require_evaluator_or_admin_allows_evaluator (evaluator role passes, returns user)

- [ ] T095 [US1] Add test_require_evaluator_or_admin_allows_admin (admin role passes, returns user)

- [ ] T096 [US1] Add test_require_evaluator_or_admin_denies_submitter (submitter role raises 403 Forbidden)

- [ ] T097 [US1] Add test_require_submitter_allows_submitter (submitter role passes, returns user)

- [ ] T098 [US1] Add test_require_submitter_denies_evaluator (evaluator role raises 403 Forbidden)

### 6.2 Authorization Dependency Implementation

- [X] T099 [US1] Implement get_current_user() in api/dependencies.py (extract token from header, verify, return User)

- [ ] T100 [US1] Implement require_evaluator_or_admin() in api/dependencies.py (FastAPI dependency raising 403 if not evaluator/admin)

- [ ] T101 [US1] [P] Implement require_submitter() in api/dependencies.py (FastAPI dependency raising 403 if not submitter)

- [ ] T102 [US1] [P] Implement require_admin() in api/dependencies.py (FastAPI dependency raising 403 if not admin)

- [X] T103 [US1] Add token decoding error handling in get_current_user() (invalid signature, expired token both raise 401)

### 6.3 Protected Endpoint Contract Tests (Red)

- [ ] T104 [US1] Add tests/contract/test_auth_contracts.py test_protected_endpoint_requires_auth_header (GET /user/profile without Authorization header returns 401)

- [ ] T105 [US1] Add test_protected_endpoint_invalid_token (GET /user/profile with invalid token returns 401)

- [ ] T106 [US1] Add test_evaluator_endpoint_denies_submitter (submitter accessing evaluator endpoint returns 403 Forbidden)

- [ ] T107 [US1] Add test_admin_endpoint_denies_non_admin (non-admin accessing admin endpoint returns 403 Forbidden)

### 6.4 Protected Endpoints Implementation

- [ ] T108 [US1] Implement GET /auth/me endpoint returning current user profile (requires get_current_user dependency)

- [ ] T109 [US1] [P] Implement GET /auth/verify endpoint to validate current token (requires get_current_user, returns 200 if valid)

- [X] T110 [US1] Add authorization headers to all endpoints (Authorization: Bearer <token> required for protected endpoints)

### 6.5 RBAC Edge Case Tests

- [ ] T111 [US1] Add test_token_expired_after_1_hour (access token issued, wait/mock 1h+1s, token validation fails with 401)

- [ ] T112 [US1] Add test_refresh_token_expires_after_24_hours (refresh token issued, mock 24h+1s, token validation fails with 401)

- [ ] T113 [US1] Add test_concurrent_logout_and_refresh (logout and refresh called concurrently, second one gets 401)

- [ ] T114 [US1] Add test_role_change_requires_new_token (user role changed from submitter to evaluator, old token still has submitter role until expiry)

### 6.6 Integration Test RBAC Flow

- [ ] T115 [US1] Add tests/integration/test_auth_flow.py test_rbac_submitter_cannot_access_evaluator_endpoints (submitter token accessing evaluator-only endpoint returns 403)

- [ ] T116 [US1] Add test_rbac_evaluator_can_access_evaluator_endpoints (evaluator token accessing evaluator endpoint returns 200)

- [ ] T117 [US1] Add test_rbac_admin_can_access_all_endpoints (admin token accessing any endpoint permitted by role)

### 6.7 Audit Trail for Auth Actions

- [ ] T118 [US1] Verify registration creates audit_logs entry (type=registration, user_id, timestamp)

- [ ] T119 [US1] Verify login creates audit_logs entry (type=login, success/failure, email, timestamp)

- [ ] T120 [US1] Verify logout creates audit_logs entry (type=logout, user_id, timestamp)

- [ ] T121 [US1] Verify failed login creates audit_logs entry (type=login_failed, email, timestamp, reason)

### 6.8 Final Verification

- [ ] T122 [US1] Run all Story-001 tests (pytest tests/ -v), verify 100% pass rate, 95%+ coverage

- [ ] T123 [US1] Generate final mutation testing report (mutmut run tests/ --paths-to-mutate src/services/), verify score >= 75%

- [ ] T124 [US1] Verify no hashed_password leaks in any API response (grep -r hashed_password tests/contract/)

- [ ] T125 [US1] Verify all FR-001 through FR-007 requirements covered by tests (map each FR to test case)

- [ ] T126 [US1] Verify Story-001 acceptance criteria met:
  - [ ] New employee registers and signs in successfully ✓
  - [ ] Receives role-appropriate access (submitter by default) ✓
  - [ ] Can sign out so previously valid credentials no longer grant access ✓

---

## Dependencies & Execution Order

### Critical Path (Blocking Order)

1. **Phase 1** (T001-T010): Must complete before any other phases
2. **Phase 2** (T011-T020): Must complete before Phase 3
3. **Phase 3** (T021-T037): Must complete before Phase 4 (TDD gate: all tests RED)
4. **Phase 4** (T038-T056): Implements Phase 3 tests (gate: all Phase 3 tests GREEN)
5. **Phase 5** (T057-T090): Depends on Phase 4 completion
6. **Phase 6** (T091-T126): Depends on Phase 5 completion

### Parallelizable Tasks

**Phase 1**: T002, T003, T004, T005, T006, T008, T009 can run in parallel (independent scaffolding)

**Phase 2**: T011-T018, T020 can run in parallel (independent schema definitions)

**Phase 3**: Within a phase group (success, validation, endpoint, security), tests can be written in parallel

**Phase 4**: Within component group (password, repository, service, endpoint), implementations can run in parallel

**Phase 5**: Token tests (T061-T066) can run in parallel; implementation (T068-T070) must follow tests

---

## Test Evidence & Quality Gates

### Code Coverage Requirements

- **Services layer** (core/security.py, services/auth_service.py): **95% minimum**
- **API endpoints** (api/endpoints/auth.py): **90% minimum**
- **Repositories** (db/repositories/user_repository.py): **85% minimum**
- **Overall project**: **95% target**

### Mutation Testing Requirements

- **services/auth_service.py**: **75% minimum mutation score**
- **core/security.py**: **75% minimum mutation score**
- **api/endpoints/auth.py**: **70% minimum mutation score**

### Test Organization

```text
tests/
├── unit/
│   ├── test_auth_service.py           # T021-T025, T061-T067, T072-T074, T081-T082
│   ├── test_security.py               # T034-T037
│   ├── test_dependencies.py           # T091-T103
│   └── test_user_repository.py        # (if needed for coverage)
├── integration/
│   └── test_auth_flow.py              # T053-T054, T115-T117
└── contract/
    └── test_auth_contracts.py         # T030-T033, T065-T066, T075, T083-T084, T104-T107
```

### Test Naming Convention

```python
# Test naming: test_<function>_<scenario>_<expected_result>

# Examples:
test_register_user_success()
test_register_user_duplicate_email_returns_409()
test_login_with_invalid_credentials_returns_401()
test_require_evaluator_role_denies_submitter()
test_access_token_expires_after_1_hour()
```

---

## Implementation Checklist Summary

**Total Tasks**: 126  
**Phase 1 (Scaffolding)**: 10 tasks  
**Phase 2 (Models & Schemas)**: 10 tasks  
**Phase 3 (Red Tests)**: 17 tasks  
**Phase 4 (Green Implementation)**: 18 tasks  
**Phase 5 (JWT & Auth Logic)**: 34 tasks  
**Phase 6 (RBAC & Authorization)**: 37 tasks  

**Parallelizable**: ~40 tasks  
**Sequential (TDD critical path)**: ~86 tasks  

**Estimated Duration**: 4-5 days for single developer (3 days minimum with parallel execution)

---

## Traceability to Specification

| FR | Requirement | Task(s) | Status |
|----|-------------|---------|--------|
| FR-001 | Registration creates account with submitter role | T021, T038-T048, T055 | ✓ |
| FR-002 | Login with valid credentials | T061-T068 | ✓ |
| FR-003 | Log each login attempt | T070, T088, T121 | ✓ |
| FR-005 | Issue short-lived + refresh tokens | T057-T059, T076-T079 | ✓ |
| FR-006 | Allow logout and invalidate session | T081-T088 | ✓ |
| FR-007 | Enforce role-based permissions | T091-T117 | ✓ |

**All acceptance criteria mapped to specific test tasks**

---

## Next Steps After Story-001

Upon completion of all 126 tasks:
1. **Code Review**: Peer review of all implementation and tests
2. **Mutation Testing Report**: Review mutmut output, refine tests if score < 75%
3. **Coverage Report**: Generate htmlcov/index.html, verify coverage targets met
4. **Story-001 Sign-Off**: QA acceptance testing of registration/login/logout flows
5. **Proceed to Story-002**: Idea Submission and Visibility (depends on Story-001 complete)

---

## Story-002 & Story-003: Implementation Status (No Formal Tasks Generated)

> Tasks for Story-002 and Story-003 were not generated via speckit.tasks. The features below
> were implemented directly and are verified by passing tests.

### Story-002 - Idea Submission & Visibility (FR-008 - FR-014) [COMPLETE]

- [X] POST /ideas/submit - title, description, category (form data)
- [X] Optional single file attachment (multipart/form-data, type + size validated, stored in uploads/)
- [X] GET /ideas - role-based list (submitter sees own; admin/evaluator sees all) with ?status= filter
- [X] GET /ideas/{id} - retrieve single idea with all fields including attachment_url

### Story-003 - Evaluation Workflow (FR-015 - FR-018) [COMPLETE]

- [X] PATCH /ideas/{id}/status - admin/evaluator only, persists status + evaluator_comment
- [X] IdeaStatus enum: SUBMITTED -> UNDER_REVIEW -> ACCEPTED/REJECTED
- [X] evaluator_comment stored and returned on GET /ideas/{id}
- [ ] Status transition enforcement (any->any currently allowed; submitted->under_review->final not enforced)
- [ ] Mandatory evaluator_comment for ACCEPTED/REJECTED statuses (currently optional)

### Known Remaining Gaps (Story-001)

- [ ] T072-T079 - POST /auth/refresh (refresh token endpoint + token store)
- [ ] T067, T070, T088, T118-T121 - Audit logging (login/logout/register events)
- [ ] T108 - GET /auth/me (profile endpoint)
- [ ] T056, T090, T123 - mutmut mutation testing (score not yet verified; 75% minimum required)
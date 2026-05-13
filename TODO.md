# TODO

## Completed Today
- [x] Initialized FastAPI package structure under app/ and tests/.
- [x] Added settings and MongoDB client wiring with Atlas-compatible environment loading.
- [x] Implemented password hashing and verification utilities.
- [x] Added user and token Pydantic models.
- [x] Wrote RED tests for registration and login authentication flows.
- [x] Implemented registration service logic and user repository operations.
- [x] Exposed POST /auth/register endpoint and verified registration path.
- [x] Implemented authenticate_user, create_access_token, and create_refresh_token.
- [x] Exposed POST /auth/login endpoint and verified login path.
- [x] Achieved green unit tests: 6 passed in tests/unit/test_auth_service.py.
- [x] Completed basic idea submission form via POST /ideas/submit with JWT authentication and MongoDB persistence.
- [x] Completed idea listing and viewing via GET /ideas for authenticated users.
- [x] Completed single file attachment support with multipart upload validation and static hosting.
- [x] Completed Global API Documentation with standardized Swagger success and failure examples across all endpoints.

## Next Steps (Tomorrow)
- [ ] Implement logout endpoint and token revocation storage flow.
- [ ] Add refresh token persistence/revocation repository and tests.
- [ ] Add API tests for /auth/register and /auth/login contract behavior.
- [ ] Implement RBAC dependencies for submitter vs evaluator/admin routes.
- [ ] Add integration tests against MongoDB Atlas or test database fixture.
- [ ] Prepare commit and push for Phase 5 completion checkpoint.

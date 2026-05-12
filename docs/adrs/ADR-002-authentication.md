# ADR-002: Authentication & Authorization

**Status**: Accepted  
**Date**: 2026-05-12  
**Deciders**: InnovatEPAM Portal Architecture Committee  
**Affected Stakeholders**: Security team, backend team, frontend team  

---

## Context

InnovatEPAM Portal Phase 1 MVP must:
- Allow secure user registration and login (FR-001, FR-002)
- Enforce role-based access control distinguishing submitter vs evaluator/admin (FR-007, FR-019)
- Issue short-lived credentials to minimize exposure if token compromised (security best practice)
- Provide logout capability with session invalidation (FR-006)
- Log all login attempts for audit compliance (FR-003)

**Specification Requirements**:
- Two roles: `submitter` (create ideas) and `evaluator`/`admin` (review decisions)
- New users default to `submitter` role (FR-001)
- Phase 1 does NOT auto-block repeated failed login attempts (FR-004)
- Failed login attempts must be logged (FR-003)
- Authenticated sessions must support logout (FR-006)

---

## Decision

Implement **OAuth2 with JWT** authentication using:
- **OAuth2 with Bearer Token** (industry standard for REST APIs)
- **JWT (JSON Web Tokens)** for stateless token validation
- **Short-lived access tokens** (1-hour expiration) + **longer-lived refresh tokens** (24-hour expiration)
- **passlib[bcrypt]** for password hashing (Constitution Principle IV)
- **Token blacklist** for logout enforcement (in-memory cache)
- **Automatic audit logging** for all login attempts

---

## Rationale

### 1. OAuth2 with Bearer Token

**Why OAuth2?**
- **Industry standard**: Widely understood and implemented
- **Stateless**: No server-side session table required (scales horizontally)
- **Secure**: Defined security best practices for token-based auth
- **Flexible**: Works with SPA, mobile, and server-rendered clients

**Why not Session Cookies?**
- Cookies require CSRF protection (adds complexity)
- Session table requires server state (doesn't scale as well)
- JWT fits modern architecture better (microservices-ready)

### 2. JWT (JSON Web Tokens)

**Structure**:
```
Header.Payload.Signature
```

**Example Token** (decoded):
```json
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload
{
  "sub": "user-uuid-123",
  "email": "alice@company.com",
  "role": "submitter",
  "iat": 1715500000,  // issued at
  "exp": 1715503600,  // expires at (1 hour later)
  "type": "access"
}

// Signature
HMACSHA256(base64(header) + "." + base64(payload), SECRET_KEY)
```

**Why JWT?**
- **Compact**: Fits in HTTP headers
- **Self-contained**: Payload includes all needed claims (no DB lookup for validation)
- **Verifiable**: Signature prevents tampering
- **Stateless**: Server only needs secret key to validate

### 3. Token Expiration Windows

**Access Token** (1 hour):
- Short window minimizes exposure if token leaked
- Frequent refresh forces fresh authentication check
- Reasonable UX (requires re-login only once per day for typical user)

**Refresh Token** (24 hours):
- Longer window allows seamless re-authentication without user interaction
- Still forces periodic full login for security audit
- Aligns with common web app login timeout

**Trade-off**:
- Shorter windows = more secure but requires more requests
- 1-hour access + 24-hour refresh balances security and usability

**Token Refresh Flow**:
```
1. User logs in → receives access_token (1h) + refresh_token (24h)
2. Access token expires → client uses refresh_token to get new access_token
3. Refresh token expires → user must log in again
```

### 4. Password Hashing with passlib[bcrypt]

**Why passlib?**
- Abstracts hashing algorithm (can upgrade from bcrypt to scrypt if needed)
- Handles salt generation automatically (no developer mistakes)
- GPU-resistant (bcrypt uses key derivation)

**Why bcrypt?**
- **Adaptive**: Cost factor increases automatically with hardware improvements
- **Proven**: 20+ years of security research backing
- **Configurable**: Cost factor 12 provides ~0.3 second hash time (acceptable)
- **Slow hashing**: Makes brute-force attacks computationally expensive

**Constitution Compliance**:
- Constitution Principle IV mandates: "Password handling MUST use passlib with bcrypt"
- This decision implements that requirement

**Hash Generation**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# During registration:
hashed = pwd_context.hash("UserPassword123")

# During login:
is_valid = pwd_context.verify("UserPassword123", hashed)
```

### 5. Token Blacklist for Logout

**Why blacklist instead of token revocation table?**
- **Performance**: In-memory lookup (<1ms) vs database query (10-100ms per request)
- **Phase 1 scope**: Low concurrent evaluator count; contention unlikely
- **Simplicity**: No new collection or schema complexity
- **Cleanup**: TTL-based cleanup when token naturally expires

**Implementation**:
```python
# On logout:
blacklist.add(token_jti, expires_at)

# On each request:
if token_jti in blacklist and not expired(expires_at):
    return 401 Unauthorized
```

**Phase 2 upgrade path**: Store in Redis for multi-instance deployments

### 6. Automatic Audit Logging

**Every login attempt logged** (FR-003):
```python
await audit_repo.create({
    "actor_id": user_id,
    "action": "login",
    "result": "success",  # or "failure"
    "timestamp": now(),
    "details": {"email": user_email}
})
```

**Why log failed attempts?**
- Security monitoring: Detect brute-force attempts
- Compliance: Required for audit trails
- Specification FR-003: "System MUST log each login attempt"

**Why not auto-block in Phase 1?**
- Specification FR-004: "System MUST NOT automatically block login attempts in Phase 1"
- Security trade-off: Phase 1 accepts temporary DoS risk for simpler implementation
- Phase 2: Can add rate limiting when monitoring detects attacks

---

## Alternatives Considered

### Alternative 1: Multi-Role RBAC with Resource-Level Permissions

**Rejected for Phase 1** because:
- Too complex: Requires ACL matrix (role × resource × action)
- Not in spec: Phase 1 only needs submitter vs evaluator distinction
- Deferred to Phase 2: Can implement attribute-based access control later

**Our approach**: Simple role-based (`if role == "evaluator": allow_decision()`)

### Alternative 2: OAuth2 with External Provider (Google, Azure)

**Rejected because**:
- Adds external dependency (slower development)
- Requires employee email from external provider
- Unnecessary complexity for internal company portal
- Better for Phase 2 if multi-organization support needed

### Alternative 3: Mutual TLS (mTLS) with Certificates

**Rejected because**:
- Overkill for MVP (expensive certificate management)
- Not user-friendly (end users don't manage certificates)
- Better suited for service-to-service auth (Phase 2 microservices)

### Alternative 4: API Keys (Simple but Insecure)

**Rejected because**:
- No user-facing login experience
- No logout capability (keys valid until expiration)
- No role differentiation per token
- Violates security best practice (no expiration enforcement)

### Alternative 5: Session Cookies (Traditional)

**Rejected because**:
- CSRF complexity (SameSite, CSRF tokens)
- No built-in support for refresh tokens
- Doesn't work well with mobile clients (no cookies)
- Requires server-side session storage

---

## Consequences

### Positive

✅ **Secure by default**: Short token windows + bcrypt hashing  
✅ **Scalable**: Stateless JWT validation (no session table bottleneck)  
✅ **Standards-based**: OAuth2/JWT widely supported and understood  
✅ **Audit-ready**: All login attempts logged automatically  
✅ **Phone-friendly**: Works with mobile apps (no cookie dependency)  
✅ **Logout capability**: Token blacklist enforces session invalidation  

### Negative

❌ **Token revocation lag**: Blacklist cleanup requires TTL overhead (acceptable for Phase 1)  
❌ **No immediate refresh token revocation**: If compromised, valid for 24 hours (mitigated by short access window)  
❌ **Additional logging**: Every login requires DB write (negligible overhead)  

### Mitigations

| Risk | Mitigation |
|------|-----------|
| Tokens compromised if leaked | 1-hour access token limits exposure window |
| Refresh token compromised | Attacker can issue new access tokens for 24h; user logs in next day and issue resolved |
| Brute-force login attempts | Phase 1 logs attempts; Phase 2 adds rate limiting |
| Token stored insecurely on client | Client responsibility (browser localStorage or HTTP-only cookies) |
| Database of blacklisted tokens grows unbounded | TTL index auto-deletes expired entries |

---

## Implementation Details

### Registration Endpoint (`POST /auth/register`)

```python
async def register(request: RegisterRequest) -> User:
    # Validate password strength
    if len(request.password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    
    # Check email uniqueness
    existing = await user_repo.find_by_email(request.email)
    if existing:
        raise ValidationError("Email already registered")
    
    # Hash password
    hashed = pwd_context.hash(request.password)
    
    # Create user with submitter role (FR-001)
    user = User(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        hashed_password=hashed,
        role="submitter"  # Default role
    )
    
    return await user_repo.create(user)
```

### Login Endpoint (`POST /auth/login`)

```python
async def login(credentials: LoginRequest) -> TokenResponse:
    # Find user (FR-002)
    user = await user_repo.find_by_email(credentials.email)
    
    # Validate password
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        # Log failed attempt (FR-003)
        await audit_repo.create({
            "action": "login",
            "result": "failure",
            "details": {"email": credentials.email}
        })
        raise AuthenticationError("Invalid credentials")
    
    # Log successful attempt (FR-003)
    await audit_repo.create({
        "actor_id": user.id,
        "action": "login",
        "result": "success"
    })
    
    # Issue tokens (FR-005)
    access_token = create_access_token(user, expires_delta=3600)  # 1 hour
    refresh_token = create_refresh_token(user, expires_delta=86400)  # 24 hours
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600
    )
```

### Token Generation

```python
def create_access_token(user: User, expires_delta: int = 3600) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=expires_delta)
    }
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

### RBAC Implementation

```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract user from token; verify role if needed"""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    user_id = payload.get("sub")
    user = await user_repo.get(user_id)
    return user

async def require_evaluator(user: User = Depends(get_current_user)):
    """Dependency to enforce evaluator/admin role (FR-019)"""
    if user.role not in ["evaluator", "admin"]:
        raise PermissionError("Only evaluators/admins can perform this action")
    return user

# Usage in endpoint:
@app.put("/ideas/{idea_id}/decision")
async def make_decision(
    idea_id: str,
    decision: DecisionRequest,
    evaluator: User = Depends(require_evaluator)  # Enforces FR-019
) -> DecisionResponse:
    ...
```

### Logout Endpoint (`POST /auth/logout`)

```python
async def logout(token: str = Depends(oauth2_scheme)) -> dict:
    """Invalidate token by adding to blacklist (FR-006)"""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    jti = payload.get("jti")
    exp = payload.get("exp")
    
    # Add to blacklist with expiration
    token_blacklist[jti] = exp
    
    # Log logout
    await audit_repo.create({
        "actor_id": payload.get("sub"),
        "action": "logout",
        "result": "success"
    })
    
    return {"message": "Logout successful"}
```

---

## Testing Strategy

**Unit Tests** (test components in isolation):
```python
def test_password_hash_not_plain():
    pwd = "SecurePass123"
    hashed = pwd_context.hash(pwd)
    assert hashed != pwd  # Never store plain password

def test_token_expiration():
    payload = {"exp": datetime.utcnow() - timedelta(hours=1)}
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(payload, SECRET_KEY)
```

**Integration Tests** (full auth flow):
```python
@pytest.mark.asyncio
async def test_auth_flow():
    # Register
    resp = await register({"email": "test@company.com", "password": "Pass123!"})
    assert resp.status_code == 201
    
    # Login
    tokens = await login({"email": "test@company.com", "password": "Pass123!"})
    assert tokens.access_token
    assert tokens.refresh_token
    
    # Use token
    user = await get_current_user(tokens.access_token)
    assert user.email == "test@company.com"
    assert user.role == "submitter"
    
    # Logout
    await logout(tokens.access_token)
    
    # Try to use token again (should fail)
    with pytest.raises(AuthenticationError):
        await get_current_user(tokens.access_token)
```

**Contract Tests** (API specifications):
```python
def test_login_returns_bearer_token():
    """FR-005 contract: Login returns access and refresh tokens"""
    response = client.post("/auth/login", json=credentials)
    assert response.json()["token_type"] == "bearer"
```

---

## Related Decisions

- **ADR-001**: Data Persistence (User collection structure)
- **ADR-003**: Testing & Quality Assurance (auth test coverage)
- **Constitution Principle IV**: Security Discipline (passlib/bcrypt mandated)

---

## Verification

Acceptance criteria:
- [ ] Registration endpoint creates user with submitter role
- [ ] Login validates credentials and issues access + refresh tokens
- [ ] Access token expires after 1 hour
- [ ] Refresh token expires after 24 hours
- [ ] Failed login attempts logged
- [ ] Logout invalidates access token
- [ ] Evaluator-only endpoints reject submitters (FR-019)
- [ ] RBAC enforced on all protected endpoints
- [ ] Passwords hashed with bcrypt (cost 12)
- [ ] Sensitive fields (passwords, hashes) never exposed in API responses

---

## Questions & Answers

**Q: What if access token is stolen?**  
A: Thief has 1 hour before token expires. Legitimate user can log out immediately to invalidate refresh token.

**Q: How does refresh token rotation work?**  
A: Phase 1 doesn't rotate; Phase 2 can invalidate old refresh token on reuse to prevent token compromise replay.

**Q: What about multi-device login?**  
A: Each device login generates unique access+refresh token pair. Logout on one device doesn't affect others.

**Q: Is there rate limiting on failed logins?**  
A: Phase 1 doesn't rate-limit (FR-004); Phase 2 adds lock-after-5-attempts with 15-minute window.

**Q: What if someone brute-forces weak passwords?**  
A: Mitigated by: password complexity requirement (8+ chars), bcrypt slow hashing (0.3s per attempt), audit logging for detection.

---

## References

- [RFC 6749: OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
- [RFC 7519: JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [OWASP: Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [bcrypt Security](https://auth0.com/blog/hashing-in-action-understanding-bcrypt/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)

---

**Approval Status**: ✅ Accepted  
**Next Review Date**: 2026-08-12 (end of Phase 2, consider refresh token rotation)

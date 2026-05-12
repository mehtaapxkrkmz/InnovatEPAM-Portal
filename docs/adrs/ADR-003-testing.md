# ADR-003: Testing & Quality Assurance

**Status**: Accepted  
**Date**: 2026-05-12  
**Deciders**: InnovatEPAM Portal Architecture Committee, Constitution Ratification Board  
**Affected Stakeholders**: Engineering team, DevOps, QA, Management  

---

## Context

InnovatEPAM Portal is built under the Constitution which mandates (Principle III - Testing Authority):
- **TDD is mandatory** for all feature work (Red-Green-Refactor)
- **75% minimum mutation testing score** on covered business logic
- No tooling defaults can bypass or reduce testing requirements

**Requirements**:
- Verify behavior, not assumptions (test-first prevents false confidence)
- Catch regressions automatically (mutation testing)
- Maintain high code quality as team grows
- Producible evidence of testing compliance for stakeholders

**Challenges**:
- Achieving 75% mutation score requires rigorous test design
- TDD requires discipline; easy to skip if not enforced
- Mutation testing tools have learning curve

---

## Decision

Implement **TDD with pytest + mutmut** for comprehensive quality assurance:

1. **pytest** - Unit, integration, and contract test framework
   - TDD red-green-refactor workflow
   - Async test support (for FastAPI + Motor)
   - Fixture-based test isolation
   - Parametrized tests for comprehensive coverage

2. **pytest-cov** - Code coverage measurement
   - Baseline: 95% code coverage target
   - HTML reports for visibility
   - Fail build if <95% on services layer

3. **mutmut** - Mutation testing framework
   - Apply semantic mutations to code (change operators, constants, conditions)
   - Verify tests catch mutated code
   - Mutation score = (killed mutations / total mutations)
   - Gate: Fail build if mutation score < 75% on services layer

4. **Test Organization** by concern:
   - **Unit tests** (`tests/unit/`): Test services in isolation with mocked repositories
   - **Integration tests** (`tests/integration/`): Test full flows with real MongoDB
   - **Contract tests** (`tests/contract/`): Test API endpoints match specification

---

## Rationale

### 1. Why TDD (Red-Green-Refactor)?

**The TDD Cycle**:
```
RED:      Write test for new feature → test fails (no implementation)
GREEN:    Write minimal code → test passes
REFACTOR: Improve code structure → tests still pass
```

**Why this discipline?**
- **Tests first = clear requirements**: Writing test forces clarity on expected behavior
- **No false confidence**: Code only written to pass test (minimal surface area)
- **Easier refactoring**: If tests pass, refactoring didn't break behavior
- **Regression prevention**: Test suite grows with codebase (catches new bugs)

**Example**:
```python
# RED: Test for new feature (fails - no implementation)
def test_register_user_creates_submitter_role():
    result = await register_user({"email": "test@company.com", ...})
    assert result.role == "submitter"

# GREEN: Minimal implementation (pass test)
async def register_user(data):
    user = User(**data, role="submitter")
    return await db.users.insert_one(user)

# REFACTOR: Improve implementation (tests still pass)
async def register_user(data):
    validate_registration_input(data)  # Add validation
    hashed = hash_password(data["password"])
    user = User(**data, password=hashed, role="submitter")
    return await db.users.insert_one(user)
```

**Constitution Compliance**: Principle III mandates "Red-Green-Refactor for each story slice"

### 2. Why pytest?

**Advantages over alternatives**:
- **Fixtures**: Parameterizable test setup/teardown (vs unittest's setUp/tearDown boilerplate)
- **Async support**: `@pytest.mark.asyncio` enables testing async functions naturally
- **Parametrization**: Test same logic with multiple inputs (`@pytest.mark.parametrize`)
- **Plugins ecosystem**: pytest-cov, pytest-asyncio, pytest-mock all standard
- **Minimal assertions**: Simple `assert x == y` (vs unittest's `self.assertEqual(x, y)`)

**Example Test**:
```python
@pytest.mark.asyncio
async def test_user_registration():
    user_data = {
        "email": "alice@company.com",
        "first_name": "Alice",
        "last_name": "Smith",
        "password": "SecurePass123"
    }
    
    user = await register_user(user_data)
    
    assert user.email == user_data["email"]
    assert user.role == "submitter"
    assert user.hashed_password != user_data["password"]  # Password hashed
```

### 3. Why 95% Code Coverage Baseline?

**Coverage = "% of lines executed by tests"**

Coverage != Quality, but it's a good signal:
- **95% coverage**: Nearly all code has at least one test touching it
- **Catches dead code**: Code with 0% coverage is clearly untested
- **Sets discipline**: Team knows coverage is measured and enforced

**How coverage relates to mutation testing**:
```
Code Coverage: Did tests execute this line?
Mutation Testing: Did tests CATCH when we broke this line?
```

**Example**:
```python
def approve_idea(idea_id):
    idea = get_idea(idea_id)
    if idea.status == "under_review":      # ← Coverage checks if this line runs
        idea.status = "accepted"
        return True                        # ← Mutation testing checks if test fails when we change to False

# Test with 95% coverage:
def test_approve_idea():
    result = approve_idea(test_idea_id)
    assert result == True                  # ← Coverage: "if" line runs; Mutation: changing True to False is caught
```

### 4. Why mutmut for Mutation Testing?

**Mutation Testing Definition**: Automatically introduce bugs (mutations) into code, then check if tests catch the bugs.

**Example Mutations**:
```python
# Original
if idea.status == "under_review":         # Mutation 1: change == to !=
if idea.status == "under_review":         # Mutation 2: change "under_review" to "submitted"
return True                               # Mutation 3: change True to False
```

**Mutation Score** = (Killed Mutations / Total Mutations)
- **Killed mutation**: Test failed; bug was caught ✓
- **Survived mutation**: Test passed; bug was NOT caught ✗

**Why 75%?**
- 100% is impossible (some mutations are semantically invalid)
- 75% = High confidence tests catch most real bugs
- Constitution Principle III mandates >= 75%

**Example**:
```python
def transfer_idea_to_review(idea_id):
    idea = get_idea(idea_id)
    idea.status = "under_review"    # ← Mutation: change string to "submitted" (SHOULD be caught by test)
    return idea

def test_transfer_to_review():
    result = transfer_idea_to_review(test_idea_id)
    assert result.status == "under_review"  # ← This test CATCHES mutation (good)

# Another test:
def test_transfer_only_updates_status():
    old_idea = load_idea_before()
    transfer_idea_to_review(test_idea_id)
    new_idea = load_idea_after()
    assert new_idea.title == old_idea.title  # Test doesn't verify STATUS, so mutation survives (bad)
```

### 5. Test Organization

**Unit Tests** (`tests/unit/`):
- Test services in isolation
- Mock external dependencies (database, external APIs)
- Fast execution (<100ms per test)
- Focus: Business logic correctness

```python
# tests/unit/test_idea_service.py
@pytest.mark.asyncio
async def test_validate_idea_rejects_short_title(mock_repo):
    with pytest.raises(ValidationError) as exc_info:
        await IdeaService.validate_create_request({"title": "Hi"})
    assert "Title must be at least 1 character" in str(exc_info.value)
```

**Integration Tests** (`tests/integration/`):
- Test full flows with real database
- Verify end-to-end behavior
- Slower but more realistic (~1s per test)
- Focus: Feature completeness

```python
# tests/integration/test_auth_flow.py
@pytest.mark.asyncio
async def test_full_auth_flow(db):
    # 1. Register
    reg_resp = await register_user(...)
    assert reg_resp.role == "submitter"
    
    # 2. Login
    login_resp = await login(...)
    assert login_resp.access_token
    
    # 3. Use token
    user = await get_current_user(login_resp.access_token)
    assert user.email == "..."
    
    # 4. Logout
    await logout(login_resp.access_token)
    
    # 5. Token no longer works
    with pytest.raises(AuthenticationError):
        await get_current_user(login_resp.access_token)
```

**Contract Tests** (`tests/contract/`):
- Test HTTP API endpoints
- Verify request/response formats match specification
- ~500ms per test (includes HTTP overhead)
- Focus: API specification compliance

```python
# tests/contract/test_auth_contracts.py
def test_login_endpoint_contract():
    """FR-005 contract: Login returns correct token structure"""
    
    response = client.post("/auth/login", json={
        "email": "alice@company.com",
        "password": "SecurePass123!"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600  # 1 hour
```

### 6. Implementation Workflow

**For Each Story**:

1. **RED Phase**: Write tests covering acceptance criteria
   ```bash
   pytest tests/ -v  # Watch tests fail
   ```

2. **GREEN Phase**: Implement minimal code to pass tests
   ```bash
   pytest tests/ -v  # Watch tests pass
   ```

3. **REFACTOR Phase**: Improve structure while maintaining green tests
   ```bash
   pytest tests/ -v --cov=app/services --cov-report=html  # Track coverage
   ```

4. **MUTATION Phase**: Run mutation testing to find gaps
   ```bash
   mutmut run --paths app/services --tests-dir tests/
   mutmut results  # Check score
   ```

5. **IMPROVE Tests**: Fix tests to kill surviving mutations
   ```bash
   mutmut run ...  # Re-check score until >= 75%
   ```

---

## Alternatives Considered

### Alternative 1: Manual Testing / QA Team

**Rejected because**:
- Non-scalable (test count grows with features)
- Unreliable (human testers miss edge cases)
- Slow feedback (tests run hours later, not during development)
- No regression verification (old bugs creep back)
- Contradicts Constitution Principle III

### Alternative 2: Code Coverage Only (No Mutation Testing)

**Rejected because**:
- 95% coverage doesn't verify correctness (code can be wrong and still execute)
- Satisfies Constitution requirement partially only
- Gives false confidence (all code is tested but tests might be weak)

**Example**:
```python
def is_valid_status(status):
    return status in ["submitted", "under_review", "accepted"]

# 100% coverage test:
def test_valid_status():
    assert is_valid_status("submitted")

# This test has 100% coverage but doesn't catch this mutation:
def is_valid_status(status):
    return status in ["submitted", "under_review", "accepted", "invalid"]  # Added invalid
    
# Mutation testing would catch it!
```

### Alternative 3: Pytest-only, No Mutation Testing

**Rejected because**:
- Constitution Principle III mandates "75% mutation testing minimum"
- No way to verify test quality
- Risk of false confidence in weak tests

### Alternative 4: Different Framework (nose, unittest, etc.)

**Rejected because**:
- pytest is industry standard for FastAPI projects
- Better ecosystem (fixtures, async support, plugins)
- Most FastAPI tutorials use pytest
- Team familiarity

---

## Consequences

### Positive

✅ **High confidence in correctness**: Mutation testing verifies tests are strong  
✅ **Regression prevention**: Test suite grows with codebase  
✅ **Faster feedback**: Developers know immediately if change broke something  
✅ **Easier refactoring**: Tests give permission to improve structure  
✅ **Clear requirements**: Tests document expected behavior  
✅ **Constitution compliance**: Mandatory discipline enforced  

### Negative

❌ **More code to write**: Test code ~2x feature code volume  
❌ **Slower development**: TDD adds upfront time (paid back in fewer bugs)  
❌ **Learning curve**: Team must learn pytest + mutation testing  
❌ **Async complexity**: Testing async code adds some complexity  

### Mitigations

| Challenge | Mitigation |
|-----------|-----------|
| TDD feels slow initially | Frame as investment; later features faster due to fewer bugs |
| Mutation testing output confusing | Document mutation types; focus on high-impact survivors |
| Fixtures get complex | Create well-documented fixture library in conftest.py |
| Database tests slow | Use in-memory MongoDB (mongomock) for unit tests; real DB for integration |

---

## Implementation Details

### Test Structure Template

```python
# tests/unit/test_idea_service.py

import pytest
from app.services.idea_service import IdeaService
from app.models.idea import Idea
from unittest.mock import AsyncMock, MagicMock

class TestIdeaService:
    """Red-Green-Refactor workflow for idea submission"""
    
    @pytest.fixture
    def idea_repo(self):
        """Mock repository for unit tests"""
        repo = AsyncMock()
        return repo
    
    @pytest.mark.asyncio
    async def test_create_idea_with_valid_data_succeeds(self, idea_repo):
        """RED: Test new requirement
        
        Acceptance Criteria (FR-008):
        - Idea created with title, description, category
        - Initial status is "submitted"
        """
        
        # Arrange
        idea_data = {
            "title": "Improve onboarding",
            "description": "Implement automated checklist system...",
            "category": "process-improvement",
            "submitter_id": "user-123"
        }
        idea_repo.create.return_value = Idea(**idea_data, status="submitted")
        
        service = IdeaService(idea_repo)
        
        # Act
        result = await service.create_idea(idea_data)
        
        # Assert
        assert result.title == idea_data["title"]
        assert result.status == "submitted"  ← GREEN: Test passes when code implements
        idea_repo.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_idea_rejects_short_title(self, idea_repo):
        """Acceptance Criteria: Title must be 1-500 chars"""
        
        idea_data = {"title": "", "description": "...", "category": "..."}
        service = IdeaService(idea_repo)
        
        with pytest.raises(ValidationError) as exc_info:
            await service.create_idea(idea_data)
        
        assert "Title must be at least 1 character" in str(exc_info.value)
```

### pytest.ini Configuration

```ini
[pytest]
asyncio_mode = auto  # Enable async tests automatically
testpaths = tests    # Where to find tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = 
    -v                                    # Verbose output
    --strict-markers                      # Fail on unknown markers
    --tb=short                            # Short traceback format
    --cov=app/services                    # Coverage on services layer
    --cov-report=term-missing             # Show uncovered lines
    --cov-report=html                     # Generate HTML report
    --cov-fail-under=95                   # Fail if <95% coverage

markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, with DB)
    contract: API contract tests
    slow: Slow tests
```

### Mutation Testing Configuration

**pyproject.toml** or **mutmut.ini**:
```ini
[mutmut]
paths = app/services/
tests-dir = tests/
dont-mutate-decorators = True
mutation-score-target = 75
```

**CI Command**:
```bash
# Run after all tests pass
mutmut run --paths app/services --tests-dir tests/
SCORE=$(mutmut results | grep "Mutation score")
if [[ $SCORE < 75 ]]; then exit 1; fi  # Fail if < 75%
```

### Fixtures for Async Testing

**tests/conftest.py**:
```python
import pytest
import asyncio
from motor.motor_asyncio import AsyncClient
from app.core.config import settings

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_client():
    """Create test MongoDB client"""
    client = AsyncClient(settings.MONGODB_URI)
    yield client
    client.close()

@pytest.fixture
async def db(db_client):
    """Get test database (cleaned after each test)"""
    db = db_client.innovatepam_test
    yield db
    # Cleanup
    await db.drop_collection("users")
    await db.drop_collection("ideas")
    await db.drop_collection("audit_logs")
```

---

## Verification

Acceptance criteria:
- [ ] pytest installed and test suite runs: `pytest tests/ -v`
- [ ] At least 1 test per acceptance criterion from specification
- [ ] Unit tests with 95%+ code coverage: `pytest --cov=app/services`
- [ ] Integration tests with real database verify end-to-end flows
- [ ] Contract tests verify API matches specification
- [ ] Mutation testing score >= 75%: `mutmut run && mutmut results`
- [ ] All three stories have TDD red-green-refactor workflow demonstrated
- [ ] CI gate fails build if mutation score < 75%

---

## Testing Checklist

For each story, verify:

```
[ ] RED:  Write tests, watch them fail
[ ] GREEN: Write code, watch tests pass
[ ] REFACTOR: Improve code, tests still pass
[ ] COVERAGE: Run pytest-cov; document coverage %
[ ] MUTATION: Run mutmut; analyze survivors; improve tests
[ ] SCORE: Verify mutation score >= 75%
[ ] INTEGRATE: Merge only after all gates pass
```

---

## Related Decisions

- **ADR-001**: Data Persistence (test data in MongoDB)
- **ADR-002**: Authentication (auth test strategy)
- **Constitution Principle III**: Testing Authority (TDD mandatory, 75% mutation minimum)

---

## Questions & Answers

**Q: Does mutation testing slow down CI?**  
A: Yes (~5-10 minutes). Worth it for quality. Parallel runs across cores reduce time.

**Q: How do we know 75% mutation is enough?**  
A: Industry research shows 70-80% catches most real bugs. 75% is well-established threshold.

**Q: Can we skip mutation testing for simple code?**  
A: Constitution Principle III says no exceptions. All business logic must meet 75% mutation score.

**Q: What if a mutation can't be killed (equivalent mutation)?**  
A: Document it in code comment. mutmut has `--skip-covered` flag to exclude unreachable mutations.

**Q: How do we motivate TDD if it feels slow?**  
A: Show team how Phase 2 development is faster (fewer bugs, faster refactoring). Time ROI becomes positive.

---

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Test-Driven Development (Kent Beck)](https://www.pearson.com/en-us/subject-catalog/p/test-driven-development-by-example/P200000009481)
- [mutmut GitHub](https://github.com/boxed/mutmut)
- [Mutation Testing (Wikipedia)](https://en.wikipedia.org/wiki/Mutation_testing)
- [OWASP: Code Review Guide - Testing](https://owasp.org/www-project-code-review-guide/)

---

**Approval Status**: ✅ Accepted  
**Enforcement**: Mandatory (Constitution Principle III)  
**Next Review Date**: 2026-08-12 (mid-Phase 2, evaluate mutation score trends)

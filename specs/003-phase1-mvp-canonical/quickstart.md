# Quickstart: InnovatEPAM Portal Phase 1 MVP

**Date**: 2026-05-12  
**Target Audience**: Developers beginning Phase 1 implementation  
**Prerequisites**: Python 3.11+, MongoDB Atlas account, Git

---

## Project Setup (5 minutes)

### 1. Clone and Initialize

```powershell
cd c:\Users\Asus\OneDrive\Masaüstü\InnovatEPAM Portal
git checkout main
```

### 2. Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**File: requirements.txt** (should contain):
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
motor==3.3.2
pymongo==4.6.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.23.2
mutmut==2.4.5
httpx==0.25.2
```

### 4. Configure Environment Variables

Create `.env` file in project root:

```powershell
# .env (not committed to git)

# MongoDB Connection
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/innovatepam?retryWrites=true&w=majority

# JWT Secrets
SECRET_KEY=your-super-secret-key-min-32-chars-change-in-production
ALGORITHM=HS256

# API Configuration
DEBUG=True
PORT=8000
HOST=0.0.0.0

# Password Requirements
MIN_PASSWORD_LENGTH=8
MAX_PASSWORD_LENGTH=128
```

**Secure `SECRET_KEY` generation**:
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## Project Structure

Create the following directory structure:

```
InnovatEPAM Portal/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py                    # FastAPI app entry point
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py              # Settings, environment
│       │   ├── security.py            # JWT, password utilities
│       │   └── constants.py           # App constants
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py                # User Pydantic schema
│       │   ├── idea.py                # Idea Pydantic schema
│       │   ├── audit.py               # Audit log schema
│       │   └── token.py               # Token schemas
│       ├── db/
│       │   ├── __init__.py
│       │   ├── client.py              # Motor client setup
│       │   ├── repositories/
│       │   │   ├── __init__.py
│       │   │   ├── user_repo.py       # User CRUD operations
│       │   │   ├── idea_repo.py       # Idea CRUD operations
│       │   │   └── audit_repo.py      # Audit CRUD operations
│       │   └── schemas.py             # MongoDB collection schemas
│       ├── api/
│       │   ├── __init__.py
│       │   ├── router.py              # API routes
│       │   ├── endpoints/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py            # /auth endpoints
│       │   │   ├── ideas.py           # /ideas endpoints
│       │   │   └── governance.py      # /ideas/{id}/decision endpoints
│       │   └── dependencies.py        # Dependency injection
│       └── services/
│           ├── __init__.py
│           ├── auth_service.py        # Authentication logic
│           ├── idea_service.py        # Idea submission logic
│           ├── governance_service.py  # Evaluation logic
│           └── attachment_service.py  # File handling
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_auth_service.py
│   │   ├── test_idea_service.py
│   │   └── test_validation.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_auth_flow.py
│   │   ├── test_idea_submission_flow.py
│   │   └── test_evaluation_flow.py
│   └── contract/
│       ├── __init__.py
│       ├── test_auth_contracts.py
│       ├── test_ideas_contracts.py
│       └── test_governance_contracts.py
├── .env                               # Local environment (not committed)
├── .gitignore
├── requirements.txt
├── README.md
└── pytest.ini
```

---

## First Sprint: Getting Started

### Story 1: User Identity (FR-001 through FR-007)

**TDD Workflow** (RED → GREEN → REFACTOR):

#### Step 1: RED - Write failing test

```python
# tests/unit/test_auth_service.py

import pytest
from app.services.auth_service import register_user

@pytest.mark.asyncio
async def test_register_creates_user_with_submitter_role():
    """FR-001: Registration creates account with submitter role"""
    
    new_user = {
        "email": "alice@company.com",
        "first_name": "Alice",
        "last_name": "Smith",
        "password": "SecurePass123!"
    }
    
    user = await register_user(new_user)
    
    assert user.email == "alice@company.com"
    assert user.role == "submitter"
    assert user.is_active == True
    assert user.id is not None
```

**Run test (watch it FAIL)**:
```powershell
pytest tests/unit/test_auth_service.py::test_register_creates_user_with_submitter_role -v
```

#### Step 2: GREEN - Implement minimal code to pass test

```python
# app/services/auth_service.py

from app.models.user import User
from app.db.repositories.user_repo import UserRepository

async def register_user(user_data: dict) -> User:
    """Register new user with submitter role"""
    
    repo = UserRepository()
    
    # Hash password using passlib
    hashed_password = hash_password(user_data["password"])
    
    # Create user document
    user = User(
        email=user_data["email"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        hashed_password=hashed_password,
        role="submitter"
    )
    
    # Save to MongoDB
    saved_user = await repo.create(user)
    return saved_user
```

**Run test again (watch it PASS)**:
```powershell
pytest tests/unit/test_auth_service.py::test_register_creates_user_with_submitter_role -v
```

#### Step 3: REFACTOR - Improve code while tests remain green

```python
# Refactor: Extract password hashing to separate function
# Refactor: Add type hints
# Refactor: Add logging
```

**Run full test suite to ensure nothing broke**:
```powershell
pytest tests/ -v --cov=app/services --cov-report=term-missing
```

---

### Story 2: API Endpoint (FR-002 Integration)

**Contract Test**:

```python
# tests/contract/test_auth_contracts.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_endpoint_returns_tokens():
    """FR-002 & FR-005: Login returns access and refresh tokens"""
    
    # First register
    client.post("/auth/register", json={
        "email": "bob@company.com",
        "first_name": "Bob",
        "last_name": "Jones",
        "password": "ValidPass123!"
    })
    
    # Then login
    response = client.post("/auth/login", json={
        "email": "bob@company.com",
        "password": "ValidPass123!"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600
```

---

## Development Commands

### Run Development Server

```powershell
cd c:\Users\Asus\OneDrive\Masaüstü\InnovatEPAM Portal
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: http://localhost:8000

**Interactive API docs**: http://localhost:8000/docs (Swagger UI)

### Run Tests

```powershell
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# With coverage report
pytest tests/ -v --cov=app/services --cov-report=html

# Specific test file
pytest tests/unit/test_auth_service.py -v

# Specific test function
pytest tests/unit/test_auth_service.py::test_register_creates_user_with_submitter_role -v
```

### Mutation Testing

```powershell
# Generate mutations and run tests
mutmut run --paths app/services --tests-dir tests/

# Show mutation report
mutmut results

# Show detailed mutation results
mutmut results --show-times
```

**Target**: >= 75% mutation score (Constitution Principle III)

---

## MongoDB Atlas Setup

### 1. Create Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free tier cluster (M0)
3. Name: `InnovatEPAM`
4. Region: Choose closest to development location

### 2. Create Database User

1. Navigate to Database Access
2. Add Database User:
   - Username: `innovate_admin`
   - Password: Generate strong password
   - Role: `readWriteAnyDatabase`

### 3. Configure Network Access

1. Navigate to Network Access
2. Add IP Address: Allow `0.0.0.0/0` (development only; restrict in production)

### 4. Get Connection String

1. Navigate to Clusters
2. Click "Connect" → "Drivers" → "Python"
3. Copy connection string (URI)
4. Replace `<password>` with your database user password
5. Paste into `.env` as `MONGODB_URI`

### 5. Initialize Indexes

```python
# scripts/init_db.py

import asyncio
from motor.motor_asyncio import AsyncClient
from app.core.config import settings

async def create_indexes():
    """Create MongoDB indexes for all collections"""
    
    client = AsyncClient(settings.MONGODB_URI)
    db = client.innovatepam
    
    # Users collection
    await db.users.create_index("email", unique=True)
    await db.users.create_index("created_at", -1)
    await db.users.create_index("role", 1)
    
    # Ideas collection
    await db.ideas.create_index([("submitter_id", 1), ("created_at", -1)])
    await db.ideas.create_index("status", 1)
    await db.ideas.create_index("created_at", -1)
    await db.ideas.create_index([("_id", 1), ("_version", 1)])
    
    # Audit logs
    await db.audit_logs.create_index([("actor_id", 1), ("timestamp", -1)])
    await db.audit_logs.create_index([("action", 1), ("timestamp", -1)])
    await db.audit_logs.create_index([("resource_id", 1), ("timestamp", -1)])
    await db.audit_logs.create_index([("timestamp", -1)])
    
    # Refresh tokens with TTL
    await db.refresh_tokens.create_index("expires_at", expireAfterSeconds=0)
    
    client.close()
    print("✓ Indexes created successfully")

if __name__ == "__main__":
    asyncio.run(create_indexes())
```

**Run once per environment**:
```powershell
python scripts/init_db.py
```

---

## Key Files to Start With

### 1. Core Configuration

**app/core/config.py**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. FastAPI Entry Point

**app/main.py**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router

app = FastAPI(
    title="InnovatEPAM Portal",
    version="1.0.0",
    description="Employee innovation management platform"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.get("/")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

### 3. Pytest Configuration

**pytest.ini**:
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    contract: API contract tests
```

### 4. Fixtures

**tests/conftest.py**:
```python
import pytest
import asyncio
from motor.motor_asyncio import AsyncClient
from app.core.config import settings

@pytest.fixture
def event_loop():
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
async def test_db(db_client):
    """Get test database"""
    return db_client.innovatepam_test

@pytest.fixture
async def test_user(test_db):
    """Create test user"""
    user_data = {
        "_id": "test-user-1",
        "email": "test@company.com",
        "first_name": "Test",
        "last_name": "User",
        "hashed_password": "hashed_pwd",
        "role": "submitter",
        "is_active": True
    }
    await test_db.users.insert_one(user_data)
    yield user_data
    await test_db.users.delete_one({"_id": "test-user-1"})
```

---

## Verification Checklist

Before starting implementation, verify:

- [ ] Python 3.11+ installed: `python --version`
- [ ] Virtual environment active: `.venv\Scripts\Activate.ps1` executed
- [ ] Dependencies installed: `pip list | grep fastapi`
- [ ] `.env` configured with `MONGODB_URI` and `SECRET_KEY`
- [ ] MongoDB Atlas cluster created and accessible
- [ ] Indexes created: `python scripts/init_db.py`
- [ ] Test suite runs: `pytest tests/ --collect-only`
- [ ] Dev server starts: `uvicorn app.main:app --reload` (no errors)
- [ ] API docs accessible: http://localhost:8000/docs

---

## Next Steps

1. **Day 1**: Complete Story 1 (User Identity) with full test coverage
2. **Day 2**: Complete Story 2 (Idea Submission) with full test coverage
3. **Day 3**: Complete Story 3 (Evaluation Governance) with full test coverage
4. **Days 4-5**: Refactor, improve mutation score to 75%+, document discoveries

---

## Reference Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Motor (Async MongoDB)](https://motor.readthedocs.io/)
- [Pydantic](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [MongoDB Atlas](https://docs.atlas.mongodb.com/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc7519)

---

## Troubleshooting

### MongoDB Connection Error

```
pymongo.errors.ServerSelectionTimeoutError: connection string error
```

**Solution**:
- Verify `MONGODB_URI` in `.env` is correct
- Check MongoDB Atlas network access allows your IP
- Verify database user password is correct

### Permission Denied on Virtual Environment

```powershell
# On Windows, if activation fails:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### Port 8000 Already in Use

```powershell
# Use different port:
uvicorn app.main:app --reload --port 8001
```

### Tests Hang or Timeout

- Check `pytest.ini` has `asyncio_mode = auto`
- Verify `test_db` fixture properly closes connections
- Check MongoDB Atlas connection is working

---

**Quickstart Complete**: You are ready to begin Phase 1 implementation!

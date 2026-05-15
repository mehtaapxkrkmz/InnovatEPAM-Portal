# InnovatEPAM Portal - Phase 1 MVP

## Description
InnovatEPAM Portal is an employee innovation management platform built with FastAPI and MongoDB, following the SpecKit Tool-First governance protocol.

## Governance
This project follows the official SpecKit workflow (Specify -> Plan -> Tasks -> Implement) with a canonical specification approved by the professor.

Primary source of truth:
- Canonical specification: specs/003-phase1-mvp-canonical/spec.md
- Constitution: .specify/memory/constitution.md

## Setup Instructions
### 1. Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies
```powershell
pip install --upgrade pip
pip install fastapi uvicorn motor pymongo pydantic
```

### 3. (Optional) Install from requirements
```powershell
pip install -r requirements.txt
```

### 4. Run the application
```powershell
uvicorn src.main:app --reload
```

### 5. Run tests
```powershell
pytest
```

## User Interface Overview

### Key Features in Action

**Dashboard**
- All ideas displayed in a unified view with priority filtering
- Blind review mode toggle for anonymous evaluation
- Real-time idea counting by priority level
- Quick access to submit new ideas

**Authentication System**
- User registration with role selection (Submitter, Reviewer, Admin)
- Secure login with JWT token-based authentication
- Email-based account management

**Idea Management**
- **Submit New Idea**: Add innovation ideas with:
  - Title and detailed description
  - Category selection (Product, Process, Service)
  - Priority levels (Low, Medium, High)
  - Budget estimation
  - File attachments (PDF, images, documents - max 3 files)
  
- **Draft Management**: Save ideas as drafts before publishing
- **Idea Cards**: Display idea metadata with creator info, scoring, and feedback history

**Multi-Stage Review Process**
- **Review Workflow**: Sequential or parallel review stages
  - Stage 1: Initial Review
  - Stage 2: Business Review
  - Stage 3: Leadership Review
  - Stage 4: Final Decision

- **Evaluation Features**:
  - Scoring system (1-5 scale)
  - Structured evaluation comments
  - Status tracking (Under Review, Accepted, Rejected)
  - Anonymous evaluation mode for fair assessment

- **Error Handling**:
  - Validation feedback for incomplete submissions
  - Clear error messages for API issues
  - Form guidance and constraints

## Features
- **Employee Innovation Management**: Submit, track, and manage innovation ideas
- **Multi-Stage Review Process**: Configurable review workflows
- **Blind Review Mode**: Anonymous evaluation of ideas
- **File Attachments**: Support for PDF, images, and documents
- **Role-Based Access**: Submitter, Reviewer, Admin roles
- **Real-Time Dashboard**: Overview of all ideas with filtering and sorting

## Project Structure
```
app/
├── api/
│   └── endpoints/          # REST API endpoints
├── core/
│   ├── config.py          # Configuration management
│   ├── security.py        # Authentication & authorization
│   └── deps.py            # Dependency injection
├── db/
│   ├── client.py          # MongoDB connection
│   └── repositories/      # Data access layer
├── models/
│   ├── auth.py            # Auth models
│   ├── idea.py            # Idea schema
│   ├── user.py            # User schema
│   ├── review_stage.py    # Review stage schema
│   └── token.py           # Token models
└── services/
    ├── auth_service.py    # Authentication logic
    ├── idea_service.py    # Idea business logic
    └── review_service.py  # Review workflow logic
```

## Architecture & Documentation
- **API Specification**: [API REST Contracts](specs/003-phase1-mvp-canonical/contracts/api-rest.md)
- **Data Model**: [Database Schema](specs/003-phase1-mvp-canonical/data-model.md)
- **Architectural Decisions**: [ADRs](docs/adrs/)
  - [ADR-001: Data Persistence](docs/adrs/ADR-001-data-persistence.md)
  - [ADR-002: Authentication](docs/adrs/ADR-002-authentication.md)
  - [ADR-003: Testing Strategy](docs/adrs/ADR-003-testing.md)

## Testing
The project uses TDD (Test-Driven Development) with pytest and mutation testing:

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run mutation tests
mutmut run
```

## Technology Stack
- **Backend**: FastAPI, Python 3.11+
- **Database**: MongoDB Atlas with Motor (async driver)
- **API Documentation**: Pydantic, OpenAPI/Swagger
- **Authentication**: OAuth2 + JWT + bcrypt
- **Testing**: pytest, mutmut (mutation testing)
- **Frontend**: React, Vite, TailwindCSS

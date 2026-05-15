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

## User Interface - Screenshots

### Dashboard
All ideas displayed in a unified view with priority filtering and blind review mode.
![Dashboard](docs/screenshots/dashboard.png)

### Authentication
#### Login Page
![Login](docs/screenshots/login.png)

#### Register Page
![Register](docs/screenshots/register.png)

### Idea Management
#### Submit New Idea
Create and submit innovation ideas with attachments, budget estimates, and categorization.
![Submit Idea](docs/screenshots/submit-idea.png)

#### Draft Idea
Save ideas as drafts before publishing.
![Draft Idea](docs/screenshots/draft-idea.png)

### Review Process
#### Review Stages Interface
Multi-stage review process with status tracking and evaluation scoring.
![Review Stages](docs/screenshots/review-stages.png)

#### Validation Handling
Error handling and feedback display during review process.
![Validation](docs/screenshots/validation-error.png)

#### Blind Review Mode
Review ideas anonymously with blind review mode active.
![Blind Review](docs/screenshots/blind-review.png)

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

# InnovatEPAM Portal - Complete Innovation Management Platform

## 🚀 Overview
InnovatEPAM Portal is a full-stack **employee innovation management platform** that enables organizations to collect, evaluate, and nurture innovative ideas through a comprehensive governance workflow. Built with FastAPI, React, and MongoDB, it provides multi-stage review capabilities, file attachments, scoring systems, and blind review functionality for fair and transparent evaluation.

## 📋 Project Journey
This project has evolved through **7 phases** from initial MVP concept to production-ready platform:

- **Phase 1 - MVP**: Core authentication, idea submission, and basic listing
- **Phase 2**: Specification formalization following SpecKit protocol
- **Phase 3**: Multi-media file attachment support with validation
- **Phase 4**: Draft management with publication workflow
- **Phase 5**: Multi-stage review process with approval tracking
- **Phase 6**: Blind review for anonymous evaluation (PHASE 6 BLIND REVIEW)
- **Phase 7**: Scoring system with 1-5 rating and admin controls

## 🛠️ Project Governance
This project follows the **SpecKit Tool-First governance protocol** - a specification-first, test-driven development approach:

- **Specification Source**: specs/003-phase1-mvp-canonical/spec.md (canonical reference)
- **Architecture Decisions**: Documented in docs/adrs/ (ADRs 001-003)
- **Test-Driven Development**: 82% code coverage with 200+ unit and integration tests
- **Specification-First Workflow**: Specify → Plan → Tasks → Implement

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- MongoDB Atlas account
- Git

### Backend Setup
```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configure environment
# Create .env file with MongoDB connection string:
# MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/dbname?retryWrites=true&w=majority

# 4. Run the application
uvicorn src.main:app --reload
# API available at: http://localhost:8000
# Docs at: http://localhost:8000/docs (Swagger UI)

# 5. Run tests
pytest                          # All tests
pytest --cov=app tests/        # With coverage
pytest tests/unit/ -v          # Verbose unit tests
```

### Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
# Frontend available at: http://localhost:5173

# 4. Build for production
npm run build
```

## 📖 Documentation

### API & Technical Specifications
- **[API REST Contracts](specs/003-phase1-mvp-canonical/contracts/api-rest.md)**: 12 REST endpoints with request/response schemas
- **[Data Model](specs/003-phase1-mvp-canonical/data-model.md)**: MongoDB collections, indexes, Pydantic schemas
- **[Specification](specs/003-phase1-mvp-canonical/spec.md)**: Canonical feature specification (source of truth)
- **[Implementation Plan](specs/003-phase1-mvp-canonical/plan.md)**: Design and implementation strategy

### Architecture & Decisions
- **[ADR-001: Data Persistence](docs/adrs/ADR-001-data-persistence.md)**: MongoDB + Motor + GridFS architecture
- **[ADR-002: Authentication](docs/adrs/ADR-002-authentication.md)**: OAuth2 + JWT + bcrypt strategy
- **[ADR-003: Testing](docs/adrs/ADR-003-testing.md)**: TDD approach with 75% mutation minimum

### Developer Resources
- **[Quickstart Guide](specs/003-phase1-mvp-canonical/quickstart.md)**: First steps for developers
- **[Tasks List](specs/003-phase1-mvp-canonical/tasks.md)**: Implementation checklist
- **[Requirements](specs/003-phase1-mvp-canonical/checklists/requirements.md)**: Detailed requirements

## 📸 User Interface Overview

### Dashboard Interface
![Dashboard](docs/screenshots/1.jpg)

- **All Ideas View**: Unified dashboard displaying all submitted ideas with visual organization
- **Priority Filtering**: Ideas categorized by priority levels (High/Medium/Low) with real-time counts
- **Blind Review Toggle**: Enable/disable anonymous evaluation mode to hide creator information
- **Quick Actions**: Direct access to submit new ideas or view detailed idea cards
- **User Welcome**: Personalized greeting with user account information

### Authentication System

**Login Page**
![Login](docs/screenshots/2.jpg)

- Email-based authentication
- Secure password field
- JWT token-based session management
- Account recovery links

**Registration Page**  
![Register](docs/screenshots/3.jpg)

- Email input with validation
- Password creation with strength requirements
- Role selection dropdown (Submitter/Reviewer/Admin)
- Account creation button with validation feedback

### Idea Management Interface

**Submit New Idea**
![Submit Idea](docs/screenshots/4.jpg)

- Title input field (required)
- Rich description textarea with formatting support
- Category dropdown (Product/Process/Service)
- Priority selector (Low/Medium/High)
- Budget estimation field (numeric input)
- File attachment upload (supports PDF, images, documents)
- Submit or Save as Draft options

**Draft Idea Card**
![Draft Idea](docs/screenshots/5.jpg)

- Status badge showing "Draft" state
- Creator and metadata display
- "Publish Idea" button for publication workflow
- Edit capabilities for draft owner
- No Scoring available in draft state

### Multi-Stage Review Interface

**Review Stages Navigation**
![Review Stages](docs/screenshots/6.jpg)

- Visual stage indicators (Stage 1, 2, 3, 4...)
- Current stage highlighting
- Progress tracking through evaluation workflow
- Sequential or parallel review configuration

**Evaluation Form**
- Score dropdown (1-5 scale with descriptions)
- Comment textarea for structured feedback
- Status change buttons (Under Review/Accepted/Rejected)
- History tracking of all stage transitions

**Blind Review Mode**
![Blind Review](docs/screenshots/7.jpg)

- Anonymous idea display (no creator name visible)
- Leadership Review stage identification
- Fair evaluation environment
- Score and comment submission
- Status tracking indicators

**Error & Validation Handling**
- Validation error messages (422 error display)
- Clear feedback on missing required fields
- Form constraint guidance
- API error status information

## ✅ Features & Capabilities

### Core Features (MVP - Phase 1)
- [x] **User Authentication**: OAuth2 + JWT tokens + bcrypt password hashing
- [x] **Idea Submission**: Create, read, update ideas with comprehensive validation
- [x] **File Attachments**: Multi-file upload (PDF, images, documents) with 5MB per file limit

### Extended Features (Phases 3-7)
- [x] **Multi-Media Support**: Enhanced file attachment with format validation
- [x] **Draft Management**: Save ideas as drafts with owner-only visibility
- [x] **Multi-Stage Review**: Configurable review workflow (4 stages: Initial, Business, Leadership, Final)
- [x] **Blind Review Mode**: Anonymous evaluation - creator information hidden during review
- [x] **Scoring System**: 1-5 rating scale with admin-only controls
- [x] **Role-Based Access**: Submitter, Reviewer, Admin roles with distinct permissions
- [x] **Real-Time Dashboard**: Live idea overview with filtering, sorting, and status tracking
- [x] **Evaluation Comments**: Structured feedback system with audit trail

## 📊 Quality Metrics
- **Code Coverage**: 82% (Exceeds 80% target) ✅
- **Test Suite**: 200+ tests across unit, integration, and API endpoint coverage
- **Pass Rate**: 100% (all tests passing)
- **Mutation Testing**: Applied for robustness validation
- **API Documentation**: Full OpenAPI/Swagger specification

## 📁 Project Structure

```
InnovatEPAM-Portal/
├── app/                          # Backend FastAPI application
│   ├── main.py                  # FastAPI app initialization
│   ├── api/
│   │   └── endpoints/           # REST API endpoints
│   │       ├── auth.py          # /auth/* endpoints
│   │       ├── ideas.py         # /ideas/* endpoints
│   │       └── review_stages.py # /review-stages/* endpoints
│   ├── core/
│   │   ├── config.py            # App configuration & secrets
│   │   ├── security.py          # JWT & auth utilities
│   │   └── deps.py              # Dependency injection (FastAPI)
│   ├── db/
│   │   ├── client.py            # MongoDB async connection
│   │   └── repositories/        # Data access layer
│   ├── models/                  # Pydantic schemas
│   └── services/                # Business logic layer
├── frontend/                     # React + Vite SPA
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── api.js               # Axios client for backend
│   │   ├── App.jsx              # Main app component
│   │   └── main.jsx             # Vite entry point
│   ├── vite.config.js           # Vite bundler config
│   ├── tailwind.config.js       # Tailwind CSS config
│   └── package.json             # Frontend dependencies
├── specs/                        # SpecKit specifications
│   └── 003-phase1-mvp-canonical/
│       ├── spec.md              # Canonical specification
│       ├── plan.md              # Implementation plan
│       ├── data-model.md        # Data model & indexes
│       ├── contracts/
│       │   └── api-rest.md      # API endpoint specs
│       └── tasks.md             # Implementation tasks
├── tests/                        # Test suite
│   ├── test_*.py                # Integration tests
│   ├── unit/                    # Unit tests
│   └── api/                     # API endpoint tests
├── docs/
│   └── adrs/                    # Architectural decisions
├── .env                          # Environment variables
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🔐 Security Features
- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Secure token-based authentication
- **OAuth2 Scopes**: Role-based access control
- **CORS Configuration**: Restricted cross-origin access
- **Environment Secrets**: Stored in .env (not committed)
- **Input Validation**: Pydantic schemas enforce type safety

## 🌐 API Endpoints
The application provides 12 REST endpoints:

**Authentication** (3 endpoints)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh

**Ideas** (5 endpoints)
- `GET /ideas/` - List all ideas (filtered by visibility)
- `POST /ideas/` - Create new idea
- `GET /ideas/{idea_id}` - Get idea details
- `PUT /ideas/{idea_id}` - Update idea
- `DELETE /ideas/{idea_id}` - Delete idea (owner/admin only)

**Review Stages** (4 endpoints)
- `GET /review-stages/` - List review configurations
- `POST /review-stages/{idea_id}/evaluate` - Submit evaluation
- `GET /ideas/{idea_id}/review-status` - Get review progress
- `PUT /ideas/{idea_id}/status` - Update idea status

Full specification: [api-rest.md](specs/003-phase1-mvp-canonical/contracts/api-rest.md)

## 🤝 Contributing
1. Follow SpecKit workflow: Specification first, then TDD implementation
2. Maintain 80%+ code coverage with tests
3. Use conventional commit messages
4. Submit PRs against feature branches

## 📝 Key Files
- **Main Entry**: [src/main.py](src/main.py) or [app/main.py](app/main.py)
- **Canonical Spec**: [specs/003-phase1-mvp-canonical/spec.md](specs/003-phase1-mvp-canonical/spec.md)
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **Phase 6 Details**: [PHASE6_BLIND_REVIEW.md](PHASE6_BLIND_REVIEW.md)

## 🎯 Current Status
✅ **Phase 7 Complete** - All features implemented and tested
- Multi-stage review workflow fully functional
- Blind review mode active and tested
- Scoring system integrated
- 82% code coverage achieved
- 200+ tests passing
- Ready for production deployment

## Testing
The project uses **Test-Driven Development (TDD)** with comprehensive test coverage:

```powershell
# Run all tests
pytest

# Run with detailed coverage report
pytest --cov=app tests/

# Run mutation tests (robustness validation)
mutmut run

# Run specific test module
pytest tests/unit/test_auth_service.py -v

# Run with output
pytest -v --tb=short
```

### Test Categories
- **Unit Tests**: app/services, app/models, app/core
- **Integration Tests**: Database interactions, multi-service workflows
- **API Endpoint Tests**: All 12 REST endpoints with various scenarios
- **Coverage**: Core business logic: 85%+, Infrastructure: 50%+, Overall: 82%

## 📚 Technology Stack

| Category | Technology |
|----------|-----------|
| **Backend** | FastAPI 0.104+, Python 3.11+ |
| **Database** | MongoDB Atlas, Motor (async driver), Pydantic v2 |
| **Authentication** | OAuth2, JWT, bcrypt |
| **Frontend** | React 18, Vite, TailwindCSS |
| **API Docs** | OpenAPI/Swagger auto-generated |
| **Testing** | pytest, pytest-asyncio, mutmut |
| **File Storage** | GridFS + local filesystem |

## 🏗️ Architecture

### Backend Architecture (FastAPI)
```
app/
├── api/
│   └── endpoints/
│       ├── auth.py           # Authentication endpoints
│       ├── ideas.py          # Idea CRUD operations
│       └── review_stages.py  # Review workflow endpoints
├── core/
│   ├── config.py            # Configuration & settings
│   ├── security.py          # JWT & auth utilities
│   └── deps.py              # Dependency injection
├── db/
│   ├── client.py            # MongoDB connection
│   └── repositories/
│       ├── user_repository.py
│       ├── idea_repository.py
│       └── review_stage_repository.py
├── models/
│   ├── auth.py              # Auth Pydantic schemas
│   ├── user.py              # User schema
│   ├── idea.py              # Idea schema with validation
│   ├── review_stage.py      # Review workflow schema
│   └── token.py             # JWT token models
└── services/
    ├── auth_service.py      # Authentication business logic
    ├── idea_service.py      # Idea management logic
    └── review_service.py    # Multi-stage review logic
```

### Frontend Architecture (React + Vite)
```
frontend/
├── src/
│   ├── components/
│   │   ├── Login.jsx        # Authentication UI
│   │   ├── Register.jsx     # Registration form
│   │   └── SubmitIdea.jsx   # Idea submission form
│   ├── App.jsx              # Main app component
│   ├── api.js               # API client
│   └── main.jsx             # Entry point
├── vite.config.js           # Vite bundler config
├── tailwind.config.js       # TailwindCSS config
└── package.json             # Dependencies
```

### Data Model
MongoDB collections with Pydantic validation:
- **users**: User accounts, roles, credentials
- **ideas**: Innovation submissions with metadata
- **review_stages**: Review workflow configurations
- **attachments**: File metadata (GridFS integration)

Full schema: [data-model.md](specs/003-phase1-mvp-canonical/data-model.md)

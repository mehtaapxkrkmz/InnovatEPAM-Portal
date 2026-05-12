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

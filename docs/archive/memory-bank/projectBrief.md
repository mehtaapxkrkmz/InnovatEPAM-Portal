# InnovatEPAM Portal - Project Brief

## Project Overview
InnovatEPAM Portal is an employee innovation management platform for collecting, reviewing, and deciding on innovation ideas. The project follows Beyond Vibe Coding principles: specification-first development, explicit architecture decisions, disciplined memory/context management, and test-first implementation.

This implementation is initialized for Module 08 using Python (FastAPI) and MongoDB Atlas.

This MVP is built as a practical capstone to demonstrate an AI-native engineering workflow where requirements, architecture, implementation, and testing are all traceable.

## Phase 1 MVP Scope

### 1) Authentication and User Management
- User registration, login, and logout.
- Basic role distinction:
  - submitter: creates and tracks ideas.
  - admin: reviews and decides on ideas.

### 2) Idea Submission
- Idea submission form with:
  - title
  - description
  - category
- Single file attachment per idea.
- Ability to list and view submitted ideas.

### 3) Evaluation Workflow
- Idea status lifecycle:
  - submitted
  - under review
  - accepted
  - rejected
- Admin can accept or reject with comments.

## Delivery Intent
Phase 1 prioritizes a working, test-backed MVP over advanced functionality. The objective is to deliver core end-to-end value with clear specs, ADR-backed decisions, and constitution-aligned tests.

## Source of Truth
The following documents are the controlling references for implementation decisions in this project phase:
- docs/memory-bank/projectBrief.md
- docs/memos/engineering_standards.md
- specs/adrs/ADR-001-tech-stack.md

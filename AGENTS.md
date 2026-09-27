# AGENTS.md

Instructions for AI Agents working on IncidentIQ.

## Project Overview

IncidentIQ is an AI-powered incident response assistant designed for DevOps/SRE engineers.

## Codebase Guidelines & Standards

- **Frontend**:
  - Located in `frontend/`.
  - Built with React, Vite, and Tailwind CSS.
  - Follow modular component structure and clean functional React paradigms.
  - Run `npm run build` or frontend tests to verify UI changes.

- **Backend**:
  - Located in `backend/`.
  - Built with Python 3, FastAPI, SQLAlchemy, `hindsight-client`, and `groq`.
  - AI Service logic resides in `backend/app/ai_service.py`.
  - Memory Service logic resides in `backend/app/hindsight_service.py`.
  - Route handlers reside in `backend/app/routers/`.
  - Ensure database interactions use SQLAlchemy sessions cleanly.
  - Run `pytest` to verify backend routes, database connections, and AI/memory integrations.

- **Groq AI Integration**:
  - `ai_incident_service.analyze_incident` handles root cause diagnosis and action recommendations.
  - Triggered via `POST /api/v1/incidents/analyze` and `POST /api/v1/incidents/{id}/analyze`.
  - Prompt instructions strictly prohibit fabricating historical incidents or IDs and enforce distinguishing historical evidence from LLM reasoning.
  - Configure via `GROQ_API_KEY` and `GROQ_MODEL`.

- **Hindsight Integration**:
  - Hindsight is used for central persistent memory operations (`RETAIN`, `RECALL`, `REFLECT`).
  - `RETAIN`: Invoked when an incident is created/updated/seeded as resolved.
  - `RECALL`: API endpoint `POST /api/v1/incidents/recall` to fetch past incident memories.
  - `REFLECT`: API endpoint `POST /api/v1/incidents/reflect` to synthesize patterns.
  - Configure via `HINDSIGHT_API_URL`, `HINDSIGHT_API_KEY`, and `HINDSIGHT_BANK_ID`.

- **Data**:
  - Persistent SQLite database files reside in `data/`. Do not commit `.db` binary files to git.

- **Testing & Verification**:
  - Always verify that both frontend builds and backend tests pass before completing tasks.

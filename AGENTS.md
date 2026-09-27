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
  - Built with Python 3, FastAPI, and SQLAlchemy.
  - Keep route handlers modular inside `backend/app/routers/` or `backend/app/main.py`.
  - Ensure database interactions use SQLAlchemy sessions cleanly.
  - Run `pytest` to verify backend routes and database connections.

- **Data**:
  - Persistent SQLite database files reside in `data/`. Do not commit `.db` binary files to git.

- **Testing & Verification**:
  - Always verify that both frontend builds and backend tests pass before completing tasks.

# IncidentIQ

IncidentIQ is an AI-powered incident response assistant for DevOps and SRE engineers.

## Architecture & Tech Stack

- **Frontend**: React, Vite, Tailwind CSS
- **Backend**: FastAPI (Python), Uvicorn, SQLAlchemy
- **Database**: SQLite (stored in `data/incidentiq.db` or configured via env)
- **AI Integrations** (Planned): Groq, Hindsight

## Directory Structure

```
.
├── backend/          # FastAPI backend service
├── frontend/         # React + Vite + Tailwind CSS web interface
├── data/             # SQLite database and persistent data storage
├── .env.example      # Environment variable configurations
├── AGENTS.md         # Instructions and guidance for AI agents
└── README.md         # Project documentation
```

## Getting Started

### Prerequisites

- Node.js (v18+) & npm
- Python 3.10+

### Backend Setup

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy env example file:
   ```bash
   cp ../.env.example .env
   ```
5. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Health check endpoint: `http://localhost:8000/api/v1/health`

### Frontend Setup

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   Access application at: `http://localhost:5173`

## Running Tests

### Backend Tests

```bash
cd backend
pytest
```

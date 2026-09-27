# IncidentIQ

IncidentIQ is an AI-powered incident response assistant for DevOps and SRE engineers.

## Architecture & Tech Stack

- **Frontend**: React, Vite, Tailwind CSS
- **Backend**: FastAPI (Python), Uvicorn, SQLAlchemy
- **Database**: SQLite (stored in `data/incidentiq.db` or configured via env)
- **Central Memory**: Hindsight (`hindsight-client` Python SDK)
- **AI Provider**: Groq LLM API (`groq` Python SDK)

## Directory Structure

```
.
├── backend/          # FastAPI backend service
│   ├── app/
│   │   ├── ai_service.py        # Groq AI incident analysis service
│   │   ├── hindsight_service.py # Hindsight memory service (RETAIN, RECALL, REFLECT)
│   │   ├── routers/             # API route handlers
│   │   └── seed.py              # Initial seed data including INC-101
│   └── tests/                   # Backend pytest test suite
├── frontend/         # React + Vite + Tailwind CSS web interface
├── data/             # SQLite database and persistent data storage
├── .env.example      # Environment variable configurations
├── AGENTS.md         # Instructions and guidance for AI agents
└── README.md         # Project documentation
```

## Complete Investigation & Resolution Workflow

IncidentIQ connects incidents, Hindsight memory recall/retention, and Groq AI into an integrated investigation loop:

```
[Incident Created]
       │
       ▼
[POST /api/incidents/{incident_id}/analyze]
       │
       ├─► 1. Fetch current incident details from SQLite DB
       ├─► 2. Execute Hindsight RECALL to search similar past memories
       ├─► 3. Extract previous root causes and previous resolutions
       ├─► 4. Query Groq LLM with incident context + recalled memories
       └─► 5. Return structured response:
               - current_incident
               - similar_historical_incidents
               - previous_root_causes
               - previous_resolutions
               - ai_analysis
               - recommended_action
               - explanation

[Incident Resolved via POST /api/incidents/{incident_id}/resolve]
       │
       └─► Execute Hindsight RETAIN to store the resolution experience into memory
           so future incidents can recall and learn from it.
```

### Key API Endpoints

- `POST /api/incidents/{incident_id}/analyze` (or `POST /api/v1/incidents/{incident_id}/analyze`):
  Executes the full investigation workflow combining DB incident details, Hindsight RECALL, and Groq AI analysis.
- `POST /api/incidents/{incident_id}/resolve` (or `POST /api/v1/incidents/{incident_id}/resolve`):
  Resolves an incident with `root_cause` and `resolution`, then triggers Hindsight RETAIN.
- `POST /api/v1/incidents/recall`:
  Query Hindsight memory directly for similar past incidents.
- `POST /api/v1/incidents/reflect`:
  Synthesize cross-incident patterns in Hindsight.

## Hindsight Integration

IncidentIQ uses **Hindsight** as its central persistent memory engine:

1. **RETAIN (`hindsight_service.retain_incident`)**:
   Stores resolved incidents and investigation experiences into Hindsight memory banks.
2. **RECALL (`hindsight_service.recall_memories`)**:
   Retrieves relevant historical memories for a new incident or query.
3. **REFLECT (`hindsight_service.reflect_patterns`)**:
   Synthesizes higher-level patterns across multiple memories.

### Configuration

Environment variables in `.env` (or `.env.example`):

```bash
# Hindsight
HINDSIGHT_API_URL=http://localhost:8888
HINDSIGHT_API_KEY=
HINDSIGHT_BANK_ID=incidentiq

# Groq AI
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
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
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy env example file:
   ```bash
   cp ../.env.example .env
   ```
4. Run the FastAPI development server:
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

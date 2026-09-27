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

## Groq AI Incident Analysis

IncidentIQ uses **Groq** (with models such as `llama-3.3-70b-versatile`) to perform automated AI root-cause analysis and remediation recommendations.

### Workflow

1. **Incident Context Retrieval**:
   - For a given incident (new or existing), relevant historical incidents are retrieved from Hindsight persistent memory (`RECALL`).
2. **AI Analysis Generation**:
   - The current incident details alongside recalled historical memories are sent to Groq.
   - Guardrails instruct the AI never to fabricate historical incidents and strictly distinguish historical evidence from model reasoning.
3. **Structured Output**:
   - The analysis endpoint returns a JSON response containing:
     - `probable_root_cause`
     - `recommended_action`
     - `confidence` ("high" | "medium" | "low")
     - `reasoning`
     - `supporting_historical_incidents`

### Analysis Endpoints

- `POST /api/v1/incidents/analyze`: Analyze an uncommitted / new incident.
- `POST /api/v1/incidents/{incident_id}/analyze`: Analyze an existing incident from the database.

## Hindsight Integration

IncidentIQ uses **Hindsight** as its central persistent memory engine to store, retrieve, and synthesize incident investigation experiences.

### Key Operations

1. **RETAIN (`hindsight_service.retain_incident`)**:
   - Stores resolved incidents and their resolution details (service, error, symptoms, severity, root cause, resolution) into Hindsight banks.
   - Automatically triggered when incidents are created as resolved, updated to resolved, resolved via `POST /api/v1/incidents/{id}/resolve`, or seeded on startup (including `INC-101`).

2. **RECALL (`POST /api/v1/incidents/recall`)**:
   - Retrieves relevant historical incidents and memories from Hindsight based on new incident symptoms or query parameters.

3. **REFLECT (`POST /api/v1/incidents/reflect`)**:
   - Synthesizes higher-level patterns, recurring root causes, or architectural vulnerabilities across multiple historical incident memories in Hindsight.

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

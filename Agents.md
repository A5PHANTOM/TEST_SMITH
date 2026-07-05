# TestSmith — Diagnostic Reporting Agent

An OpenCode-compatible AI agent that **scans, analyzes, and reports** on test readiness for any codebase. Produces a structured markdown diagnostic report identifying coverage gaps, dependency issues, and testability concerns. Uses **FastAPI** backend (async), **React + Vite + Tailwind** frontend, and **DeepSeek via OpenCode API**.

---

## Architecture (2 Specialized Agents + Orchestrator)

| Agent | Role | OpenCode Tools Used |
|---|---|---|
| **Scanner** | Reads target repo, identifies source files & existing tests, maps dependency graph | `read`, `glob`, `grep`, `ls` |
| **Analyzer** | Reads source code via AST, produces diagnostic markdown report with coverage gaps, import issues, and testability concerns | `read` |

**Orchestrator** pipeline flow:
1. `Scanner` → produces `analysis.json` (files, deps, existing coverage, entry points)
2. `Analyzer` → produces markdown report covering coverage, dependencies, testability, recommendations
3. Final state → `done` — view or download the report

---

## Stack

- **Backend**: FastAPI async + SQLAlchemy + SQLite (aiosqlite)
- **Frontend**: React 19 + Vite + Tailwind 4 + react-router
- **Agent runtime**: OpenCode API (DeepSeek V4) — agent mode with tool calling
- **Backend tests**: pytest + httpx

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /api/runs | Start diagnostic run (body: `repo_path`) |
| GET | /api/runs | List past runs |
| GET | /api/runs/{id} | Run detail (analysis + full report) |
| POST | /api/runs/{id}/dismiss | Mark run as dismissed (discard) |
| WS | /ws/runs/{id} | Live stream — agent status, report progress |

**WebSocket event types**:
- `{"event":"agent_status","agent":"scanner|analyzer","status":"idle|working|done","detail":"..."}`
- `{"event":"report_ready","report":"..."}`
- `{"event":"run_complete","run_id":N}`

---

## Data Model (Run)

```
Run {
  id: int PK
  repo_path: str
  status: enum(pending|scanning|analyzing|done|dismissed|rejected)
  analysis: JSON (Scanner output)
  report: Text (markdown diagnostic report, null until analysis completes)
  transcript: JSON (full agent conversation)
  created_at, updated_at: datetime
}
```

---

## File Layout

```
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI app, CORS, lifespan
│   │   ├── db.py                     # SQLAlchemy async engine + session
│   │   ├── models/
│   │   │   └── run.py                # Run ORM model
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── runs.py               # REST endpoints
│   │   │   └── ws.py                 # WebSocket handler
│   │   ├── orchestrator/
│   │   │   ├── __init__.py
│   │   │   ├── loop.py               # Orchestrator logic (single pass)
│   │   │   ├── scanner.py            # Scanner sub-agent
│   │   │   ├── reporter.py           # Analyzer sub-agent (produces report)
│   │   │   └── prompts/
│   │   │       ├── __init__.py
│   │   │       ├── scanner.py
│   │   │       └── generator.py      # Analyzer system prompt
│   │   └── mcp_server/
│   │       ├── __init__.py
│   │       └── tools.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_reporter.py
│   │   ├── test_scanner.py
│   │   ├── test_loop.py
│   │   └── test_ws.py
│   ├── .env                          # OPENCODE_API_KEY, MODEL, DB_URL, REPO_ROOT_WHITELIST
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── NewRun.jsx            # Configure & launch a diagnostic run
│   │   │   ├── LiveRun.jsx           # Real-time streaming dashboard
│   │   │   ├── RunDetail.jsx         # View report + download .md + dismiss
│   │   │   └── History.jsx           # Past runs
│   │   ├── components/
│   │   │   ├── AgentStatus.jsx       # Per-agent status card
│   │   │   └── LiveFeed.jsx          # WebSocket event log
│   │   ├── hooks/
│   │   │   └── useRunSocket.js       # WebSocket hook
│   │   └── api/
│   │       └── client.js             # REST API client
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── AGENTS.md                         # This file
```

---

## Architectural Rules (Non-Negotiable)

1. **Scanner** reports only what OpenCode MCP tools observed — no guessing. Unclear areas go in `notable_patterns`.
2. **Analyzer** produces reports based on actual source code analysis (AST parsing). No invented findings.
3. **No test files are generated or written to disk.** This is a diagnostic-only tool.
4. **Report writing** only happens through the API (`report` field on the Run model). Never writes to the target repo.
5. Prompt templates in `orchestrator/prompts/*.py` — never inlined in logic.

---

## Safety

- Repo path validated against whitelist (env `REPO_ROOT_WHITELIST`) — reject `../` or paths resolving outside.
- Source file reads capped at 100KB during scanning.
- AST analysis is read-only — never modifies source files.
- `.env` gitignored, secrets never committed.

---

## Conventions

- FastAPI async endpoints for I/O. Pydantic models for all schemas. Type hints everywhere.
- SQLAlchemy models in `models/`, one file per table.
- React: functional components + hooks only. Tailwind 4. One file per component.
- WebSocket hook: `hooks/useRunSocket.js`. API calls: `api/client.js` (no raw fetch).
- No emojis. Dark theme with monospace accents.
- Commit messages: `feat:|fix:|refactor:|test:` prefixes.
- `.env` gitignored, secrets never committed.

---

## Setup

```bash
# Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8001

# Frontend
cd frontend && npm install && npm run dev
```

**Env** (`backend/.env`):
```
OPENCODE_API_KEY=...
MODEL=deepseek-v4
DB_URL=sqlite+aiosqlite:///./testsmith.db
REPO_ROOT_WHITELIST=*
TEST_TIMEOUT_SECONDS=300
```

---

## Tests

```bash
cd backend && source venv/bin/activate && pytest tests/ -v
```

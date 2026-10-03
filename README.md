# SupportOps AI

Enterprise-style AI support operations platform for ticket classification, priority detection, sentiment analysis, smart routing, SLA-risk prediction, AI summaries, and operations analytics.

## What is included

- FastAPI backend
- SQLAlchemy database layer
- SQLite local mode: zero PostgreSQL setup required
- Seeded demo data
- Ticket CRUD and search
- AI classification/category/subcategory
- Priority scoring
- Sentiment analysis
- SLA-risk prediction
- Skill/workload routing
- AI summary and recommended action fallback
- Operations analytics
- Interactive dashboard
- Health/readiness endpoints
- Optional LLM configuration
- React/Vite starter source directory for future frontend expansion
- ML classifier module and training-ready artifact path

## Run on Windows

### Recommended

Open PowerShell in the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe scripts\seed.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

Then open:

- Dashboard: http://127.0.0.1:8000/dashboard
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/v1/health

Or simply run:

```powershell
.\start.ps1
```

## API examples

Create a ticket:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/tickets -ContentType 'application/json' -Body '{"customer_name":"Vansh","subject":"Production API timeout","description":"Our production API is timing out for multiple users and business is blocked.","auto_analyze":true}'
```

List tickets:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/tickets
```

## Optional PostgreSQL / LLM

The local build intentionally defaults to SQLite and local AI so the project works immediately. For deployment, set `DATABASE_URL` to PostgreSQL and configure an LLM provider in `backend/.env`.

## Architecture

Customer/Ticket Sources -> FastAPI -> AI Pipeline -> Database -> Operations Dashboard

AI pipeline:

Ticket -> classification -> priority -> sentiment -> SLA risk -> routing -> summary/action -> analytics

## Project layout

```text
SupportOps-AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
├── ai/
│   └── models/
├── frontend/
│   └── dashboard.html
├── scripts/
│   └── seed.py
├── data/
├── logs/
├── run.py
├── start.ps1
└── README.md
```

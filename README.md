# SprintFlow — Agile/Scrum API + Basic UI (FastAPI)

SprintFlow is a lightweight Agile/Scrum tracker built with **FastAPI**, **SQLAlchemy**, and **JWT auth**, plus a minimal **Jinja2** UI for login + project browsing.

## Features
- JWT authentication (register/login) + user scoping
- Role-based access control per project: **ADMIN / MEMBER / VIEWER**
- CRUD for:
  - Projects
  - Memberships
  - Stories (backlog)
  - Sprints (planned/active/closed)
  - Sprint Items (sprint planning: add/remove stories)
- Minimal UI (Jinja2):
  - Login / Logout
  - Project list
  - Project detail (stories + sprints)

## Tech Stack
- FastAPI, Pydantic
- SQLAlchemy (SQLite for dev)
- Jinja2 templates + Session cookie for UI auth

## Running locally

### 1) Create venv + install deps
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2) Run
```bash
uvicorn app.main:app --reload
```
Open:
- UI: http://127.0.0.1:8000/ui/login
- API docs: http://127.0.0.1:8000/docs

## API Quick Test (curl)

### Register
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123"}'
```

### Login
```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo $TOKEN
```

### Create project
```bash
curl -X POST http://127.0.0.1:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key":"P1","name":"Project One"}'
```

### Notes / Design Decisions
- Some endpoints return 403 instead of 404 to reduce resource enumeration.
- SQLite is used for local development; migrations can be added later (Alembic).
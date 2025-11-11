# Sales CRM - Minimal MVP

> A quick proof-of-concept Sales CRM built to demonstrate modern full-stack development.

## What is it?

A working end-to-end lead management system:
- ✅ Create, read, update, delete leads
- ✅ Tenant-aware (multi-company support)
- ✅ REST API with auto-docs
- ✅ Modern React UI
- ✅ AI email generation (OpenAI)

**Tech Stack**: FastAPI + React + PostgreSQL (all containerized)

## 🚀 Quick Start

```bash
# 1. Copy environment template
copy .env.example .env

# 2. Start everything
docker-compose up --build

# 3. Open in browser
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

Done! Sample data is already loaded.

## 📁 Structure

```
sales-crm/
├── backend/          # FastAPI (main.py, models.py, schemas.py, crud.py)
├── frontend/         # React (App.jsx + components)
├── database/         # init.sql
├── tests/            # pytest tests
├── docker-compose.yml
└── pyproject.toml
```

## 🛠️ Local Development

```bash
# Install Poetry
pip install poetry

# Backend
poetry install
poetry run uvicorn backend.main:app --reload

# Frontend (separate terminal)
cd frontend && npm install && npm run dev

# Database (separate terminal)
docker-compose up postgres
```

## 🧪 Quality Tools

```bash
poetry run pytest              # Run tests
poetry run ruff check backend/ # Lint code
poetry run mypy backend/       # Type check
```

## 🎯 Key Features

### API (FastAPI)
- Auto-generated docs at `/docs`
- Full CRUD for leads
- Tenant filtering
- Type-safe with Pydantic

### UI (React)
- Lead creation form
- Card-based lead view
- Status tracking
- AI email generator

### Database
- Two tables: `tenants`, `leads`
- Foreign key constraints
- Auto-timestamps
- Sample data on startup

## 🤖 AI Email Generator

If you add an OpenAI API key to `.env`, the app can generate personalized emails for leads:

```
OPENAI_API_KEY=sk-...
```

Click the "🤖 Email" button on any lead card to try it!

## ⚡ Demo Flow

1. `docker-compose up` → Everything starts
2. Open http://localhost:5173
3. Create a few leads
4. Try AI email generation
5. Update lead statuses
6. Show API docs at `/docs`

## 🎯 MVP Philosophy

**Included**: Core CRUD + tenant awareness + AI feature  
**Excluded**: Auth, advanced search, reporting, mobile app  
**Why**: Demonstrates capability without over-engineering

This is intentionally minimal - built to show understanding of:
- Modern architecture (REST API, SPA, containerization)
- Clean code (type hints, separation of concerns)
- Practical trade-offs (MVP scope)

## 📊 API Endpoints

```
GET    /api/tenants          List tenants
POST   /api/tenants          Create tenant

GET    /api/leads            List leads (filterable)
POST   /api/leads            Create lead
GET    /api/leads/{id}       Get lead
PUT    /api/leads/{id}       Update lead
DELETE /api/leads/{id}       Delete lead

POST   /api/ai/generate-email  Generate email template
```

## 🔧 Environment Variables

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sales_crm
OPENAI_API_KEY=sk-...  # Optional
```

## 📝 Notes

- Poetry for Python deps (modern, reproducible)
- Vite for React (fast dev server)
- Docker Compose for easy orchestration
- Type hints throughout (mypy compatible)
- Tests included (pytest)

---

**Built as a proof of concept to demonstrate modern development practices** 🚀

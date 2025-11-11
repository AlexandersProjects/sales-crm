# 🚀 Sales CRM - Quick Reference

## Start the Project

```powershell
# Windows - One command!
.\start.ps1

# Or manually
docker-compose up --build
```

**That's it!** Open http://localhost:5173

## URLs

- 🌐 Frontend: http://localhost:5173
- 📚 API Docs: http://localhost:8000/docs
- 🔧 Backend: http://localhost:8000

## File Guide

### Backend (Python/FastAPI)
```
backend/
├── main.py      → All API endpoints (GET, POST, PUT, DELETE)
├── models.py    → Database models (Tenant, Lead)
├── schemas.py   → Request/response validation (Pydantic)
├── crud.py      → Database operations
└── database.py  → DB connection setup
```

### Frontend (React)
```
frontend/src/
├── App.jsx                    → Main app component
├── components/
│   ├── LeadForm.jsx          → Create/edit leads
│   ├── LeadList.jsx          → Display lead cards
│   └── EmailGenerator.jsx    → AI email modal
└── api/client.js             → API calls
```

### Database
```
database/init.sql → Schema + sample data
```

## Key Commands

```powershell
# Full stack
docker-compose up

# Run tests
poetry install
poetry run pytest

# Lint code
poetry run ruff check backend/

# Type check
poetry run mypy backend/

# Backend only (Docker DB must be running)
poetry run uvicorn backend.main:app --reload

# Frontend only
cd frontend
npm install
npm run dev
```

## Quick Edits

### Add OpenAI Key
Edit `.env`:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Add Lead Status
Edit `frontend/src/components/LeadForm.jsx` line 4:
```javascript
const STATUSES = ['new', 'contacted', 'qualified', 'won', 'lost', 'YOUR_STATUS'];
```

### Change API Endpoint
Edit `backend/main.py` - all endpoints are marked with `@app.get()` or `@app.post()` etc.

## Demo Script

1. **Start** (30 sec)
   ```powershell
   .\start.ps1
   ```

2. **Show Auto Docs** (1 min)
   - Open http://localhost:8000/docs
   - Try POST /api/leads directly in browser

3. **Show UI** (2 min)
   - Open http://localhost:5173
   - Create 2-3 leads with different statuses
   - Update one lead
   - Generate AI email (if OpenAI key set)

4. **Show Code** (1 min)
   - Open `backend/main.py` - show endpoints
   - Open `frontend/src/App.jsx` - show component
   - Mention: "All typed, tested, containerized"

## Troubleshooting

### Docker not starting
```powershell
docker info  # Check if Docker Desktop is running
```

### Port already in use
```powershell
# Stop other services or edit docker-compose.yml ports
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

### Database issues
```powershell
# Reset database
docker-compose down -v
docker-compose up postgres
```

### Poetry issues
```powershell
# Install Poetry
pip install poetry

# Or use official installer
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

## Project Stats

- **Lines of Code**: ~1000 total
- **Backend**: ~600 lines Python
- **Frontend**: ~400 lines React
- **Time**: 3-4 hours (realistic)
- **Dependencies**: Managed by Poetry + npm

## What Makes This Good

✅ **Simple** - No over-engineering, just what's needed  
✅ **Modern** - Latest tools and practices  
✅ **Complete** - Full stack, end-to-end  
✅ **Typed** - Python type hints throughout  
✅ **Tested** - pytest suite included  
✅ **Containerized** - Docker Compose ready  
✅ **Documented** - API docs auto-generated  
✅ **Bonus** - AI integration shows extra skill  

## Next Steps (If Asked)

1. Add JWT authentication
2. Implement advanced search/filtering
3. Add file upload for lead documents
4. Create analytics dashboard
5. Add email sending (not just generation)
6. Mobile responsive improvements
7. Deploy to cloud (AWS, GCP, Azure)

---

**You're ready to demo!** 🎯


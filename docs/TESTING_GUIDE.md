# 🎯 Complete Testing Guide (No Poetry Needed!)

## ✅ The Simple Solution

Poetry is broken in this directory, but **you don't need it!** Everything runs in Docker anyway.

---

## 🔍 1. Check Database

### Option A: Use the Script
```powershell
.\check_db.ps1
```

### Option B: Manual Steps
```powershell
# Install dependencies (once)
py -m pip install rich sqlalchemy psycopg2-binary python-dotenv

# Run check
py check_database.py
```

### Option C: Direct SQL
```powershell
# Connect to Docker database
docker exec -it sales-crm-db psql -U postgres -d sales_crm

# Run queries
SELECT COUNT(*) FROM tenants;
SELECT * FROM leads;
SELECT status, COUNT(*) FROM leads GROUP BY status;

# Exit
\q
```

**Expected output:**
```
🔍 Sales CRM Database Checker

✓ Database connection successful!

Checking Tenants:
┏━━━━┳━━━━━━━━━━━━━━┓
┃ ID ┃ Name         ┃
┡━━━━╇━━━━━━━━━━━━━━┩
│ 1  │ Demo Company │
└────┴──────────────┘

✓ Found 1 tenant(s)

[Shows leads in table]
```

---

## 📧 2. Test Email Generation

### Option A: Use the Script
```powershell
.\test_email.ps1
```

### Option B: Manual Steps
```powershell
# Install dependencies (once)
py -m pip install rich openai

# Make sure OpenAI key is in .env
# OPENAI_API_KEY=sk-your-key-here

# Run test
py test_email_generation.py
```

### Option C: Test in UI
1. Add OpenAI key to `.env`
2. Restart Docker: `docker-compose down && docker-compose up`
3. Open http://localhost:5173
4. Click "🤖 Email" on any lead
5. Generate email

**Expected output:**
```
🤖 Email Generation Tester

✓ OpenAI API key found

Test Case 1:
  Lead: John Doe
  Company: Acme Corp

┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ✓ Generated Email #1   ┃
┃ Subject: Partnership...┃
┃ Body: Dear John, ...   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🎨 3. Check UI

### Just Open Browser
```powershell
start http://localhost:5173
```

**What to check:**
- ✅ Purple gradient background
- ✅ Frosted glass cards
- ✅ Lead form on left
- ✅ Lead cards on right
- ✅ Sample data visible
- ✅ Smooth animations on hover

### Hard Refresh
If styles don't look updated:
```
Ctrl + Shift + R
```

---

## 📊 4. Check API

### Open Swagger UI
```powershell
start http://localhost:8000/docs
```

**Test endpoints:**
1. `GET /api/tenants` - Should return Demo Company
2. `GET /api/leads` - Should return sample leads
3. `POST /api/leads` - Create a new lead
4. `GET /health` - Should return `{"status": "healthy"}`

---

## 🐳 Docker Commands

### View Logs
```powershell
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Follow logs (live)
docker-compose logs -f backend
```

### Restart Services
```powershell
# Restart one service
docker-compose restart backend

# Restart all
docker-compose down
docker-compose up
```

### Check Status
```powershell
# See running containers
docker-compose ps

# See container health
docker ps
```

---

## 🔧 Troubleshooting

### Python not found?
You have Python installed (works in proof_tracker). Try:
```powershell
# Find Python
where.exe python
where.exe py

# Use full path
C:\Users\Alex\AppData\Local\Programs\Python\Python313\python.exe check_database.py
```

### Database connection fails?
```powershell
# Make sure database is running
docker-compose ps

# Check database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### OpenAI test fails?
```powershell
# Check if key is set
Get-Content .env | Select-String "OPENAI"

# Make sure format is correct (no quotes, no spaces)
# OPENAI_API_KEY=sk-...
```

### UI not updating?
```powershell
# Restart frontend
docker-compose restart frontend

# Or rebuild
docker-compose down
docker-compose up --build frontend
```

---

## 💡 Why Poetry Doesn't Matter Here

**The Truth:**
- ✅ Backend runs in Docker → Docker has Poetry
- ✅ Frontend runs in Docker → Uses npm
- ✅ Database runs in Docker → Just PostgreSQL
- ✅ Test scripts → Work with plain Python

**Poetry is only needed in Docker**, not on your local machine!

The `pyproject.toml` file is used by Docker when building the backend image. Your local Poetry installation is irrelevant.

---

## 📋 Quick Reference

| Task | Command |
|------|---------|
| Start everything | `docker-compose up` |
| Check database | `.\check_db.ps1` or `python check_database.py` |
| Test email | `.\test_email.ps1` or `python test_email_generation.py` |
| View UI | `start http://localhost:5173` |
| View API docs | `start http://localhost:8000/docs` |
| Connect to DB | `docker exec -it sales-crm-db psql -U postgres -d sales_crm` |
| View logs | `docker-compose logs -f` |

---

## ✅ Summary

**You asked:**
1. ❓ How to check database?
2. ❓ How to test email generation?
3. ❓ Why Poetry doesn't work?

**Answers:**
1. ✅ Use `.\check_db.ps1` or `python check_database.py`
2. ✅ Use `.\test_email.ps1` or `python test_email_generation.py`
3. ✅ Poetry is broken locally but **you don't need it!** Everything runs in Docker

**Just use these commands:**
```powershell
# Install dependencies first (one time)
py -m pip install rich sqlalchemy psycopg2-binary python-dotenv openai

# Check database
py check_database.py

# Test email
py test_email_generation.py

# View in browser
start http://localhost:5173
```

**That's it! No Poetry needed!** 🎉


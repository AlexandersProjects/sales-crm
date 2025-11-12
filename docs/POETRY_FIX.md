# 🔧 Poetry Setup Fix

## Problem

Poetry commands are failing with "Das System kann den angegebenen Pfad nicht finden" (System cannot find the specified path). This means Poetry's Python configuration is broken.

## Quick Solution: Use Python Directly

Since the backend runs in Docker anyway, you can run the test scripts directly with Python (without Poetry):

### 1. Install Dependencies Directly

```powershell
# Install required packages with pip
pip install rich sqlalchemy psycopg2-binary python-dotenv openai
```

### 2. Run Database Checker

```powershell
# Direct Python execution
python check_database.py
```

### 3. Run Email Generation Test

```powershell
# Direct Python execution
python test_email_generation.py
```

---

## Alternative: Fix Poetry

If you want to fix Poetry properly:

### Option 1: Reinstall Poetry

```powershell
# Uninstall Poetry
pip uninstall poetry

# Reinstall Poetry
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### Option 2: Use Different Directory

The issue might be specific to this directory. Try:

```powershell
# Copy the working proof_tracker poetry config
Copy-Item C:\Users\Alex\Workspaces\proof_tracker\.venv C:\Users\Alex\Workspaces\sales-crm\.venv -Recurse

# Or start fresh in a new directory
```

### Option 3: Skip Poetry for Scripts

Poetry is mainly useful for:
- Dependency management (handled by Docker)
- Virtual environment isolation
- Publishing packages (not needed here)

For this MVP, you don't really need Poetry locally since everything runs in Docker!

---

## Simplified Commands (No Poetry Needed)

### Install Test Dependencies

```powershell
pip install rich sqlalchemy psycopg2-binary python-dotenv openai
```

### Run Tests

```powershell
# Database check
python check_database.py

# Email generation test (needs OpenAI key in .env)
python test_email_generation.py

# Backend tests (if you want)
pytest tests/
```

### Run Backend Locally (Without Docker)

```powershell
# Install all dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv openai rich email-validator

# Run backend
cd backend
python -m uvicorn main:app --reload
```

---

## Why This Works

**Docker handles the real dependencies:**
- The Docker container has its own Python environment
- Poetry is used IN the container (Dockerfile)
- Local Poetry is just for convenience

**For testing scripts:**
- They're simple standalone scripts
- Just need a few libraries (rich, sqlalchemy)
- Can use pip instead of Poetry

---

## Quick Reference

### Check Database (No Poetry)
```powershell
# Install if needed
pip install rich sqlalchemy psycopg2-binary

# Run
python check_database.py
```

### Test Email (No Poetry)
```powershell
# Install if needed
pip install rich openai

# Set OpenAI key in .env first
# Run
python test_email_generation.py
```

### Check Database Manually
```powershell
# Connect to Docker PostgreSQL
docker exec -it sales-crm-db psql -U postgres -d sales_crm

# Run SQL
SELECT COUNT(*) FROM tenants;
SELECT * FROM leads;
\q
```

---

## Bottom Line

**You don't need Poetry working locally!**

1. ✅ Backend runs in Docker (Poetry works there)
2. ✅ Frontend runs in Docker (npm works there)
3. ✅ Test scripts can use plain Python + pip

Just use:
```powershell
pip install rich sqlalchemy psycopg2-binary openai
python check_database.py
python test_email_generation.py
```

**Much simpler!** 🎉


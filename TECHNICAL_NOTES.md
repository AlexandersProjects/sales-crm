# 🔧 Technical Details & Updates

## ✅ Recent Updates

### Python Version Updated: 3.13
- **Updated from**: Python 3.11
- **Updated to**: Python 3.13-slim (latest stable)
- **Why**: You're using Python 3.13 locally, and `python:3.13-slim` Docker image is available
- **Benefits**: Latest features, performance improvements, better type checking

### Dependencies Updated (November 2025)
All Python packages updated to latest compatible versions:
- **FastAPI**: 0.104 → 0.115 (latest features)
- **Uvicorn**: 0.24 → 0.32 (better performance)
- **SQLAlchemy**: 2.0.23 → 2.0.36 (bug fixes)
- **Pydantic**: 2.5 → 2.10 (improved validation)
- **OpenAI**: 1.3 → 1.54 (latest API features)
- **pytest**: 7.4 → 8.3 (new testing features)
- **ruff**: 0.1 → 0.7 (faster, more checks)
- **mypy**: 1.7 → 1.13 (better type inference)

### Fixed Issues
- ✅ **Frontend Dockerfile**: Was empty, now properly configured with Node.js 18
- ✅ **Backend Dockerfile**: Updated to Python 3.13-slim
- ✅ **Docker context**: Fixed to properly access pyproject.toml from root
- ✅ **Dependencies**: All updated to latest compatible versions

---

## 🚀 What is Uvicorn?

### Simple Explanation
**Uvicorn** is a lightning-fast ASGI web server that runs your FastAPI application.

Think of it like this:
```
Your FastAPI code (main.py) → Uvicorn (server) → HTTP requests from browser
```

### Key Points

**1. What it does:**
- Runs your FastAPI application as a web server
- Handles incoming HTTP requests
- Manages connections efficiently
- Provides hot-reload during development

**2. Why FastAPI needs it:**
- FastAPI is a **framework** (tells you how to write code)
- Uvicorn is a **server** (actually runs that code)
- FastAPI doesn't run by itself - it needs a server like Uvicorn

**3. The Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Breaking it down:
- `uvicorn` - The server program
- `main:app` - Import `app` from `main.py` 
- `--host 0.0.0.0` - Listen on all network interfaces (needed for Docker)
- `--port 8000` - Listen on port 8000
- `--reload` - Auto-restart when code changes (development only)

### ASGI vs WSGI

**WSGI (older, synchronous):**
- Used by Flask, Django (traditional)
- One request at a time per worker
- Example: Gunicorn

**ASGI (newer, asynchronous):**
- Used by FastAPI, Starlette
- Multiple requests simultaneously
- Better for modern async code
- Example: Uvicorn

### Why Uvicorn with `[standard]` extras?

```toml
uvicorn = {extras = ["standard"], version = "^0.32.0"}
```

**Standard extras include:**
- `uvloop` - Ultra-fast event loop (10x faster than default)
- `httptools` - Fast HTTP parsing in C
- `websockets` - WebSocket support
- `watchfiles` - Better file watching for reload

**Performance difference:**
- Basic Uvicorn: ~20k requests/sec
- Uvicorn[standard]: ~50k+ requests/sec

### Alternatives to Uvicorn

**Other ASGI servers:**
1. **Hypercorn** - Supports HTTP/2, slower than Uvicorn
2. **Daphne** - Made for Django Channels
3. **Gunicorn + Uvicorn** - Production setup (multiple workers)

**Production setup** (you'd use later):
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### In Your Project

**Development:**
```bash
poetry run uvicorn backend.main:app --reload
```

**Docker (from Dockerfile):**
```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Production** (what you'd change to):
```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
# Remove --reload in production!
```

---

## 📦 Docker Build Context Explanation

### The Fix We Made

**Before (broken):**
```yaml
backend:
  build:
    context: ./backend  # ❌ Can't see pyproject.toml in parent dir
    dockerfile: Dockerfile
```

**After (fixed):**
```yaml
backend:
  build:
    context: .  # ✅ Build from project root
    dockerfile: ./backend/Dockerfile  # Use this Dockerfile
```

### Why This Matters

**Docker build context** = the files Docker can see during build

When we run `COPY pyproject.toml ./` in the Dockerfile:
- With `context: ./backend` → Can't find it (file is outside)
- With `context: .` → Can find it (file is in parent, which is included)

### The Dockerfile Strategy

```dockerfile
FROM python:3.13-slim
WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy pyproject.toml from context root (project root)
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --only main

# Copy backend code
COPY backend/ ./backend/

# Work from backend directory
WORKDIR /app/backend

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key insight**: We copy `pyproject.toml` from project root, but run the app from `/app/backend`.

---

## 🔍 Quick Reference

### Start Commands

```bash
# Full stack (easiest)
.\start.ps1

# Or manually
docker-compose up --build

# Backend only (local development)
poetry install
poetry run uvicorn backend.main:app --reload

# Frontend only
cd frontend && npm install && npm run dev
```

### Check Versions

```bash
# Python version
py --version  # Should show 3.13.x

# Poetry
poetry --version

# Docker Python image
docker run --rm python:3.13-slim python --version
```

### Update Dependencies

```bash
# Update all to latest compatible versions
poetry update

# Update specific package
poetry update fastapi

# Show outdated packages
poetry show --outdated
```

---

## 💡 Pro Tips

### Development Mode
Uvicorn's `--reload` watches for file changes and auto-restarts. Perfect for development!

### Production Mode
Remove `--reload`, add multiple workers:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Performance Monitoring
Add logs to see Uvicorn working:
```bash
uvicorn main:app --log-level debug
```

### Why Python 3.13?
- **Performance**: 5-10% faster than 3.11
- **Better error messages**: More helpful tracebacks
- **Type hints**: Improved syntax and features
- **Future-proof**: Latest stable version

---

**Your project is now up-to-date with modern dependencies and Python 3.13!** 🎉


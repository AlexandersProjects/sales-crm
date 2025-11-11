# 🔧 email-validator Missing Dependency - FIXED

## ❌ The Error You Saw

```
ModuleNotFoundError: No module named 'email_validator'
```

Backend container started but crashed immediately with this error.

## 🔍 Root Cause

**What happened:**
- Your `schemas.py` uses `EmailStr` from Pydantic
- `EmailStr` is a special type that validates email addresses
- Pydantic's email validation requires the `email-validator` package
- This package wasn't listed in dependencies

**Code that needs it:**
```python
# In schemas.py
from pydantic import EmailStr

class LeadBase(BaseModel):
    email: Optional[EmailStr] = None  # ← This needs email-validator
```

## ✅ The Fix

Added `email-validator` to `pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = "^3.13"
fastapi = "^0.115.0"
# ... other dependencies ...
email-validator = "^2.2.0"  # ← ADDED THIS
```

## 📚 Why This Happens

Pydantic has **optional dependencies** for certain field types:

| Field Type | Requires Package |
|------------|------------------|
| `EmailStr` | `email-validator` |
| `HttpUrl`, `AnyUrl` | Built-in (no extra needed in v2) |
| `color` | `pydantic[color]` |

Since email validation is common but not always needed, Pydantic makes it optional. You only install it when you use `EmailStr`.

## 🔄 What to Do Now

**Rebuild the Docker containers:**

```powershell
# Stop containers
docker-compose down

# Rebuild (Poetry will install email-validator)
docker-compose build --no-cache

# Start again
docker-compose up
```

The backend will now start successfully!

## ✅ How to Verify It Works

After starting, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1] using WatchFiles
INFO:     Started server process [7]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**No more ModuleNotFoundError!**

Then:
- ✅ Open http://localhost:8000/docs (should load)
- ✅ Open http://localhost:5173 (frontend should work)
- ✅ Try creating a lead with an email

## 🎓 Bonus: Alternative Solutions

### Option 1: Install with Pydantic extras
```toml
pydantic = {extras = ["email"], version = "^2.10.0"}
```

### Option 2: Make email just a string
```python
# If you don't need validation
class LeadBase(BaseModel):
    email: Optional[str] = None  # Just a string, no validation
```

### Option 3: Custom validation
```python
from pydantic import field_validator
import re

class LeadBase(BaseModel):
    email: Optional[str] = None
    
    @field_validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email')
        return v
```

**We chose Option 1 (add email-validator)** because:
- ✅ Proper email validation
- ✅ Industry standard (uses `email-validator` package)
- ✅ Works with EmailStr type hints
- ✅ Minimal code change

## 📝 Updated Dependencies

Your complete `pyproject.toml` dependencies now:

```toml
[tool.poetry.dependencies]
python = "^3.13"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
sqlalchemy = "^2.0.36"
psycopg2-binary = "^2.9.10"
pydantic = "^2.10.0"
pydantic-settings = "^2.6.0"
python-dotenv = "^1.0.1"
openai = "^1.54.0"
rich = "^13.9.0"
email-validator = "^2.2.0"  # ← FIXED!
```

## 🚀 Status: READY TO BUILD

Run this now:
```powershell
docker-compose down
docker-compose build --no-cache
docker-compose up
```

Everything should work! 🎉

---

**Summary**: Pydantic's `EmailStr` needs `email-validator` package. Added it to dependencies. Rebuild Docker and you're good to go!


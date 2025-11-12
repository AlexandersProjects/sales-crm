# ✅ FINAL SOLUTION - Working Commands!

## The Problem
- `pip` command doesn't exist in PATH
- Need to use `py -m pip` instead
- Packages weren't installed

## ✅ THE SOLUTION (Copy & Paste These!)

### Step 1: Install Packages (One Time Only)
```powershell
py -m pip install rich sqlalchemy psycopg2-binary python-dotenv openai
```

**Note:** `python-dotenv` loads your `.env` file automatically so the scripts can read environment variables like `OPENAI_API_KEY`!

### Step 2: Check Database
```powershell
py check_database.py
```

### Step 3: Test Email Generation (Optional - needs OpenAI key)
```powershell
py test_email_generation.py
```

---

## Why `py -m pip` Instead of `pip`?

**The Issue:**
- Windows Python Launcher (`py`) works ✅
- But `pip` isn't in your PATH ❌
- Solution: Use `py -m pip` (calls pip as a module)

**Command Reference:**
```powershell
# ❌ DOESN'T WORK
pip install package

# ✅ WORKS!
py -m pip install package
```

---

## Complete Working Commands

```powershell
# 1. Install everything you need (run once)
py -m pip install rich sqlalchemy psycopg2-binary python-dotenv openai

# 2. Check database
py check_database.py

# 3. Test email (needs OpenAI key in .env)
py test_email_generation.py

# 4. Or use the wrapper scripts
.\check_db.ps1
.\test_email.ps1
```

---

## Expected Output

### Database Check:
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

Checking Leads:
[Shows lead table]
```

### Email Test:
```
🤖 Email Generation Tester

✓ OpenAI API key found

Test Case 1:
  Lead: John Doe
  ...
```

---

## Quick Test Right Now

Copy and paste this entire block:

```powershell
# Install dependencies
py -m pip install rich sqlalchemy psycopg2-binary python-dotenv openai

# Run database check
py check_database.py
```

---

## Alternative: Check Database Directly

If the script still doesn't work, use Docker directly:

```powershell
# Connect to database
docker exec -it sales-crm-db psql -U postgres -d sales_crm

# Run SQL
SELECT * FROM tenants;
SELECT * FROM leads;
SELECT status, COUNT(*) FROM leads GROUP BY status;

# Exit
\q
```

---

## Summary

**Working command to install:**
```powershell
py -m pip install rich sqlalchemy psycopg2-binary python-dotenv openai
```

**Working command to check database:**
```powershell
py check_database.py
```

**That's it!** 🎉


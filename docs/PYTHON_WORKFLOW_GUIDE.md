# Python Environment Workflow Guide

## ❓ Where Should You Work?

### ✅ **CORRECT: Work OUTSIDE the virtual environment for Poetry commands**

```powershell
# In the project directory, WITHOUT activating .venv
PS C:\Users\Alex\Workspaces\env_guard> poetry install
PS C:\Users\Alex\Workspaces\env_guard> poetry update proof-tracker
PS C:\Users\Alex\Workspaces\env_guard> poetry show proof-tracker
PS C:\Users\Alex\Workspaces\env_guard> poetry run pytest
```

### ❌ **WRONG: Don't activate .venv for Poetry**

```powershell
# This is WRONG - causes the Poetry error you saw
(.venv) PS C:\Users\Alex\Workspaces\env_guard> poetry show proof-tracker
# ERROR: ModuleNotFoundError: No module named 'poetry.console'
```

## 🔧 Workflow Rules

### For Poetry Commands (dependency management)
```powershell
# Always work WITHOUT .venv activated
PS C:\Users\Alex\Workspaces\env_guard> poetry <command>
```

### For Running Python Code (testing, scripts)
```powershell
# Option 1: Use poetry run (recommended)
PS C:\Users\Alex\Workspaces\env_guard> poetry run py script.py
PS C:\Users\Alex\Workspaces\env_guard> poetry run pytest

# Option 2: Activate .venv
PS C:\Users\Alex\Workspaces\env_guard> .venv\Scripts\Activate.ps1
(.venv) PS C:\Users\Alex\Workspaces\env_guard> py script.py
(.venv) PS C:\Users\Alex\Workspaces\env_guard> pytest
```

## 🐛 Why the Poetry Error Happens

When you activate `.venv`, PowerShell finds `poetry.exe` inside `.venv\Scripts\`, but this is just a **stub/entry point** that expects the actual Poetry modules to be installed in the virtual environment. They're not there because Poetry should be installed globally, not in your project's venv.

## 📋 Common Tasks

### Install dependencies
```powershell
poetry install --extras telemetry
```

### Update a specific package
```powershell
poetry update proof-tracker
```

### Check package version
```powershell
poetry show proof-tracker
```

### Run tests
```powershell
poetry run pytest
# OR
poetry run py test_supabase_live.py
```

### Run the CLI tool
```powershell
poetry run env-guard check
```

### Activate venv manually (if needed)
```powershell
# Only for running Python code, NOT for Poetry commands
.venv\Scripts\Activate.ps1
```

### Deactivate venv
```powershell
deactivate
```

## 🎯 Quick Fix for Your Current Situation

If you see the Poetry error:
```powershell
# 1. Deactivate if you're in .venv
(.venv) PS> deactivate

# 2. Now run Poetry commands
PS> poetry show proof-tracker
PS> poetry update proof-tracker
```

## 📦 Package Management Summary

| Task | Command | Environment |
|------|---------|-------------|
| Add package | `poetry add package-name` | **Outside .venv** |
| Remove package | `poetry remove package-name` | **Outside .venv** |
| Update package | `poetry update package-name` | **Outside .venv** |
| Show package | `poetry show package-name` | **Outside .venv** |
| Install all deps | `poetry install` | **Outside .venv** |
| Run Python code | `poetry run py script.py` | **Outside .venv** |
| Run tests | `poetry run pytest` | **Outside .venv** |
| Use Python manually | `py script.py` | **Inside .venv** (after activating) |


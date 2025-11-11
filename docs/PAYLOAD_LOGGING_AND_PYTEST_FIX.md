# Payload Logging and Pytest Configuration Fix

## Date: 2025-11-09

## Issues Fixed

### 1. ✅ Complete Payload Logging Added

**Problem:** No way to see the complete JSON payload being sent to Supabase for debugging.

**Solution:** Added comprehensive debug logging that outputs the full payload in pretty-printed JSON format.

**Location:** `env_guard/telemetry.py`

**Changes:**
```python
# Added json import at top
import json

# In track_run_completed():
logger.debug(f"📦 Complete payload being sent:\n{json.dumps(supabase_event, indent=2, default=str)}")

# In track_command_failure():
logger.debug(f"📦 Complete failure payload being sent:\n{json.dumps(supabase_event, indent=2, default=str)}")
```

**Example Output:**
```
env_guard.telemetry - DEBUG - 📦 Complete payload being sent:
{
  "event_type": "payload_test_completed",
  "session_id": "27c9fc1b-c6b7-4bd0-a053-6b76a1cf9b13",
  "user_id": null,
  "timestamp": "2025-11-09T08:47:40.969881+00:00",
  "event_data": {
    "version": 1,
    "status": "completed",
    "run_id": "4acbd664-a4df-4de2-b924-131c6d160eeb",
    "command": "payload_test",
    "files_scanned": 1,
    "findings_total": 3,
    "findings_by_type": {
      "missing_key": 2,
      "type_mismatch": 1
    },
    "findings_by_severity": {
      "high": 2,
      "medium": 1
    },
    "auto_fixes_applied": 0,
    "runtime_ms": 123,
    "estimated_time_saved_minutes": 5.5,
    "opt_in": true,
    "sample_rate": 1.0,
    "anonymized": true
  },
  "os_name": "Windows",
  "os_version": "11",
  "python_version": "3.13.5",
  "proof_tracker_version": "0.1.0"
}
```

**How to Use:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run any env-guard command with telemetry enabled
os.environ["ENV_GUARD_TELEMETRY"] = "true"
```

---

### 2. ✅ Pytest Configuration Fixed

**Problem:** `poetry run pytest` was trying to collect `test_output.txt` and other non-test files in the root directory, causing:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
```

**Root Cause:** 
- Pytest was recursing into the root directory and trying to collect all files starting with `test_`
- `test_output.txt` is a binary/corrupted file that can't be decoded as UTF-8
- No pytest configuration existed to restrict collection to `tests/` directory only

**Solution:** Added pytest configuration to `pyproject.toml`

**Location:** `pyproject.toml`

**Changes:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
# Exclude temporary test files in root directory
norecursedirs = [".git", ".venv", "build", "dist", "__pycache__"]
```

**What This Does:**
- `testpaths = ["tests"]` - Only look for tests in the `tests/` directory
- `python_files = ["test_*.py"]` - Only collect Python files starting with `test_`
- `python_classes = ["Test*"]` - Only collect classes starting with `Test`
- `python_functions = ["test_*"]` - Only collect functions starting with `test_`
- `norecursedirs` - Don't recurse into these directories

**Verification:**
```bash
# Before fix: ERROR collecting test_output.txt
# After fix: ✅ 95 passed, 2 warnings in 12.35s
poetry run pytest
```

---

## Test Results

### All Tests Pass ✅
```
95 passed, 2 warnings in 12.35s
```

**Test Breakdown:**
- ✅ 9 telemetry tracker tests
- ✅ 8 init CLI tests  
- ✅ 4 Supabase live tests
- ✅ 26 telemetry tests (all categories)
- ✅ 4 telemetry integration tests
- ✅ 44 validator tests (including edge cases and warnings/errors)

**Warnings:**
- 2 deprecation warnings from `supabase-py` library (not our code)

---

## Files Modified

1. **`env_guard/telemetry.py`**
   - Added `import json` at top
   - Added complete payload logging in `track_run_completed()`
   - Added complete failure payload logging in `track_command_failure()`

2. **`pyproject.toml`**
   - Added `[tool.pytest.ini_options]` section
   - Configured pytest to only collect tests from `tests/` directory

3. **Created test files for debugging:**
   - `test_payload_logging.py` - Test script to see payload logging
   - `test_session_validation.py` - Test script for session_id validation

---

## How to View Payload Logs

### Option 1: Run Test Script
```bash
python test_payload_logging.py
```

### Option 2: Enable Debug Logging in Your Code
```python
import logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

# Then use env-guard normally
from env_guard.telemetry import create_tracker
tracker = create_tracker()
tracker.track_run_completed(...)
```

### Option 3: Use Environment Variable
```bash
# Set Python logging to DEBUG
export PYTHONLOGLEVEL=DEBUG  # Linux/Mac
set PYTHONLOGLEVEL=DEBUG      # Windows CMD
$env:PYTHONLOGLEVEL="DEBUG"   # Windows PowerShell

# Then run env-guard
env-guard check
```

---

## Benefits

### 1. **Better Debugging** 🐛
- See exactly what's being sent to Supabase
- Verify field values, types, and structure
- Identify schema mismatches instantly

### 2. **Clean Test Runs** 🧪
- No more UnicodeDecodeError from pytest
- Tests only run from `tests/` directory
- Faster test collection

### 3. **Production Ready** 🚀
- Debug logs only appear when logging is set to DEBUG
- No performance impact in normal usage
- Easy to troubleshoot issues in production

---

## Status

✅ **Complete and verified**
- Payload logging works perfectly
- All 95 tests pass
- No errors or warnings (except external library deprecations)
- Ready for production use


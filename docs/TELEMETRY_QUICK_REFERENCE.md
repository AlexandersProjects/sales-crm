# Telemetry Quick Reference

## Quick Start

### Enable Telemetry (File-Only)

```powershell
# Windows PowerShell
$env:ENV_GUARD_TELEMETRY="true"
```

```bash
# Linux/Mac
export ENV_GUARD_TELEMETRY=true
```

That's it! Telemetry logs to: `~/.env_guard_telemetry/env_guard_tracking.json`

### Enable Supabase (Dual-Backend)

```powershell
# Windows PowerShell
$env:ENV_GUARD_TELEMETRY="true"
$env:SUPABASE_URL="https://your-project.supabase.co"
$env:SUPABASE_KEY="your-key"
```

```bash
# Linux/Mac
export ENV_GUARD_TELEMETRY=true
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-key"
```

Now logs to BOTH local file AND Supabase!

## Commands

```powershell
# Run with telemetry
env-guard check

# Disable for one command
env-guard check --no-telemetry

# Test telemetry integration
py test_telemetry_integration.py

# Run tests
pytest tests/test_telemetry.py tests/test_telemetry_integration.py -v
```

## What Gets Tracked?

✅ **Tracked (Anonymous)**
- Command names (`check`, `suggest`, `init`)
- Aggregate counts (files scanned, findings)
- Error types
- Performance metrics (runtime)

❌ **Never Tracked**
- File paths or names
- Environment variable names or values
- User identifiers
- Project information

## Architecture

```
proof_tracker 0.4.0
├── File Backend (always enabled)
│   └── ~/.env_guard_telemetry/env_guard_tracking.json
│
└── Supabase Backend (optional)
    └── Requires SUPABASE_URL + SUPABASE_KEY
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Telemetry not enabled | Set `ENV_GUARD_TELEMETRY=true` |
| No proof_tracker | `pip install -e .[telemetry]` |
| Supabase not working | Verify both URL and KEY are set |
| File not created | Check `~/.env_guard_telemetry/` permissions |

## Code Example

```python
from env_guard.telemetry import create_tracker

# Create tracker (automatically configures backends)
tracker = create_tracker()

# Track success
tracker.track_run_completed(
    command="check",
    files_scanned=5,
    findings_total=10,
    findings_by_type={"missing_key": 5},
    findings_by_severity={"high": 3},
    auto_fixes_applied=2,
    runtime_ms=500,
)

# Track failure
tracker.track_command_failure(
    command="check",
    error_type="FileNotFoundError",
    error_message="File not found"
)
```

## Files

| File | Purpose |
|------|---------|
| `env_guard/telemetry.py` | Core implementation |
| `tests/test_telemetry.py` | Unit tests (26 tests) |
| `tests/test_telemetry_integration.py` | Integration tests (12 tests) |
| `docs/TELEMETRY_INTEGRATION.md` | Complete guide |
| `docs/PROOF_TRACKER_0.4.0_MIGRATION.md` | Migration summary |

## Dependencies

```toml
[project.optional-dependencies]
telemetry = [
    "proof_tracker>=0.4.0",
    "python-dotenv>=1.2.1",
    "supabase>=2.0.0",
]
```

Install: `pip install -e .[telemetry]`

## Key Features

1. **Dual-Backend** - File + Supabase simultaneously
2. **Graceful Fallback** - File-only if Supabase unavailable
3. **Privacy-First** - Opt-in, anonymous, local-first
4. **Never Crashes** - Telemetry failures don't affect app
5. **Well-Tested** - 38 test cases

## See Also

- 📖 [Complete Integration Guide](./TELEMETRY_INTEGRATION.md)
- 🚀 [Migration Summary](./PROOF_TRACKER_0.4.0_MIGRATION.md)
- 🧪 [Testing Guide](../TELEMETRY_TESTING_GUIDE.md)
- ⚡ [Quick Start](../TELEMETRY_QUICKSTART.md)


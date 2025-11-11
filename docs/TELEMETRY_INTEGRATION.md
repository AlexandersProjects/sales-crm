# Telemetry Integration with proof_tracker 0.4.0

## Overview

env_guard integrates with [proof_tracker](https://github.com/AlexandersProjects/proof_tracker) version 0.4.0 to provide anonymous telemetry tracking. The integration supports **dual-backend logging**:

1. **Local File Logging** (always enabled when telemetry is on)
2. **Supabase Telemetry** (optional, requires credentials)

## Architecture

### Dual-Backend Design

The telemetry system uses proof_tracker's 0.4.0 API which supports simultaneous logging to multiple backends:

```python
# File-only backend (default)
tracker = ProofTracker(
    telemetry_backend=["file"],
    file_path="~/.env_guard_telemetry/env_guard_tracking.json"
)

# Dual backend (file + Supabase)
tracker = ProofTracker(
    telemetry_backend=["file", "supabase"],
    file_path="~/.env_guard_telemetry/env_guard_tracking.json"
)
```

### Backend Selection Logic

The backend configuration is determined automatically:

- **File backend** is ALWAYS used when telemetry is enabled
- **Supabase backend** is added when BOTH credentials are present:
  - `SUPABASE_URL` environment variable
  - `SUPABASE_KEY` environment variable

## Configuration

### Enabling Telemetry

Telemetry is **opt-in** by default. To enable:

```bash
export ENV_GUARD_TELEMETRY=true
```

Accepted values: `1`, `true`, `yes`, `on`, `enabled`

### Local File Logging

When telemetry is enabled, events are always logged to:

```
~/.env_guard_telemetry/env_guard_tracking.json
```

No additional configuration is required.

### Supabase Integration (Optional)

To enable Supabase telemetry, set these environment variables:

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-or-service-key"
```

**Important:** Both must be set for Supabase to be enabled. If only one is set, telemetry will fall back to file-only mode.

## Usage in Code

### TelemetryTracker Class

The `TelemetryTracker` class handles all telemetry operations:

```python
from env_guard.telemetry import create_tracker

# Create a tracker instance
tracker = create_tracker()

# Track a successful run
tracker.track_run_completed(
    command="check",
    files_scanned=5,
    findings_total=10,
    findings_by_type={"missing_key": 5, "type_mismatch": 5},
    findings_by_severity={"high": 3, "medium": 7},
    auto_fixes_applied=2,
    runtime_ms=500,
    estimated_time_saved_minutes=15.0,
)

# Track a command failure
tracker.track_command_failure(
    command="check",
    error_type="FileNotFoundError",
    error_message="File not found: .env"
)
```

### Integration with proof_tracker API

The tracker uses proof_tracker's 0.4.0 methods:

#### `log_proof(data: dict)`

Used for both success and failure events:

```python
# Success event
tracker.tracker.log_proof({
    "action": "check_command",
    "status": "completed",
    "details": {
        "files_scanned": 5,
        "findings_total": 10,
        # ... more details
    }
})

# Failure event
tracker.tracker.log_proof({
    "action": "check_command",
    "status": "failed",
    "error_type": "FileNotFoundError",
    "error_message": "File not found"
})
```

#### `register_event(event_name: str, count: int)`

Used for tracking metrics:

```python
tracker.tracker.register_event("check_runs", 1)
tracker.tracker.register_event("total_findings", 10)
tracker.tracker.register_event("auto_fixes_applied", 2)
```

## Data Format

### Event Structure

All telemetry events follow this structure:

```json
{
    "version": 1,
    "event": "run.completed",
    "timestamp": "2025-11-06T12:34:56.789Z",
    "run_id": "uuid-here",
    "command": "check",
    "files_scanned": 5,
    "findings_total": 10,
    "findings_by_type": {
        "missing_key": 5,
        "type_mismatch": 3,
        "pattern_mismatch": 2
    },
    "findings_by_severity": {
        "critical": 1,
        "high": 3,
        "medium": 4,
        "low": 2
    },
    "auto_fixes_applied": 2,
    "runtime_ms": 500,
    "estimated_time_saved_minutes": 15.0,
    "opt_in": true,
    "sample_rate": 1.0,
    "anonymized": true
}
```

### Privacy

All telemetry data is **anonymized**:

- ✅ Command names (e.g., "check", "suggest", "init")
- ✅ Aggregate counts (files scanned, findings)
- ✅ Error types (e.g., "FileNotFoundError")
- ✅ Performance metrics (runtime)

**Never included:**

- ❌ File paths or names
- ❌ Environment variable names or values
- ❌ User identifiers
- ❌ Project names or paths

## Testing

### Unit Tests

Run the unit tests to verify the telemetry module:

```bash
pytest tests/test_telemetry.py -v
```

### Integration Tests

Run the integration tests to verify proof_tracker interaction:

```bash
pytest tests/test_telemetry_integration.py -v
```

### Manual Testing

Use the test script to verify end-to-end functionality:

```bash
# Enable telemetry
export ENV_GUARD_TELEMETRY=true

# Optional: Add Supabase credentials
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-key"

# Run the test script
python test_telemetry_integration.py
```

This will:
1. Verify telemetry initialization
2. Send test events
3. Confirm backend configuration

## Troubleshooting

### Telemetry Not Enabled

**Symptom:** `Tracker enabled: False`

**Solutions:**
1. Set `ENV_GUARD_TELEMETRY=true`
2. Install telemetry dependencies: `pip install -e .[telemetry]`
3. Verify proof_tracker is installed: `python -c "import proof_tracker"`

### Supabase Not Working

**Symptom:** Events logged to file but not appearing in Supabase

**Solutions:**
1. Verify both `SUPABASE_URL` and `SUPABASE_KEY` are set
2. Check the credentials are correct
3. Ensure the Supabase table exists and is accessible
4. Review logs for Supabase-specific errors

### File Logging Not Working

**Symptom:** No local tracking file created

**Solutions:**
1. Check write permissions for `~/.env_guard_telemetry/`
2. Verify disk space is available
3. Review logs for file system errors

## Error Handling

The telemetry system is designed to **fail gracefully**:

- ❌ Telemetry failures NEVER crash the main application
- ✅ Errors are logged at DEBUG level
- ✅ Users can disable telemetry with `--no-telemetry` flag

Example from CLI:

```python
try:
    tracker.track_run_completed(...)
except Exception as e:
    logger.debug(f"Failed to send telemetry: {e}")
    # Application continues normally
```

## Development

### Adding New Events

To track new events:

1. Define the event structure in `telemetry.py`
2. Add a tracking method if needed
3. Call the tracking method from the CLI
4. Add tests for the new event

Example:

```python
def track_custom_event(self, event_type: str, details: dict):
    """Track a custom event."""
    if not self.enabled or self.tracker is None:
        return
    
    try:
        self.tracker.log_proof({
            "action": f"custom_{event_type}",
            "status": "completed",
            "details": details
        })
    except Exception as e:
        logger.debug(f"Failed to track custom event: {e}")
```

### Updating proof_tracker

To update to a new version of proof_tracker:

1. Update `pyproject.toml` dependency version
2. Review proof_tracker changelog for API changes
3. Update `telemetry.py` if API changed
4. Update tests to match new behavior
5. Run full test suite

## Dependencies

Required for telemetry:

```toml
[project.optional-dependencies]
telemetry = [
    "proof_tracker>=0.4.0",
    "python-dotenv>=1.2.1",
    "supabase>=2.0.0",
]
```

Install with:

```bash
pip install -e .[telemetry]
```

## See Also

- [proof_tracker documentation](https://github.com/AlexandersProjects/proof_tracker)
- [TELEMETRY_QUICKSTART.md](../TELEMETRY_QUICKSTART.md)
- [TELEMETRY_TESTING_GUIDE.md](../TELEMETRY_TESTING_GUIDE.md)


"""Quick test to see the complete payload logging."""
import os
import logging

# Set up DEBUG level logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

# Enable telemetry
os.environ["ENV_GUARD_TELEMETRY"] = "true"

# Load .env
from dotenv import load_dotenv
load_dotenv()

print("Creating tracker and sending test event...\n")

from env_guard.telemetry import create_tracker

tracker = create_tracker()

if tracker.enabled:
    print("Sending test event (check DEBUG logs below)...\n")
    tracker.track_run_completed(
        command="payload_test",
        files_scanned=1,
        findings_total=3,
        findings_by_type={"missing_key": 2, "type_mismatch": 1},
        findings_by_severity={"high": 2, "medium": 1},
        auto_fixes_applied=0,
        runtime_ms=123,
        estimated_time_saved_minutes=5.5,
    )
    print("\n\nCheck the '📦 Complete payload being sent' log above!")
else:
    print("Telemetry not enabled")


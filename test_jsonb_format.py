"""
Test to verify if event_data is sent as JSON object or string to Supabase.
"""
import os
import json
import logging

# Enable DEBUG logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

# Enable telemetry
os.environ["ENV_GUARD_TELEMETRY"] = "true"

# Load .env
from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("TESTING: event_data JSONB vs STRING")
print("=" * 70)
print()

from env_guard.telemetry import create_tracker

tracker = create_tracker()

if tracker.enabled:
    print("Sending test event with complex event_data...")
    print()

    # Create test data with nested structure
    test_event_data = {
        "version": 1,
        "test": "jsonb_check",
        "nested": {
            "level1": {
                "level2": "deep_value"
            }
        },
        "array": [1, 2, 3],
        "boolean": True,
        "null_value": None
    }

    print(f"Test data (Python dict):")
    print(json.dumps(test_event_data, indent=2))
    print()

    try:
        tracker.track_run_completed(
            command="jsonb_test",
            files_scanned=1,
            findings_total=0,
            findings_by_type={},
            findings_by_severity={},
            auto_fixes_applied=0,
            runtime_ms=10,
            estimated_time_saved_minutes=0.0,
        )

        print()
        print("✅ Event sent!")
        print()
        print("Check the '📦 Complete payload being sent' log above.")
        print("Look at how 'event_data' is formatted - is it:")
        print("  1. A dict/object (good for JSONB)")
        print("  2. A string (bad for JSONB)")
        print()
        print("Then check your Supabase table to see how it's stored.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Telemetry not enabled")

print()
print("=" * 70)


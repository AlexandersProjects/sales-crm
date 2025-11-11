"""Test script to verify session_id validation with debug logging."""

import os
import logging

# Set up logging to see debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

# Enable telemetry
os.environ["ENV_GUARD_TELEMETRY"] = "true"

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file\n")
except ImportError:
    print("⚠ python-dotenv not installed\n")

from env_guard.telemetry import create_tracker

print("=" * 70)
print("SESSION_ID VALIDATION TEST")
print("=" * 70)
print()

# Create tracker - this will load/generate session_id
print("Creating telemetry tracker...")
print()
tracker = create_tracker()

print()
print(f"Tracker Status:")
print(f"  - Enabled: {tracker.enabled}")
print(f"  - Session ID: {tracker.session_id}")
print(f"  - Run ID: {tracker.run_id}")
print()

if tracker.enabled:
    print("Sending test event with validated session_id...")
    print()
    
    try:
        tracker.track_run_completed(
            command="session_validation_test",
            files_scanned=1,
            findings_total=0,
            findings_by_type={},
            findings_by_severity={},
            auto_fixes_applied=0,
            runtime_ms=50,
            estimated_time_saved_minutes=0.0,
        )
        
        print("✅ Event sent successfully!")
        print()
        print("Check the logs above - you should see:")
        print("  ✅ Loaded valid session_id from file: [UUID]")
        print("  ✅ session_id is valid UUID: [UUID]")
        print("  📤 Sending event to Supabase: event_type=session_validation_test_completed")
        print()
        
    except Exception as e:
        print(f"❌ Error sending event: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Telemetry not enabled")

print()
print("=" * 70)
print("Test complete!")
print("=" * 70)


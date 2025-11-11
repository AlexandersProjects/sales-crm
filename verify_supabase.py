"""Verify that env_guard telemetry is reaching Supabase correctly."""

import os
import sys

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file")
except ImportError:
    print("⚠ python-dotenv not installed")

# Set environment variable explicitly just in case
os.environ["ENV_GUARD_TELEMETRY"] = "true"

print(f"ENV_GUARD_TELEMETRY = {os.getenv('ENV_GUARD_TELEMETRY')}")
print()

from env_guard.telemetry import create_tracker

print("=" * 70)
print("SUPABASE TELEMETRY VERIFICATION TEST")
print("=" * 70)
print()

# Create tracker
tracker = create_tracker()

print(f"Tracker Status:")
print(f"  - Enabled: {tracker.enabled}")
print(f"  - Session ID: {tracker.session_id}")
print(f"  - Run ID: {tracker.run_id}")
print()

if not tracker.enabled:
    print("❌ Telemetry is NOT enabled!")
    print()
    print("Please ensure:")
    print("  1. ENV_GUARD_TELEMETRY=true is set")
    print("  2. proof_tracker is installed")
    sys.exit(1)

print(f"Environment Metadata:")
for key, value in tracker.env_metadata.items():
    print(f"  - {key}: {value}")
print()

print("Sending test event to Supabase...")
print()

try:
    # Send a test event
    tracker.track_run_completed(
        command="verify_test",
        files_scanned=1,
        findings_total=3,
        findings_by_type={
            "missing_key": 1,
            "type_mismatch": 1,
            "pattern_mismatch": 1,
        },
        findings_by_severity={
            "critical": 0,
            "high": 1,
            "medium": 1,
            "low": 1,
        },
        auto_fixes_applied=0,
        runtime_ms=100,
        estimated_time_saved_minutes=6.0,
    )
    
    print("✅ Event sent successfully!")
    print()
    print("Expected in Supabase:")
    print("  - event_type: 'verify_test_completed'")
    print(f"  - session_id: {tracker.session_id}")
    print(f"  - user_id: NULL (anonymous)")
    print("  - timestamp: (current time)")
    print("  - event_data: JSON with all details")
    print(f"  - os_name: {tracker.env_metadata['os_name']}")
    print(f"  - os_version: {tracker.env_metadata['os_version']}")
    print(f"  - python_version: {tracker.env_metadata['python_version']}")
    print(f"  - proof_tracker_version: {tracker.env_metadata['proof_tracker_version']}")
    print()
    
except Exception as e:
    print(f"❌ Error sending telemetry: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Sending a failure event...")
print()

try:
    tracker.track_command_failure(
        command="verify_test",
        error_type="TestError",
        error_message="This is a test failure event - not a real error"
    )
    
    print("✅ Failure event sent successfully!")
    print()
    print("Expected in Supabase:")
    print("  - event_type: 'verify_test_failed'")
    print(f"  - session_id: {tracker.session_id}")
    print("  - event_data: JSON with error details")
    print()
    
except Exception as e:
    print(f"❌ Error sending failure telemetry: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print()
print("Now check your Supabase dashboard:")
print("  1. Go to: https://supabase.com/dashboard")
print("  2. Select your project")
print("  3. Go to 'Table Editor'")
print("  4. Select 'telemetry_events' table")
print("  5. Look for events with:")
print(f"     - session_id: {tracker.session_id}")
print("     - event_type: 'verify_test_completed' or 'verify_test_failed'")
print()
print("If you see these events, env_guard telemetry is working! 🎉")


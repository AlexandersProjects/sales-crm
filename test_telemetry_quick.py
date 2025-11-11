"""Quick test of updated telemetry with Supabase schema compatibility."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[INFO] Loaded .env file")
except ImportError:
    print("[WARNING] python-dotenv not installed, using system environment variables only")

from env_guard.telemetry import create_tracker

print("=" * 70)
print("QUICK TELEMETRY TEST - Supabase Schema Compatibility")
print("=" * 70)
print()

# Show current env var value
env_telemetry = os.getenv("ENV_GUARD_TELEMETRY", "not set")
print(f"ENV_GUARD_TELEMETRY = {env_telemetry}")
print()

# Create tracker
print("Creating telemetry tracker...")
tracker = create_tracker()

print(f"✓ Tracker created")
print(f"  - Enabled: {tracker.enabled}")
print(f"  - Session ID: {tracker.session_id}")
print(f"  - Run ID: {tracker.run_id}")
print(f"  - Environment metadata: {tracker.env_metadata}")
print()

if tracker.enabled:
    print("Sending test event with Supabase-compatible format...")
    try:
        tracker.track_run_completed(
            command="test",
            files_scanned=1,
            findings_total=5,
            findings_by_type={
                "missing_key": 2,
                "type_mismatch": 2,
                "pattern_mismatch": 1,
            },
            findings_by_severity={
                "critical": 0,
                "high": 2,
                "medium": 2,
                "low": 1,
            },
            auto_fixes_applied=1,
            runtime_ms=420,
            estimated_time_saved_minutes=12.5,
            sample_rate=1.0,
        )
        print("✓ Event sent successfully!")
        print()
        print("Event format should now include:")
        print("  - event_type: 'test_completed'")
        print("  - session_id: UUID")
        print("  - timestamp: ISO format")
        print("  - event_data: JSONB with all details")
        print("  - os_name, os_version, python_version, proof_tracker_version")
        print()
        print("Check Supabase to see if the event was accepted!")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠ Telemetry not enabled (ENV_GUARD_TELEMETRY not set to true)")

print()
print("=" * 70)
print("Test complete!")
print("=" * 70)


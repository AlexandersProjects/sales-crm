"""
Simple direct test of telemetry with explicit output.
"""
import os

# Set environment variable explicitly
os.environ["ENV_GUARD_TELEMETRY"] = "true"

print("=" * 70)
print("DIRECT TELEMETRY TEST")
print("=" * 70)

# Load dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

print(f"\nENV_GUARD_TELEMETRY = {os.getenv('ENV_GUARD_TELEMETRY')}\n")

from env_guard.telemetry import create_tracker

tracker = create_tracker()

print(f"Tracker enabled: {tracker.enabled}")
print(f"Session ID: {tracker.session_id}")
print(f"Environment: {tracker.env_metadata}")
print()

if tracker.enabled:
    print("Sending test event...")
    try:
        tracker.track_run_completed(
            command="direct_test",
            files_scanned=1,
            findings_total=2,
            findings_by_type={"missing_key": 1, "type_mismatch": 1},
            findings_by_severity={"high": 1, "medium": 1},
            auto_fixes_applied=0,
            runtime_ms=50,
            estimated_time_saved_minutes=4.0,
        )
        print("✅ Event sent!")
        print()
        print("Check Supabase for:")
        print(f"  - event_type: 'direct_test_completed'")
        print(f"  - session_id: {tracker.session_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Telemetry NOT enabled")

print()
print("=" * 70)


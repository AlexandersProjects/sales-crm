"""
Live Supabase Integration Test

This test actually sends data to Supabase to verify the dual-backend system works.
It requires:
- ENV_GUARD_TELEMETRY=true
- SUPABASE_URL set
- SUPABASE_KEY set

Run with: py test_supabase_live.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except Exception as e:
    print(f"⚠️  Could not load .env: {e}")

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

from env_guard.telemetry import create_tracker


def print_header(title):
    """Print a nice header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_environment():
    """Check if the environment is properly configured."""
    print_header("ENVIRONMENT CHECK")

    telemetry = os.getenv("ENV_GUARD_TELEMETRY")

    print(f"ENV_GUARD_TELEMETRY: {telemetry}")
    print(f"proof_tracker version: 0.4.2+ (with hardcoded Supabase credentials)")

    if telemetry not in ['true', '1', 'yes', 'on', 'enabled']:
        print("\n❌ ERROR: ENV_GUARD_TELEMETRY is not enabled!")
        print("   Set: ENV_GUARD_TELEMETRY=true")
        return False

    print("\n✅ Environment configured correctly")
    print("   Note: Supabase credentials are hardcoded in proof_tracker 0.4.2+")
    return True


def test_tracker_initialization():
    """Test that the tracker initializes with dual backends."""
    print_header("TEST 1: Tracker Initialization")

    tracker = create_tracker()

    print(f"Tracker enabled: {tracker.enabled}")
    print(f"Run ID: {tracker.run_id}")
    print(f"Tracker instance: {tracker.tracker}")

    # If tracker.tracker exists, telemetry is enabled (they're linked)
    assert tracker.tracker is not None, "ProofTracker instance not created"

    print("\n✅ PASSED: Tracker initialized successfully")


def test_send_success_event():
    """Test sending a success event to Supabase."""
    print_header("TEST 2: Send Success Event to Supabase")

    tracker = create_tracker()

    if not tracker.enabled:
        print("⚠️  SKIPPED: Tracker not enabled")
        import pytest
        pytest.skip("Tracker not enabled")

    print("Sending success event...")
    tracker.track_run_completed(
        command="test_live",
        files_scanned=5,
        findings_total=10,
        findings_by_type={
            "missing_key": 5,
            "type_mismatch": 3,
            "pattern_mismatch": 2,
        },
        findings_by_severity={
            "critical": 1,
            "high": 3,
            "medium": 4,
            "low": 2,
        },
        auto_fixes_applied=2,
        runtime_ms=500,
        estimated_time_saved_minutes=15.0,
        sample_rate=1.0,
    )

    print("✅ Event sent!")
    print("\n📊 What to check in Supabase:")
    print("   1. Go to your Supabase project dashboard")
    print("   2. Navigate to Table Editor")
    print("   3. Look for tables created by proof_tracker:")
    print("      - 'proofs' or 'proof_logs' table")
    print("      - 'events' or 'telemetry_events' table")
    print("   4. You should see a new row with:")
    print(f"      - action: 'check_command'")
    print(f"      - status: 'completed'")
    print(f"      - command: 'test_live'")
    print(f"      - findings_total: 10")
    print(f"      - run_id: {tracker.run_id}")



def test_send_failure_event():
    """Test sending a failure event to Supabase."""
    print_header("TEST 3: Send Failure Event to Supabase")

    tracker = create_tracker()

    if not tracker.enabled:
        print("⚠️  SKIPPED: Tracker not enabled")
        import pytest
        pytest.skip("Tracker not enabled")

    print("Sending failure event...")
    tracker.track_command_failure(
        command="test_live",
        error_type="TestError",
        error_message="This is a test error - not a real failure"
    )

    print("✅ Event sent!")
    print("\n📊 Check Supabase for:")
    print("   - action: 'test_live_command'")
    print("   - status: 'failed'")
    print("   - error_type: 'TestError'")



def test_check_local_file():
    """Check if local file logging is working."""
    print_header("TEST 4: Verify Local File Logging")

    try:
        import os.path

        # Check for local tracking file
        home = os.path.expanduser("~")
        file_path = os.path.join(home, ".env_guard_telemetry", "env_guard_tracking.json")

        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ Local file exists: {file_path}")
            print(f"   Size: {size} bytes")

            # Show last few lines
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    print(f"   Total events: {len(lines)}")

                    if lines:
                        print("\n   Last event:")
                        import json
                        last_event = json.loads(lines[-1])
                        print(f"      Action: {last_event.get('action')}")
                        print(f"      Status: {last_event.get('status')}")
                        print(f"      Timestamp: {last_event.get('timestamp')}")
            except Exception as e:
                print(f"   Could not read file content: {e}")
        else:
            print(f"❌ Local file not found: {file_path}")
            assert False, "This might indicate file logging is not working"

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  LIVE SUPABASE INTEGRATION TEST")
    print("  proof_tracker 0.4.2 - Dual Backend (File + Supabase)")
    print("  Supabase credentials: Hardcoded in proof_tracker")
    print("=" * 70)

    # Check environment
    if not check_environment():
        print("\n❌ Environment not configured - tests cannot run")
        sys.exit(1)

    # Run tests and track results
    print_header("TEST SUMMARY")
    failed = 0

    # Test 1
    try:
        test_tracker_initialization()
        print("✅ PASSED: Tracker Initialization")
    except (AssertionError, Exception) as e:
        print(f"❌ FAILED: Tracker Initialization - {e}")
        failed += 1

    # Test 2
    try:
        test_send_success_event()
        print("✅ PASSED: Send Success Event")
    except (AssertionError, Exception) as e:
        print(f"❌ FAILED: Send Success Event - {e}")
        failed += 1

    # Test 3
    try:
        test_send_failure_event()
        print("✅ PASSED: Send Failure Event")
    except (AssertionError, Exception) as e:
        print(f"❌ FAILED: Send Failure Event - {e}")
        failed += 1

    # Test 4
    try:
        test_check_local_file()
        print("✅ PASSED: Local File Logging")
    except (AssertionError, Exception) as e:
        print(f"❌ FAILED: Local File Logging - {e}")
        failed += 1

    total = 4
    passed = total - failed
    print(f"\nResults: {passed}/{total} tests passed")

    if failed == 0:
        print("\n🎉 All tests passed!")
        print("\n📋 Next Steps:")
        print("   1. Check your Supabase dashboard")
        print("   2. Verify events appear in the database")
        print("   3. Check the local file for backup logs")
    else:
        print("\n⚠️  Some tests failed")
        print("   Check the error messages above for details")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()


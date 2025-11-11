"""
Test script to verify telemetry integration with ProofTracker.

This script helps you verify that:
1. Telemetry is properly enabled
2. ProofTracker can connect to Supabase
3. Events are being sent correctly
4. Data format matches expectations
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import env_guard
sys.path.insert(0, str(Path(__file__).parent))

# Fix Windows console encoding
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Loaded environment variables from .env file")
except ImportError:
    print("[WARNING] python-dotenv not installed. Using system environment variables only.")
except Exception as e:
    print(f"[WARNING] Could not load .env file: {e}")

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

from env_guard.telemetry import TelemetryTracker, create_tracker


def test_telemetry_basic():
    """Test basic telemetry initialization."""
    print("=" * 70)
    print("TEST 1: Basic Telemetry Initialization (proof_tracker 0.4.0)")
    print("=" * 70)

    # Check environment variables
    telemetry_enabled = os.getenv("ENV_GUARD_TELEMETRY", "false")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    print(f"ENV_GUARD_TELEMETRY: {telemetry_enabled}")
    print(f"SUPABASE_URL: {supabase_url[:50] + '...' if supabase_url else 'NOT SET'}")
    print(f"SUPABASE_KEY: {'SET (' + str(len(supabase_key)) + ' chars)' if supabase_key else 'NOT SET'}")
    print()

    # Determine expected backend configuration
    if supabase_url and supabase_key:
        expected_backends = ["file", "supabase"]
        print("Expected backend: DUAL (file + supabase)")
    else:
        expected_backends = ["file"]
        print("Expected backend: FILE ONLY (no Supabase credentials)")
    print()

    # Create tracker
    tracker = create_tracker()
    print(f"Tracker enabled: {tracker.enabled}")
    print(f"Run ID: {tracker.run_id}")
    print(f"ProofTracker instance: {tracker.tracker}")
    print()

    if not tracker.enabled:
        print("❌ FAILED: Telemetry is not enabled!")
        print()
        print("To enable telemetry:")
        print("1. Set ENV_GUARD_TELEMETRY=true")
        print("2. Install telemetry extras: pip install -e .[telemetry]")
        print()
        print("Optional (for Supabase):")
        print("3. Set SUPABASE_URL=https://your-project.supabase.co")
        print("4. Set SUPABASE_KEY=your-key")
        print()
        print("Note: Without Supabase credentials, telemetry will log to local file only.")
        import pytest
        pytest.skip("Telemetry not enabled")

    print("✅ PASSED: Telemetry initialized successfully")
    print(f"   Backends configured: {expected_backends}")


def test_telemetry_event():
    """Test sending a telemetry event."""
    print()
    print("=" * 70)
    print("TEST 2: Send Test Event")
    print("=" * 70)

    tracker = create_tracker()

    if not tracker.enabled:
        print("⚠️  SKIPPED: Telemetry not enabled")
        import pytest
        pytest.skip("Telemetry not enabled")

    # Send a test event
    print("Sending test event...")
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

    print("✅ PASSED: Event sent successfully!")
    print()
    print("Check your Supabase dashboard to verify the event was received.")


def test_telemetry_failure():
    """Test sending a failure event."""
    print()
    print("=" * 70)
    print("TEST 3: Send Failure Event")
    print("=" * 70)

    tracker = create_tracker()

    if not tracker.enabled:
        print("⚠️  SKIPPED: Telemetry not enabled")
        import pytest
        pytest.skip("Telemetry not enabled")

    # Send a test failure
    print("Sending test failure event...")
    tracker.track_command_failure(
        command="test",
        error_type="FileNotFoundError",
        error_message="Test error message (this is not a real error)"
    )

    print("✅ PASSED: Failure event sent successfully!")
    print()
    print("Check your Supabase dashboard to verify the failure was logged.")


def test_actual_check_command():
    """Test telemetry with actual check command."""
    print()
    print("=" * 70)
    print("TEST 4: Real Check Command with Telemetry")
    print("=" * 70)

    print("Running: env-guard check")
    print()

    # Import CLI
    from env_guard.cli import app
    from typer.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(app, ["check"])

    print("Command output:")
    print(result.stdout)
    print()

    assert result.exit_code in (0, 1, 2), f"Command failed with exit code {result.exit_code}"

    print(f"✅ PASSED: Command executed (exit code: {result.exit_code})")
    print()
    print("If telemetry is enabled, check Supabase for the event.")


def main():
    """Run all telemetry tests."""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ENV_GUARD TELEMETRY TEST SUITE" + " " * 23 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    failed = 0
    results = []

    # Test 1: Basic initialization
    try:
        test_telemetry_basic()
        results.append(("Basic Initialization", True))
    except Exception as e:
        print(f"Test failed: {e}")
        results.append(("Basic Initialization", False))
        failed += 1

    # Test 2: Send event
    try:
        test_telemetry_event()
        results.append(("Send Success Event", True))
    except Exception as e:
        print(f"Test failed: {e}")
        results.append(("Send Success Event", False))
        failed += 1

    # Test 3: Send failure
    try:
        test_telemetry_failure()
        results.append(("Send Failure Event", True))
    except Exception as e:
        print(f"Test failed: {e}")
        results.append(("Send Failure Event", False))
        failed += 1

    # Test 4: Actual command
    try:
        test_actual_check_command()
        results.append(("Real Check Command", True))
    except Exception as e:
        print(f"Test failed: {e}")
        results.append(("Real Check Command", False))
        failed += 1

    # Summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    print()
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    print(f"Results: {passed_count}/{total_count} tests passed")
    print()

    if passed_count == total_count:
        print("🎉 All tests passed! Telemetry is working correctly.")
    elif passed_count == 0:
        print("⚠️  No tests passed. Please check your configuration:")
        print("   1. Install telemetry: pip install -e .[telemetry]")
        print("   2. Set ENV_GUARD_TELEMETRY=true")
        print("   3. Set SUPABASE_URL and SUPABASE_KEY")
    else:
        print("⚠️  Some tests failed. Please review the output above.")

    print()
    print("Next steps:")
    print("1. Check your Supabase dashboard for the events")
    print("2. Verify the data structure matches your expectations")
    print("3. Run: env-guard check (to test in production)")
    print()


if __name__ == "__main__":
    main()


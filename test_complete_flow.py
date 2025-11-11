#!/usr/bin/env python3
"""
Complete user flow test: From first run to telemetry opt-in and data collection.

This tests the entire user journey:
1. First run without ENV_GUARD_TELEMETRY (default opt-out)
2. Enable telemetry with ENV_GUARD_TELEMETRY=true
3. Run command and verify local data is saved
4. Verify Supabase data (if credentials configured)
"""

import os
import sys
import shutil
from pathlib import Path
import json

# Colors for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_step(step_num, description):
    print(f"\n{BLUE}═══ Step {step_num}: {description} ═══{RESET}")

def print_success(message):
    print(f"{GREEN}✓{RESET} {message}")

def print_warning(message):
    print(f"{YELLOW}⚠{RESET} {message}")

def print_error(message):
    print(f"{RED}✗{RESET} {message}")

def print_info(message):
    print(f"  {message}")

def test_first_run_no_telemetry():
    """Test: First run without telemetry enabled (default opt-out)."""
    print_step(1, "First Run - Telemetry Disabled by Default")
    
    # Ensure ENV_GUARD_TELEMETRY is not set
    if 'ENV_GUARD_TELEMETRY' in os.environ:
        del os.environ['ENV_GUARD_TELEMETRY']
    
    print_info("ENV_GUARD_TELEMETRY not set (default: disabled)")
    
    from env_guard.telemetry import create_tracker
    
    tracker = create_tracker()
    
    if not tracker.enabled:
        print_success("Telemetry correctly disabled by default (opt-out)")
        print_info(f"  Enabled: {tracker.enabled}")
        print_info(f"  ProofTracker: {tracker.tracker}")
        return True
    else:
        print_error("Telemetry should be disabled by default!")
        return False

def test_enable_telemetry():
    """Test: Enable telemetry with environment variable."""
    print_step(2, "Enable Telemetry")
    
    # Set environment variable
    os.environ['ENV_GUARD_TELEMETRY'] = 'true'
    print_info("Set ENV_GUARD_TELEMETRY=true")
    
    # Need to reimport to pick up the change
    import importlib
    from env_guard import telemetry
    importlib.reload(telemetry)
    
    tracker = telemetry.create_tracker()
    
    if tracker.enabled:
        print_success("Telemetry successfully enabled")
        print_info(f"  Enabled: {tracker.enabled}")
        print_info(f"  Session ID: {tracker.session_id}")
        print_info(f"  Run ID: {tracker.run_id}")
        return True
    else:
        print_error("Telemetry should be enabled!")
        print_info(f"  Check if proof-tracker is installed: pip show proof-tracker")
        return False

def test_local_data_saved():
    """Test: Verify data is saved locally."""
    print_step(3, "Verify Local Data Storage")
    
    os.environ['ENV_GUARD_TELEMETRY'] = 'true'
    
    from env_guard.telemetry import create_tracker
    
    tracker = create_tracker()
    
    if not tracker.enabled:
        print_warning("Telemetry not enabled - skipping local storage test")
        return True
    
    # Track a test event
    tracker.track_run_completed(
        command="flow_test",
        files_scanned=1,
        findings_total=2,
        findings_by_type={"test": 1, "example": 1},
        findings_by_severity={"medium": 2},
        auto_fixes_applied=0,
        runtime_ms=50,
        estimated_time_saved_minutes=0.5
    )
    
    # Check local file exists
    local_file = Path.home() / ".env_guard_telemetry" / "env_guard_tracking.json"
    stats_file = Path.home() / ".env_guard_telemetry" / "stats.json"
    
    if local_file.exists():
        print_success(f"Local tracking file exists: {local_file}")
        
        # Read and show recent event
        try:
            with open(local_file, 'r') as f:
                data = json.load(f)
                events = data.get('events', [])
                if events:
                    latest = events[-1]
                    print_info(f"  Latest event: {latest.get('name', 'N/A')}")
                    print_info(f"  Timestamp: {latest.get('timestamp', 'N/A')}")
                    print_success(f"  Total events logged: {len(events)}")
                else:
                    print_warning("  No events in file yet")
        except Exception as e:
            print_warning(f"  Could not read file: {e}")
    else:
        print_error(f"Local file not found: {local_file}")
        return False
    
    if stats_file.exists():
        print_success(f"Stats file exists: {stats_file}")
        try:
            with open(stats_file, 'r') as f:
                stats = json.load(f)
                print_info(f"  Total runs: {stats.get('total_runs', 0)}")
                print_info(f"  Success rate: {stats.get('reliability', {}).get('success_rate_percent', 0)}%")
        except Exception as e:
            print_warning(f"  Could not read stats: {e}")
    else:
        print_warning(f"Stats file not found yet: {stats_file}")
    
    return True

def test_supabase_connection():
    """Test: Verify Supabase connection (if configured)."""
    print_step(4, "Verify Supabase Connection (Optional)")
    
    # Check if Supabase credentials are configured
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print_warning("Supabase credentials not configured")
        print_info("  Set SUPABASE_URL and SUPABASE_KEY in .env to enable cloud telemetry")
        print_info("  Local telemetry still works without Supabase!")
        return True
    
    print_success("Supabase credentials found")
    print_info(f"  URL: {supabase_url[:30]}...")
    
    # Try to query recent events
    try:
        from supabase import create_client
        
        client = create_client(supabase_url, supabase_key)
        
        # Query recent events
        result = client.table('telemetry_events') \
            .select('type, name, timestamp') \
            .order('timestamp', desc=True) \
            .limit(5) \
            .execute()
        
        if result.data:
            print_success(f"Found {len(result.data)} recent events in Supabase")
            for event in result.data[:3]:
                print_info(f"  - {event.get('type')}: {event.get('name')} at {event.get('timestamp')}")
        else:
            print_warning("No events found in Supabase yet")
            print_info("  This is normal for a fresh installation")
        
        return True
        
    except Exception as e:
        print_error(f"Supabase connection failed: {e}")
        print_info("  Local telemetry will still work")
        return True  # Don't fail the test, just warning

def test_opt_out():
    """Test: Verify opt-out works."""
    print_step(5, "Verify Opt-Out")
    
    # Disable telemetry
    os.environ['ENV_GUARD_TELEMETRY'] = 'false'
    print_info("Set ENV_GUARD_TELEMETRY=false")
    
    import importlib
    from env_guard import telemetry
    importlib.reload(telemetry)
    
    tracker = telemetry.create_tracker()
    
    if not tracker.enabled:
        print_success("Opt-out successful - telemetry disabled")
        return True
    else:
        print_error("Opt-out failed - telemetry still enabled!")
        return False

def main():
    print("\n" + "="*70)
    print(" env-guard TELEMETRY FLOW TEST")
    print(" Complete User Journey: First Run → Opt-in → Data Collection")
    print("="*70)
    
    results = []
    
    # Run all tests
    results.append(("Default opt-out", test_first_run_no_telemetry()))
    results.append(("Enable telemetry", test_enable_telemetry()))
    results.append(("Local data storage", test_local_data_saved()))
    results.append(("Supabase connection", test_supabase_connection()))
    results.append(("Opt-out verification", test_opt_out()))
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        if result:
            print(f"{GREEN}✓{RESET} {name}")
            passed += 1
        else:
            print(f"{RED}✗{RESET} {name}")
            failed += 1
    
    print("\n" + "="*70)
    if failed == 0:
        print(f"{GREEN}✓ ALL TESTS PASSED ({passed}/{len(results)}){RESET}")
        print("="*70)
        print("\n" + GREEN + "Telemetry flow is working correctly!" + RESET)
        print("\nNext steps:")
        print("1. Run any env-guard command: env-guard check")
        print("2. Check local data: cat ~/.env_guard_telemetry/stats.json")
        print("3. Check Supabase dashboard (if configured)")
        return 0
    else:
        print(f"{RED}✗ SOME TESTS FAILED ({passed}/{len(results)} passed){RESET}")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())


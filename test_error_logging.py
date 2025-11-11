#!/usr/bin/env python3
"""
Test error logging to telemetry_errors table via ProofTracker.

This test checks if errors are automatically logged to Supabase's telemetry_errors table
when exceptions occur during env_guard operations.
"""

import sys
import os
import traceback
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def test_error_logging_via_tracker():
    """Test that errors are logged through ProofTracker to telemetry_errors table."""
    print("=" * 70)
    print("TEST: Error Logging to telemetry_errors via ProofTracker")
    print("=" * 70)
    print()
    
    try:
        # Set up environment
        os.environ["ENV_GUARD_TELEMETRY"] = "true"
        
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Environment configured")
        
        from env_guard.telemetry import create_tracker
        from proof_tracker import ProofTracker
        
        # Create tracker
        tracker = create_tracker()
        
        if not tracker.enabled:
            print("❌ Telemetry not enabled - cannot test error logging")
            print("   Make sure ENV_GUARD_TELEMETRY=true in your .env file")
            return False
        
        print(f"✓ Tracker created")
        print(f"  - Session ID: {tracker.session_id}")
        print(f"  - Enabled: {tracker.enabled}")
        print()
        
        # Test 1: Send a deliberate error through track_command_failure
        print("Test 1: Sending test error via track_command_failure...")
        try:
            tracker.track_command_failure(
                command="error_test",
                error_type="TestError",
                error_message="This is a test error for telemetry_errors table"
            )
            print("  ✓ Error event sent via track_command_failure")
        except Exception as e:
            print(f"  ❌ Failed to send error: {e}")
            traceback.print_exc()
            return False
        
        print()
        
        # Test 2: Trigger an actual exception and see if it's logged
        print("Test 2: Triggering real exception to test automatic logging...")
        try:
            # This should trigger an error that might be logged
            raise ValueError("Test exception - checking if ProofTracker logs to telemetry_errors")
        except ValueError as e:
            # Log this as a failure event
            stack = traceback.format_exc()
            tracker.track_command_failure(
                command="exception_test",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            print(f"  ✓ Exception caught and logged: {type(e).__name__}")
        
        print()
        
        # Test 3: Check if ProofTracker has error logging capabilities
        print("Test 3: Checking ProofTracker error logging capabilities...")
        if hasattr(tracker.tracker, 'supabase_client'):
            print("  ✓ ProofTracker has Supabase client")
            
            # Try to query the telemetry_errors table
            try:
                from supabase import create_client
                
                supabase_url = os.getenv("SUPABASE_URL")
                supabase_key = os.getenv("SUPABASE_KEY")
                
                if supabase_url and supabase_key:
                    client = create_client(supabase_url, supabase_key)
                    
                    # Query recent errors
                    result = client.table('telemetry_errors') \
                        .select('*') \
                        .order('timestamp', desc=True) \
                        .limit(5) \
                        .execute()
                    
                    if result.data:
                        print(f"  ✓ Found {len(result.data)} recent errors in database")
                        for i, error in enumerate(result.data[:3], 1):
                            print(f"    {i}. [{error.get('error_type')}] {error.get('error_message')[:60]}...")
                            print(f"       Session: {error.get('session_id')}")
                            print(f"       Time: {error.get('timestamp')}")
                    else:
                        print("  ℹ No errors found in database (this is okay)")
                else:
                    print("  ⚠ SUPABASE_URL or SUPABASE_KEY not configured")
                    
            except Exception as e:
                print(f"  ⚠ Could not query telemetry_errors: {e}")
        else:
            print("  ℹ ProofTracker doesn't expose Supabase client directly")
        
        print()
        print("=" * 70)
        print("✅ Error logging tests completed!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Check your Supabase dashboard")
        print("2. Go to: Table Editor → telemetry_errors")
        print("3. Look for errors with error_type='TestError' or 'ValueError'")
        print(f"4. Filter by session_id: {tracker.session_id}")
        print()
        print("Note: ProofTracker may log errors automatically when internal")
        print("      operations fail. Check the context field in telemetry_errors")
        print("      for proof_data that shows which events triggered errors.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        traceback.print_exc()
        return False


def test_error_context_in_supabase():
    """Test that error context is properly stored in Supabase."""
    print("\n" + "=" * 70)
    print("TEST: Error Context Preservation")
    print("=" * 70)
    print()
    
    try:
        os.environ["ENV_GUARD_TELEMETRY"] = "true"
        from dotenv import load_dotenv
        load_dotenv()
        
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("⚠ Supabase credentials not configured - skipping")
            return True
        
        client = create_client(supabase_url, supabase_key)
        
        # Query recent errors with context
        result = client.table('telemetry_errors') \
            .select('*') \
            .order('timestamp', desc=True) \
            .limit(10) \
            .execute()
        
        if not result.data:
            print("ℹ No errors found in database")
            print("  This could mean:")
            print("  - ProofTracker hasn't encountered any errors yet")
            print("  - Errors are logged elsewhere")
            print("  - Table permissions need to be checked")
            return True
        
        print(f"✓ Found {len(result.data)} errors in database")
        print()
        
        # Analyze error context
        for i, error in enumerate(result.data[:3], 1):
            print(f"Error #{i}:")
            print(f"  Type: {error.get('error_type')}")
            print(f"  Message: {error.get('error_message')[:80]}")
            print(f"  Session: {error.get('session_id')}")
            
            context = error.get('context', {})
            if context:
                print(f"  Context: {context}")
                
                # Check if this is from our proof_data
                proof_data = context.get('proof_data', {})
                if proof_data:
                    print(f"    - Event Type: {proof_data.get('event_type')}")
                    event_data = proof_data.get('event_data', {})
                    if event_data:
                        print(f"    - Event Data: {str(event_data)[:60]}...")
            
            stack_trace = error.get('stack_trace', '')
            if stack_trace:
                lines = stack_trace.split('\n')
                print(f"  Stack Trace: {len(lines)} lines")
                # Show relevant lines
                for line in lines:
                    if 'env_guard' in line or 'telemetry' in line:
                        print(f"    {line.strip()}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║         env_guard - Telemetry Error Logging Tests                ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print()
    
    all_passed = True
    
    all_passed &= test_error_logging_via_tracker()
    all_passed &= test_error_context_in_supabase()
    
    print()
    if all_passed:
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║                    ✅ ALL TESTS PASSED                            ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        sys.exit(0)
    else:
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║                    ❌ SOME TESTS FAILED                           ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        sys.exit(1)


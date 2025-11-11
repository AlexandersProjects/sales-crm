"""Quick test to check proof_tracker version and Supabase support."""
import sys
sys.path.insert(0, '.venv/Lib/site-packages')

try:
    from proof_tracker import ProofTracker
    import proof_tracker
    print(f"✅ proof_tracker found")
    print(f"   Version: {proof_tracker.__version__ if hasattr(proof_tracker, '__version__') else 'Unknown'}")
    print(f"   Location: {proof_tracker.__file__}")

    # Check if Supabase support exists
    import inspect
    source = inspect.getsource(ProofTracker.__init__)

    if "telemetry_backend" in source:
        print(f"✅ telemetry_backend parameter exists")
    else:
        print(f"❌ telemetry_backend parameter NOT found")

    if "supabase_url" in source:
        print(f"✅ supabase_url parameter exists")
    else:
        print(f"❌ supabase_url parameter NOT found")

    # Try to find SupabaseTelemetryClient
    try:
        # Check the import attempt
        if "SupabaseTelemetryClient" in source:
            print(f"✅ SupabaseTelemetryClient referenced in code")

        # Try to import it
        import os
        pkg_dir = os.path.dirname(proof_tracker.__file__)
        print(f"\n📁 Package contents:")
        for item in os.listdir(pkg_dir):
            print(f"   - {item}")

    except Exception as e:
        print(f"⚠️  Error checking Supabase support: {e}")

except ImportError as e:
    print(f"❌ proof_tracker NOT installed: {e}")


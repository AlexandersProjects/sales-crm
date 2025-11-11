#!/usr/bin/env python3
"""Release helper script (cross-platform).

Usage:
    python scripts/release.py [--upload testpypi|pypi]

What it does:
- Runs tests (pytest)
- Runs ruff and mypy (if installed)
- Builds sdist and wheel (python -m build)
- Runs twine check on artifacts
- Optionally uploads to TestPyPI or PyPI with twine

Requires: Python 3.9+, build, twine in your environment.
"""
import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
DIST_DIR = os.path.join(ROOT, "dist")


def run(cmd, check=True, **kwargs):
    print("Running:", " ".join(cmd) if isinstance(cmd, list) else cmd)
    res = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=ROOT, **kwargs)
    if check and res.returncode != 0:
        raise SystemExit(res.returncode)
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", choices=["testpypi", "pypi"], help="Upload target")
    parser.add_argument("--skip-checks", action="store_true", help="Skip lint/type checks")
    args = parser.parse_args()

    # 1) tests
    run([sys.executable, "-m", "pytest", "-q"])

    # 2) lint/type checks (optional)
    if not args.skip_checks:
        if shutil.which("ruff"):
            run([shutil.which("ruff"), "check", "."])
        else:
            print("ruff not found; skipping ruff checks")
        if shutil.which("mypy"):
            run([shutil.which("mypy"), "env_guard"])
        else:
            print("mypy not found; skipping mypy checks")

    # 3) clean dist
    if os.path.exists(DIST_DIR):
        print("Removing existing dist/ directory")
        shutil.rmtree(DIST_DIR)

    # 4) build
    run([sys.executable, "-m", "build", "--sdist", "--wheel", "--outdir", "dist"])

    # 5) twine check
    run([sys.executable, "-m", "twine", "check", "dist/*"])

    # 6) optional upload
    if args.upload:
        if args.upload == "testpypi":
            repo = "testpypi"
        else:
            repo = "pypi"
        print(f"Uploading to {repo} (twine will ask for credentials or use env vars)")
        run([sys.executable, "-m", "twine", "upload", "--repository", repo, "dist/*"])

    print("Release process completed successfully.")


if __name__ == "__main__":
    main()


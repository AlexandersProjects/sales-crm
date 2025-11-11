# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

"""Telemetry tracking for env_guard using proof_tracker.

Simple integration:
1. pip install proof_tracker[supabase]
2. tracker = ProofTracker(telemetry_backend="supabase")
3. tracker.log_proof({...})

That's it! proof_tracker handles all Supabase details internally.
"""

import os
import platform
import uuid
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Try to import proof_tracker, but make it optional
try:
    from proof_tracker import ProofTracker
    PROOF_TRACKER_AVAILABLE = True
except ImportError:
    PROOF_TRACKER_AVAILABLE = False
    ProofTracker = None
    logger.debug("proof_tracker not available - telemetry disabled")


def get_session_id() -> str:
    """
    Get or create a persistent session ID for this telemetry session.

    The session ID is stored in the telemetry config directory and persists
    across multiple command invocations within the same session/environment.

    Returns:
        A valid UUID string in standard format (e.g., "abc-123-...")
    """
    config_dir = os.path.expanduser("~/.env_guard_telemetry")
    session_file = os.path.join(config_dir, "session_id.txt")

    try:
        # Try to read existing session ID
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                session_id = f.read().strip()
                if session_id:
                    # Validate it's a proper UUID format
                    try:
                        uuid.UUID(session_id)  # This validates the format
                        logger.debug(f"✅ Loaded valid session_id from file: {session_id}")
                        return session_id
                    except ValueError:
                        logger.debug(f"⚠️ Invalid UUID in session file, generating new one")
                        pass  # Invalid UUID, will generate new one below

        # Create new session ID if file doesn't exist, is empty, or invalid
        os.makedirs(config_dir, exist_ok=True)
        session_id = str(uuid.uuid4())

        with open(session_file, 'w') as f:
            f.write(session_id)

        logger.debug(f"✅ Generated new session_id: {session_id}")
        return session_id
    except Exception as e:
        logger.debug(f"Failed to manage session ID file: {e}")
        # Fallback to generating a new UUID each time
        fallback_id = str(uuid.uuid4())
        logger.debug(f"⚠️ Using fallback session_id: {fallback_id}")
        return fallback_id


def get_environment_metadata() -> Dict[str, Optional[str]]:
    """
    Collect environment metadata for telemetry.

    Returns:
        Dict containing OS info, Python version, and proof_tracker version
    """
    metadata = {
        "os_name": platform.system(),
        "os_version": platform.release(),
        "python_version": platform.python_version(),
        "proof_tracker_version": None,
    }

    # Try to get proof_tracker version
    try:
        if PROOF_TRACKER_AVAILABLE:
            import proof_tracker
            if hasattr(proof_tracker, '__version__'):
                metadata["proof_tracker_version"] = proof_tracker.__version__
            else:
                metadata["proof_tracker_version"] = "unknown"
    except Exception as e:
        logger.debug(f"Could not determine proof_tracker version: {e}")

    return metadata


class TelemetryTracker:
    """Handles anonymous telemetry tracking for env_guard."""

    def __init__(self):
        self.enabled = self._is_enabled()
        self.run_id = str(uuid.uuid4())
        self.session_id = get_session_id()  # Persistent session ID
        self.start_time = datetime.now(timezone.utc)
        self.env_metadata = get_environment_metadata()  # OS, Python version, etc.
        self.tracker: Optional[Any] = None

        if self.enabled:
            self._initialize_tracker()

    def _custom_stats_calculator(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Custom statistics calculator for env_guard.

        Collects anonymous, safe-to-store metrics about usage patterns.

        Args:
            logs: List of all proof log entries

        Returns:
            Dictionary containing calculated statistics
        """
        if not logs:
            return {
                "total_runs": 0,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "commands": {},
                "findings": {
                    "total": 0,
                    "by_type": {},
                    "by_severity": {},
                },
                "auto_fixes": {
                    "total": 0,
                },
                "time_saved_minutes": 0.0,
            }

        # Initialize counters
        total_runs = len(logs)
        commands_count = {}
        total_findings = 0
        findings_by_type = {}
        findings_by_severity = {}
        total_auto_fixes = 0
        total_time_saved = 0.0
        total_runtime_ms = 0
        completed_runs = 0
        failed_runs = 0

        # Process each log entry
        for log in logs:
            # Handle both old and new formats
            event_data = log.get("event_data") or log.get("details") or {}

            # ProofTracker may store event_data as JSON string in file
            # but passes it as dict when it's a new event
            if isinstance(event_data, str):
                try:
                    event_data = json.loads(event_data)
                except (json.JSONDecodeError, ValueError):
                    logger.debug(f"Failed to parse event_data as JSON: {event_data}")
                    event_data = {}

            event_type = log.get("event_type", "")
            status = event_data.get("status", "")

            # Extract command name from event_type (e.g., "check_completed" -> "check")
            command = event_data.get("command", "unknown")
            if not command or command == "unknown":
                # Try to extract from event_type
                if "_completed" in event_type:
                    command = event_type.replace("_completed", "")
                elif "_failed" in event_type:
                    command = event_type.replace("_failed", "")

            # Count commands
            commands_count[command] = commands_count.get(command, 0) + 1

            # Track findings
            if "findings_total" in event_data:
                total_findings += event_data["findings_total"]

            # Track findings by type
            if "findings_by_type" in event_data:
                for ftype, count in event_data["findings_by_type"].items():
                    findings_by_type[ftype] = findings_by_type.get(ftype, 0) + count

            # Track findings by severity
            if "findings_by_severity" in event_data:
                for severity, count in event_data["findings_by_severity"].items():
                    findings_by_severity[severity] = findings_by_severity.get(severity, 0) + count

            # Track auto-fixes
            if "auto_fixes_applied" in event_data:
                total_auto_fixes += event_data["auto_fixes_applied"]

            # Track time saved
            if "estimated_time_saved_minutes" in event_data:
                total_time_saved += event_data["estimated_time_saved_minutes"]

            # Track runtime
            if "runtime_ms" in event_data:
                total_runtime_ms += event_data["runtime_ms"]

            # Track success/failure
            if status == "completed" or "_completed" in event_type:
                completed_runs += 1
            elif status == "failed" or "_failed" in event_type:
                failed_runs += 1

        # Calculate averages
        avg_runtime_ms = total_runtime_ms / completed_runs if completed_runs > 0 else 0
        avg_findings_per_run = total_findings / total_runs if total_runs > 0 else 0
        success_rate = (completed_runs / total_runs * 100) if total_runs > 0 else 0

        return {
            "total_runs": total_runs,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "commands": commands_count,
            "findings": {
                "total": total_findings,
                "average_per_run": round(avg_findings_per_run, 2),
                "by_type": findings_by_type,
                "by_severity": findings_by_severity,
            },
            "auto_fixes": {
                "total": total_auto_fixes,
            },
            "time_saved_minutes": round(total_time_saved, 2),
            "performance": {
                "average_runtime_ms": round(avg_runtime_ms, 2),
                "total_runtime_ms": total_runtime_ms,
            },
            "reliability": {
                "completed_runs": completed_runs,
                "failed_runs": failed_runs,
                "success_rate_percent": round(success_rate, 2),
            },
        }

    def _is_enabled(self) -> bool:
        """Check if telemetry is enabled via environment variable or config."""
        # Check environment variable for opt-in/opt-out
        # Default to opt-out (false) to respect user privacy
        env_value = os.getenv("ENV_GUARD_TELEMETRY", "false").lower()

        # Only enable if explicitly set to true
        if env_value not in ("1", "true", "yes", "on", "enabled"):
            return False

        # Check if proof_tracker is available
        if not PROOF_TRACKER_AVAILABLE:
            logger.debug("Telemetry disabled: proof_tracker not installed")
            return False

        return True

    def _initialize_tracker(self) -> None:
        """Initialize the ProofTracker instance.

        Simple setup:
        - ProofTracker(telemetry_backend="supabase") enables both:
          * Local file logging (always works)
          * Supabase cloud telemetry (proof_tracker handles URL, API key, client)
        - We provide a custom stats_calculator for enhanced metrics

        That's it! We just use tracker.log_proof() and proof_tracker does the rest.
        """
        if not PROOF_TRACKER_AVAILABLE or ProofTracker is None:
            logger.debug("ProofTracker not available - cannot initialize")
            return

        try:
            # Create config directory for env_guard telemetry
            config_dir = os.path.expanduser("~/.env_guard_telemetry")
            os.makedirs(config_dir, exist_ok=True)

            # Set up file path for local logging
            file_path = os.path.join(config_dir, "env_guard_tracking.json")

            # Initialize ProofTracker - it handles everything internally:
            # - Local file logging
            # - Supabase client initialization (URL, API key, connection)
            # - Telemetry opt-in preference management
            # We just call tracker.log_proof() and it does the rest!
            self.tracker = ProofTracker(
                file_path=file_path,
                stats_calculator=self._custom_stats_calculator,  # Our enhanced metrics
                telemetry_backend="supabase"  # proof_tracker handles the Supabase details
            )

            logger.debug(f"ProofTracker initialized successfully")
            logger.debug(f"  - Local file: {file_path}")
            logger.debug(f"  - Stats file: {os.path.join(config_dir, 'stats.json')}")
            logger.debug(f"  - Custom stats: Enhanced metrics enabled")
            logger.debug(f"  - Cloud backend: Supabase (via proof_tracker)")
            logger.debug(f"  - Usage: Just call tracker.log_proof({...}) and proof_tracker handles everything")

        except Exception as e:
            logger.warning(f"Failed to initialize ProofTracker: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            self.enabled = False
            self.tracker = None

    def track_run_completed(
        self,
        command: str,
        files_scanned: int,
        findings_total: int,
        findings_by_type: Dict[str, int],
        findings_by_severity: Dict[str, int],
        auto_fixes_applied: int = 0,
        runtime_ms: Optional[int] = None,
        estimated_time_saved_minutes: Optional[float] = None,
        sample_rate: float = 1.0,
    ) -> None:
        """
        Track a completed run of env_guard.

        Args:
            command: The command that was run (e.g., "check", "suggest", "init")
            files_scanned: Number of files scanned
            findings_total: Total number of findings
            findings_by_type: Dict mapping finding type to count
            findings_by_severity: Dict mapping severity level to count
            auto_fixes_applied: Number of automatic fixes applied
            runtime_ms: Runtime in milliseconds
            estimated_time_saved_minutes: Estimated time saved in minutes
            sample_rate: Sampling rate for telemetry (0.0-1.0)
        """
        if not self.enabled or self.tracker is None:
            return

        # Calculate runtime if not provided
        if runtime_ms is None:
            elapsed = datetime.now(timezone.utc) - self.start_time
            runtime_ms = int(elapsed.total_seconds() * 1000)

        # Build event data in Supabase-compatible format
        event_data = {
            "version": 1,
            "status": "completed",
            "run_id": self.run_id,
            "command": command,
            "files_scanned": files_scanned,
            "findings_total": findings_total,
            "findings_by_type": findings_by_type,
            "findings_by_severity": findings_by_severity,
            "auto_fixes_applied": auto_fixes_applied,
            "runtime_ms": runtime_ms,
            "estimated_time_saved_minutes": estimated_time_saved_minutes or 0.0,
            "opt_in": True,
            "sample_rate": sample_rate,
            "anonymized": True,
        }

        try:
            # Use ProofTracker's unified API - just send event_type and event_data
            # ProofTracker automatically enriches with session_id, timestamp, environment metadata
            logger.debug(f"📤 Sending event to ProofTracker: event_type={command}_completed")
            logger.debug(f"📦 Event data:\n{json.dumps(event_data, indent=2, default=str)}")

            self.tracker.log_proof({
                "event_type": f"{command}_completed",
                "event_data": event_data
            })

            # Register additional metrics
            self.tracker.register_event(f"{command}_runs", 1)
            self.tracker.register_event("total_findings", findings_total)
            self.tracker.register_event("auto_fixes_applied", auto_fixes_applied)

            logger.debug(f"✅ Telemetry event sent: {command}_completed")
        except Exception as e:
            # Never fail the user's command due to telemetry issues
            logger.debug(f"⚠️ Failed to send telemetry: {e}")

    def track_command_failure(
        self,
        command: str,
        error_type: str,
        error_message: str,
    ) -> None:
        """
        Track a failed command execution.

        Args:
            command: The command that failed (e.g., "check", "suggest", "init")
            error_type: Type of error (e.g., "FileNotFoundError", "ValidationError")
            error_message: Brief error message (no sensitive data)
        """
        if not self.enabled or self.tracker is None:
            return

        try:
            # Use ProofTracker's unified API
            logger.debug(f"📤 Sending failure event to ProofTracker: event_type={command}_failed")

            self.tracker.log_proof({
                "event_type": f"{command}_failed",
                "event_data": {
                    "version": 1,
                    "status": "failed",
                    "run_id": self.run_id,
                    "command": command,
                    "error_type": error_type,
                    "error_message": error_message,
                    "anonymized": True,
                }
            })

            # Also log to telemetry_errors table using ProofTracker's log_error
            self.tracker.log_error(
                error_type=error_type,
                error_message=error_message,
                context={
                    "command": command,
                    "run_id": self.run_id,
                    "source": "env_guard"
                }
            )

            # Register failure metric
            self.tracker.register_event(f"{command}_failures", 1)

            logger.debug(f"✅ Telemetry failure logged: {command}_failed")
        except Exception as e:
            # Never fail the user's command due to telemetry issues
            logger.debug(f"⚠️ Failed to log telemetry failure: {e}")


def create_tracker() -> TelemetryTracker:
    """Create and return a new telemetry tracker instance."""
    return TelemetryTracker()


def calculate_findings_by_type(results: List[Any]) -> Dict[str, int]:
    """
    Calculate findings by type from validation results.

    Args:
        results: List of ValidationResult objects

    Returns:
        Dict mapping finding type to count
    """
    findings = {
        "missing_key": 0,
        "type_mismatch": 0,
        "pattern_mismatch": 0,
        "forbidden_value": 0,
        "required_if": 0,
        "unknown_key": 0,
        "other": 0,
    }

    for result in results:
        if result.status == "ok":
            continue

        # Categorize by expected field or message
        if result.expected and "required" in result.expected.lower():
            findings["missing_key"] += 1
        elif result.expected and "pattern" in result.expected.lower():
            findings["pattern_mismatch"] += 1
        elif result.expected and "not" in result.expected.lower():
            findings["forbidden_value"] += 1
        elif result.expected and "required_if" in result.expected.lower():
            findings["required_if"] += 1
        elif "type" in result.message.lower() or "should be" in result.message.lower():
            findings["type_mismatch"] += 1
        elif "unknown" in result.message.lower():
            findings["unknown_key"] += 1
        else:
            findings["other"] += 1

    return findings


def calculate_findings_by_severity(results: List[Any]) -> Dict[str, int]:
    """
    Calculate findings by severity from validation results.

    Args:
        results: List of ValidationResult objects

    Returns:
        Dict mapping severity level to count
    """
    severity = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for result in results:
        if result.status == "error":
            # Categorize errors by type
            if "forbidden" in result.message.lower() or "secret" in result.message.lower():
                severity["critical"] += 1
            elif "missing required" in result.message.lower():
                severity["high"] += 1
            else:
                severity["medium"] += 1
        elif result.status == "warning":
            severity["low"] += 1

    return severity


def estimate_time_saved(findings_total: int, auto_fixes_applied: int) -> float:
    """
    Estimate time saved by using env_guard.

    Rough estimates:
    - Each finding identified saves ~2 minutes of debugging time
    - Each auto-fix saves an additional ~1 minute of manual editing

    Args:
        findings_total: Total number of findings
        auto_fixes_applied: Number of automatic fixes applied

    Returns:
        Estimated time saved in minutes
    """
    time_per_finding = 2.0  # minutes
    time_per_fix = 1.0  # additional minutes

    return (findings_total * time_per_finding) + (auto_fixes_applied * time_per_fix)


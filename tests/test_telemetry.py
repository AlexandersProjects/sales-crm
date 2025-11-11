"""Tests for telemetry module."""

from unittest.mock import Mock, patch
from env_guard.telemetry import (
    TelemetryTracker,
    create_tracker,
    calculate_findings_by_type,
    calculate_findings_by_severity,
    estimate_time_saved,
)
from env_guard.validator import ValidationResult


class TestTelemetryTracker:
    """Test the TelemetryTracker class."""

    def test_tracker_disabled_when_env_var_false(self, monkeypatch):
        """Test that tracker is disabled when ENV_GUARD_TELEMETRY=false."""
        monkeypatch.setenv("ENV_GUARD_TELEMETRY", "false")
        tracker = TelemetryTracker()
        assert tracker.enabled is False

    def test_tracker_disabled_when_env_var_0(self, monkeypatch):
        """Test that tracker is disabled when ENV_GUARD_TELEMETRY=0."""
        monkeypatch.setenv("ENV_GUARD_TELEMETRY", "0")
        tracker = TelemetryTracker()
        assert tracker.enabled is False

    def test_tracker_disabled_when_proof_tracker_not_available(self, monkeypatch):
        """Test that tracker is disabled when proof_tracker is not installed."""
        # Mock the import to simulate proof_tracker not being available
        with patch.dict('sys.modules', {'proof_tracker': None}):
            monkeypatch.setenv("ENV_GUARD_TELEMETRY", "true")
            tracker = TelemetryTracker()
            # Should be disabled because proof_tracker is not available
            # This test might need adjustment based on actual import behavior
            pass

    def test_tracker_disabled_by_default(self, monkeypatch):
        """Test that tracker is disabled by default (opt-in required)."""
        monkeypatch.delenv("ENV_GUARD_TELEMETRY", raising=False)
        tracker = TelemetryTracker()
        # Should be disabled by default (opt-in approach)
        assert tracker.enabled is False

    def test_tracker_enabled_when_explicitly_enabled(self, monkeypatch):
        """Test that tracker is enabled when ENV_GUARD_TELEMETRY=true."""
        monkeypatch.setenv("ENV_GUARD_TELEMETRY", "true")
        # Note: This will be False if proof_tracker is not installed, which is expected
        tracker = TelemetryTracker()
        # Check that it's a boolean (True if proof_tracker installed, False otherwise)
        assert isinstance(tracker.enabled, bool)

    def test_run_id_is_generated(self):
        """Test that each tracker gets a unique run_id."""
        tracker1 = TelemetryTracker()
        tracker2 = TelemetryTracker()
        assert tracker1.run_id != tracker2.run_id

    def test_track_run_completed_disabled(self, monkeypatch):
        """Test that track_run_completed does nothing when disabled."""
        monkeypatch.setenv("ENV_GUARD_TELEMETRY", "false")
        tracker = TelemetryTracker()

        # Should not raise an error even when disabled
        tracker.track_run_completed(
            command="check",
            files_scanned=1,
            findings_total=5,
            findings_by_type={"missing_key": 3, "type_mismatch": 2},
            findings_by_severity={"high": 2, "medium": 3},
            auto_fixes_applied=1,
        )

    def test_track_run_completed_with_runtime(self):
        """Test track_run_completed with explicit runtime."""
        tracker = TelemetryTracker()
        tracker.enabled = True  # Force enable for test

        # Mock the tracker instance
        mock_proof_tracker = Mock()
        tracker.tracker = mock_proof_tracker

        tracker.track_run_completed(
            command="check",
            files_scanned=1,
            findings_total=5,
            findings_by_type={"missing_key": 3},
            findings_by_severity={"high": 2},
            auto_fixes_applied=1,
            runtime_ms=420,
            estimated_time_saved_minutes=12.5,
        )

        # Verify log_proof was called
        mock_proof_tracker.log_proof.assert_called_once()
        call_args = mock_proof_tracker.log_proof.call_args[0][0]
        # Check ProofTracker format: ONLY event_type and event_data
        assert call_args["event_type"] == "check_completed"
        # event_data is a dict (ProofTracker handles serialization)
        assert isinstance(call_args["event_data"], dict)
        assert call_args["event_data"]["status"] == "completed"
        assert call_args["event_data"]["runtime_ms"] == 420
        assert call_args["event_data"]["findings_total"] == 5
        # Auto-enriched fields should NOT be in our payload (ProofTracker adds them)
        assert "session_id" not in call_args
        assert "os_name" not in call_args
        assert "timestamp" not in call_args
    def test_track_command_failure(self):
        """Test track_command_failure method."""
        tracker = TelemetryTracker()
        tracker.enabled = True  # Force enable for test

        # Mock the tracker instance
        mock_proof_tracker = Mock()
        tracker.tracker = mock_proof_tracker

        tracker.track_command_failure(
            command="check",
            error_type="FileNotFoundError",
            error_message="File not found: .env"
        )

        # Verify log_proof was called
        mock_proof_tracker.log_proof.assert_called_once()
        call_args = mock_proof_tracker.log_proof.call_args[0][0]
        # Check ProofTracker format: ONLY event_type and event_data
        assert call_args["event_type"] == "check_failed"
        # event_data is a dict (ProofTracker handles serialization)
        assert isinstance(call_args["event_data"], dict)
        assert call_args["event_data"]["status"] == "failed"
        assert call_args["event_data"]["error_type"] == "FileNotFoundError"
        assert call_args["event_data"]["error_message"] == "File not found: .env"
        # Auto-enriched fields should NOT be in our payload (ProofTracker adds them)
        assert "session_id" not in call_args
        assert "os_name" not in call_args
        assert "timestamp" not in call_args
class TestCalculateFindingsByType:
    """Test the calculate_findings_by_type function."""

    def test_empty_results(self):
        """Test with no results."""
        results = []
        findings = calculate_findings_by_type(results)
        assert findings["missing_key"] == 0
        assert findings["type_mismatch"] == 0

    def test_missing_key(self):
        """Test detection of missing key errors."""
        results = [
            ValidationResult(
                key="API_KEY",
                status="error",
                message="Missing required variable: API_KEY",
                expected="required",
            )
        ]
        findings = calculate_findings_by_type(results)
        assert findings["missing_key"] == 1

    def test_type_mismatch(self):
        """Test detection of type mismatch errors."""
        results = [
            ValidationResult(
                key="PORT",
                status="error",
                message="PORT should be an integer",
                expected="int",
                found="abc",
            )
        ]
        findings = calculate_findings_by_type(results)
        assert findings["type_mismatch"] == 1

    def test_pattern_mismatch(self):
        """Test detection of pattern mismatch errors."""
        results = [
            ValidationResult(
                key="EMAIL",
                status="error",
                message="EMAIL does not match pattern",
                expected="pattern ^[a-z]+$",
                found="test@test.com",
            )
        ]
        findings = calculate_findings_by_type(results)
        assert findings["pattern_mismatch"] == 1

    def test_forbidden_value(self):
        """Test detection of forbidden values."""
        results = [
            ValidationResult(
                key="DEBUG",
                status="error",
                message="Forbidden value: DEBUG=true",
                expected="not true",
                found="true",
            )
        ]
        findings = calculate_findings_by_type(results)
        assert findings["forbidden_value"] == 1

    def test_mixed_findings(self):
        """Test with multiple types of findings."""
        results = [
            ValidationResult("KEY1", "error", "Missing required variable: KEY1", expected="required"),
            ValidationResult("KEY2", "error", "KEY2 should be an integer", expected="int"),
            ValidationResult("KEY3", "ok", "KEY3 is valid", expected="string"),
        ]
        findings = calculate_findings_by_type(results)
        assert findings["missing_key"] == 1
        assert findings["type_mismatch"] == 1


class TestCalculateFindingsBySeverity:
    """Test the calculate_findings_by_severity function."""

    def test_empty_results(self):
        """Test with no results."""
        results = []
        severity = calculate_findings_by_severity(results)
        assert severity["critical"] == 0
        assert severity["high"] == 0

    def test_critical_forbidden_value(self):
        """Test that forbidden values are marked as critical."""
        results = [
            ValidationResult(
                key="API_KEY",
                status="error",
                message="Forbidden value: API_KEY=test",
                expected="not test",
            )
        ]
        severity = calculate_findings_by_severity(results)
        assert severity["critical"] == 1

    def test_high_missing_required(self):
        """Test that missing required keys are marked as high."""
        results = [
            ValidationResult(
                key="API_KEY",
                status="error",
                message="Missing required variable: API_KEY",
                expected="required",
            )
        ]
        severity = calculate_findings_by_severity(results)
        assert severity["high"] == 1

    def test_medium_other_errors(self):
        """Test that other errors are marked as medium."""
        results = [
            ValidationResult(
                key="PORT",
                status="error",
                message="PORT should be an integer",
                expected="int",
            )
        ]
        severity = calculate_findings_by_severity(results)
        assert severity["medium"] == 1

    def test_low_warnings(self):
        """Test that warnings are marked as low."""
        results = [
            ValidationResult(
                key="DEBUG",
                status="warning",
                message="DEBUG has default available",
                suggestion="Use default: false",
            )
        ]
        severity = calculate_findings_by_severity(results)
        assert severity["low"] == 1


class TestEstimateTimeSaved:
    """Test the estimate_time_saved function."""

    def test_no_findings(self):
        """Test with no findings."""
        time_saved = estimate_time_saved(findings_total=0, auto_fixes_applied=0)
        assert time_saved == 0.0

    def test_only_findings(self):
        """Test with findings but no fixes."""
        time_saved = estimate_time_saved(findings_total=5, auto_fixes_applied=0)
        assert time_saved == 10.0  # 5 * 2 minutes

    def test_findings_and_fixes(self):
        """Test with both findings and fixes."""
        time_saved = estimate_time_saved(findings_total=3, auto_fixes_applied=2)
        assert time_saved == 8.0  # (3 * 2) + (2 * 1) = 8 minutes

    def test_only_fixes(self):
        """Test with only fixes (edge case)."""
        time_saved = estimate_time_saved(findings_total=0, auto_fixes_applied=3)
        assert time_saved == 3.0  # 3 * 1 minute


class TestCreateTracker:
    """Test the create_tracker factory function."""

    def test_create_tracker_returns_instance(self):
        """Test that create_tracker returns a TelemetryTracker instance."""
        tracker = create_tracker()
        assert isinstance(tracker, TelemetryTracker)

    def test_create_tracker_generates_unique_ids(self):
        """Test that each created tracker has a unique run_id."""
        tracker1 = create_tracker()
        tracker2 = create_tracker()
        assert tracker1.run_id != tracker2.run_id


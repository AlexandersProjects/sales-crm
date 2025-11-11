# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

"""
Test suite for warning vs error distinction in validation results.
"""

from pathlib import Path
from env_guard.validator import EnvValidator


def write_env(lines, path):
    """Helper to write env file content."""
    p = Path(path)
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def test_missing_required_without_default_is_error(tmp_path):
    """Missing required variable without default should be ERROR."""
    env_file = tmp_path / ".env"
    write_env(["PORT=8000"], env_file)

    schema = {
        "required": ["DATABASE_URL"],
        "types": {"PORT": "int"}
    }

    v = EnvValidator(str(env_file), schema)
    res = v.run_all()

    # Find the DATABASE_URL result
    db_result = next((r for r in res if r.key == "DATABASE_URL"), None)
    assert db_result is not None, "DATABASE_URL should have a validation result"
    assert db_result.status == "error", "Missing required var without default should be ERROR"
    assert db_result.expected == "required"
    assert db_result.found is None


def test_missing_required_with_default_is_warning(tmp_path):
    """Missing required variable with default should be WARNING."""
    env_file = tmp_path / ".env"
    write_env(["PORT=8000"], env_file)

    schema = {
        "required": ["DATABASE_URL"],
        "types": {"PORT": "int"},
        "defaults": {
            "DATABASE_URL": "sqlite:///:memory:"
        }
    }

    v = EnvValidator(str(env_file), schema)
    res = v.run_all()

    # Find the DATABASE_URL result
    db_result = next((r for r in res if r.key == "DATABASE_URL"), None)
    assert db_result is not None, "DATABASE_URL should have a validation result"
    assert db_result.status == "warning", "Missing required var with default should be WARNING"
    assert db_result.expected == "required"
    assert db_result.found is None
    assert db_result.suggestion is not None, "Should have a suggestion"
    assert "default" in db_result.message.lower()


def test_empty_required_without_default_is_error(tmp_path):
    """Empty required variable without default should be ERROR."""
    env_file = tmp_path / ".env"
    write_env(["DATABASE_URL=", "PORT=8000"], env_file)

    schema = {
        "required": ["DATABASE_URL"],
        "types": {"PORT": "int"}
    }

    v = EnvValidator(str(env_file), schema)
    res = v.run_all()

    db_result = next((r for r in res if r.key == "DATABASE_URL"), None)
    assert db_result is not None
    assert db_result.status == "error", "Empty required var without default should be ERROR"
    assert db_result.line is None, "Missing/empty required vars should have line=None (show as ?)"


def test_empty_required_with_default_is_warning(tmp_path):
    """Empty required variable with default should be WARNING."""
    env_file = tmp_path / ".env"
    write_env(["DATABASE_URL=", "PORT=8000"], env_file)

    schema = {
        "required": ["DATABASE_URL"],
        "types": {"PORT": "int"},
        "defaults": {
            "DATABASE_URL": "postgres://localhost/db"
        }
    }

    v = EnvValidator(str(env_file), schema)
    res = v.run_all()

    db_result = next((r for r in res if r.key == "DATABASE_URL"), None)
    assert db_result is not None
    assert db_result.status == "warning", "Empty required var with default should be WARNING"
    assert db_result.line is None, "Missing/empty required vars should have line=None (show as ?)"


def test_multiple_missing_vars_correct_status(tmp_path):
    """Test multiple missing variables with mixed default availability."""
    env_file = tmp_path / ".env"
    write_env(["PORT=8000"], env_file)

    schema = {
        "required": ["DATABASE_URL", "SECRET_KEY", "API_KEY"],
        "defaults": {
            "DATABASE_URL": "sqlite:///:memory:",
            "API_KEY": "default-key"
        }
    }

    v = EnvValidator(str(env_file), schema)
    res = v.run_all()

    # DATABASE_URL and API_KEY have defaults -> WARNING
    db_result = next((r for r in res if r.key == "DATABASE_URL"), None)
    assert db_result is not None
    assert db_result.status == "warning", "DATABASE_URL with default should be WARNING"

    api_result = next((r for r in res if r.key == "API_KEY"), None)
    assert api_result is not None
    assert api_result.status == "warning", "API_KEY with default should be WARNING"

    # SECRET_KEY has no default -> ERROR
    secret_result = next((r for r in res if r.key == "SECRET_KEY"), None)
    assert secret_result is not None
    assert secret_result.status == "error", "SECRET_KEY without default should be ERROR"


def test_all_missing_vars_show_question_mark_location(tmp_path):
    """All missing/empty required variables should show line=None (displays as ?)."""
    env_file = tmp_path / ".env"
    write_env([
        "PORT=8000",
        "SECRET_KEY=",  # Empty on line 2
        "# Comment",
        "DEBUG=true"
    ], env_file)

    schema = {
        "required": ["DATABASE_URL", "SECRET_KEY", "API_KEY"],
        "defaults": {
            "API_KEY": "test"
        }
    }

    v = EnvValidator(str(env_file), schema)
    res = v.run_all()

    # DATABASE_URL doesn't exist -> line should be None
    db_result = next((r for r in res if r.key == "DATABASE_URL"), None)
    assert db_result is not None
    assert db_result.line is None, "Non-existent key should have line=None"

    # SECRET_KEY exists but is empty on line 2 -> line should still be None for missing vars
    secret_result = next((r for r in res if r.key == "SECRET_KEY"), None)
    assert secret_result is not None
    assert secret_result.line is None, "Empty required key should have line=None"

    # API_KEY doesn't exist -> line should be None
    api_result = next((r for r in res if r.key == "API_KEY"), None)
    assert api_result is not None
    assert api_result.line is None, "Non-existent key should have line=None"


def test_validation_errors_show_actual_line_numbers(tmp_path):
    """Non-missing validation errors should show actual line numbers."""
    env_file = tmp_path / ".env"
    write_env([
        "DATABASE_URL=postgres://localhost/db",  # Line 1
        "PORT=abc",  # Line 2 - invalid int
        "DEBUG=True",  # Line 3 - forbidden
        "EMAIL=bad@email"  # Line 4 - invalid pattern
    ], env_file)

    schema = {
        "types": {
            "PORT": "int",
            "EMAIL": "email"
        },
        "forbidden": ["DEBUG=True"]
    }

    v = EnvValidator(str(env_file), schema)
    res = v.run_all()

    # PORT validation error should have line number 2
    port_result = next((r for r in res if r.key == "PORT" and r.status == "error"), None)
    assert port_result is not None
    assert port_result.line == 2, "PORT error should show actual line number"

    # DEBUG forbidden error should have line number 3
    debug_result = next((r for r in res if r.key == "DEBUG" and r.status == "error"), None)
    assert debug_result is not None
    assert debug_result.line == 3, "DEBUG error should show actual line number"

    # EMAIL pattern error should have line number 4
    email_result = next((r for r in res if r.key == "EMAIL" and r.status == "error"), None)
    assert email_result is not None
    assert email_result.line == 4, "EMAIL error should show actual line number"


def test_ok_results_show_line_numbers(tmp_path):
    """Valid variables should show their actual line numbers."""
    env_file = tmp_path / ".env"
    write_env([
        "PORT=8000",  # Line 1
        "DEBUG=false",  # Line 2
        "EMAIL=test@example.com"  # Line 3
    ], env_file)

    schema = {
        "types": {
            "PORT": "int",
            "DEBUG": "bool",
            "EMAIL": "email"
        }
    }

    v = EnvValidator(str(env_file), schema)
    res = v.run_all()

    # All should be OK with their line numbers
    port_result = next((r for r in res if r.key == "PORT"), None)
    assert port_result is not None
    assert port_result.status == "ok"
    assert port_result.line == 1

    debug_result = next((r for r in res if r.key == "DEBUG"), None)
    assert debug_result is not None
    assert debug_result.status == "ok"
    assert debug_result.line == 2

    email_result = next((r for r in res if r.key == "EMAIL"), None)
    assert email_result is not None
    assert email_result.status == "ok"
    assert email_result.line == 3


def test_secret_with_default_is_warning(tmp_path):
    """Missing secret variable with default should be WARNING."""
    env_file = tmp_path / ".env"
    write_env(["PORT=8000"], env_file)

    schema = {
        "required": ["SECRET_KEY"],
        "secrets": ["SECRET_KEY"],
        "defaults": {
            "SECRET_KEY": "default-secret"
        }
    }

    v = EnvValidator(str(env_file), schema)
    res = v.run_all()

    secret_result = next((r for r in res if r.key == "SECRET_KEY"), None)
    assert secret_result is not None
    assert secret_result.status == "warning", "Missing secret with default should be WARNING"
    assert secret_result.secret is True, "Should be marked as secret"
    assert secret_result.suggestion is not None


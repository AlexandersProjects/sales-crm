# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


from typer.testing import CliRunner
from env_guard import cli


runner = CliRunner()


def test_suggest_writes_file(tmp_path):
    env = tmp_path / ".env"
    env.write_text("PORT=8000\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("required:\n  - PORT\n")
    out = tmp_path / ".env.suggested"

    # invoke suggest via CliRunner
    result = runner.invoke(cli.app, ["suggest", "--env-file", str(env), "--schema-file", str(schema), "--out-file", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_check_exitcodes(tmp_path):
    env = tmp_path / ".env"
    env.write_text("DEBUG=true\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("required:\n  - DATABASE_URL\n")

    # run check -> should exit with code 1 (error)
    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--json"])
    assert result.exit_code == 1

    # make missing required have default -> should produce warning (exit 2)
    schema.write_text("required:\n  - DATABASE_URL\ndefaults:\n  DATABASE_URL: \"sqlite:///:memory:\"\n")
    result2 = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--json"])
    assert result2.exit_code == 2


def test_check_env_file_option(tmp_path):
    """Test that --env-file option works correctly."""
    env = tmp_path / ".env"
    env.write_text("PORT=8000\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("required:\n  - PORT\ntypes:\n  PORT: int\n")

    # Test with --env-file flag
    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--json"])
    assert result.exit_code == 0
    assert "PORT" in result.stdout


def test_check_env_file_option_with_custom_name(tmp_path):
    """Test --env-file with a non-standard filename."""
    env = tmp_path / "custom.env"
    env.write_text("DEBUG=false\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("types:\n  DEBUG: bool\n")

    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--json"])
    assert result.exit_code == 0


def test_check_defaults_to_dotenv(tmp_path):
    """Test that check defaults to .env when no file specified."""
    env = tmp_path / ".env"
    env.write_text("PORT=8000\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("required:\n  - PORT\n")

    # Change to tmp_path and run without specifying env file
    import os
    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(cli.app, ["check", "--schema-file", str(schema), "--json"])
        assert result.exit_code == 0
    finally:
        os.chdir(old_cwd)


def test_check_warning_output_format(tmp_path):
    """Test that warnings are displayed with yellow color in non-JSON output."""
    env = tmp_path / ".env"
    env.write_text("PORT=8000\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("required:\n  - DATABASE_URL\ndefaults:\n  DATABASE_URL: \"sqlite:///:memory:\"\n")

    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema)])
    assert result.exit_code == 2  # warnings exit with code 2
    assert "WARNING" in result.stdout or "warning" in result.stdout.lower()
    assert "DATABASE_URL" in result.stdout


def test_check_error_output_format(tmp_path):
    """Test that errors are displayed with red color in non-JSON output."""
    env = tmp_path / ".env"
    env.write_text("PORT=abc\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("types:\n  PORT: int\n")

    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema)])
    assert result.exit_code == 1  # errors exit with code 1
    assert "ERROR" in result.stdout or "error" in result.stdout.lower()
    assert "PORT" in result.stdout


def test_check_location_format_for_missing(tmp_path):
    """Test that missing variables show ? in location."""
    env = tmp_path / ".env"
    env.write_text("PORT=8000\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("required:\n  - DATABASE_URL\n  - SECRET_KEY\n")

    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema)])
    assert result.exit_code == 1
    # Both missing vars should show with ?
    # Check using JSON output for easier parsing
    result_json = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--json"])
    import json
    data = json.loads(result_json.stdout)
    db_result = next((r for r in data if r["key"] == "DATABASE_URL"), None)
    secret_result = next((r for r in data if r["key"] == "SECRET_KEY"), None)
    assert db_result is not None
    assert secret_result is not None
    assert db_result["line"] is None  # None means it will show as ?
    assert secret_result["line"] is None  # None means it will show as ?


def test_check_location_format_for_validation_errors(tmp_path):
    """Test that validation errors show actual line numbers."""
    env = tmp_path / ".env"
    env.write_text("PORT=abc\nDEBUG=True\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("types:\n  PORT: int\nforbidden:\n  - DEBUG=True\n")

    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--json"])
    assert result.exit_code == 1
    # Should show actual line numbers (not None)
    import json
    data = json.loads(result.stdout)
    port_result = next((r for r in data if r["key"] == "PORT"), None)
    debug_result = next((r for r in data if r["key"] == "DEBUG"), None)
    assert port_result is not None
    assert debug_result is not None
    assert port_result["line"] == 1  # PORT on line 1
    assert debug_result["line"] == 2  # DEBUG on line 2


def test_check_json_output_structure(tmp_path):
    """Test JSON output contains correct structure."""
    env = tmp_path / ".env"
    env.write_text("PORT=8000\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("required:\n  - PORT\n  - DATABASE_URL\ndefaults:\n  DATABASE_URL: \"test\"\n")

    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--json"])
    import json

    # Debug: print raw output if parsing fails
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Output: {repr(result.stdout)}")
        raise

    assert isinstance(data, list)
    assert len(data) > 0

    # Check structure of results
    for item in data:
        assert "key" in item
        assert "status" in item
        assert "message" in item

    # Find the warning result
    warning_result = next((r for r in data if r["status"] == "warning"), None)
    assert warning_result is not None
    assert warning_result["key"] == "DATABASE_URL"


def test_check_yaml_output(tmp_path):
    """Test YAML output works."""
    env = tmp_path / ".env"
    env.write_text("PORT=8000\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("required:\n  - PORT\n")

    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--yaml"])
    assert result.exit_code == 0
    assert "PORT" in result.stdout
    assert "key:" in result.stdout or "- key" in result.stdout


def test_check_show_secrets_flag(tmp_path):
    """Test that --show-secrets reveals secret values."""
    env = tmp_path / ".env"
    env.write_text("SECRET_KEY=topsecret\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("required:\n  - SECRET_KEY\nsecrets:\n  - SECRET_KEY\n")

    # Without --show-secrets, should show **** (need --show-ok to see it in table)
    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--show-ok"])
    assert "****" in result.stdout
    assert "topsecret" not in result.stdout

    # With --show-secrets, should show actual value
    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--show-secrets", "--show-ok"])
    assert "topsecret" in result.stdout


def test_check_strict_mode(tmp_path):
    """Test that --strict mode reports unknown variables as errors."""
    env = tmp_path / ".env"
    env.write_text("PORT=8000\nUNKNOWN_VAR=test\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("required:\n  - PORT\n")

    # Without strict, should pass
    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--json"])
    assert result.exit_code == 0

    # With strict, should error on unknown var
    result = runner.invoke(cli.app, ["check", "--env-file", str(env), "--schema-file", str(schema), "--strict", "--json"])
    assert result.exit_code == 1
    assert "UNKNOWN_VAR" in result.stdout


def test_check_profile_option(tmp_path):
    """Test --profile option for multi-environment files."""
    env_prod = tmp_path / ".env.production"
    env_prod.write_text("PORT=443\n")
    schema = tmp_path / "rules.schema.yaml"
    schema.write_text("required:\n  - PORT\ntypes:\n  PORT: int\n")

    result = runner.invoke(cli.app, ["check", "--env-file", str(tmp_path / ".env"), "--profile", "production", "--schema-file", str(schema), "--json"])
    # Should look for .env.production
    assert result.exit_code == 0
    assert "PORT" in result.stdout



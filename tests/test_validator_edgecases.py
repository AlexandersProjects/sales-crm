# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

from pathlib import Path
import re
from env_guard.validator import EnvValidator
from typer.testing import CliRunner
from env_guard import cli

runner = CliRunner()


def write_env(lines, path):
    p = Path(path)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_ip_octet_bounds(tmp_path):
    env = tmp_path / ".env"
    # invalid octet
    write_env(["HOST=256.0.0.1"], env)
    schema = {"types": {"HOST": "ip"}}
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    assert any(r.key == "HOST" and r.status == "error" for r in res)

    # valid
    write_env(["HOST=255.255.255.255"], env)
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    assert any(r.key == "HOST" and r.status == "ok" for r in res)


def test_url_validation(tmp_path):
    env = tmp_path / ".env"
    write_env(["ENDPOINT=example.com/path"], env)
    schema = {"types": {"ENDPOINT": "url"}}
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    assert any(r.key == "ENDPOINT" and r.status == "error" for r in res)

    write_env(["ENDPOINT=https://example.com:8080/path"], env)
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    assert any(r.key == "ENDPOINT" and r.status == "ok" for r in res)


def test_semver(tmp_path):
    env = tmp_path / ".env"
    write_env(["VER=1.2.3"], env)
    schema = {"types": {"VER": "semver"}}
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    assert any(r.key == "VER" and r.status == "ok" for r in res)

    write_env(["VER=1.2"], env)
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    assert any(r.key == "VER" and r.status == "error" for r in res)


def test_float_parsing(tmp_path):
    env = tmp_path / ".env"
    write_env(["F=1.234"], env)
    schema = {"types": {"F": "float"}}
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    assert any(r.key == "F" and r.status == "ok" for r in res)

    write_env(["F=nan"], env)
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    assert any(r.key == "F" and r.status == "error" for r in res)


def test_malformed_line_and_line_numbers(tmp_path):
    env = tmp_path / ".env"
    # include a malformed line without '=' on line 2
    p = Path(env)
    p.write_text("GOOD=1\nBROKENLINE\nANOTHER=2\n", encoding='utf-8')
    schema = {"required": ["BROKENLINE"]}
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    # find BROKENLINE result - it's missing/malformed, so line should be None (shows as ?)
    r = next((r for r in res if r.key == "BROKENLINE"), None)
    assert r is not None
    # Missing required vars always show line=None, even if there's a malformed line
    assert r.line is None


def test_duplicate_keys_last_wins(tmp_path):
    env = tmp_path / ".env"
    write_env(["PORT=8000", "PORT=9000"], env)
    schema = {"types": {"PORT": {"type": "int", "min": 1, "max": 65535}}}
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    # PORT should be ok and take last value 9000
    r = next((r for r in res if r.key == "PORT"), None)
    assert r is not None
    assert r.found == "9000"


def test_required_if_not_triggered(tmp_path):
    env = tmp_path / ".env"
    write_env(["ENV=staging"], env)
    schema = {"required": [], "required_if": {"ENV": {"value": "production", "required": ["SENTRY_DSN"]}}}
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    # SENTRY_DSN should not be required here
    assert not any(r.key == "SENTRY_DSN" and r.status == "error" for r in res)


def test_suggest_defaults_and_secret_safe(tmp_path):
    # ensure suggest respects safe_mode for secrets
    env = tmp_path / ".env"
    env.write_text("", encoding='utf-8')
    schema = tmp_path / "rules.schema.yaml"
    # defaults with a secret value
    schema.write_text('required:\n  - SECRET_KEY\ndefaults:\n  SECRET_KEY: "topsecret"\nsecrets:\n  - SECRET_KEY\n', encoding='utf-8')
    out = tmp_path / ".env.suggested"

    # run suggest without show-secrets (safe_mode True) -> secret placeholder should be empty
    result = runner.invoke(cli.app, ["suggest", "--env-file", str(env), "--schema-file", str(schema), "--out-file", str(out)])
    assert result.exit_code == 0
    txt = out.read_text(encoding='utf-8')
    assert re.search(r"^SECRET_KEY=\s*$", txt, flags=re.M)

    # run suggest with --show-secrets -> secret value should be present
    out2 = tmp_path / ".env.suggested2"
    result2 = runner.invoke(cli.app, ["suggest", "--env-file", str(env), "--schema-file", str(schema), "--out-file", str(out2), "--show-secrets"])
    assert result2.exit_code == 0
    txt2 = out2.read_text(encoding='utf-8')
    assert "SECRET_KEY=topsecret" in txt2


def test_to_yaml_redaction(tmp_path):
    env = tmp_path / ".env"
    write_env(["SECRET_KEY=topsecret"], env)
    schema = {"required": ["SECRET_KEY"], "types": {"SECRET_KEY": "str"}, "secrets": ["SECRET_KEY"]}
    v = EnvValidator(str(env), schema)
    v.run_all()
    y = v.to_yaml(show_secrets=False)
    assert "****" in y or "found: \"****\"" in y

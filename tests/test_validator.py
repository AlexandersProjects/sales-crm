# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

from pathlib import Path
from env_guard.validator import EnvValidator


def write_env(lines, path):
    # lines: list[str], path: Path-like or str
    p = Path(path)
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def test_validator_happy_path(tmp_path):
    env_file = tmp_path / ".env"
    write_env(["PORT=8000", "DEBUG=false", "SUPPORT_EMAIL=foo@example.com"], env_file)
    schema = {
        "required": ["PORT"],
        "types": {"PORT": {"type": "int", "min": 1, "max": 65535}, "DEBUG": "bool", "SUPPORT_EMAIL": "email"},
    }
    v = EnvValidator(str(env_file), schema)
    res = v.run_all()
    statuses = {r.key: r.status for r in res}
    assert statuses["PORT"] == "ok"
    assert statuses["DEBUG"] == "ok"
    assert statuses["SUPPORT_EMAIL"] == "ok"


def test_validator_missing_required(tmp_path):
    env_file = tmp_path / ".env"
    write_env(["DEBUG=true"], env_file)
    schema = {"required": ["DATABASE_URL"], "types": {"DEBUG": "bool"}}
    v = EnvValidator(str(env_file), schema)
    res = v.run_all()
    assert any(r.status == "error" and r.key == "DATABASE_URL" for r in res)


def test_bool_parsing(tmp_path):
    env_file = tmp_path / ".env"
    write_env(["FLAG=Yes", "FLAG2=no"], env_file)
    schema = {"types": {"FLAG": "bool", "FLAG2": "bool"}}
    v = EnvValidator(str(env_file), schema)
    res = v.run_all()
    # both flags should be OK
    assert any(r.key == "FLAG" and r.status == "ok" for r in res)
    assert any(r.key == "FLAG2" and r.status == "ok" for r in res)


def test_strict_unknown(tmp_path):
    env_file = tmp_path / ".env"
    write_env(["EXTRA=1"], env_file)
    schema = {"required": [], "types": {}}
    v = EnvValidator(str(env_file), schema, strict=True)
    res = v.run_all()
    assert any(r.status == "error" and "Unknown variable" in r.message for r in res)


# --- additional tests ---

def test_pattern_mismatch(tmp_path):
    env = tmp_path / ".env"
    write_env(["EMAIL=not-an-email"], env)
    schema = {"types": {"EMAIL": "email"}}
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    assert any(r.key == "EMAIL" and r.status == "error" for r in res)


def test_forbidden_value(tmp_path):
    env = tmp_path / ".env"
    write_env(["DEBUG=True"], env)
    schema = {"forbidden": ["DEBUG=True"]}
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    assert any(r.key == "DEBUG" and r.status == "error" for r in res)


def test_required_if(tmp_path):
    env = tmp_path / ".env"
    write_env(["ENV=production"], env)
    schema = {"required": [], "required_if": {"ENV": {"value": "production", "required": ["SENTRY_DSN"]}}}
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    assert any(r.key == "SENTRY_DSN" and r.status == "error" for r in res)


def test_secret_redaction_in_json(tmp_path):
    env = tmp_path / ".env"
    write_env(["SECRET_KEY=topsecret"], env)
    schema = {"required": ["SECRET_KEY"], "types": {"SECRET_KEY": "str"}, "secrets": ["SECRET_KEY"]}
    v = EnvValidator(str(env), schema)
    res = v.run_all()
    secret_res = next((r for r in res if r.key == "SECRET_KEY"), None)
    assert secret_res is not None
    j = v.to_json(show_secrets=False)
    assert '"found": "****"' in j or '"****"' in j

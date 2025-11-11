# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# validation logic

from typing import Dict, List, Optional, Tuple, Any, Set
import re
import json
from pathlib import Path
import math

# simple helper regexes
EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
IPV4_RE = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
URL_RE = re.compile(r"^https?://[\w\.-]+(:\d+)?(/.*)?$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+].+)?$")


class ValidationResult:
    def __init__(self, key: str, status: str, message: str, *, suggestion: Optional[str] = None,
                 found: Optional[str] = None, expected: Optional[str] = None,
                 file: Optional[str] = None, line: Optional[int] = None, secret: bool = False):
        self.key = key
        self.status = status  # 'ok', 'warning', 'error'
        self.message = message
        self.suggestion = suggestion
        self.found = found
        self.expected = expected
        self.file = file
        self.line = line
        self.secret = secret

    def to_dict(self, show_secrets: bool = False) -> Dict[str, Any]:
        found = self.found
        if self.secret and not show_secrets and found is not None:
            found = "****"
        return {
            "key": self.key,
            "status": self.status,
            "message": self.message,
            "suggestion": self.suggestion,
            "found": found,
            "expected": self.expected,
            "file": self.file,
            "line": self.line,
        }


class EnvValidator:
    """Validates a .env file against a (simple) schema.

    Supported schema keys:
      - required: [VAR1, VAR2]
      - types: { VAR: "int" } or { VAR: {type: "int", min:..., max:...} }
      - patterns: { VAR: "regex" }
      - forbidden: ["KEY=VAL"]
      - secrets: [VAR1]
      - defaults: { VAR: "value" }
      - required_if: { VAR: {value: "x", required: ["OTHER"]} }
    """

    def __init__(self, env_path: str, schema: Dict[str, Any], *, show_secrets: bool = False, strict: bool = False, profile: Optional[str] = None):
        self.env_path = env_path
        # normalize schema to a dict to help typing
        self.schema: Dict[str, Any] = schema or {}
        self.show_secrets = show_secrets
        self.strict = strict
        self.profile = profile

        # parsed env: key -> (value, line_no)
        self.env: Dict[str, Tuple[Optional[str], int]] = {}
        self._load_env()

        self.results: List[ValidationResult] = []

    def _load_env(self) -> None:
        path = Path(self.env_path)
        if not path.exists():
            return
        with path.open("r", encoding="utf-8") as f:
            for idx, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    key = line
                    self.env[key] = (None, idx)
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                self.env[k] = (v, idx)

    def _get_known_keys(self) -> Set[str]:
        keys: Set[str] = set()
        keys.update(self.schema.get("required", []) or [])
        types = self.schema.get("types", {}) or {}
        keys.update(types.keys())
        keys.update((self.schema.get("patterns", {}) or {}).keys())
        keys.update((self.schema.get("defaults", {}) or {}).keys())
        keys.update((self.schema.get("secrets", []) or []))
        for f in (self.schema.get("forbidden", []) or []):
            if isinstance(f, str) and "=" in f:
                keys.add(f.split("=", 1)[0])
        for k, cond in (self.schema.get("required_if", {}) or {}).items():
            keys.add(k)
            for r in cond.get("required", []):
                keys.add(r)
        return keys

    def _parse_bool(self, val: str) -> Optional[bool]:
        if val is None:
            return None
        v = val.strip().lower()
        if v in ("1", "true", "yes", "y", "on"):
            return True
        if v in ("0", "false", "no", "n", "off"):
            return False
        return None

    def _is_int(self, val: str) -> bool:
        try:
            int(val)
            return True
        except Exception:
            return False

    def _is_float(self, val: str) -> bool:
        try:
            f = float(val)
            return math.isfinite(f)
        except Exception:
            return False

    def _check_pattern(self, key: str, pattern: str, value: Optional[str]) -> Optional[ValidationResult]:
        if value is None:
            return ValidationResult(key, "error", f"Variable {key} has no value", found=None, expected=f"pattern {pattern}")
        if not re.match(pattern, value):
            return ValidationResult(key, "error", f"{key} does not match pattern: {pattern}", found=value, expected=f"pattern {pattern}")
        return None

    def _check_type(self, key: str, tdef: Any, value: Optional[str]) -> Optional[ValidationResult]:
        tname: Optional[str]
        extras: Dict[str, Any]
        if isinstance(tdef, str):
            tname = tdef
            extras = {}
        elif isinstance(tdef, dict):
            tname = tdef.get("type")
            extras = tdef
        else:
            return ValidationResult(key, "warning", f"Unknown type definition for {key}", found=value)

        # If value is missing or empty, don't duplicate the "missing required" error here.
        # Required/empty presence is checked separately in run_all(). For optional keys, skip type checks when no value present.
        if value is None or value == "":
            return None

        # Treat plain string types as valid (no-op). Accept 'str' and 'string'.
        if isinstance(tname, str) and tname.lower() in ("str", "string"):
            return None

        if tname == "int":
            if value is None or not self._is_int(value):
                return ValidationResult(key, "error", f"{key} should be an integer", suggestion="Provide an integer, e.g. 123", found=value, expected="int")
            ival = int(value)
            minv = extras.get("min") if isinstance(extras, dict) else None
            maxv = extras.get("max") if isinstance(extras, dict) else None
            if minv is not None:
                try:
                    if ival < int(minv):
                        return ValidationResult(key, "error", f"{key} < min {minv}", suggestion=f"Use a value >= {minv}", found=value, expected=f"int >= {minv}")
                except Exception:
                    pass
            if maxv is not None:
                try:
                    if ival > int(maxv):
                        return ValidationResult(key, "error", f"{key} > max {maxv}", suggestion=f"Use a value <= {maxv}", found=value, expected=f"int <= {maxv}")
                except Exception:
                    pass
            return None

        if tname == "float":
            if value is None or not self._is_float(value):
                return ValidationResult(key, "error", f"{key} should be a float", suggestion="Provide a float like 1.23", found=value, expected="float")
            return None

        if tname == "bool":
            b = self._parse_bool(value) if value is not None else None
            if b is None:
                return ValidationResult(key, "error", f"{key} should be a boolean (true/false/1/0/yes/no)", suggestion="Use true/false or 1/0", found=value, expected="bool")
            return None

        if tname == "email":
            if value is None or not EMAIL_RE.match(value):
                return ValidationResult(key, "error", f"{key} should be a valid email", suggestion="example@example.com", found=value, expected="email")
            return None

        if tname == "ip":
            if value is None or not IPV4_RE.match(value):
                return ValidationResult(key, "error", f"{key} should be an IPv4 address", suggestion="127.0.0.1", found=value, expected="ipv4")
            parts = value.split(".")
            try:
                if any(not (0 <= int(p) <= 255) for p in parts):
                    return ValidationResult(key, "error", f"{key} has invalid IPv4 octets", suggestion="Use 0-255 per octet", found=value, expected="ipv4")
            except Exception:
                return ValidationResult(key, "error", f"{key} has invalid IPv4 octets", suggestion="Use 0-255 per octet", found=value, expected="ipv4")
            return None

        if tname == "url":
            if value is None or not URL_RE.match(value):
                return ValidationResult(key, "error", f"{key} should be a valid URL (http/https)", suggestion="https://example.com", found=value, expected="url")
            return None

        if tname == "semver":
            if value is None or not SEMVER_RE.match(value):
                return ValidationResult(key, "error", f"{key} should be a semantic version (MAJOR.MINOR.PATCH)", suggestion="1.2.3", found=value, expected="semver")
            return None

        return ValidationResult(key, "warning", f"Unknown type '{tname}' for {key}", found=value, expected=tname)

    def run_all(self) -> List[ValidationResult]:
        path = Path(self.env_path)
        if not path.exists():
            self.results.append(ValidationResult(".env", "error", f"Env file not found: {self.env_path}", file=str(path), line=None))
            return self.results

        known_keys = self._get_known_keys()

        # required checks
        for key in self.schema.get("required", []) or []:
            # determine if key exists in parsed env and get line number
            val_line = self.env.get(key, (None, None))
            val_present = key in self.env
            val_is_empty = val_line[0] in (None, "")
            if (not val_present) or val_is_empty:
                default = (self.schema.get("defaults", {}) or {}).get(key)
                # Always use None for missing/empty required vars so they show as "?" in location
                line_no = None
                if default is not None:
                    msg = f"Missing required variable: {key} (default available)"
                    suggestion = f"Use default: {default}"
                    self.results.append(ValidationResult(key, "warning", msg, suggestion=suggestion, found=None, expected="required", file=self.env_path, line=line_no, secret=(key in (self.schema.get("secrets", []) or []))))
                else:
                    self.results.append(ValidationResult(key, "error", f"Missing required variable: {key}", found=None, expected="required", file=self.env_path, line=line_no, secret=(key in (self.schema.get("secrets", []) or []))))

        # required_if
        for key, cond in (self.schema.get("required_if", {}) or {}).items():
            cond_val = cond.get("value")
            required_list = cond.get("required", [])
            actual = self.env.get(key, (None, None))[0]
            if actual == cond_val:
                for r in required_list:
                    if r not in self.env or self.env[r][0] in (None, ""):
                        self.results.append(ValidationResult(r, "error", f"{r} is required when {key}={cond_val}", found=None, expected=f"required_if {key}={cond_val}", file=self.env_path, line=None))

        # types
        for key, t in (self.schema.get("types", {}) or {}).items():
            val_line = self.env.get(key, (None, None))
            val_opt = val_line[0]
            line_opt = val_line[1]
            res = self._check_type(key, t, val_opt)
            if res:
                res.file = self.env_path
                res.line = line_opt
                res.secret = key in (self.schema.get("secrets", []) or [])
                self.results.append(res)

        # patterns
        for key, pattern in (self.schema.get("patterns", {}) or {}).items():
            val_line = self.env.get(key, (None, None))
            val_opt = val_line[0]
            line_opt = val_line[1]
            res = self._check_pattern(key, pattern, val_opt)
            if res:
                res.file = self.env_path
                res.line = line_opt
                res.secret = key in (self.schema.get("secrets", []) or [])
                self.results.append(res)

        # forbidden
        for forbidden in (self.schema.get("forbidden", []) or []):
            if isinstance(forbidden, str) and "=" in forbidden:
                k, v = forbidden.split("=", 1)
                val_forbidden = self.env.get(k, (None, None))[0]
                if val_forbidden == v:
                    line_forbidden = self.env.get(k, (None, None))[1]
                    found_val = val_forbidden if val_forbidden is not None else ""
                    self.results.append(ValidationResult(k, "error", f"Forbidden value: {k}={v}", found=found_val, expected=f"not {v}", file=self.env_path, line=line_forbidden, secret=(k in (self.schema.get("secrets", []) or []))))

        # unknown keys when strict
        if self.strict:
            for k, val_tuple in self.env.items():
                if k not in known_keys:
                    self.results.append(ValidationResult(k, "error", f"Unknown variable (strict mode): {k}", found=val_tuple[0], file=self.env_path, line=val_tuple[1]))

        # final OK entries: keys that had no errors/warnings -> report ok
        problematic = {r.key for r in self.results}
        for k, val_tuple in self.env.items():
            if k in problematic:
                continue
            self.results.append(ValidationResult(k, "ok", "OK", found=val_tuple[0], expected=None, file=self.env_path, line=val_tuple[1], secret=(k in (self.schema.get("secrets", []) or []))))

        return self.results

    def to_json(self, show_secrets: bool = False) -> str:
        return json.dumps([r.to_dict(show_secrets=show_secrets) for r in self.results], ensure_ascii=False, indent=2)

    def to_yaml(self, show_secrets: bool = False) -> str:
        try:
            import yaml  # type: ignore
        except Exception:
            raise
        # mypy: yaml is dynamically typed without stubs; keep return type as str
        return str(yaml.safe_dump([r.to_dict(show_secrets=show_secrets) for r in self.results], sort_keys=False))

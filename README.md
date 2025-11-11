# env-guard

A robust CLI tool for validating `.env` files against schema rules to catch missing secrets, invalid types, and unsafe defaults before they cause production issues.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Commands](#cli-commands)
- [Schema Configuration](#schema-configuration)
- [Supported Types](#supported-types)
- [Examples](#examples)
- [Telemetry](#telemetry)
- [Community & Feedback](#community--feedback)
- [API Reference](#api-reference)
- [Development](#development)
- [License](#license)

## ✨ Features

- **Type Validation**: Supports `int`, `float`, `bool`, `string`, `email`, `ip`, `url`, `semver`
- **Pattern Matching**: Custom regex patterns for environment variables
- **Required Fields**: Enforce presence of critical configuration
- **Conditional Requirements**: `required_if` - require fields based on other field values
- **Forbidden Values**: Block dangerous or deprecated values
- **Secret Redaction**: Automatically hide sensitive values in output
- **Default Values**: Suggest or apply defaults for missing variables
- **Strict Mode**: Flag unknown environment variables
- **Auto-fix**: Automatically apply simple fixes (boolean normalization, defaults, etc.)
- **Multiple Output Formats**: Human-readable tables, JSON, or YAML
- **Git Integration**: Detect uncommitted changes before applying fixes
- **Profile Support**: Validate different environments (dev, staging, prod)

## 📦 Installation

### For usage:

```bash
python -m pip install env_guard
```
Or with dotenv support:
```bash
python -m pip install env_guard[dotenv]
```

### For development:

```bash
python -m pip install -e .[dev,dotenv]
```

## 🚀 Quick Start

### Initialize from Template

```bash
# Create .env from example.env template
env-guard init

# Interactive mode - prompts for each value
env-guard init --interactive
```

### Basic Validation

```bash
# Validate default .env file
env-guard check

# Validate specific file and schema
env-guard check --env-file .env.production --schema-file rules.schema.yaml
```

### Exit Codes

- **0**: OK (no errors)
- **1**: Validation errors present
- **2**: Usage/runtime errors or warnings-only (configurable)

## 🛠️ CLI Commands

### `check` - Validate Environment Files

Validate a `.env` file against schema rules.

```bash
env-guard check [OPTIONS]
```

#### Options:

| Option | Default | Description |
|--------|---------|-------------|
| `--env-file` | `.env` | Path to environment file |
| `--schema-file`, `--schema` | `rules.schema.yaml` | Path to schema file |
| `--json` | `False` | Output results as JSON |
| `--yaml` | `False` | Output results as YAML |
| `--show-secrets` | `False` | Show secret values in output (unsafe) |
| `--safe-mode` | `True` | Avoid exposing secrets and sensitive suggestions |
| `--strict` | `False` | Unknown env vars are errors |
| `--show-ok` | `False` | Show OK entries in table output |
| `--highlight` | `True` | Highlight rows by status (green/yellow/red) |
| `--fix` | `False` | Automatically apply simple fixes |
| `--dry-run` | `True` | Preview fixes without writing (with `--fix`) |
| `--backup` | `True` | Create backup as .bak (with `--fix`) |
| `--profile` | `None` | Profile name for multi-env files |

#### Examples:

```bash
# Basic validation
env-guard check

# Validate with strict mode (unknown vars are errors)
env-guard check --strict

# Output as JSON for CI/CD integration
env-guard check --json

# Show all variables including OK ones
env-guard check --show-ok

# Validate production profile
env-guard check --env-file .env --profile production

# Preview automatic fixes
env-guard check --fix

# Apply fixes with backup
env-guard check --fix --dry-run=false
```

### `suggest` - Generate Suggestions

Generate a suggested `.env` file with fixes and defaults applied.

```bash
env-guard suggest [OPTIONS]
```

#### Options:

| Option | Default | Description |
|--------|---------|-------------|
| `--env-file` | `.env` | Path to source environment file |
| `--schema-file`, `--schema` | `rules.schema.yaml` | Path to schema file |
| `--out-file` | `.env.suggested` | Path for output file |
| `--show-secrets` | `False` | Include secret values in suggestions |
| `--safe-mode` | `True` | Don't write secrets to suggested file |

#### Examples:

```bash
# Generate suggested .env file
env-guard suggest

# Output to custom file
env-guard suggest --out-file .env.new

# Include secrets (use with caution)
env-guard suggest --show-secrets --safe-mode=false
```

### `init` - Initialize from Template

Create a `.env` file from `example.env` template.

```bash
env-guard init [OPTIONS]
```

#### Options:

| Option | Default | Description |
|--------|---------|-------------|
| `--example-file` | `example.env` | Template file path |
| `--out-file` | `.env` | Output file path |
| `--interactive`, `-i` | `False` | Prompt for each value |
| `--overwrite` | `False` | Overwrite existing file |
| `--keep-comments` | `True` | Preserve comments |
| `--schema-file` | `None` | Validate after creation |

#### Examples:

```bash
# Basic initialization
env-guard init

# Interactive mode
env-guard init --interactive

# Custom files
env-guard init --example-file .env.template --out-file .env.local

# With validation
env-guard init --schema-file rules.schema.yaml

# Overwrite existing file
env-guard init --overwrite

# Without comments
env-guard init --no-comments
```

## 📝 Schema Configuration

Create a `rules.schema.yaml` file to define validation rules:

```yaml
# Required environment variables
required:
  - DATABASE_URL
  - SECRET_KEY
  - PORT
  - DEBUG

# Type definitions
types:
  PORT:
    type: int
    min: 1
    max: 65535
  DEBUG: bool
  SECRET_KEY: string
  DATABASE_URL: url
  ADMIN_EMAIL: email
  SERVER_IP: ip
  APP_VERSION: semver
  MAX_CONNECTIONS:
    type: int
    min: 1
    max: 1000

# Custom regex patterns
patterns:
  API_KEY: "^[A-Za-z0-9]{32}$"
  PHONE: "^\\+?[0-9]{10,15}$"

# Forbidden values (e.g., dangerous defaults)
forbidden:
  - DEBUG=True
  - SECRET_KEY=changeme
  - DATABASE_URL=sqlite:///:memory:

# Secret variables (will be redacted in output)
secrets:
  - SECRET_KEY
  - API_KEY
  - DATABASE_PASSWORD

# Default values for missing variables
defaults:
  PORT: "8000"
  DEBUG: "false"
  MAX_CONNECTIONS: "100"

# Conditional requirements
required_if:
  ENV:
    value: "production"
    required:
      - SENTRY_DSN
      - SSL_CERT_PATH
  DATABASE_TYPE:
    value: "postgres"
    required:
      - DATABASE_HOST
      - DATABASE_PORT
```

## 🔍 Supported Types

### Basic Types

| Type | Description | Example |
|------|-------------|---------|
| `string` / `str` | Any text value | `"hello world"` |
| `int` | Integer with optional min/max | `42`, `8000` |
| `float` | Floating-point number | `3.14`, `1.0` |
| `bool` | Boolean (true/false, yes/no, 1/0, on/off) | `true`, `false` |

### Specialized Types

| Type | Description | Example |
|------|-------------|---------|
| `email` | Valid email address | `user@example.com` |
| `ip` | IPv4 address | `192.168.1.1` |
| `url` | HTTP/HTTPS URL | `https://example.com:8080/path` |
| `semver` | Semantic version (MAJOR.MINOR.PATCH) | `1.2.3`, `2.0.0-beta` |

### Type Options

For `int` and `float` types, you can specify constraints:

```yaml
types:
  PORT:
    type: int
    min: 1024
    max: 65535
  TIMEOUT:
    type: float
    min: 0.1
    max: 300.0
```

## 📚 Examples

### Example 1: Valid Configuration

**`.env`**:
```dotenv
DATABASE_URL=postgres://localhost/mydb
SECRET_KEY=super-secret-key-here
PORT=5432
DEBUG=false
ADMIN_EMAIL=admin@example.com
APP_VERSION=1.2.3
```

**`rules.schema.yaml`**:
```yaml
required:
  - DATABASE_URL
  - SECRET_KEY
  - PORT

types:
  PORT: int
  DEBUG: bool
  ADMIN_EMAIL: email
  APP_VERSION: semver

secrets:
  - SECRET_KEY
```

**Result**: ✅ All checks pass

### Example 2: Invalid Configuration

**`.env`**:
```dotenv
DATABASE_URL=postgres://localhost/db
SECRET_KEY=
PORT=abc
DEBUG=True
EMAIL=not-an-email
```

**Issues Detected**:
- ❌ `SECRET_KEY` is empty (required)
- ❌ `PORT` should be int, got "abc"
- ❌ `DEBUG=True` is forbidden
- ❌ `EMAIL` is invalid email format

### Example 3: Conditional Requirements

**`.env`**:
```dotenv
ENV=production
DATABASE_URL=postgres://localhost/db
```

**`rules.schema.yaml`**:
```yaml
required:
  - ENV
  - DATABASE_URL

required_if:
  ENV:
    value: production
    required:
      - SENTRY_DSN
      - SSL_CERT_PATH
```

**Result**: ❌ Missing `SENTRY_DSN` and `SSL_CERT_PATH` (required when ENV=production)

### Example 4: Initialize from Template

**`example.env`**:
```dotenv
# Database Configuration
DATABASE_URL=your-database-url-here
DATABASE_PORT=5432

# Application Settings
APP_NAME=MyApp
DEBUG=false
SECRET_KEY=your-secret-key-here
```

**Command**:
```bash
env-guard init --interactive
```

**Interactive Prompts**:
```
Enter value for DATABASE_URL [your-database-url-here]: postgres://localhost/mydb
Enter value for DATABASE_PORT [5432]: ⏎
Enter value for APP_NAME [MyApp]: ProductionApp
Enter value for DEBUG [false]: ⏎
Enter value for SECRET_KEY [your-secret-key-here]: super-secret-production-key
```

**Result**: ✅ Created `.env` with user-provided values

## 🔧 API Reference

### Core Classes

#### `EnvValidator`

Main validation engine for environment files.

```python
from env_guard.validator import EnvValidator

validator = EnvValidator(
    env_path: str,              # Path to .env file
    schema: Dict[str, Any],     # Schema dictionary
    show_secrets: bool = False, # Show secret values
    strict: bool = False,       # Strict mode (unknown vars = error)
    profile: Optional[str] = None  # Profile name
)

# Run all validations
results: List[ValidationResult] = validator.run_all()

# Export results
json_output = validator.to_json(show_secrets=False)
yaml_output = validator.to_yaml(show_secrets=False)
```

#### `ValidationResult`

Represents a single validation result.

```python
class ValidationResult:
    key: str              # Environment variable name
    status: str           # 'ok', 'warning', or 'error'
    message: str          # Human-readable message
    suggestion: Optional[str]  # Suggested fix
    found: Optional[str]  # Actual value found
    expected: Optional[str]    # Expected value/type
    file: Optional[str]   # File path
    line: Optional[int]   # Line number
    secret: bool          # Is this a secret?
    
    def to_dict(self, show_secrets: bool = False) -> Dict[str, Any]:
        """Convert to dictionary (secrets redacted if show_secrets=False)"""
```

#### `load_schema`

Load and parse a YAML schema file.

```python
from env_guard.schema_loader import load_schema

schema: Dict[str, Any] = load_schema(path: str)
```

### CLI Entry Point

```python
from env_guard.cli import main

# Programmatic CLI usage
exit_code: int = main(argv: Optional[List[str]] = None)
```

## 🔄 Using the CLI

After installation, you can run the tool in multiple ways:

### 1. Installed Console Script (Recommended)

```bash
# Activate venv (bash)
.\.venv\Scripts\Activate.ps1

# Run (either name works)
env-guard check --env-file .env --schema-file rules.schema.yaml
# or
env_guard check --env-file .env --schema-file rules.schema.yaml
```

### 2. Direct Path (No venv activation needed)

```bash
.\.venv\Scripts\env_guard.exe check --env-file .env --schema-file rules.schema.yaml
```

### 3. Python Module (Always works)

```bash
python -m env_guard.cli check --env-file .env --schema-file rules.schema.yaml
```

## 📊 Telemetry

env_guard includes **optional, anonymous telemetry** to help improve the tool by understanding usage patterns and effectiveness.

### Privacy-First Approach

- 🔒 **Opt-in by default** - Disabled unless you explicitly enable it
- 🔐 **Anonymous** - No personal information, file paths, or secrets collected
- 📖 **Transparent** - All telemetry code is open source
- ✅ **Optional** - Works perfectly without it

### What's Collected (When Enabled)

- Command usage (check, suggest, init)
- Number of findings by type and severity
- Runtime performance metrics
- Estimated time saved

### What's NOT Collected

- ❌ No file paths or names
- ❌ No environment variable names or values
- ❌ No secrets or sensitive data
- ❌ No PII (personally identifiable information)

### Enable Telemetry

```bash
# Install telemetry support
pip install env_guard[telemetry]

# Enable via environment variable
export ENV_GUARD_TELEMETRY=true

# Run commands as normal
env-guard check
```

### Per-Command Opt-Out

```bash
# Disable for a single run
env-guard check --no-telemetry
```

📚 **Learn more:** See [docs/TELEMETRY.md](docs/TELEMETRY.md) for complete documentation.

## 💬 Community & Feedback

**If this saved you time, tell me on X — I collect real stories from developers to keep improving.**

Found a bug? Caught an issue before production? Saved hours of debugging? I'd love to hear about it!

- 🐦 **Twitter/X:** [@ActiveDadAlex](https://x.com/ActiveDadAlex)
- 📧 **Email:** alexander@elementalwebvisions.com
- 🐛 **Issues:** [GitHub Issues](https://github.com/yourusername/env_guard/issues)
- ⭐ **Star the repo** if you find it useful!

Your feedback helps me understand what's working and what needs improvement. Real-world usage stories are incredibly valuable for prioritizing features and improvements.

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd env_guard

# Install with dev dependencies
python -m pip install -e .[dev]
```

### Run Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=env_guard --cov-report=html

# Run specific test file
python -m pytest tests/test_validator.py

# Run with verbose output
python -m pytest -v
```

### Linting and Type Checking

```bash
# Run ruff linter
ruff check .

# Run mypy type checker
mypy env_guard

# Auto-fix with ruff
ruff check --fix .
```

### Install pre-commit Hooks

#### 1. Install pre-commit
```bash
pip install pre-commit
```

#### 2. .pre-commit-config.yaml
```yaml
repos:
  - repo: local
    hooks:
      - id: env-guard
        name: Validate .env files
        entry: env-guard check --strict
        language: system
        files: ^\.env.*$
        pass_filenames: false

```

#### 3. Enable hooks
```bash
pre-commit install
```

#### 4. Run manually
```bash
pre-commit run --all-files
```

#### 5.1 Test the functionality manually (suggested for the first test)
```bash
# run manually all hooks against all files
pre-commit run --all-files
```

```bash
# test env-guard hook only
pre-commit run env-guard --all-files
```

#### 5.2 Test the functionality with a simulated commit

```bash
# simulate a commit
git add .env
git commit -m "Test commit"  # hook will run automatically
```

```bash
# reset the commit after the failed simulated commit
git reset HEAD~1
```
or
```bash
# reset the commit and reroll all changes after the failed simulated commit
git reset --hard HEAD~1
```

### Building and Publishing

```bash
# Install build tools
python -m pip install --upgrade build twine

# Build distributions
python -m build

# Check distribution
python -m twine check dist/*

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

### Release Scripts

```bash
# Cross-platform release script
python scripts\release.py --skip-checks

# bash release script
.\scripts\release.ps1
```

## 🔐 Security Best Practices

1. **Never commit secrets**: Use `.gitignore` to exclude `.env` files
2. **Use safe-mode**: Keep `--safe-mode` enabled (default) to prevent secret leakage
3. **Redact in CI/CD**: Always use `--safe-mode` in automated environments
4. **Validate before deploy**: Run `env-guard check` in your deployment pipeline
5. **Use profiles**: Separate configs for dev, staging, production

## 🌐 CI/CD Integration

### GitHub Actions Example

```yaml
name: Validate Environment

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install env_guard
      - run: env-guard check --json --strict
```

### GitLab CI Example

```yaml
validate:env:
  stage: test
  script:
    - pip install env_guard
    - env-guard check --json --strict
  only:
    changes:
      - .env*
      - rules.schema.yaml
```

## 📄 Project Structure

```
env_guard/
├── env_guard/
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # CLI commands (check, suggest)
│   ├── validator.py       # Validation logic and types
│   └── schema_loader.py   # YAML schema loading
├── tests/
│   ├── test_validator.py          # Core validator tests
│   ├── test_validator_edgecases.py # Edge case tests
│   └── test_cli_integration.py    # CLI integration tests
├── scripts/
│   ├── release.py         # Release automation
│   └── release.ps1        # bash release script
├── pyproject.toml         # Project metadata and dependencies
├── rules.schema.yaml      # Example schema file
├── LICENSE                # Apache 2.0 License
├── NOTICE                 # Attribution notices
└── README.md              # This file
```

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `pytest`
2. Code is linted: `ruff check .`
3. Type checking passes: `mypy env_guard`
4. Add tests for new features
5. Update documentation

## 🪪 License

This project is licensed under the [Apache License 2.0](./LICENSE).

Copyright © 2025 Alexander Blaschko-Schänzer

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## 📞 Contact

For questions, issues, or suggestions:
- **Issues**: [GitHub Issues](https://github.com/AlexandersProjects/env_guard/issues)

---

**Made with ❤️ to make environment configuration safer and more reliable.**


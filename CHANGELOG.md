# Changelog

All notable changes to env-guard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-10-29

### Added
- Initial release of env-guard
- Core validation engine with comprehensive type support
  - Type validation: `int`, `float`, `bool`, `string`, `email`, `ip`, `url`, `semver`
  - Pattern matching with regex support
  - Required field enforcement
  - Conditional requirements (`required_if`)
  - Forbidden value blocking
  - Default value suggestions
- CLI commands:
  - `check` - Validate .env files against schema rules
  - `suggest` - Generate suggested fixes
  - `init` - Initialize .env from template files
- Features:
  - Secret redaction for sensitive values
  - Strict mode for unknown variables
  - Auto-fix functionality with dry-run mode
  - Multiple output formats (table, JSON, YAML)
  - Git integration to detect uncommitted changes
  - Profile support for multi-environment validation
  - Interactive mode for template initialization
- Rich terminal output:
  - Colored status indicators
  - Table formatting
  - Progress feedback
  - Emoji support for visual clarity
- Pre-commit hook integration
- Comprehensive test suite (40 tests, 100% passing)
- Apache 2.0 license
- Complete documentation in README.md

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- Safe mode enabled by default to prevent secret exposure
- Secret redaction in all output modes
- Permission error handling

## [0.0.1] - Development

### Added
- Initial development version
- Core validation logic
- Basic CLI structure

---

## Release Notes

### v0.1.0 - First Public Release

This is the first public release of env-guard, a professional CLI tool for validating `.env` files against schema rules. The tool is production-ready and has been thoroughly tested with comprehensive test coverage.

**Key Features:**
- ✅ Comprehensive type validation
- ✅ Schema-based configuration validation
- ✅ Secret management and redaction
- ✅ Auto-fix capabilities
- ✅ Multiple output formats
- ✅ Pre-commit hook support
- ✅ Interactive template initialization

**Installation:**
```bash
pip install env_guard
```

**Quick Start:**
```bash
# Validate your .env file
env-guard check

# Initialize from template
env-guard init

# Get suggestions for fixes
env-guard suggest
```

See README.md for complete documentation.

---

[Unreleased]: https://github.com/yourusername/env_guard/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/env_guard/releases/tag/v0.1.0
[0.0.1]: https://github.com/yourusername/env_guard/releases/tag/v0.0.1


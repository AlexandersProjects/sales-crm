# Contributing to env-guard

Thank you for your interest in contributing to env-guard! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## 📜 Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## 🤝 How Can I Contribute?

### Reporting Bugs

Before submitting a bug report:
1. Check the [issue tracker](https://github.com/yourusername/env_guard/issues) for existing reports
2. Verify the bug with the latest version
3. Collect relevant information (OS, Python version, error messages)

When reporting a bug, include:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Environment details (Python version, OS, etc.)
- Any relevant logs or error messages

### Suggesting Features

Feature requests are welcome! Please:
1. Check if the feature has already been requested
2. Provide a clear use case
3. Explain why it would be useful to most users
4. Consider offering to implement it yourself

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Ensure all tests pass
6. Update documentation
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 🛠️ Development Setup

### Prerequisites

- Python 3.9 or higher
- pip
- git

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/env_guard.git
   cd env_guard
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   
   **Windows:**
   ```bash
   .venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source .venv/bin/activate
   ```

4. **Install development dependencies:**
   ```bash
   pip install -e .[dev,dotenv]
   ```

5. **Verify installation:**
   ```bash
   env-guard --help
   pytest tests/
   ```

### Project Structure

```
env_guard/
├── env_guard/          # Main package
│   ├── __init__.py
│   ├── cli.py         # CLI commands
│   ├── init.py        # Template initialization
│   ├── schema_loader.py  # Schema loading
│   └── validator.py   # Core validation logic
├── tests/             # Test suite
├── docs/              # Documentation
├── pyproject.toml     # Package configuration
└── README.md          # User documentation
```

## 📐 Coding Standards

### Style Guide

This project follows:
- **PEP 8** for Python code style
- **Type hints** for all function signatures
- **Docstrings** for all public functions and classes

### Linting

We use `ruff` for linting:

```bash
# Check code
ruff check env_guard/ tests/

# Auto-fix issues
ruff check env_guard/ tests/ --fix
```

### Type Checking

We use `mypy` for type checking:

```bash
mypy env_guard/ --ignore-missing-imports
```

### Code Formatting

While not enforced, we recommend:
- **Line length**: 120 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Organized and alphabetized
- **Strings**: Double quotes for user-facing strings

### Best Practices

- Keep functions focused and single-purpose
- Use descriptive variable and function names
- Add comments for complex logic
- Prefer composition over inheritance
- Handle errors gracefully with informative messages

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_validator.py

# Run specific test
pytest tests/test_validator.py::test_validator_happy_path

# Run with coverage
pytest tests/ --cov=env_guard --cov-report=html
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Include docstrings explaining what is tested
- Aim for high code coverage (>80%)

Example test structure:

```python
def test_feature_name():
    """Test that feature works correctly with valid input."""
    # Arrange
    input_data = "test"
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

### Test Categories

- **Unit tests**: Test individual functions
- **Integration tests**: Test component interactions
- **CLI tests**: Test command-line interface
- **Edge case tests**: Test boundary conditions

## 📝 Submitting Changes

### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(cli): add --exclude-pattern option for template files

fix(validator): handle None values in forbidden value checks

docs(readme): update installation instructions

test(init): add tests for interactive mode
```

### Pull Request Process

1. **Update documentation**: Ensure README.md and docstrings are current
2. **Add tests**: Include tests for new features or bug fixes
3. **Update CHANGELOG.md**: Add entry under "Unreleased" section
4. **Ensure tests pass**: All tests must pass before merging
5. **Code review**: Address any feedback from reviewers
6. **Squash commits**: Consider squashing commits for cleaner history

### Review Criteria

Pull requests will be reviewed for:
- ✅ Code quality and style
- ✅ Test coverage
- ✅ Documentation completeness
- ✅ Backward compatibility
- ✅ Performance impact
- ✅ Security implications

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
- OS: [e.g., Windows 11, macOS 14, Ubuntu 22.04]
- Python version: [e.g., 3.11.5]
- env-guard version: [e.g., 0.1.0]

**Additional context**
Any other relevant information.
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Describe the problem.

**Describe the solution you'd like**
Clear description of what you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features.

**Additional context**
Any other context or screenshots.
```

## 📚 Additional Resources

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## 🙏 Recognition

Contributors will be recognized in:
- Project README.md
- Release notes
- GitHub contributors page

Thank you for helping make env-guard better! 🎉


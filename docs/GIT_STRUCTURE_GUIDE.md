# Git Repository Structure Guide

## ✅ Files to INCLUDE in Git

### Documentation
```
✅ docs/*.md                  # All markdown documentation
✅ README.md                  # Project readme
✅ CHANGELOG.md               # Version history
✅ CONTRIBUTING.md            # Contribution guidelines
✅ LICENSE                    # Apache 2.0 license
✅ NOTICE                     # Copyright notice
```

### Source Code
```
✅ env_guard/**/*.py          # All Python source files
✅ tests/**/*.py              # All test files
✅ scripts/*.py               # Release scripts
✅ scripts/*.ps1              # PowerShell scripts
```

### Configuration
```
✅ pyproject.toml             # Package configuration
✅ mypy.ini                   # Type checking config
✅ rules.schema.yaml          # Example schema
✅ schema.yml                 # Example schema
✅ example.env                # Template file
✅ .gitignore                 # This file!
```

### Pre-commit (if using)
```
✅ .pre-commit-config.yaml    # Pre-commit hooks config
```

---

## ❌ Files to EXCLUDE from Git

### Environment Files
```
❌ .env                       # Never commit actual .env!
❌ .env.local                 # Local overrides
❌ .env.production           # Production secrets
❌ .env.staging              # Staging secrets
❌ .env.*.local              # Any local env files
❌ .env.test*                # Test env files
❌ .env.suggested            # Generated suggestions
```

### Temporary Files
```
❌ tmp_*/                    # Temporary directories
❌ tmp_*.py                  # Temporary Python files
❌ tmp_*.env                 # Temporary env files
❌ *.tmp                     # Generic temp files
❌ *.bak                     # Backup files
❌ *~                        # Editor backups
```

### Python Generated Files
```
❌ __pycache__/              # Python cache
❌ *.pyc                     # Compiled Python
❌ *.pyo                     # Optimized Python
❌ *.pyd                     # Python DLL
❌ .pytest_cache/            # Pytest cache
❌ .mypy_cache/              # Mypy cache
❌ .ruff_cache/              # Ruff cache
```

### Build Artifacts
```
❌ build/                    # Build directory
❌ dist/                     # Distribution directory
❌ *.egg-info/               # Egg metadata
❌ .eggs/                    # Eggs directory
```

### Virtual Environments
```
❌ .venv/                    # Virtual environment
❌ venv/                     # Alternative venv name
❌ ENV/                      # Another venv name
```

### IDE Files
```
❌ .vscode/                  # VS Code settings
❌ .idea/                    # PyCharm settings
❌ *.code-workspace          # VS Code workspace
```

### Coverage & Reports
```
❌ .coverage                 # Coverage data
❌ htmlcov/                  # Coverage HTML report
❌ coverage.xml              # Coverage XML report
❌ junit-*.xml               # JUnit reports
```

---

## 🤔 Current Debate: docs/ Folder

### ✅ RECOMMENDED: Include docs/

**Reasons to include:**
- 📚 Professional documentation
- 🎯 Shows development process
- 🔍 Helps contributors understand decisions
- 📈 Can be used for GitHub Pages
- ✨ Demonstrates quality and thoroughness

**Current docs/ contents:**
```
docs/
├── BUG_FIX_SUMMARY.md              ✅ Keep - explains pre-commit fix
├── PUBLICATION_READINESS_ASSESSMENT.md  🤔 Optional - detailed analysis
└── FINAL_PUBLICATION_STATUS.md     🤔 Optional - status report
```

### Options:

**Option 1: Keep All (Recommended)** ✅
- Shows professionalism
- Transparent development process
- Useful for future reference

**Option 2: Keep Only User-Facing Docs**
- Keep: BUG_FIX_SUMMARY.md
- Archive or delete: Assessment and status reports

**Option 3: Move Internal Docs to Archive**
```
docs/
├── BUG_FIX_SUMMARY.md              # Public
└── archive/                        # Internal (gitignored)
    ├── PUBLICATION_READINESS_ASSESSMENT.md
    └── FINAL_PUBLICATION_STATUS.md
```

---

## 📋 Quick Check Commands

### See what's being tracked:
```bash
git ls-files
```

### See what would be ignored:
```bash
git status --ignored
```

### See untracked files:
```bash
git status -u
```

### Check specific file:
```bash
git check-ignore -v path/to/file
```

### List all ignored files:
```bash
git ls-files --others --ignored --exclude-standard
```

---

## 🎯 Recommended Action for docs/

**Include the docs/ folder** but consider organizing it better:

```
docs/
├── README.md                       # Overview of documentation
├── guides/                         # User guides
│   └── getting-started.md
├── development/                    # Developer docs
│   ├── BUG_FIX_SUMMARY.md
│   └── architecture.md
└── archive/                        # Historical (optional, gitignored)
    ├── PUBLICATION_READINESS_ASSESSMENT.md
    └── FINAL_PUBLICATION_STATUS.md
```

Then add to `.gitignore`:
```gitignore
# Archive internal development docs (optional)
docs/archive/
```

This way:
- ✅ Important fixes are documented (BUG_FIX_SUMMARY.md)
- ✅ Project looks professional
- ❌ Internal analysis reports don't clutter the repo
- 🔄 You can still access them locally

---

## 🎉 Final Recommendation

**Include docs/** - Professional open source projects have good documentation.

If you want to keep it clean:
1. Move assessment reports to `docs/archive/`
2. Add `docs/archive/` to `.gitignore`
3. Keep BUG_FIX_SUMMARY.md in `docs/development/`
4. Commit everything else

This shows professionalism while keeping internal analysis private.


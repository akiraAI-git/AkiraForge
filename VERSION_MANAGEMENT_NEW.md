# 📦 Version Branch Management System

This directory uses a semantic versioning system with Git branches to track releases.

## Branch Structure with Stability Levels

Versions now include stability classification:

- **1.1(stable)** - Original release branch (stable)
- **1.1.2(stable)** - First patch release (production-ready)
- **1.1.3(experimental)** - Second release (testing/beta)
- **1.1.4(unstable)** - Development release (unstable)
- ... continues ...
- **1.1.9(stable)** - Last stable patch for minor version 1.1
- **1.2(experimental)** - Next minor version (beta)

### Stability Levels

| Level | Purpose | Use When |
|-------|---------|----------|
| **(stable)** | Production-ready | Feature complete, tested, ready for users |
| **(experimental)** | Beta/testing | New features being tested, feedback wanted |
| **(unstable)** | Development | Work in progress, not ready for general use |

## Creating a New Version Branch

### Interactive Mode (Recommended)
```bash
python create_version_branch.py
```
This opens an interactive menu where you can:
1. Create the next auto-calculated version
2. Create a custom version
3. List all existing versions
4. Choose stability level: (stable), (experimental), or (unstable)

### Command Line Mode

**Show next version:**
```bash
python create_version_branch.py next
```

**Create next version:**
```bash
# You'll be asked to choose stability
python create_version_branch.py create

# Or specify stability directly
python create_version_branch.py create stable
python create_version_branch.py create experimental
python create_version_branch.py create unstable
```

**Create custom version:**
```bash
# You'll be asked to choose stability
python create_version_branch.py create-custom 1.2.5

# Or specify stability directly
python create_version_branch.py create-custom 1.2.5 stable
python create_version_branch.py create-custom 1.2.5 experimental
```

**List all versions:**
```bash
python create_version_branch.py list
```

## What the Script Does

1. ✅ Detects the latest version branch
2. ✅ Calculates the next version (1.1 → 1.1.2 → 1.1.3 → 1.2)
3. ✅ Asks for stability level: (stable), (experimental), or (unstable)
4. ✅ Creates a new branch with the version name and stability
5. ✅ Updates `VERSION` file with stability
6. ✅ Updates `core/__version__.py` with stability info
7. ✅ Commits version changes
8. ✅ Prints push instructions

## Files Not Pushed to GitHub

The following files are ignored in `.gitignore`:
- `test_*.py` - All test files
- `tests/` - Test directory
- `validate_*.py` - Validation scripts
- `verify_*.py` - Verification scripts
- `*_test.py` - Any test files

## Accessing Version Info in Code

```python
from core.__version__ import __version__, __version_number__, __stability__

print(__version__)          # "1.1.2(stable)"
print(__version_number__)   # "1.1.2"
print(__stability__)        # "stable"
```

## Workflow Example

1. You're on the `1.1(stable)` branch with latest code
2. Run: `python create_version_branch.py`
3. Choose option 1 (auto version)
4. Choose stability (stable, experimental, or unstable)
5. Script creates branch `1.1.2(experimental)` with updated version files
6. Script automatically commits: `Release version 1.1.2(experimental)`
7. Push to GitHub: `git push -u origin 1.1.2(experimental)`
8. Create a pull request to merge into main repository

## Notes

- **create_version_branch.py** is NOT in `.gitignore` - it's a developer tool
- Version files (VERSION, __version__.py) ARE committed to each branch
- Stability level is part of the version identifier
- Test files are ignored by git and won't be pushed

---
Last Updated: April 27, 2026

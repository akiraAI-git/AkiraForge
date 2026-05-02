# 📦 Version Branch Management System

This directory uses a semantic versioning system with Git branches to track releases.

## Branch Structure

- **1.1** - Original release branch (renamed from `main`)
- **1.1.2** - First patch release 
- **1.1.3** - Second patch release
- ... continues ...
- **1.1.9** - Last patch for minor version 1.1
- **1.2** - Next minor version
- etc.

## Creating a New Version Branch

### Interactive Mode (Recommended)
```bash
python create_version_branch.py
```
This opens an interactive menu where you can:
1. Create the next auto-calculated version
2. Create a custom version
3. List all existing versions

### Command Line Mode
```bash
# Show next version
python create_version_branch.py next

# Create the next version automatically
python create_version_branch.py create

# Create a custom version
python create_version_branch.py create-custom 1.2.5

# List all versions
python create_version_branch.py list
```

## What the Script Does

1. ✅ Detects the latest version branch
2. ✅ Calculates the next version (1.1 → 1.1.2 → 1.1.3 → 1.2)
3. ✅ Creates a new branch with the new version number
4. ✅ Updates `VERSION` file
5. ✅ Updates `core/__version__.py`
6. ✅ Commits version changes
7. ✅ Prints push instructions

## Files Not Pushed to GitHub

The following files are ignored in `.gitignore`:
- `test_*.py` - All test files
- `tests/` - Test directory
- `validate_*.py` - Validation scripts
- `verify_*.py` - Verification scripts
- `*_test.py` - Any test files

## Accessing Version Info in Code

```python
from core.__version__ import __version__, __version_info__

print(__version__)  # "1.1.2"
print(__version_info__)  # (1, 1, 2)
```

## Workflow Example

1. You're on the `1.1` branch with latest code
2. Run: `python create_version_branch.py`
3. Choose option 1 (auto version)
4. Script creates branch `1.1.2` with updated version files
5. Script automatically commits: `Release version 1.1.2`
6. Push to GitHub: `git push -u origin 1.1.2`
7. Create a pull request to merge into main repository

## Notes

- **create_version_branch.py** is NOT in `.gitignore` - it's a developer tool
- Version files (VERSION, __version__.py) ARE committed to each branch
- Test files are ignored by git and won't be pushed

---
Last Updated: April 27, 2026

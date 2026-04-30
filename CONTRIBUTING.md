# 🤝 Contributing to Akira Forge

Thank you for considering contributing to Akira Forge! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on ideas, not people
- Accept constructive criticism
- Help others learn and grow

## Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/AkiraForge.git
cd AkiraForge
git remote add upstream https://github.com/akiraAI-git/AkiraForge.git
```

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
# or
git checkout -b docs/documentation-update
```

### 3. Install Development Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # includes testing tools
```

### 4. Make Your Changes
- Write clean, readable code
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Add docstrings to functions

## Development Workflow

### Branch Naming Conventions
- `feature/user-authentication` - New features
- `fix/login-crash` - Bug fixes
- `docs/api-documentation` - Documentation updates
- `refactor/db-optimization` - Code refactoring
- `test/edge-case-coverage` - Test improvements

### Commit Messages

Follow semantic commit messages:

```
type: short description

Longer description explaining why this change was needed.

Fixes #123
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Code style (no logic change)
- `refactor:` - Code refactoring
- `test:` - Test improvements
- `chore:` - Build, dependencies, setup

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names

```python
# Good
def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user with credentials."""
    return login_manager.verify_credentials(username, password)

# Bad
def auth(u, p):
    return verify(u, p)
```

**Documentation:**
- Docstrings for all modules, classes, functions
- Docstring format: Google style
- Examples in docstrings when helpful

```python
def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Retrieve a user by their ID.
    
    Args:
        user_id: The unique identifier of the user.
    
    Returns:
        User object if found, None otherwise.
    
    Raises:
        ValueError: If user_id is not a positive integer.
        DatabaseError: If database connection fails.
    
    Example:
        >>> user = get_user_by_id(42)
        >>> print(user.username)
        john_doe
    """
```

## Testing

### Running Tests

```bash
# Run all tests
python tester_everything.py

# Run specific test category
python tester_everything.py --category authentication

# Run with verbose output
python tester_everything.py --verbose
```

### Writing Tests

- Aim for >80% code coverage
- Test happy path and edge cases
- Test error conditions
- Mock external dependencies

```python
def test_login_with_valid_credentials(self):
    """Test successful login with valid credentials."""
    result = login_manager.authenticate("user@example.com", "password123")
    self.assertTrue(result)

def test_login_with_invalid_credentials(self):
    """Test login failure with invalid credentials."""
    result = login_manager.authenticate("user@example.com", "wrongpass")
    self.assertFalse(result)

def test_login_with_empty_password(self):
    """Test login with missing password."""
    with self.assertRaises(ValueError):
        login_manager.authenticate("user@example.com", "")
```

## Pull Request Process

### Before Submitting

1. **Update master**
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```

2. **Run tests**
   ```bash
   python tester_everything.py
   ```

3. **Check code quality**
   ```bash
   python -m pylint core windows
   ```

### Submitting PR

1. Push to your fork
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open PR on GitHub with:
   - Clear title: `feat: Add feature description`
   - Detailed description of changes
   - Reference related issues: `Fixes #123`
   - Screenshots for UI changes
   - Test results output

3. PR Template:
   ```markdown
   ## Description
   Brief description of what this PR does.
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   How was this tested?
   - [ ] Unit tests added
   - [ ] Integration tests passed
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex logic
   - [ ] Documentation updated
   - [ ] No new warnings generated
   - [ ] Tests pass locally
   - [ ] Commits squashed where needed
   ```

### Review Process

1. Maintainers will review your code
2. Address feedback and make updates
3. Re-request review after changes
4. PR is merged once approved by 2+ maintainers

## Issues

### Reporting Bugs

Use the bug template:
```markdown
## Description
Clear description of the bug.

## Steps to Reproduce
1. Step 1
2. Step 2
3. ...

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: Windows 11
- Python: 3.11
- Version: 1.1.3(experimental)

## Error Message
```
Full error traceback
```
```

### Requesting Features

Use the feature template:
```markdown
## Description
Clear description of the feature.

## Motivation
Why is this needed?

## Proposed Solution
How should this work?

## Alternatives Considered
Other approaches?

## Additional Context
Any other information.
```

## Development Setup

### IDE Setup (JetBrains PyCharm)

1. Open project
2. Configure Python interpreter (3.10+)
3. Install inspection tools
4. Mark `core/` and `windows/` as sources root

### Database Setup (MySQL)

```bash
# Create database
CREATE DATABASE akiraforge;
CREATE USER 'forge_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON akiraforge.* TO 'forge_user'@'localhost';
FLUSH PRIVILEGES;

# Run migrations
python init_db_tables.py
```

## Documentation

### Updating Docs

1. Edit relevant .md file in repo root
2. Use clear, concise language
3. Include code examples
4. Keep API docs up-to-date

### Building Docs

```bash
# Install sphinx
pip install sphinx

# Build HTML docs
sphinx-build -b html docs docs/_build
```

## Performance Considerations

- Avoid N+1 database queries
- Cache frequently accessed data
- Use connection pooling
- Profile code for bottlenecks
- Optimize AI/LLM calls

## Security Considerations

- Never hardcode secrets
- Validate all user input
- Use parameterized queries
- Encrypt sensitive data
- Log security events
- Follow OWASP guidelines

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

## Getting Help

- **Questions**: Open a discussion or email support@akiraforge.local
- **Bugs**: Open an issue with bug template
- **Features**: Open an issue with feature template
- **Chat**: Join our Discord community (link TBD)

## Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- GitHub contributors graph
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Happy coding! 🚀

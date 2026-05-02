# GUI Integration Testing Suite

**IMPORTANT: These test files are NOT included in GitHub. They are for local development and testing only.**

## Files Overview

### `gui_integration_tester.py`
Comprehensive GUI integration testing that:
- Simulates real user interactions through the GUI
- Tests all accessible features at user level
- Validates backend responses
- Checks for password/secret leakage
- Logs all results for security audit
- Works with tester_everything.py for backend validation

### `run_complete_tests.py`
Master test runner that:
- Coordinates backend tests (tester_everything.py)
- Coordinates GUI tests (gui_integration_tester.py)
- Ensures no secrets are exposed in test output
- Generates comprehensive test report
- Saves results to ~/.akiraforge/integration_test_report.txt

## How to Run Tests

### Option 1: Run Complete Test Suite (Backend + GUI)
```bash
python USER_NOTES/run_complete_tests.py
```

This will:
1. Run all backend tests (tester_everything.py)
2. Run all GUI integration tests (gui_integration_tester.py)
3. Generate comprehensive report
4. Verify no secrets are leaked

### Option 2: Run Backend Tests Only
```bash
python tester_everything.py
```

### Option 3: Run GUI Tests Only
```bash
python USER_NOTES/gui_integration_tester.py
```

## Test Coverage

### GUI Tests
- **Login Flow**: Tests login window, authentication, secret checking
- **Home Screen**: Tests home screen navigation, UI security
- **Builder Features**: Tests AI project builder, configuration security
- **Data Access Controls**: Ensures user can only access own data
- **API Integration**: Tests API endpoints, key security
- **Workflow Automation**: Tests workflow engine functionality
- **Collaboration Features**: Tests workspace and team features
- **Visualization**: Tests chart and dashboard features
- **Search & Export**: Tests search engine and data export
- **Backend Scans**: Coordinates with tester_everything.py

### Security Checks Built-in
✓ No hardcoded passwords detected
✓ No API keys exposed
✓ No database credentials visible
✓ User data isolation verified
✓ Session security validated
✓ Encryption working correctly
✓ Audit logging functional
✓ Rate limiting operational

## Test Results

Results are saved to:
- `~/.akiraforge/gui_test_results.json` - Detailed JSON results
- `~/.akiraforge/gui_test.log` - Full test log
- `~/.akiraforge/integration_test_report.txt` - Summary report

## Important Security Notes

### What the Tests DO
- ✓ Simulate real user interactions
- ✓ Test all public features
- ✓ Validate data isolation
- ✓ Check for secret leakage
- ✓ Verify encryption
- ✓ Test error handling
- ✓ Validate permissions

### What the Tests DON'T Do
- ✗ Don't use real production database (uses test data)
- ✗ Don't store test passwords permanently
- ✗ Don't commit test results to GitHub
- ✗ Don't expose any real credentials
- ✗ Don't test real user accounts

### Password Usage in Tests
- Tests use temporary test accounts only
- Passwords are generated at runtime
- No passwords are hardcoded
- All test data is cleared after tests complete
- Logging sanitizes all sensitive data

## Troubleshooting

### "ImportError: No module named windows.login_window"
Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### "GUI tests skipped"
GUI tests require PyQt6/PySide6. Install:
```bash
pip install PyQt6
```

### "Database connection failed"
Tests can run without database (offline mode). Some features may be skipped.

### "Tests take too long"
- Backend tests: ~2-5 minutes
- GUI tests: ~5-10 minutes
- Complete suite: ~10-15 minutes total

## Adding New Tests

To add a new test:

1. Add method to `GUIIntegrationTester` class:
   ```python
   def test_my_feature(self) -> bool:
       """Test my new feature."""
       try:
           # Test code here
           self._log_result("test_name", "Category", True, "Success message")
           return True
       except Exception as e:
           self._log_result("test_name", "Category", False, str(e))
           return False
   ```

2. Add test to the `test_suites` list in `run_all_tests()`:
   ```python
   test_suites = [
       # ... existing tests ...
       ("My Feature", self.test_my_feature),
   ]
   ```

3. Run tests to verify:
   ```bash
   python USER_NOTES/gui_integration_tester.py
   ```

## GitHub Integration

**These test files are permanently excluded from GitHub** via `.gitignore`:
```
USER_NOTES/
REPORTS/
```

This is intentional because:
- Tests contain temporary credentials
- Results may contain sensitive diagnostics
- Test output is for local development only
- GitHub doesn't need test infrastructure files

## Running in CI/CD

If you want to run tests in GitHub Actions, create a new workflow:

1. Create `.github/workflows/test.yml`
2. Use `tester_everything.py` only (not GUI tests)
3. Don't include test results in artifacts
4. Focus on backend security validation

## Contact

For issues with tests:
- Check log files in ~/.akiraforge/
- Run with verbose output
- Review test source code
- Check GitHub issues for known problems

---

**Last Updated**: May 2, 2026
**Status**: Production Ready (Local Testing Only)

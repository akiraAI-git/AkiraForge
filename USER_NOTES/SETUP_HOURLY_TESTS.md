# Quick Setup - Hourly Test Monitoring

## 1. One-Time Setup

### Install Dependencies
```bash
pip install schedule sendgrid
```

### Configure SendGrid (Optional but Recommended)
```bash
# Windows PowerShell
$env:SENDGRID_API_KEY = "your_sendgrid_api_key"
$env:ADMIN_EMAIL = "your-admin@company.com"

# Or add to .env file in project root
SENDGRID_API_KEY=your_sendgrid_api_key
ADMIN_EMAIL=your-admin@company.com
```

## 2. Test It Once

```bash
python tester_everything.py
```

Expected output: ~33 passing tests

## 3. Enable Hourly Monitoring

### Option A: Run in Background (Windows)
```bash
# Create a batch file run_tests.bat
@echo off
:loop
python tester_everything.py
REM Wait 1 hour (3600 seconds)
timeout /t 3600
goto loop
```

Then run:
```bash
start run_tests.bat
```

### Option B: Use Scheduler (Windows Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily
4. Action: Run program `python tester_everything.py`
5. Advanced: Repeat every 1 hour

### Option C: Use schedule flag
```bash
python tester_everything.py --schedule
```
(Press Ctrl+C to stop)

## 4. What to Expect

### ✓ No Issues
```
[OK] Application is ready for use!
Email: NOT sent
```

### ✗ Issues Found
```
[FAIL] 3 TESTS FAILED
Email: Sent to admin@company.com with:
  - Issue location
  - Severity level
  - Whether it can be auto-fixed
```

### 🔌 Database Offline
```
[OFFLINE] Connection failed - OFFLINE MODE ACTIVATED
Email: NOT sent (no internet)
```

## 5. Email Alert Example

**If issues are detected:**

```
From: security@akiraforge.local
To: your-admin@company.com
Subject: Akira Forge - 2 Issues Detected

Issues Detected:
1. [ERROR] Security/Rate Limiting
   Description: Rate limiter failed to initialize
   Status: AUTO-FIXABLE

2. [WARNING] Performance/Query Speed
   Description: Database queries slow (250ms)
   Status: MANUAL FIX REQUIRED
```

## 6. Troubleshooting

### Email Not Sending
```bash
# Check API key is set
echo $env:SENDGRID_API_KEY

# Check admin email is set
echo $env:ADMIN_EMAIL

# Check database is online
python -c "from core.db import OFFLINE_MODE; print(f'Offline: {OFFLINE_MODE}')"
```

### Tests Failing

1. Check database connection:
   ```bash
   python -c "from core.db import get_db_connection; print('DB OK')"
   ```

2. Check imports work:
   ```bash
   python -c "from core.project_generator import ProjectGenerator; print('OK')"
   ```

3. Review test output carefully - read the [FAIL] messages

## 7. Disable/Enable Features

### Disable Emails Completely
```bash
python tester_everything.py --no-email
```

### Run Tests Without Waiting 1 Hour
```bash
python tester_everything.py
```

## 8. Monitor Your Tests

Create a simple Python script to review results:

```python
import subprocess
import datetime

while True:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] Running tests...")
    subprocess.run(["python", "tester_everything.py"])
    
    # Wait 1 hour
    import time
    time.sleep(3600)
```

## 9. Integration with CI/CD

If using GitHub Actions or similar CI/CD:

```yaml
name: Hourly Tests
on:
  schedule:
    - cron: '0 * * * *'  # Every hour

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        env:
          SENDGRID_API_KEY: ${{ secrets.SENDGRID_API_KEY }}
          ADMIN_EMAIL: ${{ secrets.ADMIN_EMAIL }}
        run: python tester_everything.py
```

## 10. File Locations

| Item | Location |
|------|----------|
| Main test file | `./tester_everything.py` |
| Config | `.env` or environment variables |
| Logs | Console output (no persistent log file) |
| Old tests | **DELETED** |

---

**Status:** ✓ Ready to use
**Last Updated:** April 29, 2026

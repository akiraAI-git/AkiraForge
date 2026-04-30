@echo off
REM Akira Forge - Terminal Testing Script
REM This script runs the app in terminal mode so you can see all errors

cd /d C:\akiraforge\DesktopAIApp

echo.
echo ========================================
echo   AKIRA FORGE - Terminal Testing
echo ========================================
echo.
echo Setting environment variables...

REM Set minimum required environment variables for testing
REM You can modify these values as needed

set DB_USER=forge_user
set DB_PASSWORD=048686mariadb
set DB_NAME=akira_forge
set HOME_DB_HOST=192.168.4.138
set OFFICE_DB_HOST=10.34.4.59
set SENDGRID_API_KEY=test

echo.
echo Starting app in terminal mode...
echo You will see all error messages below:
echo.
echo ========================================
echo.

REM Run the Python app
python -u main.py

echo.
echo ========================================
echo App exited. Check errors above.
echo ========================================
pause



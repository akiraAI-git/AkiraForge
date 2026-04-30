# Create a batch file run_tests.bat
@echo off
:loop
python tester_everything.py
REM Wait 1 hour (3600 seconds)
timeout /t 3600
goto loop
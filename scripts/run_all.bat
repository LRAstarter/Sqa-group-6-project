@echo off
rem Run all indexed tests and validate daily and terminal output using Python 3.
if "%~1"=="" (
    echo Usage: scripts\run_all.bat C:\path\to\frontend.exe
    exit /b 2
)
py -3 "%~dp0run_tests.py" "%~f1"
exit /b %errorlevel%

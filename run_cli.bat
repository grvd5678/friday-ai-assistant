@echo off
cd /d "%~dp0"
title F.R.I.D.A.Y. Terminal Mode
echo Starting F.R.I.D.A.Y. in CLI Terminal Mode...
set PYTHONIOENCODING=utf-8
.\venv\Scripts\python.exe main.py --cli
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [FRIDAY exited with an error code: %ERRORLEVEL%]
    pause
)

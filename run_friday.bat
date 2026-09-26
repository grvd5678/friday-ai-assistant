@echo off
title F.R.I.D.A.Y. AI Assistant
echo Starting F.R.I.D.A.Y. Holographic Tactical HUD...
set PYTHONIOENCODING=utf-8
.\venv\Scripts\python.exe main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [FRIDAY exited with an error code: %ERRORLEVEL%]
    pause
)

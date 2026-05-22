@echo off
REM JARVIS PC Agent - Windows Batch Start Script
REM Double-click this file to run the PC Agent
REM Or add to Startup folder for auto-start

echo.
echo ====================================
echo   JARVIS PC Agent Launcher
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8+ from https://www.python.org
    echo.
    pause
    exit /b 1
)

echo Python found!
echo.
echo Starting JARVIS PC Agent...
echo.

REM Run the agent
python "%~dp0jarvis_pc_agent.py"

pause

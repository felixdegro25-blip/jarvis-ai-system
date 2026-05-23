@echo off
echo.
echo ========================================
echo   JARVIS Local Server - Setup & Start
echo   Windows 10/11
echo ========================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo OK: Python found
echo.

REM Create virtual environment
echo Setting up Virtual Environment...
if not exist "venv" (
    python -m venv venv
    echo Created venv
)

echo.
echo Activating venv...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo Try running: pip install --upgrade pip setuptools wheel
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   JARVIS Server Starting...
echo   Chat:      http://localhost:5000/static/index.html
echo   Dashboard: http://localhost:5000/static/dashboard.html
echo   API Docs:  http://localhost:5000/docs
echo   Press Ctrl+C to stop
echo ========================================
echo.

REM Start server
python -m backend.app

pause

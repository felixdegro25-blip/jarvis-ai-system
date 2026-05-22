@echo off
REM 🚀 JARVIS Dashboard Setup & API Configuration
REM Automatische Installation und Konfiguration
REM
REM Diese Datei:
REM 1. Prüft Python Installation
REM 2. Installiert Abhängigkeiten
REM 3. Generiert API Keys
REM 4. Erstellt Konfigurationsdateien
REM 5. Startet JARVIS PC Server

echo.
echo ========================================
echo   🚀 JARVIS Dashboard Setup
echo   Automatische Konfiguration
echo ========================================
echo.

REM Prüfe Python
echo 👀 Prüfe Python Installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ FEHLER: Python nicht gefunden!
    echo    Bitte Python 3.10+ von https://www.python.org installieren
    echo    wähle "Add Python to PATH" während Installation!
    echo.
    pause
    exit /b 1
)

echo ✅ Python gefunden
echo.

REM Prüfe ob Skript im richtigen Verzeichnis ist
if not exist "pc_agent" (
    echo ⚠️  Warnung: pc_agent Verzeichnis nicht gefunden
    echo    Bitte das Skript aus dem Projekthauptverzeichnis starten
    pause
    exit /b 1
)

echo 🚀 Starte JARVIS Configuration Generator...
echo.

REM Starte Config Generator
python pc_agent\config_generator.py

if errorlevel 1 (
    echo.
    echo ❌ Fehler bei Konfiguration!
    pause
    exit /b 1
)

echo.
echo 🃋 Starte JARVIS PC Server...
echo.

REM Starte PC Server
if exist "jarvis_server.py" (
    python jarvis_server.py
) else if exist "pc_agent\jarvis_server.py" (
    python pc_agent\jarvis_server.py
) else (
    echo ❌ jarvis_server.py nicht gefunden!
    pause
    exit /b 1
)

pause

#!/bin/bash
# 🚀 JARVIS Dashboard Setup & API Configuration
# Automatische Installation und Konfiguration (Linux/Mac)

echo ""
echo "========================================"
echo "  🚀 JARVIS Dashboard Setup"
echo "  Automatische Konfiguration"
echo "========================================"
echo ""

# Prüfe Python
echo "👀 Prüfe Python Installation..."
if ! command -v python3 &> /dev/null
then
    echo ""
    echo "❌ FEHLER: Python 3 nicht gefunden!"
    echo "   Bitte Python 3.10+ installieren"
    echo "   Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "   macOS: brew install python3"
    echo ""
    exit 1
fi

echo "✅ Python gefunden"
echo ""

# Prüfe Verzeichnis
if [ ! -d "pc_agent" ]; then
    echo "⚠️  Warnung: pc_agent Verzeichnis nicht gefunden"
    echo "   Bitte das Skript aus dem Projekthauptverzeichnis starten"
    exit 1
fi

echo "🚀 Starte JARVIS Configuration Generator..."
echo ""

# Starte Config Generator
python3 pc_agent/config_generator.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Fehler bei Konfiguration!"
    exit 1
fi

echo ""
echo "🃋 Starte JARVIS PC Server..."
echo ""

# Starte PC Server
if [ -f "jarvis_server.py" ]; then
    python3 jarvis_server.py
elif [ -f "pc_agent/jarvis_server.py" ]; then
    python3 pc_agent/jarvis_server.py
else
    echo "❌ jarvis_server.py nicht gefunden!"
    exit 1
fi

#!/bin/bash
# JARVIS PC Agent - Linux/Mac Start Script
# Make executable: chmod +x jarvis_pc_agent.sh
# Run: ./jarvis_pc_agent.sh

echo ""
echo "===================================="
echo "  JARVIS PC Agent Launcher"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

echo "Python found!"
echo ""
echo "Starting JARVIS PC Agent..."
echo ""

# Run the agent
python3 "$(dirname "$0")/jarvis_pc_agent.py"

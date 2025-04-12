#!/bin/bash
# Enhanced BonziBuddy Launcher Script

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run BonziBuddy Enhanced Version
python3 fixed_bonzi.py

# Deactivate the virtual environment
deactivate
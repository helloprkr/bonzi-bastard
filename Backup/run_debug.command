#!/bin/bash
# Run the debug version of BonziBuddy with detailed logging

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    # Create a virtual environment if it doesn't exist
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Clear previous log file
if [ -f "bonzi_debug.log" ]; then
    echo "Clearing previous log file"
    > bonzi_debug.log
fi

# Run the debug version of BonziBuddy
echo "Starting debug version of BonziBuddy..."
echo "Log will be saved to bonzi_debug.log"
python debug_bonzi.py

# Open the log file at the end (for convenience)
echo "Opening log file in text editor..."
open -a TextEdit bonzi_debug.log
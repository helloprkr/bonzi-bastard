#!/bin/bash
# Run BonziBuddy from the command line

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

# Run BonziBuddy
python bonzi_buddy.py
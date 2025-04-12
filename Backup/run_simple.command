#!/bin/bash
# Run the simplified version of BonziBuddy which focuses on core functionality

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

# Run the simplified version of BonziBuddy
echo "Starting simple version of BonziBuddy..."
python simple_bonzi.py
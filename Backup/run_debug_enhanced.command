#!/bin/bash
# BonziBuddy Debug Launcher Script

# Change to the directory where the script is located
cd "$(dirname "$0")"

echo "=== BonziBuddy Debug Launcher ==="
echo "This script will launch BonziBuddy with detailed logging"
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not found. Please install Python 3."
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

# Run the API test first
echo "Testing Claude API connection..."
python3 test_claude_api.py
API_TEST_RESULT=$?

if [ $API_TEST_RESULT -ne 0 ]; then
    echo
    echo "WARNING: API test failed. BonziBuddy will run in offline mode."
    echo "Check your API key in config.yaml and internet connection."
    echo
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Create a log file
LOGFILE="bonzi_debug_$(date +%Y-%m-%d_%H-%M-%S).log"
echo "Logging to $LOGFILE"

# Run BonziBuddy with debugging output
echo "Starting BonziBuddy..."
echo "===== BonziBuddy Debug Log: $(date) =====" > $LOGFILE
echo "Python version: $(python3 --version)" >> $LOGFILE
echo "Pip packages:" >> $LOGFILE
pip list >> $LOGFILE
echo "===== BonziBuddy Output =====" >> $LOGFILE

# Run with output going to both terminal and log file
python3 -u fixed_bonzi.py 2>&1 | tee -a $LOGFILE

# Deactivate the virtual environment
deactivate

echo "BonziBuddy has exited. Log saved to $LOGFILE"
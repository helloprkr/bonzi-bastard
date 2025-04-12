#!/bin/bash
# BonziBuddy macOS Complete Installation Script
# This script handles the complete setup and installation of BonziBuddy for macOS

# Ensure script exits on any error
set -e

echo "==== BonziBuddy macOS Installer ===="
echo ""
echo "This script will install BonziBuddy as a standalone macOS application."
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 from python.org and try again."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
python3 -m pip install -r requirements.txt

# Check for Anthropic API key
CONFIG_FILE="config.yaml"
API_KEY=$(grep "anthropic_api_key" "$CONFIG_FILE" | cut -d '"' -f 2)

if [ -z "$API_KEY" ] || [ "$API_KEY" = '""' ]; then
    echo "Anthropic API key not found in config.yaml."
    echo "Please enter your Anthropic API key:"
    read -r API_KEY
    
    # Update the API key in config.yaml
    if [ -n "$API_KEY" ]; then
        sed -i '' "s/anthropic_api_key: \".*\"/anthropic_api_key: \"$API_KEY\"/" "$CONFIG_FILE"
        echo "API key updated in config.yaml."
    else
        echo "No API key provided. BonziBuddy will run in test mode."
    fi
else
    echo "Anthropic API key found in config.yaml."
fi

# Create application icon
echo "Creating application icon..."
ICON_SOURCE="idle/0999.png"
ICON_DEST="BonziBuddy.icns"

if [ -f "$ICON_SOURCE" ]; then
    ./create_icon.sh "$ICON_SOURCE" "$ICON_DEST"
else
    echo "Warning: Icon source $ICON_SOURCE not found."
fi

# Ask if user wants to create the standalone app
echo ""
echo "Would you like to create a standalone macOS application? (y/n)"
read -r CREATE_APP

if [[ "$CREATE_APP" =~ ^[Yy]$ ]]; then
    echo "Creating standalone macOS application..."
    python3 create_app.py
    
    echo ""
    echo "Installation complete! BonziBuddy.app has been created on your Desktop."
    echo "To start BonziBuddy, simply double-click the application icon."
else
    echo ""
    echo "You can run BonziBuddy directly using:"
    echo "python3 bonzi_buddy.py"
fi

echo ""
echo "Thank you for installing BonziBuddy macOS!"
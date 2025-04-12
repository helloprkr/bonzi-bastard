#!/bin/bash
# BonziBuddy Enhanced Setup Script
# This script handles everything needed to get BonziBuddy up and running

# Display welcome message
clear
echo "========================================================"
echo "       BonziBuddy macOS - Enhanced Edition Setup        "
echo "========================================================"
echo ""
echo "Welcome to BonziBuddy Enhanced Edition setup!"
echo "This script will set up the most robust version of BonziBuddy."
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check for API key
API_KEY=$(grep "anthropic_api_key" "config.yaml" | cut -d '"' -f 2)
if [ -z "$API_KEY" ] || [ "$API_KEY" = "" ]; then
    echo "Anthropic API key not found in config.yaml."
    echo "Please enter your Anthropic API key:"
    read -r NEW_API_KEY
    
    # Update the API key in config.yaml
    if [ -n "$NEW_API_KEY" ]; then
        sed -i '' "s/anthropic_api_key: \".*\"/anthropic_api_key: \"$NEW_API_KEY\"/" "config.yaml"
        echo "API key updated in config.yaml."
    else
        echo "No API key provided. BonziBuddy will run in test mode."
    fi
fi

# Create the app
echo "Creating macOS App Bundle..."
python3 create_app.py

echo ""
echo "Setup complete! BonziBuddy.app has been created on your Desktop."
echo "You can now double-click it to run BonziBuddy."
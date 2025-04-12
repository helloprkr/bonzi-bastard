#!/bin/bash
# BonziBuddy macOS - One-Click Setup
# This script handles everything needed to get BonziBuddy up and running

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Display welcome message
clear
echo "========================================================"
echo "       BonziBuddy macOS - Complete Setup Script         "
echo "========================================================"
echo ""
echo "Welcome to BonziBuddy macOS setup!"
echo "This script will handle everything needed to get BonziBuddy"
echo "up and running on your Mac."
echo ""
echo "What would you like to do?"
echo ""
echo "1. Quick Install (run BonziBuddy directly with Python)"
echo "2. Create macOS App (requires Python, but easy to distribute)"
echo "3. Build Standalone App (no Python required, most compatible)"
echo "4. Exit"
echo ""

# Get user choice
read -p "Enter your choice (1-4): " CHOICE
echo ""

case $CHOICE in
    1)
        echo "Starting Quick Install..."
        # Install dependencies
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
        
        # Run BonziBuddy
        echo "Starting BonziBuddy..."
        python3 bonzi_buddy.py
        ;;
        
    2)
        echo "Creating macOS App Bundle..."
        # Make sure create_app.py is executable
        chmod +x create_app.py
        
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
        python3 create_app.py
        
        echo ""
        echo "BonziBuddy.app has been created on your Desktop."
        echo "You can now double-click it to run BonziBuddy."
        ;;
        
    3)
        echo "Building Standalone Application..."
        # Make sure build_standalone.py is executable
        chmod +x build_standalone.py
        
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
        
        # Build the standalone app
        python3 build_standalone.py
        ;;
        
    4)
        echo "Exiting setup. Goodbye!"
        exit 0
        ;;
        
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "Thank you for using BonziBuddy macOS!"
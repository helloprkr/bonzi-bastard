#!/bin/bash

# BonziBuddy macOS Build Script
# This script creates a standalone macOS application (.app) from the Python code

# Ensure script exits on any error
set -e

echo "==== BonziBuddy macOS App Builder ===="
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
else
    echo "PyInstaller is already installed."
fi

# Check if all dependencies are installed
echo "Checking dependencies..."
pip install -r requirements.txt

# Create build directory if it doesn't exist
mkdir -p build

# Build the application using the spec file
echo "Building BonziBuddy.app..."
pyinstaller --clean bonzibuddy.spec

# If the app was built successfully, let the user know
if [ -d "dist/BonziBuddy.app" ]; then
    echo ""
    echo "Build successful! The application is available at:"
    echo "$(pwd)/dist/BonziBuddy.app"
    echo ""
    echo "To run the application, double-click the app in Finder."
    echo "When first launching, you may need to right-click the app and select 'Open'."
    echo ""
    
    # Ask if user wants to copy the app to /Applications
    read -p "Would you like to copy BonziBuddy.app to your Applications folder? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Copying to Applications folder..."
        cp -R "dist/BonziBuddy.app" "/Applications/"
        echo "BonziBuddy.app has been copied to your Applications folder!"
    fi
else
    echo "Build failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "Thank you for building BonziBuddy macOS!"
echo "Remember to configure your Anthropic API key in the config.yaml file before running."
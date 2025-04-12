# BonziBuddy macOS Installation Guide

This document provides detailed instructions for installing and building BonziBuddy for macOS.

## Quick Installation

For the fastest and easiest installation:

```bash
./install.sh
```

This script will:
1. Install required dependencies
2. Configure your Anthropic API key
3. Create an application icon
4. Build a macOS application (.app)

After installation, you'll find BonziBuddy.app on your Desktop. Simply double-click to run!

## Installation Options

BonziBuddy offers multiple installation methods to suit your preferences:

### 1. Quick Setup (Python Required)

If you already have Python installed and just want to run BonziBuddy:

```bash
# Install dependencies
pip install -r requirements.txt

# Update config.yaml with your API key

# Run BonziBuddy
python3 bonzi_buddy.py
```

### 2. Create macOS App Bundle (Python Required)

To create a .app bundle that can be launched from Finder:

```bash
python3 create_app.py
```

This creates a BonziBuddy.app on your Desktop. This app requires Python to be installed but handles all other dependencies.

### 3. Build Fully Standalone App (No Python Required)

To create a completely standalone application that doesn't require Python:

```bash
python3 build_standalone.py
```

This creates a BonziBuddy.app that contains everything needed to run (Python interpreter included). The app is larger but can be deployed to systems without Python installed.

## Configuration

Before running BonziBuddy, make sure to configure your Anthropic API key in `config.yaml`:

```yaml
anthropic_api_key: "your-api-key-here"
```

You can also customize other settings:

```yaml
model: "claude-3-haiku-20240307"  # Claude model to use
temp: 1.0                         # Temperature (creativity)
max_tokens: 150                   # Maximum response length
use_system_tts: True              # Use macOS text-to-speech
```

## Advanced Usage

### Creating Custom Icons

BonziBuddy uses the `idle/0999.png` frame as its default icon. You can create a custom icon:

```bash
./create_icon.sh path/to/image.png BonziBuddy.icns
```

### Running from Command Line

You can always run BonziBuddy directly:

```bash
python3 bonzi_buddy.py
```

## Troubleshooting

### Security Warning

When first launching BonziBuddy, macOS might show a security warning. To resolve:

1. Go to System Preferences > Security & Privacy
2. Look for a message about BonziBuddy being blocked
3. Click "Open Anyway"

### Missing Animations

If you see errors about missing animation frames, ensure all animation directories (idle, wave, etc.) are properly populated with PNG files.

### API Key Issues

If BonziBuddy can't connect to Anthropic's API, check:
- Your API key is correctly entered in config.yaml
- Your API key has sufficient credits
- Your internet connection is working

## Uninstalling

To uninstall BonziBuddy:

1. Delete the BonziBuddy.app file from your Desktop or Applications folder
2. Optionally, remove the BonziBuddy-Build directory
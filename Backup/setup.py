#!/usr/bin/env python3
"""
BonziBuddy macOS - Setup Script
This script handles the installation and configuration of BonziBuddy for macOS.
"""

import os
import sys
import subprocess
import yaml
import getpass

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("Checking dependencies...")
    
    try:
        import PyQt5
        import requests
        import yaml as yaml_lib
        import PIL
        import anthropic
        print("All required Python packages are installed.")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("Dependencies installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return False

def configure_anthropic_api():
    """Configure Anthropic API settings."""
    print("\nBonziBuddy needs Anthropic's API to function properly.")
    
    # Read current config
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return False
    
    # Get API key
    api_key = input("Enter your Anthropic API key (press Enter to skip): ").strip()
    
    if api_key:
        config["anthropic_api_key"] = api_key
        config["api_enabled"] = True
    
    # Write updated config
    try:
        with open("config.yaml", "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        print("Configuration updated successfully.")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

def create_desktop_shortcut():
    """Create a desktop shortcut to launch BonziBuddy."""
    print("\nCreating desktop shortcut...")
    
    # Get desktop path
    desktop_path = os.path.expanduser("~/Desktop")
    bonzi_path = os.path.abspath("bonzi_buddy.py")
    
    # Create launcher script
    launcher_path = os.path.join(os.path.dirname(bonzi_path), "launch_bonzi.sh")
    
    with open(launcher_path, "w") as f:
        f.write(f"""#!/bin/bash
cd "{os.path.dirname(bonzi_path)}"
python3 bonzi_buddy.py
""")
    
    os.chmod(launcher_path, 0o755)
    
    # Create desktop shortcut
    shortcut_path = os.path.join(desktop_path, "BonziBuddy.command")
    
    with open(shortcut_path, "w") as f:
        f.write(f"""#!/bin/bash
cd "{os.path.dirname(bonzi_path)}"
python3 bonzi_buddy.py
""")
    
    os.chmod(shortcut_path, 0o755)
    
    print(f"Desktop shortcut created at: {shortcut_path}")
    return True

def main():
    """Main setup function."""
    print("=" * 60)
    print("BonziBuddy macOS Setup")
    print("=" * 60)
    print("\nThis script will set up BonziBuddy on your macOS system.")
    
    # Check dependencies
    if not check_dependencies():
        print("Error: Could not install dependencies. Please try manually with:")
        print("pip install -r requirements.txt")
        return False
    
    # Configure Anthropic API
    if not configure_anthropic_api():
        print("Warning: Could not configure Anthropic API. BonziBuddy will run in test mode.")
    
    # Create desktop shortcut
    create_desktop_shortcut()
    
    print("\nSetup completed successfully!")
    print("To run BonziBuddy, double-click the BonziBuddy.command file on your desktop.")
    print("\nNOTE: When first launching BonziBuddy, macOS might show a security warning.")
    print("To allow the app to run, go to System Preferences > Security & Privacy and click 'Open Anyway'.")
    
    launch_now = input("\nDo you want to launch BonziBuddy now? (y/n): ").strip().lower()
    if launch_now == 'y':
        print("Launching BonziBuddy...")
        subprocess.Popen([sys.executable, "bonzi_buddy.py"])
    
    return True

if __name__ == "__main__":
    main()
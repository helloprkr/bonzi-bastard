#!/usr/bin/env python3
"""
BonziBuddy Launcher

This script ensures proper launching of BonziBuddy with all necessary paths
and environment variables set correctly when running from a .app bundle.
"""

import os
import sys
import subprocess
import yaml

def main():
    """Main launcher function"""
    # Determine if we're running from an app bundle
    is_app_bundle = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    
    # Get the script directory
    if is_app_bundle:
        app_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.executable)))
        resources_path = os.path.join(app_path, 'Resources')
        script_dir = resources_path
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Add the script directory to Python path
    sys.path.insert(0, script_dir)
    
    # Set environment variables for Anthropic API key
    try:
        with open(os.path.join(script_dir, 'config.yaml'), 'r') as f:
            config = yaml.safe_load(f)
            api_key = config.get('anthropic_api_key', '')
            if api_key:
                os.environ['ANTHROPIC_API_KEY'] = api_key
    except Exception as e:
        print(f"Error loading config: {e}")
    
    # Import and run BonziBuddy
    try:
        import bonzi_buddy
        sys.exit(0)
    except ImportError:
        # If import fails, try running the script directly
        try:
            bonzi_path = os.path.join(script_dir, 'bonzi_buddy.py')
            subprocess.run([sys.executable, bonzi_path], check=True)
        except Exception as e:
            print(f"Error launching BonziBuddy: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
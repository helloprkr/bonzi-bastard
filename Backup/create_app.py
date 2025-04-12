#!/usr/bin/env python3
"""
Create a standalone macOS application (.app) for BonziBuddy
"""

import os
import sys
import shutil
import subprocess
import glob
import tempfile
import plistlib

def main():
    """Main function to create the BonziBuddy.app bundle"""
    print("==== Creating BonziBuddy.app ====")
    
    # Create app bundle structure
    app_path = os.path.expanduser("~/Desktop/BonziBuddy.app")
    if os.path.exists(app_path):
        print(f"Removing existing {app_path}")
        shutil.rmtree(app_path)
    
    # Create required directories
    contents_path = os.path.join(app_path, "Contents")
    macos_path = os.path.join(contents_path, "MacOS")
    resources_path = os.path.join(contents_path, "Resources")
    
    os.makedirs(macos_path)
    os.makedirs(resources_path)
    
    # Create Python virtual environment
    venv_path = os.path.join(resources_path, "venv")
    subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
    
    # Activate virtual environment and install dependencies
    pip_path = os.path.join(venv_path, "bin", "pip")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    
    # Copy resources
    print("Copying resources...")
    # Copy all animation directories
    for anim_dir in ["idle", "arrive", "backflip", "glasses", "goodbye", "talking", "wave"]:
        src_dir = os.path.join(os.getcwd(), anim_dir)
        dst_dir = os.path.join(resources_path, anim_dir)
        if os.path.exists(src_dir):
            shutil.copytree(src_dir, dst_dir)
    
    # Copy audio files
    audio_src = os.path.join(os.getcwd(), "audio")
    audio_dst = os.path.join(resources_path, "audio")
    if os.path.exists(audio_src):
        shutil.copytree(audio_src, audio_dst)
    else:
        os.makedirs(audio_dst)
    
    # Copy config.yaml
    shutil.copy("config.yaml", os.path.join(resources_path, "config.yaml"))
    
    # Copy Python file (using fixed_bonzi.py which is more robust)
    shutil.copy("fixed_bonzi.py", os.path.join(resources_path, "fixed_bonzi.py"))
    
    # Create launcher script
    launcher_script = os.path.join(macos_path, "BonziBuddy")
    with open(launcher_script, "w") as f:
        f.write(f"""#!/bin/bash
# Get the directory where this script is running
DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
RESOURCES_DIR="$DIR/../Resources"
VENV_DIR="$RESOURCES_DIR/venv"

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Change to the resources directory
cd "$RESOURCES_DIR"

# Run the application
python3 fixed_bonzi.py
""")
    
    os.chmod(launcher_script, 0o755)
    
    # Create Info.plist
    info_plist = {
        'CFBundleName': 'BonziBuddy',
        'CFBundleDisplayName': 'BonziBuddy',
        'CFBundleIdentifier': 'com.bonzibuddy.macos',
        'CFBundleVersion': '1.0',
        'CFBundleShortVersionString': '1.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleExecutable': 'BonziBuddy',
        'CFBundleIconFile': 'AppIcon.icns',
        'NSHighResolutionCapable': True,
        'LSUIElement': True,  # Makes app appear in menu bar, not dock
    }
    
    with open(os.path.join(contents_path, "Info.plist"), 'wb') as f:
        plistlib.dump(info_plist, f)
    
    # Create app icon from one of the idle frames
    icon_path = os.path.join(resources_path, "AppIcon.icns")
    print("Creating app icon...")
    try:
        # Use idle/0999.png as the icon
        source_icon = os.path.join(os.getcwd(), "idle", "0999.png")
        if os.path.exists(source_icon):
            # Create temporary iconset directory
            with tempfile.TemporaryDirectory() as tmp_dir:
                iconset_path = os.path.join(tmp_dir, "AppIcon.iconset")
                os.makedirs(iconset_path)
                
                # Copy the source icon to multiple sizes
                sizes = [16, 32, 64, 128, 256, 512]
                for size in sizes:
                    subprocess.run([
                        "sips", 
                        "-z", str(size), str(size), 
                        source_icon, 
                        "--out", os.path.join(iconset_path, f"icon_{size}x{size}.png")
                    ], check=True)
                    
                    # Create 2x versions
                    if size <= 256:
                        subprocess.run([
                            "sips", 
                            "-z", str(size*2), str(size*2), 
                            source_icon, 
                            "--out", os.path.join(iconset_path, f"icon_{size}x{size}@2x.png")
                        ], check=True)
                
                # Convert iconset to icns
                subprocess.run([
                    "iconutil", 
                    "-c", "icns", 
                    iconset_path, 
                    "-o", icon_path
                ], check=True)
        else:
            print(f"Warning: Icon source {source_icon} not found")
    except Exception as e:
        print(f"Error creating icon: {e}")
    
    print(f"\nApplication created successfully at {app_path}")
    print("To run BonziBuddy, simply double-click the application icon.")

if __name__ == "__main__":
    main()
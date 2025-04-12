#!/usr/bin/env python3
"""
Build a fully standalone BonziBuddy.app for macOS using PyInstaller
No Python installation required to run the resulting app
"""

import os
import sys
import subprocess
import shutil
import tempfile
import plistlib

def check_requirements():
    """Check if required tools are installed"""
    try:
        # Check PyInstaller
        import PyInstaller
        print("PyInstaller is installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyInstaller"], check=True)
    
    # Check other dependencies are installed
    print("Checking other dependencies...")
    requirements = ["PyQt5", "Pillow", "pyyaml", "requests", "anthropic"]
    for req in requirements:
        try:
            __import__(req)
            print(f"✅ {req} is installed.")
        except ImportError:
            print(f"⚠️ {req} is not installed. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", req], check=True)

def create_icon():
    """Create an app icon from an idle frame"""
    source_icon = "idle/0999.png"
    output_icon = "BonziBuddy.icns"
    
    if not os.path.exists(source_icon):
        print(f"Warning: Icon source {source_icon} not found.")
        return None
    
    print("Creating application icon...")
    
    # Create iconset directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        iconset_path = os.path.join(tmp_dir, "AppIcon.iconset")
        os.makedirs(iconset_path)
        
        # Generate various icon sizes
        sizes = [16, 32, 64, 128, 256, 512]
        for size in sizes:
            subprocess.run([
                "sips", 
                "-z", str(size), str(size), 
                source_icon, 
                "--out", os.path.join(iconset_path, f"icon_{size}x{size}.png")
            ], check=True)
            
            # 2x versions
            if size <= 256:
                subprocess.run([
                    "sips", 
                    "-z", str(size*2), str(size*2), 
                    source_icon, 
                    "--out", os.path.join(iconset_path, f"icon_{size}x{size}@2x.png")
                ], check=True)
        
        # Convert to icns
        subprocess.run([
            "iconutil", 
            "-c", "icns", 
            iconset_path, 
            "-o", output_icon
        ], check=True)
    
    print(f"Icon created at {output_icon}")
    return output_icon

def build_app():
    """Build the standalone app using PyInstaller"""
    print("Building standalone application with PyInstaller...")
    
    # Create icon
    icon_path = create_icon()
    
    # Ensure dist directory is clean
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Prepare data files
    data_files = []
    for dir_name in ["idle", "arrive", "backflip", "glasses", "goodbye", "talking", "wave", "audio"]:
        if os.path.exists(dir_name):
            data_files.append((dir_name, os.path.join(dir_name, "*")))
    
    data_files.append((".", "config.yaml"))
    
    # Format data files for PyInstaller command
    data_args = []
    for dest, src in data_files:
        data_args.extend(["--add-data", f"{src}:{dest}"])
    
    # Build command
    cmd = [
        "pyinstaller",
        "--windowed",  # No console window
        "--onefile",   # Single executable
        "--clean",     # Clean PyInstaller cache
        "--name", "BonziBuddy"
    ]
    
    # Add icon if created
    if icon_path:
        cmd.extend(["--icon", icon_path])
    
    # Add data files
    cmd.extend(data_args)
    
    # Add hidden imports
    cmd.extend([
        "--hidden-import", "PyQt5.QtMultimedia",
        "--hidden-import", "PyQt5.sip",
        "--hidden-import", "yaml",
        "--hidden-import", "PIL",
        "--hidden-import", "requests",
        "--hidden-import", "anthropic"
    ])
    
    # Add main script
    cmd.append("launcher.py")
    
    # Run PyInstaller
    print("Running PyInstaller...")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    
    # Customize Info.plist
    app_path = "dist/BonziBuddy.app"
    info_plist_path = os.path.join(app_path, "Contents", "Info.plist")
    
    try:
        with open(info_plist_path, "rb") as f:
            info = plistlib.load(f)
        
        # Modify properties
        info["CFBundleDisplayName"] = "BonziBuddy"
        info["CFBundleIdentifier"] = "com.bonzibuddy.macos"
        info["CFBundleShortVersionString"] = "1.0.0"
        info["CFBundleVersion"] = "1.0.0"
        info["NSHighResolutionCapable"] = True
        info["LSUIElement"] = True  # App appears in menu bar, not dock
        
        # Write back
        with open(info_plist_path, "wb") as f:
            plistlib.dump(info, f)
        
        print("Info.plist customized.")
    except Exception as e:
        print(f"Warning: Failed to customize Info.plist: {e}")
    
    print(f"\nBuild complete! Standalone app created at: {os.path.abspath(app_path)}")
    
    # Ask to copy to Applications
    answer = input("\nWould you like to copy BonziBuddy.app to your Applications folder? (y/n): ")
    if answer.lower() == "y":
        applications_path = "/Applications/BonziBuddy.app"
        if os.path.exists(applications_path):
            shutil.rmtree(applications_path)
        shutil.copytree(app_path, applications_path)
        print(f"BonziBuddy.app copied to {applications_path}")

def main():
    """Main function"""
    print("==== BonziBuddy macOS Standalone App Builder ====")
    print("")
    
    # Check requirements
    check_requirements()
    
    # Build the app
    build_app()
    
    print("\nAll done! You can now run BonziBuddy by double-clicking its icon.")
    print("Note: When first launching, macOS might show a security warning.")
    print("To allow the app to run, go to System Preferences > Security & Privacy and click 'Open Anyway'.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simplified BonziBuddy implementation focusing on the core functionality
"""

import sys
import os
import random
import hashlib
import tempfile
import subprocess
import glob
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PIL import Image

# ---------------------------
# ChatBubble Class - Simplified
# ---------------------------
class SimpleChatBubble(QtWidgets.QWidget):
    def __init__(self, text):
        # Create a regular window that stays on top
        super().__init__(None, QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Bonzi Says")
        
        # Set up the UI
        layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel(text)
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("""
            color: black;
            font: 12pt Arial;
            padding: 10px;
        """)
        
        # Add a close button
        self.closeButton = QtWidgets.QPushButton("Close")
        self.closeButton.clicked.connect(self.close)
        
        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.closeButton)
        
        # Set window properties
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        self.adjustSize()
        
        # Style the window
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFF99;
                border: 2px solid black;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #E6E6E6;
                border: 1px solid #999999;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
        """)

# ---------------------------
# BonziBuddy Main Class - Simplified
# ---------------------------
class SimpleBonziBuddy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # Set up the window
        self.setWindowTitle("BonziBuddy")
        self.setFixedSize(200, 200)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        
        # Set up the layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Add a label for the image
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        # Try to load an image from the idle folder
        idle_images = sorted(glob.glob("idle/*.png"))
        if idle_images:
            pixmap = QtGui.QPixmap(idle_images[0])
            if not pixmap.isNull():
                self.imageLabel.setPixmap(pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio))
            else:
                self.imageLabel.setText("(Image not found)")
        else:
            self.imageLabel.setText("(No images found)")
        
        # Add a button to talk to Bonzi
        self.talkButton = QtWidgets.QPushButton("Talk to Bonzi")
        self.talkButton.clicked.connect(self.prompt_user)
        
        # Add widgets to layout
        layout.addWidget(self.imageLabel)
        layout.addWidget(self.talkButton)
    
    def prompt_user(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Talk to Bonzi", "What do you want to say?")
        if ok and text:
            # For simplicity, just show a static response
            response = random.choice([
                "Oh look, the human thinks I care about what they have to say!",
                "Wow, that's the most intelligent thing you've said all day... which isn't saying much.",
                "I'd give you a clever response, but I'm afraid you wouldn't understand it.",
                "Did you really think that was worth saying? How adorable.",
                "I've seen smarter questions from a broken calculator."
            ])
            
            # Show the chat bubble
            bubble = SimpleChatBubble(response)
            bubble.show()
            
            # Play sound if macOS
            try:
                subprocess.run(['say', '-v', 'Alex', response], check=False)
            except Exception:
                pass  # Ignore errors with speech

# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    bonzi = SimpleBonziBuddy()
    bonzi.show()
    sys.exit(app.exec_())
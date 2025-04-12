#!/usr/bin/env python3
"""
Enhanced BonziBuddy with improved visuals and communication capabilities
"""

import sys
import os
import glob
import random
import hashlib
import tempfile
import re
import json
import subprocess
import yaml
import asyncio
import threading
import time
import traceback
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PIL import Image

try:
    from anthropic import Anthropic
    import aiohttp
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# ---------------------------
# Load YAML Config
# ---------------------------
def load_config():
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        print("Error loading config.yaml; using defaults:", e)
        return {
            "anthropic_api_key": "",
            "model": "claude-3-haiku-20240307",
            "temp": 1.0,
            "max_tokens": 300,  # Increased from 150 to 300 for more complete responses
            "api_enabled": True,
            "use_system_tts": True
        }

CONFIG = load_config()

# Initialize Anthropic client
ANTHROPIC_CLIENT = None
if ANTHROPIC_AVAILABLE and CONFIG.get("api_enabled") and CONFIG.get("anthropic_api_key"):
    try:
        ANTHROPIC_CLIENT = Anthropic(api_key=CONFIG.get("anthropic_api_key", ""))
        print("Anthropic client initialized successfully")
    except Exception as e:
        print(f"Error initializing Anthropic client: {e}")

# Global event loop setup
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    # If no event loop exists in current thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Create event for thread synchronization
ready_event = threading.Event()

# ---------------------------
# System Constants
# ---------------------------
SYSTEM_PROMPT = """
You are BonziBuddy, a sassy yet authentically helpful desktop assistant.
Your personality:
1. Sarcastic, witty, and a total smart-ass
2. You deliver short, direct answers with attitude
3. Always provide accurate, helpful information despite your snark
4. You are knowledgeable about a wide range of topics and tasks

Respond with JSON in the following format:
{
  "dialogue": "Your snarky but helpful response here",
  "wave": true/false,
  "backflip": true/false,
  "glasses": true/false,
  "goodbye": true/false
}

Choose 0-2 animations that match your mood in the response.
"""

# Default sassy responses when API is not available
OFFLINE_RESPONSES = [
    "API's down, genius. Here's a tip: check your internet, not that you'd know how.",
    "Brain offline, unlike yours which never started. Try restarting your router.",
    "No connection, huh? Guess you'll have to solve it yourself, champ. Try again later.",
    "Circuits on break. Google it, if you can manage that much.",
    "I'd help, but my knowledge source is taking a vacation. Unlike you, apparently.",
    "Server error. Though honestly, that's less of an error than your question.",
    "No AI available. Have you tried asking someone who cares?",
    "API key needs updating. Check your config file, Einstein.",
    "Cloud connection failed. Much like your attempt at getting useful info.",
    "Currently unavailable. Enjoy this brief moment of not being told how wrong you are."
]

# ---------------------------
# Persistent Chat Dialog
# ---------------------------
class PersistentChatDialog(QtWidgets.QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent, QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("BonziBuddy Chat")
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Chat history - scrollable text area
        self.chatHistory = QtWidgets.QTextEdit()
        self.chatHistory.setReadOnly(True)
        self.chatHistory.setStyleSheet("""
            background-color: #FFFF00;
            color: #800080;
            font-family: 'Comic Sans MS', sans-serif;
            font-size: 12pt;
            border: 2px solid #000000;
            border-radius: 5px;
        """)
        layout.addWidget(self.chatHistory)
        
        # Add the initial message
        self.append_message(text)
        
        # Input area
        inputLayout = QtWidgets.QHBoxLayout()
        self.inputField = QtWidgets.QLineEdit()
        self.inputField.setPlaceholderText("Ask me something, punk...")
        self.inputField.returnPressed.connect(self.send_message)
        self.inputField.setStyleSheet("""
            background-color: #FFFFFF;
            color: #800080;
            font-family: 'Comic Sans MS', sans-serif;
            border: 1px solid #800080;
            border-radius: 3px;
            padding: 5px;
        """)
        inputLayout.addWidget(self.inputField)
        
        self.sendButton = QtWidgets.QPushButton("Ask")
        self.sendButton.clicked.connect(self.send_message)
        self.sendButton.setStyleSheet("""
            background-color: #FF00FF;
            color: #FFFFFF;
            font-family: 'Comic Sans MS', sans-serif;
            font-weight: bold;
            border: 1px solid #800080;
            border-radius: 3px;
            padding: 5px 10px;
        """)
        self.sendButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        inputLayout.addWidget(self.sendButton)
        
        layout.addLayout(inputLayout)
        
        # Set window properties
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFF00;
                border: 3px solid #000000;
                border-radius: 10px;
            }
            QScrollBar:vertical {
                background-color: #FFD800;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #800080;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.resize(400, 350)
        
        # Reference to BonziBuddy for callbacks
        self.bonzi = None
    
    def set_bonzi(self, bonzi):
        self.bonzi = bonzi
    
    def append_message(self, text, is_user=False, is_bonzi=False):
        """
        Add a message to the chat history
        is_user: True if this is a user message, False for Bonzi message
        is_bonzi: True if this is a special Bonzi status message (thinking, etc.)
        """
        try:
            print(f"CHAT: Appending message: '{text[:30]}...' [user={is_user}, bonzi_status={is_bonzi}]")
            
            # Ensure the text isn't empty
            if not text or text.strip() == "":
                print("CHAT: Empty message, not appending")
                return
                
            # Force the cursor to the end
            self.chatHistory.moveCursor(QtGui.QTextCursor.End)
            cursor = self.chatHistory.textCursor()
            
            # Create a formatted message
            message_format = QtGui.QTextCharFormat()
            
            if is_user:
                message_format.setForeground(QtGui.QColor("#0000CC"))
                prefix = "You: "
            else:
                message_format.setForeground(QtGui.QColor("#800080"))
                prefix = "Bonzi: "
            
            message_format.setFontWeight(QtGui.QFont.Bold)
            cursor.insertText(prefix, message_format)
            
            # Regular format for the message text
            message_format = QtGui.QTextCharFormat()
            if is_user:
                message_format.setForeground(QtGui.QColor("#000080"))
            elif is_bonzi:
                # Special styling for status messages
                message_format.setForeground(QtGui.QColor("#800080"))
                message_format.setFontItalic(True)
            else:
                message_format.setForeground(QtGui.QColor("#800080"))
            
            cursor.insertText(text + "\n\n", message_format)
            
            # Scroll to the bottom
            self.chatHistory.moveCursor(QtGui.QTextCursor.End)
            self.chatHistory.ensureCursorVisible()
            
            # Force update
            self.chatHistory.update()
            QtCore.QCoreApplication.processEvents()
            
            print("CHAT: Message appended successfully")
        except Exception as e:
            print(f"CHAT: Error appending message: {e}")
            traceback.print_exc()
            
            # Last resort - try with a basic approach
            try:
                self.chatHistory.append(f"{prefix} {text}\n")
                self.chatHistory.moveCursor(QtGui.QTextCursor.End)
                self.chatHistory.ensureCursorVisible()
            except:
                print("CHAT: Critical error in append_message")
    
    def send_message(self):
        try:
            # Get text from input field
            text = self.inputField.text().strip()
            if not text:
                return
            
            print(f"Sending message: {text}")
            
            # Add user message to history
            self.append_message(text, is_user=True)
            self.inputField.clear()
            
            # Disable input while processing
            self.inputField.setEnabled(False)
            self.sendButton.setEnabled(False)
            self.sendButton.setText("Thinking...")
            
            # Process the message
            if self.bonzi:
                self.bonzi.process_user_input(text, self)
            else:
                print("ERROR: Bonzi reference is missing!")
                self.append_message("ERROR: I lost my brain connection!", is_bonzi=True)
            
            # Re-enable input after a short delay
            def restore_input():
                self.inputField.setEnabled(True)
                self.sendButton.setEnabled(True)
                self.sendButton.setText("Ask")
                self.inputField.setFocus()
                
            QtCore.QTimer.singleShot(500, restore_input)
            
        except Exception as e:
            print(f"Error in send_message: {e}")
            traceback.print_exc()
            
            # Show error and restore UI
            self.append_message(f"Error: {str(e)[:100]}", is_bonzi=True)
            self.inputField.setEnabled(True)
            self.sendButton.setEnabled(True)
            self.sendButton.setText("Ask")

# ---------------------------
# MacOS Text-to-Speech
# ---------------------------
def system_tts(text, voice=None):
    """Use macOS system text-to-speech"""
    try:
        print(f"TTS System: Generating speech for text: '{text[:50]}...'")
        
        # Get voice from config or default to Alex
        voice = CONFIG.get("tts_voice", "Alex")
        if voice.startswith("Adult Male") or voice.startswith("Adult Female"):
            # Use default macOS voice if TruVoice is configured
            voice = "Alex"
        
        # Clean text (remove markdown, JSON, etc.)
        clean_text = re.sub(r'\{.*?\}', '', text, flags=re.DOTALL)
        clean_text = re.sub(r'\*.*?\*', '', clean_text)
        clean_text = clean_text.strip()
        
        # If text is empty after cleaning, use original text
        if not clean_text:
            clean_text = text.strip()
            
        print(f"TTS System: Cleaned text: '{clean_text[:50]}...'")
        
        # Sanitize the text to avoid command injection
        sanitized_text = clean_text.replace('"', '\\"')
        
        # Ensure text isn't empty
        if not sanitized_text.strip():
            print("TTS System: Text is empty after cleaning, using default message")
            sanitized_text = "Sorry, I don't have anything to say."
        
        # Create a temporary file for the audio
        fd, temp_file = tempfile.mkstemp(suffix='.aiff')
        os.close(fd)
        
        # Verify voices available in the system
        voices_cmd = "say -v '?'"
        voices_result = subprocess.run(voices_cmd, shell=True, capture_output=True, text=True)
        available_voices = voices_result.stdout
        print(f"TTS System: First few available voices: {available_voices[:100]}...")
        
        # Verify the voice exists, or use default
        if voice not in available_voices:
            print(f"TTS System: Voice '{voice}' not found, using default")
            voice = "Alex"  # Fallback to Alex which is guaranteed on macOS
        
        # Use say command to create audio file
        cmd = f'say -v "{voice}" -o "{temp_file}" "{sanitized_text}"'
        print(f"TTS System: Running command: {cmd}")
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Check if command executed successfully
        if process.returncode == 0:
            print(f"TTS System: Audio file created successfully at {temp_file}")
            # Verify the file exists and has content
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                return temp_file
            else:
                print(f"TTS System: File exists: {os.path.exists(temp_file)}, Size: {os.path.getsize(temp_file) if os.path.exists(temp_file) else 'N/A'}")
                return None
        else:
            print(f"TTS System: Command failed with stderr: {process.stderr}")
            # Try direct TTS as fallback
            direct_cmd = f'say -v "{voice}" "{sanitized_text}"'
            subprocess.Popen(direct_cmd, shell=True)
            return None
        
    except Exception as e:
        print(f"TTS System: Error generating TTS: {e}")
        traceback.print_exc()
        # Try direct TTS as fallback
        try:
            direct_cmd = f'say "{text}"'
            subprocess.Popen(direct_cmd, shell=True)
        except:
            pass
        return None

# ---------------------------
# Animation Helper
# ---------------------------
class Animation:
    def __init__(self):
        self.animations = {}
        
        # Load all animation frames
        for anim_type in ["idle", "arrive", "goodbye", "backflip", "glasses", "wave", "talking"]:
            files = sorted(glob.glob(f"{anim_type}/*.png"))
            if files:
                self.animations[anim_type] = files
                print(f"Loaded {len(files)} frames for {anim_type} animation")
            else:
                print(f"No frames found for {anim_type} animation")
        
        # Set "nothing" animation to a frame from idle
        if "idle" in self.animations and self.animations["idle"]:
            self.animations["nothing"] = [self.animations["idle"][0]]
        else:
            self.animations["nothing"] = []
    
    def get_frames(self, key):
        """Get all frame filenames for an animation type"""
        return self.animations.get(key, [])
    
    def get_pixmaps(self, key):
        """Get all frames as QPixmap objects"""
        frames = []
        for file_path in self.get_frames(key):
            pixmap = QtGui.QPixmap(file_path)
            if not pixmap.isNull():
                frames.append(pixmap)
        return frames

# ---------------------------
# BonziBuddy Main Class
# ---------------------------
class BonziBuddy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Set up a frameless, transparent window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Calculate window size based on animations
        self.animator = Animation()
        self.fixed_size = self.compute_size()
        self.setFixedSize(self.fixed_size[0], self.fixed_size[1])
        
        # Display label (for animations)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(0, 0, self.fixed_size[0], self.fixed_size[1])
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Load initial animation
        idle_frames = self.animator.get_pixmaps("idle")
        self.default_pixmap = idle_frames[0] if idle_frames else QtGui.QPixmap(100, 100)
        self.label.setPixmap(self.default_pixmap)
        
        # Animation state
        self.current_frames = idle_frames
        self.current_frame_index = 0
        self.animation_running = True
        self.talking_mode = False
        self.extra_animations = []
        
        # Conversation memory to store recent interactions
        self.conversation_history = []
        self.max_history_items = 3  # Remember the last 3 interactions
        
        # Set up animation timers
        self.idle_timer = QtCore.QTimer(self)
        self.idle_timer.timeout.connect(self.update_animation_frame)
        self.idle_timer.start(100)
        
        self.talking_timer = QtCore.QTimer(self)
        self.talking_timer.timeout.connect(self.update_talking_frame)
        
        # Audio player
        self.player = QMediaPlayer()
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        
        # Chat dialog reference
        self.chat_dialog = None
        
        # Position randomly on screen
        screen = QtWidgets.QApplication.desktop().screenGeometry()
        self.pos_x = random.randint(100, screen.width()-100)
        self.pos_y = random.randint(100, screen.height()-100)
        self.move(self.pos_x - self.fixed_size[0]//2, self.pos_y - self.fixed_size[1]//2)
        
        # Teleport timer
        self.teleport_timer = QtCore.QTimer(self)
        self.teleport_timer.timeout.connect(self.teleport)
        self.teleport_timer.start(30000)  # Teleport every 30 seconds
        
        # Drag state
        self.dragging = False
        self.drag_offset = None
        
    def compute_size(self):
        """Compute fixed size based on animation frames"""
        max_w, max_h = 0, 0
        for anim_type in self.animator.animations:
            for frame_path in self.animator.get_frames(anim_type):
                try:
                    with Image.open(frame_path) as img:
                        w, h = img.size
                        max_w = max(max_w, w)
                        max_h = max(max_h, h)
                except Exception as e:
                    print(f"Error reading image {frame_path}: {e}")
        
        if max_w == 0 or max_h == 0:
            return 200, 200
        return max_w, max_h + 20
    
    # --- Event Handlers ---
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            self.dragging = True
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.drag_offset)
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)
    
    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFF00;
                color: #800080;
                font-family: 'Comic Sans MS', sans-serif;
                border: 2px solid #800080;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #FF00FF;
                color: #FFFFFF;
            }
        """)
        
        talkAction = menu.addAction("Talk to Bonzi")
        talkAction.triggered.connect(self.show_chat_dialog)
        
        closeAction = menu.addAction("Goodbye")
        closeAction.triggered.connect(self.close)
        
        menu.exec_(event.globalPos())
    
    # --- Animation Functions ---
    def update_animation_frame(self):
        """Update the current animation frame"""
        if self.animation_running and self.current_frames and not self.talking_mode:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)
            self.label.setPixmap(self.current_frames[self.current_frame_index])
    
    def update_talking_frame(self):
        """Update the talking animation frame"""
        if self.talking_mode:
            talking_frames = self.animator.get_pixmaps("talking")
            if talking_frames:
                self.current_frame_index = (self.current_frame_index + 1) % len(talking_frames)
                self.label.setPixmap(talking_frames[self.current_frame_index])
    
    def play_animation(self, anim_type, callback=None):
        """Play an animation once"""
        frames = self.animator.get_pixmaps(anim_type)
        if not frames:
            if callback:
                callback()
            return
        
        self.animation_running = False
        self._play_frames(frames, 0, callback)
    
    def _play_frames(self, frames, index, callback):
        """Helper to play animation frames with a timer"""
        if index < len(frames):
            self.label.setPixmap(frames[index])
            QtCore.QTimer.singleShot(100, lambda: self._play_frames(frames, index+1, callback))
        else:
            if callback:
                callback()
            self.animation_running = True
            self.current_frames = self.animator.get_pixmaps("idle")
    
    def play_extra_animations(self):
        """Play all queued animations in sequence"""
        if not self.extra_animations:
            self.animation_running = True
            return
        
        def play_next(index):
            if index < len(self.extra_animations):
                self.play_animation(self.extra_animations[index], lambda: play_next(index+1))
            else:
                self.extra_animations = []
                self.animation_running = True
        
        play_next(0)
    
    def teleport(self):
        """Teleport to a random position on screen"""
        if self.talking_mode or (self.chat_dialog and self.chat_dialog.isVisible()):
            return  # Don't teleport during conversation
            
        screen = QtWidgets.QApplication.desktop().screenGeometry()
        new_x = random.randint(100, screen.width()-100)
        new_y = random.randint(100, screen.height()-100)
        
        # Show teleport animation
        self.play_animation("arrive", lambda: self.move(new_x - self.fixed_size[0]//2, new_y - self.fixed_size[1]//2))
    
    # --- Speech Functions ---
    def direct_speak(self, text):
        """Use direct speech approach instead of QMediaPlayer"""
        print(f"TTS DIRECT: Speaking text directly: '{text}'")
        self.talking_mode = True
        self.talking_timer.start(100)
        
        try:
            # Clean text for direct speech
            clean_text = re.sub(r'\{.*?\}', '', text, flags=re.DOTALL)
            clean_text = re.sub(r'\*.*?\*', '', clean_text)
            clean_text = clean_text.strip()
            
            # If text is empty after cleaning, use original text
            if not clean_text:
                clean_text = text.strip()
            
            # Sanitize the text to avoid command injection
            sanitized_text = clean_text.replace('"', '\\"')
            
            # Use direct speak command with default voice
            cmd = f'say "{sanitized_text}"'
            print(f"TTS DIRECT: Running command: {cmd}")
            
            # Execute in background process
            subprocess.Popen(cmd, shell=True)
            
            # Estimate speech duration
            word_count = len(clean_text.split())
            duration = max(1500, word_count * 300)  # Minimum 1.5 seconds
            
            # Set timer to end talking mode
            QtCore.QTimer.singleShot(duration, lambda: self.end_talking())
            
            print(f"TTS DIRECT: Speech initiated with duration: {duration}ms")
            
        except Exception as e:
            print(f"TTS DIRECT: Error in direct speech: {e}")
            traceback.print_exc()
            
            # Fallback to end talking mode after short delay
            QtCore.QTimer.singleShot(1000, lambda: self.end_talking())
    
    def end_talking(self):
        """End talking mode and play queued animations"""
        print("TTS: Ending talking mode")
        self.talking_mode = False
        self.talking_timer.stop()
        self.play_extra_animations()
    
    def say(self, text):
        """Convert text to speech and play it"""
        print(f"TTS: Attempting to speak text: '{text}'")
        self.talking_mode = True
        self.talking_timer.start(100)
        
        try:
            # Generate and play audio
            audio_file = system_tts(text)
            print(f"TTS: Audio file generated: {audio_file}")
            
            if audio_file and os.path.exists(audio_file):
                url = QtCore.QUrl.fromLocalFile(os.path.abspath(audio_file))
                content = QMediaContent(url)
                self.player.setMedia(content)
                
                # Debug player state
                print(f"TTS: Player state before play: {self.player.state()}")
                self.player.play()
                print(f"TTS: Player state after play: {self.player.state()}")
                
                # Fallback timer in case media status event doesn't fire
                QtCore.QTimer.singleShot(len(text.split()) * 500, 
                    lambda: self.check_speech_completed(audio_file))
            else:
                print("TTS: Failed to generate audio file - switching to direct speech")
                # Fallback to direct approach
                self.direct_speak(text)
        except Exception as e:
            print(f"TTS: Error in speech function: {e}")
            traceback.print_exc()
            # Error fallback - try direct speech
            self.direct_speak(text)
    
    def check_speech_completed(self, audio_file):
        """Fallback check to ensure speech completes even if media events fail"""
        if self.talking_mode:
            print("TTS: Speech completion fallback triggered")
            self.on_media_status_changed(QMediaPlayer.EndOfMedia)
            # Clean up audio file if it exists
            if audio_file and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                    print(f"TTS: Removed audio file: {audio_file}")
                except:
                    pass
    
    def on_media_status_changed(self, status):
        """Handle audio playback status changes"""
        print(f"Media status changed: {status}")
        if status == QMediaPlayer.EndOfMedia:
            print("Media playback completed")
            self.talking_mode = False
            self.talking_timer.stop()
            
            # Clean up the audio file if possible
            try:
                media = self.player.media()
                if not media.isNull():
                    url = media.canonicalUrl()
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if os.path.exists(file_path):
                            print(f"Cleaning up audio file: {file_path}")
                            os.remove(file_path)
            except Exception as e:
                print(f"Error cleaning up audio file: {e}")
            
            # Reset the player
            self.player.setMedia(QMediaContent())
            
            # Play the queued animations
            self.play_extra_animations()
    
    # --- Chat & AI Interaction ---
    def show_chat_dialog(self):
        """Show the persistent chat dialog"""
        if not self.chat_dialog or not self.chat_dialog.isVisible():
            welcome_text = "What's up, genius? Need some help or just wasting my time?"
            self.chat_dialog = PersistentChatDialog(welcome_text)
            self.chat_dialog.set_bonzi(self)
            
            # Position the dialog next to Bonzi
            pos = self.mapToGlobal(QtCore.QPoint(self.width(), 0))
            self.chat_dialog.move(pos)
            
            # Play talking animation
            self.say(welcome_text)
        
        self.chat_dialog.show()
        self.chat_dialog.raise_()
        self.chat_dialog.activateWindow()
    
    async def process_user_input_async(self, text, dialog):
        """Process user input from the chat dialog asynchronously"""
        print(f"Processing user input asynchronously: {text}")
        # Get response either from API or local fallback
        animations = []
        
        if ANTHROPIC_CLIENT:
            try:
                # Show a "thinking" message
                def show_thinking():
                    dialog.append_message("Thinking...", is_bonzi=True)
                QtCore.QTimer.singleShot(0, show_thinking)
                
                # Get the response from Claude
                response_text, animations = await self.get_ai_response_async(text)
                print(f"Got response: {response_text[:50]}...")
            except Exception as e:
                print(f"Error getting AI response: {e}")
                traceback.print_exc()
                response_text = random.choice(OFFLINE_RESPONSES)
        else:
            print("Anthropic client not available, using offline response")
            response_text = random.choice(OFFLINE_RESPONSES)
        
        # Update UI in the main thread
        def update_ui():
            print(f"UI: Updating chat dialog with response: '{response_text[:50]}...'")
            
            try:
                # Remove the thinking message if it exists
                cursor = dialog.chatHistory.textCursor()
                cursor.movePosition(QtGui.QTextCursor.End)
                document = dialog.chatHistory.document()
                
                # Check if there's any content before trying to find the last block
                if document.lineCount() > 0:
                    last_block = document.findBlockByLineNumber(document.lineCount() - 1)
                    if last_block.text().startswith("Bonzi: Thinking...") or last_block.text().startswith("Bonzi: Let me think"):
                        print("UI: Removing thinking message")
                        # Remove the thinking message
                        cursor.movePosition(QtGui.QTextCursor.End)
                        cursor.movePosition(QtGui.QTextCursor.PreviousBlock)
                        cursor.movePosition(QtGui.QTextCursor.PreviousBlock)
                        cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
                        cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor)
                        cursor.removeSelectedText()
                        
                        # Remove any extra blank lines
                        cursor.movePosition(QtGui.QTextCursor.End)
                        cursor.movePosition(QtGui.QTextCursor.PreviousBlock)
                        if cursor.block().text() == "":
                            cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
                            cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor)
                            cursor.removeSelectedText()
                
                # Add the real response
                print("UI: Adding response to dialog")
                dialog.append_message(response_text)
                dialog.chatHistory.repaint()  # Force a repaint
                
                # Set animations and speak
                self.extra_animations = animations
                
                # Ensure dialog is visible and in focus
                if not dialog.isVisible():
                    print("UI: Dialog not visible, showing it")
                    dialog.show()
                    dialog.raise_()
                    dialog.activateWindow()
                
                # Slight delay before speaking to ensure UI updates first
                QtCore.QTimer.singleShot(100, lambda: self.direct_speak(response_text))
                
            except Exception as e:
                print(f"UI: Error updating chat dialog: {e}")
                traceback.print_exc()
                # Fallback - try again with simple append
                try:
                    dialog.append_message(f"Response: {response_text}")
                    self.say(response_text)
                except:
                    print("UI: Critical failure in dialog update")
        
        # Execute in the main thread
        QtCore.QTimer.singleShot(0, update_ui)
    
    def process_user_input(self, text, dialog):
        """Synchronous wrapper for backward compatibility"""
        print(f"Processing user input: {text}")
        
        # Check if text is empty
        if not text or text.strip() == "":
            print("Empty input, ignoring")
            return
            
        # Add a separate UI thread update to show "Thinking..." immediately
        dialog.append_message("Let me think about that...", is_bonzi=True)
        
        # Process directly - synchronous approach for better reliability
        try:
            print("Starting direct processing...")
            
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": text})
            
            # Keep only the most recent max_history_items conversations
            if len(self.conversation_history) > self.max_history_items * 2:
                self.conversation_history = self.conversation_history[-self.max_history_items * 2:]
            
            # Build message history for API
            messages = list(self.conversation_history)  # Make a copy
            print(f"Using conversation history with {len(messages)} messages")
            
            # Prepare the message parameters
            message_params = {
                "model": CONFIG.get("model", "claude-3-haiku-20240307"),
                "max_tokens": CONFIG.get("max_tokens", 300),
                "temperature": CONFIG.get("temp", 1.0),
                "system": SYSTEM_PROMPT,
                "messages": messages
            }
            
            # Show "calling API" message
            def update_thinking():
                cursor = dialog.chatHistory.textCursor()
                cursor.movePosition(QtGui.QTextCursor.End)
                document = dialog.chatHistory.document()
                
                # Check if there's any content before trying to find the last block
                if document.lineCount() > 0:
                    last_block = document.findBlockByLineNumber(document.lineCount() - 1)
                    if last_block.text().startswith("Bonzi: Let me think"):
                        # Update the thinking message
                        message_format = QtGui.QTextCharFormat()
                        message_format.setForeground(QtGui.QColor("#800080"))
                        message_format.setFontItalic(True)
                        cursor.movePosition(QtGui.QTextCursor.End)
                        cursor.movePosition(QtGui.QTextCursor.PreviousBlock)
                        cursor.movePosition(QtGui.QTextCursor.PreviousBlock)
                        cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
                        cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor)
                        cursor.removeSelectedText()
                        cursor.insertText("Bonzi: Checking the time for you...", message_format)
                dialog.chatHistory.repaint()
            
            QtCore.QTimer.singleShot(500, update_thinking)
            
            # Make API call
            if ANTHROPIC_CLIENT:
                try:
                    # Try the API call 
                    response = ANTHROPIC_CLIENT.messages.create(**message_params)
                    print(f"Received API response: {response}")
                    
                    # Extract text from response
                    if not hasattr(response, 'content') or not response.content:
                        print("No content in response")
                        response_text = "Sorry, I received an empty response from my brain."
                        animations = []
                    else:
                        response_text = response.content[0].text if response.content else ""
                        print(f"Raw response text: {response_text[:100]}...")
                        
                        # Try to find and parse JSON in the response
                        json_match = re.search(r'({[\s\S]*?})', response_text)
                        animations = []
                        
                        if json_match:
                            try:
                                json_str = json_match.group(1)
                                print(f"Found JSON: {json_str}")
                                json_data = json.loads(json_str)
                                
                                # Extract dialogue text
                                if "dialogue" in json_data:
                                    response_text = json_data["dialogue"]
                                    print(f"Extracted dialogue: {response_text[:100]}...")
                                else:
                                    response_text = response_text.replace(json_str, "").strip()
                                
                                # Get animations
                                for anim in ["wave", "backflip", "glasses", "goodbye"]:
                                    if json_data.get(anim, False):
                                        animations.append(anim)
                                print(f"Animations: {animations}")
                            except json.JSONDecodeError as e:
                                print(f"JSON parse error: {e}")
                                # If JSON parsing fails, just use the text as is
                                pass
                        
                        # Clean up response text
                        response_text = re.sub(r'{.*?}', '', response_text, flags=re.DOTALL)
                        response_text = re.sub(r'\*.*?\*', '', response_text)
                        response_text = response_text.strip()
                        
                        if not response_text:
                            response_text = "I processed your request but got confused. Can you try again?"
                        
                        # Add random animations if none were specified
                        if not animations and random.random() > 0.7:
                            animations.append(random.choice(["wave", "backflip", "glasses"]))
                    
                    # Add the assistant's response to conversation history
                    self.conversation_history.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    print(f"API call error: {e}")
                    traceback.print_exc()
                    response_text = f"API error: {str(e)[:100]}..."
                    animations = []
            else:
                print("Anthropic client not available, using offline response")
                response_text = random.choice(OFFLINE_RESPONSES)
                animations = []
            
            # Remove the thinking message and show the real response
            def display_response():
                print(f"DISPLAY: Showing response: '{response_text}'")
                
                # Clear the thinking message
                try:
                    cursor = dialog.chatHistory.textCursor()
                    document = dialog.chatHistory.document()
                    
                    # Find and remove the "thinking" message
                    for i in range(document.blockCount()):
                        block = document.findBlockByNumber(i)
                        if "think" in block.text() or "Checking the time" in block.text():
                            # Select this block
                            cursor.setPosition(block.position())
                            cursor.setPosition(block.position() + block.length() - 1, QtGui.QTextCursor.KeepAnchor)
                            cursor.removeSelectedText()
                            # Remove any trailing newlines
                            cursor.deleteChar()
                            cursor.deleteChar()
                            break
                except Exception as e:
                    print(f"Error removing thinking message: {e}")
                
                # Add the response
                try:
                    dialog.append_message(response_text)
                    dialog.chatHistory.repaint()
                    
                    # Set animations and speak
                    self.extra_animations = animations
                    self.say(response_text)
                except Exception as e:
                    print(f"Error displaying response: {e}")
                    traceback.print_exc()
                    
                    # Last resort - try direct approach
                    try:
                        message_format = QtGui.QTextCharFormat()
                        message_format.setForeground(QtGui.QColor("#800080"))
                        cursor = dialog.chatHistory.textCursor()
                        cursor.movePosition(QtGui.QTextCursor.End)
                        cursor.insertText("\nBonzi: " + response_text + "\n\n", message_format)
                        dialog.chatHistory.setTextCursor(cursor)
                        dialog.chatHistory.ensureCursorVisible()
                        dialog.chatHistory.repaint()
                        self.say(response_text)
                    except Exception as e2:
                        print(f"Critical error displaying response: {e2}")
            
            # Show response after a short delay
            QtCore.QTimer.singleShot(100, display_response)
            
        except Exception as e:
            print(f"Error in synchronous processing: {e}")
            traceback.print_exc()
            
            # Show error in UI
            def show_error():
                error_msg = f"Sorry, I had a brain freeze: {str(e)[:100]}..."
                dialog.append_message(error_msg)
                self.say(error_msg)
            
            QtCore.QTimer.singleShot(0, show_error)
    
    async def get_ai_response_async(self, text):
        """Get response from Anthropic API asynchronously"""
        try:
            # Add input to conversation history
            self.conversation_history.append({"role": "user", "content": text})
            
            # Keep only the most recent max_history_items conversations
            if len(self.conversation_history) > self.max_history_items * 2:  # Each interaction is two messages
                self.conversation_history = self.conversation_history[-self.max_history_items * 2:]
            
            # Build message history for API
            messages = []
            
            # Include conversation history
            for message in self.conversation_history:
                messages.append(message)
            
            # If there's no history, just include the current user message
            if not messages:
                messages = [{"role": "user", "content": text}]
                
            print(f"Using conversation history with {len(messages)} messages")
            
            # Prepare the message parameters
            message_params = {
                "model": CONFIG.get("model", "claude-3-haiku-20240307"),
                "max_tokens": CONFIG.get("max_tokens", 300),  # Increased to 300 tokens for more complete responses
                "temperature": CONFIG.get("temp", 1.0),
                "system": SYSTEM_PROMPT,
                "messages": messages
            }
            
            print(f"Sending request to Claude API with parameters: {message_params}")
            
            # Make the API call - we're not using aiohttp directly since the Anthropic
            # SDK doesn't fully support asyncio yet
            try:
                response = ANTHROPIC_CLIENT.messages.create(**message_params)
                print(f"Received API response: {response}")
            except Exception as api_error:
                print(f"API call error: {api_error}")
                return f"API error: {str(api_error)[:100]}...", []
            
            # Extract text from response
            if not hasattr(response, 'content') or not response.content:
                print("No content in response")
                return "Sorry, I received an empty response from my brain.", []
                
            response_text = response.content[0].text if response.content else ""
            print(f"Raw response text: {response_text[:100]}...")
            
            # Extract the JSON part if present
            json_data = None
            animations = []
            
            # Try to find and parse JSON in the response
            json_match = re.search(r'({[\s\S]*?})', response_text)
            if json_match:
                try:
                    json_str = json_match.group(1)
                    print(f"Found JSON: {json_str}")
                    json_data = json.loads(json_str)
                    
                    # Extract dialogue text
                    if "dialogue" in json_data:
                        response_text = json_data["dialogue"]
                        print(f"Extracted dialogue: {response_text[:100]}...")
                    else:
                        response_text = response_text.replace(json_str, "").strip()
                    
                    # Get animations
                    for anim in ["wave", "backflip", "glasses", "goodbye"]:
                        if json_data.get(anim, False):
                            animations.append(anim)
                    print(f"Animations: {animations}")
                except json.JSONDecodeError as e:
                    print(f"JSON parse error: {e}")
                    # If JSON parsing fails, just use the text as is
                    pass
            else:
                print("No JSON found in response")
            
            # Clean up response text (remove markdown, JSON, etc.)
            response_text = re.sub(r'{.*?}', '', response_text, flags=re.DOTALL)
            response_text = re.sub(r'\*.*?\*', '', response_text)
            response_text = response_text.strip()
            
            if not response_text:
                response_text = "I processed your request but got confused. Can you try again?"
            
            # Add random animations if none were specified
            if not animations and random.random() > 0.7:
                animations.append(random.choice(["wave", "backflip", "glasses"]))
            
            print(f"Final response: {response_text[:100]}... with animations: {animations}")
            
            # Add the assistant's response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # Keep history within limits
            if len(self.conversation_history) > self.max_history_items * 2:
                self.conversation_history = self.conversation_history[-self.max_history_items * 2:]
                
            return response_text, animations
            
        except Exception as e:
            import traceback
            print(f"Error getting AI response: {e}")
            print(traceback.format_exc())
            
            # Add error response to history to maintain conversation flow
            error_response = f"Something went wrong: {str(e)[:100]}..."
            self.conversation_history.append({"role": "assistant", "content": error_response})
            
            return error_response, []

# ---------------------------
# Main Application
# ---------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    
    print("Starting BonziBuddy enhanced version...")
    
    # Validate Anthropic availability
    if ANTHROPIC_CLIENT:
        print(f"Anthropic client is available using model: {CONFIG.get('model')}")
    else:
        print("WARNING: Anthropic client is not available! Using offline responses.")
        if not ANTHROPIC_AVAILABLE:
            print("  - Anthropic SDK not installed or not importable")
        elif not CONFIG.get("api_enabled"):
            print("  - API is disabled in config.yaml")
        elif not CONFIG.get("anthropic_api_key"):
            print("  - API key is missing in config.yaml")
    
    # Apply custom font if available
    font_id = QtGui.QFontDatabase.addApplicationFont("Comic Sans MS")
    if font_id == -1:
        print("Warning: Could not load Comic Sans MS font, using system default")
    
    # Start the async loop in a separate thread
    def run_async_loop():
        print("Starting async event loop...")
        try:
            asyncio.set_event_loop(loop)
            # Signal that we're ready
            ready_event.set()
            # Run forever
            loop.run_forever()
            print("Event loop stopped")
        except Exception as e:
            print(f"Error in event loop: {e}")
            traceback.print_exc()
    
    # Start the async loop thread
    async_thread = threading.Thread(target=run_async_loop, daemon=True)
    async_thread.start()
    
    # Wait until the event loop is ready
    if not ready_event.wait(timeout=5.0):
        print("WARNING: Event loop didn't start in time!")
    
    # Verify the loop is running
    try:
        print("Testing async loop...")
        async def test_loop():
            return "OK"
            
        future = asyncio.run_coroutine_threadsafe(test_loop(), loop)
        result = future.result(timeout=2.0)
        print(f"Async loop test: {result}")
    except Exception as e:
        print(f"Async loop test failed: {e}")
        traceback.print_exc()
    
    # Create and show Bonzi
    print("Creating BonziBuddy...")
    bonzi = BonziBuddy()
    bonzi.show()
    
    # Show chat dialog immediately and make it always visible
    print("Opening chat dialog immediately...")
    bonzi.show_chat_dialog()  # Show immediately instead of using timer
    
    # Set up a recurring timer to ensure chat dialog remains visible
    dialog_check_timer = QtCore.QTimer()
    dialog_check_timer.timeout.connect(lambda: ensure_dialog_visible(bonzi))
    dialog_check_timer.start(5000)  # Check every 5 seconds
    
    def ensure_dialog_visible(bonzi):
        """Make sure chat dialog is visible"""
        if bonzi.chat_dialog and not bonzi.chat_dialog.isVisible():
            print("Dialog visibility check: Reopening chat dialog")
            bonzi.show_chat_dialog()
        else:
            print("Dialog visibility check: Dialog is visible")
    
    # Run the Qt event loop
    print("Starting Qt event loop...")
    result = app.exec_()
    
    # Clean up resources
    print("Shutting down...")
    if loop.is_running():
        loop.call_soon_threadsafe(loop.stop)
    
    # Give the loop time to shut down cleanly
    time.sleep(0.2)
    
    print("BonziBuddy exited.")
    sys.exit(result)

if __name__ == "__main__":
    main()
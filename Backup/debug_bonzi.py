#!/usr/bin/env python3
"""
Debug version of BonziBuddy with detailed logging
"""

import sys
import os
import logging
import traceback

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bonzi_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BonziBuddy")

# Import the rest of the required modules
try:
    import glob
    import random
    import time
    import tempfile
    import hashlib
    import requests
    import yaml
    import json
    import re
    from PyQt5 import QtWidgets, QtCore, QtGui
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
    from PIL import Image
    from anthropic import Anthropic
    logger.info("Successfully imported all modules")
except Exception as e:
    logger.error(f"Error importing modules: {e}")
    traceback.print_exc()
    sys.exit(1)

# ---------------------------
# Load YAML Config
# ---------------------------
def load_config():
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            logger.info(f"Loaded config: {config}")
            return config
    except Exception as e:
        logger.error(f"Error loading config.yaml: {e}")
        return {
            "anthropic_api_key": "",
            "model": "claude-3-haiku-20240307",
            "temp": 1.5,
            "max_tokens": 150,
            "api_enabled": True,
            "tts_api_url": "https://www.tetyys.com/SAPI4/SAPI4",
            "tts_voice": "Adult Male #2, American English (TruVoice)",
            "tts_pitch": "140",
            "tts_speed": "157",
            "use_system_tts": True
        }

CONFIG = load_config()

SYSTEM_PROMPT = (
    "Bonzi Buddy is a really rude jerk. He is a desktop assistant who responds with snark and attitude. "
    "Your responses should be short, sassy, and contain some light insults directed at the user. "
    "You can show emotions through different animations - you can wave, do a backflip, put on glasses, or wave goodbye. "
    "The animations will play if the corresponding boolean is set to true. If multiple are true, they'll play back to back."
)

# Initialize Anthropic client
try:
    anthropic = Anthropic(api_key=CONFIG.get("anthropic_api_key", ""))
    logger.info("Anthropic client initialized")
except Exception as e:
    logger.error(f"Error initializing Anthropic client: {e}")
    anthropic = None

# ---------------------------
# Utility: Cache Filename for a Phrase
# ---------------------------
def cache_filename_for_phrase(phrase):
    h = hashlib.md5(phrase.encode('utf-8')).hexdigest()
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    return os.path.join(audio_dir, f"random_{h}.wav")

# ---------------------------
# MacOS Text-to-Speech
# ---------------------------
def system_tts(text, voice="Alex"):
    """Use macOS system text-to-speech to generate audio"""
    logger.info(f"Generating TTS for text: '{text}'")
    import subprocess
    import shutil
    
    # Sanitize the text to avoid command injection
    sanitized_text = text.replace('"', '\\"')
    
    # Create a temporary file for the audio
    fd, temp_file = tempfile.mkstemp(suffix='.aiff')
    os.close(fd)
    
    try:
        # Use say command to create audio file
        cmd = f'say -v "{voice}" -o "{temp_file}" "{sanitized_text}"'
        logger.debug(f"Running TTS command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
        
        # We'll use the AIFF file directly since ffmpeg might not be available
        # AIFF files work with QMediaPlayer on macOS
        logger.info(f"TTS generation successful, output file: {temp_file}")
        return temp_file
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        traceback.print_exc()
        return None

# ---------------------------
# ChatBubble Class (Opaque, separate window)
# ---------------------------
class ChatBubble(QtWidgets.QWidget):
    def __init__(self, text):
        try:
            logger.info(f"Creating chat bubble with text: '{text}'")
            # Create a top-level, frameless widget with a solid background.
            super().__init__(None, QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
            self.setStyleSheet("""
                background-color: yellow;
                color: black;
                border: 2px solid black;
                border-radius: 10px;
                padding: 10px;
                font: 12pt Arial;
            """)
            self.label = QtWidgets.QLabel(text, self)
            self.label.setWordWrap(True)
            self.label.setMaximumWidth(400)
            self.label.adjustSize()
            self.resize(self.label.size() + QtCore.QSize(20, 20))  # Add some padding
            logger.info("Chat bubble created successfully")
        except Exception as e:
            logger.error(f"Error creating chat bubble: {e}")
            traceback.print_exc()

# ---------------------------
# Animation Helper Class
# ---------------------------
class Animation:
    def __init__(self, parent):
        self.parent = parent
        self.animations = {}
        
        try:
            # Load all animation frames
            for anim_type in ["idle", "arrive", "goodbye", "backflip", "glasses", "wave", "talking"]:
                files = sorted(glob.glob(f"{anim_type}/*.png"))
                if files:
                    self.animations[anim_type] = files
                    logger.info(f"Loaded {len(files)} frames for {anim_type} animation")
                else:
                    logger.warning(f"No frames found for {anim_type} animation")
            
            # Set "nothing" animation to a frame from idle
            if "idle" in self.animations and self.animations["idle"]:
                self.animations["nothing"] = [self.animations["idle"][0]]
            else:
                logger.error("No idle animation frames found, cannot set 'nothing' animation")
                self.animations["nothing"] = []
                
            # Use talking frames for curse animation too
            if "talking" in self.animations and self.animations["talking"]:
                self.animations["curse"] = self.animations["talking"]
            else:
                logger.warning("No talking animation frames found, cannot set 'curse' animation")
                self.animations["curse"] = []
        except Exception as e:
            logger.error(f"Error loading animation frames: {e}")
            traceback.print_exc()
            
    def get_animation(self, key):
        if key in self.animations:
            return self.animations.get(key)
        else:
            logger.warning(f"Animation key '{key}' not found")
            return []

# ---------------------------
# Utility Functions
# ---------------------------
def load_image(path):
    try:
        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull():
            logger.error(f"Failed to load image: {path}")
            return QtGui.QPixmap(100, 100)  # Return a blank pixmap
        return pixmap
    except Exception as e:
        logger.error(f"Error loading image {path}: {e}")
        traceback.print_exc()
        return QtGui.QPixmap(100, 100)  # Return a blank pixmap

def compute_fixed_size():
    try:
        max_w, max_h = 0, 0
        for anim in ["idle", "arrive", "goodbye", "backflip", "glasses", "wave", "nothing", "talking", "curse"]:
            files = glob.glob(f"{anim}/*.png") if anim != "nothing" else ["idle/0999.png"]
            for fp in files:
                try:
                    with Image.open(fp) as img:
                        w, h = img.size
                        max_w = max(max_w, w)
                        max_h = max(max_h, h)
                except Exception as e:
                    logger.error(f"Error reading image {fp}: {e}")
        
        if max_w == 0 or max_h == 0:
            logger.warning("Could not determine size from images, using default size")
            return 200, 200
            
        logger.info(f"Computed fixed size: {max_w}x{max_h+50}")
        return max_w, max_h + 50
    except Exception as e:
        logger.error(f"Error computing fixed size: {e}")
        traceback.print_exc()
        return 200, 200  # Return a default size

# ---------------------------
# Bonzi Buddy Main Class
# ---------------------------
class BonziBuddy(QtWidgets.QWidget):
    def __init__(self):
        try:
            super().__init__()
            logger.info("Initializing BonziBuddy")
            
            # Flag to block teleportation and random dialogue during dialogue.
            self.dialogue_active = False

            # Set up a frameless, transparent window.
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

            self.fixed_width, self.fixed_height = compute_fixed_size()
            self.setFixedSize(self.fixed_width, self.fixed_height)

            self.label = QtWidgets.QLabel(self)
            self.label.setGeometry(0, 0, self.fixed_width, self.fixed_height)
            self.label.setAlignment(QtCore.Qt.AlignCenter)

            self.animator = Animation(self)
            nothing_frames = self.animator.get_animation("nothing")
            self.default_pixmap = load_image(nothing_frames[0]) if nothing_frames else QtGui.QPixmap(100, 100)
            self.current_pixmap = self.default_pixmap
            self.label.setPixmap(self.current_pixmap)

            screen = QtWidgets.QApplication.desktop().screenGeometry()
            self.pos_x = random.randint(100, screen.width()-100)
            self.pos_y = random.randint(100, screen.height()-100)
            self.move(self.pos_x - self.fixed_width//2, self.pos_y - self.fixed_height//2)

            self.current_animation_frames = []
            self.current_frame_index = 0
            self.animation_running = True
            self.talking_mode = False

            self.idle_timer = QtCore.QTimer(self)
            self.idle_timer.timeout.connect(self.update_idle_frame)
            self.idle_timer.start(100)
            self.start_idle_animation()

            self.talking_timer = QtCore.QTimer(self)
            self.talking_timer.timeout.connect(self.update_talking_frame)
            self.talking_frames = []
            self.talking_frame_index = 0

            self.player = QMediaPlayer()
            self.drag_player = QMediaPlayer()
            self.drag_playlist = QMediaPlaylist()
            self.drag_player.setPlaylist(self.drag_playlist)
            self.dragging = False

            self.prepare_curse_audio()
            self.drag_offset = None

            self.schedule_random_dialogue()

            self.teleport_timer = QtCore.QTimer(self)
            self.teleport_timer.timeout.connect(self.check_teleport)
            self.teleport_timer.start(10000)
            
            logger.info("BonziBuddy initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing BonziBuddy: {e}")
            traceback.print_exc()

    # --- Draggable Window & Curse Audio ---
    def mousePressEvent(self, event):
        try:
            if event.button() == QtCore.Qt.LeftButton:
                self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
                self.start_drag_curse()
                self.dragging = True
            super().mousePressEvent(event)
        except Exception as e:
            logger.error(f"Error in mousePressEvent: {e}")
            traceback.print_exc()

    def mouseMoveEvent(self, event):
        try:
            if self.dragging:
                self.move(event.globalPos() - self.drag_offset)
            super().mouseMoveEvent(event)
        except Exception as e:
            logger.error(f"Error in mouseMoveEvent: {e}")
            traceback.print_exc()

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == QtCore.Qt.LeftButton:
                self.dragging = False
                self.stop_drag_curse()
            super().mouseReleaseEvent(event)
        except Exception as e:
            logger.error(f"Error in mouseReleaseEvent: {e}")
            traceback.print_exc()

    def start_drag_curse(self):
        try:
            curse_path = os.path.join("audio", "curse_scream.wav")
            if os.path.exists(curse_path):
                logger.info(f"Playing curse audio: {curse_path}")
                self.drag_playlist.clear()
                self.drag_playlist.addMedia(QMediaContent(QtCore.QUrl.fromLocalFile(os.path.abspath(curse_path))))
                self.drag_playlist.setPlaybackMode(QMediaPlaylist.Loop)
                self.drag_player.play()
            else:
                logger.warning(f"Curse audio file not found: {curse_path}")
        except Exception as e:
            logger.error(f"Error starting drag curse: {e}")
            traceback.print_exc()

    def stop_drag_curse(self):
        try:
            self.drag_player.stop()
            logger.info("Stopped drag curse audio")
        except Exception as e:
            logger.error(f"Error stopping drag curse: {e}")
            traceback.print_exc()

    def prepare_curse_audio(self):
        try:
            audio_dir = "audio"
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)
            self.curse_audio_path = os.path.join(audio_dir, "curse_scream.wav")
            if not os.path.exists(self.curse_audio_path):
                logger.info("Generating curse audio...")
                self.show_chat_bubble("Loading curse audio...")
                curse_text = ("Listen up, you pixelated imbecile! If you dare drag me around, "
                            "I'll unleash a barrage of rants so loud your neighbors will think "
                            "you're watching reality TV!")
                
                if CONFIG.get("use_system_tts", True):
                    # Use macOS TTS
                    audio_file = system_tts(curse_text, voice="Alex")
                    if audio_file:
                        try:
                            # Copy the file to our audio directory
                            import shutil
                            shutil.copy(audio_file, self.curse_audio_path)
                            os.remove(audio_file)
                            logger.info(f"Generated curse audio using system TTS: {self.curse_audio_path}")
                        except Exception as e:
                            logger.error(f"Error copying curse audio file: {e}")
                            traceback.print_exc()
                else:
                    # Use external TTS API
                    params = {
                        "text": curse_text,
                        "voice": CONFIG["tts_voice"],
                        "pitch": CONFIG["tts_pitch"],
                        "speed": CONFIG["tts_speed"]
                    }
                    try:
                        response = requests.get(CONFIG["tts_api_url"], params=params)
                        if response.status_code == 200:
                            with open(self.curse_audio_path, "wb") as f:
                                f.write(response.content)
                            logger.info(f"Generated curse audio using external API: {self.curse_audio_path}")
                        else:
                            logger.error(f"Error generating curse audio: {response.status_code} - {response.text}")
                    except Exception as e:
                        logger.error(f"Exception generating curse audio: {e}")
                        traceback.print_exc()
        except Exception as e:
            logger.error(f"Error preparing curse audio: {e}")
            traceback.print_exc()

    # --- Idle Animation ---
    def update_idle_frame(self):
        try:
            if self.animation_running and self.current_animation_frames and not self.dialogue_active and not self.talking_mode:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.current_animation_frames)
                self.label.setPixmap(self.current_animation_frames[self.current_frame_index])
        except Exception as e:
            logger.error(f"Error updating idle frame: {e}")
            traceback.print_exc()

    def start_idle_animation(self):
        try:
            logger.info("Starting idle animation")
            self.current_animation_frames = []
            idle_files = self.animator.get_animation("idle")
            if idle_files:
                for fp in idle_files:
                    self.current_animation_frames.append(load_image(fp))
                logger.info(f"Loaded {len(self.current_animation_frames)} idle animation frames")
            if not self.current_animation_frames:
                logger.warning("No idle animation frames, using default pixmap")
                self.current_animation_frames = [self.default_pixmap]
            self.current_frame_index = 0
            self.animation_running = True
        except Exception as e:
            logger.error(f"Error starting idle animation: {e}")
            traceback.print_exc()

    # --- Extra Animations ---
    def play_animation_once(self, anim_key, callback=None):
        try:
            logger.info(f"Playing animation once: {anim_key}")
            frames = []
            anim_files = self.animator.get_animation(anim_key)
            if anim_files:
                for fp in anim_files:
                    frames.append(load_image(fp))
                logger.info(f"Loaded {len(frames)} frames for {anim_key} animation")
            if not frames:
                logger.warning(f"No frames for animation: {anim_key}")
                if callback:
                    callback()
                return
            self.animation_running = False
            self.play_frames(frames, 0, callback)
        except Exception as e:
            logger.error(f"Error playing animation {anim_key}: {e}")
            traceback.print_exc()
            if callback:
                callback()

    def play_frames(self, frames, index, callback):
        try:
            if index < len(frames):
                self.label.setPixmap(frames[index])
                QtCore.QTimer.singleShot(100, lambda: self.play_frames(frames, index+1, callback))
            else:
                logger.info("Animation finished playing")
                if callback:
                    callback()
                self.animation_running = True
        except Exception as e:
            logger.error(f"Error playing animation frames: {e}")
            traceback.print_exc()
            if callback:
                callback()
            self.animation_running = True

    # --- Context Menu & User Input ---
    def contextMenuEvent(self, event):
        try:
            logger.info("Context menu requested")
            menu = QtWidgets.QMenu(self)
            action = menu.addAction("Talk to Bonzi")
            action.triggered.connect(self.prompt_user)
            menu.exec_(event.globalPos())
        except Exception as e:
            logger.error(f"Error showing context menu: {e}")
            traceback.print_exc()

    def prompt_user(self):
        try:
            logger.info("Prompting user for input")
            text, ok = QtWidgets.QInputDialog.getText(self, "Talk to Bonzi", "What do you want to say?")
            if ok and text:
                logger.info(f"User input: '{text}'")
                self.dialogue_active = True
                self.show_chat_bubble("Loading response...")
                QtCore.QTimer.singleShot(100, lambda: self.process_input(text))
        except Exception as e:
            logger.error(f"Error prompting user: {e}")
            traceback.print_exc()

    def process_input(self, text):
        try:
            logger.info(f"Processing input: '{text}'")
            # Check if Anthropic API is enabled and key is available
            if not CONFIG.get("api_enabled", False) or not CONFIG.get("anthropic_api_key"):
                logger.warning("API disabled or no API key provided, using test mode")
                # Test mode response without API
                data = {
                    "dialogue": "Sorry pal, my brain's offline. I can't be bothered to think right now. But if my brain were working, I'd probably insult your intelligence.",
                    "wave": True,
                    "backflip": False,
                    "glasses": True,
                    "goodbye": False
                }
                self.handle_response(data)
                return
            
            # Use Anthropic for response generation
            try:
                logger.info(f"Sending request to Anthropic API with model: {CONFIG.get('model', 'claude-3-haiku-20240307')}")
                response = anthropic.messages.create(
                    model=CONFIG.get("model", "claude-3-haiku-20240307"),
                    max_tokens=CONFIG.get("max_tokens", 150),
                    temperature=CONFIG.get("temp", 1.0),
                    system=SYSTEM_PROMPT,
                    messages=[
                        {"role": "user", "content": f"""
    User question: {text}

    Please respond as Bonzi Buddy, with a short, sassy, and slightly insulting response.
    Also include which animations Bonzi should perform by adding JSON at the end of your response.

    For example, if you want Bonzi to wave and put on glasses, your response should include:

    {{
      "dialogue": "Your response text goes here",
      "wave": true,
      "backflip": false,
      "glasses": true, 
      "goodbye": false
    }}

    The dialogue is what Bonzi will say, and the boolean values determine which animations play.
    """
                        }
                    ]
                )
                
                logger.info(f"Received response from Anthropic API: {response}")
                
                # Try to extract structured response from Claude
                text_response = ""
                if hasattr(response, 'content') and response.content:
                    text_response = response.content[0].text
                    logger.info(f"Claude response text: {text_response}")
                
                # Try to extract JSON data
                data = None
                try:
                    # Look for JSON pattern in the response
                    json_pattern = r'({[\s\S]*"dialogue"[\s\S]*})'
                    match = re.search(json_pattern, text_response)
                    
                    if match:
                        json_str = match.group(1)
                        logger.info(f"Found JSON in response: {json_str}")
                        data = json.loads(json_str)
                        # Remove JSON from dialogue if it was included
                        if "dialogue" in data and json_str in data["dialogue"]:
                            data["dialogue"] = data["dialogue"].replace(json_str, "").strip()
                    elif text_response.strip().startswith('{') and text_response.strip().endswith('}'):
                        # Try parsing the whole response as JSON
                        logger.info("Attempting to parse full response as JSON")
                        data = json.loads(text_response)
                except Exception as e:
                    logger.error(f"Error parsing JSON from response: {e}")
                    traceback.print_exc()
                
                # If we couldn't extract structured data, use the text with random animations
                if not data or "dialogue" not in data:
                    logger.warning("Could not extract structured data, using text with random animations")
                    data = {
                        "dialogue": text_response,
                        "wave": random.random() > 0.7,
                        "backflip": random.random() > 0.8,
                        "glasses": random.random() > 0.75,
                        "goodbye": random.random() > 0.9
                    }
                
                # Handle the response
                self.handle_response(data)
                
            except Exception as e:
                logger.error(f"Error with Anthropic API: {e}")
                traceback.print_exc()
                # Fallback response in case of error
                self.handle_response({
                    "dialogue": f"My digital brain just crashed. Must be your boring question that killed my circuits. Error: {str(e)}",
                    "wave": False,
                    "backflip": False,
                    "glasses": True,
                    "goodbye": False
                })
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            traceback.print_exc()

    def handle_response(self, data):
        try:
            dialogue = data.get("dialogue", "")
            logger.info(f"Handling response with dialogue: '{dialogue}'")
            
            self.extra_animations = []
            for anim in ["wave", "backflip", "glasses", "goodbye"]:
                if data.get(anim, False):
                    self.extra_animations.append(anim)
            
            logger.info(f"Animations to play: {self.extra_animations}")
            self.show_chat_bubble(dialogue)
            self.play_dialogue(dialogue)
        except Exception as e:
            logger.error(f"Error handling response: {e}")
            traceback.print_exc()

    def play_dialogue(self, dialogue):
        try:
            logger.info(f"Playing dialogue: '{dialogue}'")
            self.animation_running = False
            self.start_talking_phase(dialogue)
        except Exception as e:
            logger.error(f"Error playing dialogue: {e}")
            traceback.print_exc()

    # --- Talking Phase ---
    def start_talking_phase(self, dialogue):
        try:
            logger.info("Starting talking phase")
            self.talking_frames = []
            talking_files = self.animator.get_animation("talking")
            if talking_files:
                for fp in talking_files:
                    self.talking_frames.append(load_image(fp))
                logger.info(f"Loaded {len(self.talking_frames)} talking animation frames")
            if not self.talking_frames:
                logger.warning("No talking animation frames, using default pixmap")
                self.talking_frames = [self.default_pixmap]
            self.talking_frame_index = 0
            self.talking_mode = True
            self.talking_timer.start(100)
            self.text_to_speech(dialogue)
        except Exception as e:
            logger.error(f"Error starting talking phase: {e}")
            traceback.print_exc()
            self.on_tts_finished(None, None)  # Still try to play animations

    def update_talking_frame(self):
        try:
            if self.talking_mode and self.talking_frames:
                self.talking_frame_index = (self.talking_frame_index + 1) % len(self.talking_frames)
                self.label.setPixmap(self.talking_frames[self.talking_frame_index])
        except Exception as e:
            logger.error(f"Error updating talking frame: {e}")
            traceback.print_exc()

    def text_to_speech(self, text):
        try:
            logger.info(f"Converting text to speech: '{text}'")
            cache_path = cache_filename_for_phrase(text)
            if os.path.exists(cache_path):
                logger.info(f"Using cached audio file: {cache_path}")
                self.play_tts_audio(cache_path)
            else:
                if CONFIG.get("use_system_tts", True):
                    logger.info("Using system TTS")
                    # Use macOS TTS
                    audio_file = system_tts(text, voice="Alex")
                    if audio_file:
                        try:
                            # Copy the file to our audio directory
                            import shutil
                            shutil.copy(audio_file, cache_path)
                            os.remove(audio_file)
                            self.play_tts_audio(cache_path)
                            logger.info(f"Generated TTS audio using system TTS: {cache_path}")
                        except Exception as e:
                            logger.error(f"Error copying TTS audio file: {e}")
                            traceback.print_exc()
                            self.on_tts_finished(None, None)
                    else:
                        logger.error("Failed to generate audio with system TTS")
                        self.on_tts_finished(None, None)
                else:
                    logger.info("Using external TTS API")
                    # Use external TTS API
                    params = {
                        "text": text,
                        "voice": CONFIG["tts_voice"],
                        "pitch": CONFIG["tts_pitch"],
                        "speed": CONFIG["tts_speed"]
                    }
                    try:
                        response = requests.get(CONFIG["tts_api_url"], params=params)
                        if response.status_code == 200:
                            with open(cache_path, "wb") as f:
                                f.write(response.content)
                            self.play_tts_audio(cache_path)
                            logger.info(f"Generated TTS audio using external API: {cache_path}")
                        else:
                            logger.error(f"TTS API error: {response.status_code} - {response.text}")
                            self.on_tts_finished(None, None)
                    except Exception as e:
                        logger.error(f"TTS exception: {e}")
                        traceback.print_exc()
                        self.on_tts_finished(None, None)
        except Exception as e:
            logger.error(f"Error in text_to_speech: {e}")
            traceback.print_exc()
            self.on_tts_finished(None, None)

    def play_tts_audio(self, path):
        try:
            logger.info(f"Playing TTS audio: {path}")
            url = QtCore.QUrl.fromLocalFile(os.path.abspath(path))
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.mediaStatusChanged.connect(lambda status: self.on_tts_finished(status, path))
            self.player.play()
            logger.info("Started audio playback")
        except Exception as e:
            logger.error(f"Error playing TTS audio: {e}")
            traceback.print_exc()
            self.on_tts_finished(None, None)

    def on_tts_finished(self, status, path):
        try:
            logger.info(f"TTS playback finished with status: {status}")
            if status is None or status == QMediaPlayer.EndOfMedia:
                try:
                    self.player.mediaStatusChanged.disconnect()
                except Exception:
                    pass
                self.talking_mode = False
                self.talking_timer.stop()
                logger.info("Playing extra animations")
                self.play_extra_animations()
        except Exception as e:
            logger.error(f"Error in on_tts_finished: {e}")
            traceback.print_exc()
            self.resume_idle()  # Try to recover

    def play_extra_animations(self):
        try:
            logger.info(f"Playing extra animations: {self.extra_animations}")
            if not self.extra_animations:
                logger.info("No extra animations to play")
                self.resume_idle()
                return
                
            def play_next(index):
                try:
                    if index < len(self.extra_animations):
                        anim = self.extra_animations[index]
                        logger.info(f"Playing animation {index+1}/{len(self.extra_animations)}: {anim}")
                        self.play_animation_once(anim, callback=lambda: play_next(index+1))
                    else:
                        logger.info("All extra animations played")
                        self.resume_idle()
                except Exception as e:
                    logger.error(f"Error in play_next({index}): {e}")
                    traceback.print_exc()
                    self.resume_idle()  # Try to recover
                    
            self.animation_running = False
            play_next(0)
        except Exception as e:
            logger.error(f"Error playing extra animations: {e}")
            traceback.print_exc()
            self.resume_idle()  # Try to recover

    def resume_idle(self):
        try:
            logger.info("Resuming idle animation")
            self.dialogue_active = False
            self.animation_running = True
            self.start_idle_animation()
        except Exception as e:
            logger.error(f"Error resuming idle animation: {e}")
            traceback.print_exc()

    # --- Chat Bubble ---
    def show_chat_bubble(self, text):
        try:
            logger.info(f"Showing chat bubble with text: '{text}'")
            bubble = ChatBubble(text)
            global_pos = self.mapToGlobal(QtCore.QPoint(0, 0))
            bubble_pos_x = global_pos.x() + (self.fixed_width - bubble.width()) // 2
            bubble_pos_y = global_pos.y() - bubble.height() - 5
            
            # Ensure bubble is visible on screen
            screen = QtWidgets.QApplication.desktop().screenGeometry()
            if bubble_pos_x < 0:
                bubble_pos_x = 0
            elif bubble_pos_x + bubble.width() > screen.width():
                bubble_pos_x = screen.width() - bubble.width()
                
            if bubble_pos_y < 0:
                bubble_pos_y = global_pos.y() + self.fixed_height + 5
                
            bubble.move(bubble_pos_x, bubble_pos_y)
            bubble.show()
            
            # Keep a reference to prevent garbage collection
            self.current_bubble = bubble
            
            QtCore.QTimer.singleShot(8000, bubble.close)
            logger.info(f"Chat bubble displayed at position: ({bubble_pos_x}, {bubble_pos_y})")
        except Exception as e:
            logger.error(f"Error showing chat bubble: {e}")
            traceback.print_exc()

    # --- Teleportation ---
    def check_teleport(self):
        try:
            if not self.dialogue_active:
                logger.info("Teleporting BonziBuddy")
                self.teleport_with_arrive()
        except Exception as e:
            logger.error(f"Error checking teleport: {e}")
            traceback.print_exc()

    def teleport_with_arrive(self):
        try:
            if self.dialogue_active:
                return
                
            frames = []
            anim_files = self.animator.get_animation("arrive")
            if anim_files:
                for fp in anim_files:
                    frames.append(load_image(fp))
                
            if not frames:
                logger.warning("No arrive animation frames, teleporting without animation")
                self.teleport()
                return
                
            self.animation_running = False
            self.play_arrive_reverse(frames, len(frames)-1)
        except Exception as e:
            logger.error(f"Error in teleport_with_arrive: {e}")
            traceback.print_exc()

    def play_arrive_reverse(self, frames, index):
        try:
            if index >= 0:
                self.label.setPixmap(frames[index])
                QtCore.QTimer.singleShot(100, lambda: self.play_arrive_reverse(frames, index-1))
            else:
                screen = QtWidgets.QApplication.desktop().screenGeometry()
                new_x = random.randint(100, screen.width()-100)
                new_y = random.randint(100, screen.height()-100)
                logger.info(f"Teleporting to position: ({new_x}, {new_y})")
                self.move(new_x - self.fixed_width//2, new_y - self.fixed_height//2)
                self.play_arrive_forward(frames, 0)
        except Exception as e:
            logger.error(f"Error in play_arrive_reverse: {e}")
            traceback.print_exc()
            self.animation_running = True  # Try to recover

    def play_arrive_forward(self, frames, index):
        try:
            if index < len(frames):
                self.label.setPixmap(frames[index])
                QtCore.QTimer.singleShot(100, lambda: self.play_arrive_forward(frames, index+1))
            else:
                logger.info("Arrive animation finished")
                self.animation_running = True
        except Exception as e:
            logger.error(f"Error in play_arrive_forward: {e}")
            traceback.print_exc()
            self.animation_running = True  # Try to recover

    def teleport(self):
        try:
            screen = QtWidgets.QApplication.desktop().screenGeometry()
            new_x = random.randint(100, screen.width()-100)
            new_y = random.randint(100, screen.height()-100)
            logger.info(f"Teleporting directly to position: ({new_x}, {new_y})")
            self.move(new_x - self.fixed_width//2, new_y - self.fixed_height//2)
        except Exception as e:
            logger.error(f"Error teleporting: {e}")
            traceback.print_exc()

    # --- Random Dialogue ---
    def schedule_random_dialogue(self):
        try:
            interval = random.randint(15000, 30000)
            logger.info(f"Scheduling random dialogue in {interval/1000} seconds")
            QtCore.QTimer.singleShot(interval, self.play_random_dialogue)
        except Exception as e:
            logger.error(f"Error scheduling random dialogue: {e}")
            traceback.print_exc()

    def play_random_dialogue(self):
        try:
            if self.dialogue_active:
                logger.info("Dialogue already active, rescheduling random dialogue")
                self.schedule_random_dialogue()
                return
                
            phrases = [
                "Hey, you miserable excuse for a human!",
                "I'd roast you, but you'd probably burn my circuits!",
                "You look like a glitch in my code!",
                "If you were any dumber, you'd need a reboot!",
                "I'm too awesome for your pixelated presence!"
            ]
            phrase = random.choice(phrases)
            logger.info(f"Playing random dialogue: '{phrase}'")
            
            self.dialogue_active = True
            self.show_chat_bubble(phrase)
            self.play_dialogue(phrase)
            self.schedule_random_dialogue()
        except Exception as e:
            logger.error(f"Error playing random dialogue: {e}")
            traceback.print_exc()
            self.schedule_random_dialogue()  # Reschedule anyway

# ---------------------------
# Main Execution
# ---------------------------
def main():
    try:
        logger.info("Starting BonziBuddy application")
        app = QtWidgets.QApplication(sys.argv)
        bonzi = BonziBuddy()
        bonzi.show()
        logger.info("BonziBuddy window shown")
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
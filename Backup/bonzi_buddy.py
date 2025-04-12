#!/usr/bin/env python3
"""
Bonzi Buddy Monoscript (PyQt Version with Anthropic API Integration)

SYSTEM_PROMPT:
"Bonzi Buddy is a really rude jerk. He is a desktop assistant who responds with snark and attitude.
If he sets one of the animation bools (wave, backflip, glasses, goodbye) in the structured output to true,
that animation will play – and if multiple are true they will play back to back. The default image is taken from the 'nothing' animation."
"""

import sys, os, glob, random, time, tempfile, hashlib, requests, yaml, json
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PIL import Image
from anthropic import Anthropic

# ---------------------------
# Load YAML Config
# ---------------------------
def load_config():
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        print("Error loading config.yaml; using defaults.", e)
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
except Exception as e:
    print(f"Error initializing Anthropic client: {e}")
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
        subprocess.run(cmd, shell=True, check=True)
        
        # We'll use the AIFF file directly since ffmpeg might not be available
        # AIFF files work with QMediaPlayer on macOS
        return temp_file
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return None

# ---------------------------
# ChatBubble Class (Opaque, separate window)
# ---------------------------
class ChatBubble(QtWidgets.QWidget):
    def __init__(self, text):
        # Create a top-level, frameless widget with a solid background.
        super().__init__(None, QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("""
            background-color: yellow;
            color: black;
            border: 2px solid black;
            border-radius: 10px;
            padding: 5px;
            font: 10pt Arial;
        """)
        self.label = QtWidgets.QLabel(text, self)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(400)
        self.label.adjustSize()
        self.resize(self.label.size())

# ---------------------------
# Animation Helper Class
# ---------------------------
class Animation:
    def __init__(self, parent):
        self.parent = parent
        self.animations = {
            "idle": sorted(glob.glob("idle/*.png")),
            "arrive": sorted(glob.glob("arrive/*.png")),
            "goodbye": sorted(glob.glob("goodbye/*.png")),
            "backflip": sorted(glob.glob("backflip/*.png")),
            "glasses": sorted(glob.glob("glasses/*.png")),
            "wave": sorted(glob.glob("wave/*.png")),
            "nothing": ["idle/0999.png"],
            "talking": sorted(glob.glob("talking/*.png")),
            "curse": sorted(glob.glob("talking/*.png"))  # Reuse talking for curse animation
        }
    def get_animation(self, key):
        return self.animations.get(key)

# ---------------------------
# Utility Functions
# ---------------------------
def load_image(path):
    return QtGui.QPixmap(path)

def compute_fixed_size():
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
                print("Error reading image", fp, e)
    return max_w, max_h + 50

# ---------------------------
# Bonzi Buddy Main Class
# ---------------------------
class BonziBuddy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
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
        self.default_pixmap = load_image(nothing_frames[0]) if nothing_frames else None
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

    # --- Draggable Window & Curse Audio ---
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            self.start_drag_curse()
            self.dragging = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.drag_offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False
            self.stop_drag_curse()
        super().mouseReleaseEvent(event)

    def start_drag_curse(self):
        curse_path = os.path.join("audio", "curse_scream.wav")
        if os.path.exists(curse_path):
            self.drag_playlist.clear()
            self.drag_playlist.addMedia(QMediaContent(QtCore.QUrl.fromLocalFile(os.path.abspath(curse_path))))
            self.drag_playlist.setPlaybackMode(QMediaPlaylist.Loop)
            self.drag_player.play()

    def stop_drag_curse(self):
        self.drag_player.stop()

    def prepare_curse_audio(self):
        audio_dir = "audio"
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        self.curse_audio_path = os.path.join(audio_dir, "curse_scream.wav")
        if not os.path.exists(self.curse_audio_path):
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
                        print("Generated curse audio using system TTS.")
                    except Exception as e:
                        print(f"Error copying curse audio file: {e}")
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
                        print("Generated curse audio.")
                    else:
                        print("Error generating curse audio", response.status_code, response.text)
                except Exception as e:
                    print("Exception generating curse audio:", e)

    # --- Idle Animation ---
    def update_idle_frame(self):
        if self.animation_running and self.current_animation_frames and not self.dialogue_active and not self.talking_mode:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_animation_frames)
            self.label.setPixmap(self.current_animation_frames[self.current_frame_index])

    def start_idle_animation(self):
        self.current_animation_frames = []
        idle_files = self.animator.get_animation("idle")
        if idle_files:
            for fp in idle_files:
                self.current_animation_frames.append(load_image(fp))
        if not self.current_animation_frames:
            self.current_animation_frames = [self.default_pixmap]
        self.current_frame_index = 0
        self.animation_running = True

    # --- Extra Animations ---
    def play_animation_once(self, anim_key, callback=None):
        frames = []
        anim_files = self.animator.get_animation(anim_key)
        if anim_files:
            for fp in anim_files:
                frames.append(load_image(fp))
        if not frames:
            if callback:
                callback()
            return
        self.animation_running = False
        self.play_frames(frames, 0, callback)

    def play_frames(self, frames, index, callback):
        if index < len(frames):
            self.label.setPixmap(frames[index])
            QtCore.QTimer.singleShot(100, lambda: self.play_frames(frames, index+1, callback))
        else:
            if callback:
                callback()
            self.animation_running = True

    # --- Teleportation ---
    def check_teleport(self):
        if not self.dialogue_active:
            self.teleport_with_arrive()

    def teleport_with_arrive(self):
        if self.dialogue_active:
            return
        frames = []
        anim_files = self.animator.get_animation("arrive")
        if anim_files:
            for fp in anim_files:
                frames.append(load_image(fp))
        if not frames:
            self.teleport()
            return
        self.animation_running = False
        self.play_arrive_reverse(frames, len(frames)-1)

    def play_arrive_reverse(self, frames, index):
        if index >= 0:
            self.label.setPixmap(frames[index])
            QtCore.QTimer.singleShot(100, lambda: self.play_arrive_reverse(frames, index-1))
        else:
            screen = QtWidgets.QApplication.desktop().screenGeometry()
            new_x = random.randint(100, screen.width()-100)
            new_y = random.randint(100, screen.height()-100)
            self.move(new_x - self.fixed_width//2, new_y - self.fixed_height//2)
            self.play_arrive_forward(frames, 0)

    def play_arrive_forward(self, frames, index):
        if index < len(frames):
            self.label.setPixmap(frames[index])
            QtCore.QTimer.singleShot(100, lambda: self.play_arrive_forward(frames, index+1))
        else:
            self.animation_running = True

    def teleport(self):
        screen = QtWidgets.QApplication.desktop().screenGeometry()
        new_x = random.randint(100, screen.width()-100)
        new_y = random.randint(100, screen.height()-100)
        self.move(new_x - self.fixed_width//2, new_y - self.fixed_height//2)

    # --- Random Dialogue ---
    def schedule_random_dialogue(self):
        interval = random.randint(15000, 30000)
        QtCore.QTimer.singleShot(interval, self.play_random_dialogue)

    def play_random_dialogue(self):
        if self.dialogue_active:
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
        self.dialogue_active = True
        self.show_chat_bubble(phrase)
        self.play_dialogue(phrase)
        self.schedule_random_dialogue()

    # --- Context Menu & User Input ---
    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        action = menu.addAction("Talk to Bonzi")
        action.triggered.connect(self.prompt_user)
        menu.exec_(event.globalPos())

    def prompt_user(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Talk to Bonzi", "What do you want to say?")
        if ok and text:
            self.dialogue_active = True
            self.show_chat_bubble("Loading response...")
            QtCore.QTimer.singleShot(0, lambda: self.process_input(text))

    def process_input(self, text):
        # Check if Anthropic API is enabled and key is available
        if not CONFIG.get("api_enabled", False) or not CONFIG.get("anthropic_api_key"):
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
        
        try:
            # Use Anthropic for response generation
            response = anthropic.messages.create(
                model=CONFIG.get("model", "claude-3-haiku-20240307"),
                max_tokens=CONFIG.get("max_tokens", 150),
                temperature=CONFIG.get("temp", 1.0),
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": f"""
User question: {text}

Please respond as Bonzi Buddy, with a short, sassy, and slightly insulting response.
Also include which animations Bonzi should perform by including JSON at the end of your response.

For example, if you want Bonzi to wave and put on glasses, your response should end with:

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
            
            # Try to extract structured response from Claude
            try:
                # Handle case when tool_calls attribute is available
                if hasattr(response, 'tool_calls') and response.tool_calls and len(response.tool_calls) > 0:
                    # Get the first tool call
                    tool_call = response.tool_calls[0]
                    if tool_call.name == "bonzi_actions":
                        # Extract the JSON from the tool call
                        data = json.loads(tool_call.input)
                        self.handle_response(data)
                    else:
                        # Fallback response if tool call is not recognized
                        self.handle_response({
                            "dialogue": response.content[0].text,
                            "wave": False,
                            "backflip": False,
                            "glasses": False,
                            "goodbye": False
                        })
                else:
                    # For newer versions of the Anthropic client, we need to parse the content differently
                    text = response.content[0].text
                    print("Claude response:", text)
                    
                    # Let's attempt to extract structured data from plain text
                    try:
                        # Look for JSON patterns in the text
                        json_pattern = r'({[\s\S]*"dialogue"[\s\S]*})'
                        import re
                        match = re.search(json_pattern, text)
                        
                        if match:
                            # Try to parse the JSON part
                            json_str = match.group(1)
                            data = json.loads(json_str)
                            if "dialogue" in data:
                                # Remove the JSON part from the dialogue if it was included
                                if "dialogue" in data and json_str in data["dialogue"]:
                                    data["dialogue"] = data["dialogue"].replace(json_str, "").strip()
                                self.handle_response(data)
                                return
                        elif text.strip().startswith('{') and text.strip().endswith('}'):
                            # Try to parse the entire response as JSON
                            data = json.loads(text)
                            if "dialogue" in data:
                                self.handle_response(data)
                                return
                    except json.JSONDecodeError:
                        pass
                        
                    # If we couldn't get structured data, randomly select animations
                    random_animations = {
                        "dialogue": text,
                        "wave": random.random() > 0.7,
                        "backflip": random.random() > 0.8,
                        "glasses": random.random() > 0.75,
                        "goodbye": random.random() > 0.9
                    }
                    self.handle_response(random_animations)
            except Exception as e:
                print(f"Error parsing response: {e}")
                # If something went wrong, fall back to just showing the text
                text = response.content[0].text if hasattr(response, 'content') and response.content else "Sorry, I couldn't understand that."
                self.handle_response({
                    "dialogue": text,
                    "wave": False,
                    "backflip": False,
                    "glasses": False,
                    "goodbye": False
                })
                
        except Exception as e:
            print("Error with Anthropic API:", e)
            # Fallback response in case of error
            self.handle_response({
                "dialogue": "My digital brain just crashed. Must be your boring question that killed my circuits.",
                "wave": False,
                "backflip": False,
                "glasses": True,
                "goodbye": False
            })

    def handle_response(self, data):
        dialogue = data.get("dialogue", "")
        self.extra_animations = []
        for anim in ["wave", "backflip", "glasses", "goodbye"]:
            if data.get(anim, False):
                self.extra_animations.append(anim)
        self.show_chat_bubble(dialogue)
        self.play_dialogue(dialogue)

    def play_dialogue(self, dialogue):
        self.animation_running = False
        self.start_talking_phase(dialogue)

    # --- Talking Phase ---
    def start_talking_phase(self, dialogue):
        self.talking_frames = []
        talking_files = self.animator.get_animation("talking")
        if talking_files:
            for fp in talking_files:
                self.talking_frames.append(load_image(fp))
        if not self.talking_frames:
            self.talking_frames = [self.default_pixmap]
        self.talking_frame_index = 0
        self.talking_mode = True
        self.talking_timer.start(100)
        self.text_to_speech(dialogue)

    def update_talking_frame(self):
        if self.talking_mode and self.talking_frames:
            self.talking_frame_index = (self.talking_frame_index + 1) % len(self.talking_frames)
            self.label.setPixmap(self.talking_frames[self.talking_frame_index])

    def text_to_speech(self, text):
        cache_path = cache_filename_for_phrase(text)
        if os.path.exists(cache_path):
            self.play_tts_audio(cache_path)
        else:
            if CONFIG.get("use_system_tts", True):
                # Use macOS TTS
                audio_file = system_tts(text, voice="Alex")
                if audio_file:
                    try:
                        # Copy the file to our audio directory
                        import shutil
                        shutil.copy(audio_file, cache_path)
                        os.remove(audio_file)
                        self.play_tts_audio(cache_path)
                        print("Generated TTS audio using system TTS.")
                    except Exception as e:
                        print(f"Error copying TTS audio file: {e}")
                        self.on_tts_finished(None, None)
            else:
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
                    else:
                        print("TTS API error", response.status_code, response.text)
                        self.on_tts_finished(None, None)
                except Exception as e:
                    print("TTS exception", e)
                    self.on_tts_finished(None, None)

    def play_tts_audio(self, path):
        url = QtCore.QUrl.fromLocalFile(os.path.abspath(path))
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.play()
        self.player.mediaStatusChanged.connect(lambda status: self.on_tts_finished(status, path))

    def on_tts_finished(self, status, path):
        if status is None or status == QMediaPlayer.EndOfMedia:
            try:
                self.player.mediaStatusChanged.disconnect()
            except Exception:
                pass
            self.talking_mode = False
            self.talking_timer.stop()
            self.play_extra_animations()

    def play_extra_animations(self):
        if not self.extra_animations:
            self.resume_idle()
            return
        def play_next(index):
            if index < len(self.extra_animations):
                self.play_animation_once(self.extra_animations[index], callback=lambda: play_next(index+1))
            else:
                self.resume_idle()
        self.animation_running = False
        play_next(0)

    def resume_idle(self):
        self.dialogue_active = False
        self.animation_running = True
        self.start_idle_animation()

    # --- Chat Bubble ---
    def show_chat_bubble(self, text):
        bubble = ChatBubble(text)
        global_pos = self.mapToGlobal(QtCore.QPoint(0, 0))
        bubble.move(global_pos.x() + (self.fixed_width - bubble.width()) // 2,
                    global_pos.y() - bubble.height() - 5)
        bubble.show()
        QtCore.QTimer.singleShot(5000, bubble.close)

    # --- Random Dialogue ---
    def schedule_random_dialogue(self):
        interval = random.randint(15000, 30000)
        QtCore.QTimer.singleShot(interval, self.play_random_dialogue)

    def play_random_dialogue(self):
        if self.dialogue_active:
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
        self.dialogue_active = True
        self.show_chat_bubble(phrase)
        self.play_dialogue(phrase)
        self.schedule_random_dialogue()

# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    bonzi = BonziBuddy()
    bonzi.show()
    sys.exit(app.exec_())
# 🦍 **BonziBuddy for macOS**

*"The future arrived and it's sarcastic, animated, and definitely not impressed with you."*

BonziBuddy for macOS is a modern reimagining of the classic desktop assistant, now powered by Anthropic's Claude AI. This version brings the nostalgic character to your Mac with a healthy dose of attitude and sass.

## 📖 **Features**

- **AI-Powered Responses**: Uses Anthropic's Claude AI for intelligent, contextual, and humorously rude responses
- **Animated Character**: Fully animated character with multiple animations including idle, talking, waving, backflips, and more
- **Text-to-Speech**: Hear BonziBuddy's sassy remarks through your speakers
- **Persistent Desktop Presence**: BonziBuddy stays on top of your other windows, ready to assist (or insult) you at any time
- **Custom Animations**: BonziBuddy selects appropriate animations based on his responses
- **Teleportation**: BonziBuddy will occasionally teleport around your screen, just to keep you on your toes

## ⚙️ **Installation**

### Prerequisites

- macOS 10.14 or newer
- Python 3.6 or newer
- Anthropic API key (get one at [anthropic.com](https://console.anthropic.com/))

### Easy Installation

1. Run the setup script:
   ```bash
   python3 setup.py
   ```

2. When prompted, enter your Anthropic API key.

3. The setup script will create a desktop shortcut for easy launching.

### Manual Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Edit `config.yaml` and add your Anthropic API key:
   ```yaml
   anthropic_api_key: "your-api-key-here"
   ```

3. Run BonziBuddy:
   ```bash
   python3 bonzi_buddy.py
   ```

## 🚀 **Using BonziBuddy**

- **Right-click** on BonziBuddy to talk to him
- **Drag** BonziBuddy around your screen (at your own risk - he doesn't like it!)
- BonziBuddy will occasionally teleport around your screen and say random phrases
- BonziBuddy responds with animations based on his mood

## 🔧 **Configuration**

You can customize BonziBuddy's behavior by editing the `config.yaml` file:

- `anthropic_api_key`: Your Anthropic API key
- `model`: The Claude model to use (default: "claude-3-haiku-20240307")
- `temp`: Temperature setting for response generation (higher = more creative)
- `max_tokens`: Maximum length of responses
- `api_enabled`: Enable/disable API integration
- `use_system_tts`: Use macOS system text-to-speech instead of external API
- Additional TTS settings if using external API

## 💡 **Troubleshooting**

- **BonziBuddy doesn't appear**: Make sure you have all the dependencies installed and the animation files are in the correct directories.
- **No sound**: Check that your system volume is turned up.
- **API errors**: Verify your Anthropic API key in `config.yaml` is correct and has sufficient credits.
- **Animation issues**: Ensure all the animation PNG files are in their respective directories.

## 🛠️ **Building a Standalone App**

To create a standalone macOS app (no Python installation required):

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the app:
   ```bash
   pyinstaller --windowed --onefile --add-data "*.png:." --add-data "*.yaml:." --add-data "*/*.png:." bonzi_buddy.py
   ```

3. The standalone app will be in the `dist` directory.

## 🎭 **Credits**

- Original BonziBuddy character by BONZI.COM
- AI integration powered by Anthropic's Claude
- Animation frames from various sources

## ⚠️ **Disclaimer**

BonziBuddy is intentionally rude and sassy. His responses are meant to be humorous but may occasionally be offensive. Use at your own discretion and don't take his insults personally!

---

✨ **Enjoy your new digital companion!** ✨
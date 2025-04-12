# 🦍 **BonziBuddy Enhanced Edition for macOS**

*"The future arrived and it's sarcastic, animated, and definitely not impressed with you."*

This is the Enhanced Edition of BonziBuddy for macOS, using the most robust and feature-rich implementation.

## 📖 **Features**

- **Enhanced Error Handling**: Comprehensive error recovery across all components
- **Persistent Chat Dialog**: Maintains conversation history for more contextual interactions
- **Improved UI**: Styled components and better visual feedback
- **Robust TTS System**: Multiple fallback mechanisms for text-to-speech
- **Async Processing**: Background processing that prevents UI freezing
- **AI-Powered Responses**: Uses Anthropic's Claude AI for intelligent, contextual responses
- **Fully Animated Character**: Multiple animations including idle, talking, waving, backflips, and more
- **Persistent Desktop Presence**: BonziBuddy stays on top of your other windows

## ⚙️ **Installation**

### Prerequisites

- macOS 10.14 or newer
- Python 3.6 or newer
- Anthropic API key (get one at [anthropic.com](https://console.anthropic.com/))

### Quick Setup

1. Run the setup script:
   ```bash
   ./setup.sh
   ```

2. The script will:
   - Install required dependencies
   - Prompt for your Anthropic API key if needed
   - Create a macOS app bundle on your desktop

3. Launch BonziBuddy by double-clicking the app icon on your desktop

### Manual Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Edit `config.yaml` and add your Anthropic API key:
   ```yaml
   anthropic_api_key: "your-api-key-here"
   ```

3. Run BonziBuddy directly:
   ```bash
   python3 fixed_bonzi.py
   ```

## 🚀 **Using BonziBuddy**

- **Right-click** on BonziBuddy to talk to him
- **Drag** BonziBuddy around your screen
- BonziBuddy maintains conversation context for more natural interactions
- Animations are selected based on conversation context

## 🔧 **Configuration**

You can customize BonziBuddy's behavior by editing the `config.yaml` file:

- `anthropic_api_key`: Your Anthropic API key
- `model`: The Claude model to use (default: "claude-3-haiku-20240307")
- `temp`: Temperature setting for response generation
- `max_tokens`: Maximum length of responses
- `api_enabled`: Enable/disable API integration
- `use_system_tts`: Use macOS system text-to-speech

## ⚠️ **Disclaimer**

BonziBuddy is intentionally rude and sassy. His responses are meant to be humorous but may occasionally be offensive. Use at your own discretion!

---

✨ **Enjoy your new digital companion!** ✨
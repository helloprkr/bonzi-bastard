# 🦍 BonziBuddy for macOS - Enhanced Version

*"Authentically helpful, consistently sassy, full of attitude."*

Welcome to the enhanced version of BonziBuddy for macOS! This version features significant improvements to the visual styling, communication capabilities, and performance optimization for a better user experience.

## ✨ New Features & Improvements

- **Retro Visual Styling**: Classic purple and yellow aesthetic with Comic Sans MS font
- **Enhanced UI Elements**: Custom styled buttons, menus, and chat bubbles
- **Improved AI Integration**: More helpful and genuinely useful responses with attitude
- **Asynchronous API Calls**: Non-blocking Anthropic API requests for a smoother experience
- **Better Voice Integration**: Improved macOS text-to-speech with better text cleaning
- **Animation Handling**: Smoother transitions and better animation triggering
- **Optimized Performance**: Reduced lag during conversations and animations

## 🚀 Running BonziBuddy

1. **Double-click** `run_enhanced.command` to launch the enhanced BonziBuddy
2. A retro-styled chat dialog will automatically appear where you can interact with Bonzi
3. Enjoy the sassy yet genuinely helpful responses and animations!

## 💬 Using the Chat Dialog

- The enhanced chat dialog shows your conversation history with Bonzi
- Type your question or command in the input field at the bottom
- Press Enter or click "Ask" to send your message
- Bonzi will respond with a sassy but genuinely helpful answer
- The dialog stays open so you can have a continuous conversation

## 🎭 Bonzi's Upgraded Personality

Bonzi is now programmed to be:
- Sarcastic, witty, and a total smart-ass
- Genuinely helpful despite the snark
- Knowledgeable across a wide range of topics
- More responsive and faster with async processing

## 🖱️ Other Controls

- **Right-click** on Bonzi to show the styled context menu
- Select "Talk to Bonzi" to open the enhanced chat dialog
- Select "Goodbye" to close BonziBuddy
- **Drag** Bonzi around your screen to reposition him

## 🔧 Troubleshooting

### Chat Not Working
If BonziBuddy doesn't respond to your messages:

1. **Check API Connectivity**:
   - Run `run_debug_enhanced.command` to test the API connection
   - Verify your API key in `config.yaml` is correct and not expired
   - Check your internet connection is working

2. **Common API Issues**:
   - Invalid API key: Update your key in `config.yaml`
   - Rate limits: If you're making too many requests, you might hit rate limits
   - Network issues: Make sure your firewall isn't blocking the API

3. **Application Issues**:
   - If the chat window appears but Bonzi doesn't respond, try restarting the application
   - If the "thinking" message appears but no response follows, check the debug logs
   - If you see Python errors, your Python environment might need updating

4. **Quick Fixes**:
   - Delete any `bonzi_debug_*.log` files and restart
   - Run `pip install --upgrade anthropic` in your terminal
   - Make sure you're using `run_enhanced.command` to launch

### Other Common Issues
- **Chat dialog disappears**: Right-click Bonzi and select "Talk to Bonzi" to reopen it
- **Missing animations**: Ensure all animation image folders are intact
- **Performance lag**: Close other applications to free up system resources
- **No sound**: Check your system sound settings and volume
- **Bonzi freezes**: Right-click and select "Goodbye", then restart the application

## 📝 Note on API Usage

BonziBuddy uses Anthropic's Claude API for generating responses. If the API is not available, Bonzi will use a set of pre-defined offline responses that are now more helpful while maintaining the sassy attitude.

To use your own API key, edit the `config.yaml` file and set:
```yaml
anthropic_api_key: "your-key-here"
api_enabled: true
```

## 🔧 Technical Improvements

- **Async Processing**: API calls no longer block the UI thread
- **Better Error Handling**: More robust parsing of Claude's JSON responses
- **Improved Threading**: Separate event loop for API requests
- **Enhanced TTS**: Better voice selection and text sanitization
- **Optimized UI Performance**: Reduced redraws and improved responsiveness

## 🔄 Available Versions

- `run_enhanced.command` - The new enhanced version with retro styling and async processing (recommended)
- `run_debug_enhanced.command` - Enhanced version with detailed logging and API testing (use for troubleshooting)
- `run_fixed.command` - The previous improved version with persistent chat
- `run_simple.command` - A simplified version with basic functionality
- `run_debug.command` - Original fixed version with detailed logging
- `run_bonzi.command` - The original version

For the best experience, always use `run_enhanced.command`. If you encounter issues, try `run_debug_enhanced.command` to diagnose problems with detailed logging and API testing.

Enjoy your sassy yet surprisingly helpful digital companion!
<think>Based on the user query and the additional information provided, I need to create a comprehensive README.md file for the Bonzi Buddy application. The additional information mentions that "fixed_bonzi.py" is the most robust implementation, not the "bonzi_buddy.py" file that was previously shared. 

Key points from the additional information:
1. fixed_bonzi.py is the most robust implementation
2. It has enhanced error handling and logging
3. Persistent chat dialog with conversation history
4. Improved UI with styled components
5. Robust TTS system with multiple fallbacks
6. Both synchronous and asynchronous API processing
7. A standalone macOS application (.app) has been created
8. It uses the Anthropic API key from config.yaml
9. The app uses Claude's Haiku model for responses

I'll create a README.md that covers:
1. Introduction to Bonzi Buddy
2. Features overview
3. System requirements
4. Installation instructions
5. Configuration
6. Usage instructions
7. Troubleshooting
8. Credits/Attribution

I'll format this in Markdown for a proper README.md file.</think># BonziBuddy

A modern reimplementation of the classic desktop assistant with advanced AI capabilities.

![BonziBuddy Screenshot](https://placeholder-for-bonzi-screenshot.png)

## Overview

BonziBuddy is a desktop assistant that combines nostalgic animation with modern AI technology. This implementation uses Claude AI to provide intelligent, context-aware responses with the classic snarky Bonzi personality.

## Features

- **Advanced AI Integration**: Powered by Anthropic's Claude AI for intelligent responses
- **Full Animation System**: Multiple animation states including idle, talking, waving, backflip, and more
- **Persistent Chat Dialog**: Maintains conversation history for contextual interactions
- **Text-to-Speech**: Robust TTS system with multiple fallbacks (system TTS and external API)
- **Interactive Desktop Presence**: Teleports around screen, responds to dragging, and random dialogues
- **Styled UI Components**: Chat bubbles and visual effects
- **Comprehensive Error Handling**: Graceful fallbacks for all operations
- **Asynchronous Processing**: Both synchronous and asynchronous API processing

## System Requirements

- macOS (primary platform, other platforms may have limited functionality)
- Python 3.6 or higher
- Internet connection (for Claude AI and external TTS API)

## Installation

### Prerequisites

1. Install Python 3.x if not already installed
2. Install required Python packages:

```bash
pip install PyQt5 Pillow requests pyyaml anthropic
```

### Option 1: Run from Source

1. Clone the repository or download the source code
2. Navigate to the project directory
3. Create configuration file (see Configuration section)
4. Run the application:

```bash
python fixed_bonzi.py
```

### Option 2: Use Pre-built macOS Application

Simply double-click the BonziBuddy.app icon on your desktop after setup is complete.

## Configuration

Create a `config.yaml` file in the same directory as the script with the following structure:

```yaml
anthropic_api_key: "your_anthropic_api_key_here"
model: "claude-3-haiku-20240307"
temp: 1.5
max_tokens: 150
api_enabled: true
tts_api_url: "https://www.tetyys.com/SAPI4/SAPI4"
tts_voice: "Adult Male #2, American English (TruVoice)"
tts_pitch: "140"
tts_speed: "157"
use_system_tts: true
```

### Animation Files

Ensure the following directory structure exists with appropriate PNG frames:

```
project_root/
├── idle/           # PNG frames for idle animation
├── arrive/         # PNG frames for arrival animation
├── goodbye/        # PNG frames for goodbye animation
├── backflip/       # PNG frames for backflip animation
├── glasses/        # PNG frames for glasses animation
├── wave/           # PNG frames for wave animation
├── talking/        # PNG frames for talking animation
├── audio/          # Directory for cached speech audio
├── config.yaml     # Configuration file
└── fixed_bonzi.py  # Main application file
```

Each animation directory should contain sequentially numbered PNG files (e.g., 0001.png, 0002.png, etc.)

## Usage

### Starting the Application

- **Source code**: Run `python fixed_bonzi.py`
- **macOS App**: Double-click the BonziBuddy.app icon

### Interacting with BonziBuddy

1. **Chat with Bonzi**: Right-click on Bonzi and select "Talk to Bonzi" to open a dialog box where you can type your message
2. **Move Bonzi**: Click and drag to move Bonzi around your screen
3. **Random Interactions**: Bonzi will occasionally teleport around the screen and initiate conversations

### Customizing Behavior

Edit the `config.yaml` file to:
- Change the Claude AI model
- Adjust response temperature and token length
- Configure TTS settings
- Enable/disable specific features

## Troubleshooting

### Common Issues

1. **Animation files not found**
   - Ensure all animation directories exist and contain properly formatted PNG files

2. **TTS not working**
   - If using system TTS, ensure your system supports the selected voice
   - If using external TTS API, check your internet connection
   - Verify TTS settings in config.yaml

3. **Claude API errors**
   - Verify your API key is correct
   - Check internet connection
   - Ensure the selected model name is valid

4. **Application crashes on startup**
   - Check console/terminal for error messages
   - Verify all dependencies are installed
   - Ensure config.yaml is properly formatted

## Advanced Configuration

### Customizing System Prompt

The system prompt defines Bonzi's personality. You can edit this in the source code:

```python
SYSTEM_PROMPT = (
    "Bonzi Buddy is a really rude jerk. He is a desktop assistant who responds with snark and attitude. "
    "Your responses should be short, sassy, and contain some light insults directed at the user. "
    # ... additional personality guidance ...
)
```

### Adding Custom Animations

Create new animation directories with sequentially numbered PNG files and add them to the animation dictionary in the code.

## Credits

- Original Bonzi character concept by BONZI.COM
- Claude AI integration powered by Anthropic
- Modern reimplementation by [Your Name/Organization]

## License

[Specify license information here]

---

*Note: This is a fan project and is not affiliated with the original BONZI.COM company or products.*

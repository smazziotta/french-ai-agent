# French AI Agent - Ollama Local

A conversational AI agent that speaks French using local Ollama models, with voice input/output capabilities.

## Features

- 🇫🇷 **French conversation** - Responds naturally in French using local models
- 🎙️ **Voice input** - Speech-to-text with Whisper
- 🔊 **Voice output** - Text-to-speech with macOS
- 💾 **Memory** - Persistent conversation history
- 🏠 **Local AI** - Uses Ollama for private, offline inference
- 🌤️ **Weather tool** - Real-time weather lookup

## Quick Start

1. **Install Ollama:**
   ```bash
   # macOS
   brew install ollama
   # or download from https://ollama.ai
   ```

2. **Setup virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install ollama openai-whisper sounddevice numpy requests
   ```

3. **Start Ollama and pull model:**
   ```bash
   ollama serve
   ollama pull phi3
   ```

4. **Run the agent:**
   ```bash
   python mistral_french_agent.py
   ```

## Files

- **`mistral_french_agent.py`** - Main agent using local Ollama models
- **`Modelfile`** - Configuration for French Mistral model

## Configuration

### Model Selection
The agent uses `phi3` by default. You can modify the model in the code:
```python
MODEL_NAME = "phi3"  # or "mistral", "llama2", etc.
```

### Voice Setup
- **macOS**: Text-to-speech works out of the box
- **Microphone**: Grant microphone permissions in System Preferences

## Usage

1. Choose mode: `k` for keyboard, `v` for voice
2. Ask questions in French
3. Type `quit` to exit

## Example Conversations

```
👤 Vous: Quelle est la capitale de la France?
🤖: La capitale de la France est Paris.

👤 Vous: Bonjour, comment ça va?
🤖: Je vais bien, merci ! Et vous ?
```

## Development

The project uses:
- **Ollama** for local LLM inference
- **Whisper** for speech recognition
- **sounddevice** for audio capture
- **requests** for weather API calls

## Troubleshooting

- **Model not found**: Run `ollama pull phi3` first
- **Ollama not running**: Start with `ollama serve`
- **Voice not working**: Check microphone permissions in System Preferences
- **SSL errors**: Fixed automatically in the code
- **Weather not working**: Check internet connection
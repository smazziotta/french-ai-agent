# French AI Agent

A conversational AI agent that speaks French, with voice input/output capabilities and multiple backend options.

## Features

- 🇫🇷 **French conversation** - Responds naturally in French
- 🎙️ **Voice input** - Speech-to-text with Whisper
- 🔊 **Voice output** - Text-to-speech with macOS
- 💾 **Memory** - Persistent conversation history
- 🤖 **Multiple backends** - Ollama local models or OpenAI API

## Quick Start

1. **Setup virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install ollama openai-whisper sounddevice numpy requests
   ```

2. **Run the simple agent (recommended):**
   ```bash
   python simple_french_agent.py
   ```

3. **Or run the Ollama-based agent:**
   ```bash
   # First ensure Ollama is running with a model
   ollama serve
   ollama pull phi3
   
   python mistral_french_agent.py
   ```

## Files

- **`simple_french_agent.py`** - Standalone agent with built-in responses and optional OpenAI
- **`mistral_french_agent.py`** - Ollama-based agent with local LLM models
- **`Modelfile`** - Configuration for French Mistral model

## Configuration

### OpenAI Integration (Optional)
For better responses in the simple agent:
```bash
export OPENAI_API_KEY="your-api-key-here"
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
- **Whisper** for speech recognition
- **Ollama** for local LLM inference
- **OpenAI API** as fallback/alternative
- **sounddevice** for audio capture

## Troubleshooting

- **Ollama issues**: Use `simple_french_agent.py` instead
- **Voice not working**: Check microphone permissions
- **SSL errors**: Fixed automatically in the code
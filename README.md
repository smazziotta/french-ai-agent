# French AI Agent

A conversational AI agent that speaks French, powered by hosted Mistral AI with voice input/output capabilities.

## Features

- 🇫🇷 **French conversation** - Responds naturally in French using Mistral AI
- 🎙️ **Voice input** - Speech-to-text with Whisper
- 🔊 **Voice output** - Text-to-speech with macOS
- 💾 **Memory** - Persistent conversation history
- 🚀 **Hosted LLM** - Uses Mistral AI API (with OpenAI fallback)
- 📱 **No local setup** - No need for local model downloads

## Quick Start

1. **Setup virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install openai-whisper sounddevice numpy requests openai
   ```

2. **Get a Mistral API key:**
   - Visit [console.mistral.ai](https://console.mistral.ai)
   - Create an account and get your API key
   - Or use OpenAI API as alternative

3. **Configure API key:**
   ```bash
   export MISTRAL_API_KEY="your-mistral-api-key-here"
   # OR for OpenAI
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

4. **Run the agent:**
   ```bash
   python simple_french_agent.py
   ```

## Files

- **`simple_french_agent.py`** - Main agent using Mistral AI API with OpenAI fallback
- **`mistral_french_agent.py`** - Legacy Ollama-based agent (deprecated)
- **`Modelfile`** - Configuration for local Mistral model (deprecated)

## Configuration

### Mistral AI API (Recommended)
Best performance and French language support:
```bash
export MISTRAL_API_KEY="your-mistral-api-key-here"
```

### OpenAI API (Alternative)
Fallback option if Mistral is not available:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
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
- **Mistral AI API** for French language model inference
- **Whisper** for speech recognition
- **OpenAI API** as fallback alternative
- **sounddevice** for audio capture
- **requests** for HTTP API calls

## API Information

### Mistral AI Models
- **mistral-small-latest**: Balanced performance and cost
- **mistral-medium-latest**: Higher quality responses
- **mistral-large-latest**: Best quality, higher cost

### Pricing (Mistral AI)
- Very competitive pricing compared to alternatives
- Pay-per-token usage model
- Free tier available for testing

## Troubleshooting

- **API key issues**: Ensure your Mistral or OpenAI API key is correctly set
- **Voice not working**: Check microphone permissions in System Preferences
- **Network errors**: Check internet connection and API status
- **SSL errors**: Fixed automatically in the code
#!/usr/bin/env python3
"""
mistral_french_agent.py
A local French AI agent using ollama (Mistral 7B), whisper for speech-to-text,
and macOS `say` for text-to-speech. Saves simple chat memory to disk.

Run:
    source venv/bin/activate
    python mistral_french_agent.py
"""

import json
import os
import time
import requests
import ssl
import urllib.request
from pathlib import Path

# Ollama chat client
# The ollama Python package should expose a chat helper (install via pip install ollama).
# The usage below follows the simple pattern: chat(model=..., messages=...)
from ollama import chat

# Optional speech libs (Whisper)
try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception:
    WHISPER_AVAILABLE = False

# Optional audio capture
try:
    import sounddevice as sd
    import numpy as np
    SD_AVAILABLE = True
except Exception:
    SD_AVAILABLE = False

MEMORY_FILE = Path.home() / ".mistral_french_agent_memory.json"
MODEL_NAME = "phi3"  # using smaller, more stable model
FALLBACK_MODEL = "phi3"  # fallback to same model if issues

# Load/save memory
def load_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text())
        except Exception:
            return []
    return []

def save_memory(mem):
    MEMORY_FILE.write_text(json.dumps(mem, ensure_ascii=False, indent=2))

# Tiny tool: weather lookup via wttr.in (human-friendly)
def tool_weather(city: str) -> str:
    try:
        r = requests.get(f"https://wttr.in/{city}?format=3", timeout=6)
        if r.status_code == 200:
            return r.text.strip()
        return "Impossible de récupérer la météo pour l'instant."
    except Exception as e:
        return f"Erreur météo: {e}"

# Decide if the prompt asks for a tool (very simple heuristic)
def check_for_tools(prompt: str):
    text = prompt.lower()
    if "météo" in text or "météor" in text:
        # naive city extraction: last word
        tokens = prompt.split()
        if tokens:
            return ("weather", tokens[-1])
        return ("weather", "Paris")
    return (None, None)

# Ask the model (with simple memory as messages list)
def ask_model(history):
    """
    history: list of messages, each {'role': 'user'|'assistant'|'system', 'content': str}
    Uses ollama.chat to send messages and returns assistant content.
    """
    # Try the custom French model first, then fallback to base model
    for model_to_try in [MODEL_NAME, FALLBACK_MODEL]:
        try:
            print(f"🔄 Essai avec le modèle: {model_to_try}")
            resp = chat(model=model_to_try, messages=history)
            assistant_text = resp.get("message", {}).get("content", "")
            if assistant_text:
                return assistant_text
        except Exception as e:
            print(f"❌ Erreur avec {model_to_try}: {e}")
            continue
    
    # If all models fail, return a French error message
    return "Je suis désolé, je ne peux pas accéder aux modèles locaux pour le moment. Veuillez vérifier que Ollama fonctionne correctement."

# Global variable to cache the whisper model
_whisper_model = None

def load_whisper_model():
    """Load whisper model with SSL fix"""
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    
    # Fix SSL certificate verification issue
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Install the SSL context globally
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context))
    urllib.request.install_opener(opener)
    
    try:
        _whisper_model = whisper.load_model("base")
        return _whisper_model
    except Exception as e:
        print(f"Erreur lors du chargement du modèle Whisper: {e}")
        return None

# Whisper recording + transcription (very simple)
def record_and_transcribe(duration=5, sr=16000):
    if not WHISPER_AVAILABLE or not SD_AVAILABLE:
        print("Whisper or sounddevice not available. Install `openai-whisper` and `sounddevice` or use keyboard input.")
        return None

    model = load_whisper_model()
    if model is None:
        print("Impossible de charger le modèle Whisper. Utilisez le clavier.")
        return None

    print(f"🎙️ Enregistrement {duration}s — parlez maintenant...")
    audio = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype=np.float32)
    sd.wait()
    audio = np.squeeze(audio)
    
    # Debug: check audio levels
    audio_max = np.max(np.abs(audio))
    print(f"🔊 Niveau audio max: {audio_max:.4f}")
    
    if audio_max < 0.001:
        print("⚠️ Aucun son détecté. Vérifiez votre microphone ou les permissions.")
        return None
    
    result = model.transcribe(audio, language='fr', task='transcribe')  # force French
    text = result.get("text", "").strip()
    print("✅ Transcription:", text if text else "(silence détecté)")
    return text if text else None

# macOS TTS
def speak(text: str):
    # Use 'say' with a French voice if available
    try:
        # 'Thomas' is a commonly available French voice on macOS. If unavailable, the system picks a voice.
        os.system(f'say -v Thomas "{text}"')
    except Exception:
        # fallback: no TTS
        pass

def interactive_loop():
    memory = load_memory()
    # Ensure system message entry at memory[0]
    system_msg = {
        "role": "system", 
        "content": "Tu es un agent IA français utile et poli. Tu réponds toujours en français sauf si on te demande explicitement d'utiliser une autre langue. Réponds de manière concise et naturelle."
    }
    # If the memory file exists and already has a system message, leave it; else prepend
    if not memory or memory[0].get("role") != "system":
        memory.insert(0, system_msg)

    print("Agent Mistral 7B (local). Tapez 'voice' pour entrer en mode voix, 'quit' pour sortir.")
    while True:
        mode = input("\nMode [keyboard/voice] (k/v) ? ").strip().lower()
        if mode in ("q", "quit", "exit"):
            break

        if mode in ("v", "voice"):
            if not WHISPER_AVAILABLE or not SD_AVAILABLE:
                print("La capture audio ou Whisper n'est pas disponible. Tapez au clavier à la place.")
                continue
            user_text = record_and_transcribe(duration=5)  # 5s default
            if not user_text:
                continue
            print("👤 Vous:", user_text)
        else:
            user_text = input("👤 Vous: ").strip()
            if user_text.lower() in ("quit", "exit", "q"):
                break

        # tool detection
        tool_name, tool_arg = check_for_tools(user_text)
        if tool_name == "weather":
            tool_out = tool_weather(tool_arg)
            assistant_reply = f"Voici la météo pour {tool_arg}: {tool_out}"
            # append to memory
            memory.append({"role": "user", "content": user_text})
            memory.append({"role": "assistant", "content": assistant_reply})
            save_memory(memory)
            print("🤖 (outil):", assistant_reply)
            speak(assistant_reply)
            continue

        # otherwise, append user message and call model
        memory.append({"role": "user", "content": user_text})
        # Send full history (or a truncated version to fit local/context window)
        # For safety, keep only last N messages to avoid overflow
        MAX_HISTORY = 30
        to_send = memory[-MAX_HISTORY:]
        assistant_text = ask_model(to_send)
        if not assistant_text:
            assistant_text = "Je suis désolé, je n'ai pas de réponse pour le moment."

        memory.append({"role": "assistant", "content": assistant_text})
        save_memory(memory)

        print("🤖:", assistant_text)
        speak(assistant_text)
        time.sleep(0.2)

if __name__ == "__main__":
    try:
        interactive_loop()
    except KeyboardInterrupt:
        print("\nFin du programme. Mémoire sauvegardée.")

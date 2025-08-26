#!/usr/bin/env python3
"""
simple_french_agent.py
A French conversation agent powered by Mistral AI API.
Provides natural French conversation with voice input/output capabilities.

Run:
    export MISTRAL_API_KEY="your-api-key"
    source venv/bin/activate
    python simple_french_agent.py
"""

import json
import os
import time
from pathlib import Path

# Optional speech libs (Whisper)
try:
    import whisper
    import ssl
    import urllib.request
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

# HTTP requests for Mistral API
try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False

MEMORY_FILE = Path.home() / ".mistral_french_agent_memory.json"

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

# Simple French responses for common questions
FRENCH_RESPONSES = {
    "bonjour": "Bonjour ! Comment allez-vous ?",
    "hello": "Bonjour ! Je préfère parler en français.",
    "comment": "Je vais bien, merci ! Et vous ?",
    "capitale": "La capitale de la France est Paris.",
    "paris": "Paris est une belle ville, la capitale de la France.",
    "france": "La France est un pays magnifique en Europe.",
    "météo": "Je ne peux pas vérifier la météo actuellement, mais j'espère qu'il fait beau !",
    "merci": "De rien ! C'est un plaisir de vous aider.",
    "au revoir": "Au revoir ! À bientôt !",
    "aide": "Je suis ici pour vous aider ! Posez-moi vos questions en français.",
    "qui": "Je suis un assistant IA qui parle français. Comment puis-je vous aider ?",
    "quoi": "Pouvez-vous reformuler votre question ? Je ferai de mon mieux pour répondre.",
    "pourquoi": "C'est une bonne question ! Pouvez-vous être plus précis ?",
    "où": "Je ne connais pas les lieux spécifiques, mais je peux discuter en français !",
    "quand": "Je n'ai pas accès à l'heure actuelle, mais nous pouvons continuer à discuter.",
}

def get_simple_response(text: str) -> str:
    """Get a simple French response based on keywords"""
    text_lower = text.lower()
    
    # Check for keywords and return appropriate responses
    for keyword, response in FRENCH_RESPONSES.items():
        if keyword in text_lower:
            return response
    
    # Default responses based on question words
    if any(word in text_lower for word in ["comment", "ça va", "allez"]):
        return "Je vais bien, merci ! C'est gentil de demander. Et vous ?"
    
    if any(word in text_lower for word in ["quelle", "quel", "qu'est"]):
        return "C'est une bonne question ! Je ferai de mon mieux pour répondre, mais mes connaissances sont limitées."
    
    if "?" in text:
        return "Hmm, c'est une question intéressante ! Malheureusement, je n'ai pas accès à des modèles avancés actuellement."
    
    return "C'est intéressant ! Pouvez-vous me dire plus ? J'aime discuter en français."

def ask_mistral(history):
    """Use Mistral AI API for French conversation"""
    if not REQUESTS_AVAILABLE:
        print("⚠️ Module requests non disponible")
        return None
        
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("⚠️ MISTRAL_API_KEY non configurée")
        return None
    
    try:
        # Add French system prompt
        messages = [
            {
                "role": "system", 
                "content": "Tu es un assistant IA français expert. Réponds toujours en français de manière naturelle, amicale et informative. Sois concis mais complet dans tes réponses."
            }
        ] + history[-10:]
        
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-small-latest",
                "messages": messages,
                "max_tokens": 200,
                "temperature": 0.7
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            print("⚠️ Clé API Mistral invalide")
            return None
        else:
            print(f"⚠️ Erreur API Mistral: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erreur réseau Mistral: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Erreur Mistral: {e}")
        return None

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

# Whisper recording + transcription
def record_and_transcribe(duration=5, sr=16000):
    if not WHISPER_AVAILABLE or not SD_AVAILABLE:
        print("Whisper ou sounddevice non disponible. Utilisez le clavier.")
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
    
    result = model.transcribe(audio, language='fr', task='transcribe')
    text = result.get("text", "").strip()
    print("✅ Transcription:", text if text else "(silence détecté)")
    return text if text else None

# macOS TTS
def speak(text: str):
    try:
        os.system(f'say -v Thomas "{text}"')
    except Exception:
        pass

def interactive_loop():
    memory = load_memory()
    
    print("🇫🇷 Agent Français avec Mistral AI - Tapez 'voice' pour la voix, 'quit' pour sortir")
    
    # Check API key configuration
    mistral_key = os.getenv('MISTRAL_API_KEY')
    if mistral_key:
        print("✅ Mistral AI configuré et prêt")
    else:
        print("⚠️ MISTRAL_API_KEY non configurée - utilisation des réponses simples uniquement")
        print("💡 Configurez votre clé: export MISTRAL_API_KEY='votre-clé-ici'")
    
    while True:
        mode = input("\nMode [keyboard/voice] (k/v) ? ").strip().lower()
        if mode in ("q", "quit", "exit"):
            break

        if mode in ("v", "voice"):
            if not WHISPER_AVAILABLE or not SD_AVAILABLE:
                print("La capture audio n'est pas disponible. Utilisez le clavier.")
                continue
            user_text = record_and_transcribe(duration=5)
            if not user_text:
                continue
            print("👤 Vous:", user_text)
        else:
            user_text = input("👤 Vous: ").strip()
            if user_text.lower() in ("quit", "exit", "q"):
                break

        # Use Mistral AI, fall back to simple responses if unavailable
        response = ask_mistral(memory + [{"role": "user", "content": user_text}])
        
        if not response:
            response = get_simple_response(user_text)
        
        # Save to memory
        memory.append({"role": "user", "content": user_text})
        memory.append({"role": "assistant", "content": response})
        
        # Keep only last 20 messages
        if len(memory) > 20:
            memory = memory[-20:]
        
        save_memory(memory)
        
        print("🤖:", response)
        speak(response)
        time.sleep(0.2)

if __name__ == "__main__":
    try:
        interactive_loop()
    except KeyboardInterrupt:
        print("\nAu revoir ! Mémoire sauvegardée.")
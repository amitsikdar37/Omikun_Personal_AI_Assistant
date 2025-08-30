import sounddevice as sd
import keyboard
import numpy as np
import time
import os

from src.audio.stt import STT
from src.audio.tts import TTS
from src.agent.memory import Memory
from src.llm.ollama_client import OllamaClient
from src.tools.whatsapp_web import WhatsAppWeb

def build_system(memory_summary):
    base = "You are Omikun, a concise and friendly AI assistant. If Memory includes the user's name, address them naturally by name."
    if memory_summary:
        return f"{base}\nMemory: {memory_summary}"
    return base

class JarvisAssistant:
    def __init__(self):
        print("Initializing Omikun...")
        
        # Initialize components
        self.stt = STT()
        self.tts = TTS()
        self.memory = Memory(path="memory.json", max_history=6)
        self.llama = OllamaClient("llama3.1:8b")  # /api/chat client
        self.whatsapp = None
        
        # Audio settings
        self.sample_rate = 16000
        self.is_recording = False
        self.audio_data = []
        
        print("Omikun is ready! Press and hold SPACE to talk.")
    
    def record_audio(self):
        """Record audio while space is pressed"""
        def audio_callback(indata, frames, time, status):
            if self.is_recording:
                self.audio_data.extend(indata[:, 0])  # Mono audio
        
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=self.sample_rate):
            while True:
                if keyboard.is_pressed('space') and not self.is_recording:
                    print("🎤 Recording... (release SPACE to stop)")
                    self.is_recording = True
                    self.audio_data = []
                
                elif not keyboard.is_pressed('space') and self.is_recording:
                    print("🎤 Recording stopped")
                    self.is_recording = False
                    
                    if len(self.audio_data) > 0:
                        self.process_audio()
                
                elif keyboard.is_pressed('q'):
                    print("Goodbye!")
                    break
                
                time.sleep(0.1)
    
    def process_audio(self):
        try:
            audio_np = np.array(self.audio_data, dtype=np.float32)
            print("🧠 Transcribing...")
            text = self.stt.transcribe(audio_np, self.sample_rate)

            if not text or not text.strip():
                self.tts.speak("I didn't hear anything.")
                return

            print(f"You said: {text}")

            # Learn facts (e.g., name) if present
            self.memory.extract_and_store(text)

            # Build per-turn system prompt using memory
            system_str = build_system(self.memory.get_profile_summary())

            # Get model reply with system + rolling messages (handled inside OllamaClient)
            reply = self.llama.chat(text, system_prompt=system_str)

            # Update short history
            self.memory.add_history("user", text)
            self.memory.add_history("assistant", reply)

            # Speak reply
            self.tts.speak(reply)

        except Exception as e:
            print(f"Error processing audio: {e}")
            self.tts.speak("Sorry, I had trouble processing that.")

    
    def handle_chat(self, text):
        """Handle regular chat"""
        print("🤖 Thinking...")
        response = self.llama.chat(text)
        print(f"Jarvis: {response}")
        self.tts.speak(response)
    
    def handle_whatsapp_command(self, text):
        """Handle WhatsApp commands"""
        # Simple parsing (you can make this smarter)
        if "message" in text.lower():
            self.tts.speak("WhatsApp messaging is not set up yet. Working on regular chat for now.")
            # For now, just do regular chat
            self.handle_chat(text)
        else:
            self.handle_chat(text)
    
    def setup_whatsapp(self):
        """Set up WhatsApp Web (call this manually first time)"""
        self.whatsapp = WhatsAppWeb()
        if self.whatsapp.login():
            print("WhatsApp is ready!")
        else:
            print("WhatsApp setup failed")
    
    def run(self):
        """Start the assistant"""
        try:
            self.record_audio()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            if self.whatsapp:
                self.whatsapp.close()
    
   
if __name__ == "__main__":
    jarvis = JarvisAssistant()
    jarvis.run()

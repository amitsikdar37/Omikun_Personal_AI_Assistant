import sounddevice as sd
import keyboard
import numpy as np
import time
import os
import re

from src.audio.stt import STT
from src.audio.tts import TTS
from src.agent.memory import Memory
from src.llm.ollama_client import OllamaClient
from src.tools.whatsapp_web import WhatsAppWeb
from threading import Thread, Event

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
        self.whatsapp = WhatsAppWeb()
        self.auto_replying = False
        self.stop_event = Event()
        
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

            if text.lower().startswith("reply to"):
                try:
                    rest = text[len("reply to"):].strip()
                    split_found = False
                    for delim in [",", ":", "-", " dash ", " comma ", " colon ", " hyphen ", " full stop "]:
                        if delim in rest:
                            parts = [p.strip() for p in rest.split(delim, 1)]
                            contact, reply = parts[0], parts[1]
                            split_found = True
                            break
                    if not split_found:
                        # Fallback: try to match the LONGEST prefix from available WhatsApp contacts
                        candidate = rest.strip()
                        # Optionally, get available_contacts dynamically from WhatsApp by inspecting span[@title], as above
                        # For now, just use first word as contact, rest as message
                        tokens = rest.split(maxsplit=1)
                        if len(tokens) == 1:
                            raise ValueError("No message found!")
                        contact, reply = tokens[0], tokens[1]
                    print(f"Contact: '{contact}', Msg: '{reply}'")
                    self.whatsapp.send_message_to_contact(contact, reply)
                    self.tts.speak(f"Sent your reply to {contact}.")
                except Exception as e:
                    print(e)
                    self.tts.speak("Sorry, I couldn't send the message. Please use 'Reply to <contact> <message>'.")
                return    # Don't continue for chat
            
            if "start auto reply" in text.lower():
                self.start_auto_reply()
                return
            elif "stop auto reply" in text.lower():
                self.stop_auto_reply()
                return


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

    def start_auto_reply(self):
        if not self.auto_replying:
            self.auto_replying = True
            self.stop_event.clear()
            Thread(target=self.whatsapp.auto_reply_loop,
                args=(self.create_ai_callback(), self.stop_event.is_set),
                daemon=True).start()
            self.tts.speak("Auto-reply mode started.")

    def stop_auto_reply(self):
        if self.auto_replying:
            self.auto_replying = False
            self.stop_event.set()
            self.tts.speak("Auto-reply mode stopped.")

    def create_ai_callback(self):
        # Provide sender and message text to your LLM
        def callback(sender, msg):
            prompt = (
                f"Sender: {sender}\n"
                f"Message: {msg}\n"
                "Reply in a friendly, WhatsApp-style chat, keeping it short and human:"
            )
            return self.llama.chat(prompt)
        return callback

    
   
if __name__ == "__main__":
    jarvis = JarvisAssistant()
    jarvis.run()

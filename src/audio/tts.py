import pyttsx3

class TTS:
    def __init__(self):
        # Don't initialize engine here - do it per call
        print("TTS initialized")
    
    def speak(self, text):
        """Convert text to speech"""
        try:
            print(f"Speaking: {text}")
            
            # Initialize engine fresh each time
            engine = pyttsx3.init()
            
            # Set voice properties
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            
            engine.setProperty('rate', 180)
            engine.setProperty('volume', 0.8)
            
            # Speak and clean up
            engine.say(text)
            engine.runAndWait()
            
            # Clean up engine
            del engine
            
        except Exception as e:
            print(f"TTS Error: {e}")

#!/usr/bin/env python3
"""Test text-to-speech functionality"""

def test_tts():
    try:
        from src.audio.tts import TTS
        print("Testing TTS...")
        
        tts = TTS()
        tts.speak("Hello! This is a test of the text to speech system.")
        print("✅ TTS test completed!")
        return True
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

if __name__ == "__main__":
    test_tts()

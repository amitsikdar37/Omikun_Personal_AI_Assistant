#!/usr/bin/env python3
"""Test speech-to-text functionality"""

import sounddevice as sd
import numpy as np

def test_stt():
    try:
        from src.audio.stt import STT
        print("Testing STT...")
        
        stt = STT()
        
        # Record 3 seconds of audio
        print("Say something for 3 seconds...")
        duration = 3  # seconds
        sample_rate = 16000
        
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()  # Wait until recording is finished
        
        # Convert to the right format
        audio_data = audio.flatten()
        
        # Transcribe
        text = stt.transcribe(audio_data, sample_rate)
        print(f"You said: '{text}'")
        
        if text:
            print("✅ STT test completed!")
            return True
        else:
            print("❌ STT returned empty text")
            return False
            
    except Exception as e:
        print(f"❌ STT test failed: {e}")
        return False

if __name__ == "__main__":
    test_stt()

#!/usr/bin/env python3
"""Test if all components can be imported"""

def test_imports():
    try:
        from src.audio.stt import STT
        from src.audio.tts import TTS
        from src.llm.llama_client import LlamaClient
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    test_imports()

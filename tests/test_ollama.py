#!/usr/bin/env python3
"""Test Ollama functionality"""

def test_ollama():
    try:
        from src.llm.ollama_client import OllamaClient
        print("Testing Ollama model...")
        
        # Check if Ollama is running
        import requests
        try:
            response = requests.get("http://localhost:11434", timeout=5)
            print("✅ Ollama server is running")
        except:
            print("❌ Ollama server not running! Start it with: ollama serve")
            return False
        
        # Test the client
        ollama = OllamaClient("llama3.1:8b")
        response = ollama.chat("Say hello in a friendly way")
        
        print(f"Ollama says: {response}")
        
        if response and "trouble processing" not in response:
            print("✅ Ollama test completed!")
            return True
        else:
            print("❌ Ollama returned error response")
            return False
            
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False

if __name__ == "__main__":
    test_ollama()

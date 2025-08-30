import requests

class OllamaClient:
    def __init__(self, model_name="llama3.1:8b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        # rolling message history (short)
        self.messages = []
        print(f"✅ Ollama client initialized with model: {model_name}")

    def reset(self):
        self.messages = []

    def chat(self, user_message, system_prompt=None):
        # Append user message to rolling history
        self.messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model_name,
            "messages": self.messages,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt  # overrides default system template if provided

        url = f"{self.base_url}/api/chat"
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()

        # Ollama chat returns a single assistant message in 'message'
        assistant_text = data.get("message", {}).get("content", "").strip()

        # Append assistant reply to history so context continues
        if assistant_text:
            self.messages.append({"role": "assistant", "content": assistant_text})

        return assistant_text or "Sorry, I had trouble processing that."

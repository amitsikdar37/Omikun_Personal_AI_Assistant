# src/agent/memory.py
import json, os, re

class Memory:
    def __init__(self, path="memory.json", max_history=6):
        self.path = path
        self.max_history = max_history
        self.state = {"profile": {}, "history": []}
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
            except Exception:
                pass

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def add_history(self, role, text):
        self.state["history"].append({"role": role, "text": text})
        if len(self.state["history"]) > self.max_history:
            self.state["history"] = self.state["history"][-self.max_history:]
        self.save()

    def get_profile_summary(self):
        prof = self.state.get("profile", {})
        parts = []
        if "name" in prof:
            parts.append(f'UserName: {prof["name"]}')
        return "; ".join(parts)

    def extract_and_store(self, user_text):
        m = re.search(r"\bmy name is ([A-Za-z][A-Za-z .'-]{1,40})", user_text, re.IGNORECASE)
        if not m:
            m = re.search(r"\bi am ([A-Za-z][A-Za-z .'-]{1,40})", user_text, re.IGNORECASE)
        if m:
            name = m.group(1).strip(" .'-")
            self.state.setdefault("profile", {})["name"] = name
            self.save()
            return {"name": name}
        return {}

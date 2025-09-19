from typing import List, Dict

class SessionMemory:
    """Simple in-memory session storage for a single CLI session."""
    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add_user(self, text: str):
        self.messages.append({"role": "user", "text": text})

    def add_assistant(self, text: str):
        self.messages.append({"role": "assistant", "text": text})

    def get_messages(self):
        return self.messages

    def clear(self):
        self.messages = []

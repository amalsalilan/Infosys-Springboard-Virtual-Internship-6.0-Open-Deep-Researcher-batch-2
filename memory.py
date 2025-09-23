# memory_store.py

from typing import List
from langchain_core.messages import BaseMessage

class ConversationHistory:
    """
    Manages the session's chat history in a simple list.
    This object stores the sequence of messages to provide conversational context.
    """
    def __init__(self):
        self._messages: List[BaseMessage] = []

    def log_message(self, message: BaseMessage):
        """Adds a new message to the end of the conversation log."""
        self._messages.append(message)

    def get_history(self) -> List[BaseMessage]:
        """Retrieves the entire list of messages exchanged so far."""
        return self._messages

    def reset(self):
        """Clears all messages from the history for a new session."""
        self._messages = []
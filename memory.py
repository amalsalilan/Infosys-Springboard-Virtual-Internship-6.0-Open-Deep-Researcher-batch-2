from typing import TypedDict, List
from langchain_core.messages import HumanMessage, AIMessage

class ChatState(TypedDict):
    messages: List
    clarification_needed: bool
    next_step: str
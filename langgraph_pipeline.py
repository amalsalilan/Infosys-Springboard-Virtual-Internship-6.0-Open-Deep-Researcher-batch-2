from typing import TypedDict
from langgraph.graph import StateGraph, END
from clarifier import Clarifier
from memory import SessionMemory

class ChatState(TypedDict):
    messages: list
    last_user: str

def build_graph(openai_api_key: str):
    clarifier = Clarifier(openai_api_key=openai_api_key)
    memory = SessionMemory()

    graph = StateGraph()

    def clarity_node(state: ChatState):
        user_text = state.get("last_user", "")
        ctx_text = "\n".join([f"{m['role']}: {m['text']}" for m in state.get("messages", [])])
        result = clarifier.need_clarification(user_text, context=ctx_text)
        state["clarify_needed"] = result["need"]
        state["clarify_question"] = result["question"]
        return state

    def ask_clarify_node(state: ChatState):
        return state

    def assistant_node(state: ChatState):
        last_user = state.get("last_user", "")
        context = "\n".join([f"{m['role']}: {m['text']}" for m in state.get("messages", [])])
        reply = f"I understand: '{last_user}'. (Context length: {len(context)} chars)"
        state.setdefault("messages", []).append({"role": "assistant", "text": reply})
        state["assistant_reply"] = reply
        return state

    graph.add_node(clarity_node, name="clarity")
    graph.add_node(ask_clarify_node, name="ask_clarify")
    graph.add_node(assistant_node, name="assistant")

    graph.set_entry_point("clarity")

    graph.add_edge("clarity", "ask_clarify", condition=lambda s: s.get("clarify_needed", False))
    graph.add_edge("clarity", "assistant", condition=lambda s: not s.get("clarify_needed", False))
    graph.add_edge("ask_clarify", END)
    graph.add_edge("assistant", END)

    return graph, memory

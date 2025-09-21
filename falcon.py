# ==========================
# Imports
# ==========================
import os
from dotenv import load_dotenv
from typing import TypedDict, List
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langchain_huggingface import HuggingFaceEndpoint
from langchain.tools import tool
import wikipedia
from datetime import datetime
import re

# ==========================
# Load API Key
# ==========================
load_dotenv()
HF_API_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not HF_API_KEY:
    raise ValueError("⚠️ Please set HUGGINGFACEHUB_API_TOKEN in your .env file")

# ==========================
# Initialize LLM
# ==========================
llm = HuggingFaceEndpoint(
    repo_id="tiiuae/falcon-7b-instruct",
    huggingfacehub_api_token=HF_API_KEY,
    task="conversational",
    max_new_tokens=512,
    temperature=0.7
)

# ==========================
# Define Agent State
# ==========================
class AgentState(TypedDict):
    input: str
    chat_history: List[HumanMessage]

# ==========================
# Tools
# ==========================
@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression and return the result."""
    try:
        return str(eval(expression))
    except:
        return "Cannot calculate that."

@tool
def wiki_search(query: str) -> str:
    """Search Wikipedia and return a short summary (2 sentences)."""
    try:
        return wikipedia.summary(query, sentences=2)
    except:
        return "No results found on Wikipedia."

@tool
def get_datetime(_: str = "") -> str:
    """Return the current date and time in YYYY-MM-DD HH:MM:SS format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================
# Clarifier Node
# ==========================
def clarifier_node(state: AgentState):
    """Ask for clarification if input is empty."""
    if not state["input"].strip():
        reply = "Can you please clarify your question?"
        state.setdefault("chat_history", []).append(AIMessage(content=reply))
    return state

# ==========================
# Responder Node (Smart Auto-Tool)
# ==========================
def responder_node(state: AgentState):
    user_input = state["input"].strip()
    messages = state.get("chat_history", [])

    # ---- Calculator Detection ----
    if re.match(r"^[0-9\s\+\-\*\/\(\)\.]+$", user_input):
        reply = f"Calculator result: {calculator.invoke(user_input)}"

    # ---- Date & Time Detection ----
    elif any(keyword in user_input.lower() for keyword in ["time", "date", "day", "current time"]):
        reply = f"Current date & time: {get_datetime.invoke('')}"

    # ---- Smart Wikipedia Detection ----
    elif any(keyword in user_input.lower() for keyword in ["who", "what", "when", "where", "define", "meaning of"]):
        wiki_result = wiki_search.invoke(user_input)
        if wiki_result != "No results found on Wikipedia.":
            reply = f"Wikipedia: {wiki_result}"
        else:
            # Fallback to LLM if Wikipedia fails
            llm_response = llm.invoke(messages + [HumanMessage(content=user_input)])
            reply = llm_response.content

    # ---- Default LLM ----
    else:
        llm_response = llm.invoke(messages + [HumanMessage(content=user_input)])
        reply = llm_response.content

    # Save assistant response
    messages.append(AIMessage(content=reply))
    state["chat_history"] = messages
    return state

# ==========================
# Build LangGraph Workflow
# ==========================
workflow = StateGraph(AgentState)
workflow.add_node("clarifier", clarifier_node)
workflow.add_node("responder", responder_node)
workflow.set_entry_point("clarifier")
workflow.add_edge("clarifier", "responder")
workflow.add_edge("responder", END)
app = workflow.compile()

# ==========================
# Chat Function
# ==========================
chat_history: List[HumanMessage] = []

def chat_with_agent(user_input: str):
    global chat_history
    state = {"input": user_input, "chat_history": chat_history}
    result = app.invoke(state)
    last_msg = result["chat_history"][-1]
    print("AI:", last_msg.content)
    chat_history = result["chat_history"]

# ==========================
# Run Chatbot
# ==========================
if __name__ == "__main__":
    print("Smart Falcon-7B-Instruct Chatbot is ready! Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        chat_with_agent(user_input)


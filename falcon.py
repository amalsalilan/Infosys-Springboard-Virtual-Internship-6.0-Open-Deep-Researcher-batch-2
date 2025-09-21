import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
import wikipedia

# =========================
# Load environment variables
# =========================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ Please set your OPENAI_API_KEY in the environment or .env file")

# =========================
# Initialize OpenAI LLM
# =========================
llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)

# =========================
# Initial chatbot state
# =========================
def get_initial_state():
    return {"messages": []}

# =========================
# Wikipedia search tool
# =========================
def wiki_search(query: str) -> str:
    try:
        return wikipedia.summary(query, sentences=2)
    except Exception:
        return "No relevant information found on Wikipedia."

# =========================
# Chatbot logic
# =========================
def chatbot_node(state):
    user_input = state["input"].strip()
    messages = state["messages"]

    # Add user message to conversation history
    messages.append(HumanMessage(content=user_input))

    # Get AI response
    response = llm(messages)
    response_text = response.content

    # If AI response is vague or not factual, try Wikipedia
    # (Simple heuristic: check for phrases like "I’m not sure", "I don't know")
    if any(phrase in response_text.lower() for phrase in ["i'm not sure", "i do not know", "i don't know", "cannot find"]):
        wiki_result = wiki_search(user_input)
        response_text += f"\n\nWikipedia info: {wiki_result}"

    # Save AI response to conversation history
    messages.append(AIMessage(content=response_text))
    return {"messages": messages, "output": response_text}

# =========================
# Build LangGraph workflow
# =========================
graph = StateGraph(dict)
graph.add_node("chatbot", chatbot_node)
graph.set_entry_point("chatbot")
graph.add_edge("chatbot", END)
app = graph.compile()

# =========================
# Chat loop
# =========================
print("Smart Q&A Chatbot with Wikipedia is ready! (type 'exit' to quit)\n")
state = get_initial_state()

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["exit", "quit"]:
        print("Chatbot: Goodbye! 👋")
        break

    state["input"] = user_input
    response = app.invoke(state)
    print("Chatbot:", response["output"])



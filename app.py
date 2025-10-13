<<<<<<< HEAD
# 🔥 COMPLETE LANGGRAPH CHATBOT - GOOGLE COLAB VERSION
# Just run this entire cell and start chatting!

# Install required packages
!pip install -q langgraph langchain-openai python-dotenv

import os
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

print("🤖 LangGraph Chatbot with Clarification System")
print("==============================================")

# Setup - use Gemini since OpenAI requires paid API
import google.generativeai as genai
genai.configure(api_key=".......")  # Free to use

def call_gemini(prompt):
    """Use Google Gemini instead of OpenAI"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Define the state
class AgentState(TypedDict):
    messages: List
    needs_clarification: bool
    clarification_question: str

# Define the nodes
def should_clarify(state: AgentState):
    """Determine if clarification is needed"""
    if not state['messages']:
        return {"needs_clarification": False}
    
    last_message = state['messages'][-1].content
    ambiguous_terms = ["it", "that", "this", "they", "them", "help", "something"]
    
    # Check for ambiguous terms
    needs_clarification = any(term in last_message.lower() for term in ambiguous_terms)
    return {"needs_clarification": needs_clarification}

def generate_clarification_question(state: AgentState):
    """Generate clarifying question using Gemini"""
    last_message = state['messages'][-1].content
    
    prompt = f"""
    The user said: "{last_message}"
    Generate a natural, helpful clarifying question to better understand what they mean.
    Respond with ONLY the question, nothing else.
    """
    
    clarification_question = call_gemini(prompt)
    
    return {
        "needs_clarification": True,
        "clarification_question": clarification_question,
        "messages": state['messages'] + [AIMessage(content=clarification_question)]
    }

def generate_response(state: AgentState):
    """Generate normal response using Gemini"""
    conversation_text = "\n".join([msg.content for msg in state['messages']])
    
    prompt = f"""
    Continue this conversation naturally and helpfully:
    
    {conversation_text}
    
    Assistant:
    """
    
    response = call_gemini(prompt)
    
    return {
        "messages": state['messages'] + [AIMessage(content=response)],
        "needs_clarification": False,
        "clarification_question": ""
    }

# Build the graph
def create_agent_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("should_clarify", should_clarify)
    workflow.add_node("ask_clarification", generate_clarification_question)
    workflow.add_node("generate_response", generate_response)
    
    workflow.set_entry_point("should_clarify")
    
    workflow.add_conditional_edges(
        "should_clarify",
        lambda state: "ask_clarification" if state["needs_clarification"] else "generate_response",
        ["ask_clarification", "generate_response"]
    )
    
    workflow.add_edge("ask_clarification", END)
    workflow.add_edge("generate_response", END)
    
    return workflow.compile()

# Initialize the agent
agent = create_agent_workflow()

# CLI interface
def run_chat():
    print("🚀 Chatbot is ready! Type 'exit', 'quit', or 'q' to stop.\n")
    
    # Initialize state
    state = {
        "messages": [AIMessage(content="Hello! I'm a smart chatbot that asks clarifying questions when needed. How can I help you today?")],
        "needs_clarification": False,
        "clarification_question": ""
    }
    
    # Show welcome message
    print(f"Assistant: {state['messages'][-1].content}\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Goodbye! 👋")
            break
        
        # Add user message to state
        state['messages'] = state['messages'] + [HumanMessage(content=user_input)]
        
        try:
            # Invoke the agent
            state = agent.invoke(state)
            
            # Print the agent's response
            if state['messages']:
                last_message = state['messages'][-1]
                print(f"Assistant: {last_message.content}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print()

# Start the chatbot
run_chat()





=======
import os
from dotenv import load_dotenv
from langgraph_pipeline import build_graph

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Please set OPENAI_API_KEY in your environment or .env file.")
    exit(1)

print("Starting Clarify_with_user (CLI). Type 'exit' to quit.")

graph, memory = build_graph(openai_api_key=OPENAI_API_KEY)

while True:
    user = input("You: ")
    if user.strip().lower() in {"exit", "quit", "q"}:
        print("Goodbye!")
        break

    state = {"messages": memory.get_messages(), "last_user": user}
    compiled = graph.compile()
    result_state = compiled.run(state)

    if result_state.get("clarify_needed"):
        q = result_state.get("clarify_question", "Could you clarify?")
        print(f"Assistant: {q}")
        clar = input("Clarification: ")
        memory.add_user(user)
        memory.add_user(clar)

        state = {"messages": memory.get_messages(), "last_user": user}
        compiled = graph.compile()
        result_state = compiled.run(state)
        assistant_reply = result_state.get("assistant_reply")
        print(f"Assistant: {assistant_reply}")
        memory.add_assistant(assistant_reply)
    else:
        assistant_reply = result_state.get("assistant_reply")
        print(f"Assistant: {assistant_reply}")
        memory.add_user(user)
        memory.add_assistant(assistant_reply)
>>>>>>> 6f59623052bc4a7e55c5d30d1e9e41061fa5e751

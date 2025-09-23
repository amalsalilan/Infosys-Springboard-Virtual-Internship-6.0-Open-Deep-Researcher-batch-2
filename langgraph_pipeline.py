
from typing import List, TypedDict
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from clarifier import analyze_user_intent

# Define the structure that holds the state of our conversation
class ConversationState(TypedDict):
    # The list of all messages in the chat
    messages: List[BaseMessage]
    # A potential question to ask the user for clarification
    follow_up_question: str

# Graph Nodes ---

def check_clarity_node(state: ConversationState):
    """
    First step in the graph: invokes the clarifier to check for ambiguity.
    """
    print("--- 🧠 Analyzing User Input... ---")
    question = analyze_user_intent(state["messages"])
    return {"follow_up_question": question}

def generate_response_node(state: ConversationState):
    """
    Generates the final answer once the user's query is clear.
    """
    print("--- 💬 Generating Response... ---")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    response = llm.invoke(state["messages"])
    # Append the AI's new message to the history
    updated_messages = state["messages"] + [response]
    return {"messages": updated_messages}

# Graph Edges

def decide_next_step(state: ConversationState):
    """
    Routes the conversation to the correct next node based on the clarity check.
    """
    print("--- 🤔 Deciding Next Step... ---")
    if state["follow_up_question"]:
        print("ROUTE: Ambiguity detected. Need to ask user for more details.")
        return "ask_clarification"
    else:
        print("ROUTE: Input is clear. Proceeding to generate a response.")
        return "generate_response"

# Graph Builder

def create_chatbot_workflow():
    """
    Constructs and compiles the conversational LangGraph workflow.
    """
    workflow = StateGraph(ConversationState)

    # Add the defined functions as nodes in the graph
    workflow.add_node("clarity_check", check_clarity_node)
    workflow.add_node("generate_response", generate_response_node)

    # The entry point is the clarity check
    workflow.set_entry_point("clarity_check")

    # Define the conditional routing
    workflow.add_conditional_edges(
        "clarity_check",
        decide_next_step,
        {
            "ask_clarification": END,
            "generate_response": "generate_response",
        },
    )

    # The response generation node marks the end of a turn
    workflow.add_edge("generate_response", END)

    # Compile the graph into a runnable application
    return workflow.compile()
# langgraph_pipeline.py  (REPLACE your existing file with this)
from typing import List, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from clarifier import analyze_user_intent
from smart_clarifier import generate_clarifying_question
from research_agent import run_research_subqueries, aggregate_and_summarize
from reflection_agent import reflective_analysis
from datetime import datetime
from typing import List
from typing_extensions import TypedDict, NotRequired
from langchain_core.messages import BaseMessage

class ConversationState(TypedDict):
    messages: List[BaseMessage]
    follow_up_question: NotRequired[str]
    
#date
def check_for_date_query(messages):
    """
    Checks if the latest user message is asking for today's date.
    """
    if not messages:
        return None

    latest_msg = None
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            latest_msg = m.content.lower()
            break

    if latest_msg and any(phrase in latest_msg for phrase in [
        "today's date", "what day is it", "date today", "current date"
    ]):
        current_date = datetime.now().strftime("%d/%m/%Y")
        return AIMessage(content=f"Today's date is {current_date}.")
    
    return None


# Node 1: Smart clarity check (uses fast model)
# Smart clarifier node
def smart_clarity_node(state: ConversationState):
    date_response = check_for_date_query(state["messages"])
    if date_response:
        updated_messages = state["messages"] + [date_response]
        return {"messages": updated_messages, "follow_up_question": None}

    q = generate_clarifying_question(state["messages"])
    return {"messages": state["messages"], "follow_up_question": q}



# Node 2: If clear, run parallel subqueries + research aggregation
def research_node(state: ConversationState):
    print("--- 🔍 Research Node: splitting into sub-queries and running parallel agents ---")
    # Extract latest human query
    latest_query = None
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            latest_query = m.content
            break
    context = "\n".join(m.content for m in state["messages"] if hasattr(m, "content") and m.content != latest_query)

    # Heuristic: split by commas or by simple decomposition (you can improve)
    # Example split: keywords, angles, comparison
    subqueries = []
    if latest_query:
        # A small heuristic decomposition:
        parts = [p.strip() for p in latest_query.split(" and ")]
        subqueries = parts if parts else [latest_query]

    # Run subqueries in parallel (web_search/docs etc.)
    sub_results = run_research_subqueries(latest_query or "", context, subqueries)

    # Aggregate and produce an AIMessage (this uses a heavy LLM)
    research_ai_message = aggregate_and_summarize(latest_query or "", context, sub_results)

    # Append the research message to the messages list and return
    updated_messages = state["messages"] + [research_ai_message]
    return {"messages": updated_messages}

# Node 3: Reflective analysis
def reflection_node(state: ConversationState):
    print("--- 🪞 Reflection Node: producing structured reflection ---")
    # Assume last message is the research AI message
    last_ai = None
    for m in reversed(state["messages"]):
        if isinstance(m, AIMessage):
            last_ai = m
            break
    if not last_ai:
        # Nothing to reflect on
        return {"messages": state["messages"]}
    reflection = reflective_analysis(last_ai)
    updated_messages = state["messages"] + [reflection]
    return {"messages": updated_messages}

# Decision node: if clarifier found a question -> ask user, else research
def decide_next_step(state: ConversationState):
    print("--- 🤔 Deciding Next Step... ---")
    if state["follow_up_question"]:
        print("ROUTE: Ambiguity detected -> ask clarification.")
        return "ask_clarification"
    else:
        print("ROUTE: Input clear -> run research.")
        return "research"

# Build workflow
def create_chatbot_workflow():
    workflow = StateGraph(ConversationState)

    # Nodes
    workflow.add_node("clarity_check", smart_clarity_node)
    # End state when clarification is needed: we will return the question to the app and stop
    # 'ask_clarification' is handled by returning END with follow_up_question set
    workflow.add_node("research", research_node)
    workflow.add_node("reflection", reflection_node)

    workflow.set_entry_point("clarity_check")

    # Conditional: if clarification needed -> END (app prints question), otherwise go research
    workflow.add_conditional_edges(
        "clarity_check",
        decide_next_step,
        {
            "ask_clarification": END,
            "research": "research",
        },
    )

    # After research, run reflection and then end
    workflow.add_edge("research", "reflection")
    workflow.add_edge("reflection", END)

    return workflow.compile()

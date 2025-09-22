# Concise Deep Research Agent with LangGraph and GROQ
# !pip install langgraph langchain groq

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from typing import List, Dict, Any

# Configuration
GROQ_API_KEY = "dummy_key"  # Replace with your actual API key

# Initialize GROQ LLM
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant", temperature=0.1)

# State definition
class ResearchState(TypedDict):
    user_query: str
    needs_clarification: bool
    research_plan: List[str]
    final_report: str

# Node 1: Validate Prompt (Word Count Check)
def validate_prompt(state: ResearchState) -> ResearchState:
    user_query = state["user_query"]
    word_count = len(user_query.split())
    
    if word_count < 4:
        print(f" Query too short ({word_count} words). Need at least 4 words for effective research.")
        return {**state, "needs_clarification": True}
    else:
        print(f" Query validated ({word_count} words)")
        return {**state, "needs_clarification": False}

# Node 2: Request Clarification
def request_clarification(state: ResearchState) -> ResearchState:
    print("\n CLARIFICATION NEEDED")
    print("Please provide more details about:")
    print("- What specific aspects you want to research")
    print("- Your research objectives")
    print("- Any particular focus areas")
    
    clarified_input = input("\n Enter detailed query: ").strip()
    
    return {
        **state,
        "user_query": clarified_input,
        "needs_clarification": False
    }

# Node 3: Create Research Plan
def create_research_plan(state: ResearchState) -> ResearchState:
    print(" Creating research plan...")
    
    planning_prompt = f"""
    Create a research plan for: "{state['user_query']}"
    
    Provide 5 specific research areas as a numbered list.
    Each area should be one focused research topic.
    """
    
    response = llm.invoke(planning_prompt)
    plan_lines = [line.strip() for line in response.content.split('\n') if line.strip() and (line.strip()[0].isdigit() or '-' in line)]
    
    print(f" Created plan with {len(plan_lines)} areas")
    return {**state, "research_plan": plan_lines}

# Node 4: Execute Research
def execute_research(state: ResearchState) -> ResearchState:
    print(f" Researching {len(state['research_plan'])} areas...")
    
    all_findings = []
    for i, area in enumerate(state['research_plan'], 1):
        print(f" Area {i}: {area}")
        
        research_prompt = f"""
        Research: {area}
        
        Provide comprehensive information including:
        - Key concepts and current understanding
        - Important facts and recent developments
        - Practical implications
        
        Be detailed and informative.
        """
        
        response = llm.invoke(research_prompt)
        all_findings.append(f"## {area}\n{response.content}")
    
    combined_findings = "\n\n".join(all_findings)
    print(" Research completed!")
    
    return {**state, "final_report": combined_findings}

# Node 5: Synthesize Report
def synthesize_report(state: ResearchState) -> ResearchState:
    print(" Creating final report...")
    
    synthesis_prompt = f"""
    Create a structured research report for: "{state['user_query']}"
    
    Based on these findings:
    {state['final_report']}
    
    Structure the report with:
    1. EXECUTIVE SUMMARY
    2. KEY FINDINGS
    3. CONCLUSIONS
    4. RECOMMENDATIONS
    
    Make it professional and comprehensive.
    """
    
    response = llm.invoke(synthesis_prompt)
    print(" Final report ready!")
    
    return {**state, "final_report": response.content}

# Routing function
def should_clarify(state: ResearchState) -> str:
    return "request_clarification" if state["needs_clarification"] else "create_research_plan"

# Build workflow
def create_workflow():
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("validate_prompt", validate_prompt)
    workflow.add_node("request_clarification", request_clarification)
    workflow.add_node("create_research_plan", create_research_plan)
    workflow.add_node("execute_research", execute_research)
    workflow.add_node("synthesize_report", synthesize_report)
    
    # Add edges
    workflow.set_entry_point("validate_prompt")
    workflow.add_conditional_edges("validate_prompt", should_clarify)
    workflow.add_edge("request_clarification", "validate_prompt")
    workflow.add_edge("create_research_plan", "execute_research")
    workflow.add_edge("execute_research", "synthesize_report")
    workflow.add_edge("synthesize_report", END)
    
    return workflow.compile()

# Main function
def start_research():
    print(" DEEP RESEARCH AGENT")
    print("="*40)
    
    while True:
        user_query = input("\n Enter research query (or 'quit'): ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print(" Session ended!")
            break
            
        if not user_query:
            continue
        
        print(f" Processing: '{user_query}'")
        
        try:
            app = create_workflow()
            initial_state = {
                "user_query": user_query,
                "needs_clarification": False,
                "research_plan": [],
                "final_report": ""
            }
            
            final_state = app.invoke(initial_state)
            
            print("\n" + "="*60)
            print(" RESEARCH REPORT")
            print("="*60)
            print(final_state["final_report"])
            print("="*60)
            
        except Exception as e:
            print(f" Error: {e}")

# Ready message
print(" Ready! Run start_research() to begin!")

# Auto-start (uncomment to activate)
start_research()
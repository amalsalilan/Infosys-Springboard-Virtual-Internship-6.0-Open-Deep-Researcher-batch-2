# Enhanced Research Agent WITH REFLECTION PATTERN (Gemini Version)
import os
import sys
import time
import re
import requests
import json
from datetime import datetime
from typing import List, Dict, Any, TypedDict

# Configuration - ADD YOUR API KEYS HERE
GEMINI_API_KEY = "..."  
TAVILY_API_KEY = "..."  
TAVILY_ENDPOINT = "https://api.tavily.com/search"
DEFAULT_COUNTRY = "India"
MAX_REFLECTION_ITERATIONS = 2

# Try to import required packages
try:
    import google.generativeai as genai
    from langgraph.graph import StateGraph, END
except ImportError:
    print(" Missing required packages. Install with:")
    print("pip install google-generativeai langgraph")
    sys.exit(1)

# Configure Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f" Gemini configuration failed: {e}")
    print("Please check your GEMINI_API_KEY")
    sys.exit(1)

# Enhanced State with Reflection
class ResearchState(TypedDict):
    user_query: str
    original_query: str
    query_type: str
    needs_followup: bool
    followup_questions: List[str]
    collected_params: Dict[str, str]
    enriched_query: str
    research_plan: List[str]
    research_iteration: int
    research_quality_score: float
    reflection_feedback: str
    needs_refinement: bool
    brief_summary: str
    final_report: str
    
    user_country: str
    current_date: str

# Gemini Chat Helper Functions
def gemini_chat(prompt: str, streaming: bool = False) -> str:
    """Send prompt to Gemini and return response"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        if streaming:
            response = model.generate_content(prompt, stream=True)
            full_response = ""
            for chunk in response:
                if chunk.text:
                    token = chunk.text
                    full_response += token
                    sys.stdout.write(token)
                    sys.stdout.flush()
                    time.sleep(0.02)
            print()  # New line after streaming
            return full_response
        else:
            response = model.generate_content(prompt)
            return response.text if response.text else "No response generated"

    except Exception as e:
        print(f"[Gemini Error] {e}")
        return f"Error: {str(e)}"

def gemini_chat_no_stream(prompt: str) -> str:
    """Gemini without streaming for background tasks"""
    return gemini_chat(prompt, streaming=False)

def gemini_chat_stream(prompt: str) -> str:
    """Gemini with streaming for user-facing responses"""
    return gemini_chat(prompt, streaming=True)

# Tavily Search Helper
def tavily_search(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """Perform Tavily web search and return structured results."""
    try:
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "max_results": num_results,
            "include_raw_content": False
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(TAVILY_ENDPOINT, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        return [
            {
                "title": item.get("title", "No title"),
                "url": item.get("url", "#"),
                "snippet": item.get("content", "")[:400]
            }
            for item in data.get("results", [])[:num_results]
        ]
    except Exception as e:
        print(f"[Tavily Error] {e}")
        return []

# Classify Query Type
def classify_query(state: ResearchState) -> ResearchState:
    """Classify the type of query."""
    query = state["user_query"]

    classification_prompt = f"""
    Classify this query into ONE category:
    - travel, local_search, shopping, research, event

    Query: "{query}"

    Respond with ONLY the category name.
    """

    try:
        query_type = gemini_chat_no_stream(classification_prompt).strip().lower()
        query_type = re.sub(r'[^a-z_]', '', query_type)

        valid_types = ['travel', 'local_search', 'shopping', 'research', 'event']
        if query_type not in valid_types:
            query_type = 'research'

        print(f"🏷  Query classified as: {query_type.upper()}")
        return {**state, "query_type": query_type}
    except Exception as e:
        return {**state, "query_type": "research"}

# Generate Follow-up Questions
def generate_followup_questions(state: ResearchState) -> ResearchState:
    """Generate smart follow-up questions."""
    query = state["user_query"]
    query_type = state["query_type"]

    question_prompt = f"""
    User query: "{query}"
    Type: {query_type}

    Generate 2-4 follow-up questions to gather missing details.

    For TRAVEL: dates, budget, starting location, duration
    For LOCAL_SEARCH: location, budget, preferences
    For SHOPPING: budget, features, preferred stores

    If all info is present, respond "COMPLETE".
    Format: Start each question with "Q:"
    """

    try:
        content = gemini_chat_no_stream(question_prompt).strip()

        if "COMPLETE" in content.upper():
            print("✅ Query complete, no follow-up needed\n")
            return {**state, "needs_followup": False, "followup_questions": []}

        questions = [
            line.replace("Q:", "").strip()
            for line in content.split('\n')
            if line.strip() and ('?' in line or line.startswith('Q:'))
        ][:4]

        if questions:
            print(f"📋 Generated {len(questions)} follow-up questions\n")
            return {**state, "needs_followup": True, "followup_questions": questions}
        else:
            return {**state, "needs_followup": False, "followup_questions": []}

    except Exception as e:
        return {**state, "needs_followup": False, "followup_questions": []}

# Collect Parameters
def collect_parameters(state: ResearchState) -> ResearchState:
    """Interactive parameter collection."""
    questions = state["followup_questions"]
    params = state.get("collected_params", {})

    print("\n" + "="*50)
    print("🔍 I need a few more details:")
    print("="*50 + "\n")

    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")
        answer = input("   → ").strip()
        params[f"q{i}"] = answer if answer else "Not specified"

    print("\n✅ Thanks! Processing...\n")
    return {**state, "collected_params": params, "needs_followup": False}

# Enrich Query
def enrich_query_with_params(state: ResearchState) -> ResearchState:
    """Combine query with collected parameters."""
    original = state["user_query"]
    params = state.get("collected_params", {})

    if not params:
        enriched = f"{original} (Date: {state['current_date']}, Region: {state['user_country']})"
    else:
        param_text = "; ".join([f"{k}: {v}" for k, v in params.items() if v != "Not specified"])
        enriched = f"{original}. Details: {param_text}. Date: {state['current_date']}, Region: {state['user_country']}"

    print(f"🔧 Query enriched\n")
    return {**state, "enriched_query": enriched}

# Create Research Plan
def create_research_plan(state: ResearchState) -> ResearchState:
    """Create detailed research plan."""
    enriched_query = state["enriched_query"]
    query_type = state["query_type"]

    print("🧩 Creating research plan...")

    # Use reflection feedback if available
    feedback_context = ""
    if state.get("reflection_feedback"):
        feedback_context = f"\n\nPrevious feedback to address:\n{state['reflection_feedback']}"

    planning_prompt = f"""
    Create a 3-5 point research plan for this {query_type} query:
    "{enriched_query}"{feedback_context}

    For TRAVEL: transport, accommodation, costs, routes, tips
    For LOCAL_SEARCH: top options, pricing, locations, reviews, contact
    For SHOPPING: products, prices, where to buy, deals

    Number each point clearly.
    """

    try:
        response = gemini_chat_no_stream(planning_prompt)
        plan = [
            re.sub(r'^[\d\-\.]+\s*', '', line.strip())
            for line in response.split('\n')
            if line.strip() and (line[0].isdigit() or line.strip().startswith('-'))
        ][:5]

        print(f"✅ Plan created with {len(plan)} areas\n")
        return {**state, "research_plan": plan}
    except Exception as e:
        return {**state, "research_plan": ["Research: " + enriched_query]}

# Execute Research
def execute_research(state: ResearchState) -> ResearchState:
    """Execute deep research with web data."""
    plan = state["research_plan"]
    iteration = state.get("research_iteration", 0)

    print(f"🔎 Research iteration {iteration + 1}...\n")
    all_findings = []

    for i, area in enumerate(plan, 1):
        search_query = f"{area} {state['current_date']}"
        print(f"🌐 Area {i}: {area[:50]}...")

        results = tavily_search(search_query, num_results=3)
        if not results:
            results = tavily_search(area, num_results=3)

        if results:
            web_context = "\n\n".join([
                f"Source: {r['title']}\nURL: {r['url']}\nContent: {r['snippet']}"
                for r in results
            ])
        else:
            web_context = "No web results found."

        analysis_prompt = f"""
        Research Area: {area}
        Context: {state['enriched_query']}

        Web Results:
        {web_context}

        Provide detailed analysis with specific information.
        Focus on practical, actionable details.
        """

        try:
            response = gemini_chat_no_stream(analysis_prompt)
            all_findings.append(f"## {area}\n\n{response}\n\n---\n")
            print(f"   ✅ Completed area {i}")
        except Exception as e:
            all_findings.append(f"## {area}\n\nResearch incomplete.\n\n---\n")
            print(f"   ❌ Failed area {i}")

    combined = "\n".join(all_findings)
    print("✅ Research phase complete!\n")
    return {
        **state,
        "final_report": combined,
        "research_iteration": iteration + 1
    }

# Reflection Node
def reflect_on_research(state: ResearchState) -> ResearchState:
    """Reflect on research quality and decide if refinement is needed."""
    print("🔍 Reflecting on research quality...")

    reflection_prompt = f"""
    Evaluate this research output:

    Original Query: "{state['original_query']}"
    Research Output:
    {state['final_report'][:2000]}

    Evaluate on:
    1. Completeness: Does it answer the query fully?
    2. Specificity: Concrete details (prices, dates, names)?
    3. Actionability: Can user act on this information?

    Respond in this format:
    SCORE: [0-10]
    NEEDS_REFINEMENT: [YES/NO]
    FEEDBACK: [brief feedback]
    """

    try:
        reflection_content = gemini_chat_no_stream(reflection_prompt)

        # Extract score
        score_match = re.search(r'SCORE:\s*(\d+)', reflection_content)
        score = float(score_match.group(1)) if score_match else 7.0

        # Check if refinement needed
        needs_refinement = "NEEDS_REFINEMENT: YES" in reflection_content.upper()

        # Extract feedback
        feedback_match = re.search(r'FEEDBACK:(.*?)(?:\n\n|\Z)', reflection_content, re.DOTALL)
        feedback = feedback_match.group(1).strip() if feedback_match else ""

        print(f"📊 Quality Score: {score}/10")

        # Don't refine if score is good or max iterations reached
        iteration = state.get("research_iteration", 1)
        if score >= 7.0 or iteration >= MAX_REFLECTION_ITERATIONS:
            print("✅ Research quality acceptable\n")
            needs_refinement = False
        elif needs_refinement:
            print(f"⚠  Quality needs improvement")
            print(f"Feedback: {feedback[:80]}...\n")

        return {
            **state,
            "research_quality_score": score,
            "reflection_feedback": feedback,
            "needs_refinement": needs_refinement and iteration < MAX_REFLECTION_ITERATIONS
        }

    except Exception as e:
        print(f"[Reflection Error] {e}")
        return {
            **state,
            "research_quality_score": 7.0,
            "needs_refinement": False
        }

# Generate Brief Summary
def generate_brief_summary(state: ResearchState) -> ResearchState:
    """Create quick bullet-point summary."""
    print("📝 Generating summary...")

    summary_prompt = f"""
    Create a brief bullet-point summary (4-6 points) for:
    "{state['enriched_query']}"

    Research:
    {state['final_report'][:1500]}

    Format as bullet points.
    Focus on actionable information.
    """

    try:
        response = gemini_chat_no_stream(summary_prompt)
        return {**state, "brief_summary": response}
    except:
        return {**state, "brief_summary": "Summary unavailable."}

# Synthesize Final Report
def synthesize_report(state: ResearchState) -> ResearchState:
    """Create comprehensive final report."""
    print("🧾 Creating final report...\n")

    synthesis_prompt = f"""
    Create a comprehensive report for:
    "{state['original_query']}"

    Context: {state['enriched_query']}

    Research Findings:
    {state['final_report']}

    Summary:
    {state['brief_summary']}

    Create a well-structured, actionable report.
    """

    try:
        response = gemini_chat_stream(synthesis_prompt)
        print("\n" + "="*60)
        print("✅ REPORT COMPLETE!")
        print("="*60)
        return {**state, "final_report": response}
    except Exception as e:
        return state

# Decision Functions
def should_ask_followup(state: ResearchState) -> str:
    """Route based on follow-up needs."""
    return "collect_parameters" if state["needs_followup"] else "enrich_query_with_params"

def should_refine_research(state: ResearchState) -> str:
    """Decide whether to refine research or proceed."""
    if state.get("needs_refinement", False):
        print("🔄 Refining research based on feedback...\n")
        return "create_research_plan"
    else:
        return "generate_brief_summary"

# Create Workflow
def create_workflow():
    """Create the research workflow graph."""
    workflow = StateGraph(ResearchState)

    # Add all nodes
    workflow.add_node("classify_query", classify_query)
    workflow.add_node("generate_followup_questions", generate_followup_questions)
    workflow.add_node("collect_parameters", collect_parameters)
    workflow.add_node("enrich_query_with_params", enrich_query_with_params)
    workflow.add_node("create_research_plan", create_research_plan)
    workflow.add_node("execute_research", execute_research)
    workflow.add_node("reflect_on_research", reflect_on_research)
    workflow.add_node("generate_brief_summary", generate_brief_summary)
    workflow.add_node("synthesize_report", synthesize_report)

    # Define workflow
    workflow.set_entry_point("classify_query")
    workflow.add_edge("classify_query", "generate_followup_questions")
    workflow.add_conditional_edges("generate_followup_questions", should_ask_followup)
    workflow.add_edge("collect_parameters", "enrich_query_with_params")
    workflow.add_edge("enrich_query_with_params", "create_research_plan")
    workflow.add_edge("create_research_plan", "execute_research")
    workflow.add_edge("execute_research", "reflect_on_research")
    workflow.add_conditional_edges("reflect_on_research", should_refine_research)
    workflow.add_edge("generate_brief_summary", "synthesize_report")
    workflow.add_edge("synthesize_report", END)

    return workflow.compile()

# Main Application
def main():
    """Main research agent application."""
    print("\n" + "="*70)
    print("🤖 ENHANCED RESEARCH AGENT (Gemini Version)")
    print("   With Reflection Pattern & Web Search")
    print("="*70)
    print("\n✨ Features:")
    print("  • Smart query classification")
    print("  • Follow-up questions")
    print("  • Self-reflection & quality assessment")
    print("  • Real-time web research")
    print("  • Automatic refinement")
    print("="*70 + "\n")

    # Test API connections
    print("🔌 Testing API connections...")
    try:
        # Test Gemini
        test_response = gemini_chat_no_stream("Say 'Gemini OK' if working.")
        if "OK" in test_response:
            print("✅ Gemini API: Connected")
        else:
            print("❌ Gemini API: Issue detected")
    except Exception as e:
        print(f"❌ Gemini API: Failed - {e}")
        return

    try:
        # Test Tavily
        test_results = tavily_search("test", 1)
        if test_results:
            print("✅ Tavily API: Connected")
        else:
            print("❌ Tavily API: Issue detected")
    except Exception as e:
        print(f"❌ Tavily API: Failed - {e}")
        return

    print("\n" + "="*70)

    # Main loop
    while True:
        user_query = input("\n🔍 What would you like to research? (or 'quit'): ").strip()

        if user_query.lower() in ["quit", "exit", "q"]:
            print("\n👋 Thank you for using Research Agent!")
            break

        if not user_query:
            continue

        try:
            app = create_workflow()

            initial_state = {
                "user_query": user_query,
                "original_query": user_query,
                "query_type": "",
                "needs_followup": False,
                "followup_questions": [],
                "collected_params": {},
                "enriched_query": "",
                "research_plan": [],
                "research_iteration": 0,
                "research_quality_score": 0.0,
                "reflection_feedback": "",
                "needs_refinement": False,
                "brief_summary": "",
                "final_report": "",
                "user_country": DEFAULT_COUNTRY,
                "current_date": datetime.now().strftime("%Y-%m-%d")
            }

            print("\n🚀 Starting research process...\n")
            final_state = app.invoke(initial_state)

            print("\n" + "="*70)
            print("📊 FINAL RESEARCH REPORT")
            print("="*70)
            print(final_state["final_report"])
            print("="*70 + "\n")

        except KeyboardInterrupt:
            print("\n\n⏹  Research cancelled.\n")
            continue
        except Exception as e:
            print(f"\n❌ Research failed: {e}\n")
            continue

if _name_ == "_main_":
   main()

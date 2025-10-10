
# Enhanced Research Agent WITH REFLECTION PATTERN

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from typing import List, Dict, Any
from langchain.callbacks.base import BaseCallbackHandler
import sys, time, re, requests, json
from datetime import datetime

# Configuration

GROQ_API_KEY = "gsk_xxx"
TAVILY_API_KEY = "tvly-dev-xxx"
TAVILY_ENDPOINT = "https://api.tavily.com/search"
DEFAULT_COUNTRY = "India"
MAX_REFLECTION_ITERATIONS = 2  

# Typing Stream Callback

class TypingCallbackHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        sys.stdout.write(token)
        sys.stdout.flush()
        time.sleep(0.03)

# Initialize LLMs

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.2,
    streaming=True,
    callbacks=[TypingCallbackHandler()]
)

llm_no_stream = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.3,
    streaming=False
)

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
        response = requests.post(TAVILY_ENDPOINT, json=payload, headers=headers, timeout=10)
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
        response = llm_no_stream.invoke(classification_prompt)
        query_type = response.content.strip().lower()
        query_type = re.sub(r'[^a-z_]', '', query_type)
        
        valid_types = ['travel', 'local_search', 'shopping', 'research', 'event']
        if query_type not in valid_types:
            query_type = 'research'
            
        print(f"🏷️  Query classified as: {query_type.upper()}")
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
        response = llm_no_stream.invoke(question_prompt)
        content = response.content.strip()
        
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
    
    print("\n" + "="*60)
    print("🔍 I need a few more details:")
    print("="*60 + "\n")
    
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")
        answer = input("   → ").strip()
        params[f"question_{i}"] = answer if answer else "Not specified"
    
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
        param_text = "; ".join([v for v in params.values() if v != "Not specified"])
        enriched = f"{original}. Context: {param_text}. Date: {state['current_date']}, Region: {state['user_country']}"
    
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
        response = llm_no_stream.invoke(planning_prompt)
        plan = [
            re.sub(r'^[\d\-\.KATEX_INLINE_CLOSE]+\s*', '', line.strip())
            for line in response.content.split('\n') 
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
        
        results = tavily_search(search_query, num_results=6)
        if not results:
            results = tavily_search(area, num_results=5)
        
        web_context = "\n\n".join([
            f"Source: {r['title']}\nURL: {r['url']}\nContent: {r['snippet']}"
            for r in results
        ])
        
        analysis_prompt = f"""
        Research Area: {area}
        Context: {state['enriched_query']}
        
        Web Results:
        {web_context}
        
        Provide detailed analysis:
        
        ### {area}
        
        **Overview:** (2-3 sentences)
        
        **Key Details:**
        - Point 1
        - Point 2
        - Point 3
        
        **Pricing/Costs:** (if applicable)
        - Specific prices and ranges
        
        **Actionable Info:**
        - Practical recommendations
        
        **Sources:**
        - [Name](URL)
        
        Extract specific data: prices, dates, names, contact info.
        """
        
        try:
            response = llm_no_stream.invoke(analysis_prompt)
            all_findings.append(response.content + "\n\n---\n")
        except Exception as e:
            all_findings.append(f"### {area}\n\nResearch incomplete.\n\n---\n")
    
    combined = "\n".join(all_findings)
    print("✅ Research phase complete!\n")
    return {
        **state, 
        "final_report": combined,
        "research_iteration": iteration + 1
    }


# 🔍 REFLECTION NODE - NEW!

def reflect_on_research(state: ResearchState) -> ResearchState:
    """
    REFLECTION PATTERN: Critique the research quality and decide if refinement is needed.
    """
    print("🔍 Reflecting on research quality...")
    
    reflection_prompt = f"""
    You are a quality assessor. Evaluate this research output:
    
    Original Query: "{state['original_query']}"
    Research Output:
    {state['final_report'][:3000]}
    
    Evaluate on these criteria:
    1. **Completeness**: Does it answer the user's query fully?
    2. **Specificity**: Are there concrete details (prices, dates, names)?
    3. **Actionability**: Can the user act on this information?
    4. **Source Quality**: Are credible sources cited?
    5. **Relevance**: Is the info current and relevant?
    
    Respond in this format:
    SCORE: [0-10]
    
    STRENGTHS:
    - Point 1
    - Point 2
    
    WEAKNESSES:
    - Issue 1
    - Issue 2
    
    NEEDS_REFINEMENT: [YES/NO]
    
    IMPROVEMENT_SUGGESTIONS:
    - Specific suggestion 1
    - Specific suggestion 2
    """
    
    try:
        response = llm_no_stream.invoke(reflection_prompt)
        reflection_content = response.content
        
        # Extract score
        score_match = re.search(r'SCORE:\s*(\d+)', reflection_content)
        score = float(score_match.group(1)) if score_match else 7.0
        
        # Check if refinement needed
        needs_refinement = "NEEDS_REFINEMENT: YES" in reflection_content.upper()
        
        # Extract improvement suggestions
        improvements_match = re.search(
            r'IMPROVEMENT_SUGGESTIONS:(.*?)(?:\n\n|\Z)', 
            reflection_content, 
            re.DOTALL
        )
        feedback = improvements_match.group(1).strip() if improvements_match else ""
        
        print(f"📊 Quality Score: {score}/10")
        
        # Don't refine if score is good or max iterations reached
        iteration = state.get("research_iteration", 1)
        if score >= 7.5 or iteration >= MAX_REFLECTION_ITERATIONS:
            print("✅ Research quality acceptable\n")
            needs_refinement = False
        elif needs_refinement:
            print(f"⚠️  Quality needs improvement (iteration {iteration}/{MAX_REFLECTION_ITERATIONS})")
            print(f"Feedback: {feedback[:100]}...\n")
        
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
    print("📝 Generating summary...\n")
    
    summary_prompt = f"""
    Create a brief bullet-point summary (5-7 points) for:
    "{state['enriched_query']}"
    
    Research:
    {state['final_report'][:2000]}
    
    Format:
    • Point 1
    • Point 2
    
    Focus on actionable information.
    """
    
    try:
        response = llm_no_stream.invoke(summary_prompt)
        return {**state, "brief_summary": response.content}
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
    Quality Score: {state.get('research_quality_score', 'N/A')}/10
    
    Research:
    {state['final_report']}
    
    Structure:
    
    # 📊 RESEARCH REPORT
    ## Query: {state['original_query']}
    **Date:** {state['current_date']}
    **Type:** {state['query_type'].title()}
    **Quality Score:** {state.get('research_quality_score', 'N/A')}/10
    
    ---
    
    ## 🎯 QUICK SUMMARY
    {state['brief_summary']}
    
    ---
    
    ## 📋 DETAILED FINDINGS
    [Well-organized findings]
    
    ## 💡 KEY RECOMMENDATIONS
    [Actionable next steps]
    
    ## 📚 REFERENCES
    [All sources]
    
    Be detailed and actionable.
    """
    
    try:
        response = llm.invoke(synthesis_prompt)
        print("\n✅ Report complete!\n")
        return {**state, "final_report": response.content}
    except Exception as e:
        return state


# Decision Functions (Conditional Routing)

def should_ask_followup(state: ResearchState) -> str:
    """Route based on follow-up needs."""
    return "collect_parameters" if state["needs_followup"] else "enrich_query_with_params"

def should_refine_research(state: ResearchState) -> str:
    """
    REFLECTION ROUTING: Decide whether to refine research or proceed.
    """
    if state.get("needs_refinement", False):
        print("🔄 Refining research based on feedback...\n")
        return "create_research_plan"  # Loop back to improve
    else:
        return "generate_brief_summary"  # Proceed to summary


# Create Workflow with Reflection

def create_workflow():
    wf = StateGraph(ResearchState)
    
    # Add all nodes
    wf.add_node("classify_query", classify_query)
    wf.add_node("generate_followup_questions", generate_followup_questions)
    wf.add_node("collect_parameters", collect_parameters)
    wf.add_node("enrich_query_with_params", enrich_query_with_params)
    wf.add_node("create_research_plan", create_research_plan)
    wf.add_node("execute_research", execute_research)
    wf.add_node("reflect_on_research", reflect_on_research)  # NEW REFLECTION NODE
    wf.add_node("generate_brief_summary", generate_brief_summary)
    wf.add_node("synthesize_report", synthesize_report)
    
    # Define workflow with reflection loop
    wf.set_entry_point("classify_query")
    wf.add_edge("classify_query", "generate_followup_questions")
    
    # Conditional: ask follow-up or skip
    wf.add_conditional_edges("generate_followup_questions", should_ask_followup)
    
    wf.add_edge("collect_parameters", "enrich_query_with_params")
    wf.add_edge("enrich_query_with_params", "create_research_plan")
    wf.add_edge("create_research_plan", "execute_research")
    
    # NEW: After research, reflect on quality
    wf.add_edge("execute_research", "reflect_on_research")
    
    # Conditional: refine research or proceed
    # This creates the REFLECTION LOOP
    wf.add_conditional_edges("reflect_on_research", should_refine_research)
    
    wf.add_edge("generate_brief_summary", "synthesize_report")
    wf.add_edge("synthesize_report", END)
    
    return wf.compile()


# Main Loop

def start_research():
    print("\n" + "="*70)
    print("🤖 ENHANCED RESEARCH AGENT WITH REFLECTION")
    print("   (GROQ + LangGraph + Tavily)")
    print("="*70)
    print("\n✨ Features:")
    print("  • Intelligent follow-up questions")
    print("  • Self-reflective quality assessment")
    print("  • Automatic research refinement")
    print("  • Real-time web data")
    print("="*70 + "\n")

    while True:
        user_query = input("🔍 What would you like to research? (or 'quit'): ").strip()
        
        if user_query.lower() in ["quit", "exit", "q"]:
            print("\n👋 Goodbye!\n")
            break
            
        if not user_query:
            continue

        try:
            app = create_workflow()
            
            init_state = {
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
                "current_date": datetime.now().strftime("%Y-%m-%d (%A)")
            }
            
            print("\n⏳ Processing...\n")
            final_state = app.invoke(init_state)

            print("\n" + "="*70)
            print(final_state["final_report"])
            print("="*70 + "\n")

        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled.\n")
            continue
        except Exception as e:
            print(f"\n❌ [ERROR] {e}\n")
            continue


# Run

if __name__ == "__main__":
    start_research()
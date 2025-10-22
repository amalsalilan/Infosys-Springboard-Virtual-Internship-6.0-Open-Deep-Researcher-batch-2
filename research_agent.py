# research_agent.py
from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from parallel_agents import run_parallel_agents, agent_from_fn

# Use a stronger model for research phase
RESEARCH_MODEL = "gemini-2.5-pro"

# ---- Placeholders for real sub-query/tool functions ----
def web_search_subquery(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Placeholder function that should run a web search and return summarized results.
    Replace with actual search integration (e.g., SerpAPI, Custom Google Search).
    """
    # Example stubbed response
    return {"source": "web_search", "query": query, "results": [f"result-{i} for {query}" for i in range(1, top_k+1)]}

def docs_search_subquery(query: str, docs: List[str]) -> Dict[str, Any]:
    return {"source": "docs", "query": query, "hits": [f"doc-hit-{d}" for d in docs[:3]]}

def run_research_subqueries(main_query: str, context: str, subqueries: List[str] = None) -> List[Dict[str, Any]]:
    """
    Runs multiple subqueries in parallel using the parallel_agents helper.
    If no subqueries are provided, automatically generate research angles dynamically.
    """
    if not subqueries:
        # Dynamically generate 5 general research angles
        subqueries = [
            f"Overview and background information on: {main_query}",
            f"Key findings, statistics, and data about: {main_query}",
            f"Different perspectives or opinions on: {main_query}",
            f"Potential challenges, risks, or limitations related to: {main_query}",
            f"Recommendations, solutions, or best practices regarding: {main_query}"
        ]

    agents = [agent_from_fn(web_search_subquery, sq, 3) for sq in subqueries]
    results = run_parallel_agents(agents, max_workers=min(8, len(agents)))
    return results


def aggregate_and_summarize(main_query: str, context: str, subquery_results: List[Dict[str, Any]]) -> AIMessage:
    """
    Aggregates multiple subquery results into a detailed research report.
    """
    llm = ChatGoogleGenerativeAI(model=RESEARCH_MODEL, temperature=0.3)
    
    # Prepare a clear summary of all subquery outputs
    sub_summary = "\n".join(
        f"- {r.get('source')}: { (r.get('results') or r.get('hits') or r.get('error'))[:5] }"
        for r in subquery_results
    )

    prompt = f"""
You are an expert research assistant. The user's query is:

\"\"\"{main_query}\"\"\"

Context:
\"\"\"{context}\"\"\"

Subquery findings:
{sub_summary}

Task:
Produce a **structured research report** including the following sections:
1. **Study Title**  
2. **Study Description / Scope**  
3. **Reliability & Relevance of the Data**  
4. **Missing Perspectives / Biases**  
5. **Improvements / Recommendations**  
6. **Executive Summary**  
7. **Key Findings**

Return the output as clearly labeled sections. Each section should have multiple points if applicable.
Respond **only in text**, do not include JSON or code format.
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response

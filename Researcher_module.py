import os

os.environ["GOOGLE_API_KEY"] = "Gemini_api_key"
os.environ["TAVILY_API_KEY"] ="Tavily_api_key"

import os
import time
import json
import re
from datetime import datetime
import google.generativeai as genai
from langgraph.graph import StateGraph
from tavily import TavilyClient

# =========================
#  INITIAL SETUP
# =========================
try:
    model = genai.GenerativeModel("gemini-2.5-flash")
    print("✅ Using Gemini 2.5 Flash")
except:
    model = genai.GenerativeModel("gemini-1.5-flash")
    print("⚙️ Fallback to Gemini 1.5 Flash")

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# =========================
#  SAFE GENERATION WRAPPER
# =========================
def safe_generate(prompt):
    """Safely call Gemini with fallback handling."""
    try:
        time.sleep(1)
        result = model.generate_content(prompt)
        return result.text.strip()
    except Exception as e:
        print(f"[Gemini Warning] {e} — switching to fallback model...")
        fallback = genai.GenerativeModel("gemini-1.5-flash")
        result = fallback.generate_content(prompt)
        return result.text.strip()

# =========================
# 💾 CHAT STATE CLASS
# =========================
class ChatState(dict):
    def __init__(self):
        super().__init__(user_input="", response="", history=[], context={}, reflection="")

# =========================
#  CLARIFY NODE 
# =========================
def clarify_node(state: ChatState):
    user_input = state["user_input"].strip()
    history = "\n".join(state["history"][-8:])

    clarify_prompt = f"""
You are an intelligent general-purpose assistant that knows when to ask clarifying questions.

Today's date: {datetime.now().strftime('%B %d, %Y')}
Conversation so far:
{history}

User said: "{user_input}"

Step 1: Determine intent type — is it:
(a) Direct factual (e.g., "What is AI?")
(b) Creative/open-ended (e.g., "Plan a trip", "Design a system", "Write a report")
(c) Instructional (e.g., "Explain X", "Summarize Y")

Step 2: Behavior
- If the request is **factual or clear**, respond with: {{"status": "clear"}}
- If it's **open-ended** (trip planning, designing, writing, building, etc.), ask up to **3 smart, contextual questions**.
  * Focus on specifics like time, duration, purpose, audience, or constraints.
  * Keep them short and natural.

Respond **only in valid JSON**, e.g.:
{{"status":"unclear","questions":["Q1","Q2"]}}
or
{{"status":"clear"}}
"""

    raw = safe_generate(clarify_prompt)
    match = re.search(r"\{.*\}", raw, re.S)

    if not match:
        parsed = {"status": "unclear", "questions": ["Can you please clarify your request?"]}
    else:
        try:
            parsed = json.loads(match.group())
        except:
            parsed = {"status": "unclear", "questions": ["Could you elaborate more?"]}

    if parsed.get("status") == "clear":
        response = "Got it — let me work on that report."
        next_step = "research"
    else:
        qs = parsed.get("questions", [])
        response = "\n".join(qs)
        next_step = "clarify"

    state["response"] = response
    state["history"].append(f"User: {user_input}")
    state["history"].append(f"Bot: {response}")
    return state, next_step

# =========================
#  RESEARCH NODE
# =========================
def research_node(state: ChatState):
    user_input = state["user_input"]
    history_context = "\n".join(state["history"][-10:])

    # Tavily live data
    try:
        search_results = tavily_client.search(query=user_input)
        summary = "\n".join([r["content"] for r in search_results.get("results", [])[:3]])
    except Exception:
        summary = "Sorry, I couldn’t fetch live data at the moment."

    research_prompt = f"""
You are a highly capable general-purpose research assistant.
Today's date: {datetime.now().strftime('%B %d, %Y')}

User query: "{user_input}"

Conversation context:
{history_context}

Supporting info (from Tavily or prior context):
{summary}

Generate a structured report in this exact format:

==== RESEARCH REPORT ====
**1. Overview:** (Brief background or purpose)
**2. Key Findings / Insights:** (Main facts, insights, or steps)
**3. Analysis / Interpretation:** (Reasoning, implications, or deeper understanding)
**4. Recommendations / Next Steps:** (If applicable)
**5. Summary:** (Concise final summary)
=========================

Keep it balanced: clear, factual, and to the point.
Avoid repetition or filler content.
"""

    result = safe_generate(research_prompt)
    state["response"] = result
    state["history"].append(f"User: {user_input}")
    state["history"].append(f"Bot: {result}")
    return state, "reflect"

# =========================
#  SIMPLIFIED REFLECTION NODE
# =========================
def reflection_node(state: ChatState):
    report_text = state["response"]

    reflection_prompt = f"""
You are a reflection and self-improvement module.

Review the following report internally for:
- Clarity
- Factual accuracy
- Missing details
- Logical flow

Then output **only** the improved version of the report (in the same 5-section structure).
Do not include your evaluation or self-analysis in the response.

Report:
{report_text}
"""

    improved = safe_generate(reflection_prompt)
    state["reflection"] = improved
    state["response"] = improved
    state["history"].append("Bot (Refined Report): " + improved)
    return state, "end"

# =========================
#  BUILD LANGGRAPH PIPELINE
# =========================
graph = StateGraph(ChatState)
graph.add_node("clarify", clarify_node)
graph.add_node("research", research_node)
graph.add_node("reflect", reflection_node)
graph.set_entry_point("clarify")
graph.add_edge("clarify", "research")
graph.add_edge("clarify", "clarify")
graph.add_edge("research", "reflect")
chatbot = graph.compile()

# =========================
#  CHAT LOOP
# =========================
print("🤖 Intelligent Research Assistant with Reflection (type 'exit' to stop)\n")
state = ChatState()

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["exit", "quit"]:
        print("Bot: Goodbye! 👋")
        break

    state["user_input"] = user_input
    state, next_step = clarify_node(state)

    if next_step == "research":
        state, _ = research_node(state)
        state, _ = reflection_node(state)

    print(f"Bot:\n{state['response']}")
    print("-" * 80)


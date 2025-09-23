#!/usr/bin/env python
# coding: utf-8

# In[3]:


get_ipython().system('pip install -U google-genai')
get_ipython().system('pip install -U langgraph')
get_ipython().system('pip install -U pydantic validators')
get_ipython().system('pip install -U typing-extensions')


# In[4]:


get_ipython().system('pip install -U google-genai')
get_ipython().system('pip install -U langgraph')


# In[9]:


import os
os.environ["GEMINI_API_KEY"] = "GEMINI_API_KEY"  


# In[11]:


from pydantic import BaseModel, Field, field_validator
from typing import Optional

class ResearchBriefModel(BaseModel):
    topic: Optional[str] = Field(None, description="The research topic")
    objective: Optional[str] = Field(None, description="Objective of the research")
    audience: Optional[str] = Field(None, description="Target audience")
    timeframe: Optional[str] = Field(None, description="Time horizon")
    depth: Optional[str] = Field(None, description="Depth required (summary, detailed, etc.)")
    deliverable: Optional[str] = Field(None, description="Format: brief, slides, report")
    constraints: Optional[str] = Field(None, description="Special constraints, if any")
    notes: Optional[str] = Field(None, description="Extra notes")

    @field_validator("depth", mode="before")
    def normalize_depth(cls, v):
        if isinstance(v, str):
            return v.lower().strip()
        return v


# In[12]:


import re
from typing import Dict, Tuple, List, Set
from pydantic import ValidationError

REQUIRED_FIELDS = {"topic","objective","audience","depth","deliverable"}  

MISSING_TO_QUESTION = {
    "topic": "What's the exact research topic? (one short sentence; include domain and focus — e.g., 'impact of AI on diabetic retinopathy diagnosis in adults')",
    "objective": "What's the objective? (choose one: summary, literature review, method comparison, recommendations, roadmap, data analysis, product spec)",
    "audience": "Who is the primary audience? (e.g., clinicians, executives, policymakers, students — be specific)",
    "timeframe": "Any timeframe or date range the research should focus on? (e.g., 2015-2025, last 10 years, ongoing)",
    "depth": "What depth do you want? (reply with one: summary, detailed, deep)",
    "deliverable": "What is the deliverable? (e.g., 2-page brief, slide deck, reproducible notebook, code + report)",
    "constraints": "Any constraints I should know? (data access, budget, model families to avoid, non-English sources, ethical constraints, file formats)",
    "data_sources": "Any required / preferred data sources or repositories to include (e.g., PubMed, IEEE, Google Scholar, web, internal DB)?",
    "evaluation_metrics": "How should outputs be evaluated? (accuracy, precision/recall, interpretability, human-in-loop scoring)",
    "deadline": "Is there a deadline? (date or relative e.g., 'in 2 weeks')",
}

def parse_fields_from_text(text: str) -> Dict[str,str]:
    """
    Lightweight heuristics to fill fields when user gives structured pieces.
    This is intentionally conservative: it only extracts very clear patterns.
    """
    out = {}
    if re.search(r'\b(summary|detailed|deep)\b', text, flags=re.I):
        out["depth"] = re.search(r'\b(summary|detailed|deep)\b', text, flags=re.I).group(1).lower()
    tf = re.search(r'((?:last|past)\s+\d+\s+years)|(\b\d{4}(?:\s*-\s*\d{4})\b)', text, flags=re.I)
    if tf:
        out["timeframe"] = tf.group(0)
    if re.search(r'\b(slide|slides|deck|notebook|brief|report|paper)\b', text, flags=re.I):
        if "slide" in text.lower() or "deck" in text.lower():
            out["deliverable"] = "slide deck"
        elif "notebook" in text.lower():
            out["deliverable"] = "notebook"
        elif "brief" in text.lower():
            out["deliverable"] = "brief"
        else:
            out["deliverable"] = "report"
    return out

def determine_missing_and_questions(conversation_fields: Dict[str,str]) -> Dict:
    """
    conversation_fields: dict of any pre-extracted fields (from parse or previous messages)
    Returns deterministic structured decision:
      {
        "clarify": bool,
        "missing_fields": [...],
        "questions": [...],
        "can_proceed": bool
      }
    """
    present = set(k for k,v in conversation_fields.items() if v is not None and str(v).strip()!="")
    missing = list(REQUIRED_FIELDS - present)
    optional_missing = []
    if conversation_fields.get("deliverable","").lower() == "notebook":
        if not conversation_fields.get("data_sources"):
            optional_missing.append("data_sources")
    if "compare" in conversation_fields.get("objective","").lower() or "evaluate" in conversation_fields.get("objective","").lower():
        if not conversation_fields.get("evaluation_metrics"):
            optional_missing.append("evaluation_metrics")
    questions = []
    for f in missing + optional_missing:
        if f in MISSING_TO_QUESTION:
            questions.append({"field": f, "question": MISSING_TO_QUESTION[f]})
    clarify = len(questions) > 0
    can_proceed = not clarify
    return {"clarify": clarify, "missing_fields": missing + optional_missing, "questions": questions, "can_proceed": can_proceed}


# In[13]:


from datetime import datetime
from typing import Any, Dict

def create_structured_brief(fields: Dict[str,Any], conversation_history: List[Dict[str,str]]=None) -> Dict:
    """
    fields: dict that must satisfy ResearchBriefModel
    conversation_history: optional list of user/assistant messages (keeps provenance)
    Returns: structured dict + pretty markdown
    """
    try:
        brief = ResearchBriefModel(**fields)
    except ValidationError as e:
        raise e

    md_lines = [
        f"# Research Brief — {brief.topic}",
        f"**Generated:** {datetime.utcnow().isoformat()}Z",
        f"**Objective:** {brief.objective}",
        f"**Audience:** {brief.audience}",
        f"**Depth:** {brief.depth}",
        f"**Deliverable:** {brief.deliverable}",
    ]
    if brief.timeframe:
        md_lines.append(f"**Timeframe:** {brief.timeframe}")
    if brief.constraints:
        md_lines.append(f"**Constraints:** {brief.constraints}")
    if brief.data_sources:
        md_lines.append(f"**Preferred Data Sources:** {', '.join(brief.data_sources)}")
    if brief.evaluation_metrics:
        md_lines.append(f"**Evaluation metrics:** {brief.evaluation_metrics}")
    if brief.deadline:
        md_lines.append(f"**Deadline:** {brief.deadline}")

    md_lines.append("\n## Scope & tasks")
    md_lines.append("- Scoping: clarify definitions and inclusion/exclusion criteria.")
    md_lines.append("- Search: targeted literature and grey literature lookup.")
    md_lines.append("- Synthesis: extract key findings, methods, and gaps.")
    md_lines.append("- Deliverable production: produce the requested deliverable (notebook/brief/slide deck).")

    return {"structured": brief.dict(), "markdown": "\n".join(md_lines)}


# In[14]:


from google import genai
import os

def genai_polish_brief(markdown_text: str, model: str = "gemini-2.5-flash") -> str:
    """
    Returns polished text from Gemini (requires GEMINI_API_KEY env var set).
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    resp = client.models.generate_content(model=model, contents=markdown_text)
    return resp.text


# In[15]:


from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langchain_core.messages import HumanMessage, AIMessage

class State(TypedDict):
    messages: list
    extracted_fields: dict
    clarify_needed: bool
    questions: list
    brief: dict

def extract_fields_node(state: State):
    user_msg = state["messages"][-1]["content"] if state["messages"] else ""
    heuristics = parse_fields_from_text(user_msg)
    fields = state.get("extracted_fields", {})
    fields.update({k:v for k,v in heuristics.items() if v})
    return {"extracted_fields": fields}

def clarify_decision_node(state: State):
    decision = determine_missing_and_questions(state.get("extracted_fields", {}))
    return {"clarify_needed": decision["clarify"], "questions": decision["questions"]}

def generate_brief_node(state: State):
    if state.get("clarify_needed"):
        return {}  # no-op here
    fields = state.get("extracted_fields", {})
    brief_obj = create_structured_brief(fields, conversation_history=state.get("messages", []))
    return {"brief": brief_obj}

builder = StateGraph(State)
builder.add_node(extract_fields_node).add_node(clarify_decision_node).add_node(generate_brief_node)
builder.add_edge(START, "extract_fields_node")
builder.add_edge("extract_fields_node", "clarify_decision_node")
builder.add_edge("clarify_decision_node", "generate_brief_node")
builder.set_entry_point("extract_fields_node")
graph = builder.compile()

input_state = {
    "messages": [{"role":"user","content":"I need a summary: impact of AI on tuberculosis diagnosis in India. Audience: public health officers. Deliverable: brief. Depth: summary."}],
    "extracted_fields": {},
    "clarify_needed": False,
    "questions": [],
    "brief": {}
}
result = graph.invoke(input_state)
print(result["clarify_needed"], result.get("questions"), "brief keys:", list(result.get("brief",{}).keys()))


# In[24]:


def create_structured_brief(fields: dict, conversation_history: list = None) -> dict:
    brief = ResearchBriefModel(**fields)

    md_lines = []
    if brief.topic:
        md_lines.append(f"**Topic:** {brief.topic}")
    if brief.objective:
        md_lines.append(f"**Objective:** {brief.objective}")
    if brief.audience:
        md_lines.append(f"**Audience:** {brief.audience}")
    if brief.timeframe:
        md_lines.append(f"**Timeframe:** {brief.timeframe}")
    if brief.depth:
        md_lines.append(f"**Depth:** {brief.depth}")
    if brief.deliverable:
        md_lines.append(f"**Deliverable:** {brief.deliverable}")
    if brief.constraints:
        md_lines.append(f"**Constraints:** {brief.constraints}")
    if brief.notes:
        md_lines.append(f"**Notes:** {brief.notes}")

    return {
        "markdown": "\n".join(md_lines),
        "structured": brief.model_dump()

    }


# In[25]:


input_state = {
    "messages": [{"role":"user","content":"Research on the impact of AI on tuberculosis diagnosis in India. Objective: recommendations. Audience: public health officers. Deliverable: brief. Depth: summary."}],
    "extracted_fields": {},
    "missing_fields": [],
    "questions": [],
    "brief": {}
}

result = graph.invoke(input_state)
print(result)


# In[26]:


get_ipython().system('pip install --upgrade google-genai')


# In[27]:


import os
from google import genai
os.environ["GENAI_API_KEY"] = "GENAI_API_KEY"

client = genai.Client()


# In[28]:


def generate_natural_questions(missing_fields, user_message):
    """
    missing_fields: list of dicts with 'field' and 'question'
    user_message: original user input
    """
    if not missing_fields:
        return []

    prompt = f"""
    The user said: "{user_message}"
    The following fields are missing: {', '.join([f['field'] for f in missing_fields])}.
    Write concise, polite, human-friendly questions asking the user for this information.
    Only ask about the missing fields.
    Return as a list of strings.
    """

    response = client.generate_text(model="gemini-1.5-t", prompt=prompt, temperature=0.2)
    return response.text.split("\n")


# In[29]:


def clarify_decision_node(state):
    decision = determine_missing_and_questions(state.get("extracted_fields", {}))
    if decision["clarify"]:
        natural_questions = generate_natural_questions(decision["questions"], state["messages"][-1]["content"])
        decision["questions"] = natural_questions
    return {
        "clarify_needed": decision["clarify"],
        "questions": decision["questions"]
    }


# In[30]:


input_state = {
    "messages": [{"role":"user","content":"I want research on AI in healthcare."}],
    "extracted_fields": {},
    "missing_fields": [],
    "questions": [],
    "brief": {}
}

result = graph.invoke(input_state)
print("Clarify Needed:", result["clarify_needed"])
print("Generated Questions:", result["questions"])


# In[35]:


def parse_fields_from_text(text: str) -> dict:
    fields = {}
    lowered = text.lower()

    if "research" in lowered or "impact" in lowered or "ai" in lowered:
        fields["topic"] = text.split(".")[0].strip()

    for obj in ["summary", "literature review", "method comparison", "recommendations", "roadmap", "data analysis", "product spec"]:
        if obj in lowered:
            fields["objective"] = obj
            break

    if "clinicians" in lowered:
        fields["audience"] = "clinicians"
    elif "officer" in lowered or "public health" in lowered:
        fields["audience"] = "public health officers"

    if "brief" in lowered:
        fields["deliverable"] = "brief"

    if "summary" in lowered:
        fields["depth"] = "summary"

    return fields


# In[36]:


user_answer = "Objective: recommendations; Depth: summary; Audience: clinicians; Deliverable: brief"
new_fields = parse_fields_from_text(user_answer)
input_state["extracted_fields"].update(new_fields)
input_state["messages"].append({"role":"user","content": user_answer})


# In[37]:


result = graph.invoke(input_state)
print("Clarify Needed:", result.get("clarify_needed"))
if result.get("brief"):
    print("Structured Brief Markdown:\n", result["brief"]["markdown"])
else:
    print("Brief not generated: some fields may still be missing")


# In[38]:


def get_user_input():
    fields = {}
    fields["topic"] = input("Enter the research topic: ")
    fields["objective"] = input("Enter the objective (e.g., summary, recommendations): ")
    fields["audience"] = input("Enter the audience (e.g., doctors, policymakers): ")
    fields["timeframe"] = input("Enter the timeframe (optional): ")
    fields["depth"] = input("Enter the depth (summary / detailed report): ")
    fields["deliverable"] = input("Enter the deliverable (brief, slides, etc.): ")
    fields["constraints"] = input("Enter constraints (if any): ")
    fields["notes"] = input("Enter any notes (optional): ")
    return fields


user_fields = get_user_input()
structured_brief = create_structured_brief(user_fields)
print("\nGenerated Research Brief:\n")
print(structured_brief["markdown"])






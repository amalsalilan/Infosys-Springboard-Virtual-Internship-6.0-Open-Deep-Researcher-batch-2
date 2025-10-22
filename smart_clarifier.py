# smart_clarifier.py
from typing import List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Configurable model names for each phase
SMART_CLARIFIER_MODEL = "gemini-2.5-flash"  # fast/cheap model


def _build_prompt(query: str, context: str) -> str:
    return f"""
You are a Clarifier Agent. The user's raw query is:
\"\"\"{query}\"\"\"

The current conversation/context is:
\"\"\"{context}\"\"\"

Task:
- If the query is already specific enough to start research, respond with the exact phrase:
  NO_FURTHER_CLARIFICATION
- Otherwise, produce ONE short, direct clarifying question (<= 20 words) that will make the query actionable.
No additional commentary. Only output the single line answer.
"""

def generate_clarifying_question(messages: List[BaseMessage]) -> Optional[str]:
    """
    Return:
      - None if no clarification needed
      - clarifying question string otherwise
    """
    # Extract latest user message and reduced context
    latest_user = None
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            latest_user = m.content
            break

    context = "\n".join(m.content for m in messages if hasattr(m, "content") and m.content != latest_user)
    prompt_text = _build_prompt(latest_user or "", context)

    llm = ChatGoogleGenerativeAI(model=SMART_CLARIFIER_MODEL, temperature=0.0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful clarity-check assistant."),
        ("user", prompt_text),
    ])
    parser = StrOutputParser()
    chain = prompt | llm | parser
    result = chain.invoke({})

    # Normalize and interpret
    out = result.strip()
    if out.upper().startswith("NO_FURTHER_CLARIFICATION") or out.upper().startswith("NO FURTHER CLARIFICATION"):
        return None
    return out

# reflection_agent.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

REFLECTION_MODEL = "gemini-2.5-pro"

def reflective_analysis(research_ai_message: AIMessage) -> AIMessage:
    """
    Produces a structured reflective analysis from the research message content.
    """
    llm = ChatGoogleGenerativeAI(model=REFLECTION_MODEL, temperature=0.5)
    prompt = f"""
You are a Research Reflection Agent. Below is the research summary that was produced:

\"\"\"{research_ai_message.content}\"\"\"

Produce a structured reflection that includes:
1. Reliability & relevance of the data.
2. Missing perspectives or biases (cost,sustainability,reviews,comparisons).
3. 2-3 improvements to make findings more deeper and more balanced.
4. A short executive summary and key findings.

Make it sound like and AI research report with reflection and reasoning.
"""
    result = llm.invoke([HumanMessage(content=prompt)])
    return result

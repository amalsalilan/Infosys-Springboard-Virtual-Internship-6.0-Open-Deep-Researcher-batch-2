# query_clarifier.py

from typing import List
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def analyze_user_intent(message_history: List[BaseMessage]) -> str:
    """
    Analyzes the latest user message for ambiguity based on conversational context.

    Returns:
        An empty string if the intent is clear, or a clarifying question if it's not.
    """
    # Initialize the Gemini model for the analysis task
    analyzer_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

    # This prompt guides the AI to act as a clarity expert
    system_prompt = """
    You are a helpful assistant who analyzes user queries for clarity.
    Review the full conversation history provided. Based on this context, determine if the LATEST user message is specific enough to be answered.

    - If the user's latest message is clear, respond with only the word: CLEAR
    - If the message is ambiguous or needs more detail, formulate a concise question to ask the user.

    Example History:
    [Human: "Find cafes in Chennai.", AI: "What kind of cafes are you looking for?", Human: "Ones with good wifi."]
    Your Response: CLEAR

    Example History:
    [Human: "Tell me about it."]
    Your Response: "Could you please specify what 'it' you are referring to?"
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        *message_history,
    ])

    # Create and invoke the analysis chain
    clarity_chain = prompt | analyzer_llm | StrOutputParser()
    analysis_result = clarity_chain.invoke({})

    # Return the clarifying question only if the intent is not clear
    if "CLEAR" in analysis_result.upper():
        return ""
    else:
        return analysis_result
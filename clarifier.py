from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict

class Clarifier:
    """Uses an LLM to decide whether clarification is needed and to generate a clarifying question."""

    def __init__(self, openai_api_key: str, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model_name=model_name, openai_api_key=openai_api_key, temperature=0.0)

    def need_clarification(self, user_message: str, context: str = None) -> Dict[str, str]:
        prompt = [
            SystemMessage(content=(
                "You are an assistant that decides whether a user's query is ambiguous and, if so, write a single concise clarifying question."
            )),
            HumanMessage(content=(
                f"Context: {context}\nUser: {user_message}\n\n" 
                "Answer with a JSON object with two keys:\n- need: true or false\n- question: if need is true, write the concise clarifying question, otherwise an empty string."
            ))
        ]

        resp = self.llm.generate_messages(prompt)
        text = resp[0].content if isinstance(resp, list) else resp.content

        import json, re
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                obj = json.loads(m.group(0))
                return {"need": bool(obj.get("need")), "question": obj.get("question", "").strip()}
            except Exception:
                pass

        lower = user_message.strip().lower()
        pronouns = ["it", "this", "that", "they", "them"]
        if len(lower.split()) <= 4 or any(p in lower.split() for p in pronouns):
            return {"need": True, "question": "Could you clarify what you mean by that?"}

        return {"need": False, "question": ""}

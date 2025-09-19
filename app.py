import os
from dotenv import load_dotenv
from langgraph_pipeline import build_graph

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Please set OPENAI_API_KEY in your environment or .env file.")
    exit(1)

print("Starting Clarify_with_user (CLI). Type 'exit' to quit.")

graph, memory = build_graph(openai_api_key=OPENAI_API_KEY)

while True:
    user = input("You: ")
    if user.strip().lower() in {"exit", "quit", "q"}:
        print("Goodbye!")
        break

    state = {"messages": memory.get_messages(), "last_user": user}
    compiled = graph.compile()
    result_state = compiled.run(state)

    if result_state.get("clarify_needed"):
        q = result_state.get("clarify_question", "Could you clarify?")
        print(f"Assistant: {q}")
        clar = input("Clarification: ")
        memory.add_user(user)
        memory.add_user(clar)

        state = {"messages": memory.get_messages(), "last_user": user}
        compiled = graph.compile()
        result_state = compiled.run(state)
        assistant_reply = result_state.get("assistant_reply")
        print(f"Assistant: {assistant_reply}")
        memory.add_assistant(assistant_reply)
    else:
        assistant_reply = result_state.get("assistant_reply")
        print(f"Assistant: {assistant_reply}")
        memory.add_user(user)
        memory.add_assistant(assistant_reply)

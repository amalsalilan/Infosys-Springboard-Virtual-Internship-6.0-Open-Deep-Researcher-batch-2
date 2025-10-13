from langchain.schema import AIMessage

def clarify_with_user(state):
    user_msg = state["messages"][-1].content
    if "?" not in user_msg and len(user_msg.split()) < 3:
        state["messages"].append(AIMessage(content="Can you please clarify your request?"))
        state["clarification_needed"] = True
        state["next_step"] = "clarify"
    else:
        state["messages"].append(AIMessage(content="Got it! Moving to research..."))
        state["clarification_needed"] = False
        state["next_step"] = "research_brief"
    return state
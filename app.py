# main_app.py

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from memory import ConversationHistory
from langgraph_pipeline import create_chatbot_workflow

# Load API key from .env file
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    raise EnvironmentError("🚨 GOOGLE_API_KEY not found in .env file.")

def run_chat_session():
    """
    Initializes and runs the main command-line interface for the chatbot.
    """
    print("🤖 Gemini Clarification Bot is online. Type 'exit' to end the session.")
    
    # Initialize components
    memory = ConversationHistory()
    chatbot_app = create_chatbot_workflow()

    while True:
        try:
            user_text = input("\nYou: ")
            if user_text.lower() in ["exit", "quit"]:
                print("👋 Bot session terminated. Goodbye!")
                break

            # Append the new user message to the current history for this turn
            current_turn_messages = memory.get_history() + [HumanMessage(content=user_text)]
            
            # Prepare the input state for the graph
            graph_input = {
                "messages": current_turn_messages,
            }

            # Execute the graph
            result_state = chatbot_app.invoke(graph_input)

            # Process the graph's final state
            if result_state.get("follow_up_question"):
                # If the graph ended by producing a clarifying question
                question_to_ask = result_state["follow_up_question"]
                print(f"AI: {question_to_ask}")
                
                # Log the turn to memory: user's vague message + bot's question
                memory.log_message(HumanMessage(content=user_text))
                memory.log_message(AIMessage(content=question_to_ask))
            else:
                # If the graph produced a direct answer
                final_ai_message = result_state["messages"][-1]
                print(f"AI: {final_ai_message.content}")
                
                # Log the successful turn to memory
                memory.log_message(HumanMessage(content=user_text))
                memory.log_message(final_ai_message)

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Bot session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n🔥 An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_chat_session()
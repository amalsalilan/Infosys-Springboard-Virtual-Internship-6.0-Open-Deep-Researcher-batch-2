OpenDeepResearcher — Clarify_with_user (LangGraph CLI)
Minimal CLI chatbot using LangGraph that stores session memory and asks clarifying questions when needed.

Setup
Create a new repo and add the files from this project.
Create a Python virtual environment and install dependencies:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Add your OpenAI API key to .env in the repo root:
OPENAI_API_KEY=sk-...
Run the CLI:
python app.py
Type exit, quit or q to stop
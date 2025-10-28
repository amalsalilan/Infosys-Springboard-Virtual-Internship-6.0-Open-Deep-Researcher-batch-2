# Quick Setup

Follow these steps to get the researcher running with the default configuration.

1. Clone the repository:
   ```bash
   git clone https://github.com/amalsalilan/Infosys-Springboard-Virtual-Internship-6.0-Open-Deep-Researcher-batch-2.git
   ```
2. Change into the project directory:
   ```bash
   cd Infosys-Springboard-Virtual-Internship-6.0-Open-Deep-Researcher-batch-2
   ```
3. Install Python dependencies with `uv` (installation guide: https://docs.astral.sh/uv/getting-started/installation/):
   ```bash
   uv sync
   ```
4. Copy the environment variable template (WSL command shown):
   ```bash
   cp .env.example .env
   ```
5. Open `.env` and fill in the required credentials:
   - `TAVILY_API_KEY`
   - `GOOGLE_API_KEY` (Gemini)
   - `LANGSMITH_API_KEY`
6. Start the LangGraph development server:
   ```bash
   uv run langgraph dev --allow-blocking
   ```

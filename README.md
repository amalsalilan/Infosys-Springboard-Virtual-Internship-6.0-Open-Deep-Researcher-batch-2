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

## Docker Setup (Simple)

1. Install Docker Desktop: https://docs.docker.com/desktop/install/
2. Copy the sample env file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API keys.
4. Build and start the containers:
   ```bash
   docker compose up --build
   ```
5. Wait for the logs to settle, then open `http://127.0.0.1:2024` in your browser (it redirects to the API docs).
6. Open LangGraph Studio at `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`.
7. When you are done, stop everything with:
   ```bash
   docker compose down
   ```

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
4. Create the persistent checkpoint volume (one-time):
   ```bash
   docker volume create langgraph-checkpoints
   ```
   - This must exist before `docker compose up` because the compose file declares an external volume.
   - Verify it exists: `docker volume ls | grep langgraph-checkpoints`
   - Inspect (optional): `docker volume inspect langgraph-checkpoints`
   - If you ever need to recreate it: stop containers, then `docker volume rm langgraph-checkpoints` and run the create command again.
5. Build and start the containers:
   ```bash
   docker compose up --build
   ```
6. Wait for the logs to settle, then open:
   - Backend API docs: `http://127.0.0.1:2024`
   - Agent Chat UI: `http://127.0.0.1:3001`
7. Launch LangGraph Studio at `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`.
8. When you are done, stop everything with:
   ```bash
   docker compose down
   ```

# 🧱 Deep Research From Scratch 

Deep research has broken out as one of the most popular agent applications. [OpenAI](https://openai.com/index/introducing-deep-research/), [Anthropic](https://www.anthropic.com/engineering/built-multi-agent-research-system), [Perplexity](https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research), and [Google](https://gemini.google/overview/deep-research/?hl=en) all have deep research products that produce comprehensive reports using [various sources](https://www.anthropic.com/news/research) of context. There are also many [open](https://huggingface.co/blog/open-deep-research) [source](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart) implementations. We built an [open deep researcher](https://github.com/langchain-ai/open_deep_research) that is simple and configurable, allowing users to bring their own models, search tools, and MCP servers. In this repo, we'll build a deep researcher from scratch! Here is a map of the major pieces that we will build:

![overview](https://github.com/user-attachments/assets/b71727bd-0094-40c4-af5e-87cdb02123b4)

## 🚀 Quickstart

### Step 1: Prerequisites

#### Python 3.11+
Ensure you're using Python 3.11 or later (required for optimal LangGraph compatibility):
```bash
python3 --version
```

If you need to install Python 3.11+:
- **macOS**: `brew install python@3.11`
- **Ubuntu/Debian**: `sudo apt install python3.11`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

#### UV Package Manager
Install [uv](https://docs.astral.sh/uv/) for fast, reliable dependency management:

**macOS/Linux/WSL:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Update PATH:**
```bash
# macOS/Linux/WSL
export PATH="$HOME/.local/bin:$PATH"

# Or add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

Verify installation:
```bash
uv --version
```

#### Node.js and NPX (Required for MCP in Notebook 3)
MCP filesystem server requires Node.js and npx:

**macOS:**
```bash
brew install node
```

**Ubuntu/Debian/WSL:**
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Windows:**
Download from [nodejs.org](https://nodejs.org/)

**Verify installation:**
```bash
node --version
npx --version
```

> **⚠️ WSL Users (Windows Subsystem for Linux):** The project includes automatic WSL detection and configuration for MCP servers. Node.js will be invoked via Windows when needed. Ensure both WSL Node.js AND Windows Node.js are installed.

---

### Step 2: Clone and Setup

1. **Clone the repository:**
```bash
git clone https://github.com/langchain-ai/deep_research_from_scratch
cd deep_research_from_scratch
```

2. **Install dependencies with uv:**
```bash
uv sync
```

This command:
- Creates a virtual environment at `.venv/`
- Installs all required packages from `pyproject.toml`
- Generates/updates `uv.lock` for reproducible builds

3. **Verify installation:**
```bash
# Check installed packages
uv pip list

# Should see langchain, langgraph, tavily-python, etc.
```

---

### Step 3: Configure API Keys

1. **Create `.env` file:**
```bash
touch .env
```

2. **Add your API keys** (open `.env` in your editor):

```env
# ========================================
# REQUIRED: Search API (for notebooks 2, 4, 5)
# ========================================
TAVILY_API_KEY=your_tavily_api_key_here
# Get free key at: https://tavily.com

# ========================================
# REQUIRED: LLM Provider (choose at least one)
# ========================================
# Google Gemini (Primary - used by default in notebooks)
GOOGLE_API_KEY=your_google_api_key_here
# Get key at: https://aistudio.google.com/apikey

# OpenAI (Alternative)
OPENAI_API_KEY=your_openai_api_key_here
# Get key at: https://platform.openai.com/api-keys

# Anthropic (Alternative)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# Get key at: https://console.anthropic.com/

# ========================================
# OPTIONAL: Tracing and Evaluation
# ========================================
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=deep_research_from_scratch
# Get key at: https://smith.langchain.com/
```

3. **Verify environment variables load:**
```bash
# Using uv to run Python
uv run python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ Keys loaded' if os.getenv('TAVILY_API_KEY') else '✗ Check .env file')"
```

---

### Step 4: Run Jupyter Notebooks

**Option 1: Direct launch with uv (Recommended)**
```bash
uv run jupyter notebook
```

**Option 2: Activate virtual environment first**
```bash
# macOS/Linux/WSL
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Then launch Jupyter
jupyter notebook
```

**Your browser should open with the notebook interface.** Navigate to `notebooks/` to start!

---

### Step 5: Notebook Execution Order

**📚 Recommended Learning Path:**

1. **[1_scoping.ipynb](notebooks/1_scoping.ipynb)** - User clarification and research brief generation
2. **[2_research_agent.ipynb](notebooks/2_research_agent.ipynb)** - Research agent with Tavily search
3. **[3_research_agent_mcp.ipynb](notebooks/3_research_agent_mcp.ipynb)** - Research agent with MCP filesystem server
4. **[4_research_supervisor.ipynb](notebooks/4_research_supervisor.ipynb)** - Multi-agent research coordinator
5. **[5_full_agent.ipynb](notebooks/5_full_agent.ipynb)** - Complete end-to-end research system

**⚙️ Important Notes:**
- Notebooks 2, 4, 5 require `TAVILY_API_KEY`
- All notebooks require at least one LLM API key (Google/OpenAI/Anthropic)
- Notebook 3 requires Node.js for MCP server (see prerequisites)

---

### 🐧 Platform-Specific Notes

#### WSL (Windows Subsystem for Linux) Users

The project **automatically detects WSL** and configures MCP servers correctly. The implementation:

1. Detects WSL environment using `platform.system()` and `platform.release()`
2. Converts WSL paths (`/mnt/c/...`) to Windows paths (`C:\...`) using `wslpath`
3. Invokes Windows Node.js via `cmd.exe` for MCP server compatibility

**No manual configuration needed!** Just ensure:
- ✅ Node.js is installed on Windows (`node.exe` in PATH)
- ✅ WSL has access to Windows binaries (`cmd.exe` available)

**Troubleshooting WSL MCP issues:**
```bash
# Verify Windows Node.js is accessible from WSL
cmd.exe /c "node --version"

# Verify wslpath conversion works
wslpath -w /mnt/c/Users/$USER
```

#### macOS Users
- Use Homebrew for Node.js: `brew install node`
- UV install path: `~/.local/bin/uv`

#### Windows (Native) Users
- Use installers from official websites
- Activate venv: `.venv\Scripts\activate` (Command Prompt) or `.venv\Scripts\Activate.ps1` (PowerShell)

---

### 🔄 Updating Dependencies

**Update all packages to latest compatible versions:**
```bash
uv sync --upgrade
```

**Update specific packages:**
```bash
uv pip install --upgrade langchain langgraph
```

**Check for outdated packages:**
```bash
uv pip list --outdated
```

## Background 

Research is an open‑ended task; the best strategy to answer a user request can’t be easily known in advance. Requests can require different research strategies and varying levels of search depth. Consider this request. 

[Agents](https://langchain-ai.github.io/langgraph/tutorials/workflows/#agent) are well suited to research because they can flexibly apply different strategies, using intermediate results to guide their exploration. Open deep research uses an agent to conduct research as part of a three step process:

1. **Scope** – clarify research scope
2. **Research** – perform research
3. **Write** – produce the final report

## 📝 Organization 

This repo contains 5 tutorial notebooks that build a deep research system from scratch:

### 📚 Tutorial Notebooks

#### 1. User Clarification and Brief Generation (`notebooks/1_scoping.ipynb`)
**Purpose**: Clarify research scope and transform user input into structured research briefs

**Key Concepts**:
- **User Clarification**: Determines if additional context is needed from the user using structured output
- **Brief Generation**: Transforms conversations into detailed research questions
- **LangGraph Commands**: Using Command system for flow control and state updates
- **Structured Output**: Pydantic schemas for reliable decision making

**Implementation Highlights**:
- Two-step workflow: clarification → brief generation
- Structured output models (`ClarifyWithUser`, `ResearchQuestion`) to prevent hallucination
- Conditional routing based on clarification needs
- Date-aware prompts for context-sensitive research

**What You'll Learn**: State management, structured output patterns, conditional routing

---

#### 2. Research Agent with Custom Tools (`notebooks/2_research_agent.ipynb`)
**Purpose**: Build an iterative research agent using external search tools

**Key Concepts**:
- **Agent Architecture**: LLM decision node + tool execution node pattern
- **Sequential Tool Execution**: Reliable synchronous tool execution
- **Search Integration**: Tavily search with content summarization
- **Tool Execution**: ReAct-style agent loop with tool calling

**Implementation Highlights**:
- Synchronous tool execution for reliability and simplicity
- Content summarization to compress search results
- Iterative research loop with conditional routing
- Rich prompt engineering for comprehensive research

**What You'll Learn**: Agent patterns, tool integration, search optimization, research workflow design

---

#### 3. Research Agent with MCP (`notebooks/3_research_agent_mcp.ipynb`)
**Purpose**: Integrate Model Context Protocol (MCP) servers as research tools

**Key Concepts**:
- **Model Context Protocol**: Standardized protocol for AI tool access
- **MCP Architecture**: Client-server communication via stdio/HTTP
- **LangChain MCP Adapters**: Seamless integration of MCP servers as LangChain tools
- **Local vs Remote MCP**: Understanding transport mechanisms

**Implementation Highlights**:
- `MultiServerMCPClient` for managing MCP servers
- Configuration-driven server setup (filesystem example)
- Rich formatting for tool output display
- Async tool execution required by MCP protocol (no nested event loops needed)

**What You'll Learn**: MCP integration, client-server architecture, protocol-based tool access

---

#### 4. Research Supervisor (`notebooks/4_research_supervisor.ipynb`)
**Purpose**: Multi-agent coordination for complex research tasks

**Key Concepts**:
- **Supervisor Pattern**: Coordination agent + worker agents
- **Parallel Research**: Concurrent research agents for independent topics using parallel tool calls
- **Research Delegation**: Structured tools for task assignment
- **Context Isolation**: Separate context windows for different research topics

**Implementation Highlights**:
- Two-node supervisor pattern (`supervisor` + `supervisor_tools`)
- Parallel research execution using `asyncio.gather()` for true concurrency
- Structured tools (`ConductResearch`, `ResearchComplete`) for delegation
- Enhanced prompts with parallel research instructions
- Comprehensive documentation of research aggregation patterns

**What You'll Learn**: Multi-agent patterns, parallel processing, research coordination, async orchestration

---

#### 5. Full Multi-Agent Research System (`notebooks/5_full_agent.ipynb`)
**Purpose**: Complete end-to-end research system integrating all components

**Key Concepts**:
- **Three-Phase Architecture**: Scope → Research → Write
- **System Integration**: Combining scoping, multi-agent research, and report generation
- **State Management**: Complex state flow across subgraphs
- **End-to-End Workflow**: From user input to final research report

**Implementation Highlights**:
- Complete workflow integration with proper state transitions
- Supervisor and researcher subgraphs with output schemas
- Final report generation with research synthesis
- Thread-based conversation management for clarification

**What You'll Learn**: System architecture, subgraph composition, end-to-end workflows

---

### 🎯 Key Learning Outcomes

- **Structured Output**: Using Pydantic schemas for reliable AI decision making
- **Async Orchestration**: Strategic use of async patterns for parallel coordination vs synchronous simplicity
- **Agent Patterns**: ReAct loops, supervisor patterns, multi-agent coordination
- **Search Integration**: External APIs, MCP servers, content processing
- **Workflow Design**: LangGraph patterns for complex multi-step processes
- **State Management**: Complex state flows across subgraphs and nodes
- **Protocol Integration**: MCP servers and tool ecosystems

Each notebook builds on the previous concepts, culminating in a production-ready deep research system that can handle complex, multi-faceted research queries with intelligent scoping and coordinated execution.

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. MCP Server "Connection Closed" Error (Notebook 3)

**Error:**
```
mcp.shared.exceptions.McpError: Connection closed
```

**Solution for WSL Users:**
The project automatically handles WSL path conversion. Ensure:
1. Windows Node.js is installed (not just WSL Node.js)
2. `cmd.exe` is accessible from WSL
3. Reload the notebook after updating (File → Reload from Disk)

**Verify:**
```bash
# Should show Windows Node.js version
cmd.exe /c "node --version"

# Should convert paths correctly
wslpath -w /mnt/c/Users/$USER
```

**Still not working?** Check that your notebook has been reloaded. The fix is in cells 4 and 6 of `3_research_agent_mcp.ipynb`.

---

#### 2. API Key Not Found Errors

**Error:**
```
ValidationError: TAVILY_API_KEY not found
```

**Solution:**
1. Verify `.env` file exists in project root
2. Check API keys are set correctly (no quotes, no spaces)
3. Reload environment:
   ```bash
   # Test key loading
   uv run python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('TAVILY_API_KEY'))"
   ```
4. Restart Jupyter kernel: Kernel → Restart Kernel

---

#### 3. Module Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'langchain'
```

**Solution:**
1. Ensure virtual environment is activated:
   ```bash
   which python  # Should show .venv/bin/python
   ```
2. Re-sync dependencies:
   ```bash
   uv sync
   ```
3. Restart Jupyter notebook server

---

#### 4. UV Not Found

**Error:**
```
command not found: uv
```

**Solution:**
1. Install uv (see Prerequisites above)
2. Update PATH:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
3. Verify: `uv --version`

---

#### 5. Jupyter Kernel Issues

**Problem:** Kernel dies or becomes unresponsive

**Solution:**
1. Restart kernel: Kernel → Restart Kernel
2. Clear outputs: Cell → All Output → Clear
3. Reinstall kernel:
   ```bash
   source .venv/bin/activate
   python -m ipykernel install --user --name=deep_research
   ```

---

#### 6. Rate Limiting / API Quota Errors

**Error:**
```
RateLimitError: You exceeded your current quota
```

**Solution:**
1. Check API usage at provider dashboard (OpenAI/Anthropic/Google)
2. Switch to alternative model in notebook:
   ```python
   # Change from:
   model = init_chat_model("gemini-2.5-pro", model_provider="google_genai")

   # To:
   model = init_chat_model("gpt-4o-mini", model_provider="openai")
   ```
3. Add delays between requests if needed

---

### Getting Help

1. **Check notebook outputs** - Error messages often contain the solution
2. **Review API key configuration** - Most issues are authentication-related
3. **Platform-specific docs** - See WSL/macOS/Windows sections above
4. **LangChain/LangGraph docs** - [https://python.langchain.com/docs/](https://python.langchain.com/docs/)
5. **Open an issue** - [GitHub Issues](https://github.com/langchain-ai/deep_research_from_scratch/issues)

---

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or for specific modules:
logging.getLogger("langchain").setLevel(logging.DEBUG)
logging.getLogger("langgraph").setLevel(logging.DEBUG)
``` 

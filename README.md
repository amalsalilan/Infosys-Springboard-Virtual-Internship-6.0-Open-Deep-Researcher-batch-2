# 🧱 Deep Research From Scratch 

Deep research has broken out as one of the most popular agent applications. [OpenAI](https://openai.com/index/introducing-deep-research/), [Anthropic](https://www.anthropic.com/engineering/built-multi-agent-research-system), [Perplexity](https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research), and [Google](https://gemini.google/overview/deep-research/?hl=en) all have deep research products that produce comprehensive reports using [various sources](https://www.anthropic.com/news/research) of context. There are also many [open](https://huggingface.co/blog/open-deep-research) [source](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart) implementations. We built an [open deep researcher](https://github.com/langchain-ai/open_deep_research) that is simple and configurable, allowing users to bring their own models, search tools, and MCP servers. In this repo, we'll build a deep researcher from scratch! Here is a map of the major pieces that we will build:

![overview](https://github.com/user-attachments/assets/b71727bd-0094-40c4-af5e-87cdb02123b4)

## 🚀 First-Time Setup Guide

Follow these steps to get the deep research system running on your machine.

---

### Step 1: Install Prerequisites

Before you begin, install these required tools:

#### 1.1 Python 3.11+

**Check if you have Python 3.11+:**
```bash
python3 --version
```

**If you need to install Python:**
- **macOS**: `brew install python@3.11`
- **Ubuntu/Debian**: `sudo apt install python3.11`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

#### 1.2 UV Package Manager

UV is a fast Python package manager that handles dependencies and virtual environments.

**Install UV:**

**macOS/Linux/WSL:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Add UV to PATH:**
```bash
# macOS/Linux/WSL - Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export PATH="$HOME/.local/bin:$PATH"
```

**Verify installation:**
```bash
uv --version
```

#### 1.3 Node.js (Required for Notebook 3 - MCP)

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

> **💡 WSL Users:** Install Node.js on BOTH Windows and WSL. The project auto-detects WSL and routes MCP servers through Windows Node.js.

---

### Step 2: Clone Repository and Install Dependencies

**2.1 Clone the repository:**
```bash
git clone https://github.com/langchain-ai/deep_research_from_scratch
cd deep_research_from_scratch
```

**2.2 Install all dependencies:**
```bash
uv sync
```

This creates a virtual environment at `.venv/` and installs all required packages.

**2.3 Verify installation:**
```bash
uv pip list
```

You should see packages like `langchain`, `langgraph`, `tavily-python`, etc.

---

### Step 3: Configure Environment Variables

**3.1 Create `.env` file in project root:**
```bash
touch .env
```

**3.2 Open `.env` in your text editor and add your API keys:**

```env
# ========================================
# REQUIRED: Search API
# ========================================
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxx
# Get free key at: https://tavily.com

# ========================================
# REQUIRED: LLM Provider (choose one or more)
# ========================================
# Google Gemini (Default)
GOOGLE_API_KEY=AIzaSy-xxxxxxxxxxxxxxxxxxxxx
# Get key at: https://aistudio.google.com/apikey

# OpenAI (Alternative)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
# Get key at: https://platform.openai.com/api-keys

# Anthropic (Alternative)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
# Get key at: https://console.anthropic.com/

# ========================================
# OPTIONAL: LangSmith Tracing
# ========================================
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxxxxxxx
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=deep_research_from_scratch
# Get key at: https://smith.langchain.com/
```

**3.3 Verify environment variables:**
```bash
uv run python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ Environment configured' if os.getenv('TAVILY_API_KEY') else '✗ Missing API keys')"
```

---

### Step 4: Choose Your Development Environment

You can work with the notebooks in two ways:

#### Option A: LangGraph Studio (Recommended for Visual Debugging)

LangGraph Studio provides a visual interface for debugging and monitoring agent workflows.

**4.1 Download LangGraph Studio:**
- **macOS**: [Download for Mac](https://langgraph-studio.vercel.app/download?os=mac)
- **Windows**: [Download for Windows](https://langgraph-studio.vercel.app/download?os=windows)
- **Linux**: [Download for Linux](https://langgraph-studio.vercel.app/download?os=linux)

**4.2 Install and launch LangGraph Studio**

**4.3 Open the project:**
1. Click "Open Folder" in LangGraph Studio
2. Navigate to your `deep_research_from_scratch` directory
3. Select the folder

**4.4 Configure environment in Studio:**
LangGraph Studio automatically loads your `.env` file. Verify keys are loaded in the Settings panel.

**4.5 Start exploring:**
- Navigate to `notebooks/` in the file explorer
- Open `1_scoping.ipynb` to begin
- Use the visual graph view to see agent execution in real-time

#### Option B: Jupyter Notebooks (Classic Approach)

**4.1 Launch Jupyter:**
```bash
uv run jupyter notebook
```

**4.2 Open notebooks:**
Your browser will open automatically. Navigate to `notebooks/` folder.

**4.3 Alternative - Activate venv first:**
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

---

### Step 5: Run the Notebooks

**📚 Recommended Order:**

| Order | Notebook | Description | Requirements |
|-------|----------|-------------|--------------|
| **1** | `1_scoping.ipynb` | User clarification & research brief generation | LLM API key |
| **2** | `2_research_agent.ipynb` | Research agent with Tavily search | Tavily + LLM API |
| **3** | `3_research_agent_mcp.ipynb` | Research agent with MCP filesystem | Node.js + LLM API |
| **4** | `4_research_supervisor.ipynb` | Multi-agent coordinator | Tavily + LLM API |
| **5** | `5_full_agent.ipynb` | Complete end-to-end system | Tavily + LLM API |

**🎯 Quick Start:**
1. Start with `1_scoping.ipynb` - it works with just an LLM API key
2. Progress sequentially - each builds on previous concepts
3. Use Shift+Enter to run cells
4. Read the markdown explanations between code cells

---

### Platform-Specific Tips

#### WSL (Windows Subsystem for Linux)
✅ **Auto-configured** - Project detects WSL and handles path conversion automatically
✅ Install Node.js on both Windows AND WSL
✅ Verify Windows Node.js access: `cmd.exe /c "node --version"`

#### macOS
✅ Use Homebrew for dependencies: `brew install python@3.11 node`
✅ UV install location: `~/.local/bin/uv`

#### Windows
✅ Use PowerShell for UV installation
✅ Activate venv: `.venv\Scripts\Activate.ps1` (PowerShell) or `.venv\Scripts\activate.bat` (CMD)

## 📚 What You'll Build

This repository contains 5 progressive tutorial notebooks that teach you to build a complete deep research system:

| Notebook | Topic | What You'll Learn |
|----------|-------|-------------------|
| **1_scoping.ipynb** | User Clarification & Brief Generation | Structured output, conditional routing, state management |
| **2_research_agent.ipynb** | Research Agent with Search Tools | Agent patterns, tool integration, Tavily search |
| **3_research_agent_mcp.ipynb** | Research Agent with MCP | Model Context Protocol, client-server architecture |
| **4_research_supervisor.ipynb** | Multi-Agent Coordination | Supervisor pattern, parallel processing, async orchestration |
| **5_full_agent.ipynb** | Complete End-to-End System | System integration, subgraph composition, workflows |

### Architecture Overview

The system implements a **3-phase research workflow**:

1. **Scope** → Clarify research scope and generate structured briefs
2. **Research** → Perform multi-agent parallel research
3. **Write** → Synthesize findings into comprehensive reports

Each notebook builds on previous concepts, progressing from basic agent patterns to a production-ready multi-agent research system.

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

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

This project is based on and references the [LangGraph Deep Research From Scratch](https://github.com/langchain-ai/deep_research_from_scratch) tutorial by LangChain AI. The original implementation provides a comprehensive guide to building deep research systems using LangGraph and multi-agent workflows.

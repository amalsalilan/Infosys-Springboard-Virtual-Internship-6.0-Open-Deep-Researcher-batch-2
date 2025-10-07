# 📓 How to Run These Notebooks

## ⚠️ IMPORTANT: Kernel Selection Required!

Before running any notebook cells, you **MUST** select the correct Python kernel. Otherwise, you'll get `ModuleNotFoundError`.

---

## 🎯 Quick Start (3 Steps)

### Step 1: Start Jupyter
```bash
# From project root directory
uv run jupyter notebook
```

### Step 2: Open a Notebook
Click on any `.ipynb` file (start with `1_scoping.ipynb`)

### Step 3: Select the Correct Kernel ⚡

**The kernel MUST be the project's `.venv`, NOT system Python!**

#### If Using VSCode:
1. Look at the **top-right corner** of the notebook
2. Click where it says "Select Kernel" or shows current kernel name
3. Select **"Python Environments"**
4. Choose **`.venv/bin/python`** or **`.venv (Python 3.11)`**

#### If Using Jupyter Notebook/Lab:
1. Click **"Kernel"** in the menu bar
2. Select **"Change Kernel"**
3. Choose a kernel that mentions **"venv"** or shows path to `.venv`

---

## ✅ How to Verify You Selected the Right Kernel

**Look at the kernel name displayed:**
- ✅ **CORRECT**: `.venv`, `Python 3.11 (venv)`, or path ending in `.venv/bin/python`
- ❌ **WRONG**: `Python 3`, `ipykernel`, or system paths like `/usr/bin/python3`

---

## 🔧 Troubleshooting

### Problem: `.venv` kernel is not in the list

**Solution:**
```bash
# Install the venv as a Jupyter kernel
source .venv/bin/activate
python -m ipykernel install --user --name=deep-research --display-name="Deep Research (venv)"
```

Then restart Jupyter and select "Deep Research (venv)" kernel.

### Problem: Still getting `ModuleNotFoundError: No module named 'utils'`

**Causes:**
1. ❌ You're using system Python kernel (not `.venv`)
2. ❌ You haven't run the first setup cell in the notebook
3. ❌ The kernel wasn't restarted after switching

**Solution:**
1. **Stop and double-check your kernel** (see "How to Verify" above)
2. **Restart the kernel**: Kernel → Restart Kernel
3. **Run Cell 0 first** (the cell with `sys.path` setup)
4. **Then run other cells** in order

### Problem: Import works but gets dependency errors (langchain_core, etc.)

**Cause:** Running in system Python which doesn't have packages installed

**Solution:**
1. Ensure `.venv` kernel is selected
2. If needed, reinstall dependencies:
   ```bash
   uv sync
   ```
3. Restart Jupyter completely

---

## 📚 Notebook Order

Run notebooks in this order to learn progressively:

1. **`1_scoping.ipynb`** - User clarification and research brief generation
2. **`2_research_agent.ipynb`** - Research agent with Tavily search
3. **`3_research_agent_mcp.ipynb`** - Research agent with MCP servers
4. **`4_research_supervisor.ipynb`** - Multi-agent supervisor coordination
5. **`5_full_agent.ipynb`** - Complete end-to-end system

---

## 💡 Pro Tips

- **Use `uv run jupyter notebook`** instead of activating venv manually - this ensures correct environment
- **Restart kernel between major changes** to avoid stale imports
- **Run cells in order** - notebooks depend on earlier cell outputs
- **First cell is critical** - It sets up Python paths for imports

---

## 🆘 Still Having Issues?

Check the main [README.md](../README.md#-troubleshooting) troubleshooting section or:
- Verify: `uv sync` completed successfully
- Verify: `.env` file exists with required API keys
- Verify: You're in the correct directory (`notebooks/`)

# Deep Research From Scratch — End‑to‑End Architecture and Module Walkthrough

This document explains how the project works step by step: how user intent is clarified, how research is executed (web and local files), how multiple agents are coordinated, and how the final report is assembled. It also explains the role and importance of the thinking tool and what changes if it’s removed.

For how to install and run the project, see README.md.

## Quick Map (Graphs)

The project exposes five runnable graphs to LangGraph Studio (declared in langgraph.json):

- `scope_research` → src/deep_research_from_scratch/research_agent_scope.py:109
- `research_agent` → src/deep_research_from_scratch/research_agent.py:144
- `research_agent_mcp` → src/deep_research_from_scratch/research_agent_mcp.py:218
- `research_agent_supervisor` → src/deep_research_from_scratch/multi_agent_supervisor.py:249
- `research_agent_full` → src/deep_research_from_scratch/research_agent_full.py:75

Recommended demo path in LangGraph Studio: scope_research → research_agent → research_agent_supervisor → research_agent_full.

## End‑to‑End Flow (High Level)

1) Scoping: clarify the request and generate a precise research brief.
2) Research: run researcher(s) to gather, reflect, and compress findings.
3) Supervision (optional but used in full flow): coordinate parallel researchers on sub‑topics, aggregate their results.
4) Report: produce a comprehensive final report from the brief and notes.

The full pipeline wires these phases together in a single graph: src/deep_research_from_scratch/research_agent_full.py:58-75

## Data and State Flow

The project relies on typed state objects passed between LangGraph nodes. The most important are:

- Agent scoping state (`AgentState`) → src/deep_research_from_scratch/state_scope.py:22-40
  - Carries conversation `messages`, the generated `research_brief`, supervisor routing `supervisor_messages`, aggregated `notes`, `raw_notes`, and the `final_report`.
- Researcher state (`ResearcherState` and `ResearcherOutputState`) → src/deep_research_from_scratch/state_research.py:17-41
  - Tracks `researcher_messages`, `compressed_research`, and `raw_notes` produced by a single researcher loop.
- Supervisor state (`SupervisorState`) → src/deep_research_from_scratch/state_multi_agent_supervisor.py:16-23
  - Tracks supervisor `supervisor_messages`, the overall `research_brief`, collected `notes`, `raw_notes`, and `research_iterations`.

These states are appended/merged across nodes and graphs, letting downstream nodes build on upstream results.

## Module‑by‑Module Walkthrough

### 1. Scoping and Brief Generation

- Module: src/deep_research_from_scratch/research_agent_scope.py:41-93, 97-109
  - Node `clarify_with_user`: Uses a structured output schema (`ClarifyWithUser`) to decide if a clarifying question is needed. If yes, the graph ends with an AI message asking the question. If not, it continues to brief generation.
  - Node `write_research_brief`: Converts the conversation into a detailed `research_brief` using structured output (`ResearchQuestion`). It also seeds `supervisor_messages` so the supervisor has context to act on.
  - Graph wiring: START → clarify_with_user → write_research_brief → END (for the scoping graph).
- State: `AgentState` captures the scoping outputs → src/deep_research_from_scratch/state_scope.py:22-40
- Prompts:
  - Clarification instructions → src/deep_research_from_scratch/prompts.py:7-45
  - Brief generation instructions → src/deep_research_from_scratch/prompts.py:47-88

Key concept: “Structured outputs” make scoping deterministic and reliable by mapping the LLM response into Pydantic schemas.

### 2. Single Research Agent (Web Search)

- Module: src/deep_research_from_scratch/research_agent.py:33-141
  - Tools: `tavily_search` and `think_tool` are bound to the LLM → src/deep_research_from_scratch/research_agent.py:21-29
  - Node `llm_call`: Adds a system prompt and invokes the LLM. The LLM either returns tool calls or a direct answer.
  - Node `tool_node`: Executes all tool calls (search and thinking) and returns their results as ToolMessages.
  - Node `compress_research`: After the loop halts (no further tool calls), compresses gathered info into `compressed_research` and aggregates `raw_notes`. Compression explicitly filters reflections (think_tool) from the final content.
  - Routing: `should_continue` decides whether to run tools again or stop to compress → src/deep_research_from_scratch/research_agent.py:101-118
  - Graph wiring: START → llm_call → (tool_node ↔ llm_call)* → compress_research → END.

- Utilities (search, summarization, thinking): src/deep_research_from_scratch/utils.py
  - Search workflow
    - Tavily search client usage → src/deep_research_from_scratch/utils.py:77-80
    - `tavily_search_multiple` → batches searches and returns raw results → src/deep_research_from_scratch/utils.py:83-112
    - Deduplicate by URL → src/deep_research_from_scratch/utils.py:147-164
    - Summarize webpage content with structured output `Summary` → src/deep_research_from_scratch/utils.py:114-145
    - Format consolidated results into a clean multi‑source string → src/deep_research_from_scratch/utils.py:192-212
    - Tool entry `tavily_search` → wraps the pipeline for a single query → src/deep_research_from_scratch/utils.py:216-240
  - Thinking tool
    - `think_tool` → a tool to record a deliberate reflection after searches or decisions → src/deep_research_from_scratch/utils.py:242-260

Why compression? The loop can generate many tool outputs. `compress_research` reduces them into a comprehensive, citation‑ready block for downstream use.

### 3. Research Agent (Local Files via MCP)

- Module: src/deep_research_from_scratch/research_agent_mcp.py
  - Purpose: Same research loop pattern but tools come from a Model Context Protocol (MCP) filesystem server, enabling research over local files.
  - MCP setup
    - Windows/WSL path handling (`convert_path_for_mcp`) → src/deep_research_from_scratch/utils.py:43-73
    - Filesystem server command selection (WSL vs others) → src/deep_research_from_scratch/research_agent_mcp.py:34-44
    - Lazy client and tool discovery → src/deep_research_from_scratch/research_agent_mcp.py:55-63, 71-98
  - Async execution
    - MCP tools require async; `tool_node` executes tools with `ainvoke` as needed → src/deep_research_from_scratch/research_agent_mcp.py:100-147
  - Compression
    - Same compression approach as web search; think_tool reflections are not included → src/deep_research_from_scratch/research_agent_mcp.py:149-175
  - Routing and wiring mirror the single researcher graph → src/deep_research_from_scratch/research_agent_mcp.py:179-218

When to use: Prefer this graph when research relies on local documents (repos, notes, datasets) rather than the web.

### 4. Multi‑Agent Supervisor

- Module: src/deep_research_from_scratch/multi_agent_supervisor.py
  - Tools available to the supervisor: `ConductResearch`, `ResearchComplete`, `think_tool` → src/deep_research_from_scratch/state_multi_agent_supervisor.py:24-40
  - Node `supervisor`: Takes the `research_brief`, decides how to proceed (plan, delegate, or finish) → src/deep_research_from_scratch/multi_agent_supervisor.py:86-115
  - Node `supervisor_tools`: Executes decisions — performs strategic reflections (think_tool), launches parallel researchers with `ConductResearch`, gathers results, and enforces exit conditions → src/deep_research_from_scratch/multi_agent_supervisor.py:146-240
  - Exit conditions: iteration limit, absence of tool calls, or explicit `ResearchComplete` tool request → src/deep_research_from_scratch/multi_agent_supervisor.py:146-157
  - Aggregation: sub‑agent results arrive as ToolMessages; `get_notes_from_tool_calls` extracts their content for `notes` → src/deep_research_from_scratch/multi_agent_supervisor.py:37-52, 224-231
  - Graph wiring: START → supervisor → supervisor_tools → (loop or END) → src/deep_research_from_scratch/multi_agent_supervisor.py:244-249

Parallelism: The supervisor can spawn multiple researchers in one iteration (bounded by max agents) for independent sub‑topics, then merge their compressed outputs.

### 5. Full Orchestration (End‑to‑End)

- Module: src/deep_research_from_scratch/research_agent_full.py:34-56, 58-75
  - Nodes: `clarify_with_user` → `write_research_brief` → `supervisor_subgraph` → `final_report_generation`.
  - Final report generation: Builds a writer prompt from the `research_brief` and aggregated `findings` (`notes`) and invokes a high‑context writer model. Updates `final_report` and appends a user‑visible message → src/deep_research_from_scratch/research_agent_full.py:34-56

This graph is what you run to show the full journey from user query to polished report.

### 6. Prompts and Guardrails

- Scoping prompts (clarification and brief) → src/deep_research_from_scratch/prompts.py:7-45, 47-88
- Research agent loop prompt and budgets → src/deep_research_from_scratch/prompts.py:90-120
- MCP research prompt and file‑operation budgets → src/deep_research_from_scratch/prompts.py:120-259
- Compression prompt (excludes think_tool reflections; focuses on facts and sources) → src/deep_research_from_scratch/prompts.py:260-313
- Supervisor prompt with parallelization rules and budgets → src/deep_research_from_scratch/prompts.py:260-313 and onward (lead_researcher_prompt section)

Design choices: prompts emphasize iteration budgets, stop conditions, and the separation between internal reflections (think_tool) and external, reportable facts.

## The Thinking Tool: Role and Importance

What it is: `think_tool` is a simple tool that records an explicit reflection at key points in the loop (after searches, before/after delegations). It acts like a structured “pause to plan.” → src/deep_research_from_scratch/utils.py:242-260

Why it matters:

- Quality control: Forces the agent (and supervisor) to assess whether current sources suffice, identify gaps, and adjust the plan.
- Budget adherence: Encourages deliberate stopping per the prompt budgets (e.g., 2–5 searches, or limited delegations).
- Relevance: Reduces “search thrash” by planning follow‑up queries with better focus.

How it is handled downstream:

- Compression excludes think_tool reflections by design, so only substantive findings (from web/local sources) appear in the final research content → src/deep_research_from_scratch/prompts.py:260-313

What happens without it:

- Less self‑correction: The agent is more likely to over‑search, wander, or miss key gaps because there’s no enforced reflection step.
- Weaker stop behavior: Without deliberate checkpoints, you may hit budgets abruptly or under‑collect critical evidence.
- Poorer supervision: The supervisor loses a quick way to express planning and assessment between delegations.

The result is often lower‑quality synthesis and less efficient use of tool budgets.

## End‑to‑End Walkthrough (What Happens When You Run Full Agent)

1. Input arrives as `messages` (user’s query) → state: AgentState.
2. `clarify_with_user` runs structured clarification. If needed, it returns one concise question and stops until the user answers. Otherwise, it acknowledges it will start.
3. `write_research_brief` converts conversation to a detailed `research_brief` and seeds `supervisor_messages`.
4. `supervisor` reads the brief, plans (often via think_tool), and may call `ConductResearch` for sub‑topics (possibly several in parallel, bounded by a max).
5. For each `ConductResearch` call, a `research_agent` subgraph runs its loop:
   - `llm_call` → tool calls (tavily_search + think_tool) → `tool_node` executes them.
   - This repeats until there are no tool calls (stop condition), then `compress_research` produces `compressed_research` and `raw_notes`.
6. The supervisor receives compressed outputs as ToolMessages, aggregates them into `notes`, and either launches more research or decides to end.
7. `final_report_generation` converts the brief + notes into a polished `final_report` and posts it to `messages` for UI.

## Notebooks (Learning Path)

These notebooks explain how each component is built; see notebooks/README.md for kernel and usage notes.

- 1_scoping.ipynb → Scoping and brief generation (maps to `scope_research` graph).
- 2_research_agent.ipynb → Single researcher with web search and reflection (maps to `research_agent`).
- 3_research_agent_mcp.ipynb → Research over local files via MCP (maps to `research_agent_mcp`).
- 4_research_supervisor.ipynb → Supervisor coordinating multiple researchers (maps to `research_agent_supervisor`).
- 5_full_agent.ipynb → End‑to‑end integration (maps to `research_agent_full`).

## Extensibility and Configuration

- Model providers: All LLMs are created via `init_chat_model`; switching providers/models is straightforward in code (Gemini default; OpenAI/Anthropic alternatives indicated inline in each module).
- Search: Swap `tavily_search` for other search tools; keep the same tool signature and adjust prompts if needed.
- MCP: Add more MCP servers or tools; the client lazily discovers available tools each run.
- Budgets and stop conditions: Adjust in prompt templates to tune cost/quality tradeoffs.

## Troubleshooting Tips (Operational)

- API keys: `TAVILY_API_KEY` and an LLM provider key (e.g., `GOOGLE_API_KEY`) must be set in `.env`.
- LangGraph Studio: Select the desired graph from the dropdown (see langgraph.json for names and paths).
- WSL and MCP: Ensure Windows Node.js is available in WSL for MCP; the code converts WSL paths and launches `npx` appropriately.
- Jupyter: Always select the `.venv` kernel (see notebooks/README.md) when running notebooks.

---

With this guide, you can present or explore the entire system—from scoping to final report—understanding what each module does, how data flows between nodes, and why the thinking tool is central to quality and efficiency.


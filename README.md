# Open Deep Researcher Framework

A powerful, AI-driven research framework that conducts comprehensive web research using state-of-the-art language models, web search capabilities, and intelligent agentic workflows. Built with LangGraph and LangChain, this framework automates the research process with autonomous multi-step reasoning and information synthesis.

## 🌟 Overview

The Open Deep Researcher is an intelligent research assistant that:
- Conducts autonomous web research using advanced search strategies
- Synthesizes information from multiple sources with proper citations
- Uses strategic reflection to guide research decisions
- Provides comprehensive, well-structured research reports
- Supports cross-platform execution (Windows, Linux, WSL, macOS)

## 🏗️ Architecture

The framework is built on a **stateful agentic workflow** using LangGraph, featuring:

### Core Components

1. **Research Agent**: Main orchestrator that plans and executes research queries
2. **Tool System**: Integrated tools for search and reflection
3. **Compression Engine**: Synthesizes findings into coherent reports
4. **State Management**: Tracks conversation history and research progress

### Workflow Graph

```
START → LLM Call → Tool Execution → Compression → END
           ↑           |
           └───────────┘
         (Iterative Loop)
```

The agent:
- Receives a research question
- Plans search strategies using reflection
- Executes searches in parallel or series
- Compresses and synthesizes findings
- Produces a final research report with citations

## 🚀 Key Features

### 🔍 Intelligent Search
- **Tavily Search Integration**: High-quality web search with content extraction
- **Multi-query Support**: Execute multiple searches in parallel
- **Content Summarization**: Automatic webpage content summarization using LLMs
- **Deduplication**: Smart removal of duplicate sources

### 🧠 Strategic Reasoning
- **Think Tool**: Built-in reflection mechanism for research planning
- **Adaptive Search**: Adjusts strategy based on findings
- **Budget Management**: Configurable search limits (2-5 queries per research)
- **Quality Control**: Stops when sufficient information is gathered

### 📊 Research Output
- **Comprehensive Reports**: Full synthesis of all findings
- **Proper Citations**: Inline citations and source bibliography
- **Key Excerpts**: Important quotes preserved from sources
- **Structured Format**: Clean, readable markdown output

### 🛠️ Technical Features
- **Cross-platform Support**: Works on Windows, Linux, WSL, and macOS
- **MCP Server Integration**: Model Context Protocol support for enhanced tooling
- **Rich Terminal Output**: Beautiful console formatting with Rich library
- **Flexible Model Support**: Easy switching between LLM providers

## 📋 Requirements

### Dependencies

```
langchain
langchain-core
langgraph
tavily-python
pydantic
typing-extensions
python-dotenv
rich
google-generativeai  # or other LLM providers
IPython (for notebook execution)
```

### API Keys

You'll need API keys for:
- **Tavily Search**: Web search capabilities
- **Google Gemini API**: LLM for research and summarization (or alternatives like OpenAI, Anthropic)

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/amalsalilan/Infosys-Springboard-Virtual-Internship-6.0-Open-Deep-Researcher-batch-2.git
   cd Infosys-Springboard-Virtual-Internship-6.0-Open-Deep-Researcher-batch-2
   ```

2. **Install dependencies**
   ```bash
   pip install langchain langchain-core langgraph tavily-python pydantic python-dotenv rich google-generativeai
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_GENAI_API_KEY=your_google_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

4. **Open the notebook**
   ```bash
   jupyter notebook Notebooks/research_agent.ipynb
   ```

## 🎯 Usage

### Basic Research Query

```python
from langchain_core.messages import HumanMessage

# Define your research question
research_brief = """
I want to identify and evaluate the coffee shops in San Francisco 
that are considered the best based specifically on coffee quality. 
My research should focus on analyzing and comparing coffee shops 
within the San Francisco area, using coffee quality as the primary criterion.
"""

# Run the research agent
result = researcher_agent.invoke({
    "messages": [HumanMessage(content=research_brief)]
})

# Access the compressed research report
print(result['compressed_research'])
```

### Model Configuration

The framework supports multiple LLM providers. Configure in the notebook:

```python
# Google Gemini (default)
model = init_chat_model(
    model="gemini-2.5-pro", 
    model_provider="google_genai", 
    temperature=0.0
)

# Alternative: OpenAI
# model = init_chat_model(model="gpt-4.1", model_provider="openai", temperature=0.0)

# Alternative: Anthropic
# model = init_chat_model(model="claude-sonnet-4-20250514", model_provider="anthropic", temperature=0.0)
```

### Customizing Search Behavior

Adjust research parameters in the prompts:

```python
# Simple queries: 2-3 search calls
# Complex queries: up to 5 search calls
# Adjust in research_agent_prompt
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_GENAI_API_KEY` | Google Gemini API key | Yes (or alternative LLM key) |
| `TAVILY_API_KEY` | Tavily search API key | Yes |

### Search Configuration

Configure in `tavily_search` function:
- `search_depth`: "basic" or "advanced"
- `max_results`: Number of results per query (default: 5)
- `include_raw_content`: Include full webpage content for summarization

### Model Settings

- **Temperature**: Set to 0.0 for deterministic outputs
- **Max Tokens**: Configure for compression model (default: 32000)
- **Provider**: Switch between Google, OpenAI, Anthropic

## 📚 Project Structure

```
.
├── Notebooks/
│   └── research_agent.ipynb    # Main implementation notebook
├── LICENSE                      # MIT License
└── README.md                    # This file
```

## 🎨 Output Examples

The framework generates comprehensive research reports with:

- **Executive Summary**: High-level overview of findings
- **Detailed Analysis**: In-depth information from multiple sources
- **Citations**: Numbered references throughout the report
- **Source List**: Complete bibliography with URLs

Example output structure:
```
**List of Queries and Tool Calls Made**
- tavily_search: "coffee shops San Francisco quality"
- tavily_search: "specialty coffee roasters SF"

**Fully Comprehensive Findings**
Based on research across multiple sources, the top coffee shops in 
San Francisco for coffee quality include:

1. **Ritual Coffee Roasters** - Known for direct trade relationships... [1]
2. **Blue Bottle Coffee** - Pioneer in third wave coffee movement... [2]

**Sources**
[1] Source Name - URL
[2] Source Name - URL
```

## 🔄 How It Works

1. **Question Analysis**: The LLM analyzes the research question
2. **Search Planning**: Uses `think_tool` to plan search strategy
3. **Parallel Execution**: Executes multiple `tavily_search` calls
4. **Content Processing**: Summarizes webpage content from results
5. **Reflection**: Evaluates if more searches are needed
6. **Synthesis**: Compresses all findings into a cohesive report
7. **Citation**: Adds proper inline citations and source bibliography

## 🛡️ Built-in Safeguards

- **Search Budgets**: Prevents excessive API calls (2-5 searches per query)
- **Deduplication**: Avoids processing same sources multiple times
- **Content Filtering**: Focuses on substantive research content
- **Iteration Limits**: Prevents infinite loops in research cycle

## 🌐 Cross-Platform Support

The framework includes utilities for:
- **WSL Integration**: Automatic path conversion for MCP servers
- **Platform Detection**: Cross-platform date formatting
- **Environment Flexibility**: Works in Jupyter notebooks and scripts

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Additional search providers
- More sophisticated citation systems
- Multi-language support
- Enhanced visualization tools
- API endpoint wrapper

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Amal Salilan

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - For agentic workflows
- [LangChain](https://github.com/langchain-ai/langchain) - For LLM orchestration
- [Tavily](https://tavily.com/) - For intelligent web search
- [Google Gemini](https://deepmind.google/technologies/gemini/) - For language understanding
- [Rich](https://github.com/Textualize/rich) - For beautiful terminal output

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the notebook for inline documentation
- Review the prompt templates for customization options

---

**Part of Infosys Springboard Virtual Internship 6.0 - Open Deep Researcher Batch 2**

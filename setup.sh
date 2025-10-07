#!/bin/bash
# Automated setup script for Deep Research From Scratch
# Run this after: uv sync

set -e

echo "🚀 Deep Research From Scratch - Automated Setup"
echo "================================================"
echo ""

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: .venv not found"
    echo "Please run 'uv sync' first to create the virtual environment"
    exit 1
fi

# Step 1: Create .env file if it doesn't exist
echo "📝 Step 1: Setting up .env file..."
if [ -f ".env" ]; then
    echo "   ℹ️  .env already exists - skipping"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "   ✅ Created .env from .env.example"
        echo "   ⚠️  IMPORTANT: Edit .env and add your API keys:"
        echo "      - TAVILY_API_KEY (get from https://tavily.com)"
        echo "      - GOOGLE_API_KEY (get from https://aistudio.google.com/app/apikey)"
    else
        echo "   ❌ .env.example not found - please create .env manually"
    fi
fi

# Step 2: Install Jupyter kernel
echo ""
echo "🔧 Step 2: Installing Jupyter kernel..."
source .venv/bin/activate
python -m ipykernel install --user --name=deep-research --display-name="Deep Research (venv)" 2>/dev/null && \
    echo "   ✅ Jupyter kernel installed successfully" || \
    echo "   ⚠️  Kernel may already be installed (this is okay)"

# Step 3: Verify setup
echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Edit .env file with your API keys (if you haven't already)"
echo "   2. For LangGraph Studio:"
echo "      → Run: uv run langgraph dev --allow-blocking"
echo "      → Open: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
echo ""
echo "   3. For Jupyter Notebooks:"
echo "      → Run: uv run jupyter notebook"
echo "      → Select kernel: 'Deep Research (venv)'"
echo "      → See notebooks/README.md for detailed instructions"
echo ""
echo "🎉 You're all set! Happy researching!"

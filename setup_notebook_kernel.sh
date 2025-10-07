#!/bin/bash
# Setup Jupyter kernel for the notebooks

set -e

echo "Setting up Jupyter kernel for Deep Research notebooks..."

# Activate venv and install kernel
if [ -d ".venv" ]; then
    source .venv/bin/activate
    python -m ipykernel install --user --name=deep-research-venv --display-name="Deep Research (venv)"
    echo "✓ Kernel installed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Start Jupyter: uv run jupyter notebook"
    echo "2. Open any notebook"
    echo "3. Click 'Kernel' → 'Change Kernel' → Select 'Deep Research (venv)'"
    echo "4. Run cells normally"
else
    echo "Error: .venv directory not found"
    echo "Please run 'uv sync' first to create the virtual environment"
    exit 1
fi

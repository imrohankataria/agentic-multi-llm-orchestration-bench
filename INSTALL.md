# Installation Guide

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (or other supported LLM provider)
- pip package manager

## Basic Installation

### Option 1: Install from source

```bash
git clone https://github.com/imrohankataria/agentic-multi-llm-orchestration-bench.git
cd agentic-multi-llm-orchestration-bench
pip install -r requirements.txt
```

### Option 2: Install with setup.py

```bash
git clone https://github.com/imrohankataria/agentic-multi-llm-orchestration-bench.git
cd agentic-multi-llm-orchestration-bench

# Install core dependencies only
pip install -e .

# OR install with CrewAI support
pip install -e ".[crewai]"

# OR install with LangGraph support
pip install -e ".[langgraph]"

# OR install everything
pip install -e ".[all]"
```

## Framework-Specific Installation

### For CrewAI Only

```bash
pip install crewai langchain langchain-openai
```

### For LangGraph Only

```bash
pip install langgraph langchain langchain-openai
```

### For Both Frameworks

```bash
pip install crewai langgraph langchain langchain-openai
```

## Configuration

### 1. Set up API Keys

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Or set environment variable:

```bash
export OPENAI_API_KEY='your_openai_api_key_here'
```

### 2. Verify Installation

Test that everything works:

```bash
# Test LangGraph (simpler, no external dependencies)
python examples/langgraph_example.py

# Test CrewAI (requires crewai package)
python examples/crewai_example.py

# Test comparison (requires both frameworks)
python examples/compare_workflows.py
```

## Troubleshooting

### ImportError: No module named 'crewai'

Install CrewAI:
```bash
pip install crewai
```

### ImportError: No module named 'langgraph'

Install LangGraph:
```bash
pip install langgraph
```

### OpenAI API errors

Make sure your API key is set correctly:
```bash
echo $OPENAI_API_KEY  # Should display your key
```

### Matplotlib/Plotly display issues

If visualizations don't display:
```bash
pip install --upgrade matplotlib plotly pandas
```

For headless environments, visualizations are saved as HTML files in `outputs/` directory.

## Development Installation

For contributing to the project:

```bash
git clone https://github.com/imrohankataria/agentic-multi-llm-orchestration-bench.git
cd agentic-multi-llm-orchestration-bench
pip install -e ".[dev]"
```

This installs additional development tools:
- pytest for testing
- black for code formatting
- flake8 for linting

## Minimal Installation (Core Only)

If you only need the cost tracking functionality:

```bash
pip install matplotlib plotly pandas python-dotenv
```

Then use the cost tracker directly in your code without the framework integrations.

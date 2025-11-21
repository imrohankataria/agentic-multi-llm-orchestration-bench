# 💰 Multi-Agent Workflow Cost Tracing Benchmark

> **How much does a multi-agent workflow really cost?**

This repository provides comprehensive cost tracking and analysis for multi-agent AI workflows. Built with support for both **CrewAI** and **LangGraph**, it traces costs at every tool call, LLM invocation, and agent step. Get visual timelines with dollar overlays, automatic spike detection ("Agent 2 is your cost problem!"), and workflow comparison charts.

## ✨ Features

- 🎯 **Granular Cost Tracking**: Track costs at every tool, LLM call, and agent step
- 📊 **Visual Agent Timeline**: Interactive timeline showing agent activities with cost overlays
- 🚨 **Spike Detection**: Automatically identifies which agents are consuming excessive resources
- 📈 **Workflow Comparison**: Compare multiple workflow runs side-by-side
- 🔧 **Framework Support**: Works with both CrewAI and LangGraph
- 💾 **Export Options**: JSON exports for further analysis
- 📉 **Multiple Visualizations**: Pie charts, timelines, event breakdowns, and comparison dashboards

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/imrohankataria/agentic-multi-llm-orchestration-bench.git
cd agentic-multi-llm-orchestration-bench

# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
# Or create a .env file
cp .env.example .env
# Edit .env and add your API key
```

### Basic Usage

#### Compare Both Frameworks

Run both CrewAI and LangGraph workflows and compare them:

```bash
python examples/compare_workflows.py
```

This will:
- Run identical workflows on both frameworks
- Generate cost analysis for each
- Create a comparison dashboard
- Identify cost spikes
- Output all visualizations to `outputs/` directory

#### LangGraph Only

```bash
python examples/langgraph_example.py
```

#### CrewAI Only

```bash
python examples/crewai_example.py
```

## 📊 What You Get

### 1. Agent Timeline with Cost Overlays
Interactive timeline showing when each agent was active and how much each action cost. Marker sizes represent relative costs.

![Timeline Example](https://via.placeholder.com/800x300.png?text=Agent+Timeline+with+Cost+Overlays)

### 2. Cost Breakdown by Agent
Pie chart showing which agents consumed the most resources. Problem agents are highlighted in red.

![Breakdown Example](https://via.placeholder.com/500x400.png?text=Cost+Breakdown+Pie+Chart)

### 3. Spike Detection
Automatically identifies agents that cost significantly more than average:

```
⚠️ Editor is your cost problem!
```

### 4. Workflow Comparison Dashboard
Side-by-side comparison of multiple workflow runs with cost metrics.

### 5. Detailed Text Reports

```
==============================================================
MULTI-AGENT WORKFLOW COST REPORT
==============================================================

Total Cost: $0.003450
Total Events: 9
Duration: 12.45 seconds

Agent Cost Breakdown:
--------------------------------------------------------------
  Researcher: $0.001200
    - LLM Calls: 1
    - Tool Calls: 0
    - Agent Steps: 1
    - Total Tokens: 850

  Writer: $0.001450
    - LLM Calls: 1
    - Tool Calls: 0
    - Agent Steps: 1
    - Total Tokens: 920

  Editor: $0.000800 ⚠️ COST SPIKE
    - LLM Calls: 1
    - Tool Calls: 0
    - Agent Steps: 1
    - Total Tokens: 650
```

## 🏗️ Architecture

```
src/
├── cost_tracker/          # Core cost tracking infrastructure
│   ├── core.py           # CostTracker, CostEvent, pricing models
│   └── __init__.py
├── agents/               # Framework integrations
│   ├── crewai_agents.py  # CrewAI workflow with cost tracking
│   └── langgraph_agents.py # LangGraph workflow with cost tracking
└── visualizations/       # Visualization generation
    └── charts.py         # Timeline, pie charts, comparisons

examples/                 # Example scripts
├── compare_workflows.py  # Compare both frameworks
├── crewai_example.py    # CrewAI example
└── langgraph_example.py # LangGraph example
```

## 💻 Using in Your Own Code

### Track Costs in CrewAI

```python
from src.agents.crewai_agents import CrewAIWorkflow
from src.visualizations.charts import create_all_visualizations

# Create workflow with cost tracking
workflow = CrewAIWorkflow(model="gpt-4o-mini")

# Run your workflow
result = workflow.run_workflow("Your topic here")

# Analyze costs
print(f"Total cost: ${result['cost_analysis']['total_cost']:.4f}")
print(f"Cost spikes: {result['cost_spikes']}")

# Generate visualizations
create_all_visualizations(workflow.get_cost_tracker(), prefix="my_run_")
```

### Track Costs in LangGraph

```python
from src.agents.langgraph_agents import LangGraphWorkflow
from src.visualizations.charts import create_all_visualizations

# Create workflow with cost tracking
workflow = LangGraphWorkflow(model="gpt-4o-mini")

# Run your workflow
result = workflow.run_workflow("Your topic here")

# Analyze costs
print(f"Total cost: ${result['cost_analysis']['total_cost']:.4f}")
if result['cost_warning']:
    print(result['cost_warning'])

# Generate visualizations
create_all_visualizations(workflow.get_cost_tracker(), prefix="my_run_")
```

### Use the Cost Tracker Directly

```python
from src.cost_tracker import CostTracker

# Create tracker
tracker = CostTracker()
tracker.start_workflow()

# Track LLM calls
tracker.track_llm_call(
    agent_name="MyAgent",
    model="gpt-4o-mini",
    input_tokens=100,
    output_tokens=50,
    duration_ms=1500
)

# Track tool calls
tracker.track_tool_call(
    agent_name="MyAgent",
    tool_name="web_search",
    duration_ms=500
)

# Track agent steps
tracker.track_agent_step(
    agent_name="MyAgent",
    step_name="analyze_results",
    duration_ms=2000
)

# End and analyze
tracker.end_workflow()
summary = tracker.get_summary()
spikes = tracker.identify_cost_spikes()
```

## 🎛️ Configuration

### Supported Models

The cost tracker includes pricing for common models:
- GPT-4, GPT-4-Turbo, GPT-4o, GPT-4o-mini
- GPT-3.5-Turbo
- Claude-3 (Opus, Sonnet, Haiku)

Pricing is automatically calculated based on token usage. See `src/cost_tracker/core.py` for full pricing table.

### Custom Models

Add your own model pricing:

```python
from src.cost_tracker.core import LLM_PRICING

LLM_PRICING["my-custom-model"] = {
    "input": 0.001,   # $ per 1K input tokens
    "output": 0.002   # $ per 1K output tokens
}
```

## 📦 Output Files

When you run a workflow, the following files are generated in `outputs/`:

- `*_timeline.html` - Interactive agent timeline
- `*_breakdown.html` - Cost breakdown pie chart
- `*_events.html` - Event type analysis
- `*_report.txt` - Detailed text report
- `*_data.json` - Raw cost data (JSON)
- `workflow_comparison.html` - Multi-workflow comparison (when comparing)

## 🔍 Use Cases

1. **Cost Optimization**: Identify which agents are most expensive and optimize them
2. **Budget Planning**: Understand actual costs before scaling to production
3. **A/B Testing**: Compare different agent configurations or prompts
4. **Framework Evaluation**: Compare CrewAI vs LangGraph for your use case
5. **Performance Monitoring**: Track costs over time as you iterate

## 🛠️ Requirements

- Python 3.8+
- OpenAI API key (or other LLM provider)
- Optional: CrewAI for CrewAI examples
- Optional: LangGraph for LangGraph examples

## 📝 License

MIT License - feel free to use in your own projects!

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional framework support (AutoGen, etc.)
- More visualization types
- Cost optimization recommendations
- Real-time cost monitoring
- More detailed token-level analysis

## 🙏 Acknowledgments

Built with:
- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent orchestration
- [LangGraph](https://github.com/langchain-ai/langgraph) - Graph-based workflows
- [Plotly](https://plotly.com/) - Interactive visualizations
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework

## 📧 Contact

For questions or feedback, open an issue or reach out to the maintainers.

---

**Start tracking your multi-agent costs today!** 💰📊
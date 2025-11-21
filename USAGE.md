# Usage Guide

## Quick Start Examples

### 1. Demo with Mock Data (No API Key Required)

The fastest way to see the cost tracker in action:

```bash
python examples/demo_mock_data.py
```

This creates mock workflow data and generates all visualizations without making any API calls.

**Output:**
- Agent timeline with cost overlays
- Cost breakdown pie chart
- Event type analysis
- Workflow comparison dashboard
- Detailed text report
- JSON data export

### 2. LangGraph Workflow (Requires OpenAI API Key)

```bash
export OPENAI_API_KEY='your-key-here'
python examples/langgraph_example.py
```

Runs a real multi-agent workflow using LangGraph with three agents:
- **Researcher**: Gathers information on a topic
- **Writer**: Creates article based on research
- **Editor**: Refines and polishes the article

### 3. CrewAI Workflow (Requires OpenAI API Key + CrewAI)

```bash
pip install crewai
export OPENAI_API_KEY='your-key-here'
python examples/crewai_example.py
```

Runs the same workflow using CrewAI framework instead of LangGraph.

### 4. Compare Both Frameworks

```bash
pip install crewai langgraph
export OPENAI_API_KEY='your-key-here'
python examples/compare_workflows.py
```

Runs identical workflows on both frameworks and generates comparison visualizations.

## Using in Your Own Code

### Basic Cost Tracking

```python
from src.cost_tracker import CostTracker

# Initialize
tracker = CostTracker()
tracker.start_workflow()

# Track LLM calls
tracker.track_llm_call(
    agent_name="MyAgent",
    model="gpt-4o-mini",
    input_tokens=500,
    output_tokens=300,
    duration_ms=1500
)

# Track tool usage
tracker.track_tool_call(
    agent_name="MyAgent",
    tool_name="web_search",
    duration_ms=800
)

# Track agent steps
tracker.track_agent_step(
    agent_name="MyAgent",
    step_name="process_data",
    duration_ms=2000
)

# Finish and analyze
tracker.end_workflow()
summary = tracker.get_summary()
print(f"Total cost: ${summary['total_cost']:.4f}")

# Identify cost problems
spikes = tracker.identify_cost_spikes()
if spikes:
    print(f"Cost problems: {', '.join(spikes)}")
```

### Creating Visualizations

```python
from src.visualizations.charts import CostVisualizer

visualizer = CostVisualizer(tracker)

# Individual visualizations
visualizer.create_agent_timeline("timeline.html")
visualizer.create_cost_breakdown_chart("breakdown.html")
visualizer.create_event_type_breakdown("events.html")
visualizer.generate_cost_report("report.txt")

# Or create all at once
from src.visualizations.charts import create_all_visualizations
create_all_visualizations(tracker, prefix="my_run_")
```

### Comparing Multiple Workflows

```python
from src.visualizations.charts import CostVisualizer

# Run multiple workflows
tracker1 = run_workflow_a()
tracker2 = run_workflow_b()

# Compare them
visualizer = CostVisualizer(tracker1)
visualizer.create_comparison_dashboard(
    {
        "Workflow A": tracker1,
        "Workflow B": tracker2
    },
    output_file="comparison.html"
)
```

### Integrating with CrewAI

```python
from src.agents.crewai_agents import CrewAIWorkflow

# Create workflow with cost tracking
workflow = CrewAIWorkflow(model="gpt-4o-mini")

# Run it
result = workflow.run_workflow("Your topic here")

# Access cost data
print(result['cost_analysis'])
print(result['cost_warning'])  # Automatic spike detection

# Get the tracker for custom analysis
tracker = workflow.get_cost_tracker()
```

### Integrating with LangGraph

```python
from src.agents.langgraph_agents import LangGraphWorkflow

# Create workflow with cost tracking
workflow = LangGraphWorkflow(model="gpt-4o-mini")

# Run it
result = workflow.run_workflow("Your topic here")

# Access cost data
print(result['cost_analysis'])
print(result['cost_warning'])

# Get the tracker
tracker = workflow.get_cost_tracker()
```

## Understanding Cost Spike Detection

The cost tracker automatically identifies agents that consume significantly more resources than average:

- **Threshold**: By default, agents consuming > 2x the average cost are flagged
- **Warning Messages**: "Agent X is your cost problem!"
- **Visual Indicators**: Cost spikes shown in red on pie charts

Customize the threshold:

```python
spikes = tracker.identify_cost_spikes(threshold=1.5)  # More sensitive
spikes = tracker.identify_cost_spikes(threshold=3.0)  # Less sensitive
```

## Output Files

All visualizations are saved as HTML files using Plotly, making them:
- **Interactive**: Hover, zoom, pan
- **Shareable**: Send to team members
- **Embeddable**: Include in reports or dashboards
- **No backend required**: Pure client-side

## Cost Models

The tracker includes pricing for:
- **OpenAI**: GPT-4, GPT-4-Turbo, GPT-4o, GPT-4o-mini, GPT-3.5-Turbo
- **Anthropic**: Claude-3 (Opus, Sonnet, Haiku)

Prices are per 1,000 tokens and automatically updated. See `src/cost_tracker/core.py` for the full pricing table.

### Adding Custom Models

```python
from src.cost_tracker.core import LLM_PRICING

LLM_PRICING["my-model"] = {
    "input": 0.001,   # $ per 1K input tokens
    "output": 0.002   # $ per 1K output tokens
}
```

## Best Practices

1. **Always start and end workflows**:
   ```python
   tracker.start_workflow()
   # ... your code ...
   tracker.end_workflow()
   ```

2. **Track everything**: LLM calls, tool usage, and agent steps give complete visibility

3. **Use meaningful agent names**: Makes it easier to identify cost problems

4. **Export data regularly**: Keep JSON exports for historical analysis

5. **Set cost budgets**: Use spike detection to catch runaway costs early

6. **Compare regularly**: Run comparison workflows to optimize over time

## Troubleshooting

### "No events to visualize"
- Make sure you're calling tracking methods (track_llm_call, etc.)
- Check that you're using the same tracker instance

### "No cost data"
- Ensure LLM calls include token counts
- Verify model names match the pricing table

### Visualizations don't display
- Check that output files were created
- Open HTML files in a modern browser
- For headless servers, copy files to local machine

### High costs detected
- Review the cost breakdown by agent
- Check token usage per call
- Consider using cheaper models (e.g., gpt-4o-mini instead of gpt-4)
- Optimize prompts to reduce token usage

## Advanced Usage

### Custom Metadata

Track additional information with events:

```python
tracker.track_llm_call(
    agent_name="Researcher",
    model="gpt-4o-mini",
    input_tokens=500,
    output_tokens=300,
    metadata={
        "prompt_type": "research",
        "user_id": "user123",
        "session_id": "abc456"
    }
)
```

### Accessing Raw Events

```python
# Get all events
for event in tracker.events:
    print(f"{event.timestamp}: {event.agent_name} - ${event.cost}")

# Filter by agent
agent_events = [e for e in tracker.events if e.agent_name == "Researcher"]

# Filter by type
llm_calls = [e for e in tracker.events if e.event_type == "llm_call"]
```

### Custom Analysis

```python
summary = tracker.get_summary()

# Calculate cost per token
total_cost = summary['total_cost']
total_tokens = sum(s['total_tokens'] for s in summary['agent_summaries'].values())
cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0

print(f"Cost per token: ${cost_per_token:.8f}")

# Find most expensive agent
most_expensive = max(summary['agent_costs'].items(), key=lambda x: x[1])
print(f"Most expensive agent: {most_expensive[0]} (${most_expensive[1]:.4f})")
```

## Next Steps

- Integrate cost tracking into your production agents
- Set up monitoring and alerting for cost spikes
- Build historical cost analysis
- Create custom dashboards with the JSON exports
- Share cost reports with your team

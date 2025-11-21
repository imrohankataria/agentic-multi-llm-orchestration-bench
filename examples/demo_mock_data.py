"""
Demo: Cost Tracker with Mock Data
Demonstrates cost tracking and visualization without requiring API calls
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cost_tracker.core import CostTracker
from visualizations.charts import CostVisualizer


def create_mock_workflow():
    """Create a mock workflow with simulated cost data"""
    tracker = CostTracker()
    tracker.start_workflow()
    
    # Simulate a researcher agent (moderate cost)
    for i in range(3):
        tracker.track_llm_call(
            agent_name="Researcher",
            model="gpt-4o-mini",
            input_tokens=random.randint(400, 600),
            output_tokens=random.randint(200, 400),
            duration_ms=random.randint(1000, 2000)
        )
        tracker.track_agent_step(
            agent_name="Researcher",
            step_name=f"research_step_{i+1}",
            duration_ms=random.randint(500, 1000)
        )
    
    # Simulate a writer agent (higher cost - will be flagged as spike)
    for i in range(4):
        tracker.track_llm_call(
            agent_name="Writer",
            model="gpt-4o-mini",
            input_tokens=random.randint(800, 1200),  # More tokens
            output_tokens=random.randint(600, 900),   # More output
            duration_ms=random.randint(2000, 3000)
        )
        tracker.track_tool_call(
            agent_name="Writer",
            tool_name="grammar_check",
            duration_ms=random.randint(300, 500)
        )
    
    # Simulate an editor agent (low cost)
    for i in range(2):
        tracker.track_llm_call(
            agent_name="Editor",
            model="gpt-4o-mini",
            input_tokens=random.randint(300, 500),
            output_tokens=random.randint(150, 250),
            duration_ms=random.randint(800, 1500)
        )
        tracker.track_agent_step(
            agent_name="Editor",
            step_name=f"edit_step_{i+1}",
            duration_ms=random.randint(400, 800)
        )
    
    tracker.end_workflow()
    return tracker


def main():
    """Run demo with mock data"""
    print("=" * 70)
    print("DEMO: Multi-Agent Cost Tracking (Mock Data)")
    print("=" * 70)
    print("\nThis demo uses simulated data to demonstrate cost tracking")
    print("without requiring API keys or actual LLM calls.\n")
    
    # Create mock workflow
    print("Creating mock workflow with 3 agents...")
    tracker = create_mock_workflow()
    
    # Display summary
    summary = tracker.get_summary()
    
    print("\n" + "=" * 70)
    print("COST ANALYSIS")
    print("=" * 70)
    
    print(f"\nTotal Cost: ${summary['total_cost']:.6f}")
    print(f"Total Events: {summary['total_events']}")
    print(f"Duration: {summary['duration_seconds']:.2f} seconds")
    
    print("\nAgent Cost Breakdown:")
    for agent, cost in summary['agent_costs'].items():
        spike_marker = " ⚠️" if agent in summary['cost_spikes'] else ""
        print(f"  • {agent}: ${cost:.6f}{spike_marker}")
    
    if summary['cost_spikes']:
        print(f"\n⚠️  Cost Spike Detection:")
        for spike in summary['cost_spikes']:
            print(f"   → {spike} is your cost problem!")
    
    print("\nDetailed Agent Breakdown:")
    print("-" * 70)
    for agent, details in summary['agent_summaries'].items():
        print(f"\n{agent}:")
        print(f"  Total Cost: ${details['total_cost']:.6f}")
        print(f"  LLM Calls: {details['num_llm_calls']}")
        print(f"  Tool Calls: {details['num_tool_calls']}")
        print(f"  Agent Steps: {details['num_steps']}")
        print(f"  Total Tokens: {details['total_tokens']}")
    
    # Generate visualizations
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)
    
    os.makedirs("outputs", exist_ok=True)
    
    visualizer = CostVisualizer(tracker)
    
    print("\nCreating visualizations...")
    visualizer.create_agent_timeline("outputs/demo_timeline.html")
    visualizer.create_cost_breakdown_chart("outputs/demo_breakdown.html")
    visualizer.create_event_type_breakdown("outputs/demo_events.html")
    visualizer.generate_cost_report("outputs/demo_report.txt")
    tracker.export_to_json("outputs/demo_data.json")
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)
    print("\nGenerated files in 'outputs/' directory:")
    print("  • demo_timeline.html - Interactive agent timeline")
    print("  • demo_breakdown.html - Cost breakdown pie chart")
    print("  • demo_events.html - Event type analysis")
    print("  • demo_report.txt - Detailed text report")
    print("  • demo_data.json - Raw cost data")
    print("\nOpen the HTML files in your browser to see the visualizations!")
    
    # Create comparison with multiple runs
    print("\n" + "=" * 70)
    print("CREATING WORKFLOW COMPARISON")
    print("=" * 70)
    
    print("\nSimulating 3 different workflow runs...")
    trackers = {
        "Run 1 (Optimized)": create_mock_workflow(),
        "Run 2 (Standard)": create_mock_workflow(),
        "Run 3 (Verbose)": create_mock_workflow()
    }
    
    visualizer.create_comparison_dashboard(
        trackers,
        output_file="outputs/demo_comparison.html"
    )
    
    print("\n✅ Comparison dashboard created: outputs/demo_comparison.html")
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("\n1. Open the HTML files in outputs/ to explore visualizations")
    print("2. Check out examples/langgraph_example.py for real LLM integration")
    print("3. Compare workflows with examples/compare_workflows.py")
    print("4. Integrate cost tracking into your own agents!")
    print()


if __name__ == "__main__":
    main()

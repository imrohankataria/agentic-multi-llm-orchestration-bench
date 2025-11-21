"""
Example: Compare CrewAI and LangGraph workflows
Demonstrates workflow comparison with cost analysis
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.crewai_agents import CrewAIWorkflow, CREWAI_AVAILABLE
from agents.langgraph_agents import LangGraphWorkflow, LANGGRAPH_AVAILABLE
from visualizations.charts import CostVisualizer


def compare_workflows():
    """Compare CrewAI and LangGraph workflows"""
    print("=" * 70)
    print("MULTI-AGENT WORKFLOW COMPARISON: CrewAI vs LangGraph")
    print("=" * 70)
    
    topic = "The Impact of AI on Modern Healthcare"
    workflows = {}
    
    # Run CrewAI workflow if available
    if CREWAI_AVAILABLE:
        print("\n[1/2] Running CrewAI Workflow...")
        print("-" * 70)
        try:
            crewai_workflow = CrewAIWorkflow(model="gpt-4o-mini")
            crewai_result = crewai_workflow.run_workflow(topic)
            workflows['CrewAI'] = crewai_workflow.get_cost_tracker()
            
            print(f"\n✅ CrewAI Workflow Complete")
            print(f"   Cost: ${crewai_result['cost_analysis']['total_cost']:.4f}")
            print(f"   Time: {crewai_result['execution_time_seconds']:.2f}s")
            if crewai_result['cost_warning']:
                print(f"   {crewai_result['cost_warning']}")
        except Exception as e:
            print(f"❌ CrewAI workflow failed: {e}")
    else:
        print("\n⚠️  CrewAI not available. Install with: pip install crewai")
    
    # Run LangGraph workflow if available
    if LANGGRAPH_AVAILABLE:
        print("\n[2/2] Running LangGraph Workflow...")
        print("-" * 70)
        try:
            langgraph_workflow = LangGraphWorkflow(model="gpt-4o-mini")
            langgraph_result = langgraph_workflow.run_workflow(topic)
            workflows['LangGraph'] = langgraph_workflow.get_cost_tracker()
            
            print(f"\n✅ LangGraph Workflow Complete")
            print(f"   Cost: ${langgraph_result['cost_analysis']['total_cost']:.4f}")
            print(f"   Time: {langgraph_result['execution_time_seconds']:.2f}s")
            if langgraph_result['cost_warning']:
                print(f"   {langgraph_result['cost_warning']}")
        except Exception as e:
            print(f"❌ LangGraph workflow failed: {e}")
    else:
        print("\n⚠️  LangGraph not available. Install with: pip install langgraph")
    
    # Create comparison visualizations
    if workflows:
        print("\n" + "=" * 70)
        print("GENERATING COMPARISON VISUALIZATIONS")
        print("=" * 70)
        
        # Create comparison dashboard
        if len(workflows) > 1:
            visualizer = CostVisualizer(list(workflows.values())[0])
            visualizer.create_comparison_dashboard(
                workflows,
                output_file="outputs/workflow_comparison.html"
            )
            
        # Create individual visualizations
        for workflow_name, tracker in workflows.items():
            print(f"\nGenerating visualizations for {workflow_name}...")
            visualizer = CostVisualizer(tracker)
            prefix = f"outputs/{workflow_name.lower()}_"
            
            visualizer.create_agent_timeline(f"{prefix}timeline.html")
            visualizer.create_cost_breakdown_chart(f"{prefix}breakdown.html")
            visualizer.create_event_type_breakdown(f"{prefix}events.html")
            visualizer.generate_cost_report(f"{prefix}report.txt")
            
            # Export JSON
            tracker.export_to_json(f"{prefix}data.json")
        
        print("\n" + "=" * 70)
        print("✅ ALL VISUALIZATIONS GENERATED")
        print("=" * 70)
        print("\nGenerated files in 'outputs/' directory:")
        print("  • workflow_comparison.html - Compare all workflows")
        print("  • <workflow>_timeline.html - Agent activity timeline")
        print("  • <workflow>_breakdown.html - Cost breakdown by agent")
        print("  • <workflow>_events.html - Event type analysis")
        print("  • <workflow>_report.txt - Detailed text report")
        print("  • <workflow>_data.json - Raw cost data")
        
    else:
        print("\n❌ No workflows were successfully executed.")
        print("Please install at least one framework:")
        print("  • CrewAI: pip install crewai langchain-openai")
        print("  • LangGraph: pip install langgraph langchain-openai")


if __name__ == "__main__":
    # Create outputs directory
    os.makedirs("outputs", exist_ok=True)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set in environment")
        print("Set it with: export OPENAI_API_KEY='your-api-key'")
        print("Or create a .env file with OPENAI_API_KEY=your-api-key")
        print()
    
    compare_workflows()

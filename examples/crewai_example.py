"""
Example: CrewAI workflow with cost tracking
Simple example demonstrating CrewAI integration
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.crewai_agents import CrewAIWorkflow
from visualizations.charts import create_all_visualizations


def main():
    """Run CrewAI workflow example"""
    print("=" * 70)
    print("CrewAI Multi-Agent Workflow with Cost Tracking")
    print("=" * 70)
    
    # Create workflow
    workflow = CrewAIWorkflow(model="gpt-4o-mini")
    
    # Run workflow
    topic = "The Impact of AI on Modern Healthcare"
    print(f"\nTopic: {topic}")
    print("-" * 70)
    
    result = workflow.run_workflow(topic)
    
    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\nExecution Time: {result['execution_time_seconds']:.2f} seconds")
    print(f"Total Cost: ${result['cost_analysis']['total_cost']:.4f}")
    
    print(f"\nAgent Cost Breakdown:")
    for agent, cost in result['cost_analysis']['agent_costs'].items():
        print(f"  • {agent}: ${cost:.4f}")
    
    if result['cost_warning']:
        print(f"\n{result['cost_warning']}")
    
    print("\nFinal Article:")
    print("-" * 70)
    print(result['result'][:500] + "..." if len(result['result']) > 500 else result['result'])
    
    # Generate visualizations
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)
    
    os.makedirs("outputs", exist_ok=True)
    create_all_visualizations(
        workflow.get_cost_tracker(),
        prefix="outputs/crewai_example_"
    )


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Error: OPENAI_API_KEY not set")
        print("Set it with: export OPENAI_API_KEY='your-api-key'")
        exit(1)
    
    main()

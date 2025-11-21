"""
CrewAI Integration with Cost Tracking
Implements multi-agent workflow using CrewAI with comprehensive cost tracking.
"""
from typing import List, Optional, Dict, Any
import time
from datetime import datetime

try:
    from crewai import Agent, Task, Crew
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain_openai import ChatOpenAI
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cost_tracker.core import CostTracker


class CostTrackingCallback(BaseCallbackHandler):
    """LangChain callback handler for tracking costs"""
    
    def __init__(self, cost_tracker: CostTracker, agent_name: str):
        self.cost_tracker = cost_tracker
        self.agent_name = agent_name
        self.call_start_time = None
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """Track when LLM call starts"""
        self.call_start_time = time.time()
        
    def on_llm_end(self, response, **kwargs):
        """Track when LLM call ends and calculate cost"""
        duration_ms = (time.time() - self.call_start_time) * 1000 if self.call_start_time else 0
        
        # Extract token usage from response
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            model_name = response.llm_output.get('model_name', 'gpt-3.5-turbo')
            
            input_tokens = token_usage.get('prompt_tokens', 0)
            output_tokens = token_usage.get('completion_tokens', 0)
            
            self.cost_tracker.track_llm_call(
                agent_name=self.agent_name,
                model=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms
            )
            
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        """Track when tool call starts"""
        self.call_start_time = time.time()
        
    def on_tool_end(self, output: str, **kwargs):
        """Track when tool call ends"""
        duration_ms = (time.time() - self.call_start_time) * 1000 if self.call_start_time else 0
        tool_name = kwargs.get('name', 'unknown_tool')
        
        self.cost_tracker.track_tool_call(
            agent_name=self.agent_name,
            tool_name=tool_name,
            duration_ms=duration_ms
        )


class CrewAIWorkflow:
    """Multi-agent workflow implementation using CrewAI with cost tracking"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        if not CREWAI_AVAILABLE:
            raise ImportError(
                "CrewAI is not installed. Install with: pip install crewai langchain-openai"
            )
        
        self.cost_tracker = CostTracker()
        self.model = model
        self.agents = []
        self.tasks = []
        
    def create_research_agent(self) -> Agent:
        """Create a research agent"""
        llm = ChatOpenAI(
            model=self.model,
            callbacks=[CostTrackingCallback(self.cost_tracker, "Researcher")]
        )
        
        agent = Agent(
            role="Research Analyst",
            goal="Conduct thorough research and gather relevant information",
            backstory="You are an expert research analyst with years of experience in data gathering and analysis.",
            llm=llm,
            verbose=True
        )
        
        self.agents.append(agent)
        return agent
        
    def create_writer_agent(self) -> Agent:
        """Create a writer agent"""
        llm = ChatOpenAI(
            model=self.model,
            callbacks=[CostTrackingCallback(self.cost_tracker, "Writer")]
        )
        
        agent = Agent(
            role="Content Writer",
            goal="Create engaging and informative content based on research",
            backstory="You are a skilled content writer who excels at transforming research into compelling narratives.",
            llm=llm,
            verbose=True
        )
        
        self.agents.append(agent)
        return agent
        
    def create_editor_agent(self) -> Agent:
        """Create an editor agent"""
        llm = ChatOpenAI(
            model=self.model,
            callbacks=[CostTrackingCallback(self.cost_tracker, "Editor")]
        )
        
        agent = Agent(
            role="Content Editor",
            goal="Review and refine content for quality and accuracy",
            backstory="You are a meticulous editor with an eye for detail and excellence.",
            llm=llm,
            verbose=True
        )
        
        self.agents.append(agent)
        return agent
        
    def run_workflow(self, topic: str) -> Dict[str, Any]:
        """
        Run the multi-agent workflow with cost tracking
        
        Args:
            topic: The topic to research and write about
            
        Returns:
            Dictionary containing the workflow result and cost analysis
        """
        self.cost_tracker.start_workflow()
        
        # Create agents
        researcher = self.create_research_agent()
        writer = self.create_writer_agent()
        editor = self.create_editor_agent()
        
        # Create tasks
        research_task = Task(
            description=f"Research the topic: {topic}. Gather key facts, statistics, and insights.",
            agent=researcher,
            expected_output="A comprehensive research report with key findings"
        )
        
        writing_task = Task(
            description=f"Based on the research, write an engaging article about {topic}.",
            agent=writer,
            expected_output="A well-written article",
            context=[research_task]
        )
        
        editing_task = Task(
            description="Review and refine the article for clarity, accuracy, and engagement.",
            agent=editor,
            expected_output="A polished final article",
            context=[writing_task]
        )
        
        # Create and run crew
        crew = Crew(
            agents=[researcher, writer, editor],
            tasks=[research_task, writing_task, editing_task],
            verbose=True
        )
        
        # Execute workflow
        start_time = time.time()
        result = crew.kickoff()
        execution_time = time.time() - start_time
        
        self.cost_tracker.end_workflow()
        
        # Get cost analysis
        cost_summary = self.cost_tracker.get_summary()
        cost_spikes = self.cost_tracker.identify_cost_spikes()
        
        return {
            "result": str(result),
            "execution_time_seconds": execution_time,
            "cost_analysis": cost_summary,
            "cost_spikes": cost_spikes,
            "cost_warning": self._generate_cost_warning(cost_spikes)
        }
        
    def _generate_cost_warning(self, cost_spikes: List[str]) -> Optional[str]:
        """Generate a warning message for cost spikes"""
        if not cost_spikes:
            return None
            
        if len(cost_spikes) == 1:
            return f"⚠️ {cost_spikes[0]} is your cost problem!"
        else:
            agents_str = ", ".join(cost_spikes[:-1]) + f" and {cost_spikes[-1]}"
            return f"⚠️ {agents_str} are your cost problems!"
            
    def get_cost_tracker(self) -> CostTracker:
        """Get the cost tracker instance"""
        return self.cost_tracker


def run_example_crewai_workflow():
    """Example function to demonstrate CrewAI workflow with cost tracking"""
    if not CREWAI_AVAILABLE:
        print("CrewAI is not installed. Please install it to run this example.")
        return
        
    print("Starting CrewAI Multi-Agent Workflow with Cost Tracking...")
    print("=" * 60)
    
    # Create workflow
    workflow = CrewAIWorkflow(model="gpt-4o-mini")
    
    # Run workflow
    topic = "The Impact of AI on Modern Healthcare"
    result = workflow.run_workflow(topic)
    
    # Print results
    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)
    print(f"\nExecution Time: {result['execution_time_seconds']:.2f} seconds")
    print(f"Total Cost: ${result['cost_analysis']['total_cost']:.4f}")
    print(f"\nAgent Cost Breakdown:")
    for agent, cost in result['cost_analysis']['agent_costs'].items():
        print(f"  - {agent}: ${cost:.4f}")
        
    if result['cost_warning']:
        print(f"\n{result['cost_warning']}")
        
    print("\nFinal Output:")
    print("-" * 60)
    print(result['result'][:500] + "..." if len(result['result']) > 500 else result['result'])
    
    # Export cost data
    workflow.get_cost_tracker().export_to_json("crewai_cost_report.json")
    print("\n✅ Cost report exported to crewai_cost_report.json")


if __name__ == "__main__":
    run_example_crewai_workflow()

"""
LangGraph Integration with Cost Tracking
Implements multi-agent workflow using LangGraph with comprehensive cost tracking.
"""
from typing import TypedDict, Annotated, List, Dict, Any
import operator
import time

try:
    from langgraph.graph import StateGraph, END
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema import HumanMessage, SystemMessage
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cost_tracker.core import CostTracker


class WorkflowState(TypedDict):
    """State for the multi-agent workflow"""
    topic: str
    research_notes: Annotated[List[str], operator.add]
    draft_content: str
    final_content: str
    messages: Annotated[List[str], operator.add]


class LangGraphWorkflow:
    """Multi-agent workflow implementation using LangGraph with cost tracking"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError(
                "LangGraph is not installed. Install with: pip install langgraph langchain-openai"
            )
        
        self.cost_tracker = CostTracker()
        self.model = model
        self.llm = ChatOpenAI(model=model)
        
    def _track_llm_response(self, agent_name: str, response, start_time: float):
        """Helper to track LLM response costs"""
        duration_ms = (time.time() - start_time) * 1000
        
        # Extract token usage
        if hasattr(response, 'response_metadata'):
            token_usage = response.response_metadata.get('token_usage', {})
            input_tokens = token_usage.get('prompt_tokens', 0)
            output_tokens = token_usage.get('completion_tokens', 0)
            
            self.cost_tracker.track_llm_call(
                agent_name=agent_name,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms
            )
            
    def research_agent(self, state: WorkflowState) -> WorkflowState:
        """Research agent node"""
        step_start = time.time()
        
        prompt = f"""You are a research analyst. Research the topic: {state['topic']}
        
Provide 3-5 key insights, facts, or statistics about this topic.
Format your response as a bulleted list."""

        start_time = time.time()
        response = self.llm.invoke([HumanMessage(content=prompt)])
        self._track_llm_response("Researcher", response, start_time)
        
        state["research_notes"].append(response.content)
        state["messages"].append(f"Researcher completed analysis of {state['topic']}")
        
        # Track agent step
        step_duration = (time.time() - step_start) * 1000
        self.cost_tracker.track_agent_step(
            agent_name="Researcher",
            step_name="research",
            duration_ms=step_duration
        )
        
        return state
        
    def writer_agent(self, state: WorkflowState) -> WorkflowState:
        """Writer agent node"""
        step_start = time.time()
        
        research_summary = "\n".join(state["research_notes"])
        
        prompt = f"""You are a content writer. Based on the following research about {state['topic']}, 
write a concise, engaging article (2-3 paragraphs).

Research Notes:
{research_summary}

Write the article:"""

        start_time = time.time()
        response = self.llm.invoke([HumanMessage(content=prompt)])
        self._track_llm_response("Writer", response, start_time)
        
        state["draft_content"] = response.content
        state["messages"].append("Writer created draft article")
        
        # Track agent step
        step_duration = (time.time() - step_start) * 1000
        self.cost_tracker.track_agent_step(
            agent_name="Writer",
            step_name="write_draft",
            duration_ms=step_duration
        )
        
        return state
        
    def editor_agent(self, state: WorkflowState) -> WorkflowState:
        """Editor agent node"""
        step_start = time.time()
        
        prompt = f"""You are a content editor. Review and refine the following article about {state['topic']}.
Improve clarity, fix any errors, and enhance engagement.

Draft Article:
{state['draft_content']}

Provide the final edited version:"""

        start_time = time.time()
        response = self.llm.invoke([HumanMessage(content=prompt)])
        self._track_llm_response("Editor", response, start_time)
        
        state["final_content"] = response.content
        state["messages"].append("Editor finalized article")
        
        # Track agent step
        step_duration = (time.time() - step_start) * 1000
        self.cost_tracker.track_agent_step(
            agent_name="Editor",
            step_name="edit_final",
            duration_ms=step_duration
        )
        
        return state
        
    def build_graph(self) -> StateGraph:
        """Build the multi-agent workflow graph"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("researcher", self.research_agent)
        workflow.add_node("writer", self.writer_agent)
        workflow.add_node("editor", self.editor_agent)
        
        # Add edges
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "writer")
        workflow.add_edge("writer", "editor")
        workflow.add_edge("editor", END)
        
        return workflow.compile()
        
    def run_workflow(self, topic: str) -> Dict[str, Any]:
        """
        Run the multi-agent workflow with cost tracking
        
        Args:
            topic: The topic to research and write about
            
        Returns:
            Dictionary containing the workflow result and cost analysis
        """
        self.cost_tracker.start_workflow()
        
        # Build and run workflow
        app = self.build_graph()
        
        initial_state = {
            "topic": topic,
            "research_notes": [],
            "draft_content": "",
            "final_content": "",
            "messages": []
        }
        
        start_time = time.time()
        final_state = app.invoke(initial_state)
        execution_time = time.time() - start_time
        
        self.cost_tracker.end_workflow()
        
        # Get cost analysis
        cost_summary = self.cost_tracker.get_summary()
        cost_spikes = self.cost_tracker.identify_cost_spikes()
        
        return {
            "result": final_state["final_content"],
            "execution_time_seconds": execution_time,
            "cost_analysis": cost_summary,
            "cost_spikes": cost_spikes,
            "cost_warning": self._generate_cost_warning(cost_spikes),
            "workflow_messages": final_state["messages"]
        }
        
    def _generate_cost_warning(self, cost_spikes: List[str]):
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


def run_example_langgraph_workflow():
    """Example function to demonstrate LangGraph workflow with cost tracking"""
    if not LANGGRAPH_AVAILABLE:
        print("LangGraph is not installed. Please install it to run this example.")
        return
        
    print("Starting LangGraph Multi-Agent Workflow with Cost Tracking...")
    print("=" * 60)
    
    # Create workflow
    workflow = LangGraphWorkflow(model="gpt-4o-mini")
    
    # Run workflow
    topic = "The Future of Renewable Energy"
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
        
    print("\nWorkflow Messages:")
    for msg in result['workflow_messages']:
        print(f"  • {msg}")
        
    print("\nFinal Output:")
    print("-" * 60)
    print(result['result'])
    
    # Export cost data
    workflow.get_cost_tracker().export_to_json("langgraph_cost_report.json")
    print("\n✅ Cost report exported to langgraph_cost_report.json")


if __name__ == "__main__":
    run_example_langgraph_workflow()

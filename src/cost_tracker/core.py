"""
Cost Tracker Module - Core cost tracking functionality for multi-agent workflows.
Tracks costs at tool, LLM call, and agent step levels.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


# Pricing per 1K tokens (as of 2024)
LLM_PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
}


@dataclass
class CostEvent:
    """Represents a single cost event (LLM call, tool usage, etc.)"""
    timestamp: datetime
    event_type: str  # "llm_call", "tool_call", "agent_step"
    agent_name: str
    model: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "agent_name": self.agent_name,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata
        }


@dataclass
class AgentCostSummary:
    """Summary of costs for a specific agent"""
    agent_name: str
    total_cost: float = 0.0
    total_tokens: int = 0
    num_llm_calls: int = 0
    num_tool_calls: int = 0
    num_steps: int = 0
    events: List[CostEvent] = field(default_factory=list)

    def add_event(self, event: CostEvent):
        """Add a cost event to this agent's summary"""
        self.events.append(event)
        self.total_cost += event.cost
        self.total_tokens += event.input_tokens + event.output_tokens
        
        if event.event_type == "llm_call":
            self.num_llm_calls += 1
        elif event.event_type == "tool_call":
            self.num_tool_calls += 1
        elif event.event_type == "agent_step":
            self.num_steps += 1


class CostTracker:
    """Main cost tracking class for multi-agent workflows"""
    
    def __init__(self):
        self.events: List[CostEvent] = []
        self.agent_summaries: Dict[str, AgentCostSummary] = {}
        self.workflow_start_time: Optional[datetime] = None
        self.workflow_end_time: Optional[datetime] = None
        
    def start_workflow(self):
        """Mark the start of a workflow"""
        self.workflow_start_time = datetime.now()
        self.events = []
        self.agent_summaries = {}
        
    def end_workflow(self):
        """Mark the end of a workflow"""
        self.workflow_end_time = datetime.now()
        
    def track_llm_call(
        self,
        agent_name: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track an LLM API call"""
        # Calculate cost based on model pricing
        pricing = LLM_PRICING.get(model, {"input": 0.0, "output": 0.0})
        cost = (input_tokens / 1000.0 * pricing["input"] + 
                output_tokens / 1000.0 * pricing["output"])
        
        event = CostEvent(
            timestamp=datetime.now(),
            event_type="llm_call",
            agent_name=agent_name,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            duration_ms=duration_ms,
            metadata=metadata or {}
        )
        
        self._add_event(event)
        
    def track_tool_call(
        self,
        agent_name: str,
        tool_name: str,
        duration_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track a tool call"""
        event = CostEvent(
            timestamp=datetime.now(),
            event_type="tool_call",
            agent_name=agent_name,
            duration_ms=duration_ms,
            metadata={"tool_name": tool_name, **(metadata or {})}
        )
        
        self._add_event(event)
        
    def track_agent_step(
        self,
        agent_name: str,
        step_name: str,
        duration_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track an agent step"""
        event = CostEvent(
            timestamp=datetime.now(),
            event_type="agent_step",
            agent_name=agent_name,
            duration_ms=duration_ms,
            metadata={"step_name": step_name, **(metadata or {})}
        )
        
        self._add_event(event)
        
    def _add_event(self, event: CostEvent):
        """Add an event to the tracker"""
        self.events.append(event)
        
        # Update agent summary
        if event.agent_name not in self.agent_summaries:
            self.agent_summaries[event.agent_name] = AgentCostSummary(
                agent_name=event.agent_name
            )
        
        self.agent_summaries[event.agent_name].add_event(event)
        
    def get_total_cost(self) -> float:
        """Get total cost across all agents"""
        return sum(summary.total_cost for summary in self.agent_summaries.values())
    
    def get_agent_costs(self) -> Dict[str, float]:
        """Get cost breakdown by agent"""
        return {
            name: summary.total_cost 
            for name, summary in self.agent_summaries.items()
        }
    
    def identify_cost_spikes(self, threshold: float = 2.0) -> List[str]:
        """
        Identify agents with costs significantly above average.
        Returns list of agent names that are cost problems.
        
        Args:
            threshold: Multiple of average cost to consider a spike (default: 2.0)
        """
        if not self.agent_summaries:
            return []
            
        costs = [s.total_cost for s in self.agent_summaries.values()]
        avg_cost = sum(costs) / len(costs)
        
        spikes = []
        for name, summary in self.agent_summaries.items():
            if summary.total_cost > avg_cost * threshold:
                spikes.append(name)
                
        return spikes
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of costs"""
        duration_seconds = 0.0
        if self.workflow_start_time and self.workflow_end_time:
            duration_seconds = (
                self.workflow_end_time - self.workflow_start_time
            ).total_seconds()
        
        return {
            "total_cost": self.get_total_cost(),
            "total_events": len(self.events),
            "duration_seconds": duration_seconds,
            "agent_costs": self.get_agent_costs(),
            "cost_spikes": self.identify_cost_spikes(),
            "agent_summaries": {
                name: {
                    "total_cost": summary.total_cost,
                    "total_tokens": summary.total_tokens,
                    "num_llm_calls": summary.num_llm_calls,
                    "num_tool_calls": summary.num_tool_calls,
                    "num_steps": summary.num_steps
                }
                for name, summary in self.agent_summaries.items()
            }
        }
    
    def export_to_json(self, filepath: str):
        """Export cost data to JSON file"""
        data = {
            "summary": self.get_summary(),
            "events": [event.to_dict() for event in self.events]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

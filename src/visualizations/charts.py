"""
Visualization Module - Create visual timeline and cost analysis charts
Generates agent timelines with cost overlays, spike detection, and comparison charts.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cost_tracker.core import CostTracker, CostEvent


class CostVisualizer:
    """Create visualizations for cost tracking data"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        
    def create_agent_timeline(self, output_file: str = "agent_timeline.html"):
        """
        Create an interactive timeline showing agent activities with cost overlays
        """
        if not self.cost_tracker.events:
            print("No events to visualize")
            return
            
        # Convert events to DataFrame
        events_data = []
        for event in self.cost_tracker.events:
            events_data.append({
                'timestamp': event.timestamp,
                'agent': event.agent_name,
                'type': event.event_type,
                'cost': event.cost,
                'duration_ms': event.duration_ms,
                'model': event.model or 'N/A',
                'tokens': event.input_tokens + event.output_tokens
            })
            
        df = pd.DataFrame(events_data)
        
        # Create figure with Plotly
        fig = go.Figure()
        
        # Get unique agents
        agents = df['agent'].unique()
        colors = px.colors.qualitative.Set2[:len(agents)]
        
        # Add timeline bars for each agent
        for idx, agent in enumerate(agents):
            agent_events = df[df['agent'] == agent]
            
            # Create timeline bars
            for _, event in agent_events.iterrows():
                hover_text = (
                    f"Agent: {event['agent']}<br>"
                    f"Type: {event['type']}<br>"
                    f"Cost: ${event['cost']:.6f}<br>"
                    f"Duration: {event['duration_ms']:.0f}ms<br>"
                    f"Tokens: {event['tokens']}<br>"
                    f"Model: {event['model']}"
                )
                
                # Size based on cost (minimum size for visibility)
                marker_size = max(10, event['cost'] * 1000)
                
                fig.add_trace(go.Scatter(
                    x=[event['timestamp']],
                    y=[idx],
                    mode='markers',
                    name=agent if _ == 0 else "",
                    showlegend=(_ == 0),
                    marker=dict(
                        size=marker_size,
                        color=colors[idx],
                        line=dict(width=2, color='white'),
                        opacity=0.7
                    ),
                    text=hover_text,
                    hovertemplate='%{text}<extra></extra>'
                ))
                
        # Update layout
        fig.update_layout(
            title={
                'text': 'Agent Timeline with Cost Overlays',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Time',
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(agents))),
                ticktext=agents,
                title='Agent'
            ),
            height=400 + len(agents) * 50,
            hovermode='closest',
            showlegend=True,
            plot_bgcolor='rgba(240,240,240,0.5)'
        )
        
        # Save to file
        fig.write_html(output_file)
        print(f"✅ Agent timeline saved to {output_file}")
        
        return fig
        
    def create_cost_breakdown_chart(self, output_file: str = "cost_breakdown.html"):
        """
        Create a pie chart showing cost breakdown by agent
        """
        agent_costs = self.cost_tracker.get_agent_costs()
        
        if not agent_costs:
            print("No cost data to visualize")
            return
            
        # Identify cost spikes
        cost_spikes = self.cost_tracker.identify_cost_spikes()
        
        # Create colors (red for spikes, blue for normal)
        colors = []
        labels = []
        for agent, cost in agent_costs.items():
            labels.append(agent)
            if agent in cost_spikes:
                colors.append('#ff6b6b')  # Red for problem agents
            else:
                colors.append('#4ecdc4')  # Teal for normal agents
                
        values = list(agent_costs.values())
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            textinfo='label+percent+value',
            texttemplate='%{label}<br>$%{value:.4f}<br>(%{percent})',
            hovertemplate='<b>%{label}</b><br>Cost: $%{value:.6f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        # Add title with cost spike warning
        title_text = 'Cost Breakdown by Agent'
        if cost_spikes:
            spike_text = ', '.join(cost_spikes)
            title_text += f'<br><sub>⚠️ Cost Spikes: {spike_text}</sub>'
            
        fig.update_layout(
            title={
                'text': title_text,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            height=500,
            showlegend=True
        )
        
        fig.write_html(output_file)
        print(f"✅ Cost breakdown chart saved to {output_file}")
        
        return fig
        
    def create_event_type_breakdown(self, output_file: str = "event_type_breakdown.html"):
        """
        Create a stacked bar chart showing event types by agent
        """
        if not self.cost_tracker.events:
            print("No events to visualize")
            return
            
        # Prepare data
        data = []
        for agent_name, summary in self.cost_tracker.agent_summaries.items():
            data.append({
                'Agent': agent_name,
                'LLM Calls': summary.num_llm_calls,
                'Tool Calls': summary.num_tool_calls,
                'Agent Steps': summary.num_steps
            })
            
        df = pd.DataFrame(data)
        
        # Create stacked bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='LLM Calls',
            x=df['Agent'],
            y=df['LLM Calls'],
            marker_color='#4ecdc4'
        ))
        
        fig.add_trace(go.Bar(
            name='Tool Calls',
            x=df['Agent'],
            y=df['Tool Calls'],
            marker_color='#ffa07a'
        ))
        
        fig.add_trace(go.Bar(
            name='Agent Steps',
            x=df['Agent'],
            y=df['Agent Steps'],
            marker_color='#9b59b6'
        ))
        
        fig.update_layout(
            title='Event Types by Agent',
            xaxis_title='Agent',
            yaxis_title='Count',
            barmode='stack',
            height=500
        )
        
        fig.write_html(output_file)
        print(f"✅ Event type breakdown saved to {output_file}")
        
        return fig
        
    def create_comparison_dashboard(
        self,
        trackers: Dict[str, CostTracker],
        output_file: str = "workflow_comparison.html"
    ):
        """
        Create a comparison dashboard for multiple workflow runs
        
        Args:
            trackers: Dictionary mapping workflow names to their cost trackers
            output_file: Output HTML file path
        """
        from plotly.subplots import make_subplots
        
        # Prepare comparison data
        workflow_names = list(trackers.keys())
        total_costs = [tracker.get_total_cost() for tracker in trackers.values()]
        total_events = [len(tracker.events) for tracker in trackers.values()]
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Total Cost Comparison',
                'Total Events Comparison',
                'Agent Cost Distribution',
                'Execution Metrics'
            ),
            specs=[
                [{'type': 'bar'}, {'type': 'bar'}],
                [{'type': 'box'}, {'type': 'table'}]
            ]
        )
        
        # Total cost comparison
        fig.add_trace(
            go.Bar(
                x=workflow_names,
                y=total_costs,
                name='Total Cost',
                marker_color='#4ecdc4',
                text=[f'${c:.4f}' for c in total_costs],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # Total events comparison
        fig.add_trace(
            go.Bar(
                x=workflow_names,
                y=total_events,
                name='Total Events',
                marker_color='#ffa07a',
                text=total_events,
                textposition='auto'
            ),
            row=1, col=2
        )
        
        # Agent cost distribution (box plot)
        for workflow_name, tracker in trackers.items():
            agent_costs = list(tracker.get_agent_costs().values())
            fig.add_trace(
                go.Box(
                    y=agent_costs,
                    name=workflow_name,
                    boxmean='sd'
                ),
                row=2, col=1
            )
            
        # Execution metrics table
        table_data = []
        for workflow_name, tracker in trackers.items():
            summary = tracker.get_summary()
            table_data.append([
                workflow_name,
                f"${summary['total_cost']:.4f}",
                summary['total_events'],
                f"{summary['duration_seconds']:.2f}s",
                len(summary['cost_spikes'])
            ])
            
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Workflow', 'Total Cost', 'Events', 'Duration', 'Spikes'],
                    fill_color='paleturquoise',
                    align='left'
                ),
                cells=dict(
                    values=list(zip(*table_data)) if table_data else [[]],
                    fill_color='lavender',
                    align='left'
                )
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text='Workflow Comparison Dashboard',
            showlegend=False,
            height=800
        )
        
        fig.write_html(output_file)
        print(f"✅ Workflow comparison dashboard saved to {output_file}")
        
        return fig
        
    def generate_cost_report(self, output_file: str = "cost_report.txt"):
        """
        Generate a text-based cost report
        """
        summary = self.cost_tracker.get_summary()
        
        report_lines = [
            "=" * 60,
            "MULTI-AGENT WORKFLOW COST REPORT",
            "=" * 60,
            "",
            f"Total Cost: ${summary['total_cost']:.6f}",
            f"Total Events: {summary['total_events']}",
            f"Duration: {summary['duration_seconds']:.2f} seconds",
            "",
            "Agent Cost Breakdown:",
            "-" * 60
        ]
        
        for agent, cost in summary['agent_costs'].items():
            spike_marker = " ⚠️ COST SPIKE" if agent in summary['cost_spikes'] else ""
            report_lines.append(f"  {agent}: ${cost:.6f}{spike_marker}")
            
            # Add detailed breakdown
            agent_summary = self.cost_tracker.agent_summaries[agent]
            report_lines.append(f"    - LLM Calls: {agent_summary.num_llm_calls}")
            report_lines.append(f"    - Tool Calls: {agent_summary.num_tool_calls}")
            report_lines.append(f"    - Agent Steps: {agent_summary.num_steps}")
            report_lines.append(f"    - Total Tokens: {agent_summary.total_tokens}")
            report_lines.append("")
            
        if summary['cost_spikes']:
            report_lines.extend([
                "",
                "⚠️ COST SPIKE DETECTION:",
                "-" * 60
            ])
            for spike in summary['cost_spikes']:
                report_lines.append(f"  • {spike} is consuming significantly more resources than average")
                
        report = "\n".join(report_lines)
        
        with open(output_file, 'w') as f:
            f.write(report)
            
        print(report)
        print(f"\n✅ Cost report saved to {output_file}")
        
        return report


def create_all_visualizations(cost_tracker: CostTracker, prefix: str = ""):
    """
    Generate all visualizations for a cost tracker
    
    Args:
        cost_tracker: The cost tracker to visualize
        prefix: Prefix for output filenames
    """
    visualizer = CostVisualizer(cost_tracker)
    
    print(f"\nGenerating visualizations with prefix '{prefix}'...")
    
    visualizer.create_agent_timeline(f"{prefix}agent_timeline.html")
    visualizer.create_cost_breakdown_chart(f"{prefix}cost_breakdown.html")
    visualizer.create_event_type_breakdown(f"{prefix}event_type_breakdown.html")
    visualizer.generate_cost_report(f"{prefix}cost_report.txt")
    
    print("\n✅ All visualizations generated successfully!")

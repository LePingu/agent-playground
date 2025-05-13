"""
Visualization functionality for the Source of Wealth Agent system.

This module provides tools to visualize agent interactions, workflow execution,
and performance metrics.
"""

import time
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from IPython.display import display, HTML, Markdown
from typing import Dict, List, Any, Tuple

from source_of_wealth_agent.core.state import AgentState


class AgentInteractionTracer:
    """
    Tracks and visualizes agent interactions during workflow execution.
    """
    
    def __init__(self):
        """Initialize the tracer with empty tracking data."""
        self.interactions = []
        self.agent_activities = {}
        self.start_time = None
    
    def start_tracing(self):
        """Start a new tracing session."""
        self.start_time = time.time()
        self.interactions = []
        self.agent_activities = {}
        print("📊 Tracing agent interactions...")
    
    def record_interaction(self, from_agent: str, to_agent: str, data: Any = None):
        """
        Record an interaction between two agents.
        
        Args:
            from_agent: The agent initiating the interaction
            to_agent: The agent receiving the interaction
            data: Optional data associated with the interaction
        """
        elapsed = time.time() - self.start_time
        self.interactions.append({
            "from": from_agent,
            "to": to_agent,
            "timestamp": elapsed,
            "data": data
        })
        
        # Record activity
        if from_agent not in self.agent_activities:
            self.agent_activities[from_agent] = []
        self.agent_activities[from_agent].append((elapsed, f"Sent to {to_agent}"))
        
        if to_agent not in self.agent_activities:
            self.agent_activities[to_agent] = []
        self.agent_activities[to_agent].append((elapsed, f"Received from {from_agent}"))
    
    def visualize_interactions(self):
        """Generate and display visualizations of agent interactions."""
        if not self.interactions:
            print("No interactions recorded yet.")
            return
        
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes and edges
        node_colors = {}
        edge_counts = {}
        
        for interaction in self.interactions:
            from_agent = interaction['from']
            to_agent = interaction['to']
            
            # Add nodes if they don't exist
            if from_agent not in node_colors:
                node_colors[from_agent] = (np.random.rand(), np.random.rand(), np.random.rand(), 0.8)
            if to_agent not in node_colors:
                node_colors[to_agent] = (np.random.rand(), np.random.rand(), np.random.rand(), 0.8)
            
            # Add edge
            edge_key = (from_agent, to_agent)
            if edge_key not in edge_counts:
                edge_counts[edge_key] = 0
            edge_counts[edge_key] += 1
            
            G.add_edge(from_agent, to_agent, weight=edge_counts[edge_key])
        
        # Set up the figure
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes
        for node, color in node_colors.items():
            nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=[color], node_size=1500, alpha=0.8)
        
        # Draw edges with varying width
        for edge, count in edge_counts.items():
            nx.draw_networkx_edges(G, pos, edgelist=[edge], width=1+count, alpha=0.7, arrows=True, arrowstyle='-|>', arrowsize=20)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
        
        # Draw edge labels (interaction counts)
        edge_labels = {edge: count for edge, count in edge_counts.items()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        plt.axis('off')
        plt.tight_layout()
        plt.title('Agent Interaction Graph', fontsize=16)
        plt.show()
        
        # Display a timeline of agent activities
        plt.figure(figsize=(12, 6))
        colormap = plt.cm.tab20
        agents = list(self.agent_activities.keys())
        
        for i, agent in enumerate(agents):
            activities = self.agent_activities[agent]
            times = [act[0] for act in activities]
            y_pos = [i] * len(activities)
            plt.scatter(times, y_pos, s=100, label=agent, color=colormap(i % 20))
        
        plt.yticks(range(len(agents)), agents)
        plt.xlabel('Time (seconds)')
        plt.title('Agent Activity Timeline')
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
    
    def display_execution_statistics(self):
        """Display statistics about the workflow execution."""
        if not self.interactions:
            print("No interactions recorded yet.")
            return
        
        # Count agent invocations
        agent_invocation_counts = {}
        for interaction in self.interactions:
            to_agent = interaction['to']
            if to_agent not in agent_invocation_counts:
                agent_invocation_counts[to_agent] = 0
            agent_invocation_counts[to_agent] += 1
        
        # Display statistics
        display(HTML("<h3>Agent Execution Statistics</h3>"))
        display(HTML(f"<p>Total execution time: {time.time() - self.start_time:.2f} seconds</p>"))
        display(HTML(f"<p>Total agent interactions: {len(self.interactions)}</p>"))
        
        # Create a bar chart of agent invocations
        plt.figure(figsize=(10, 6))
        agents = list(agent_invocation_counts.keys())
        counts = [agent_invocation_counts[agent] for agent in agents]
        
        bars = plt.bar(agents, counts, color='skyblue')
        
        # Add count labels on bars
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                     str(count), ha='center', va='bottom')
        
        plt.ylabel('Number of Invocations')
        plt.title('Agent Invocation Counts')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
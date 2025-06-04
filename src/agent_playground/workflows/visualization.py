"""Enhanced visualization capabilities for agent workflows."""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import networkx as nx
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from IPython.display import display, HTML
    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False

from ..core.base import BaseWorkflow, BaseState
from ..utils.logging import get_logger


class WorkflowVisualizer:
    """Enhanced workflow visualization with multiple output formats."""
    
    def __init__(self):
        self.logger = get_logger("workflow_visualizer")
        self.execution_data: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
        self.workflow_graph: Optional[nx.DiGraph] = None
    
    def start_recording(self, workflow: BaseWorkflow):
        """Start recording workflow execution."""
        self.start_time = time.time()
        self.execution_data = []
        self.workflow_graph = self._build_workflow_graph(workflow)
        self.logger.info(f"Started recording workflow: {workflow.name}")
    
    def record_step(
        self,
        agent_name: str,
        action: str,
        state: BaseState,
        duration: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a workflow execution step."""
        if self.start_time is None:
            self.logger.warning("Recording not started. Call start_recording() first.")
            return
        
        elapsed = time.time() - self.start_time
        step_data = {
            "timestamp": elapsed,
            "agent_name": agent_name,
            "action": action,
            "duration": duration,
            "state_progress": state.get_progress_percentage() if hasattr(state, 'get_progress_percentage') else 0,
            "completed_steps": len(state.completed_steps) if hasattr(state, 'completed_steps') else 0,
            "metadata": metadata or {}
        }
        
        self.execution_data.append(step_data)
        self.logger.debug(f"Recorded step: {agent_name} - {action}")
    
    def stop_recording(self):
        """Stop recording workflow execution."""
        if self.start_time is None:
            self.logger.warning("Recording not started.")
            return
        
        total_time = time.time() - self.start_time
        self.logger.info(f"Stopped recording. Total execution time: {total_time:.2f}s")
        return total_time
    
    def _build_workflow_graph(self, workflow: BaseWorkflow) -> nx.DiGraph:
        """Build a NetworkX graph representation of the workflow."""
        G = nx.DiGraph()
        
        # For now, create a simple graph based on agents
        # In a real implementation, this would parse the actual workflow structure
        if hasattr(workflow, 'agents'):
            agents = list(workflow.agents.keys()) if isinstance(workflow.agents, dict) else workflow.agents
            for i, agent in enumerate(agents):
                G.add_node(agent)
                if i > 0:
                    G.add_edge(agents[i-1], agent)
        
        return G
    
    def generate_execution_timeline(self, save_path: Optional[str] = None) -> Optional[str]:
        """Generate an execution timeline visualization."""
        if not MATPLOTLIB_AVAILABLE:
            self.logger.warning("Matplotlib not available. Cannot generate timeline.")
            return None
        
        if not self.execution_data:
            self.logger.warning("No execution data recorded.")
            return None
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Timeline plot
        timestamps = [step["timestamp"] for step in self.execution_data]
        agents = [step["agent_name"] for step in self.execution_data]
        durations = [step["duration"] for step in self.execution_data]
        
        # Create color map for agents
        unique_agents = list(set(agents))
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_agents)))
        agent_colors = {agent: colors[i] for i, agent in enumerate(unique_agents)}
        
        # Plot execution timeline
        for i, step in enumerate(self.execution_data):
            ax1.barh(
                i, 
                step["duration"], 
                left=step["timestamp"], 
                color=agent_colors[step["agent_name"]], 
                alpha=0.7,
                label=step["agent_name"] if step["agent_name"] not in [s["agent_name"] for s in self.execution_data[:i]] else ""
            )
            ax1.text(
                step["timestamp"] + step["duration"]/2, 
                i, 
                step["action"][:20] + "..." if len(step["action"]) > 20 else step["action"],
                ha='center', 
                va='center', 
                fontsize=8
            )
        
        ax1.set_xlabel("Time (seconds)")
        ax1.set_ylabel("Execution Steps")
        ax1.set_title("Workflow Execution Timeline")
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Progress over time
        progress_data = [step["state_progress"] for step in self.execution_data]
        ax2.plot(timestamps, progress_data, marker='o', linewidth=2, markersize=4)
        ax2.set_xlabel("Time (seconds)")
        ax2.set_ylabel("Progress (%)")
        ax2.set_title("Workflow Progress Over Time")
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Timeline saved to: {save_path}")
        
        if IPYTHON_AVAILABLE:
            plt.show()
        
        return save_path
    
    def generate_workflow_graph(self, save_path: Optional[str] = None) -> Optional[str]:
        """Generate a workflow graph visualization."""
        if not MATPLOTLIB_AVAILABLE:
            self.logger.warning("Matplotlib not available. Cannot generate graph.")
            return None
        
        if self.workflow_graph is None:
            self.logger.warning("No workflow graph available.")
            return None
        
        plt.figure(figsize=(12, 8))
        
        # Calculate node positions
        pos = nx.spring_layout(self.workflow_graph, k=2, iterations=50)
        
        # Draw nodes
        node_colors = []
        node_sizes = []
        
        for node in self.workflow_graph.nodes():
            # Color based on execution data
            executed = any(step["agent_name"] == node for step in self.execution_data)
            if executed:
                node_colors.append('lightgreen')
                node_sizes.append(1500)
            else:
                node_colors.append('lightblue')
                node_sizes.append(1000)
        
        nx.draw_networkx_nodes(
            self.workflow_graph, 
            pos, 
            node_color=node_colors, 
            node_size=node_sizes,
            alpha=0.8
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            self.workflow_graph, 
            pos, 
            edge_color='gray', 
            arrows=True, 
            arrowstyle='->', 
            arrowsize=20,
            alpha=0.6
        )
        
        # Draw labels
        nx.draw_networkx_labels(
            self.workflow_graph, 
            pos, 
            font_size=10, 
            font_weight='bold'
        )
        
        plt.title("Workflow Graph Structure", fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='lightgreen', label='Executed'),
            Patch(facecolor='lightblue', label='Not Executed')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Graph saved to: {save_path}")
        
        if IPYTHON_AVAILABLE:
            plt.show()
        
        return save_path
    
    def generate_performance_metrics(self) -> Dict[str, Any]:
        """Generate performance metrics from execution data."""
        if not self.execution_data:
            return {}
        
        # Calculate metrics
        total_duration = sum(step["duration"] for step in self.execution_data)
        avg_step_duration = total_duration / len(self.execution_data)
        
        # Agent-specific metrics
        agent_metrics = {}
        for step in self.execution_data:
            agent = step["agent_name"]
            if agent not in agent_metrics:
                agent_metrics[agent] = {
                    "total_duration": 0,
                    "step_count": 0,
                    "actions": []
                }
            
            agent_metrics[agent]["total_duration"] += step["duration"]
            agent_metrics[agent]["step_count"] += 1
            agent_metrics[agent]["actions"].append(step["action"])
        
        # Calculate average duration per agent
        for agent, metrics in agent_metrics.items():
            metrics["avg_duration"] = metrics["total_duration"] / metrics["step_count"]
        
        return {
            "total_execution_time": self.execution_data[-1]["timestamp"] if self.execution_data else 0,
            "total_processing_time": total_duration,
            "average_step_duration": avg_step_duration,
            "total_steps": len(self.execution_data),
            "agent_metrics": agent_metrics,
            "efficiency_ratio": total_duration / self.execution_data[-1]["timestamp"] if self.execution_data else 0
        }
    
    def generate_html_report(self, save_path: str, include_graphs: bool = True) -> str:
        """Generate an HTML report with all visualizations and metrics."""
        metrics = self.generate_performance_metrics()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Workflow Execution Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metric {{ background-color: #e8f4fd; padding: 10px; margin: 10px 0; border-radius: 3px; }}
                .agent-section {{ background-color: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .step {{ margin: 5px 0; padding: 5px; background-color: #ffffff; border-left: 3px solid #007acc; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Workflow Execution Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <h2>Performance Metrics</h2>
            <div class="metric">
                <strong>Total Execution Time:</strong> {metrics.get('total_execution_time', 0):.2f} seconds
            </div>
            <div class="metric">
                <strong>Total Processing Time:</strong> {metrics.get('total_processing_time', 0):.2f} seconds
            </div>
            <div class="metric">
                <strong>Average Step Duration:</strong> {metrics.get('average_step_duration', 0):.2f} seconds
            </div>
            <div class="metric">
                <strong>Total Steps:</strong> {metrics.get('total_steps', 0)}
            </div>
            <div class="metric">
                <strong>Efficiency Ratio:</strong> {metrics.get('efficiency_ratio', 0):.2f}
            </div>
            
            <h2>Agent Performance</h2>
        """
        
        # Add agent metrics
        for agent, agent_data in metrics.get('agent_metrics', {}).items():
            html_content += f"""
            <div class="agent-section">
                <h3>{agent}</h3>
                <p><strong>Total Duration:</strong> {agent_data['total_duration']:.2f}s</p>
                <p><strong>Step Count:</strong> {agent_data['step_count']}</p>
                <p><strong>Average Duration:</strong> {agent_data['avg_duration']:.2f}s</p>
                <p><strong>Actions:</strong> {', '.join(agent_data['actions'])}</p>
            </div>
            """
        
        # Add execution timeline
        html_content += """
            <h2>Execution Timeline</h2>
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>Agent</th>
                    <th>Action</th>
                    <th>Duration</th>
                    <th>Progress</th>
                </tr>
        """
        
        for step in self.execution_data:
            html_content += f"""
                <tr>
                    <td>{step['timestamp']:.2f}s</td>
                    <td>{step['agent_name']}</td>
                    <td>{step['action']}</td>
                    <td>{step['duration']:.2f}s</td>
                    <td>{step['state_progress']:.1f}%</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2>Execution Steps Detail</h2>
        """
        
        for i, step in enumerate(self.execution_data, 1):
            html_content += f"""
            <div class="step">
                <strong>Step {i}:</strong> {step['agent_name']} - {step['action']}<br>
                <small>Time: {step['timestamp']:.2f}s | Duration: {step['duration']:.2f}s | Progress: {step['state_progress']:.1f}%</small>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        # Save HTML report
        Path(save_path).write_text(html_content)
        self.logger.info(f"HTML report saved to: {save_path}")
        
        return save_path
    
    def export_data(self, save_path: str, format: str = "json") -> str:
        """Export execution data in various formats."""
        data = {
            "execution_data": self.execution_data,
            "performance_metrics": self.generate_performance_metrics(),
            "workflow_graph": {
                "nodes": list(self.workflow_graph.nodes()) if self.workflow_graph else [],
                "edges": list(self.workflow_graph.edges()) if self.workflow_graph else []
            }
        }
        
        if format.lower() == "json":
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif format.lower() == "csv":
            import csv
            with open(save_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.execution_data[0].keys() if self.execution_data else [])
                writer.writeheader()
                writer.writerows(self.execution_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Data exported to: {save_path}")
        return save_path


class InteractiveWorkflowVisualizer:
    """Interactive workflow visualizer using web technologies."""
    
    def __init__(self):
        self.logger = get_logger("interactive_visualizer")
    
    def generate_interactive_graph(
        self, 
        workflow: BaseWorkflow, 
        execution_data: List[Dict[str, Any]], 
        save_path: str
    ) -> str:
        """Generate an interactive HTML graph using D3.js or similar."""
        
        # Create a simple interactive visualization
        nodes = []
        links = []
        
        if hasattr(workflow, 'agents'):
            agents = list(workflow.agents.keys()) if isinstance(workflow.agents, dict) else workflow.agents
            
            # Create nodes
            for i, agent in enumerate(agents):
                executed = any(step["agent_name"] == agent for step in execution_data)
                nodes.append({
                    "id": agent,
                    "name": agent,
                    "executed": executed,
                    "group": i % 5  # For coloring
                })
                
                # Create links
                if i > 0:
                    links.append({
                        "source": agents[i-1],
                        "target": agent,
                        "value": 1
                    })
        
        # Generate HTML with embedded JavaScript
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Interactive Workflow Graph</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .node {{ stroke: #fff; stroke-width: 2px; cursor: pointer; }}
                .node.executed {{ fill: #90EE90; }}
                .node.not-executed {{ fill: #87CEEB; }}
                .link {{ stroke: #999; stroke-opacity: 0.6; stroke-width: 2px; }}
                .tooltip {{ 
                    position: absolute; 
                    padding: 10px; 
                    background: rgba(0,0,0,0.8); 
                    color: white; 
                    border-radius: 5px; 
                    pointer-events: none; 
                }}
                #controls {{ margin: 20px; }}
                button {{ margin: 5px; padding: 10px; }}
            </style>
        </head>
        <body>
            <h1>Interactive Workflow Visualization</h1>
            <div id="controls">
                <button onclick="restart()">Restart Animation</button>
                <button onclick="toggleLabels()">Toggle Labels</button>
            </div>
            <svg width="800" height="600"></svg>
            
            <script>
                const nodes = {json.dumps(nodes)};
                const links = {json.dumps(links)};
                
                const svg = d3.select("svg"),
                    width = +svg.attr("width"),
                    height = +svg.attr("height");
                
                const simulation = d3.forceSimulation()
                    .force("link", d3.forceLink().id(d => d.id))
                    .force("charge", d3.forceManyBody().strength(-300))
                    .force("center", d3.forceCenter(width / 2, height / 2));
                
                const link = svg.append("g")
                    .attr("class", "links")
                    .selectAll("line")
                    .data(links)
                    .enter().append("line")
                    .attr("class", "link");
                
                const node = svg.append("g")
                    .attr("class", "nodes")
                    .selectAll("circle")
                    .data(nodes)
                    .enter().append("circle")
                    .attr("class", d => "node " + (d.executed ? "executed" : "not-executed"))
                    .attr("r", 20)
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));
                
                const labels = svg.append("g")
                    .attr("class", "labels")
                    .selectAll("text")
                    .data(nodes)
                    .enter().append("text")
                    .text(d => d.name)
                    .attr("font-size", "12px")
                    .attr("text-anchor", "middle")
                    .attr("dy", ".35em");
                
                // Tooltip
                const tooltip = d3.select("body").append("div")
                    .attr("class", "tooltip")
                    .style("opacity", 0);
                
                node.on("mouseover", function(event, d) {{
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", .9);
                    tooltip.html("Agent: " + d.name + "<br/>Status: " + (d.executed ? "Executed" : "Not Executed"))
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                }})
                .on("mouseout", function(d) {{
                    tooltip.transition()
                        .duration(500)
                        .style("opacity", 0);
                }});
                
                simulation
                    .nodes(nodes)
                    .on("tick", ticked);
                
                simulation.force("link")
                    .links(links);
                
                function ticked() {{
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                    
                    node
                        .attr("cx", d => d.x)
                        .attr("cy", d => d.y);
                    
                    labels
                        .attr("x", d => d.x)
                        .attr("y", d => d.y);
                }}
                
                function dragstarted(event, d) {{
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }}
                
                function dragged(event, d) {{
                    d.fx = event.x;
                    d.fy = event.y;
                }}
                
                function dragended(event, d) {{
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }}
                
                function restart() {{
                    simulation.alpha(1).restart();
                }}
                
                function toggleLabels() {{
                    const labelsVisible = labels.style("opacity") !== "0";
                    labels.style("opacity", labelsVisible ? "0" : "1");
                }}
            </script>
        </body>
        </html>
        """
        
        Path(save_path).write_text(html_content)
        self.logger.info(f"Interactive graph saved to: {save_path}")
        
        return save_path

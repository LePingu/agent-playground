"""Workflow monitoring and execution management."""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable, Union
from enum import Enum
from datetime import datetime
from pathlib import Path

from ..core.base import BaseWorkflow, BaseState, BaseAgent
from ..utils.logging import get_logger
from .visualization import WorkflowVisualizer, InteractiveWorkflowVisualizer


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ExecutionMetrics:
    """Container for workflow execution metrics."""
    
    def __init__(self):
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.total_duration: float = 0.0
        self.agent_durations: Dict[str, float] = {}
        self.step_count: int = 0
        self.error_count: int = 0
        self.success_count: int = 0
        self.agent_executions: Dict[str, int] = {}
    
    def add_step(self, agent_name: str, duration: float, success: bool = True):
        """Add a step to the metrics."""
        self.step_count += 1
        if agent_name not in self.agent_durations:
            self.agent_durations[agent_name] = 0.0
            self.agent_executions[agent_name] = 0
        
        self.agent_durations[agent_name] += duration
        self.agent_executions[agent_name] += 1
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of execution metrics."""
        total_time = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0.0
        
        return {
            "total_execution_time": total_time,
            "total_processing_time": self.total_duration,
            "step_count": self.step_count,
            "success_rate": self.success_count / self.step_count if self.step_count > 0 else 0.0,
            "error_count": self.error_count,
            "agent_performance": {
                agent: {
                    "total_duration": self.agent_durations.get(agent, 0.0),
                    "execution_count": self.agent_executions.get(agent, 0),
                    "avg_duration": self.agent_durations.get(agent, 0.0) / self.agent_executions.get(agent, 1)
                }
                for agent in self.agent_durations.keys()
            }
        }


class WorkflowMonitor:
    """Monitor workflow execution with real-time updates."""
    
    def __init__(self, workflow: BaseWorkflow):
        self.workflow = workflow
        self.logger = get_logger(f"monitor_{workflow.name}")
        self.status = WorkflowStatus.PENDING
        self.metrics = ExecutionMetrics()
        self.visualizer = WorkflowVisualizer()
        self.interactive_visualizer = InteractiveWorkflowVisualizer()
        
        # Event callbacks
        self.on_start_callbacks: List[Callable] = []
        self.on_step_callbacks: List[Callable] = []
        self.on_complete_callbacks: List[Callable] = []
        self.on_error_callbacks: List[Callable] = []
        
        # Current execution state
        self.current_state: Optional[BaseState] = None
        self.current_agent: Optional[str] = None
        self.execution_log: List[Dict[str, Any]] = []
    
    def add_callback(self, event: str, callback: Callable):
        """Add a callback for workflow events."""
        if event == "start":
            self.on_start_callbacks.append(callback)
        elif event == "step":
            self.on_step_callbacks.append(callback)
        elif event == "complete":
            self.on_complete_callbacks.append(callback)
        elif event == "error":
            self.on_error_callbacks.append(callback)
        else:
            self.logger.warning(f"Unknown event type: {event}")
    
    def start_monitoring(self, state: BaseState):
        """Start monitoring workflow execution."""
        self.status = WorkflowStatus.RUNNING
        self.metrics.start_time = datetime.now()
        self.current_state = state
        self.visualizer.start_recording(self.workflow)
        
        # Trigger start callbacks
        for callback in self.on_start_callbacks:
            try:
                callback(self.workflow, state)
            except Exception as e:
                self.logger.error(f"Error in start callback: {e}")
        
        self.logger.info(f"Started monitoring workflow: {self.workflow.name}")
    
    def record_step(
        self, 
        agent_name: str, 
        action: str, 
        duration: float, 
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a workflow step."""
        self.current_agent = agent_name
        self.metrics.add_step(agent_name, duration, success)
        
        # Log the step
        step_log = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "duration": duration,
            "success": success,
            "metadata": metadata or {}
        }
        self.execution_log.append(step_log)
        
        # Record in visualizer
        if self.current_state:
            self.visualizer.record_step(agent_name, action, self.current_state, duration, metadata)
        
        # Trigger step callbacks
        for callback in self.on_step_callbacks:
            try:
                callback(agent_name, action, self.current_state, duration, success)
            except Exception as e:
                self.logger.error(f"Error in step callback: {e}")
        
        self.logger.debug(f"Recorded step: {agent_name} - {action} ({duration:.2f}s)")
    
    def complete_monitoring(self, final_state: BaseState):
        """Complete monitoring workflow execution."""
        self.status = WorkflowStatus.COMPLETED
        self.metrics.end_time = datetime.now()
        self.current_state = final_state
        
        total_time = self.visualizer.stop_recording()
        
        # Trigger complete callbacks
        for callback in self.on_complete_callbacks:
            try:
                callback(self.workflow, final_state, self.metrics)
            except Exception as e:
                self.logger.error(f"Error in complete callback: {e}")
        
        self.logger.info(f"Completed monitoring workflow: {self.workflow.name} ({total_time:.2f}s)")
    
    def handle_error(self, error: Exception, agent_name: Optional[str] = None):
        """Handle workflow execution error."""
        self.status = WorkflowStatus.FAILED
        
        error_log = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name or "unknown",
            "error": str(error),
            "error_type": type(error).__name__
        }
        self.execution_log.append(error_log)
        
        # Trigger error callbacks
        for callback in self.on_error_callbacks:
            try:
                callback(error, agent_name, self.current_state)
            except Exception as e:
                self.logger.error(f"Error in error callback: {e}")
        
        self.logger.error(f"Workflow error in {agent_name}: {error}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            "workflow_name": self.workflow.name,
            "status": self.status.value,
            "current_agent": self.current_agent,
            "metrics": self.metrics.get_summary(),
            "execution_log": self.execution_log[-10:],  # Last 10 entries
            "progress": self.current_state.get_progress_percentage() if self.current_state and hasattr(self.current_state, 'get_progress_percentage') else 0
        }
    
    def generate_report(self, output_dir: str = "workflow_reports") -> Dict[str, str]:
        """Generate comprehensive execution report."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workflow_name = self.workflow.name.replace(" ", "_")
        
        reports = {}
        
        # Generate timeline visualization
        timeline_path = output_path / f"{workflow_name}_timeline_{timestamp}.png"
        if self.visualizer.generate_execution_timeline(str(timeline_path)):
            reports["timeline"] = str(timeline_path)
        
        # Generate workflow graph
        graph_path = output_path / f"{workflow_name}_graph_{timestamp}.png"
        if self.visualizer.generate_workflow_graph(str(graph_path)):
            reports["graph"] = str(graph_path)
        
        # Generate HTML report
        html_path = output_path / f"{workflow_name}_report_{timestamp}.html"
        reports["html_report"] = self.visualizer.generate_html_report(str(html_path))
        
        # Generate interactive visualization
        interactive_path = output_path / f"{workflow_name}_interactive_{timestamp}.html"
        reports["interactive"] = self.interactive_visualizer.generate_interactive_graph(
            self.workflow,
            self.visualizer.execution_data,
            str(interactive_path)
        )
        
        # Export execution data
        data_path = output_path / f"{workflow_name}_data_{timestamp}.json"
        reports["data"] = self.visualizer.export_data(str(data_path))
        
        self.logger.info(f"Generated workflow report in: {output_path}")
        return reports


class WorkflowExecutor:
    """Execute workflows with monitoring and error handling."""
    
    def __init__(self):
        self.logger = get_logger("workflow_executor")
        self.active_monitors: Dict[str, WorkflowMonitor] = {}
    
    async def execute_workflow(
        self,
        workflow: BaseWorkflow,
        initial_state: BaseState,
        monitor: bool = True,
        generate_report: bool = True,
        output_dir: str = "workflow_reports"
    ) -> tuple[BaseState, Optional[WorkflowMonitor]]:
        """Execute a workflow with optional monitoring."""
        
        workflow_monitor = None
        if monitor:
            workflow_monitor = WorkflowMonitor(workflow)
            self.active_monitors[workflow.name] = workflow_monitor
            workflow_monitor.start_monitoring(initial_state)
        
        try:
            # Execute the workflow
            # Note: This is a simplified example. In reality, you'd integrate with
            # your actual workflow execution engine (like LangGraph)
            final_state = await self._execute_workflow_steps(workflow, initial_state, workflow_monitor)
            
            if workflow_monitor:
                workflow_monitor.complete_monitoring(final_state)
                
                if generate_report:
                    reports = workflow_monitor.generate_report(output_dir)
                    self.logger.info(f"Generated reports: {list(reports.keys())}")
            
            return final_state, workflow_monitor
            
        except Exception as e:
            if workflow_monitor:
                workflow_monitor.handle_error(e)
            raise
        finally:
            if workflow.name in self.active_monitors:
                del self.active_monitors[workflow.name]
    
    async def _execute_workflow_steps(
        self,
        workflow: BaseWorkflow,
        state: BaseState,
        monitor: Optional[WorkflowMonitor] = None
    ) -> BaseState:
        """Execute workflow steps with monitoring."""
        
        # This is a simplified execution model
        # In a real implementation, this would integrate with LangGraph or similar
        
        if hasattr(workflow, 'agents'):
            agents = workflow.agents
            if isinstance(agents, dict):
                agents = list(agents.values())
            
            for agent in agents:
                if isinstance(agent, BaseAgent):
                    start_time = time.time()
                    
                    try:
                        # Execute agent
                        state = await agent.process(state)
                        duration = time.time() - start_time
                        
                        if monitor:
                            monitor.record_step(
                                agent.name,
                                f"Processed {agent.description}",
                                duration,
                                success=True
                            )
                        
                    except Exception as e:
                        duration = time.time() - start_time
                        
                        if monitor:
                            monitor.record_step(
                                agent.name,
                                f"Failed: {str(e)}",
                                duration,
                                success=False
                            )
                        raise
        
        return state
    
    def get_active_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active workflows."""
        return {
            name: monitor.get_current_status()
            for name, monitor in self.active_monitors.items()
        }
    
    def cancel_workflow(self, workflow_name: str) -> bool:
        """Cancel an active workflow."""
        if workflow_name in self.active_monitors:
            monitor = self.active_monitors[workflow_name]
            monitor.status = WorkflowStatus.CANCELLED
            self.logger.info(f"Cancelled workflow: {workflow_name}")
            return True
        return False


class WorkflowScheduler:
    """Schedule and manage workflow executions."""
    
    def __init__(self):
        self.logger = get_logger("workflow_scheduler")
        self.executor = WorkflowExecutor()
        self.scheduled_workflows: List[Dict[str, Any]] = []
        self.running = False
    
    def schedule_workflow(
        self,
        workflow: BaseWorkflow,
        initial_state: BaseState,
        schedule_time: Optional[datetime] = None,
        recurring: bool = False,
        interval_minutes: int = 60
    ) -> str:
        """Schedule a workflow for execution."""
        
        schedule_id = f"{workflow.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        scheduled_workflow = {
            "id": schedule_id,
            "workflow": workflow,
            "initial_state": initial_state,
            "schedule_time": schedule_time or datetime.now(),
            "recurring": recurring,
            "interval_minutes": interval_minutes,
            "last_execution": None,
            "execution_count": 0
        }
        
        self.scheduled_workflows.append(scheduled_workflow)
        self.logger.info(f"Scheduled workflow: {schedule_id}")
        
        return schedule_id
    
    async def start_scheduler(self):
        """Start the workflow scheduler."""
        self.running = True
        self.logger.info("Started workflow scheduler")
        
        while self.running:
            try:
                await self._check_and_execute_scheduled_workflows()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in scheduler: {e}")
                await asyncio.sleep(60)
    
    def stop_scheduler(self):
        """Stop the workflow scheduler."""
        self.running = False
        self.logger.info("Stopped workflow scheduler")
    
    async def _check_and_execute_scheduled_workflows(self):
        """Check and execute scheduled workflows."""
        current_time = datetime.now()
        
        for scheduled in self.scheduled_workflows[:]:  # Copy list to avoid modification issues
            should_execute = False
            
            # Check if it's time to execute
            if scheduled["last_execution"] is None:
                # First execution
                should_execute = current_time >= scheduled["schedule_time"]
            elif scheduled["recurring"]:
                # Recurring execution
                time_since_last = current_time - scheduled["last_execution"]
                should_execute = time_since_last.total_seconds() >= (scheduled["interval_minutes"] * 60)
            
            if should_execute:
                try:
                    self.logger.info(f"Executing scheduled workflow: {scheduled['id']}")
                    
                    await self.executor.execute_workflow(
                        scheduled["workflow"],
                        scheduled["initial_state"]
                    )
                    
                    scheduled["last_execution"] = current_time
                    scheduled["execution_count"] += 1
                    
                    # Remove non-recurring workflows after execution
                    if not scheduled["recurring"]:
                        self.scheduled_workflows.remove(scheduled)
                        
                except Exception as e:
                    self.logger.error(f"Error executing scheduled workflow {scheduled['id']}: {e}")
    
    def get_scheduled_workflows(self) -> List[Dict[str, Any]]:
        """Get list of scheduled workflows."""
        return [
            {
                "id": scheduled["id"],
                "workflow_name": scheduled["workflow"].name,
                "schedule_time": scheduled["schedule_time"].isoformat(),
                "recurring": scheduled["recurring"],
                "interval_minutes": scheduled["interval_minutes"],
                "last_execution": scheduled["last_execution"].isoformat() if scheduled["last_execution"] else None,
                "execution_count": scheduled["execution_count"]
            }
            for scheduled in self.scheduled_workflows
        ]
    
    def cancel_scheduled_workflow(self, schedule_id: str) -> bool:
        """Cancel a scheduled workflow."""
        for scheduled in self.scheduled_workflows:
            if scheduled["id"] == schedule_id:
                self.scheduled_workflows.remove(scheduled)
                self.logger.info(f"Cancelled scheduled workflow: {schedule_id}")
                return True
        return False

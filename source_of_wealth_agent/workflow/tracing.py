"""
Tracing functionality for the Source of Wealth Agent system.

This module provides tools to trace and log agent interactions and execution
paths during workflow execution.
"""

from typing import Any, Dict, Callable
from functools import wraps

from source_of_wealth_agent.core.state import AgentState, log_action
from source_of_wealth_agent.workflow.visualization import AgentInteractionTracer


# Create a global tracer instance
tracer = AgentInteractionTracer()


def trace_agent_call(agent_function: Callable, agent_name: str) -> Callable:
    """
    Wrap an agent function to trace its execution.
    
    Args:
        agent_function: The original agent function to wrap
        agent_name: The name of the agent
        
    Returns:
        A wrapped function that traces execution
    """
    @wraps(agent_function)
    def wrapper(state: AgentState) -> AgentState:
        # Determine the calling agent from the audit log
        calling_agent = "Start"
        if state.get("audit_log") and len(state["audit_log"]) > 0:
            calling_agent = state["audit_log"][-1]["agent"]
        
        # Record the interaction
        tracer.record_interaction(calling_agent, agent_name, None)
        
        # Execute the actual agent function
        print(f"⏳ Executing {agent_name}...")
        result = agent_function(state)
        print(f"✅ {agent_name} completed")
        
        return result
    
    return wrapper


def create_traceable_workflow(workflow_factory: Callable, *args, **kwargs) -> Callable:
    """
    Create a traceable version of a workflow.
    
    Args:
        workflow_factory: A function that creates a workflow
        *args: Arguments to pass to the workflow factory
        **kwargs: Keyword arguments to pass to the workflow factory
        
    Returns:
        A function that creates a traceable workflow
    """
    def create_wrapped_workflow():
        # Create the workflow graph from the factory
        workflow = workflow_factory(*args, **kwargs)
        
        # Return the workflow
        return workflow
    
    return create_wrapped_workflow
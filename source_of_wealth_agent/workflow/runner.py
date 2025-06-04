"""
Runner functionality for the Source of Wealth Agent system.

This module provides functionality to execute workflows and handle results.
It now includes support for LangGraph's Interrupt pattern for human-in-the-loop functionality.
"""

import json
import os
import logging
from typing import Optional, Dict, Any

from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langgraph.types import Command

from source_of_wealth_agent.agents.id_verification_agent import IDVerificationAgent
from source_of_wealth_agent.agents.payslip_verification_agent import PayslipVerificationAgent
from source_of_wealth_agent.agents.web_references_agent import WebReferencesAgent
from source_of_wealth_agent.agents.financial_reports_agent import FinancialReportsAgent
from source_of_wealth_agent.core.mocked_model import MockedOllamaLLM, get_mocked_financial_reports_model, get_mocked_id_verification_model, get_mocked_payslips_model, get_mocked_web_references_model
from source_of_wealth_agent.core.state import AgentState, create_initial_state
from source_of_wealth_agent.workflow.orchestration import create_workflow
from source_of_wealth_agent.workflow.tracing import tracer

# Setup logger for runner
logger = logging.getLogger("workflow_runner")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Global variables to track workflow and thread
_current_workflow = None
_current_thread_id = None
_output_file = "output_state.json"

def set_output_file(filename: str):
    """Set the output file for state saving."""
    global _output_file
    _output_file = filename
    logger.info(f"Output file set to: {_output_file}")

async def run_workflow(client_id: str, client_name: Optional[str] = None, traceable: bool = False, openrouter_model: ChatOpenAI = None, 
                 ollama_model: OllamaLLM = None, initial_state: Optional[AgentState] = None) -> AgentState:
    """
    Run the source of wealth verification workflow for a client.
    
    Args:
        client_id: The unique identifier for the client
        client_name: The name of the client (optional)
        traceable: Whether to enable tracing for visualization
        openrouter_model: OpenRouter model instance
        ollama_model: Ollama model instance
        initial_state: Optional initial state to use
        
    Returns:
        The final workflow state
    """
    print(f"🚀 Starting source of wealth verification for client: {client_id}")
    
    global _current_workflow, _current_thread_id

    mocked_id_model = get_mocked_id_verification_model("12345", "Hatim Nourbay")
    mocked_payslip_model = get_mocked_payslips_model("12345", "Hatim Nourbay")
    mocked_financial_model = get_mocked_financial_reports_model("12345", "Hatim Nourbay")
    mocked_web_model = get_mocked_web_references_model("12345", "Hatim Nourbay")

    # Initialize agents
    id_agent = IDVerificationAgent(model=mocked_id_model)  # Uses local model for sensitive ID data
    payslip_agent = PayslipVerificationAgent(model=mocked_payslip_model)  # Uses local model for sensitive financial data
    web_agent = WebReferencesAgent(model=mocked_web_model)  # Uses OpenRouter for web searches
    financial_agent = FinancialReportsAgent(model=mocked_financial_model)  # Uses OpenRouter for financial analysis
    
    # Initialize state
    if initial_state is not None:
        # Use provided state but ensure client_id and client_name are set
        state = initial_state
        if "client_id" not in state:
            state["client_id"] = client_id
        if "client_name" not in state and client_name:
            state["client_name"] = client_name
        print(f"🔄 Continuing workflow with imported state")
    else:
        # Create a fresh state
        state = create_initial_state(client_id, client_name)
    
    if traceable:
        # Start tracing if requested
        tracer.start_tracing()
        
    # Create and compile the workflow with tracing
    _current_workflow = create_workflow(
        id_agent, 
        payslip_agent,
        web_agent,
        financial_agent
    )
    
    # Set default thread ID
    _current_thread_id = f"client_{client_id}"
    
    try:
        # Configure with thread_id for checkpointing
        config = {"configurable": {"thread_id": _current_thread_id}}
        
        # Properly await the async result
        result = await _current_workflow.ainvoke(state, config=config)
        print(f"✅ Workflow completed for client: {client_id}")
        
        # Save final state
        save_graph_state(_output_file, result)
        
        if traceable:
            # Check if tracer has these methods before calling them
            if hasattr(tracer, 'stop_tracing'):
                tracer.stop_tracing()
            if hasattr(tracer, 'visualize_interactions'):
                tracer.visualize_interactions()
            if hasattr(tracer, 'display_execution_statistics'):
                tracer.display_execution_statistics()
        return result
        
    except Exception as e:
        logger.error(f"Error in workflow execution: {str(e)}")
        return state

def run_workflow_with_thread(thread_id: str, state: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run the workflow with a specific thread ID, allowing for continuations and interrupts.
    
    Args:
        thread_id: Thread ID for the workflow
        state: Optional state to start with
        
    Returns:
        Updated state
    """
    global _current_workflow, _current_thread_id
    
    if _current_workflow is None:
        raise ValueError("No workflow has been initialized. Call run_workflow first.")
    
    _current_thread_id = thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        if state is None:
            # Start a new execution with empty state
            result = _current_workflow.invoke({}, config=config)
        else:
            # Continue with provided state
            result = _current_workflow.invoke(state, config=config)
            
        return result
    except Exception as e:
        logger.error(f"Error running workflow step: {str(e)}")
        if state:
            return state
        return {}

def run_workflow_step(thread_id: str, state: Dict[str, Any] = None, resume_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run a single step of the workflow, handling interrupts if needed.
    
    Args:
        thread_id: Thread ID for the workflow
        state: Optional state to use (not needed for resume)
        resume_data: Data to resume an interrupt with
        
    Returns:
        Updated state
    """
    global _current_workflow, _current_thread_id
    
    if _current_workflow is None:
        raise ValueError("No workflow has been initialized. Call run_workflow first.")
    
    _current_thread_id = thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        if resume_data:
            # Resume from interrupt with the provided data
            logger.info(f"Resuming workflow from interrupt with data: {resume_data}")
            result = _current_workflow.invoke(Command(resume=resume_data), config=config)
            return result
        elif state:
            # Continue with provided state
            result = _current_workflow.invoke(state, config=config)
            return result
        else:
            # Start new workflow
            result = _current_workflow.invoke({}, config=config)
            return result
    except Exception as e:
        logger.error(f"Error running workflow step: {str(e)}")
        if state:
            return state
        return {}

def load_graph_state(state_file: str) -> Dict[str, Any]:
    """
    Load graph state from a JSON file.
    
    Args:
        state_file: Path to the state file
        
    Returns:
        Loaded state as dictionary
    """
    if not os.path.exists(state_file):
        logger.warning(f"State file {state_file} not found.")
        return {}
        
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        logger.info(f"Loaded state from {state_file}")
        return state
    except Exception as e:
        logger.error(f"Error loading state file: {str(e)}")
        return {}

def save_graph_state(state_file: str, state: Dict[str, Any]) -> bool:
    """
    Save graph state to a JSON file.
    
    Args:
        state_file: Path to save the state file
        state: State to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        logger.info(f"Saved state to {state_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving state file: {str(e)}")
        return False

def apply_state_update(base_state: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply an update to a base state.
    
    Args:
        base_state: The base state to update
        update: The update to apply
        
    Returns:
        Updated state
    """
    if not update:
        return base_state
        
    result = base_state.copy()
    
    # Handle special keys that should replace rather than merge
    replace_keys = ["next_verification", "next_agent"]
    
    for key, value in update.items():
        if key in replace_keys:
            # For these keys, we just replace the value
            result[key] = value
        elif isinstance(value, dict) and key in result and isinstance(result[key], dict):
            # For nested dictionaries, recursively merge
            result[key] = apply_state_update(result[key], value)
        elif isinstance(value, list) and key in result and isinstance(result[key], list):
            # For lists, append new items
            result[key].extend(value)
        else:
            # For everything else, just replace
            result[key] = value
    
    return result

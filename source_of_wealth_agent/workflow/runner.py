"""
Runner functionality for the Source of Wealth Agent system.

This module provides functionality to execute workflows and handle results.
"""

from typing import Optional, Dict, Any

from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

from source_of_wealth_agent.agents.id_verification_agent import IDVerificationAgent
from source_of_wealth_agent.agents.payslip_verification_agent import PayslipVerificationAgent
from source_of_wealth_agent.agents.web_references_agent import WebReferencesAgent
from source_of_wealth_agent.agents.financial_reports_agent import FinancialReportsAgent
from source_of_wealth_agent.core.state import AgentState, create_initial_state
from source_of_wealth_agent.workflow.orchestration import create_workflow
from source_of_wealth_agent.workflow.tracing import trace_agent_call, tracer


def create_traceable_workflow(
    id_agent: IDVerificationAgent,
    payslip_agent: PayslipVerificationAgent,
    web_agent: WebReferencesAgent,
    financial_agent: FinancialReportsAgent = None
):
    """
    Create a workflow with tracing enabled for all agents.
    
    Args:
        id_agent: ID verification agent instance
        payslip_agent: Payslip verification agent instance
        web_agent: Web references agent instance
        financial_agent: Financial reports agent instance (optional)
        
    Returns:
        A compiled workflow graph with tracing enabled
    """
    from source_of_wealth_agent.agents.risk_assessment_agent import risk_assessment_agent
    from source_of_wealth_agent.agents.report_generation_agent import report_generation_agent
    from source_of_wealth_agent.agents.summarization_agent import summarization_agent
    from source_of_wealth_agent.workflow.orchestration import StateGraph, END
    
    # Build the workflow graph
    workflow = StateGraph(AgentState)
    
    # Add all agent nodes with tracing
    workflow.add_node("id_verification_node", trace_agent_call(id_agent.run, "ID Verification Agent"))
    workflow.add_node("payslip_verification_node", trace_agent_call(payslip_agent.run, "Payslip Verification Agent"))
    workflow.add_node("web_references_node", trace_agent_call(web_agent.run, "Web References Agent"))
    workflow.add_node("summarization_node", trace_agent_call(summarization_agent, "Summarization Agent"))
    workflow.add_node("risk_assessment_node", trace_agent_call(risk_assessment_agent, "Risk Assessment Agent"))
    workflow.add_node("report_generation_node", trace_agent_call(report_generation_agent, "Report Generation Agent"))
    
    # Define the workflow edges - add an entrypoint from START to the first node
    workflow.add_edge("__start__", "id_verification_node")
    
    # Basic verification flow
    workflow.add_edge("id_verification_node", "payslip_verification_node")
    workflow.add_edge("payslip_verification_node", "web_references_node")
    
    # Summarization to collate all verification data
    workflow.add_edge("web_references_node", "summarization_node")
    
    # Risk assessment based on summarized data
    workflow.add_edge("summarization_node", "risk_assessment_node")
    
    # Generate final report
    workflow.add_edge("risk_assessment_node", "report_generation_node")
    workflow.add_edge("report_generation_node", END)
    
    # Compile the workflow
    return workflow.compile()


def run_workflow(client_id: str, client_name: Optional[str] = None, traceable: bool = False, openrouter_model: ChatOpenAI = None, 
                 ollama_model: OllamaLLM = None, **agent_kwargs) -> AgentState:
    """
    Run the source of wealth verification workflow for a client.
    
    Args:
        client_id: The unique identifier for the client
        client_name: The name of the client (optional)
        traceable: Whether to enable tracing for visualization
        **agent_kwargs: Additional kwargs to pass to agent initialization
        
    Returns:
        The final workflow state
    """
    print(f"🚀 Starting source of wealth verification for client: {client_id}")
    
    # Initialize agents
    id_agent = IDVerificationAgent(model=ollama_model)  # Uses local model for sensitive ID data
    payslip_agent = PayslipVerificationAgent(model=ollama_model)  # Uses local model for sensitive financial data
    web_agent = WebReferencesAgent(model=openrouter_model)  # Uses OpenRouter for web searches
    financial_agent = FinancialReportsAgent(model=openrouter_model)  # Uses OpenRouter for financial analysis
    
    # Initialize state
    initial_state = create_initial_state(client_id, client_name)
    
    if traceable:
        # Start tracing if requested
        tracer.start_tracing()
        
        # Create and compile the workflow with tracing
        graph = create_traceable_workflow(
            id_agent, 
            payslip_agent,
            web_agent,
            financial_agent
        )
    else:
        # Create and compile the normal workflow
        graph = create_workflow(
            id_agent, 
            payslip_agent,
            web_agent,
            financial_agent
        )
    
    try:
        result = graph.invoke(initial_state)
        print(f"✅ Workflow completed for client: {client_id}")
        return result
    except Exception as e:
        print(f"❌ Error in workflow execution: {str(e)}")
        return initial_state
    

def run_traceable_workflow(client_id: str, client_name: Optional[str] = None, 
                           openrouter_model=None, ollama_model=None) -> AgentState:
    """
    Run a workflow with tracing enabled for visualization.
    
    Args:
        client_id: The unique identifier for the client
        client_name: The name of the client (optional)
        
    Returns:
        The final workflow state
    """
    result = run_workflow(client_id, client_name, traceable=True, openrouter_model=openrouter_model, ollama_model=ollama_model)
    
    # Visualize the interactions after completion
    tracer.visualize_interactions()
    tracer.display_execution_statistics()
    
    return result
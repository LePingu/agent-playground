"""
Workflow orchestration for the Source of Wealth Agent system.

This module defines and manages the workflow graph that coordinates
the execution of all agents in the system.
"""

from langgraph.graph import StateGraph, END

from source_of_wealth_agent.core.state import AgentState
from source_of_wealth_agent.agents.id_verification_agent import IDVerificationAgent
from source_of_wealth_agent.agents.payslip_verification_agent import PayslipVerificationAgent
from source_of_wealth_agent.agents.web_references_agent import WebReferencesAgent
from source_of_wealth_agent.agents.financial_reports_agent import FinancialReportsAgent
from source_of_wealth_agent.agents.corroboration_agents import employment_corroboration_agent, funds_corroboration_agent
from source_of_wealth_agent.agents.human_advisory_agent import human_advisory_agent
from source_of_wealth_agent.agents.risk_assessment_agent import risk_assessment_agent
from source_of_wealth_agent.agents.report_generation_agent import report_generation_agent
from source_of_wealth_agent.agents.summarization_agent import summarization_agent


# This function is no longer needed in the simplified workflow


def create_workflow(
    id_agent: IDVerificationAgent,
    payslip_agent: PayslipVerificationAgent,
    web_agent: WebReferencesAgent,
    financial_agent: FinancialReportsAgent = None
) -> StateGraph:
    """
    Create the workflow graph for the Source of Wealth Agent system.
    
    Args:
        id_agent: Instance of the ID verification agent
        payslip_agent: Instance of the payslip verification agent
        web_agent: Instance of the web references agent
        financial_agent: Optional instance of the financial reports agent
    
    Returns:
        Compiled workflow graph
    """
    # Build the workflow graph
    workflow = StateGraph(AgentState)
    
    # Add the basic verification agent nodes - use '_node' suffix to avoid conflicts with state keys
    workflow.add_node("id_verification_node", id_agent.run)
    workflow.add_node("payslip_verification_node", payslip_agent.run)
    workflow.add_node("web_references_node", web_agent.run)
    
    # Add summarization agent to collate data from verification agents
    workflow.add_node("summarization_node", summarization_agent)
    
    # Add risk assessment and report generation nodes
    workflow.add_node("risk_assessment_node", risk_assessment_agent)
    workflow.add_node("report_generation_node", report_generation_agent)
    
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
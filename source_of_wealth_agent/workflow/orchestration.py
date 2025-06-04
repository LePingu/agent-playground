"""
Workflow orchestration for the Source of Wealth Agent system.

This module defines and manages the workflow graph that coordinates
the execution of all agents in the system.

The updated orchestration uses a dynamic verification approach with human-in-the-loop:
1. Risk Assessment Agent determines what verifications are needed
2. ID verification is performed first with interrupt-based human review
3. Other verifications run in parallel with asynchronous human review
4. Summarization collates all verification results
5. Final risk assessment is performed
6. Report is generated
"""

from typing import Literal, TypedDict, Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from source_of_wealth_agent.core.state import AgentState, log_action
from source_of_wealth_agent.agents.id_verification_agent import IDVerificationAgent
from source_of_wealth_agent.agents.payslip_verification_agent import PayslipVerificationAgent
from source_of_wealth_agent.agents.web_references_agent import WebReferencesAgent
from source_of_wealth_agent.agents.financial_reports_agent import FinancialReportsAgent
from source_of_wealth_agent.agents.corroboration_agents import employment_corroboration_agent, funds_corroboration_agent
from source_of_wealth_agent.agents.human_advisory_agent import human_advisory_agent
from source_of_wealth_agent.agents.risk_assessment_agent import risk_assessment_agent
from source_of_wealth_agent.agents.report_generation_agent import report_generation_agent
from source_of_wealth_agent.agents.summarization_agent import summarization_agent

# Define helper functions for the dynamic workflow routing

def route_after_risk_assessment(state: AgentState) -> str:
    """
    Determine where to route after risk assessment agent runs,
    ensuring ID verification has priority and must complete first.
    
    ID verification now uses LangGraph's Interrupt pattern for blocking human review.
    Other verification steps will continue to run asynchronously while waiting for
    other types of human review responses.
    """
    # First, check if there are any review responses to process
    if state.get("review_responses") and len(state.get("review_responses", [])) > 0:
        print(f"ℹ️ Found {len(state.get('review_responses', []))} review responses to process")
        return "human_advisory_node"
    
    # Always check if ID verification has been completed
    # This enforces ID verification as a sequential prerequisite for any other steps
    id_verified = state.get("id_verification", {}).get("verified", None)
    id_approved = state.get("human_approvals", {}).get("id_verification", {}).get("approved", False)
    
    # If ID verification hasn't been completed yet and isn't the next step,
    # override any other routing and enforce ID verification first
    if id_verified is None and state.get("next_verification") != "id_verification":
        print("⚠️ SEQUENTIAL ENFORCEMENT: ID verification must be completed first - overriding next step")
        return "id_verification_node"
    
    # If ID verification failed and no human approval, we need to handle it
    if id_verified is False and not id_approved:
        # Check if we already have a pending review for ID verification
        if state.get("pending_reviews"):
            has_id_review_pending = any(
                review.get("verification_type") == "id_verification" 
                for review in state.get("pending_reviews", [])
            )
            if has_id_review_pending:
                print("⚠️ ID verification failed - waiting for human review (non-blocking)")
                # Since ID verification is sequential, we still need to block here
                # However, we've logged the request asynchronously so human can respond anytime
                return "human_advisory_node"
        
        print("⚠️ ID verification failed - must get human review before proceeding")
        return "human_advisory_node"
        
    # Only if ID verification passed or has human override, check normal routing logic
    if id_verified is True or id_approved:
        # If the risk assessment indicates a next agent, use that
        if "next_agent" in state:
            return state["next_agent"]
        
        # If there's a next verification step, return the corresponding node
        if "next_verification" in state:
            next_step = state["next_verification"]
                
            # Route to the appropriate node based on next_verification
            if next_step == "id_verification":
                return "id_verification_node"
            elif next_step == "payslip_verification":
                return "payslip_verification_node"
            elif next_step == "web_references_node":
                return "web_references_node"
            elif next_step == "financial_reports":
                return "financial_reports_node"
            elif next_step == "summarization":
                # Before going to summarization, check if we need to wait for any pending reviews
                if state.get("pending_reviews") and not state.get("human_approvals", {}).get("data_readiness_override", {}).get("approved", False):
                    print("ℹ️ There are pending reviews before summarization - requesting review")
                    return "human_advisory_node"
                return "summarization_node"
    
    # Default to human advisory if we can't determine the next step
    return "human_advisory_node"


def verification_needs_human_review(state: AgentState) -> str:
    """
    Determine if a verification step needs human review based on issues found.
    ID verification is a critical first step that blocks all other steps,
    so its issues are always prioritized for human review.
    
    With the new asynchronous human review system, this function now checks
    for issues and routes to the human advisory agent to register them for review,
    but will not block execution of other verification steps.
    """
    # Check if we have pending reviews and if there's a need to check status
    if state.get("pending_reviews") and len(state.get("pending_reviews", [])) > 0:
        print(f"ℹ️ There are {len(state.get('pending_reviews', []))} pending human reviews")
        # Still route to human advisory to check if any responses have been provided
        return "human_advisory_node"
    
    # Handle ID verification issues with highest priority
    # This is critical since ID verification is a sequential prerequisite
    if "id_verification" in state and state["id_verification"].get("issues_found"):
        print("⚠️ CRITICAL: ID verification issues detected - requesting human review")
        # Mark this as requiring special attention since it blocks the entire workflow
        state["id_verification_critical_issues"] = True
        return "human_advisory_node"
    
    # Only check other verification issues if ID verification was successful
    # or has been approved by human override - this enforces the sequential requirement
    id_verified = state.get("id_verification", {}).get("verified", False)
    human_approved_id = state.get("human_approvals", {}).get("id_verification", {}).get("approved", False)
    
    if id_verified or human_approved_id:
        needs_review = False
        
        if "payslip_verification" in state and state["payslip_verification"].get("issues_found"):
            print("⚠️ Payslip verification issues detected - requesting human review")
            needs_review = True
        
        if "web_references" in state and state["web_references"].get("risk_flags"):
            print("⚠️ Web references risk flags detected - requesting human review")
            needs_review = True
        
        if "financial_reports" in state and state["financial_reports"].get("issues_found"):
            print("⚠️ Financial reports issues detected - requesting human review")
            needs_review = True
            
        if needs_review:
            return "human_advisory_node"
    else:
        # If ID verification hasn't completed successfully and there's no human override,
        # route back to risk assessment which will enforce ID verification first
        print("⚠️ SEQUENTIAL ENFORCEMENT: Cannot proceed with verification review until ID is verified")
        return "risk_assessment_node"
    
    # If no human review needed, return to risk assessment for next steps
    return "risk_assessment_node"


def route_after_summarization(state: AgentState) -> str:
    """
    Determine where to route after summarization agent runs
    """
    # After summarization, we want to perform the final risk assessment
    # new_state = state.copy()
    state["risk_assessment_action"] = "perform_assessment"
    return "risk_assessment_node"


def create_workflow(
    id_agent: IDVerificationAgent,
    payslip_agent: PayslipVerificationAgent,
    web_agent: WebReferencesAgent,
    financial_agent: FinancialReportsAgent = None
) -> StateGraph:
    """
    Create the workflow graph for the Source of Wealth Agent system.
    
    This updated version implements a dynamic verification workflow with human-in-the-loop
    functionality using LangGraph's Interrupt pattern.
    
    Args:
        id_agent: Instance of the ID verification agent
        payslip_agent: Instance of the payslip verification agent
        web_agent: Instance of the web references agent
        financial_agent: Instance of the financial reports agent
    
    Returns:
        Compiled workflow graph
    """
    # Create a checkpointer for the graph to support interrupts
    checkpointer = MemorySaver()
    
    # Build the workflow graph
    workflow = StateGraph(AgentState)

    # Add the verification agent nodes
    workflow.add_node("id_verification_node", id_agent.run)
    workflow.add_node("payslip_verification_node", payslip_agent.run)
    workflow.add_node("web_references_node", web_agent.run)
    if financial_agent:
        workflow.add_node("financial_reports_node", financial_agent.run)
    
    # Add the human advisory node that now handles interrupts
    workflow.add_node("human_advisory_node", human_advisory_agent)
    
    # Add planning, summarization, and final processing nodes
    workflow.add_node("risk_assessment_node", risk_assessment_agent)
    workflow.add_node("summarization_node", summarization_agent)
    workflow.add_node("report_generation_node", report_generation_agent)
    
    # Define workflow entry point - start with risk assessment for planning
    workflow.add_edge("__start__", "risk_assessment_node")
    
    # Connect ID verification directly to human advisory
    # The human advisory agent will interrupt if human review is needed
    workflow.add_edge("id_verification_node", "human_advisory_node")
    
    # Risk assessment node determines the next verification step
    # workflow.add_conditional_edges(
    #     "risk_assessment_node",
    #     route_after_risk_assessment,
    #     {
    #         "id_verification_node": "id_verification_node",
    #         "payslip_verification_node": "payslip_verification_node",
    #         "web_references_node": "web_references_node",
    #         "financial_reports_node": "financial_reports_node" if financial_agent else "risk_assessment_node",
    #         "summarization_node": "summarization_node",
    #         "human_advisory_node": "human_advisory_node"
    #     }
    # )
    
    # After each verification (except ID which already goes to human advisory), 
    # check for issues and route to human review if needed
    for node in ["payslip_verification_node", "web_references_node", "financial_reports_node" if financial_agent else None]:
        if node:
            workflow.add_conditional_edges(
                node,
                verification_needs_human_review,
                {
                    "human_advisory_node": "human_advisory_node",
                    "risk_assessment_node": "risk_assessment_node"
                }
            )
    
    
    
    # After summarization, go to risk assessment for final assessment
    # workflow.add_conditional_edges("summarization_node", route_after_summarization, {
    #     "report_generation_node": "report_generation_node",
    # })
    
    # After final risk assessment, generate report
    workflow.add_conditional_edges(
        "risk_assessment_node", 
        lambda state: "report_generation_node" if "risk_assessment" in state else route_after_risk_assessment(state),
        {
            "report_generation_node": "report_generation_node",
            "id_verification_node": "id_verification_node",
            "payslip_verification_node": "payslip_verification_node", 
            "web_references_node": "web_references_node",
            "financial_reports_node": "financial_reports_node" if financial_agent else "risk_assessment_node",
            "summarization_node": "summarization_node",
            "human_advisory_node": "human_advisory_node"
        }
    )

    workflow.add_conditional_edges(
        "summarization_node",
        route_after_summarization,
        {
            "risk_assessment_node": "risk_assessment_node",
            "report_generation_node": "report_generation_node"
        }
    )
    
    # End the workflow after report generation
    workflow.add_edge("report_generation_node", END)
    
    # Compile the workflow with checkpointer for interrupt support
    return workflow.compile(checkpointer=checkpointer)

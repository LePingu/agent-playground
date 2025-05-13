"""
Risk Assessment Agent for the Source of Wealth Agent system.

This module provides risk analysis functionality to evaluate the verification results
and determine the risk level associated with a client.
"""

from datetime import datetime
from typing import List, Dict

from source_of_wealth_agent.core.state import AgentState, log_action, RiskAssessmentResult


def risk_assessment_agent(state: AgentState) -> AgentState:
    """
    Agent that evaluates all verification results and determines an overall risk assessment.
    
    This updated version works with the simplified workflow and the summarization agent data.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with risk assessment results
    """
    print("⚠️ Performing risk assessment...")
    
    # Gather all verification and corroboration results
    risk_factors = []
    risk_score = 0
    
    # First check if we have the summarization data
    if "verification_summary" in state:
        summary = state["verification_summary"]
        
        # Check verification statuses from summary
        verification_status = summary.get("verification_status", {})
        if not verification_status.get("id_verified", False):
            risk_factors.append("ID verification failed or missing")
            risk_score += 30
        
        if not verification_status.get("payslip_verified", False):
            risk_factors.append("Payslip verification failed or missing")
            risk_score += 25
            
        if not verification_status.get("web_references_verified", False):
            risk_factors.append("Web references check failed or missing")
            risk_score += 15
            
        # Add any risk indicators identified in the summarization
        if "risk_indicators" in summary and summary["risk_indicators"]:
            for indicator in summary["risk_indicators"]:
                if indicator not in risk_factors:  # Avoid duplicates
                    risk_factors.append(indicator)
                    risk_score += 10
    else:
        # Fallback to direct verification checks if summarization is missing
        # Check ID verification
        if "id_verification" not in state or not state["id_verification"].get("verified", False):
            risk_factors.append("ID verification failed or missing")
            risk_score += 30
        
        # Check payslip verification
        if "payslip_verification" not in state or not state["payslip_verification"].get("verified", False):
            risk_factors.append("Payslip verification failed or missing")
            risk_score += 25
            
        # Check web references
        if "web_references" not in state or not state["web_references"].get("verified", False):
            risk_factors.append("Web references check failed or missing")
            risk_score += 15
            
        # Check for risk flags in web references
        if "web_references" in state and "risk_flags" in state["web_references"]:
            for flag in state["web_references"]["risk_flags"]:
                risk_factors.append(f"Web reference risk: {flag}")
                risk_score += 10
    
    # Check human approvals (if any)
    for check_name, approved in state.get("human_approvals", {}).items():
        if not approved:
            risk_factors.append(f"Human reviewer rejected {check_name} check")
            risk_score += 15
    
    # Determine risk level using the same scale
    if risk_score == 0:
        risk_level = "Low"
    elif risk_score < 30:
        risk_level = "Medium-Low"
    elif risk_score < 50:
        risk_level = "Medium"
    elif risk_score < 70:
        risk_level = "Medium-High"
    else:
        risk_level = "High"
        
    result: RiskAssessmentResult = {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "assessment_date": datetime.now().isoformat()
    }
    
    new_state = state.copy()
    new_state["risk_assessment"] = result
    return log_action(new_state, "Risk_Assessment_Agent", "Risk assessment completed", result)
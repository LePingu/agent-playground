"""
Summarization Agent for the Source of Wealth Agent system.

This module provides functionality to collate and summarize data from different
verification agents to create a cohesive summary for the functional agents.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from source_of_wealth_agent.core.state import AgentState, log_action


def summarization_agent(state: AgentState) -> AgentState:
    """
    Agent that summarizes and collates information from various verification agents.
    
    This agent creates a consolidated view of the client's profile by extracting
    key information from the verification steps that were completed based on the
    verification plan.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with summarized information
    """
    print("📋 Summarizing verification data...")
    
    # Create a new state to avoid modifying the original
    new_state = state.copy()
    
    # Get verification plan to determine what was required
    verification_plan = state.get("verification_plan", {})
    
    # Extract key information from different sources
    summary = {
        "client_info": {
            "client_id": state.get("client_id", "Unknown"),
            "client_name": state.get("client_name", "Unknown"),
            "verification_date": datetime.now().isoformat()
        },
        "verification_plan": {
            "id_verification_required": verification_plan.get("id_verification_required", True),
            "payslip_verification_required": verification_plan.get("payslip_verification_required", False),
            "web_references_required": verification_plan.get("web_references_required", True),
            "financial_reports_required": verification_plan.get("financial_reports_required", False),
        },
        "verification_status": {
            "id_verified": _check_verification_status(state, "id_verification", "verified"),
            "payslip_verified": (_check_verification_status(state, "payslip_verification", "verified") 
                                if verification_plan.get("payslip_verification_required", False) else "Not Required"),
            "web_references_verified": _check_verification_status(state, "web_references", "verified"),
            "financial_reports_verified": (_check_verification_status(state, "financial_reports", "verified")
                                          if verification_plan.get("financial_reports_required", False) else "Not Required"),
        },
        "identity_details": _extract_identity_details(state),
        "employment_details": _extract_employment_details(state) if verification_plan.get("payslip_verification_required", False) else {"available": False, "reason": "Not required based on verification plan"},
        "web_presence": _extract_web_presence(state),
        "financial_reports": _extract_financial_reports(state) if verification_plan.get("financial_reports_required", False) else {"available": False, "reason": "Not required based on verification plan"},
        "risk_indicators": _extract_risk_indicators(state)
    }
    
    # Add the summary to the state
    state["verification_summary"] = summary
    state["risk_assessment_action"] = "perform_assessment"
    log_action( "Summarization_Agent", "Verification data summarized", summary)
    return state


def _check_verification_status(state: AgentState, key: str, status_field: str) -> bool:
    """Check if a verification step is completed successfully."""
    if key in state and isinstance(state[key], dict):
        return state[key].get(status_field, False)
    return False


def _extract_identity_details(state: AgentState) -> Dict[str, Any]:
    """Extract identity information from ID verification."""
    if "id_verification" not in state:
        return {"available": False}
    
    id_data = state["id_verification"]
    return {
        "available": True,
        "id_type": id_data.get("id_type", "Unknown"),
        "id_number": id_data.get("id_number", "Unknown"),
        "id_expiry": id_data.get("id_expiry", "Unknown"),
        "name_on_id": id_data.get("name", "Unknown"),
        "date_of_birth": id_data.get("date_of_birth", "Unknown"),
        "nationality": id_data.get("nationality", "Unknown"),
        "human_verified": state.get("human_approvals", {}).get("id_verification", False)
    }


def _extract_employment_details(state: AgentState) -> Dict[str, Any]:
    """Extract employment information from payslip verification."""
    if "payslip_verification" not in state:
        return {"available": False}
    
    payslip_data = state["payslip_verification"]
    return {
        "available": True,
        "employer": payslip_data.get("employer", "Unknown"),
        "position": payslip_data.get("position", "Unknown"),
        "monthly_income": payslip_data.get("monthly_income", 0),
        "annual_income": payslip_data.get("monthly_income", 0) * 12,
        "employment_start": payslip_data.get("employment_start", "Unknown"),
        "last_payment_date": payslip_data.get("payment_date", "Unknown")
    }


def _extract_web_presence(state: AgentState) -> Dict[str, Any]:
    """Extract online presence information from web references."""
    if "web_references" not in state:
        return {"available": False}
    
    web_data = state["web_references"]
    
    # Process mentions to extract key information
    mentions = web_data.get("mentions", [])
    processed_mentions = []
    
    for mention in mentions:
        processed_mentions.append({
            "source": mention.get("source", "Unknown"),
            "url": mention.get("url", ""),
            "summary": mention.get("analysis", {}).get("summary", "No summary available"),
            "sentiment": mention.get("analysis", {}).get("sentiment", "Neutral"),
        })
    
    return {
        "available": True,
        "mentions_count": len(mentions),
        "top_mentions": processed_mentions[:3],  # Just include the first 3 mentions
        "risk_flags": web_data.get("risk_flags", []),
        "search_date": web_data.get("search_date", datetime.now().isoformat())
    }


def _extract_financial_reports(state: AgentState) -> Dict[str, Any]:
    """Extract information from financial reports if available."""
    if "financial_reports" not in state:
        return {"available": False}
    
    financial_data = state["financial_reports"]
    return {
        "available": True,
        "reports_analyzed": financial_data.get("reports_analyzed", []),
        "annual_income_range": financial_data.get("annual_income_range", "Unknown"),
        "investment_assets": financial_data.get("investment_assets", "Unknown"),
        "credit_score": financial_data.get("credit_score", "Unknown"),
        "analysis_date": financial_data.get("analysis_date", datetime.now().isoformat())
    }


def _extract_risk_indicators(state: AgentState) -> List[str]:
    """Extract potential risk indicators from all verification sources."""
    risk_indicators = []
    
    # Check ID verification risks
    if not _check_verification_status(state, "id_verification", "verified"):
        risk_indicators.append("ID verification failed or incomplete")
    elif "id_verification" in state and state["id_verification"].get("warnings"):
        risk_indicators.extend(state["id_verification"].get("warnings", []))
    
    # Check payslip verification risks
    if not _check_verification_status(state, "payslip_verification", "verified"):
        risk_indicators.append("Payslip verification failed or incomplete")
    elif "payslip_verification" in state and state["payslip_verification"].get("warnings"):
        risk_indicators.extend(state["payslip_verification"].get("warnings", []))
    
    # Check web reference risks
    if "web_references" in state and "risk_flags" in state["web_references"]:
        risk_indicators.extend(state["web_references"]["risk_flags"])
        
    return risk_indicators

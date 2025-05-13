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
    key information from ID verification, payslip verification, and web references.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with summarized information
    """
    print("📋 Summarizing verification data...")
    
    # Create a new state to avoid modifying the original
    new_state = state.copy()
    
    # Extract key information from different sources
    summary = {
        "client_info": {
            "client_id": state.get("client_id", "Unknown"),
            "client_name": state.get("client_name", "Unknown"),
            "verification_date": datetime.now().isoformat()
        },
        "verification_status": {
            "id_verified": _check_verification_status(state, "id_verification", "verified"),
            "payslip_verified": _check_verification_status(state, "payslip_verification", "verified"),
            "web_references_verified": _check_verification_status(state, "web_references", "verified")
        },
        "identity_details": _extract_identity_details(state),
        "employment_details": _extract_employment_details(state),
        "web_presence": _extract_web_presence(state),
        "risk_indicators": _extract_risk_indicators(state)
    }
    
    # Add the summary to the state
    new_state["verification_summary"] = summary
    
    return log_action(new_state, "Summarization_Agent", "Verification data summarized", summary)


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

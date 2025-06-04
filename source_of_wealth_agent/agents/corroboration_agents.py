"""
Corroboration agents for the Source of Wealth Agent system.

This module contains agents that analyze and corroborate information from
different sources to verify consistency and accuracy.
"""

from datetime import datetime
from typing import List, Dict, Any

from source_of_wealth_agent.core.state import AgentState, log_action


def employment_corroboration_agent(state: AgentState) -> AgentState:
    """
    Agent that corroborates employment information between payslips and web references.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with employment corroboration results
    """
    print("🔄 Corroborating employment information...")
    
    # Ensure we have the necessary data
    if "payslip_verification" not in state or "web_references" not in state:
        return log_action( 
            "Employment_Corroboration_Agent", 
            "Employment corroboration skipped - missing data",
            {"error": "Missing required data"}
        )
    
    # Analyze consistency between payslips and web references
    payslip_employer = state["payslip_verification"].get("employer")
    web_mentions = state["web_references"].get("mentions", [])
    
    # Check if employment info is consistent
    consistency_check = any(
        payslip_employer in mention.get("details", "") 
        for mention in web_mentions
    )
    
    result = {
        "consistent": consistency_check,
        "confidence": "High" if consistency_check else "Low",
        "corroboration_date": datetime.now().isoformat()
    }
    
    new_state = state.copy()
    new_state["employment_corroboration"] = result
    return log_action("Employment_Corroboration_Agent", "Employment corroboration completed", result)


def funds_corroboration_agent(state: AgentState) -> AgentState:
    """
    Agent that corroborates source of funds between payslips and financial reports.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with funds corroboration results
    """
    print("💰 Corroborating source of funds...")
    
    # Check if payslips and financial reports are consistent
    if "payslip_verification" not in state or "financial_reports" not in state:
        return log_action(
            state, 
            "Funds_Corroboration_Agent", 
            "Funds corroboration skipped - missing data",
            {"error": "Missing required data"}
        )
    
    # Analyze if declared income can explain the financial position
    monthly_income = state["payslip_verification"].get("monthly_income", 0)
    annual_income = monthly_income * 12
    income_range = state["financial_reports"].get("annual_income_range", "")
    
    # Extract range values (simplified)
    try:
        range_parts = income_range.replace(",", "").split(" - ")
        min_range = float(range_parts[0])
        max_range = float(range_parts[1])
        income_consistent = min_range <= annual_income <= max_range
    except:
        income_consistent = False
    
    result = {
        "income_consistent": income_consistent,
        "analysis": "Declared income matches financial position" if income_consistent else "Potential discrepancy in income",
        "corroboration_date": datetime.now().isoformat()
    }
    
    new_state = state.copy()
    new_state["funds_corroboration"] = result
    return log_action( "Funds_Corroboration_Agent", "Source of funds corroboration completed", result)
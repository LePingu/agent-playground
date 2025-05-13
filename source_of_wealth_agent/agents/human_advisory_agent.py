"""
Human Advisory Agent for the Source of Wealth Agent system.

This module provides human-in-the-loop functionality to allow human reviewers
to approve or reject verification steps during the workflow.
"""

import json
from typing import Dict, Any

from source_of_wealth_agent.core.state import AgentState, log_action


def human_advisory_agent(state: AgentState) -> AgentState:
    """
    Agent that coordinates human review and approvals during the verification workflow.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with human approval decisions
    """
    print("👤 Human advisory checkpoint...")
    new_state = state.copy()
    
    # Check if employment corroboration needs approval
    if "employment_corroboration" in state and "employment_corroboration" not in state.get("human_approvals", {}):
        print("\n===== HUMAN INPUT REQUIRED: Employment Corroboration =====")
        print(f"Employment corroboration result: {json.dumps(state['employment_corroboration'], indent=2)}")
        decision = input("Approve this check? (yes/no): ").lower().strip()
        approved = decision == "yes"
        
        if "human_approvals" not in new_state:
            new_state["human_approvals"] = {}
        new_state["human_approvals"]["employment_corroboration"] = approved
        new_state = log_action(new_state, "Human_Advisory_Agent", f"Human approval for employment corroboration", approved)
    
    # Check if funds corroboration needs approval
    if "funds_corroboration" in state and "funds_corroboration" not in state.get("human_approvals", {}):
        print("\n===== HUMAN INPUT REQUIRED: Funds Corroboration =====")
        print(f"Funds corroboration result: {json.dumps(state['funds_corroboration'], indent=2)}")
        decision = input("Approve this check? (yes/no): ").lower().strip()
        approved = decision == "yes"
        
        if "human_approvals" not in new_state:
            new_state["human_approvals"] = {}
        new_state["human_approvals"]["funds_corroboration"] = approved
        new_state = log_action(new_state, "Human_Advisory_Agent", f"Human approval for funds corroboration", approved)
    
    return new_state
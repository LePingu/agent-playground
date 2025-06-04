"""
Example of integrating mock results with the actual agents.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from source_of_wealth_agent.core.state import create_initial_state, log_action
from source_of_wealth_agent.core.mock_results import (
    get_mock_client_verification_results,
    get_mock_high_risk_client_verification_results,
    get_mock_medium_risk_client_verification_results,
    get_mock_low_risk_client_verification_results
)

# Import agents (commented out for now since we're just demonstrating the concept)
# from source_of_wealth_agent.agents.id_verification_agent import IDVerificationAgent
# from source_of_wealth_agent.agents.payslip_verification_agent import PayslipVerificationAgent
# from source_of_wealth_agent.agents.web_references_agent import WebReferencesAgent
# from source_of_wealth_agent.agents.financial_reports_agent import FinancialReportsAgent

def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))

async def run_with_mock_results(client_id: str, client_name: str, risk_level: str = "low"):
    """
    Run a simulated workflow with mock results.
    
    Args:
        client_id: The client ID
        client_name: The client name
        risk_level: The risk level ("low", "medium", "high", or "custom")
    """
    print(f"\n=== Running workflow for {client_name} (ID: {client_id}) with {risk_level} risk level ===\n")
    
    # Step 1: Create initial state
    state = create_initial_state(client_id, client_name)
    print("\nInitial State:")
    print_json(state)
    
    # Step 2: Get mock results based on risk level
    if risk_level.lower() == "high":
        mock_results = get_mock_high_risk_client_verification_results(client_id, client_name)
    elif risk_level.lower() == "medium":
        mock_results = get_mock_medium_risk_client_verification_results(client_id, client_name)
    elif risk_level.lower() == "low":
        mock_results = get_mock_low_risk_client_verification_results(client_id, client_name)
    else:  # custom or any other value
        mock_results = get_mock_client_verification_results(client_id, client_name, all_verified=True)
    
    # Step 3: Update state with mock results
    # In a real scenario, these would come from actual agent runs
    state.update(mock_results)
    
    # Step 4: Log actions for each verification step
    # This simulates what would happen in the actual agents
    log_action("ID_Verification_Agent", "ID verification completed", state["id_verification"])
    log_action("Payslip_Verification_Agent", "Payslip verification completed", state["payslip_verification"])
    log_action("Web_References_Agent", "Web references check completed", state["web_references"])
    log_action("Financial_Reports_Agent", "Financial reports analysis completed", state["financial_reports"])
    
    # Step 5: Print the updated state
    print("\nState after verification steps:")
    print_json(state)
    
    # Step 6: In a real scenario, you would now run downstream agents
    # For example:
    # risk_assessment_result = await risk_assessment_agent.run(state)
    # state.update(risk_assessment_result)
    
    # Step 7: Print final state
    print("\nFinal State (after simulated workflow):")
    print_json(state)
    
    return state

async def main():
    """Main function to demonstrate integration with agents."""
    # Example 1: Low-risk client
    await run_with_mock_results("12345", "John Doe", "low")
    
    # Example 2: Medium-risk client
    # await run_with_mock_results("67890", "Jane Smith", "medium")
    
    # Example 3: High-risk client
    # await run_with_mock_results("54321", "Alex Johnson", "high")

if __name__ == "__main__":
    asyncio.run(main())

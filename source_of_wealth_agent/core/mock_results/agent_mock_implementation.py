"""
Example of implementing mock versions of the agents using the mock results.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any

from source_of_wealth_agent.core.state import AgentState, log_action
from source_of_wealth_agent.core.mock_results import (
    get_mock_id_verification_result,
    get_mock_payslip_verification_result,
    get_mock_web_references_result,
    get_mock_financial_reports_result
)

class MockIDVerificationAgent:
    """Mock implementation of the ID Verification Agent."""
    
    def __init__(self, model=None):
        """Initialize the mock agent."""
        self.name = "ID_Verification_Agent"
    
    async def run(self, state: AgentState) -> AgentState:
        """Run the mock agent."""
        client_id = state["client_id"]
        client_name = state.get("client_name", "Unknown")
        print(f"🔍 [MOCK] Verifying ID for client: {client_id} ({client_name})")
        
        # Generate mock ID verification result
        verification_result = get_mock_id_verification_result(
            client_id=client_id,
            client_name=client_name,
            verified=True  # Set to False to simulate verification failure
        )
        
        # Update state with verification result
        state["id_verification"] = verification_result
        log_action(self.name, "ID verification completed", verification_result)
        
        return state

class MockPayslipVerificationAgent:
    """Mock implementation of the Payslip Verification Agent."""
    
    def __init__(self, model=None):
        """Initialize the mock agent."""
        self.name = "Payslip_Verification_Agent"
    
    def run(self, state: AgentState) -> AgentState:
        """Run the mock agent."""
        client_id = state["client_id"]
        client_name = state.get("client_name", "Unknown")
        print(f"📄 [MOCK] Verifying payslips for client: {client_id} ({client_name})")
        
        # Generate mock payslip verification result
        verification_result = get_mock_payslip_verification_result(
            client_id=client_id,
            client_name=client_name,
            verified=True,  # Set to False to simulate verification failure
            monthly_income=15000.0,
            employer="Global Bank Ltd",
            position="Senior Manager"
        )
        
        # Update state with verification result
        state["payslip_verification"] = verification_result
        log_action(self.name, "Payslip verification completed", verification_result)
        
        return state

class MockWebReferencesAgent:
    """Mock implementation of the Web References Agent."""
    
    def __init__(self, model=None, retry_attempts=3):
        """Initialize the mock agent."""
        self.name = "Web_References_Agent"
    
    def run(self, state: AgentState) -> AgentState:
        """Run the mock agent."""
        client_id = state["client_id"]
        client_name = state.get("client_name", "Unknown")
        print(f"🌐 [MOCK] Checking web references for: {client_id} ({client_name})")
        
        # Get employer from payslip verification if available
        employer = None
        if "payslip_verification" in state and state["payslip_verification"]:
            employer = state["payslip_verification"].get("employer", "Global Bank Ltd")
        
        # Generate mock web references result
        verification_result = get_mock_web_references_result(
            client_id=client_id,
            client_name=client_name,
            verified=True,  # Set to False to simulate verification failure
            employer=employer
        )
        
        # Update state with verification result
        state["web_references"] = verification_result
        log_action(self.name, "Web references check completed", verification_result)
        
        return state

class MockFinancialReportsAgent:
    """Mock implementation of the Financial Reports Agent."""
    
    def __init__(self, model=None):
        """Initialize the mock agent."""
        self.name = "Financial_Reports_Agent"
    
    def run(self, state: AgentState) -> AgentState:
        """Run the mock agent."""
        client_id = state["client_id"]
        client_name = state.get("client_name", "Unknown")
        print(f"📊 [MOCK] Checking financial reports for client: {client_id} ({client_name})")
        
        # Generate mock financial reports result
        verification_result = get_mock_financial_reports_result(
            client_id=client_id,
            client_name=client_name,
            verified=True,  # Set to False to simulate verification failure
            annual_income_range="100,000 - 200,000",
            investment_assets="500,000+",
            credit_score="Excellent"
        )
        
        # Update state with verification result
        state["financial_reports"] = verification_result
        log_action(self.name, "Financial reports analysis completed", verification_result)
        
        return state

async def run_mock_workflow(client_id: str, client_name: str) -> Dict[str, Any]:
    """
    Run a complete mock workflow with all agents.
    
    Args:
        client_id: The client ID
        client_name: The client name
        
    Returns:
        The final state after all agents have run
    """
    from source_of_wealth_agent.core.state import create_initial_state
    
    # Create initial state
    state = create_initial_state(client_id, client_name)
    
    # Initialize mock agents
    id_agent = MockIDVerificationAgent()
    payslip_agent = MockPayslipVerificationAgent()
    web_agent = MockWebReferencesAgent()
    financial_agent = MockFinancialReportsAgent()
    
    # Run ID verification (async)
    state = await id_agent.run(state)
    
    # Run payslip verification (sync)
    state = payslip_agent.run(state)
    
    # Run web references check (sync)
    state = web_agent.run(state)
    
    # Run financial reports analysis (sync)
    state = financial_agent.run(state)
    
    return state

async def main():
    """Main function to demonstrate the mock agents."""
    import json
    
    def print_json(data):
        """Print data as formatted JSON."""
        print(json.dumps(data, indent=2))
    
    print("\n=== Running Mock Workflow ===\n")
    
    # Run the mock workflow
    final_state = await run_mock_workflow("12345", "John Doe")
    
    # Print the final state
    print("\nFinal State:")
    print_json(final_state)

if __name__ == "__main__":
    asyncio.run(main())

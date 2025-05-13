#!/usr/bin/env python3
"""
End-to-end test of the modified source of wealth verification workflow.

This script skips the actual agent execution and injects mock data to verify
the full workflow with the new summarization agent.
"""

import sys
import os
from datetime import datetime
import json

# Adjust path to include parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from source_of_wealth_agent.core.state import AgentState, create_initial_state
from langgraph.graph import StateGraph, END
from source_of_wealth_agent.agents.summarization_agent import summarization_agent
from source_of_wealth_agent.agents.risk_assessment_agent import risk_assessment_agent
from source_of_wealth_agent.agents.report_generation_agent import report_generation_agent


def create_mock_id_agent(client_id: str):
    """Create a mock ID verification agent."""
    def mock_id_verification(state: AgentState) -> AgentState:
        print(f"🔍 Mock ID verification for client: {client_id}")
        
        # Add mock data to state
        new_state = state.copy()
        new_state["id_verification"] = {
            "verified": True,
            "id_type": "Passport",
            "id_number": "AB123456",
            "id_expiry": "2028-01-15",
            "name": "Hatim Nourbay",
            "date_of_birth": "1985-06-22",
            "nationality": "Morocco",
            "verification_date": datetime.now().isoformat()
        }
        
        # Add to audit log
        if "audit_log" not in new_state:
            new_state["audit_log"] = []
            
        new_state["audit_log"].append({
            "timestamp": datetime.now().isoformat(),
            "agent": "Mock_ID_Verification_Agent",
            "action": "ID verification completed"
        })
        
        return new_state
    
    return mock_id_verification


def create_mock_payslip_agent():
    """Create a mock payslip verification agent."""
    def mock_payslip_verification(state: AgentState) -> AgentState:
        print("📄 Mock payslip verification")
        
        # Add mock data to state
        new_state = state.copy()
        new_state["payslip_verification"] = {
            "verified": True,
            "employer": "Global Finance Partners",
            "position": "Senior Analyst",
            "monthly_income": 12000,
            "payment_date": "2025-04-30",
            "employment_start": "2021-03-15",
            "verification_date": datetime.now().isoformat()
        }
        
        # Add to audit log
        if "audit_log" not in new_state:
            new_state["audit_log"] = []
            
        new_state["audit_log"].append({
            "timestamp": datetime.now().isoformat(),
            "agent": "Mock_Payslip_Verification_Agent",
            "action": "Payslip verification completed"
        })
        
        return new_state
    
    return mock_payslip_verification


def create_mock_web_agent():
    """Create a mock web references agent."""
    def mock_web_verification(state: AgentState) -> AgentState:
        print("🌐 Mock web references verification")
        
        # Add mock data to state
        new_state = state.copy()
        new_state["web_references"] = {
            "verified": True,
            "mentions": [
                {
                    "source": "LinkedIn",
                    "url": "https://linkedin.com/in/hatim-nourbay",
                    "details": "Senior Analyst at Global Finance Partners since March 2021",
                    "analysis": {
                        "summary": "Professional profile confirms employment information",
                        "sentiment": "Positive",
                        "risk_flags": []
                    }
                },
                {
                    "source": "Financial News Daily",
                    "url": "https://financialnewsdaily.com/global-finance-partners-expansion",
                    "details": "Global Finance Partners announces new senior team including Hatim Nourbay",
                    "analysis": {
                        "summary": "News article confirms employment with the company",
                        "sentiment": "Neutral",
                        "risk_flags": []
                    }
                }
            ],
            "risk_flags": [],
            "search_date": datetime.now().isoformat()
        }
        
        # Add to audit log
        if "audit_log" not in new_state:
            new_state["audit_log"] = []
            
        new_state["audit_log"].append({
            "timestamp": datetime.now().isoformat(),
            "agent": "Mock_Web_References_Agent",
            "action": "Web references check completed"
        })
        
        return new_state
    
    return mock_web_verification


def create_test_workflow():
    """Create a test workflow with mock agents."""
    # Create workflow
    workflow = StateGraph(AgentState)
    
    # Create mock agents
    mock_id_agent = create_mock_id_agent("12345")
    mock_payslip_agent = create_mock_payslip_agent()
    mock_web_agent = create_mock_web_agent()
    
    # Add nodes to workflow
    workflow.add_node("id_verification_node", mock_id_agent)
    workflow.add_node("payslip_verification_node", mock_payslip_agent)
    workflow.add_node("web_references_node", mock_web_agent)
    workflow.add_node("summarization_node", summarization_agent)
    workflow.add_node("risk_assessment_node", risk_assessment_agent)
    workflow.add_node("report_generation_node", report_generation_agent)
    
    # Define workflow edges
    workflow.add_edge("__start__", "id_verification_node")
    workflow.add_edge("id_verification_node", "payslip_verification_node")
    workflow.add_edge("payslip_verification_node", "web_references_node")
    workflow.add_edge("web_references_node", "summarization_node")
    workflow.add_edge("summarization_node", "risk_assessment_node")
    workflow.add_edge("risk_assessment_node", "report_generation_node")
    workflow.add_edge("report_generation_node", END)
    
    # Compile workflow
    return workflow.compile()


def main():
    """Run the end-to-end workflow test."""
    try:
        print("=== Running End-to-End Workflow Test ===")
        
        # Create initial state
        client_id = "12345"
        client_name = "Hatim Nourbay"
        initial_state = create_initial_state(client_id, client_name)
        
        # Create workflow
        workflow = create_test_workflow()
        
        # Execute workflow
        print(f"\nExecuting workflow for client: {client_name} (ID: {client_id})...\n")
        result = workflow.invoke(initial_state)
        
        print("\n✅ Workflow execution completed")
        
        # Display final report
        if "final_report" in result:
            print("\n=== FINAL REPORT ===\n")
            print(result["final_report"])
        else:
            print("❌ No final report was generated")
        
        # Display audit log
        if "audit_log" in result:
            print("\n=== AUDIT LOG ===\n")
            for entry in result["audit_log"]:
                print(f"{entry['timestamp']} | {entry['agent']} | {entry['action']}")
        
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"Error in end-to-end test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

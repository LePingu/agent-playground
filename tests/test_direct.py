#!/usr/bin/env python3
"""
Direct testing script for the summarization agent and report generation.

This script directly tests the summarization and report generation agents 
using predefined test data, bypassing the actual verification steps.
"""

import os
import sys
import json
from datetime import datetime

# Adjust path to include parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from source_of_wealth_agent.core.state import AgentState, create_initial_state, log_action
from source_of_wealth_agent.agents.summarization_agent import summarization_agent
from source_of_wealth_agent.agents.risk_assessment_agent import risk_assessment_agent
from source_of_wealth_agent.agents.report_generation_agent import report_generation_agent


def create_test_state():
    """Create a test state with predefined verification data."""
    client_id = "12345"
    client_name = "Hatim Nourbay"
    
    # Create initial state
    state = create_initial_state(client_id, client_name)
    
    # Add mock ID verification data
    state["id_verification"] = {
        "verified": True,
        "id_type": "Passport",
        "id_number": "AB123456",
        "id_expiry": "2028-01-15",
        "name": "Hatim Nourbay",
        "date_of_birth": "1985-06-22",
        "nationality": "Morocco",
        "verification_date": datetime.now().isoformat()
    }
    
    # Add mock payslip verification data
    state["payslip_verification"] = {
        "verified": True,
        "employer": "Global Finance Partners",
        "position": "Senior Analyst",
        "monthly_income": 12000,
        "payment_date": "2025-04-30",
        "employment_start": "2021-03-15",
        "verification_date": datetime.now().isoformat()
    }
    
    # Add mock web references data
    state["web_references"] = {
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
    
    # Add mock human approvals
    state["human_approvals"] = {
        "id_verification": True
    }
    
    return state


def main():
    """Run the test for summarization and report generation."""
    print("Creating test state with mock verification data...")
    state = create_test_state()
    
    print("\n=== Test State Created ===")
    print(f"Client: {state['client_name']} (ID: {state['client_id']})")
    print(f"ID Verified: {state['id_verification']['verified']}")
    print(f"Payslip Verified: {state['payslip_verification']['verified']}")
    print(f"Web References Verified: {state['web_references']['verified']}")
    
    # Run summarization agent
    print("\n=== Running Summarization Agent ===")
    state = summarization_agent(state)
    
    # Verify summarization output
    if "verification_summary" in state:
        print("✅ Summarization completed")
        print(f"Summary sections: {', '.join(state['verification_summary'].keys())}")
    else:
        print("❌ Summarization failed")
        
    # Run risk assessment agent
    print("\n=== Running Risk Assessment Agent ===")
    state = risk_assessment_agent(state)
    
    # Verify risk assessment output
    if "risk_assessment" in state:
        print("✅ Risk assessment completed")
        print(f"Risk Level: {state['risk_assessment'].get('risk_level')}")
        print(f"Risk Score: {state['risk_assessment'].get('risk_score')}")
        print(f"Risk Factors: {len(state['risk_assessment'].get('risk_factors', []))}")
    else:
        print("❌ Risk assessment failed")
    
    # Run report generation agent
    print("\n=== Running Report Generation Agent ===")
    state = report_generation_agent(state)
    
    # Display final report
    if "final_report" in state:
        print("\n=== FINAL REPORT ===\n")
        print(state["final_report"])
    else:
        print("❌ No final report was generated")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()

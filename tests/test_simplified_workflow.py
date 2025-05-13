#!/usr/bin/env python3
"""
Test script for the simplified Source of Wealth verification workflow.

This script tests the workflow with just ID verification, payslip verification,
and web references checks, using the new summarization agent.
"""

import os
import sys
import json
from datetime import datetime

# Adjust path to include parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from source_of_wealth_agent.core.state import create_initial_state
from source_of_wealth_agent.agents.id_verification_agent import IDVerificationAgent
from source_of_wealth_agent.agents.payslip_verification_agent import PayslipVerificationAgent
from source_of_wealth_agent.agents.web_references_agent import WebReferencesAgent
from source_of_wealth_agent.workflow.orchestration import create_workflow


def initialize_models():
    """Initialize language models for the agents."""
    print("Initializing language models...")
    
    try:
        # OpenRouter model for general tasks
        # Using simpler model for testing to avoid hitting rate limits
        # For testing purposes, let's simulate the model responses
        from langchain.llms.fake import FakeListLLM
        
        # Create a fake model that returns predefined responses
        fake_responses = [
            "This is a simulated response for testing purposes.",
            "Here's another simulated response.",
            "The test workflow is working correctly.",
            "The verification has been completed successfully."
        ]
        
        openrouter_model = FakeListLLM(responses=fake_responses)
        
        # Use the same fake model for Ollama too
        ollama_model = FakeListLLM(responses=fake_responses)
        
        print("✅ Using simulated models for testing")
    except Exception as e:
        print(f"Error initializing models: {e}")
        print("Falling back to simple string response model")
        
        # Extremely simple fallback that just returns strings
        from langchain.llms.base import LLM
        from typing import Optional, List, Dict, Any
        
        class SimpleResponseLLM(LLM):
            def _llm_type(self) -> str:
                return "simple_response"
                
            def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
                return "Simulated response for testing workflow"
        
        openrouter_model = SimpleResponseLLM()
        ollama_model = SimpleResponseLLM()
    
    print("✅ Models initialized")
    return openrouter_model, ollama_model


def main():
    """Run the simplified workflow with test client data."""
    # Initialize models
    openrouter_model, ollama_model = initialize_models()
    
    # Initialize agents with appropriate models
    print("Initializing agents...")
    id_agent = IDVerificationAgent(model=ollama_model)
    payslip_agent = PayslipVerificationAgent(model=ollama_model)
    web_agent = WebReferencesAgent(model=openrouter_model)
    print("✅ Agents initialized")
    
    # Create workflow
    print("Creating workflow...")
    workflow = create_workflow(
        id_agent=id_agent,
        payslip_agent=payslip_agent,
        web_agent=web_agent
    )
    print("✅ Workflow created")
    
    # Create initial state with test client data
    client_id = "12345"
    client_name = "Hatim Nourbay"
    
    print(f"Running workflow for client: {client_name} (ID: {client_id})...")
    initial_state = create_initial_state(client_id, client_name)
    
    # Add mock verification data to test the full workflow
    initial_state = inject_test_verification_data(initial_state)
    
    # Execute workflow
    try:
        result = workflow.invoke(initial_state)
        print("\n✅ Workflow execution completed")
        
        # Display final report
        if "final_report" in result:
            print("\n=== FINAL REPORT ===\n")
            print(result["final_report"])
        else:
            print("❌ No final report was generated")
        
        # Display audit log summary
        if "audit_log" in result:
            print("\n=== AUDIT LOG SUMMARY ===\n")
            for entry in result["audit_log"]:
                print(f"{entry['timestamp']} | {entry['agent']} | {entry['action']}")
    except Exception as e:
        print(f"❌ Error executing workflow: {str(e)}")
        import traceback
        traceback.print_exc()


def inject_test_verification_data(state):
    """Inject test verification data to simulate agent outputs."""
    print("Injecting test verification data...")
    
    # Mock ID verification data
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
    
    # Mock payslip verification data
    state["payslip_verification"] = {
        "verified": True,
        "employer": "Global Finance Partners",
        "position": "Senior Analyst",
        "monthly_income": 12000,
        "payment_date": "2025-04-30",
        "employment_start": "2021-03-15",
        "verification_date": datetime.now().isoformat()
    }
    
    # Mock web references data
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
    
    print("✅ Test data injected")
    return state


if __name__ == "__main__":
    main()

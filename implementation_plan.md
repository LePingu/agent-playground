# Implementation Plan: Integrating LangGraph Interrupt for Human-in-the-Loop

## Overview

This implementation plan outlines how to integrate LangGraph's "Interrupt" pattern for human-in-the-loop functionality into the Source of Wealth Agent system. The key requirement is to make ID verification block using Interrupt pattern, while keeping the rest of the workflow (payslip, web references, financial reports agents) running asynchronously in the background.

## Current System

The current system:
- Uses an asynchronous review mechanism for all verifications
- Stores pending reviews in the state and continues execution
- Processes human reviews separately through a CLI interface
- Has ID verification as a sequential prerequisite for other steps

## Implementation Plan

### 1. Create a New ID Verification Advisory Agent with Interrupt Pattern

Create a new agent specifically for handling ID verification using the Interrupt pattern:

```python
# source_of_wealth_agent/agents/id_verification_advisory_agent.py

from langgraph.types import interrupt, Command
from typing import Dict, Any

def id_verification_advisory_agent(state: AgentState) -> AgentState:
    """
    Agent that handles ID verification reviews using the Interrupt pattern.
    This agent blocks execution until human review is provided.
    """
    client_id = state.get("client_id", "N/A")
    
    # Only process ID verification
    if "id_verification" in state:
        id_check_data = state["id_verification"]
        
        # Only interrupt if issues found or not verified
        if id_check_data.get("issues_found") or id_check_data.get("verified") is False:
            # Create payload for human review
            review_payload = {
                "verification_type": "id_verification",
                "client_id": client_id,
                "verification_data": id_check_data,
                "issues": id_check_data.get("issues_found", [])
            }
            
            # Interrupt execution and wait for human input
            human_response = interrupt(review_payload)
            
            # Process the human response
            approval_detail = {
                "approved": human_response["approved"],
                "review_date": human_response["review_date"],
                "issues_at_review": human_response.get("issues_at_review", []),
                "reviewer_comments": human_response.get("reviewer_comments")
            }
            
            # Update state with human approval
            new_state = state.copy()
            if "human_approvals" not in new_state:
                new_state["human_approvals"] = {}
            new_state["human_approvals"]["id_verification"] = approval_detail
            
            # Update ID verification status based on approval
            new_state["id_verification"]["verified"] = approval_detail["approved"]
            new_state["id_verification"]["human_approved"] = approval_detail["approved"]
            
            # Add to audit log
            log_action_update = log_action("ID_Verification_Advisory_Agent", 
                                     f"Processed ID verification review for client {client_id}", 
                                     {"approved": approval_detail["approved"]})
            
            if "audit_log" in log_action_update:
                if "audit_log" not in new_state:
                    new_state["audit_log"] = []
                new_state["audit_log"].extend(log_action_update["audit_log"])
                
            return new_state
    
    # If no ID verification or no issues, just return the state unchanged
    return state
```

### 2. Update Human Advisory Agent for Other Verifications

Modify the existing human advisory agent to exclude ID verification but continue handling other verifications asynchronously:

```python
# Modified human_advisory_agent function
def human_advisory_agent(state: AgentState) -> AgentState:
    """
    Agent that coordinates human review and approvals for all verifications
    except ID verification, which is handled separately with interrupts.
    Non-blocking implementation that records review requests in the state.
    """
    # ... existing code ...
    
    # Remove the ID verification handling section
    # Only handle payslip, web references, employment, funds, etc.
    
    # ... rest of existing code ...
```

### 3. Update Workflow Orchestration for Interrupt Handling

Modify the orchestration workflow to:
1. Add the new ID verification advisory node
2. Update routing to include the interrupt mechanism
3. Ensure the checkpoint system is configured for handling interrupts

```python
# source_of_wealth_agent/workflow/orchestration.py

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
# ... existing imports ...

from source_of_wealth_agent.agents.id_verification_advisory_agent import id_verification_advisory_agent

def create_workflow(
    id_agent: IDVerificationAgent,
    payslip_agent: PayslipVerificationAgent,
    web_agent: WebReferencesAgent,
    financial_agent: FinancialReportsAgent = None
) -> StateGraph:
    """Create the workflow graph for the Source of Wealth Agent system."""
    # Create a checkpointer for the graph to support interrupts
    checkpointer = MemorySaver()
    
    # Build the workflow graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("id_verification_node", id_agent.run)
    workflow.add_node("id_verification_advisory_node", id_verification_advisory_agent)
    # ... add other nodes as before ...
    
    # Update routing logic to include ID verification advisory
    # Make ID verification go through advisory before moving to other steps
    workflow.add_edge("id_verification_node", "id_verification_advisory_node")
    
    # After ID advisory, route to risk assessment
    workflow.add_edge("id_verification_advisory_node", "risk_assessment_node")
    
    # ... rest of existing graph definition ...
    
    # Compile with checkpointer
    return workflow.compile(checkpointer=checkpointer)
```

### 4. Update CLI Interface to Handle Interrupts

Modify the CLI interface to handle both the interrupt-based ID verification and asynchronous reviews:

```python
# process_reviews.py

import json
import argparse
from langgraph.types import Command
from source_of_wealth_agent.workflow.runner import load_graph_state, save_graph_state

def main():
    parser = argparse.ArgumentParser(description="Process human reviews")
    parser.add_argument("--state-file", default="output_state.json", help="Path to state file")
    parser.add_argument("--thread-id", default="default", help="Thread ID for the workflow")
    args = parser.parse_args()
    
    # Load state from file
    state = load_graph_state(args.state_file)
    
    # Check if there's an interrupt to handle
    if "__interrupt__" in state:
        interrupt = state["__interrupt__"]
        value = interrupt.get("value", {})
        
        print("\n===== INTERRUPT: ID VERIFICATION REVIEW REQUIRED =====")
        print(f"Client ID: {value.get('client_id', 'N/A')}")
        print(f"Issues requiring review: {json.dumps(value.get('issues', []), indent=2)}")
        
        while True:
            decision = input(f"Approve this ID verification? (yes/no): ").lower().strip()
            if decision in ["yes", "no"]:
                break
            print("Invalid input. Please enter 'yes' or 'no'.")
        
        comments = input("Enter any comments (optional): ").strip()
        
        # Prepare response for interrupt
        resume_response = {
            "approved": (decision == "yes"),
            "review_date": datetime.now().isoformat(),
            "reviewer_comments": comments if comments else None,
            "issues_at_review": value.get('issues', [])
        }
        
        # Resume execution with the response
        # This will require executing the workflow with the Command object
        print("Resuming workflow with human review response...")
        # Code to resume workflow with Command(resume=resume_response)
        
    else:
        # Handle normal async reviews as before
        # ... existing process_human_reviews code ...
```

### 5. Update Workflow Runner for Interrupt Handling

Modify the workflow runner to support resuming from interrupts:

```python
# source_of_wealth_agent/workflow/runner.py

from langgraph.types import Command
# ... existing imports ...

def run_workflow_step(workflow, thread_id, state=None, resume_data=None):
    """Run a single step of the workflow, handling interrupts if needed."""
    config = {"configurable": {"thread_id": thread_id}}
    
    if resume_data:
        # Resume from interrupt with the provided data
        return workflow.invoke(Command(resume=resume_data), config=config)
    elif state:
        # Continue with provided state
        return workflow.invoke(state, config=config)
    else:
        # Start new workflow
        return workflow.invoke({}, config=config)
```

## Integration Points

1. **ID Verification Flow**:
   - ID verification agent performs automated checks
   - ID verification advisory agent interrupts for human review
   - Once human input is provided, workflow resumes with the decision
   - This ensures ID verification is completed before proceeding

2. **Asynchronous Verifications**:
   - All other verification agents (payslip, web references, financial) continue working asynchronously
   - Human advisory agent queues reviews without blocking
   - CLI processes these reviews separately
   - Upon submitting reviews, they're added to the state for the next run

## Testing Plan

1. **ID Verification Interrupt Test**:
   - Verify that ID verification correctly interrupts the workflow
   - Test resuming with approval and rejection scenarios
   - Ensure state is properly updated after interruption

2. **Async Verification Test**:
   - Verify that other verification steps continue to run asynchronously 
   - Test that pending reviews are properly queued
   - Ensure state is correctly updated when reviews are processed

3. **Integration Test**:
   - Test the complete flow with both interrupt and async components
   - Verify that ID verification must be completed before other steps
   - Test multiple review scenarios

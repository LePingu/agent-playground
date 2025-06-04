"""
Human Advisory Agent for the Source of Wealth Agent system.

This module provides human-in-the-loop functionality to allow human reviewers
to approve or reject verification steps during the workflow.
"""

import json
from typing import Dict, List, Any
from datetime import datetime
import logging

from langgraph.types import interrupt, Command

from source_of_wealth_agent.core.state import (
    AgentState, 
    log_action, 
    HumanApprovalDetail, 
    request_human_review
)

# Setup logger for the agent
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Module-level logger for the function
_human_advisory_agent_logger = logging.getLogger("human_advisory_agent_function")
if not _human_advisory_agent_logger.handlers:
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _handler.setFormatter(_formatter)
    _human_advisory_agent_logger.addHandler(_handler)
_human_advisory_agent_logger.setLevel(logging.INFO)


def human_advisory_agent(state: AgentState) -> AgentState:
    """
    Agent that coordinates human review and approvals for various verification checks.
    
    This agent now uses two different approaches:
    1. LangGraph's interrupt pattern for ID verification (blocking - workflow waits for review)
    2. Asynchronous reviews for other verification types (non-blocking)
    
    Args:
        state: Current workflow state
        
    Returns:
        Modified state with review requests and/or updates based on responses
        
    Raises:
        LangGraph interrupt: When ID verification requires human review
    """

    _human_advisory_agent_logger.info("👤 Human advisory checkpoint activated...")
    
    # Create a new state that's a shallow copy of the current state
    new_state = state.copy()
    client_id = state.get("client_id", "N/A") # Get client_id for logging and context
    client_name = state.get("client_name", "Unknown")

    if "human_approvals" not in new_state:
        new_state["human_approvals"] = {}
        
    # # Process any review responses that have been provided
    # if "review_responses" in state and state["review_responses"]:
    #     _human_advisory_agent_logger.info(f"Found {len(state['review_responses'])} review responses to process")
        
    #     for response in state["review_responses"]:
    #         verification_type = response.get("verification_type")
    #         if not verification_type:
    #             continue
                
    #         # Update human approvals with the response
    #         approval_detail = {
    #             "approved": response["approved"],
    #             "review_date": response["review_date"],
    #             "issues_at_review": response.get("issues_at_review", []),
    #             "reviewer_comments": response.get("reviewer_comments")
    #         }
            
    #         new_state["human_approvals"][verification_type] = approval_detail
    #         _human_advisory_agent_logger.info(f"Processed review response for {verification_type}. Approved: {approval_detail['approved']}")
            
    #         # Update the verification status based on the approval
    #         if verification_type == "id_verification" and "id_verification" in new_state:
    #             new_state["id_verification"]["verified"] = approval_detail["approved"]
    #             new_state["id_verification"]["human_approved"] = approval_detail["approved"]
            
    #         elif verification_type == "payslip_verification_review" and "payslip_verification" in new_state:
    #             new_state["payslip_verification"]["verified"] = approval_detail["approved"]
    #             new_state["payslip_verification"]["human_approved_despite_issues"] = approval_detail["approved"]
                
    #         elif verification_type == "employment_corroboration" and "employment_corroboration" in new_state:
    #             new_state["employment_corroboration"]["consistent"] = approval_detail["approved"]
                
    #         elif verification_type == "funds_corroboration" and "funds_corroboration" in new_state:
    #             new_state["funds_corroboration"]["consistent"] = approval_detail["approved"]
    #             new_state["funds_corroboration"]["income_consistent"] = approval_detail["approved"]
                
    #         elif verification_type == "data_readiness_override" and approval_detail["approved"]:
    #             # Apply overrides for missing verification data
    #             issues = approval_detail.get("issues_at_review", [])
                
    #             # For ID verification
    #             if "id_verification" in issues and "id_verification" in new_state:
    #                 new_state["id_verification"]["verified"] = True
    #                 _human_advisory_agent_logger.info("Human override applied to ID verification status")
                    
    #             # For payslip verification
    #             if "payslip_verification" in issues and "payslip_verification" in new_state:
    #                 new_state["payslip_verification"]["verified"] = True
    #                 _human_advisory_agent_logger.info("Human override applied to payslip verification status")
                    
    #             # For web references
    #             if "web_references" in issues:
    #                 if "web_references" not in new_state:
    #                     new_state["web_references"] = {
    #                         "verified": True,
    #                         "mentions": [],
    #                         "risk_flags": ["Manual override - no web references data available"],
    #                         "search_date": datetime.now().isoformat(),
    #                         "override_note": "Data placeholder created by human advisory agent"
    #                     }
    #                 else:
    #                     new_state["web_references"]["verified"] = True
    #                 _human_advisory_agent_logger.info("Human override applied to web references data")
    
    # Check if ID verification needs review - Use INTERRUPT pattern for this!
    if "id_verification" in state and not state["id_verification"].get("verified", False):
        id_verification_data = state["id_verification"]
        
        # Check if we already have human approval
        if not new_state["human_approvals"].get("id_verification", {}).get("approved", False):
            issues = id_verification_data.get("issues_found", [])
            # if issues:
            _human_advisory_agent_logger.info(f"ID verification requires human review for client {client_id}")
            
            # # Create an interrupt! This will pause workflow execution until human input is provided
            # interrupt_data = {
            #     "verification_type": "id_verification",
            #     "client_id": client_id,
            #     "client_name": client_name,
            #     "issues": issues,
            #     "verification_data": id_verification_data
            # }
            
            # Log that we're interrupting for human review
            log_action_update = log_action("Human_Advisory_Agent", 
                                         f"Interrupting workflow for ID verification review", 
                                         {"client_id": client_id, "issues": issues})
            if "audit_log" in log_action_update:
                if "audit_log" not in new_state:
                    new_state["audit_log"] = []
                new_state["audit_log"].extend(log_action_update["audit_log"])
            
            # Interrupt the workflow - this will block execution until a human resolves it
            get_approval = input(
                f"ID verification requires human review for client {client_id}. Approve? (yes/no): "
            ).strip().lower()
            # interrupt(interrupt_data, new_state["human_approvals"].get("id_verification", {}).get("approved", False))

            if get_approval == "yes":
                # Update the state with human approval
                new_state["human_approvals"]["id_verification"] = HumanApprovalDetail(
                    approved=True,
                    review_date=datetime.now().isoformat(),
                    issues_at_review=issues,
                    reviewer_comments="Human review approved ID verification"
                )
                _human_advisory_agent_logger.info(f"ID verification approved by human for client {client_id}")
                return Command(goto="risk_assessment_node", update=new_state)
            else:
                return Command(goto="end")
            # return interrupt(interrupt_data)
    
    # Check verification results and request reviews asynchronously as needed for other verification types
    
    # Check if Payslip verification needs review
    if "payslip_verification" in state and not new_state["human_approvals"].get("payslip_verification_review", {}).get("approved"):
        payslip_check_data = state["payslip_verification"]
        if payslip_check_data.get("issues_found"):
            _human_advisory_agent_logger.info(f"Requesting Payslip verification review for client {client_id}")
            review_request = request_human_review(
                verification_type="payslip_verification_review",
                client_id=client_id,
                verification_data=payslip_check_data,
                issues=payslip_check_data.get("issues_found", [])
            )
            # Merge the review request into our state update
            if "pending_reviews" not in new_state:
                new_state["pending_reviews"] = []
            new_state["pending_reviews"].extend(review_request.get("pending_reviews", []))
            
            # Add to audit log
            log_action_update = log_action("Human_Advisory_Agent", 
                                         f"Requested payslip verification review for client {client_id}", 
                                         {"issues": payslip_check_data.get("issues_found", [])})
            if "audit_log" in log_action_update:
                if "audit_log" not in new_state:
                    new_state["audit_log"] = []
                new_state["audit_log"].extend(log_action_update["audit_log"])

    # Check if employment corroboration needs review
    if "employment_corroboration" in state and not new_state["human_approvals"].get("employment_corroboration", {}).get("approved"):
        _human_advisory_agent_logger.info(f"Requesting employment corroboration review for client {client_id}")
        corroboration_data = state["employment_corroboration"]
        issues = ["Requires manual verification of employment details"]
        if not corroboration_data.get("consistent", True):
            issues.append("Employment details inconsistent with other verification sources")
            
        review_request = request_human_review(
            verification_type="employment_corroboration",
            client_id=client_id,
            verification_data=corroboration_data,
            issues=issues
        )
        # Merge the review request into our state update
        if "pending_reviews" not in new_state:
            new_state["pending_reviews"] = []
        new_state["pending_reviews"].extend(review_request.get("pending_reviews", []))
        
        # Add to audit log
        log_action_update = log_action("Human_Advisory_Agent", 
                                     f"Requested employment corroboration review for client {client_id}", 
                                     {"issues": issues})
        if "audit_log" in log_action_update:
            if "audit_log" not in new_state:
                new_state["audit_log"] = []
            new_state["audit_log"].extend(log_action_update["audit_log"])
    
    # Check if funds corroboration needs review
    if "funds_corroboration" in state and not new_state["human_approvals"].get("funds_corroboration", {}).get("approved"):
        _human_advisory_agent_logger.info(f"Requesting funds corroboration review for client {client_id}")
        funds_data = state["funds_corroboration"]
        issues = ["Requires manual verification of fund sources"]
        if not funds_data.get("income_consistent", True):
            issues.append("Fund sources inconsistent with declared income")
            
        review_request = request_human_review(
            verification_type="funds_corroboration",
            client_id=client_id,
            verification_data=funds_data,
            issues=issues
        )
        # Merge the review request into our state update
        if "pending_reviews" not in new_state:
            new_state["pending_reviews"] = []
        new_state["pending_reviews"].extend(review_request.get("pending_reviews", []))
        
        # Add to audit log
        log_action_update = log_action("Human_Advisory_Agent", 
                                     f"Requested funds corroboration review for client {client_id}", 
                                     {"issues": issues})
        if "audit_log" in log_action_update:
            if "audit_log" not in new_state:
                new_state["audit_log"] = []
            new_state["audit_log"].extend(log_action_update["audit_log"])

    # Check if there are missing or invalid verification data before summarization
    missing_verifications = []
    if not state.get("id_verification", {}).get("verified", False):
        missing_verifications.append("id_verification")
    if not state.get("payslip_verification", {}).get("verified", False):
        missing_verifications.append("payslip_verification")
    if "web_references" not in state:
        missing_verifications.append("web_references")
    
    if missing_verifications and not new_state.get("human_approvals", {}).get("data_readiness_override", {}).get("approved", False):
        _human_advisory_agent_logger.warning(f"Missing verification data detected: {missing_verifications}")
        
        review_request = request_human_review(
            verification_type="data_readiness_override",
            client_id=client_id,
            verification_data={"missing_verifications": missing_verifications},
            issues=[f"Missing required verification: {missing}" for missing in missing_verifications]
        )
        # Merge the review request into our state update
        if "pending_reviews" not in new_state:
            new_state["pending_reviews"] = []
        new_state["pending_reviews"].extend(review_request.get("pending_reviews", []))
        
        # Add to audit log
        log_action_update = log_action("Human_Advisory_Agent", 
                                     f"Requested data readiness override review for client {client_id}", 
                                     {"missing_verifications": missing_verifications})
        if "audit_log" in log_action_update:
            if "audit_log" not in new_state:
                new_state["audit_log"] = []
            new_state["audit_log"].extend(log_action_update["audit_log"])

    _human_advisory_agent_logger.info("Human advisory checkpoint finished.")
    return new_state


# def process_human_reviews(state: AgentState) -> AgentState:
#     """
#     Process pending human reviews and collect responses.
#     This function is designed to be called from a separate UI, API, or CLI interface
#     to provide human input for the pending reviews.
    
#     Args:
#         state: The current state with pending reviews
        
#     Returns:
#         State update with review responses
#     """
#     from source_of_wealth_agent.core.state import process_review_response
    
#     pending_reviews = state.get("pending_reviews", [])
#     if not pending_reviews:
#         print("No pending reviews to process.")
#         return state
    
#     new_state = state.copy()
#     processed_reviews = []
    
#     for review in pending_reviews:
#         verification_type = review.get("verification_type")
#         client_id = review.get("client_id")
#         issues = review.get("issues", [])
        
#         print(f"\n===== HUMAN REVIEW REQUIRED: {verification_type.replace('_', ' ').title()} =====")
#         print(f"Client ID: {client_id}")
#         print(f"Issues requiring review: {json.dumps(issues, indent=2)}")
        
#         while True:
#             decision = input(f"Approve this {verification_type.replace('_', ' ')}? (yes/no): ").lower().strip()
#             if decision in ["yes", "no"]:
#                 break
#             print("Invalid input. Please enter 'yes' or 'no'.")
        
#         comments = input("Enter any comments (optional): ").strip()
        
#         # Process the response
#         review_response = process_review_response(
#             verification_type=verification_type,
#             approved=(decision == "yes"),
#             reviewer_comments=comments if comments else None,
#             issues_at_review=issues
#         )
        
#         # Merge the response into our state update
#         if "review_responses" not in new_state:
#             new_state["review_responses"] = []
#         new_state["review_responses"].extend(review_response.get("review_responses", []))
        
#         # Update human approvals
#         if "human_approvals" not in new_state:
#             new_state["human_approvals"] = {}
#         for approval_type, approval_detail in review_response.get("human_approvals", {}).items():
#             new_state["human_approvals"][approval_type] = approval_detail
        
#         # Mark this review as processed
#         processed_reviews.append(review)
    
#     # Remove processed reviews from pending
#     if processed_reviews:
#         new_state["pending_reviews"] = [r for r in pending_reviews if r not in processed_reviews]
    
#     return new_state

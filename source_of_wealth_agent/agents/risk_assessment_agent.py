"""
Risk Assessment Agent for the Source of Wealth Agent system.

This module now serves as both the verification planner and final risk assessor.
It determines which verification steps are needed based on client profile,
and performs the final risk assessment after all verifications are completed.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Set

from source_of_wealth_agent.core.state import (
    AgentState, log_action, RiskAssessmentResult, 
    VerificationPlan, VerificationRequirement
)
from langgraph.types import interrupt, Command



def determine_next_action(state: AgentState) -> str:
    """
    Determine the next action to take in the verification workflow
    based on the current state and verification plan.
    
    Args:
        state: Current workflow state
        
    Returns:
        String indicating the next action/node to route to
    """
    # First, check if ID verification has been completed - this is always highest priority
    id_verified = state.get("id_verification", {}).get("verified", None)
    
    # If ID verification hasn't been attempted yet, that's our absolute first priority
    # This must be completed before any other verification steps
    if id_verified is None:
        print("🔍 ID verification not yet attempted - enforcing this as first step")
        return "id_verification"
    
    # If ID verification was attempted but failed without human override, go to human review
    # We cannot proceed with other verifications if ID verification failed
    if id_verified is False and not state.get("human_approvals", {}).get("id_verification", {}).get("approved", False):
        print("⚠️ ID verification failed - requesting human intervention")
        return "human_advisory_node"
    
    # Only proceed with other verifications if ID is successfully verified or has human override
    # This enforces ID verification as a sequential prerequisite to all other verifications
    if id_verified is True or state.get("human_approvals", {}).get("id_verification", {}).get("approved", False):
        print("✅ ID verification passed - proceeding with additional verifications")
        
        # If no verification plan exists yet, create one for the remaining steps
        if "verification_plan" not in state:
            return "planning"
        
        # If web references exist but plan hasn't been updated, analyze them
        if ("web_references" in state and 
            not state["verification_plan"]["verification_requirements"].get("payslip_verification", {}).get("status")):
            return "analyze_web_references"
        if "verification_summary" in state:
        #    If we have a summary, we can proceed to summarization
            return "summary"
        # If there's a specific next verification step, return it
        if "next_verification" in state:
            return state["next_verification"]
        
        # Otherwise check verification completion
        return "check_verification_completion"
        
    
    # Fallback path if we somehow don't match any of the conditions above
    print("⚠️ ID verification status unclear - requesting human review")
    return "human_advisory_node"


def perform_risk_assessment(state: AgentState) -> AgentState:
    """
    Performs the final risk assessment based on all verification results.
    This is called after summarization is complete.
    
    Args:
        state: Current workflow state with all verification results
        
    Returns:
        Updated state with risk assessment results
    """
    print("⚠️ Performing final risk assessment...")
    
    # Gather all verification and corroboration results
    risk_factors = []
    risk_score = 0
    
    # First check if we have the summarization data
    if "verification_summary" in state:
        summary = state["verification_summary"]
        
        # Check verification statuses from summary
        verification_status = summary.get("verification_status", {})
        verification_plan = state.get("verification_plan", {})
        
        # Check ID verification (always required)
        if not verification_status.get("id_verified", False):
            risk_factors.append("ID verification failed or missing")
            risk_score += 30
        
        # Check payslip verification (only if required by plan)
        if verification_plan.get("payslip_verification_required", False):
            if not verification_status.get("payslip_verified", False):
                risk_factors.append("Required payslip verification failed or missing")
                risk_score += 25
            
        # Check web references (always required in our approach)
        if not verification_status.get("web_references_verified", False):
            risk_factors.append("Web references check failed or missing")
            risk_score += 15
            
        # Check financial reports (only if required by plan)
        if verification_plan.get("financial_reports_required", False):
            if not verification_status.get("financial_reports_verified", False):
                risk_factors.append("Required financial reports verification failed or missing")
                risk_score += 20
            
        # Add any risk indicators identified in the summarization
        if "risk_indicators" in summary and summary["risk_indicators"]:
            for indicator in summary["risk_indicators"]:
                if indicator not in risk_factors:  # Avoid duplicates
                    risk_factors.append(indicator)
                    risk_score += 10
    else:
        # Fallback to direct verification checks if summarization is missing
        verification_plan = state.get("verification_plan", {})
        
        # Check ID verification
        if "id_verification" not in state or not state["id_verification"].get("verified", False):
            risk_factors.append("ID verification failed or missing")
            risk_score += 30
        
        # Check payslip verification (only if required)
        if verification_plan.get("payslip_verification_required", False):
            if "payslip_verification" not in state or not state["payslip_verification"].get("verified", False):
                risk_factors.append("Required payslip verification failed or missing")
                risk_score += 25
            
        # Check web references
        if "web_references" not in state or not state["web_references"].get("verified", False):
            risk_factors.append("Web references check failed or missing")
            risk_score += 15
        elif "web_references" in state and "risk_flags" in state["web_references"]:
            for flag in state["web_references"]["risk_flags"]:
                risk_factors.append(f"Web reference risk: {flag}")
                risk_score += 10
                
        # Check financial reports (only if required)
        if verification_plan.get("financial_reports_required", False):
            if "financial_reports" not in state or not state["financial_reports"].get("verified", False):
                risk_factors.append("Required financial reports verification failed or missing")
                risk_score += 20
    
    # Check human approvals (if any)
    for check_name, approval_detail in state.get("human_approvals", {}).items():
        # Handle both simple boolean and detailed approval objects
        if isinstance(approval_detail, dict):
            approved = approval_detail.get("approved", False)
        else:
            approved = bool(approval_detail)
            
        if not approved:
            risk_factors.append(f"Human reviewer rejected {check_name} check")
            risk_score += 15
    
    # Determine risk level using the same scale
    if risk_score == 0:
        risk_level = "Low"
    elif risk_score < 30:
        risk_level = "Medium-Low"
    elif risk_score < 50:
        risk_level = "Medium"
    elif risk_score < 70:
        risk_level = "Medium-High"
    else:
        risk_level = "High"
        
    result: RiskAssessmentResult = {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "assessment_date": datetime.now().isoformat()
    }
    
    new_state = state.copy()
    new_state["risk_assessment"] = result
    log_action( "Risk_Assessment_Agent", "Risk assessment completed", result)
    return new_state


def risk_assessment_agent(state: AgentState) -> AgentState:
    """
    Agent that handles both verification planning and risk assessment.
    
    This agent now serves two purposes:
    1. At the beginning of the workflow: Plan which verifications are needed
    2. After summarization: Perform final risk assessment
    
    The function determines what action to take based on the current state,
    ensuring ID verification is completed before other steps.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with either verification plan or risk assessment results
    """
    # Determine what action to take based on the current state
    action = state.get("risk_assessment_action", "determine_next")
    
    if action == "determine_next":
        next_action = determine_next_action(state)
        print(f"🔄 Risk Assessment Agent determining next action: {next_action}")
        
        # First priority: ID verification must be completed first
        if next_action == "id_verification":
            # Route to ID verification first, wait for it to complete
            new_state = {"next_verification": "id_verification"}
            return log_action( "Risk_Assessment_Agent", 
                             "Prioritizing ID verification as first step", None)
        
        # If ID verification failed, route to human advisory
        if next_action == "human_advisory_node":
            new_state = {"next_agent": "human_advisory_node"}
            return log_action( "Risk_Assessment_Agent", 
                             "Routing to human advisory for review", None)
        
        # Only if ID verification has passed, proceed with other steps
        if next_action == "planning":
            return create_verification_plan(state)
        elif next_action == "analyze_web_references":
            return analyze_web_references(state)
        elif next_action == "check_verification_completion":
            return check_verification_completion(state)
        elif next_action == "summarization":
            # We need summarization next, set the state to indicate this
            new_state = {"next_agent": "summarization_agent"}
            return log_action( "Risk_Assessment_Agent", 
                             "Ready for summarization", None)
        elif next_action in ["payslip_verification", "web_references", "financial_reports"]:
            # We need a specific verification next
            new_state = {"next_agent": f"{next_action}_agent"}
            return log_action( "Risk_Assessment_Agent", 
                              f"Requesting {next_action}", None)
        elif next_action == "summary":
            return perform_risk_assessment(state)
    elif action == "perform_assessment":
        # This action is called after summarization
        return perform_risk_assessment(state)
    
    # If we reach here, it's a fallback - just return the state
    return log_action("Risk_Assessment_Agent", 
                     "No specific action performed", None)


def create_verification_plan(state: AgentState) -> AgentState:
    """
    Creates a verification plan based on client information and any existing data.
    This function is called at the beginning of the process to determine which
    verification steps are needed.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with verification plan
    """
    print("🔍 Creating verification plan for client...")
    
    # Check if ID verification has already been performed
    id_verified = state.get("id_verification", {}).get("verified", None)
    
    # If ID verification hasn't been completed yet, it MUST be completed first
    # This enforces ID verification as a strict sequential prerequisite
    if id_verified is None:
        print("⚠️ SEQUENTIAL ENFORCEMENT: ID verification must be completed before any other verification")
        new_state = {"next_verification": "id_verification"}
        return log_action( "Risk_Assessment_Agent", "Enforcing ID verification as mandatory first step", None)
    
    # Only create full plan if ID is verified or has human override
    if id_verified is True or state.get("human_approvals", {}).get("id_verification", {}).get("approved", False):
        new_state = {}
        client_id = state.get("client_id", "Unknown")
        client_name = state.get("client_name", "Unknown")
        
        # Start with the mandatory checks
        verification_requirements = {
            # "id_verification": {
            #     "verification_type": "id_verification",
            #     "required": True,
            #     "reason": "ID verification is mandatory and must be completed before other verifications",
            #     "status": "completed",  # Mark as completed since we're here
            #     "priority": 1  # Highest priority
            # },
            "web_references": {
                "verification_type": "web_references",
                "required": True,
                "reason": "Web presence analysis is required to determine employment status and risks",
                "status": "pending",
                "priority": 2
            }
        }
        
        # Initial plan - we will add more verifications after web references are analyzed
        # ID verification is ALWAYS required and must be completed first
        plan = {
            "plan_created": datetime.now().isoformat(),
            "id_verification_required": False,
            "payslip_verification_required": False,  # Will be determined after web references
            "web_references_required": True,
            "financial_reports_required": False,  # Will be determined after web references
            "other_verifications": [],
            "verification_requirements": verification_requirements,
            "plan_justification": f"Initial verification plan for client {client_id} ({client_name}). "
                                "ID verification completed as mandatory first step. Web references check will determine "
                                "if payslip or financial report verification is needed."
        }
        
        new_state["verification_plan"] = plan
        new_state["current_verification_step"] = "planning"
        new_state["next_verification"] = "web_references_node"  # Proceed with web references next
        # test = interrupt(state)
        log_action( "Risk_Assessment_Agent", f"Created verification plan for client {client_id}", plan)
        return new_state
    
    else:
        # ID verification failed but no human override, request human intervention
        print("⚠️ ID verification failed - cannot proceed with verification plan")
        new_state = {"next_agent": "human_advisory_node"}
        return log_action( "Risk_Assessment_Agent", "ID verification failed - requesting human review", None)


def analyze_web_references(state: AgentState) -> AgentState:
    """
    Analyzes web references to determine if employment information is found,
    which affects what additional verification is required.
    
    Args:
        state: Current workflow state with web references data
        
    Returns:
        Updated state with modified verification plan
    """
    print("🌐 Analyzing web references to update verification plan...")
    
    if "web_references" not in state:
        return log_action("Risk_Assessment_Agent", 
                         "Cannot analyze web references - data not found", None)
    
    new_state = state.copy()
    verification_plan = state.get("verification_plan", {})
    requirements = verification_plan.get("verification_requirements", {}).copy()
    
    # Extract mentions and look for employment information
    web_data = state["web_references"]
    mentions = web_data.get("mentions", [])
    employment_mentioned = False
    company_names = set()
    position_mentioned = False
    financial_info_mentioned = False
    
    # Analyze mentions for employment information
    for mention in mentions:
        details = mention.get("details", "").lower()
        analysis = mention.get("analysis", {})
        
        # Check if this is a LinkedIn or employment-related mention
        if mention.get("source", "").lower() == "linkedin":
            employment_mentioned = True
        
        # Check if company/employer is mentioned
        if analysis and isinstance(analysis, dict):
            if analysis.get("company"):
                employment_mentioned = True
                company_names.add(analysis.get("company", "").lower())
            if analysis.get("position"):
                position_mentioned = True
        
        # Look for financial keywords
        financial_keywords = ["investor", "investment", "shareholder", "dividend", 
                             "stocks", "bonds", "portfolio", "financial report"]
        if any(keyword in details for keyword in financial_keywords):
            financial_info_mentioned = True
    
    # Update verification requirements based on analysis
    payslip_required = employment_mentioned
    financial_reports_required = financial_info_mentioned or not employment_mentioned
    
    # Add payslip verification if employment was mentioned
    if payslip_required:
        requirements["payslip_verification"] = {
            "verification_type": "payslip_verification",
            "required": True,
            "reason": f"Employment information found in web references: {', '.join(company_names)}",
            "status": "pending",
            "priority": 3
        }
        verification_plan["payslip_verification_required"] = True
        verification_plan["plan_justification"] += " Employment information found in web references, payslip verification required."
    
    # Add financial reports verification if financial info was mentioned or no employment found
    if financial_reports_required:
        requirements["financial_reports"] = {
            "verification_type": "financial_reports",
            "required": not employment_mentioned,  # Only required if no employment found
            "reason": "Financial information found in web references" if financial_info_mentioned else "No employment information found, alternative verification needed",
            "status": "pending",
            "priority": 3 if not employment_mentioned else 4
        }
        verification_plan["financial_reports_required"] = True
        verification_plan["plan_justification"] += " Financial reports verification added."
    
    # Update the verification plan
    verification_plan["verification_requirements"] = requirements
    new_state["verification_plan"] = verification_plan
    
    # Determine the next verification step
    # Always check ID verification first - if it's not done or failed, it takes priority
    id_verified = state.get("id_verification", {}).get("verified", None)
    id_human_approved = state.get("human_approvals", {}).get("id_verification", {}).get("approved", False)
    
    # Enforce sequential ID verification as a prerequisite
    if id_verified is None:
        print("⚠️ SEQUENTIAL ENFORCEMENT: ID verification must be completed first")
        new_state["next_verification"] = "id_verification"
    # If ID verification failed without human override, we need human review
    elif id_verified is False and not id_human_approved:
        print("⚠️ ID verification failed - cannot proceed without human review")
        new_state["next_agent"] = "human_advisory_node"
    # Only if ID verification passed or has human override, proceed with other verifications
    elif payslip_required:
        new_state["next_verification"] = "payslip_verification"
    elif financial_reports_required:
        new_state["next_verification"] = "financial_reports"
    else:
        new_state["next_verification"] = "summarization"
    log_action( "Risk_Assessment_Agent", 
                     "Updated verification plan after web references analysis", 
                     {"payslip_required": payslip_required, 
                      "financial_reports_required": financial_reports_required})
    return new_state


def check_verification_completion(state: AgentState) -> AgentState:
    """
    Checks if all required verifications have been completed.
    Enforces ID verification as a sequential prerequisite.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with verification completion status
    """
    print("✓ Checking verification completion status...")
    
    new_state = state.copy()
    verification_plan = state.get("verification_plan", {})
    requirements = verification_plan.get("verification_requirements", {})
    
    all_required_completed = True
    completed_verifications = []
    missing_verifications = []
    
    # First, check if ID verification has been completed - this is always required
    id_verified = state.get("id_verification", {}).get("verified", None)
    id_human_approved = state.get("human_approvals", {}).get("id_verification", {}).get("approved", False)
    
    # If ID verification hasn't been completed or has failed without override,
    # we cannot proceed with other verifications - enforce sequential requirement
    if id_verified is None:
        print("⚠️ SEQUENTIAL ENFORCEMENT: ID verification must be completed first")
        new_state["next_verification"] = "id_verification"
        return log_action( "Risk_Assessment_Agent", 
                         "ID verification required before checking completion", None)
    elif id_verified is False and not id_human_approved:
        print("⚠️ ID verification failed - must get human review before proceeding")
        new_state["next_agent"] = "human_advisory_node"
        return log_action( "Risk_Assessment_Agent", 
                         "ID verification failed - requesting human review", None)
    
    # Once ID verification is passed or approved, check other verifications
    # Check each required verification
    for req_key, requirement in requirements.items():
        if requirement.get("required", False):
            verification_type = requirement["verification_type"]
            verification_data = state.get(verification_type)
            
            if verification_data and verification_data.get("verified", False):
                completed_verifications.append(verification_type)
                requirement["status"] = "completed"
            else:
                missing_verifications.append(verification_type)
                requirement["status"] = "pending"
                all_required_completed = False
    
    # Update the verification plan with current status
    verification_plan["verification_requirements"] = requirements
    new_state["verification_plan"] = verification_plan
    new_state["completed_verifications"] = completed_verifications
    
    if all_required_completed:
        new_state["next_verification"] = "summarization"
        print("✅ All required verifications completed!")
    else:
        # Find the highest priority missing verification
        highest_priority = 999
        next_verification = None
        
        for req_key, requirement in requirements.items():
            if requirement.get("required", False) and requirement["status"] == "pending":
                if requirement["priority"] < highest_priority:
                    highest_priority = requirement["priority"]
                    next_verification = requirement["verification_type"]
        
        if next_verification:
            new_state["next_verification"] = next_verification
            print(f"⏳ Next verification needed: {next_verification}")
        else:
            new_state["next_verification"] = "summarization"
            print("⚠️ No specific next verification identified, proceeding to summarization")
    log_action( "Risk_Assessment_Agent", 
                     "Verification completion check", 
                     {"all_completed": all_required_completed, 
                      "completed": completed_verifications, 
                      "missing": missing_verifications})
    return new_state
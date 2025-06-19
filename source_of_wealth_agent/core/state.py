from typing import TypedDict, Optional, List, Dict, Any, Annotated
from datetime import datetime

class IDVerificationResult(TypedDict, total=False):
    verified: bool
    confidence: float
    issues_found: bool
    issues: List[str]
    verification_date: str

class PayslipVerificationResult(TypedDict, total=False):
    verified: bool
    confidence: float
    issues_found: bool
    issues: List[str]
    verification_date: str

class WebReferenceResult(TypedDict, total=False):
    verified: bool
    confidence: float
    issues_found: bool
    issues: List[str]
    verification_date: str

class FinancialReportResult(TypedDict, total=False):
    verified: bool
    confidence: float
    issues_found: bool
    issues: List[str]
    verification_date: str

class VerificationPlan(TypedDict, total=False):
    steps: List[str]
    priority: Dict[str, float]
    next_step: str

class AuditLogEntry(TypedDict, total=False):
    timestamp: str
    agent: str
    action: str
    result: Dict[str, Any]

class FundCorroborationResult(CorroborationResult):
    income_consistent: bool
    analysis: str

class RiskAssessmentResult(TypedDict):
    risk_score: int
    risk_level: str
    risk_factors: List[str]
    assessment_date: str

class HumanApprovalDetail(TypedDict):
    approved: bool
    review_date: str
    issues_at_review: Optional[List[str]]
    reviewer_comments: Optional[str] # Optional field for comments

class AuditLogEntry(TypedDict):
    timestamp: str
    agent: str
    action: str
    result: Any

# New types to support dynamic verification planning
class VerificationRequirement(TypedDict, total=False):
    """Represents a verification step that needs to be performed"""
    verification_type: str  # "id", "payslip", "web_references", "financial_reports", etc.
    required: bool  # True if this verification is mandatory, False if optional
    reason: str  # Why this verification is needed
    status: str  # "pending", "in_progress", "completed", "failed", "skipped"
    priority: int  # 1 = highest priority

class ReviewItem(TypedDict):
    """Information about an item requiring human review"""
    verification_type: str  # "id", "payslip", "web_references", "financial_reports", "summarization"
    client_id: str
    verification_data: Dict[str, Any]  # The verification result requiring review
    issues: List[str]  # List of issues requiring review
    requested_at: str  # ISO timestamp when review was requested
    status: str  # "pending", "awaiting_review", "reviewed"

class VerificationPlan(TypedDict):
    """Overall plan for verifying a client's source of wealth"""
    plan_created: str  # ISO timestamp
    id_verification_required: bool
    payslip_verification_required: bool
    web_references_required: bool
    financial_reports_required: bool
    other_verifications: List[str]  # Any additional verification methods needed
    verification_requirements: Dict[str, VerificationRequirement]
    plan_justification: str  # Explanation of why this plan was created

# Main state dictionary structure
class AgentState(TypedDict, total=False):
    # Client information
    client_id: Annotated[str, "merge"] 
    client_name: Optional[str]
    client_data: Dict[str, Any]
    messages: Annotated[List[str], operator.add]  # Multiple agents can add messages
    
    # Verification results
    id_verification: IDVerificationResult
    payslip_verification: PayslipVerificationResult
    web_references: WebReferenceResult
    financial_reports: FinancialReportResult
    
    # Analysis results
    employment_corroboration: CorroborationResult
    funds_corroboration: FundCorroborationResult
    
    # Verification planning and tracking
    verification_plan: VerificationPlan
    current_verification_step: str  # The current step being performed
    completed_verifications: Annotated[List[str], operator.add]  # Multiple agents can add completed verifications
    
    # Final results
    risk_assessment: RiskAssessmentResult
    summarization_output: Dict[str, Any]
    verification_summary: Dict[str, Any]  # Output from summarization_agent
    final_report: str
    
    # Process management
    human_approvals: Dict[str, Union[bool, HumanApprovalDetail]]
    next_agent: Optional[str]
    audit_log: Annotated[List[AuditLogEntry], operator.add]  # Multiple agents can add to audit log
    action_history: Annotated[List[Dict[str, Any]], operator.add]  # Multiple agents can add to action history
    errors: Annotated[List[Dict[str, Any]], operator.add]  # Multiple agents can report errors
    
    # Asynchronous human review management
    pending_reviews: Annotated[List[ReviewItem], operator.add]  # Reviews waiting for human input
    review_responses: Annotated[List[Dict[str, Any]], operator.add]  # Responses from human reviewers


def create_initial_state(client_id: str, client_name: Optional[str] = None) -> AgentState:
    """
    Create an empty initial state with the given client ID and optional name.
    
    Args:
        client_id: The unique identifier for the client
        client_name: The name of the client (optional)
        
    Returns:
        A new AgentState instance with basic information initialized
    """
    return {
        "client_id": client_id,
        "client_name": client_name,
        "client_data": {},
        "messages": [],
        "human_approvals": {},
        "completed_verifications": [],
        "audit_log": [],
        "action_history": [],
        "errors": [],
        "pending_reviews": [],
        "review_responses": []
    }


def log_action(agent_name: str, action: str, result: Any = None) -> AgentState:
    """
    Add an entry to the audit log.
    
    Args:
        state: The current state
        agent_name: Name of the agent performing the action
        action: Description of the action being performed
        result: Optional result data from the action
        
    Returns:
        Updated state with the new log entry
    """
    # Create a new audit log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "action": action,
        "result": result
    }
    
    # Create a minimal state update with just the new audit log entry
    state_update = {"audit_log": [log_entry]}
    
    # Return the state update - this will be properly merged by LangGraph
    # when using Annotated[List, operator.add]
    return state_update


def request_human_review(verification_type: str, client_id: str, verification_data: Dict[str, Any], 
                        issues: List[str]) -> AgentState:
    """
    Request a human review without blocking execution.
    
    Args:
        verification_type: Type of verification requiring review (id, payslip, web_references, etc.)
        client_id: The client ID
        verification_data: The verification data requiring review
        issues: List of issues requiring review
        
    Returns:
        State update with the new review request
    """
    review_item = {
        "verification_type": verification_type,
        "client_id": client_id,
        "verification_data": verification_data,
        "issues": issues,
        "requested_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    # Create a state update with just the new review request
    return {"pending_reviews": [review_item]}


def process_review_response(verification_type: str, approved: bool, 
                           reviewer_comments: Optional[str] = None, 
                           issues_at_review: Optional[List[str]] = None) -> AgentState:
    """
    Process a human review response.
    
    Args:
        verification_type: Type of verification reviewed
        approved: Whether the verification was approved
        reviewer_comments: Optional comments from the reviewer
        issues_at_review: Optional list of issues noted during review
        
    Returns:
        State update with the review response
    """
    response = {
        "verification_type": verification_type,
        "approved": approved,
        "review_date": datetime.now().isoformat(),
        "reviewer_comments": reviewer_comments,
        "issues_at_review": issues_at_review or []
    }
    
    # Create a state update with the review response
    state_update = {
        "review_responses": [response],
        "human_approvals": {
            verification_type: {
                "approved": approved,
                "review_date": response["review_date"],
                "issues_at_review": issues_at_review or [],
                "reviewer_comments": reviewer_comments
            }
        }
    }
    
    return state_update


def get_pending_reviews(state: AgentState) -> List[ReviewItem]:
    """
    Get all pending reviews from the state.
    
    Args:
        state: The current state
        
    Returns:
        List of pending review items
    """
    return state.get("pending_reviews", [])


def has_pending_review(state: AgentState, verification_type: str) -> bool:
    """
    Check if a specific verification type has a pending review.
    
    Args:
        state: The current state
        verification_type: The verification type to check
        
    Returns:
        True if there is a pending review for this verification type
    """
    pending_reviews = state.get("pending_reviews", [])
    return any(review["verification_type"] == verification_type for review in pending_reviews)
"""
State management classes and functions for the Source of Wealth Agent system.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, TypedDict, Union

# Define state management using TypedDict for better type safety
class VerificationResult(TypedDict, total=False):
    verified: bool
    verification_date: str
    # Additional fields can be added by specific verifications

class IDVerificationResult(VerificationResult):
    id_expiry: str
    id_type: str
    issues_found: List[str]

class PayslipVerificationResult(VerificationResult):
    monthly_income: float
    employer: str
    position: str

class WebReferenceResult(VerificationResult):
    mentions: List[Dict[str, str]]
    risk_flags: List[str]
    search_date: str

class FinancialReportResult(VerificationResult):
    reports_analyzed: List[str]
    annual_income_range: str
    investment_assets: str
    credit_score: str
    analysis_date: str

class CorroborationResult(TypedDict, total=False):
    consistent: bool
    confidence: str
    corroboration_date: str
    # Additional fields can be added by specific corroborations

class FundCorroborationResult(CorroborationResult):
    income_consistent: bool
    analysis: str

class RiskAssessmentResult(TypedDict):
    risk_score: int
    risk_level: str
    risk_factors: List[str]
    assessment_date: str

class AuditLogEntry(TypedDict):
    timestamp: str
    agent: str
    action: str
    result: Any

# Main state class that will be passed between agents
class AgentState(TypedDict, total=False):
    # Client information
    client_id: str
    client_name: Optional[str]
    client_data: Dict[str, Any]
    messages: List[str]
    
    # Verification results
    id_verification: Optional[IDVerificationResult]
    payslip_verification: Optional[PayslipVerificationResult]
    web_references: Optional[WebReferenceResult]
    financial_reports: Optional[FinancialReportResult]
    
    # Analysis results
    employment_corroboration: Optional[CorroborationResult]
    funds_corroboration: Optional[FundCorroborationResult]
    investment_corroboration: Optional[CorroborationResult]
    
    # Final results
    risk_assessment: Optional[RiskAssessmentResult]
    final_report: Optional[str]
    
    # Process management
    human_approvals: Dict[str, bool]
    next_agent: Optional[str]
    audit_log: List[AuditLogEntry]


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
        "audit_log": []
    }


def log_action(state: AgentState, agent_name: str, action: str, result: Any = None) -> AgentState:
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
    new_state = state.copy()
    if "audit_log" not in new_state:
        new_state["audit_log"] = []
    
    new_state["audit_log"].append({
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "action": action,
        "result": result
    })
    return new_state
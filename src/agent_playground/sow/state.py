"""State management for Source of Wealth analysis."""

from datetime import datetime
from typing import Dict, List, Any, Optional, TypedDict, Annotated, Union
from pydantic import BaseModel, Field
from pathlib import Path
import operator

from ..core.base import AgentState


class VerificationResult(BaseModel):
    """Base verification result."""
    verified: bool = False
    verification_date: datetime = Field(default_factory=datetime.now)
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    issues_found: List[str] = Field(default_factory=list)
    additional_data: Dict[str, Any] = Field(default_factory=dict)


class IDVerificationResult(VerificationResult):
    """ID verification specific result."""
    id_type: Optional[str] = None
    id_expiry: Optional[datetime] = None
    document_quality: str = "unknown"
    extracted_info: Dict[str, str] = Field(default_factory=dict)


class PayslipVerificationResult(VerificationResult):
    """Payslip verification specific result."""
    monthly_income: Optional[float] = None
    employer: Optional[str] = None
    position: Optional[str] = None
    pay_period: Optional[str] = None
    deductions: Dict[str, float] = Field(default_factory=dict)


class WebReferenceResult(VerificationResult):
    """Web reference verification result."""
    mentions: List[Dict[str, str]] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    sources_found: int = 0
    credibility_score: float = Field(0.0, ge=0.0, le=1.0)


class FinancialReportResult(VerificationResult):
    """Financial report analysis result."""
    reports_analyzed: List[str] = Field(default_factory=list)
    annual_income_range: Optional[str] = None
    investment_assets: Optional[str] = None
    credit_score: Optional[str] = None
    financial_stability: str = "unknown"


class RiskAssessmentResult(BaseModel):
    """Risk assessment result."""
    risk_score: int = Field(0, ge=0, le=100)
    risk_level: str = "unknown"
    risk_factors: List[str] = Field(default_factory=list)
    assessment_date: datetime = Field(default_factory=datetime.now)
    recommendations: List[str] = Field(default_factory=list)


class CorroborationResult(BaseModel):
    """Data corroboration result."""
    consistent: bool = False
    confidence: str = "low"
    corroboration_date: datetime = Field(default_factory=datetime.now)
    discrepancies: List[str] = Field(default_factory=list)
    analysis: str = ""


class SOWDocuments(BaseModel):
    """Document collection for SOW verification."""
    id_document: Optional[Path] = None
    payslip: Optional[Path] = None
    bank_statement: Optional[Path] = None
    employment_letter: Optional[Path] = None
    tax_document: Optional[Path] = None
    
    def to_paths_dict(self) -> Dict[str, Optional[str]]:
        """Convert to dictionary of string paths for compatibility."""
        return {
            'id_document_path': str(self.id_document) if self.id_document else None,
            'payslip_document_path': str(self.payslip) if self.payslip else None,
            'bank_statement_path': str(self.bank_statement) if self.bank_statement else None,
            'employment_letter_path': str(self.employment_letter) if self.employment_letter else None,
            'tax_document_path': str(self.tax_document) if self.tax_document else None,
        }


class SOWState(AgentState):
    """State for Source of Wealth analysis workflow."""
    
    # Client information
    client_id: str
    client_name: str
    
    # Document paths
    id_document_path: Optional[str] = None
    payslip_document_path: Optional[str] = None
    financial_report_paths: List[str] = Field(default_factory=list)
    
    # Verification results
    id_verification: Optional[IDVerificationResult] = None
    payslip_verification: Optional[PayslipVerificationResult] = None
    web_references: Optional[WebReferenceResult] = None
    financial_reports: Optional[FinancialReportResult] = None
    
    # Analysis results
    risk_assessment: Optional[RiskAssessmentResult] = None
    fund_corroboration: Optional[CorroborationResult] = None
    
    # Workflow control
    needs_human_review: bool = False
    human_review_completed: bool = False
    human_feedback: Optional[str] = None
    
    # Final outputs
    final_report: Optional[str] = None
    summary: Optional[str] = None
    
    # Messages for agent communication
    messages: Annotated[List[Dict[str, Any]], operator.add] = Field(default_factory=list)
    
    # Progress tracking
    completed_steps: Annotated[List[str], operator.add] = Field(default_factory=list)
    current_step: str = "initialization"
    
    def add_message(self, agent: str, message: str, message_type: str = "info"):
        """Add a message to the state."""
        self.messages.append({
            "agent": agent,
            "message": message,
            "type": message_type,
            "timestamp": datetime.now().isoformat()
        })
    
    def mark_step_completed(self, step: str):
        """Mark a workflow step as completed."""
        if step not in self.completed_steps:
            self.completed_steps.append(step)
    
    def get_progress_percentage(self) -> float:
        """Calculate workflow progress percentage."""
        total_steps = [
            "id_verification",
            "payslip_verification", 
            "web_references",
            "financial_reports",
            "risk_assessment",
            "corroboration",
            "report_generation"
        ]
        completed = len([s for s in total_steps if s in self.completed_steps])
        return (completed / len(total_steps)) * 100

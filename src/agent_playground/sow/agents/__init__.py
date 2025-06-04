"""Source of Wealth analysis agents."""

from .id_verification import IDVerificationAgent
from .payslip_verification import PayslipVerificationAgent
from .web_references import WebReferencesAgent
from .financial_reports import FinancialReportsAgent
from .risk_assessment import RiskAssessmentAgent
from .report_generation import ReportGenerationAgent
from .human_advisory import HumanAdvisoryAgent

__all__ = [
    "IDVerificationAgent",
    "PayslipVerificationAgent", 
    "WebReferencesAgent",
    "FinancialReportsAgent",
    "RiskAssessmentAgent",
    "ReportGenerationAgent",
    "HumanAdvisoryAgent",
]

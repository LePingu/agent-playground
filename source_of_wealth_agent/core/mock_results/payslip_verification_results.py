"""
Mock results for the Payslip Verification Agent.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

def get_mock_payslip_verification_result(
    client_id: str, 
    client_name: str = None, 
    verified: bool = True,
    monthly_income: float = 15000.0,
    employer: str = "Global Bank Ltd",
    position: str = "Senior Manager"
) -> Dict[str, Any]:
    """
    Generate a mock payslip verification result.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        verified: Whether the payslip is verified (default: True)
        monthly_income: The monthly income (default: 15000.0)
        employer: The employer name (default: "Global Bank Ltd")
        position: The job position (default: "Senior Manager")
        
    Returns:
        A mock payslip verification result
    """
    current_date = datetime.now().isoformat()
    
    if verified:
        # Return a successful verification result
        return {
            "verified": True,
            "monthly_income": monthly_income,
            "employer": employer,
            "position": position,
            "employee_name": client_name or f"Client {client_id}",
            "gross_pay": monthly_income,
            "net_pay": monthly_income * 0.7,  # Approximate after tax
            "pay_period": "Monthly",
            "issues_found": [],
            "verification_date": current_date
        }
    else:
        # Return a failed verification result with issues
        return {
            "verified": False,
            "monthly_income": monthly_income,
            "employer": employer,
            "position": position,
            "employee_name": client_name or f"Client {client_id}",
            "gross_pay": monthly_income,
            "net_pay": monthly_income * 0.7,  # Approximate after tax
            "pay_period": "Monthly",
            "issues_found": ["Inconsistent income figures", "Missing employer details"],
            "verification_date": current_date
        }

def get_mock_payslip_verification_result_with_specific_issues(
    client_id: str, 
    client_name: str = None, 
    issues: List[str] = None,
    monthly_income: float = 15000.0,
    employer: str = "Global Bank Ltd",
    position: str = "Senior Manager",
    requires_human_review: bool = False
) -> Dict[str, Any]:
    """
    Generate a mock payslip verification result with specific issues.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        issues: List of specific issues to include (optional)
        monthly_income: The monthly income (default: 15000.0)
        employer: The employer name (default: "Global Bank Ltd")
        position: The job position (default: "Senior Manager")
        requires_human_review: Whether human review is required (default: False)
        
    Returns:
        A mock payslip verification result with the specified issues
    """
    current_date = datetime.now().isoformat()
    
    # Default issues if none provided
    if issues is None:
        issues = []
    
    # Determine if verified based on presence of issues
    verified = len(issues) == 0 and not requires_human_review
    
    result = {
        "verified": verified,
        "monthly_income": monthly_income,
        "employer": employer,
        "position": position,
        "employee_name": client_name or f"Client {client_id}",
        "gross_pay": monthly_income,
        "net_pay": monthly_income * 0.7,  # Approximate after tax
        "pay_period": "Monthly",
        "issues_found": issues,
        "verification_date": current_date
    }
    
    if requires_human_review:
        result["requires_human_review"] = True
    
    return result

def get_mock_payslip_verification_result_with_pending_review(
    client_id: str,
    client_name: str = None,
    issues: List[str] = ["Requires manual verification"],
    monthly_income: float = 15000.0,
    employer: str = "Global Bank Ltd",
    position: str = "Senior Manager"
) -> Dict[str, Any]:
    """
    Generate a mock payslip verification result with pending human review.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        issues: List of issues requiring review (default: ["Requires manual verification"])
        monthly_income: The monthly income (default: 15000.0)
        employer: The employer name (default: "Global Bank Ltd")
        position: The job position (default: "Senior Manager")
        
    Returns:
        A mock payslip verification result with pending human review
    """
    # Get a basic result with issues and requiring human review
    result = get_mock_payslip_verification_result_with_specific_issues(
        client_id=client_id,
        client_name=client_name,
        issues=issues,
        monthly_income=monthly_income,
        employer=employer,
        position=position,
        requires_human_review=True
    )
    
    # Add pending review information
    result["pending_review"] = {
        "verification_type": "payslip_verification_review",
        "client_id": client_id,
        "requested_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    return result

# Sample usage:
# result = get_mock_payslip_verification_result("12345", "John Doe", True)
# result_with_issues = get_mock_payslip_verification_result("12345", "John Doe", False)
# result_with_specific_issues = get_mock_payslip_verification_result_with_specific_issues(
#     "12345", "John Doe", ["Inconsistent income figures", "Suspicious formatting"]
# )
# result_with_pending_review = get_mock_payslip_verification_result_with_pending_review("12345", "John Doe")

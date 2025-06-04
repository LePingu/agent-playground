"""
Mock results for the Source of Wealth Agent system.

This package provides mock results for the various verification agents in the system.
"""

from source_of_wealth_agent.core.mock_results.id_verification_results import (
    get_mock_id_verification_result,
    get_mock_id_verification_result_with_specific_issues
)

from source_of_wealth_agent.core.mock_results.payslip_verification_results import (
    get_mock_payslip_verification_result,
    get_mock_payslip_verification_result_with_specific_issues,
    get_mock_payslip_verification_result_with_pending_review
)

from source_of_wealth_agent.core.mock_results.web_references_results import (
    get_mock_web_references_result,
    get_mock_web_references_result_with_specific_risk_flags
)

from source_of_wealth_agent.core.mock_results.financial_reports_results import (
    get_mock_financial_reports_result,
    get_mock_financial_reports_result_with_specific_issues,
    get_mock_financial_reports_result_with_high_net_worth,
    get_mock_financial_reports_result_with_moderate_wealth
)

def get_mock_client_verification_results(
    client_id: str,
    client_name: str = None,
    all_verified: bool = True
) -> dict:
    """
    Generate a complete set of mock verification results for a client.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        all_verified: Whether all verifications should pass (default: True)
        
    Returns:
        A dictionary containing all verification results
    """
    # Generate mock results for each verification type
    id_verification = get_mock_id_verification_result(
        client_id=client_id,
        client_name=client_name,
        verified=all_verified
    )
    
    payslip_verification = get_mock_payslip_verification_result(
        client_id=client_id,
        client_name=client_name,
        verified=all_verified
    )
    
    web_references = get_mock_web_references_result(
        client_id=client_id,
        client_name=client_name,
        verified=all_verified,
        employer=payslip_verification.get("employer", "Global Bank Ltd")
    )
    
    financial_reports = get_mock_financial_reports_result(
        client_id=client_id,
        client_name=client_name,
        verified=all_verified
    )
    
    # Combine all results into a single state dictionary
    return {
        "client_id": client_id,
        "client_name": client_name or f"Client {client_id}",
        "id_verification": id_verification,
        "payslip_verification": payslip_verification,
        "web_references": web_references,
        "financial_reports": financial_reports
    }

def get_mock_client_verification_results_with_specific_issues(
    client_id: str,
    client_name: str = None,
    id_issues: list = None,
    payslip_issues: list = None,
    web_risk_flags: list = None,
    financial_issues: list = None
) -> dict:
    """
    Generate a complete set of mock verification results for a client with specific issues.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        id_issues: List of ID verification issues (optional)
        payslip_issues: List of payslip verification issues (optional)
        web_risk_flags: List of web references risk flags (optional)
        financial_issues: List of financial reports issues (optional)
        
    Returns:
        A dictionary containing all verification results with the specified issues
    """
    # Generate mock results for each verification type with specific issues
    id_verification = get_mock_id_verification_result_with_specific_issues(
        client_id=client_id,
        client_name=client_name,
        issues=id_issues or []
    )
    
    payslip_verification = get_mock_payslip_verification_result_with_specific_issues(
        client_id=client_id,
        client_name=client_name,
        issues=payslip_issues or []
    )
    
    web_references = get_mock_web_references_result_with_specific_risk_flags(
        client_id=client_id,
        client_name=client_name,
        risk_flags=web_risk_flags or [],
        employer=payslip_verification.get("employer", "Global Bank Ltd")
    )
    
    financial_reports = get_mock_financial_reports_result_with_specific_issues(
        client_id=client_id,
        client_name=client_name,
        issues=financial_issues or []
    )
    
    # Combine all results into a single state dictionary
    return {
        "client_id": client_id,
        "client_name": client_name or f"Client {client_id}",
        "id_verification": id_verification,
        "payslip_verification": payslip_verification,
        "web_references": web_references,
        "financial_reports": financial_reports
    }

def get_mock_high_risk_client_verification_results(
    client_id: str,
    client_name: str = None
) -> dict:
    """
    Generate a complete set of mock verification results for a high-risk client.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        
    Returns:
        A dictionary containing all verification results for a high-risk client
    """
    return get_mock_client_verification_results_with_specific_issues(
        client_id=client_id,
        client_name=client_name,
        id_issues=["Suspicious document features", "Potential forgery detected"],
        payslip_issues=["Inconsistent income figures", "Employer cannot be verified"],
        web_risk_flags=["PEP status identified", "Negative news mentions", "Regulatory investigations"],
        financial_issues=["Unexplained large transactions", "Inconsistent income reporting"]
    )

def get_mock_medium_risk_client_verification_results(
    client_id: str,
    client_name: str = None
) -> dict:
    """
    Generate a complete set of mock verification results for a medium-risk client.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        
    Returns:
        A dictionary containing all verification results for a medium-risk client
    """
    return get_mock_client_verification_results_with_specific_issues(
        client_id=client_id,
        client_name=client_name,
        id_issues=[],  # ID verification passes
        payslip_issues=["Requires manual verification"],  # Minor payslip issue
        web_risk_flags=["PEP status identified"],  # PEP status is a medium risk
        financial_issues=[]  # Financial reports pass
    )

def get_mock_low_risk_client_verification_results(
    client_id: str,
    client_name: str = None
) -> dict:
    """
    Generate a complete set of mock verification results for a low-risk client.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        
    Returns:
        A dictionary containing all verification results for a low-risk client
    """
    # All verifications pass, but with high net worth
    result = get_mock_client_verification_results(
        client_id=client_id,
        client_name=client_name,
        all_verified=True
    )
    
    # Replace financial reports with high net worth version
    result["financial_reports"] = get_mock_financial_reports_result_with_high_net_worth(
        client_id=client_id,
        client_name=client_name
    )
    
    return result

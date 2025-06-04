"""
Mock results for the Financial Reports Agent.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

def get_mock_financial_reports_result(
    client_id: str, 
    client_name: str = None, 
    verified: bool = True,
    annual_income_range: str = "100,000 - 200,000",
    investment_assets: str = "500,000+",
    credit_score: str = "Excellent"
) -> Dict[str, Any]:
    """
    Generate a mock financial reports verification result.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        verified: Whether the financial reports are verified (default: True)
        annual_income_range: The annual income range (default: "100,000 - 200,000")
        investment_assets: The investment assets value (default: "500,000+")
        credit_score: The credit score rating (default: "Excellent")
        
    Returns:
        A mock financial reports verification result
    """
    current_date = datetime.now().isoformat()
    
    # Default reports to analyze
    reports_analyzed = ["Credit Report", "Investment Portfolio", "Tax Returns"]
    
    # Create the result
    result = {
        "verified": verified,
        "reports_analyzed": reports_analyzed,
        "annual_income_range": annual_income_range,
        "investment_assets": investment_assets,
        "credit_score": credit_score,
        "analysis_date": current_date
    }
    
    # Add issues if not verified
    if not verified:
        result["issues_found"] = [
            "Inconsistent income reporting across documents",
            "Unexplained large transactions"
        ]
    else:
        result["issues_found"] = []
    
    # Add detailed analysis if available
    if verified:
        result["detailed_analysis"] = {
            "credit_report": {
                "score": get_credit_score_number(credit_score),
                "payment_history": "Excellent",
                "utilization": "Low",
                "derogatory_marks": 0,
                "length_of_history": "10+ years"
            },
            "investment_portfolio": {
                "asset_classes": ["Stocks", "Bonds", "Real Estate", "Alternative Investments"],
                "diversification": "Well diversified",
                "risk_profile": "Moderate",
                "major_holdings": [
                    {"type": "Stocks", "percentage": 45},
                    {"type": "Bonds", "percentage": 30},
                    {"type": "Real Estate", "percentage": 15},
                    {"type": "Alternative", "percentage": 10}
                ]
            },
            "tax_returns": {
                "years_analyzed": ["2022", "2023", "2024"],
                "income_consistency": "High",
                "income_sources": ["Employment", "Investments", "Rental Income"],
                "tax_compliance": "Compliant"
            }
        }
    
    return result

def get_mock_financial_reports_result_with_specific_issues(
    client_id: str, 
    client_name: str = None, 
    issues: List[str] = None,
    annual_income_range: str = "100,000 - 200,000",
    investment_assets: str = "500,000+",
    credit_score: str = "Excellent"
) -> Dict[str, Any]:
    """
    Generate a mock financial reports verification result with specific issues.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        issues: List of specific issues to include (optional)
        annual_income_range: The annual income range (default: "100,000 - 200,000")
        investment_assets: The investment assets value (default: "500,000+")
        credit_score: The credit score rating (default: "Excellent")
        
    Returns:
        A mock financial reports verification result with the specified issues
    """
    # Ensure issues is a list
    if issues is None:
        issues = []
    
    # Determine if verified based on presence of issues
    verified = len(issues) == 0
    
    # Get the basic result
    result = get_mock_financial_reports_result(
        client_id=client_id,
        client_name=client_name,
        verified=verified,
        annual_income_range=annual_income_range,
        investment_assets=investment_assets,
        credit_score=credit_score
    )
    
    # Override issues with the provided list
    result["issues_found"] = issues
    
    # If there are issues, adjust the detailed analysis to reflect them
    if issues and "detailed_analysis" in result:
        # Modify the detailed analysis based on the issues
        for issue in issues:
            if "credit" in issue.lower():
                result["detailed_analysis"]["credit_report"]["score"] = get_credit_score_number("Fair")
                result["detailed_analysis"]["credit_report"]["payment_history"] = "Fair"
                result["detailed_analysis"]["credit_report"]["derogatory_marks"] = 2
            elif "income" in issue.lower() or "tax" in issue.lower():
                result["detailed_analysis"]["tax_returns"]["income_consistency"] = "Low"
                result["detailed_analysis"]["tax_returns"]["tax_compliance"] = "Potential issues identified"
            elif "investment" in issue.lower() or "asset" in issue.lower():
                result["detailed_analysis"]["investment_portfolio"]["diversification"] = "Concentrated"
                result["detailed_analysis"]["investment_portfolio"]["risk_profile"] = "High"
                result["detailed_analysis"]["investment_portfolio"]["major_holdings"] = [
                    {"type": "Single Stock", "percentage": 70},
                    {"type": "Bonds", "percentage": 10},
                    {"type": "Real Estate", "percentage": 15},
                    {"type": "Cash", "percentage": 5}
                ]
    
    return result

def get_mock_financial_reports_result_with_high_net_worth(
    client_id: str, 
    client_name: str = None
) -> Dict[str, Any]:
    """
    Generate a mock financial reports verification result for a high net worth individual.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        
    Returns:
        A mock financial reports verification result for a high net worth individual
    """
    return get_mock_financial_reports_result(
        client_id=client_id,
        client_name=client_name,
        verified=True,
        annual_income_range="500,000 - 1,000,000",
        investment_assets="5,000,000+",
        credit_score="Excellent"
    )

def get_mock_financial_reports_result_with_moderate_wealth(
    client_id: str, 
    client_name: str = None
) -> Dict[str, Any]:
    """
    Generate a mock financial reports verification result for an individual with moderate wealth.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        
    Returns:
        A mock financial reports verification result for an individual with moderate wealth
    """
    return get_mock_financial_reports_result(
        client_id=client_id,
        client_name=client_name,
        verified=True,
        annual_income_range="100,000 - 200,000",
        investment_assets="250,000 - 500,000",
        credit_score="Good"
    )

# Helper functions

def get_credit_score_number(rating: str) -> int:
    """Convert a credit score rating to a numeric value."""
    ratings = {
        "Excellent": 800,
        "Very Good": 750,
        "Good": 700,
        "Fair": 650,
        "Poor": 600,
        "Very Poor": 550
    }
    return ratings.get(rating, 700)  # Default to "Good" if rating not found

# Sample usage:
# result = get_mock_financial_reports_result("12345", "John Doe", True)
# result_with_issues = get_mock_financial_reports_result("12345", "John Doe", False)
# result_with_specific_issues = get_mock_financial_reports_result_with_specific_issues(
#     "12345", "John Doe", ["Unexplained large transactions", "Recent credit inquiries"]
# )
# high_net_worth_result = get_mock_financial_reports_result_with_high_net_worth("12345", "John Doe")
# moderate_wealth_result = get_mock_financial_reports_result_with_moderate_wealth("12345", "John Doe")

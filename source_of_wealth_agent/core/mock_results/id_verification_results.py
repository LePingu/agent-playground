"""
Mock results for the ID Verification Agent.
"""

from datetime import datetime
from typing import Dict, Any, List

def get_mock_id_verification_result(client_id: str, client_name: str = None, verified: bool = True) -> Dict[str, Any]:
    """
    Generate a mock ID verification result.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        verified: Whether the ID is verified (default: True)
        
    Returns:
        A mock ID verification result
    """
    current_date = datetime.now().isoformat()
    
    if verified:
        # Return a successful verification result
        return {
            "verified": True,
            "id_type": "Passport",
            "full_name": client_name or f"Client {client_id}",
            "date_of_birth": "1985-06-22",
            "document_number": f"P{client_id}12345",
            "id_expiry": "2030-01-15",
            "issues_found": [],
            "verification_date": current_date
        }
    else:
        # Return a failed verification result with issues
        return {
            "verified": False,
            "id_type": "Passport",
            "full_name": client_name or f"Client {client_id}",
            "date_of_birth": "1985-06-22",
            "document_number": f"P{client_id}12345",
            "id_expiry": "2023-01-15",  # Expired ID
            "issues_found": ["ID document has expired", "Signature mismatch"],
            "verification_date": current_date
        }

def get_mock_id_verification_result_with_specific_issues(
    client_id: str, 
    client_name: str = None, 
    issues: List[str] = None
) -> Dict[str, Any]:
    """
    Generate a mock ID verification result with specific issues.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        issues: List of specific issues to include (optional)
        
    Returns:
        A mock ID verification result with the specified issues
    """
    current_date = datetime.now().isoformat()
    
    # Default issues if none provided
    if issues is None:
        issues = []
    
    # Determine if verified based on presence of issues
    verified = len(issues) == 0
    
    return {
        "verified": verified,
        "id_type": "Passport",
        "full_name": client_name or f"Client {client_id}",
        "date_of_birth": "1985-06-22",
        "document_number": f"P{client_id}12345",
        "id_expiry": "2030-01-15" if verified else "2023-01-15",
        "issues_found": issues,
        "verification_date": current_date
    }

# Sample usage:
# result = get_mock_id_verification_result("12345", "John Doe", True)
# result_with_issues = get_mock_id_verification_result("12345", "John Doe", False)
# result_with_specific_issues = get_mock_id_verification_result_with_specific_issues(
#     "12345", "John Doe", ["Suspicious document features", "Poor image quality"]
# )

"""
Example usage of the mock results for the Source of Wealth Agent system.
"""

import json
from datetime import datetime
from source_of_wealth_agent.core.mock_results import (
    get_mock_client_verification_results,
    get_mock_client_verification_results_with_specific_issues,
    get_mock_high_risk_client_verification_results,
    get_mock_medium_risk_client_verification_results,
    get_mock_low_risk_client_verification_results
)

def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))

def main():
    """Main function to demonstrate the usage of mock results."""
    print("\n=== Example Usage of Mock Results ===\n")
    
    # Example 1: Generate mock results for a client with all verifications passing
    print("\n--- Example 1: All Verifications Pass ---\n")
    results = get_mock_client_verification_results(
        client_id="12345",
        client_name="John Doe",
        all_verified=True
    )
    print_json(results)
    
    # Example 2: Generate mock results for a client with specific issues
    print("\n--- Example 2: Specific Issues ---\n")
    results_with_issues = get_mock_client_verification_results_with_specific_issues(
        client_id="67890",
        client_name="Jane Smith",
        id_issues=["ID document has expired"],
        payslip_issues=["Inconsistent income figures"],
        web_risk_flags=["PEP status identified"],
        financial_issues=["Unexplained large transactions"]
    )
    print_json(results_with_issues)
    
    # Example 3: Generate mock results for a high-risk client
    print("\n--- Example 3: High-Risk Client ---\n")
    high_risk_results = get_mock_high_risk_client_verification_results(
        client_id="54321",
        client_name="Alex Johnson"
    )
    print_json(high_risk_results)
    
    # Example 4: Generate mock results for a medium-risk client
    print("\n--- Example 4: Medium-Risk Client ---\n")
    medium_risk_results = get_mock_medium_risk_client_verification_results(
        client_id="98765",
        client_name="Sarah Williams"
    )
    print_json(medium_risk_results)
    
    # Example 5: Generate mock results for a low-risk client
    print("\n--- Example 5: Low-Risk Client ---\n")
    low_risk_results = get_mock_low_risk_client_verification_results(
        client_id="13579",
        client_name="Michael Brown"
    )
    print_json(low_risk_results)

if __name__ == "__main__":
    main()

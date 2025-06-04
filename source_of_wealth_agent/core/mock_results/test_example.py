"""
Example of using mock results in test cases.
"""

import unittest
import asyncio
from datetime import datetime
from typing import Dict, Any

from source_of_wealth_agent.core.state import create_initial_state
from source_of_wealth_agent.core.mock_results import (
    get_mock_client_verification_results,
    get_mock_high_risk_client_verification_results,
    get_mock_medium_risk_client_verification_results,
    get_mock_low_risk_client_verification_results
)

class TestWithMockResults(unittest.TestCase):
    """Test cases using mock results."""
    
    def setUp(self):
        """Set up test cases."""
        self.client_id = "12345"
        self.client_name = "John Doe"
        
    def test_low_risk_client(self):
        """Test with a low-risk client."""
        # Create initial state
        state = create_initial_state(self.client_id, self.client_name)
        
        # Get mock results for a low-risk client
        mock_results = get_mock_low_risk_client_verification_results(
            self.client_id, self.client_name
        )
        
        # Update state with mock results
        state.update(mock_results)
        
        # Assertions
        self.assertTrue(state["id_verification"]["verified"])
        self.assertTrue(state["payslip_verification"]["verified"])
        self.assertTrue(state["web_references"]["verified"])
        self.assertTrue(state["financial_reports"]["verified"])
        self.assertEqual(len(state["web_references"]["risk_flags"]), 0)
        self.assertEqual(state["financial_reports"]["annual_income_range"], "500,000 - 1,000,000")
        self.assertEqual(state["financial_reports"]["investment_assets"], "5,000,000+")
        
    def test_medium_risk_client(self):
        """Test with a medium-risk client."""
        # Create initial state
        state = create_initial_state(self.client_id, self.client_name)
        
        # Get mock results for a medium-risk client
        mock_results = get_mock_medium_risk_client_verification_results(
            self.client_id, self.client_name
        )
        
        # Update state with mock results
        state.update(mock_results)
        
        # Assertions
        self.assertTrue(state["id_verification"]["verified"])
        self.assertFalse(state["payslip_verification"]["verified"])
        self.assertFalse(state["web_references"]["verified"])
        self.assertTrue(state["financial_reports"]["verified"])
        self.assertEqual(state["payslip_verification"]["issues_found"], ["Requires manual verification"])
        self.assertEqual(state["web_references"]["risk_flags"], ["PEP status identified"])
        
    def test_high_risk_client(self):
        """Test with a high-risk client."""
        # Create initial state
        state = create_initial_state(self.client_id, self.client_name)
        
        # Get mock results for a high-risk client
        mock_results = get_mock_high_risk_client_verification_results(
            self.client_id, self.client_name
        )
        
        # Update state with mock results
        state.update(mock_results)
        
        # Assertions
        self.assertFalse(state["id_verification"]["verified"])
        self.assertFalse(state["payslip_verification"]["verified"])
        self.assertFalse(state["web_references"]["verified"])
        self.assertFalse(state["financial_reports"]["verified"])
        self.assertIn("Suspicious document features", state["id_verification"]["issues_found"])
        self.assertIn("Inconsistent income figures", state["payslip_verification"]["issues_found"])
        self.assertIn("PEP status identified", state["web_references"]["risk_flags"])
        self.assertIn("Unexplained large transactions", state["financial_reports"]["issues_found"])
        
    def test_custom_issues(self):
        """Test with custom issues."""
        # Create initial state
        state = create_initial_state(self.client_id, self.client_name)
        
        # Define custom issues
        id_issues = ["ID document has expired"]
        payslip_issues = ["Inconsistent income figures"]
        web_risk_flags = ["Negative news mentions"]
        financial_issues = ["Unexplained large transactions"]
        
        # Get mock results with custom issues
        from source_of_wealth_agent.core.mock_results import get_mock_client_verification_results_with_specific_issues
        mock_results = get_mock_client_verification_results_with_specific_issues(
            client_id=self.client_id,
            client_name=self.client_name,
            id_issues=id_issues,
            payslip_issues=payslip_issues,
            web_risk_flags=web_risk_flags,
            financial_issues=financial_issues
        )
        
        # Update state with mock results
        state.update(mock_results)
        
        # Assertions
        self.assertFalse(state["id_verification"]["verified"])
        self.assertFalse(state["payslip_verification"]["verified"])
        self.assertFalse(state["web_references"]["verified"])
        self.assertFalse(state["financial_reports"]["verified"])
        self.assertEqual(state["id_verification"]["issues_found"], id_issues)
        self.assertEqual(state["payslip_verification"]["issues_found"], payslip_issues)
        self.assertEqual(state["web_references"]["risk_flags"], web_risk_flags)
        self.assertEqual(state["financial_reports"]["issues_found"], financial_issues)

if __name__ == "__main__":
    unittest.main()

import sys
import os
import logging
from unittest.mock import MagicMock
from datetime import datetime

# Configure logging first
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Print debugging information
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"Path: {sys.path}")

# Import necessary modules with better error handling
try:
    from source_of_wealth_agent.core.state import create_initial_state
    print("✅ Successfully imported state module")
except ImportError as e:
    print(f"❌ Error importing state module: {e}")
    sys.exit(1)

try:
    from source_of_wealth_agent.agents.web_references_agent import WebReferencesAgent
    print("✅ Successfully imported WebReferencesAgent")
except ImportError as e:
    print(f"❌ Error importing WebReferencesAgent: {e}")
    sys.exit(1)

try:
    from source_of_wealth_agent.agents.payslip_verification_agent import PayslipVerificationAgent
    print("✅ Successfully imported PayslipVerificationAgent")
except ImportError as e:
    print(f"❌ Error importing PayslipVerificationAgent: {e}")
    sys.exit(1)

# Create a mock model for testing
mock_model = MagicMock()
# Configure the mock to return JSON for LinkedIn search
mock_model.invoke.return_value = """```json
{
  "found": true,
  "name_match": true,
  "position": "Senior Manager",
  "company": "Global Bank Ltd",
  "profile_summary": "Found profile for Jane Smith working as Senior Manager at Global Bank Ltd with 10+ years of experience."
}
```"""

print("\n=== Testing Source of Wealth Agents ===\n")

# Create a test state
state = create_initial_state("67890", "Jane Smith")

# Test Payslip Verification Agent
print("\n🔍 Testing PayslipVerificationAgent...\n")
payslip_agent = PayslipVerificationAgent(model=mock_model)

# Configure mock model to return appropriate payslip analysis
payslip_mock_response = """```json
{
  "employee_name": "Jane Smith",
  "employer": "Global Bank Ltd",
  "position": "Senior Manager",
  "gross_pay": 18000.00,
  "net_pay": 13000.00,
  "pay_period": "Monthly (May 2025)",
  "tax_deductions": 3600.00,
  "other_deductions": 1400.00,
  "ytd_gross": 90000.00,
  "ytd_net": 65000.00,
  "currency": "USD",
  "issues_found": []
}
```"""
mock_model.invoke.return_value = payslip_mock_response

# Set up test file path
test_payslip_path = "/workspaces/agent-playground/source_of_wealth_agent/data/payslip_documents/67890_payslip.txt"

# Also mock the extract_payslip_information method to use our mock response
original_extract_payslip = payslip_agent.extract_payslip_information
payslip_agent.extract_payslip_information = lambda doc_path: {
    "employee_name": "Jane Smith",
    "employer": "Global Bank Ltd",
    "position": "Senior Manager",
    "gross_pay": 18000.00,
    "net_pay": 13000.00,
    "pay_period": "Monthly (May 2025)",
    "tax_deductions": 3600.00,
    "other_deductions": 1400.00,
    "ytd_gross": 90000.00,
    "ytd_net": 65000.00,
    "currency": "USD",
    "issues_found": []
}

# Mock the find_payslip_document method for testing
original_find_payslip = payslip_agent.find_payslip_document
payslip_agent.find_payslip_document = lambda client_id: test_payslip_path

# Run the agent
print("Running payslip verification...")
payslip_state = payslip_agent.run(state)

# Restore the original methods
payslip_agent.find_payslip_document = original_find_payslip
payslip_agent.extract_payslip_information = original_extract_payslip

# Show results
if "payslip_verification" in payslip_state:
    print("\nPayslip Verification Results:")
    print(f"  Verified: {payslip_state['payslip_verification']['verified']}")
    print(f"  Monthly Income: {payslip_state['payslip_verification']['monthly_income']}")
    print(f"  Employer: {payslip_state['payslip_verification']['employer']}")
    print(f"  Position: {payslip_state['payslip_verification']['position']}")
    if "issues_found" in payslip_state["payslip_verification"]:
        print(f"  Issues Found: {', '.join(payslip_state['payslip_verification']['issues_found'])}")
else:
    print("No payslip verification data in result")

# Test Web References Agent
print("\n🔍 Testing WebReferencesAgent...\n")

# Create a mock requests.get response
class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
    
    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception(f"HTTP Error: {self.status_code}")

# Mock HTML content with LinkedIn search results
mock_html = """
<html>
<body>
    <div class="g">
        <a href="https://www.linkedin.com/in/jane-smith-12345">Jane Smith</a>
        <div class="VwiC3b">Jane Smith - Senior Manager at Global Bank Ltd | LinkedIn</div>
    </div>
    <div class="g">
        <a href="https://www.somesite.com/about">Some Other Site</a>
        <div class="VwiC3b">Some unrelated content</div>
    </div>
</body>
</html>
"""

# Create and configure the web references agent
web_agent = WebReferencesAgent(model=mock_model)

# Mock the requests.get method
import requests
original_get = requests.get
requests.get = MagicMock(return_value=MockResponse(mock_html))

# Run the agent
print("Running web references check...")
web_state = web_agent.run(payslip_state)  # Use the state from the payslip verification

# Restore the original method
requests.get = original_get

# Show results
if "web_references" in web_state:
    print("\nWeb References Results:")
    print(f"  Verified: {web_state['web_references']['verified']}")
    print(f"  Mentions: {len(web_state['web_references']['mentions'])}")
    
    print("\nTop LinkedIn Mentions:")
    linkedin_mentions = [m for m in web_state['web_references']['mentions'] if m['source'] == 'LinkedIn']
    for i, mention in enumerate(linkedin_mentions[:2]):
        print(f"  {i+1}. {mention['details']}")
    
    if "risk_flags" in web_state["web_references"] and web_state["web_references"]["risk_flags"]:
        print(f"\n  Risk Flags: {', '.join(web_state['web_references']['risk_flags'])}")
    else:
        print("\n  No risk flags found")
else:
    print("No web references data in result")

# Show the audit log
if "audit_log" in web_state:
    print("\nAudit Log:")
    for entry in web_state["audit_log"]:
        print(f"{entry['timestamp']} | {entry['agent']} | {entry['action']}")

import sys
import os
import logging
import json
from datetime import datetime
from unittest.mock import MagicMock

# Add the project root to the path
sys.path.append(os.path.abspath('.'))

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a mock model
mock_model = MagicMock()
mock_model.invoke.return_value = MagicMock(
    content='''```json
{
    "document_type": "Passport",
    "full_name": "Test User",
    "date_of_birth": "1990-01-01",
    "nationality": "United States",
    "document_number": "ABC123456",
    "issue_date": "2018-05-13",
    "expiry_date": "2028-05-13",
    "security_features": ["Hologram", "UV Reactive Ink"],
    "potential_issues": []
}
```'''
)

# Import necessary modules
from source_of_wealth_agent.core.state import create_initial_state
from source_of_wealth_agent.agents.id_verification_agent import IDVerificationAgent

# Override the ID document finding method for testing
IDVerificationAgent.find_id_document = MagicMock(return_value="/path/to/mock/id.jpg")
IDVerificationAgent.encode_image = MagicMock(return_value="mock_base64_data")

# Create agent with mock model
id_agent = IDVerificationAgent(model=mock_model)

# Create state
state = create_initial_state("12345", "Test User")

# Run agent
print("Running ID verification agent...")
result = id_agent.run(state)
print("Agent completed successfully!")

# Show the verification result
if "id_verification" in result:
    print("\nID Verification Result:")
    print(f"Verified: {result['id_verification']['verified']}")
    print(f"ID Type: {result['id_verification']['id_type']}")
    print(f"Document Number: {result['id_verification']['document_number']}")
    print(f"Full Name: {result['id_verification']['full_name']}")
    print(f"Nationality: {result['id_verification']['nationality']}")
    print(f"ID Expiry: {result['id_verification']['id_expiry']}")
    print(f"Issues Found: {', '.join(result['id_verification']['issues_found']) if result['id_verification']['issues_found'] else 'None'}")
else:
    print("No id_verification data in result")

# Show the audit log
if "audit_log" in result:
    print("\nAudit Log:")
    for entry in result["audit_log"]:
        print(f"{entry['timestamp']} | {entry['agent']} | {entry['action']}")

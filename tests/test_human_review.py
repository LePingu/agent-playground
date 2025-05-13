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
sys.path.append(os.path.abspath('.'))
print(f"Path: {sys.path}")

try:
    # Try importing before the script runs further
    from source_of_wealth_agent.core.state import create_initial_state
    print("Successfully imported core modules")
except Exception as e:
    print(f"Error importing modules: {str(e)}")
    sys.exit(1)  # Exit if imports fail

# Import necessary modules
from source_of_wealth_agent.core.state import create_initial_state
from source_of_wealth_agent.agents.id_verification_agent import IDVerificationAgent

# Create a mock model with proper binding
mock_model = MagicMock()
mock_model.bind = MagicMock(return_value=mock_model)
mock_model.invoke.return_value = """```json
{
    "document_type": "Passport",
    "full_name": "Jane Smith",
    "date_of_birth": "1985-03-15",
    "nationality": "Canada",
    "document_number": "P123456789",
    "issue_date": "2020-01-10",
    "expiry_date": "2030-01-09",
    "security_features": ["Hologram", "UV Reactive Ink", "Microtext"],
    "potential_issues": []
}
```"""

# Override the ID document finding method for testing
def mock_find_id_document(self, client_id):
    print(f"Mock ID document found for client: {client_id}")
    return "/path/to/mock/id.jpg"

IDVerificationAgent.find_id_document = mock_find_id_document
IDVerificationAgent.encode_image = MagicMock(return_value="mock_base64_data")

# Create agent with mock model
id_agent = IDVerificationAgent(model=mock_model)

# Create state
state = create_initial_state("67890", "Jane Smith")

print("\n🚀 Testing ID verification agent with human-in-the-loop...")
print("When prompted, enter 'yes' to approve or 'no' to reject the verification.")

# Run agent
result = id_agent.run(state)

print("\n🏁 Test completed!")
print(f"\nFinal verification status:")
print(f"  Verified: {result['id_verification']['verified']}")
print(f"  Human approved: {result['id_verification']['human_approved']}")

# Show the audit log
if "audit_log" in result:
    print("\nAudit Log:")
    for entry in result["audit_log"]:
        print(f"{entry['timestamp']} | {entry['agent']} | {entry['action']}")

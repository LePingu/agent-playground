# Mock Results for Source of Wealth Agent System

This directory contains mock results for the various verification agents in the Source of Wealth Agent system. These mock results can be used for testing, development, and demonstration purposes without requiring actual client data or external API calls.

## Overview

The mock results are organized by agent type:

- **ID Verification Results**: Mock results for the ID Verification Agent
- **Payslip Verification Results**: Mock results for the Payslip Verification Agent
- **Web References Results**: Mock results for the Web References Agent
- **Financial Reports Results**: Mock results for the Financial Reports Agent

Each module provides functions to generate realistic mock results with various configurations, including successful verifications and verifications with specific issues.

## Usage

### Basic Usage

```python
from source_of_wealth_agent.core.mock_results import get_mock_client_verification_results

# Generate mock results for a client with all verifications passing
results = get_mock_client_verification_results(
    client_id="12345",
    client_name="John Doe",
    all_verified=True
)
```

### Generating Results with Specific Issues

```python
from source_of_wealth_agent.core.mock_results import get_mock_client_verification_results_with_specific_issues

# Generate mock results with specific issues for each verification type
results_with_issues = get_mock_client_verification_results_with_specific_issues(
    client_id="67890",
    client_name="Jane Smith",
    id_issues=["ID document has expired"],
    payslip_issues=["Inconsistent income figures"],
    web_risk_flags=["PEP status identified"],
    financial_issues=["Unexplained large transactions"]
)
```

### Predefined Risk Profiles

```python
from source_of_wealth_agent.core.mock_results import (
    get_mock_high_risk_client_verification_results,
    get_mock_medium_risk_client_verification_results,
    get_mock_low_risk_client_verification_results
)

# Generate mock results for a high-risk client
high_risk_results = get_mock_high_risk_client_verification_results(
    client_id="54321",
    client_name="Alex Johnson"
)

# Generate mock results for a medium-risk client
medium_risk_results = get_mock_medium_risk_client_verification_results(
    client_id="98765",
    client_name="Sarah Williams"
)

# Generate mock results for a low-risk client
low_risk_results = get_mock_low_risk_client_verification_results(
    client_id="13579",
    client_name="Michael Brown"
)
```

### Individual Agent Results

You can also generate mock results for individual agents:

```python
from source_of_wealth_agent.core.mock_results.id_verification_results import get_mock_id_verification_result
from source_of_wealth_agent.core.mock_results.payslip_verification_results import get_mock_payslip_verification_result
from source_of_wealth_agent.core.mock_results.web_references_results import get_mock_web_references_result
from source_of_wealth_agent.core.mock_results.financial_reports_results import get_mock_financial_reports_result

# Generate mock ID verification result
id_result = get_mock_id_verification_result(
    client_id="12345",
    client_name="John Doe",
    verified=True
)

# Generate mock payslip verification result
payslip_result = get_mock_payslip_verification_result(
    client_id="12345",
    client_name="John Doe",
    verified=True,
    monthly_income=15000.0,
    employer="Global Bank Ltd",
    position="Senior Manager"
)

# Generate mock web references result
web_result = get_mock_web_references_result(
    client_id="12345",
    client_name="John Doe",
    verified=True,
    employer="Global Bank Ltd"
)

# Generate mock financial reports result
financial_result = get_mock_financial_reports_result(
    client_id="12345",
    client_name="John Doe",
    verified=True,
    annual_income_range="100,000 - 200,000",
    investment_assets="500,000+",
    credit_score="Excellent"
)
```

## Example Script

An example script is provided in `example_usage.py` that demonstrates how to use the mock results. You can run it with:

```bash
python -m source_of_wealth_agent.core.mock_results.example_usage
```

## Integration with Agents

These mock results can be used to test the workflow without requiring actual agent execution. For example:

```python
from source_of_wealth_agent.core.mock_results import get_mock_client_verification_results
from source_of_wealth_agent.core.state import create_initial_state

# Create initial state
state = create_initial_state(client_id="12345", client_name="John Doe")

# Get mock results
mock_results = get_mock_client_verification_results(
    client_id="12345",
    client_name="John Doe",
    all_verified=True
)

# Update state with mock results
state.update(mock_results)

# Now you can test downstream agents with this pre-populated state
# For example:
# result = risk_assessment_agent.run(state)
```

## Customization

Each mock result function provides parameters to customize the generated results. See the docstrings in each module for details on available parameters.

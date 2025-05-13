# Source of Wealth Multi-Agent System

A multi-agent system for verifying and assessing the source of wealth information for banking clients, using LangChain and LangGraph.

## Overview

This system automates the collection and assessment of client information to verify their source of wealth. It uses a multi-agent approach with specialized agents working together to analyze client data and produce a comprehensive risk assessment report.

## Key Features

- **ID Verification**: Verifies client identity documents
- **Payslip Verification**: Extracts and verifies information from payslips
- **Web References Analysis**: Searches LinkedIn and financial news for client information
- **Summarization**: Collates data from different verification steps
- **Risk Assessment**: Evaluates verification results to determine risk level
- **Report Generation**: Creates a comprehensive verification report

## Architecture

The system follows a modular, agent-based architecture organized into distinct layers:

### Core Layer
- **State Management**: Defines the structure of the state that flows through the system
- **Model Initialization**: Handles initialization and configuration of language models

### Agents Layer
- **Verification Agents**: ID, payslip, and web references verification
- **Summarization Agent**: Collates data from verification agents
- **Risk Assessment Agent**: Performs risk analysis
- **Report Generation Agent**: Creates final formatted reports

### Workflow Layer
- **Orchestration**: Defines the workflow graph and execution flow between agents
- **Tracing**: Provides tracing capabilities for monitoring agent interactions
- **Visualization**: Generates visualizations of the workflow and results
- **Runner**: Executes the workflow with or without tracing

### Testing Layer
- **Component Tests**: Verify individual agent functionality
- **Integration Tests**: Test interaction between multiple agents
- **End-to-End Tests**: Validate the complete workflow
- **Test Runner**: Unified script to run all tests

## Workflow Structure

The simplified workflow follows these steps:

1. **ID Verification** → **Payslip Verification** → **Web References Check**
2. **Summarization** of all verification data
3. **Risk Assessment** based on summarized data
4. **Report Generation** for final output

## Technical Implementation

### Language Models
- **OpenRouter**: Used for external data analysis, web reference checking
- **Ollama**: Used for processing sensitive information (ID verification, payslip analysis)

### Dependencies
- LangChain: Framework for building applications with language models
- LangGraph: Framework for building stateful, multi-agent workflows

## Usage

### Basic Usage

```python
from source_of_wealth_agent.workflow.runner import run_workflow

# Run the workflow for a client
result = run_workflow(
    client_id="12345",
    client_name="John Doe"
)

# Access the final report
if "final_report" in result:
    print(result["final_report"])
```

### Advanced Usage (Traceable Workflow)

```python
from source_of_wealth_agent.workflow.runner import run_workflow

# Run with tracing enabled
result = run_workflow(
    client_id="12345",
    client_name="John Doe",
    traceable=True
)

# Access the trace information
if "audit_log" in result:
    for entry in result["audit_log"]:
        print(f"{entry['timestamp']} | {entry['agent']} | {entry['action']}")
```

## Testing

The system includes a comprehensive test suite organized in the `tests/` directory:

- `test_components.py`: Test individual components (summarization, risk assessment, report generation)
- `test_end_to_end.py`: End-to-end test of the entire workflow with mock agents
- `test_simplified_workflow.py`: Test the simplified workflow execution
- `test_agents.py`: Tests for individual verification agents
- `test_human_review.py`: Tests for the human review process
- `basic_test.py`: Basic test for the summarization agent

### Running Tests

You can run all tests using the test runner script:

```bash
# Run all tests
./run_tests.py

# Run specific tests
./run_tests.py test_components test_direct

# Run tests with verbose output
./run_tests.py -v
```

Alternatively, you can run individual test scripts directly:

```bash
# Run a specific test file
python tests/test_end_to_end.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

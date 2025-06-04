# Human-in-the-Loop Implementation with LangGraph

## Overview

This document explains how we've implemented human-in-the-loop functionality in the Source of Wealth Agent system. The implementation uses:

1. **Sequential Blocking** for ID verification, ensuring this critical verification must complete successfully before other steps can proceed
2. **Asynchronous Review System** for other verification types (payslip, web references, financial reports) that allows these agents to continue running in the background while waiting for human review

## Implementation Components

### 1. Human Advisory Agent

The Human Advisory Agent (`human_advisory_agent.py`) is responsible for:

- Examining verification results and determining if human review is needed
- Implementing special handling for ID verification as a critical sequential step
- Processing human responses for all verification types
- Updating the state with human review decisions

When ID verification fails or has issues, the workflow is effectively blocked until a human provides input through the Human Advisory Agent.

### 2. Risk Assessment Agent with Sequential Enforcement

The Risk Assessment Agent (`risk_assessment_agent.py`) enforces sequential verification by:

- Ensuring ID verification always happens first
- Blocking other verification steps until ID verification succeeds
- Routing to human review when ID verification fails
- Creating verification plans for the remaining steps only after ID is verified

### 3. Workflow Orchestration

The workflow orchestration (`orchestration.py`) has been designed to:

- Connect ID verification directly to the human advisory node
- Configure the graph with a checkpointer for state persistence
- Implement conditional routing through the `route_after_risk_assessment` function
- Maintain proper sequential routing to ensure ID verification happens first

### 4. State Management for Reviews

The system manages human reviews through state mechanisms:

- Stores pending review requests in the state
- Tracks review responses and approvals
- Maintains human approval records by verification type
- Uses a structured data format for review requests and responses

### 5. Workflow Runner

The workflow runner (`runner.py`) supports:

- Thread-based workflow execution for state isolation
- State persistence with checkpoint saving/loading
- Configurable workflow execution with thread IDs
- Support for continuing workflows from saved states

## Workflow Sequence

1. **ID Verification First**:
   - Risk assessment agent enforces ID verification as first step
   - ID verification agent performs initial checks
   - Human advisory agent reviews ID verification if issues found
   - Workflow effectively blocks until ID verification succeeds or has human approval
   - Other verifications can only proceed after ID verification is complete

2. **Asynchronous Verifications**:
   - After ID verification completes, other agents start working
   - These agents can run simultaneously in the background
   - Each generates review requests when issues are found
   - Reviews are stored in the state without blocking
   - Human advisory agent processes these reviews asynchronously

3. **Review Processing**:
   - Human advisory agent checks for pending reviews in the workflow state
   - When human input is received, approval status is updated in state
   - Verification agents can check for human approval status before proceeding
   - Risk assessment agent enforces sequential dependencies throughout workflow

## Running the System

1. Start the workflow:
   ```
   python main.py
   ```

2. When the workflow pauses for human input, the console will prompt for approval:
   ```
   ID verification requires human review for client 12345. Approve? (yes/no):
   ```

3. After approving ID verification, other agents continue in the background.

4. For other verification types, the system will continue running while awaiting human input.

## Testing

The system includes comprehensive test files that demonstrate:

1. ID verification sequential enforcement
2. Human review handling for verification issues
3. Asynchronous processing of other verifications

Run the tests with:
```
./run_tests.py
```

## Benefits of this Implementation

1. **Sequential Enforcement**: ID verification must complete successfully before other steps can proceed, providing proper security controls.

2. **Asynchronous Processing**: Other verification steps can run in parallel once ID verification is complete, improving throughput.

3. **Flexible Review System**: Handles both critical blocking reviews (ID) and non-blocking reviews (other verification types) with a unified mechanism.

4. **Maintainable Structure**: Each agent has clear responsibilities, with the human advisory agent serving as the central coordination point for all human review actions.

5. **State Persistence**: All review requests and decisions are tracked in the workflow state, allowing for transparent audit trails.

6. **Workflow Continuity**: The system can pick up from where it left off when human input becomes available, supporting both interactive and batch processing modes.

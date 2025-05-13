# Project Brief: Source of Wealth Multi-Agent System

## Project Overview
The Source of Wealth Multi-Agent System is an agentic framework designed for a bank to verify and assess the source of wealth information for clients. The system uses a multi-agent approach with specialized agents working together to analyze client data and produce a comprehensive risk assessment report.

## Core Requirements

### Functional Requirements
1. Verify client identity documents
2. Verify client payslips and employment information
3. Check web references for client information
4. Analyze financial reports
5. Corroborate employment information across multiple sources
6. Corroborate source of funds across multiple sources
7. Assess investment information
8. Generate comprehensive risk assessment reports
9. Maintain human oversight throughout the verification process

### Technical Requirements
1. Implement using LangGraph and LangChain
2. Create a modular, maintainable architecture
3. Use OpenRouter for external data processing (using qwen3 or deepseek models)
4. Use Ollama with local models for sensitive information processing
5. Provide interactive Jupyter notebook interface
6. Implement visualization tools for workflow and results
7. Ensure human-in-the-loop at critical decision points

## Agent Structure

### Utility Agents (Specialized Verification)
- ID Verification Agent: Verifies client identity documents
- Payslip Verification Agent: Verifies client payslips
- Web References Agent: Checks online references for client information
- Financial Reports Agent: Analyzes financial reports

### Helper Agents (Data Coordination)
- Internal Data Coordinator: Coordinates internal data sources
- External Data Coordinator: Coordinates external data sources
- Report Generation Agent: Creates final reports in markdown format

### Functional Agents (Analysis)
- Summarization Agent: Summarizes collected data
- Employment Corroboration Agent: Corroborates employment information
- Source of Funds Corroboration Agent: Corroborates source of funds
- Investment Corroboration Agent: Corroborates investment information
- Risk Assessment Agent: Coordinates risk assessment

### Advisory Agent
- Human Advisory Agent: Maintains human oversight for critical checks

### Orchestration
- Global Orchestrator: Coordinates the entire workflow

## Success Criteria
1. Complete verification workflow from ID verification to final report generation
2. Human oversight at critical decision points
3. Comprehensive risk assessment with clear recommendations
4. Visualizations of agent interactions and workflow
5. Modular, maintainable codebase
6. Interactive Jupyter notebook interface

## Constraints
1. Sensitive information must be processed using local models
2. Human approval required for critical verification steps
3. System must be interactive to allow user input where necessary

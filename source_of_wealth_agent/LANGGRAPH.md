# LangGraph Configuration for Source of Wealth Agent

This document explains the LangGraph configuration (`langgraph.json`) for the Source of Wealth verification system.

## Overview

The `langgraph.json` file defines the structure and behavior of the multi-agent workflow used in the Source of Wealth verification system. It describes the nodes (agents), edges (connections between agents), and configuration settings for the workflow graph.

## Configuration Structure

### Basic Information

- `schema_version`: Version of the LangGraph schema
- `name`: Name of the workflow
- `description`: Brief description of what the workflow does
- `project`: Project identifier

### Workflow Components

#### Nodes

The workflow consists of the following nodes (agents):

1. **ID Verification Agent** (`id_verification_node`)
   - Verifies client identity documents
   - Uses local Ollama model for sensitive data processing

2. **Payslip Verification Agent** (`payslip_verification_node`)
   - Extracts and verifies information from payslips
   - Uses local Ollama model for sensitive financial data

3. **Web References Agent** (`web_references_node`) 
   - Searches for client references online
   - Uses OpenRouter model for better search capabilities

4. **Summarization Agent** (`summarization_node`)
   - Collates data from all verification steps
   - Creates a coherent summary of findings

5. **Risk Assessment Agent** (`risk_assessment_node`) 
   - Analyzes verification results
   - Determines overall risk level

6. **Report Generation Agent** (`report_generation_node`)
   - Creates the final verification report
   - Formats findings and recommendations

#### Edges

The workflow follows this sequence:

1. ID Verification → Payslip Verification → Web References
2. Web References → Summarization
3. Summarization → Risk Assessment
4. Risk Assessment → Report Generation

#### Available Graphs

The configuration defines multiple workflow graphs:

1. **main** - The full workflow graph
   - Includes all nodes and covers the complete verification process
   - Entry point: `__start__`
   - Exit point: `__end__`
   - Used for comprehensive client verification

2. **verification_only** - Simplified verification workflow
   - Includes only the verification nodes (ID, Payslip, Web)
   - Entry point: `__start__`
   - Exit point: `web_references_node`
   - Useful for quick preliminary checks

### Integration with Project

This LangGraph configuration is designed to work with the Source of Wealth Agent system. To use it:

1. The system will automatically load this configuration when running with `--use-config`
2. The nodes in the configuration map directly to agent functions in the codebase
3. The state management is handled by the `AgentState` class
4. Different graphs can be selected programmatically for different use cases

## Visualization

The configuration includes visualization settings to display the workflow graph in a structured and visually appealing way:

- Nodes are grouped by function (Verification, Processing, Output)
- Each group has a distinct color scheme
- The layout is optimized for clarity and flow understanding

## Extending the Configuration

To extend this configuration:

1. Add new nodes by defining their handlers, types, and metadata
2. Connect nodes by adding appropriate edges
3. Update visualization settings to include new nodes in appropriate groups

## Usage

This configuration is used automatically when running the workflow with the `main.py` script. No manual loading is required.

To visualize the workflow:

```bash
python main.py --trace
```

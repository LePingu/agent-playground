# Running the Source of Wealth Agent System

This guide explains how to run the Source of Wealth Agent system from the command line.

## Prerequisites

Before running the system, make sure you have:

1. Python 3.8 or higher installed
2. Required packages installed (run `pip install -r requirements.txt`)
3. Environment variables configured (see [Environment Variables Guide](env/README.md))

## Setup

Run the setup script to prepare the environment:

```bash
./setup.sh
```

This will:
- Check your Python version
- Install dependencies
- Create an initial `.env` file if it doesn't exist
- Make the main script executable

## Running the System

### Basic Execution

To run the system with default settings:

```bash
python main.py
```

### Running with Tracing

To run with tracing enabled (for visualization):

```bash
python main.py --trace
```

When tracing is enabled, the system will:
1. Log all agent interactions
2. Generate visualization data
3. Print execution statistics

### Running with LangGraph Configuration

The system can use a LangGraph JSON configuration file:

```bash
python main.py --use-config
```

This enables the system to load the graph structure from `source_of_wealth_agent/langgraph.json`. 
You can also combine options:

```bash
python main.py --use-config --trace
```

#### Selecting Different Graphs

The configuration supports multiple workflow graphs. You can select which one to use:

```bash
# Run the main comprehensive workflow
python main.py --use-config --graph main

# Run the verification-only workflow (faster, less comprehensive)
python main.py --use-config --graph verification_only

# Combine with tracing
python main.py --use-config --graph verification_only --trace
```

For more information about the LangGraph configuration and available graphs, see [LangGraph Configuration](source_of_wealth_agent/LANGGRAPH.md).

### Configuration

Configure the system by editing the `env/.env` file:

```bash
nano env/.env
```

Key settings to consider:
- `CLIENT_ID` and `CLIENT_NAME`: The client to verify
- `OPENROUTER_API_KEY`: Required for web and financial analysis
- `OLLAMA_BASE_URL` and `OLLAMA_MODEL`: For local LLM processing

## Human-in-the-Loop Interaction

The system implements a sequential verification approach that requires human review in certain scenarios:

### ID Verification Review

ID verification is a critical first step that requires human review when issues are detected:

1. When the system detects ID verification issues, it will prompt for human approval:
   ```
   ID verification requires human review for client 12345. Approve? (yes/no):
   ```

2. Respond with `yes` or `no` to approve or reject the verification.

3. Only after ID verification is approved (either automatically or through human review) will the system proceed with other verification steps.

### Other Verification Reviews

For other verification types (payslip, web references, etc.), the system will continue processing in the background while waiting for human input when needed.

## Output

The system will generate:

1. Verification status for all checks
2. Overall risk assessment
3. A comprehensive verification report
4. (If tracing enabled) Visualization and statistics

## Troubleshooting

If you encounter issues:

1. Make sure all API keys are valid
2. Check that the Ollama service is running (if using local models)
3. Verify that all required files exist (ID documents, payslips)
4. If the workflow seems stuck, check if it's waiting for human input

## Example Output

A successful run should produce output like:

```
=== Source of Wealth Verification System ===

Client: John Doe (ID: 12345)
OpenRouter Model: openai/gpt-4-turbo
Ollama Model: openhermes @ http://localhost:11434
Tracing: Enabled

===========================================

🚀 Starting source of wealth verification for client: 12345
✅ Workflow completed for client: 12345

=== Verification Results ===

Overall Status: VERIFIED
Risk Level: LOW

=== Final Report ===

# Source of Wealth Verification Report
...
```

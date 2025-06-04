# CLI Reference

The Agent Playground Command Line Interface (CLI) provides powerful tools for managing workflows, templates, and monitoring. This reference covers all available commands and their options.

## Installation and Setup

The CLI is automatically available after installing Agent Playground:

```bash
# Install Agent Playground
pip install -e .

# Verify CLI is available
agent-playground --help
```

If the command is not found, you can also run it as a module:

```bash
python -m agent_playground.workflows.cli --help
```

## Global Options

All commands support these global options:

```bash
--help, -h          Show help message and exit
--version           Show version information
--verbose, -v       Enable verbose output
--quiet, -q         Suppress non-essential output
--config FILE       Use custom configuration file
```

## Commands Overview

| Command | Description |
|---------|-------------|
| [`list-templates`](#list-templates) | Show available workflow templates |
| [`template-info`](#template-info) | Get detailed template information |
| [`list-examples`](#list-examples) | Show available example workflows |
| [`run-example`](#run-example) | Execute example workflows |
| [`create-from-template`](#create-from-template) | Create workflows from templates |
| [`generate-template-config`](#generate-template-config) | Generate template configuration files |
| [`monitor`](#monitor) | View workflow execution status |
| [`visualize`](#visualize) | Open workflow visualizations |

## Command Reference

### `list-templates`

Lists all available workflow templates with descriptions.

```bash
agent-playground list-templates [OPTIONS]
```

**Options:**
- `--format FORMAT`: Output format (`table`, `json`, `yaml`) [default: `table`]
- `--category CATEGORY`: Filter by template category
- `--pattern PATTERN`: Filter by pattern type

**Examples:**

```bash
# List all templates
agent-playground list-templates

# List only parallel templates
agent-playground list-templates --category parallel

# Output as JSON
agent-playground list-templates --format json

# Filter by pattern
agent-playground list-templates --pattern sequential
```

**Output:**

```
┌─────────────────┬────────────────────────────────────────────────────┬──────────────┐
│ Template Name   │ Description                                        │ Category     │
├─────────────────┼────────────────────────────────────────────────────┼──────────────┤
│ sequential      │ Execute agents one after another                  │ Sequential   │
│ parallel        │ Execute agents concurrently with aggregation      │ Parallel     │
│ conditional     │ Branch execution based on state conditions        │ Conditional  │
│ human_in_loop   │ Incorporate human review and approval             │ Interactive  │
│ validation      │ Multi-stage validation pipeline                   │ Validation   │
│ analysis        │ Multi-perspective analysis with synthesis         │ Analysis     │
│ transformation  │ Data transformation workflows                     │ Transform    │
└─────────────────┴────────────────────────────────────────────────────┴──────────────┘
```

### `template-info`

Shows detailed information about a specific workflow template.

```bash
agent-playground template-info TEMPLATE_NAME [OPTIONS]
```

**Arguments:**
- `TEMPLATE_NAME`: Name of the template to describe

**Options:**
- `--show-examples`: Include usage examples
- `--show-params`: Show detailed parameter information
- `--format FORMAT`: Output format (`text`, `json`, `yaml`) [default: `text`]

**Examples:**

```bash
# Get info about sequential template
agent-playground template-info sequential

# Include examples and parameters
agent-playground template-info sequential --show-examples --show-params

# Output as JSON
agent-playground template-info sequential --format json
```

**Output:**

```
╭─ Sequential Workflow Template ─╮
│                                 │
│ Description: Execute agents one │
│ after another in sequence       │
│                                 │
│ Category: Sequential            │
│ Pattern: Linear                 │
│                                 │
│ Parameters:                     │
│ • agents (required)             │
│ • state_class (required)        │
│ • error_handling (optional)     │
│ • max_retries (optional)        │
│                                 │
│ Use Cases:                      │
│ • Data processing pipelines     │
│ • Document workflows           │
│ • Step-by-step analysis        │
│                                 │
╰─────────────────────────────────╯
```

### `list-examples`

Lists all available example workflows.

```bash
agent-playground list-examples [OPTIONS]
```

**Options:**
- `--format FORMAT`: Output format (`table`, `json`, `yaml`) [default: `table`]
- `--category CATEGORY`: Filter by example category
- `--detailed`: Show detailed descriptions

**Examples:**

```bash
# List all examples
agent-playground list-examples

# Show detailed descriptions
agent-playground list-examples --detailed

# Filter by category
agent-playground list-examples --category processing
```

**Output:**

```
┌──────────────────────┬─────────────────────────────────────────────────────┬────────────────────────┐
│ Key                  │ Name                                                │ Description            │
├──────────────────────┼─────────────────────────────────────────────────────┼────────────────────────┤
│ document_processing  │ Document Processing                                 │ Process documents      │
│                      │                                                     │ through extraction,    │
│                      │                                                     │ analysis, and          │
│                      │                                                     │ classification         │
├──────────────────────┼─────────────────────────────────────────────────────┼────────────────────────┤
│ data_analysis        │ Data Analysis                                       │ Analyze data through   │
│                      │                                                     │ cleaning, statistical  │
│                      │                                                     │ analysis, and insight  │
│                      │                                                     │ generation             │
├──────────────────────┼─────────────────────────────────────────────────────┼────────────────────────┤
│ customer_service     │ Customer Service                                    │ Handle customer        │
│                      │                                                     │ queries through intent │
│                      │                                                     │ classification and     │
│                      │                                                     │ response generation    │
└──────────────────────┴─────────────────────────────────────────────────────┴────────────────────────┘
```

### `run-example`

Executes an example workflow with monitoring and visualization.

```bash
agent-playground run-example EXAMPLE_KEY [OPTIONS]
```

**Arguments:**
- `EXAMPLE_KEY`: Key of the example to run (from `list-examples`)

**Options:**
- `--input FILE`: Input data file (JSON/YAML)
- `--output FILE`: Output file for results
- `--monitor`: Enable real-time monitoring
- `--visualize`: Generate visualization after completion
- `--timeout SECONDS`: Execution timeout [default: 300]
- `--no-progress`: Disable progress bar

**Examples:**

```bash
# Run document processing example
agent-playground run-example document_processing

# Run with custom input data
agent-playground run-example data_analysis --input data.json

# Run with monitoring and visualization
agent-playground run-example customer_service --monitor --visualize

# Save output to file
agent-playground run-example document_processing --output results.json
```

**Output:**

```
╭─ Running Document Processing Example ─╮
│                                        │
│ Workflow: Document Processing          │
│ State: DocumentProcessingState         │
│ Agents: 3                              │
│                                        │
╰────────────────────────────────────────╯

Processing documents... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:03

┌─ Execution Results ─┐
│                     │
│ Status: ✅ Success   │
│ Duration: 3.2s      │
│ Agents: 3/3         │
│                     │
│ Extracted Text:     │
│ • report.pdf ✓      │
│ • memo.docx ✓       │
│ • notes.txt ✓       │
│                     │
│ Analysis Complete   │
│ Classifications:    │
│ • Financial: 1      │
│ • Business: 2       │
│                     │
└─────────────────────┘

Results saved to: results.json
```

### `create-from-template`

Creates a new workflow from a template with interactive configuration.

```bash
agent-playground create-from-template TEMPLATE_NAME [OPTIONS]
```

**Arguments:**
- `TEMPLATE_NAME`: Name of the template to use

**Options:**
- `--config FILE`: Configuration file for template parameters
- `--output FILE`: Output file for generated workflow code
- `--interactive`: Use interactive mode for configuration
- `--name NAME`: Name for the new workflow
- `--overwrite`: Overwrite existing files

**Examples:**

```bash
# Create workflow interactively
agent-playground create-from-template sequential --interactive

# Use configuration file
agent-playground create-from-template parallel --config my_config.yaml

# Specify output file
agent-playground create-from-template conditional --output my_workflow.py
```

**Interactive Mode:**

```
╭─ Create Sequential Workflow ─╮
│                               │
│ Template: Sequential          │
│ Description: Execute agents   │
│ one after another            │
│                               │
╰───────────────────────────────╯

Enter workflow name: My Document Processor
Enter state class name: DocumentState

Agent Configuration:
  Agent 1 name: TextExtractor
  Agent 1 module: my_agents.extractors
  
  Agent 2 name: ContentAnalyzer  
  Agent 2 module: my_agents.analyzers

  Add another agent? [y/N]: n

Error handling [stop/skip/retry]: retry
Max retries [3]: 5

Output file [my_document_processor.py]: 

✅ Workflow created successfully!
   File: my_document_processor.py
   
   Next steps:
   1. Implement your agents in the specified modules
   2. Test the workflow with sample data
   3. Run: python my_document_processor.py
```

### `generate-template-config`

Generates sample configuration files for workflow templates.

```bash
agent-playground generate-template-config TEMPLATE_NAME [OPTIONS]
```

**Arguments:**
- `TEMPLATE_NAME`: Name of the template

**Options:**
- `--format FORMAT`: Configuration format (`yaml`, `json`, `toml`) [default: `yaml`]
- `--output FILE`: Output file name
- `--detailed`: Include detailed comments and examples
- `--minimal`: Generate minimal configuration

**Examples:**

```bash
# Generate YAML config for parallel template
agent-playground generate-template-config parallel

# Generate with detailed comments
agent-playground generate-template-config validation --detailed

# Output to specific file
agent-playground generate-template-config analysis --output my_config.yaml
```

**Output:**

```yaml
# Configuration for Parallel Workflow Template
# Generated by Agent Playground CLI

template_name: parallel
description: "Execute agents concurrently with aggregation"

# Required Parameters
agents:
  - name: "Agent1"
    module: "my_agents.agent1"
    config: {}
  - name: "Agent2" 
    module: "my_agents.agent2"
    config: {}

aggregator_agent:
  name: "Aggregator"
  module: "my_agents.aggregator"
  config: {}

state_class:
  name: "MyWorkflowState"
  module: "my_states"

# Optional Parameters
timeout: 300.0  # seconds
max_concurrent: 4  # maximum concurrent agents

# Advanced Configuration
error_handling:
  strategy: "partial"  # "stop", "partial", "ignore"
  timeout_action: "cancel"  # "cancel", "continue"

monitoring:
  enabled: true
  real_time: true
  metrics_collection: true

logging:
  level: "INFO"
  include_agent_logs: true
  log_state_changes: false
```

### `monitor`

Displays real-time monitoring of active workflows.

```bash
agent-playground monitor [OPTIONS]
```

**Options:**
- `--workflow-id ID`: Monitor specific workflow
- `--refresh SECONDS`: Refresh interval [default: 2]
- `--format FORMAT`: Display format (`table`, `json`, `dashboard`) [default: `dashboard`]
- `--follow`: Keep monitoring until interrupted

**Examples:**

```bash
# Monitor all active workflows
agent-playground monitor

# Monitor specific workflow
agent-playground monitor --workflow-id abc123

# Monitor with custom refresh rate
agent-playground monitor --refresh 5 --follow
```

**Output:**

```
╭─ Workflow Monitor ─ Live Dashboard ─╮
│                                      │
│ 🔄 Active Workflows: 2               │
│ ✅ Completed: 15                     │
│ ❌ Failed: 1                         │
│ ⏳ Total Runtime: 45m 23s            │
│                                      │
╰──────────────────────────────────────╯

┌─ Currently Running ─┐
│                     │
│ abc123              │
│ ├─ Agent1 ✅        │
│ ├─ Agent2 🔄        │
│ └─ Agent3 ⏳        │
│                     │
│ def456              │
│ ├─ Validator ✅     │
│ ├─ Processor 🔄     │
│ └─ Reporter ⏳      │
│                     │
└─────────────────────┘

Status: 🔄 2 active | ⏱️  Next refresh in 2s | Press Ctrl+C to exit
```

### `visualize`

Opens workflow visualizations and reports.

```bash
agent-playground visualize [OPTIONS]
```

**Options:**
- `--workflow-id ID`: Visualize specific workflow
- `--type TYPE`: Visualization type (`timeline`, `graph`, `metrics`, `report`) [default: `report`]
- `--output FILE`: Save visualization to file
- `--format FORMAT`: Output format (`html`, `png`, `svg`, `json`) [default: `html`]
- `--interactive`: Generate interactive visualization
- `--open`: Open in browser automatically

**Examples:**

```bash
# Open workflow report in browser
agent-playground visualize --open

# Generate timeline visualization
agent-playground visualize --type timeline --workflow-id abc123

# Save interactive graph
agent-playground visualize --type graph --interactive --output workflow.html

# Generate metrics report
agent-playground visualize --type metrics --format json
```

**Output:**

```
╭─ Generating Workflow Visualization ─╮
│                                      │
│ Type: Interactive Report             │
│ Workflows: 3                         │
│ Time Range: Last 24 hours           │
│                                      │
╰──────────────────────────────────────╯

Creating visualizations... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

✅ Visualization complete!
   
   📄 Report: workflow_report.html
   📊 Timeline: execution_timeline.png  
   🔗 Graph: workflow_graph.svg
   📈 Metrics: performance_metrics.json
   
   🌐 Opening in browser...
```

## Configuration

### Global Configuration

The CLI can be configured using a configuration file:

```bash
# Default locations (in order of precedence):
# 1. ./agent-playground.yaml
# 2. ~/.agent-playground/config.yaml  
# 3. /etc/agent-playground/config.yaml

# Or specify custom config:
agent-playground --config my-config.yaml <command>
```

**Sample configuration file:**

```yaml
# agent-playground.yaml

# Global settings
default_timeout: 300
log_level: INFO
colored_output: true

# Template settings
template_directory: "./templates"
allow_custom_templates: true

# Monitoring settings  
monitor:
  refresh_interval: 2
  max_history: 100
  enable_notifications: true

# Visualization settings
visualization:
  default_format: html
  auto_open_browser: true
  theme: "dark"
  
# Output settings
output:
  default_format: table
  show_progress: true
  verbose_errors: true
```

### Environment Variables

The CLI also respects these environment variables:

```bash
# API Configuration
export AGENT_PLAYGROUND_API_KEY="your-api-key"
export AGENT_PLAYGROUND_API_URL="https://api.example.com"

# Logging
export AGENT_PLAYGROUND_LOG_LEVEL="DEBUG"
export AGENT_PLAYGROUND_LOG_FILE="/var/log/agent-playground.log"

# Performance
export AGENT_PLAYGROUND_MAX_WORKERS="4"
export AGENT_PLAYGROUND_TIMEOUT="600"

# Visualization
export AGENT_PLAYGROUND_BROWSER="firefox"
export AGENT_PLAYGROUND_THEME="light"
```

## Tips and Best Practices

### 1. Use Aliases

Create shell aliases for common commands:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ap="agent-playground"
alias ap-ls="agent-playground list-templates"
alias ap-run="agent-playground run-example"
alias ap-mon="agent-playground monitor --follow"
```

### 2. Tab Completion

Enable tab completion for better UX:

```bash
# For bash
agent-playground --install-completion bash

# For zsh  
agent-playground --install-completion zsh

# For fish
agent-playground --install-completion fish
```

### 3. Output Formats

Use different output formats for scripting:

```bash
# Get template list as JSON for scripting
templates=$(agent-playground list-templates --format json)
echo $templates | jq '.[] | select(.category == "parallel")'

# Export monitoring data
agent-playground monitor --format json > monitoring_data.json
```

### 4. Workflow Automation

Combine CLI commands in scripts:

```bash
#!/bin/bash
# run_analysis.sh

echo "Starting data analysis workflow..."

# Generate config
agent-playground generate-template-config analysis --output config.yaml

# Run workflow
agent-playground run-example data_analysis --config config.yaml --monitor

# Generate report
agent-playground visualize --type report --open

echo "Analysis complete!"
```

### 5. Error Handling

Handle errors gracefully in scripts:

```bash
# Check if workflow succeeded
if agent-playground run-example document_processing --quiet; then
    echo "✅ Workflow completed successfully"
    agent-playground visualize --type timeline
else
    echo "❌ Workflow failed"
    agent-playground monitor --workflow-id last --format json > error_log.json
    exit 1
fi
```

## Troubleshooting

### Common Issues

**Command not found:**
```bash
# Try running as module
python -m agent_playground.workflows.cli --help

# Check installation
pip show agent-playground
```

**Permission errors:**
```bash
# Check file permissions
ls -la ~/.agent-playground/

# Use sudo if needed (not recommended)
sudo agent-playground <command>
```

**Timeout errors:**
```bash
# Increase timeout
agent-playground run-example <name> --timeout 600

# Check system resources
agent-playground monitor --format json | jq '.system_resources'
```

**Configuration errors:**
```bash
# Validate configuration
agent-playground --config config.yaml list-templates

# Use minimal config
agent-playground generate-template-config sequential --minimal
```

### Getting Help

- Use `--help` with any command for detailed help
- Check the verbose output with `--verbose`
- View logs in `~/.agent-playground/logs/`
- Report issues on GitHub with CLI version and error output

---

**Related Documentation:**
- [Quick Start Guide](../quickstart.md) - Get started with Agent Playground
- [Workflow Templates](../workflow-templates.md) - Learn about available templates
- [Examples](../examples/) - Browse example workflows

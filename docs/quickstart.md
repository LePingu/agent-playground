# Quick Start Guide

Get up and running with Agent Playground in just a few minutes!

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or poetry for package management

### Install from Source

```bash
# Clone the repository
git clone https://github.com/your-org/agent-playground.git
cd agent-playground

# Install in development mode
pip install -e .

# Or using poetry
poetry install
```

### Verify Installation

```bash
# Check if CLI is available
agent-playground --help

# List available workflow templates
agent-playground list-templates
```

## Your First Workflow

Let's create a simple document processing workflow using built-in templates.

### 1. Create a Simple Agent

```python
# my_agent.py
from agent_playground.core import BaseAgent, BaseState
from typing import Dict, Any

class GreetingAgent(BaseAgent):
    """A simple agent that adds a greeting."""
    
    def __init__(self, name: str = "GreetingAgent"):
        super().__init__(name)
    
    async def execute(self, state: BaseState) -> BaseState:
        # Add a greeting to the state
        if not hasattr(state, 'messages'):
            state.messages = []
        
        state.messages.append(f"Hello from {self.name}!")
        return state

class ProcessingAgent(BaseAgent):
    """An agent that processes data."""
    
    def __init__(self, name: str = "ProcessingAgent"):
        super().__init__(name)
    
    async def execute(self, state: BaseState) -> BaseState:
        # Process the messages
        if hasattr(state, 'messages'):
            processed = [msg.upper() for msg in state.messages]
            state.processed_messages = processed
        
        return state
```

### 2. Create a Workflow

```python
# workflow_example.py
import asyncio
from agent_playground.workflows import workflow_templates
from agent_playground.core import BaseState
from my_agent import GreetingAgent, ProcessingAgent

async def main():
    # Create agents
    greeting_agent = GreetingAgent("Greeter")
    processing_agent = ProcessingAgent("Processor")
    
    # Create workflow using sequential template
    workflow = workflow_templates.create_workflow(
        template_name="sequential",
        agents=[greeting_agent, processing_agent],
        state_class=BaseState
    )
    
    # Create initial state
    initial_state = BaseState()
    
    # Execute workflow
    result = await workflow.execute(initial_state)
    
    # Print results
    print("Messages:", result.messages)
    print("Processed:", result.processed_messages)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Run Your Workflow

```bash
python workflow_example.py
```

Expected output:
```
Messages: ['Hello from Greeter!']
Processed: ['HELLO FROM GREETER!']
```

## Using the CLI

The Agent Playground CLI provides powerful tools for workflow management.

### List Available Templates

```bash
agent-playground list-templates
```

### Get Template Information

```bash
agent-playground template-info sequential
```

### Run Example Workflows

```bash
# List available examples
agent-playground list-examples

# Run a document processing example
agent-playground run-example document_processing
```

### Monitor Workflows

```bash
# View active workflows
agent-playground monitor

# Generate visualization
agent-playground visualize --workflow-id <id>
```

## Using Built-in Examples

Agent Playground comes with several example workflows you can run immediately:

### Document Processing Example

```python
from agent_playground.workflows.examples import create_document_processing_workflow
from agent_playground.workflows.examples import DocumentProcessingState

# Create the workflow
workflow = create_document_processing_workflow()

# Create initial state with documents
initial_state = DocumentProcessingState()
initial_state.documents = ["report.pdf", "memo.docx", "notes.txt"]

# Execute
result = await workflow.execute(initial_state)
print("Extracted text:", result.extracted_text)
print("Analysis:", result.content_analysis)
print("Classifications:", result.document_classifications)
```

### Data Analysis Example

```python
from agent_playground.workflows.examples import create_data_analysis_workflow
from agent_playground.workflows.examples import DataAnalysisState

# Create workflow
workflow = create_data_analysis_workflow()

# Create initial state with data
initial_state = DataAnalysisState()
initial_state.raw_data = {
    "sales": [100, 150, 200, 180, 220],
    "customers": [50, 65, 80, 75, 90]
}

# Execute
result = await workflow.execute(initial_state)
print("Cleaned data:", result.cleaned_data)
print("Statistics:", result.statistical_analysis)
print("Insights:", result.insights)
```

### Customer Service Example

```python
from agent_playground.workflows.examples import create_customer_service_workflow
from agent_playground.workflows.examples import CustomerServiceState

# Create workflow
workflow = create_customer_service_workflow()

# Create initial state with customer query
initial_state = CustomerServiceState()
initial_state.customer_query = "I need help with my billing"
initial_state.customer_id = "CUST123"

# Execute
result = await workflow.execute(initial_state)
print("Intent:", result.intent_classification)
print("Sentiment:", result.sentiment_analysis)
print("Response:", result.generated_response)
```

## Workflow Visualization

Agent Playground provides rich visualization capabilities:

### Generate Reports

```python
from agent_playground.workflows.visualization import WorkflowVisualizer

# Create visualizer
visualizer = WorkflowVisualizer()

# Add workflow execution data
visualizer.record_execution(workflow_id, agent_name, start_time, end_time, status)

# Generate timeline plot
visualizer.plot_execution_timeline()

# Generate workflow graph
visualizer.plot_workflow_graph(workflow)

# Create HTML report
report_path = visualizer.generate_html_report("My Workflow Report")
print(f"Report saved to: {report_path}")
```

### Interactive Visualization

```python
from agent_playground.workflows.visualization import InteractiveWorkflowVisualizer

# Create interactive visualizer
interactive_viz = InteractiveWorkflowVisualizer()

# Generate interactive graph
interactive_viz.create_workflow_graph(workflow, execution_data)

# Save as HTML
interactive_viz.save_html("interactive_workflow.html")
```

## What's Next?

Now that you have Agent Playground running:

1. **Explore Templates**: Check out all available [workflow templates](workflow-templates.md)
2. **Read Tutorials**: Follow our [detailed tutorials](tutorials/) for advanced patterns
3. **Build Custom Agents**: Learn to create [custom agents](tutorials/custom-agents.md)
4. **Monitor Performance**: Set up [workflow monitoring](tutorials/monitoring.md)
5. **Optimize Workflows**: Read our [performance guide](performance.md)

## Common Issues

### Import Errors

If you see import errors, make sure you installed the package correctly:

```bash
pip install -e .
```

### CLI Not Found

If the `agent-playground` command is not found, make sure your Python scripts directory is in your PATH, or run:

```bash
python -m agent_playground.workflows.cli --help
```

### Async/Await Issues

Remember that workflow execution is async:

```python
# ✅ Correct
result = await workflow.execute(state)

# ❌ Incorrect  
result = workflow.execute(state)
```

---

**Need help?** Check out our [tutorials](tutorials/) or browse the [API reference](api/)!

# API Reference

Complete API documentation for Agent Playground framework.

## Core API

### Base Classes
- [`BaseAgent`](core/base-agent.md) - Abstract base class for all agents
- [`BaseState`](core/base-state.md) - Base state class for workflow data
- [`AgentConfig`](core/agent-config.md) - Configuration for agent behavior

### Workflow Components
- [`Workflow`](workflows/workflow.md) - Core workflow orchestration
- [`WorkflowBuilder`](workflows/builder.md) - Programmatic workflow construction
- [`WorkflowExecutor`](workflows/executor.md) - Workflow execution engine

## Workflow Templates

### Template System
- [`WorkflowTemplate`](templates/workflow-template.md) - Abstract template base class
- [`WorkflowTemplateRegistry`](templates/registry.md) - Template registration and discovery

### Built-in Templates
- [`SequentialWorkflowTemplate`](templates/sequential.md) - Sequential execution pattern
- [`ParallelWorkflowTemplate`](templates/parallel.md) - Parallel execution with aggregation
- [`ConditionalWorkflowTemplate`](templates/conditional.md) - Conditional branching
- [`HumanInLoopWorkflowTemplate`](templates/human-in-loop.md) - Human review integration
- [`ValidationWorkflowTemplate`](templates/validation.md) - Multi-stage validation
- [`AnalysisWorkflowTemplate`](templates/analysis.md) - Multi-perspective analysis
- [`TransformationWorkflowTemplate`](templates/transformation.md) - Data transformation

## Monitoring & Visualization

### Monitoring
- [`WorkflowMonitor`](monitor/workflow-monitor.md) - Real-time execution monitoring
- [`ExecutionMetrics`](monitor/execution-metrics.md) - Performance metrics collection
- [`WorkflowScheduler`](monitor/scheduler.md) - Workflow scheduling and automation

### Visualization
- [`WorkflowVisualizer`](visualization/workflow-visualizer.md) - Workflow visualization
- [`InteractiveWorkflowVisualizer`](visualization/interactive.md) - Interactive D3.js visualizations
- [`ReportGenerator`](visualization/report-generator.md) - HTML report generation

## Utilities

### Logging
- [`get_logger()`](utils/logging.md) - Structured logging with context
- [`LoggingContext`](utils/logging-context.md) - Logging context management

### Validation
- [`StateValidator`](utils/state-validator.md) - State validation utilities
- [`AgentValidator`](utils/agent-validator.md) - Agent validation utilities

### Serialization
- [`StateSerializer`](utils/serializer.md) - State serialization/deserialization
- [`WorkflowSerializer`](utils/workflow-serializer.md) - Workflow persistence

## Examples

### Example Workflows
- [`DocumentProcessingWorkflow`](examples/document-processing.md) - Document processing pipeline
- [`DataAnalysisWorkflow`](examples/data-analysis.md) - Data analysis workflow
- [`CustomerServiceWorkflow`](examples/customer-service.md) - Customer service automation

### Example Agents
- [`TextExtractionAgent`](examples/agents/text-extraction.md) - Text extraction from documents
- [`ContentAnalysisAgent`](examples/agents/content-analysis.md) - Content analysis and classification
- [`DataCleaningAgent`](examples/agents/data-cleaning.md) - Data preprocessing and cleaning

## CLI

- [`CLI Commands`](cli/commands.md) - Command-line interface reference
- [`Configuration`](cli/configuration.md) - CLI configuration options

## Integration

### LangChain
- [`LangChainAgentWrapper`](integrations/langchain-wrapper.md) - LangChain agent integration
- [`LangChainStateAdapter`](integrations/langchain-state.md) - State adaptation for LangChain

### LangGraph
- [`LangGraphWorkflowWrapper`](integrations/langgraph-wrapper.md) - LangGraph workflow integration
- [`LangGraphStateAdapter`](integrations/langgraph-state.md) - State adaptation for LangGraph

## Quick Reference

### Common Patterns

```python
# Create a simple workflow
from agent_playground.workflows import workflow_templates

workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents=[agent1, agent2, agent3],
    state_class=MyState
)

# Execute workflow
result = await workflow.execute(initial_state)
```

```python
# Monitor workflow execution
from agent_playground.workflows.monitor import WorkflowMonitor

async with WorkflowMonitor() as monitor:
    result = await workflow.execute(state, monitor=monitor)
    metrics = monitor.get_metrics()
```

```python
# Visualize workflow
from agent_playground.workflows.visualization import WorkflowVisualizer

visualizer = WorkflowVisualizer()
visualizer.record_execution(workflow_id, agent_name, start_time, end_time, status)
report_path = visualizer.generate_html_report("My Workflow")
```

### Type Hints

```python
from typing import TypeVar, Generic
from agent_playground.core import BaseState, BaseAgent

T = TypeVar('T', bound=BaseState)

class MyAgent(BaseAgent):
    async def execute(self, state: T) -> T:
        return state
```

### Error Handling

```python
from agent_playground.core.exceptions import (
    AgentExecutionError,
    WorkflowExecutionError,
    StateValidationError
)

try:
    result = await workflow.execute(state)
except WorkflowExecutionError as e:
    print(f"Workflow failed: {e.message}")
    if e.partial_state:
        # Handle partial results
        pass
```

---

**Navigation:**
- Browse by category using the sections above
- Use the search functionality to find specific APIs
- Check the [examples](../examples/) for practical usage patterns

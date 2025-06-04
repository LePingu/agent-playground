# Framework Overview

Agent Playground is a modern, type-safe framework for building multi-agent workflows. This guide explains the core concepts, architecture, and design principles.

## Core Concepts

### Agents

Agents are the fundamental building blocks of workflows. Each agent encapsulates specific functionality and can be composed into larger workflows.

```python
from agent_playground.core import BaseAgent, BaseState

class MyAgent(BaseAgent):
    def __init__(self, name: str = "MyAgent"):
        super().__init__(name)
    
    async def execute(self, state: BaseState) -> BaseState:
        # Agent logic here
        return state
```

**Key Properties:**
- **Stateless**: Agents don't maintain internal state between executions
- **Composable**: Can be combined into complex workflows
- **Type-safe**: Full type hints and validation
- **Async**: Built for concurrent execution

### State

State objects carry data through workflows. They're type-safe and can be extended for specific use cases.

```python
from agent_playground.core import BaseState

class MyWorkflowState(BaseState):
    input_data: str = ""
    processed_data: Dict[str, Any] = {}
    results: List[str] = []
```

**State Features:**
- **Pydantic-based**: Automatic validation and serialization
- **Extensible**: Create custom state classes for your workflows
- **Thread-safe**: Safe for concurrent access
- **Serializable**: Can be saved/loaded for persistence

### Workflows

Workflows orchestrate agents in specific patterns. They define the execution order and data flow.

```python
from agent_playground.workflows import WorkflowBuilder

# Programmatic workflow building
builder = WorkflowBuilder()
workflow = (builder
    .add_agent(agent1)
    .add_agent(agent2)
    .build())

# Template-based workflow creation
workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents=[agent1, agent2],
    state_class=MyState
)
```

## Architecture

The framework is organized into several layers:

### Core Layer (`agent_playground.core`)

- **BaseAgent**: Abstract base class for all agents
- **BaseState**: Base state class for workflow data
- **AgentConfig**: Configuration for agent behavior
- **Execution Engine**: Workflow execution and coordination

### Workflow Layer (`agent_playground.workflows`)

- **Templates**: Pre-built workflow patterns
- **Builder**: Programmatic workflow construction
- **Monitor**: Execution monitoring and metrics
- **Visualization**: Charts and reports

### Utilities Layer (`agent_playground.utils`)

- **Logging**: Structured logging with context
- **Metrics**: Performance measurement
- **Serialization**: State persistence
- **Validation**: Input/output validation

## Workflow Templates

Templates provide pre-built patterns for common workflow types:

### Sequential Template

Executes agents one after another:

```python
workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents=[agent1, agent2, agent3],
    state_class=MyState
)
```

**Use Cases:**
- Data processing pipelines
- Step-by-step analysis
- Document workflows

### Parallel Template

Executes agents concurrently with aggregation:

```python
workflow = workflow_templates.create_workflow(
    template_name="parallel",
    agents=[agent1, agent2, agent3],
    aggregator_agent=aggregator,
    state_class=MyState
)
```

**Use Cases:**
- Independent data analysis
- Concurrent API calls
- Multi-perspective evaluation

### Conditional Template

Branches execution based on state conditions:

```python
def routing_function(state):
    return "path_a" if state.condition else "path_b"

workflow = workflow_templates.create_workflow(
    template_name="conditional",
    condition_func=routing_function,
    agent_paths={
        "path_a": [agent_a1, agent_a2],
        "path_b": [agent_b1, agent_b2]
    },
    state_class=MyState
)
```

**Use Cases:**
- Dynamic routing
- Error recovery
- Business logic branching

### Human-in-the-Loop Template

Incorporates human review and approval:

```python
workflow = workflow_templates.create_workflow(
    template_name="human_in_loop",
    agents=[verification_agent],
    review_agent=human_review_agent,
    approval_required=True,
    state_class=MyState
)
```

**Use Cases:**
- Quality assurance
- Compliance review
- Critical decision points

### Validation Template

Multi-stage data validation:

```python
workflow = workflow_templates.create_workflow(
    template_name="validation",
    validators=[validator1, validator2],
    processor_agent=processor,
    state_class=MyState
)
```

**Use Cases:**
- Data quality checks
- Input validation
- Content moderation

### Analysis Template

Multi-perspective analysis with synthesis:

```python
workflow = workflow_templates.create_workflow(
    template_name="analysis",
    preprocessor_agent=preprocessor,
    analysis_agents=[analyst1, analyst2],
    synthesizer_agent=synthesizer,
    state_class=MyState
)
```

**Use Cases:**
- Research analysis
- Decision support
- Comparative evaluation

### Transformation Template

Data transformation workflows:

```python
workflow = workflow_templates.create_workflow(
    template_name="transformation",
    transformer_agents=[transformer1, transformer2],
    validator_agent=validator,
    state_class=MyState
)
```

**Use Cases:**
- Data migration
- Format conversion
- ETL processes

## Execution Model

### Asynchronous Execution

All workflows execute asynchronously for better performance:

```python
# Execute workflow
result = await workflow.execute(initial_state)

# Execute with monitoring
async with WorkflowMonitor() as monitor:
    result = await workflow.execute(initial_state, monitor=monitor)
```

### Error Handling

Built-in error handling and recovery:

```python
from agent_playground.workflows.monitor import ExecutionStatus

try:
    result = await workflow.execute(state)
except WorkflowExecutionError as e:
    print(f"Workflow failed: {e.message}")
    # Access partial results
    if e.partial_state:
        print(f"Completed steps: {e.completed_steps}")
```

### Monitoring and Metrics

Real-time execution monitoring:

```python
from agent_playground.workflows.monitor import WorkflowMonitor

monitor = WorkflowMonitor()
monitor.on_agent_start(lambda agent, state: print(f"Starting {agent.name}"))
monitor.on_agent_complete(lambda agent, state, duration: 
    print(f"{agent.name} completed in {duration:.2f}s"))

result = await workflow.execute(state, monitor=monitor)

# Access metrics
metrics = monitor.get_metrics()
print(f"Total duration: {metrics.total_duration}")
print(f"Agent count: {metrics.agent_count}")
```

## Type Safety

The framework is built with comprehensive type safety:

### Generic Types

Workflows and templates support generic typing:

```python
from typing import TypeVar

T = TypeVar('T', bound=BaseState)

class MyWorkflow(Workflow[T]):
    async def execute(self, state: T) -> T:
        return state
```

### State Validation

Automatic validation using Pydantic:

```python
from pydantic import validator

class ValidatedState(BaseState):
    value: int
    
    @validator('value')
    def validate_value(cls, v):
        if v < 0:
            raise ValueError('Value must be positive')
        return v
```

### Configuration Validation

Agent configurations are validated:

```python
from agent_playground.core import AgentConfig

config = AgentConfig(
    name="MyAgent",
    timeout=30,
    retry_count=3,
    # Type validation ensures correctness
)
```

## Design Principles

### 1. Composability

Agents and workflows can be composed into larger systems:

```python
# Compose workflows
sub_workflow1 = create_preprocessing_workflow()
sub_workflow2 = create_analysis_workflow()

main_workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents=[sub_workflow1, sub_workflow2],
    state_class=MyState
)
```

### 2. Observability

Built-in monitoring and tracing:

```python
# Execution tracing
tracer = ExecutionTracer()
result = await workflow.execute(state, tracer=tracer)

# View execution tree
tracer.print_execution_tree()

# Export trace data
trace_data = tracer.export_trace()
```

### 3. Testability

Easy to test components:

```python
import pytest
from agent_playground.testing import MockState, MockAgent

@pytest.mark.asyncio
async def test_my_agent():
    agent = MyAgent()
    state = MockState(input_data="test")
    
    result = await agent.execute(state)
    assert result.output_data == "processed: test"
```

### 4. Extensibility

Framework can be extended for specific use cases:

```python
class CustomAgent(BaseAgent):
    """Custom agent with domain-specific functionality."""
    
    def __init__(self, custom_config: Dict[str, Any]):
        super().__init__()
        self.custom_config = custom_config
    
    async def execute(self, state: BaseState) -> BaseState:
        # Custom logic
        return state

# Register custom template
@workflow_templates.register_template("custom")
class CustomWorkflowTemplate(WorkflowTemplate):
    # Custom template implementation
    pass
```

## Integration Points

### LangChain Integration

```python
from langchain.agents import AgentExecutor
from agent_playground.integrations.langchain import LangChainAgentWrapper

# Wrap LangChain agent
langchain_agent = AgentExecutor(...)
wrapped_agent = LangChainAgentWrapper(langchain_agent)

# Use in workflow
workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents=[wrapped_agent],
    state_class=MyState
)
```

### LangGraph Integration

```python
from langgraph import StateGraph
from agent_playground.integrations.langgraph import LangGraphWorkflowWrapper

# Wrap LangGraph workflow
langgraph_workflow = StateGraph(...)
wrapped_workflow = LangGraphWorkflowWrapper(langgraph_workflow)
```

### External APIs

```python
from agent_playground.integrations.http import HTTPAgent

# HTTP API integration
api_agent = HTTPAgent(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"}
)
```

---

**Next Steps:**
- Explore [workflow templates](workflow-templates.md) in detail
- Follow [tutorials](tutorials/) for hands-on examples
- Check out the [API reference](api/) for complete documentation

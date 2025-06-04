# BaseAgent API Reference

The `BaseAgent` class is the abstract base class for all agents in Agent Playground. It defines the core interface and common functionality that all agents must implement.

## Class Definition

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from agent_playground.core.base import BaseState

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: Optional[str] = None):
        """Initialize the agent with an optional name."""
    
    @abstractmethod
    async def execute(self, state: BaseState) -> BaseState:
        """Execute the agent's main logic."""
        pass
    
    # Additional methods...
```

## Constructor

### `__init__(name: Optional[str] = None)`

Initializes a new agent instance.

**Parameters:**
- `name` (Optional[str]): Human-readable name for the agent. If not provided, uses the class name.

**Example:**
```python
class MyAgent(BaseAgent):
    def __init__(self, custom_name: str = "MyAgent"):
        super().__init__(custom_name)
    
    async def execute(self, state: BaseState) -> BaseState:
        return state

# Create agent with default name
agent1 = MyAgent()
print(agent1.name)  # "MyAgent"

# Create agent with custom name
agent2 = MyAgent("CustomProcessor")
print(agent2.name)  # "CustomProcessor"
```

## Abstract Methods

### `execute(state: BaseState) -> BaseState`

**Required.** The main execution method that must be implemented by all agents.

**Parameters:**
- `state` (BaseState): The current workflow state

**Returns:**
- `BaseState`: The modified state after agent execution

**Raises:**
- `AgentExecutionError`: When agent execution fails
- `StateValidationError`: When state validation fails

**Example:**
```python
class TextProcessor(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        # Get input text from state
        input_text = getattr(state, 'input_text', '')
        
        # Process the text
        processed_text = input_text.upper()
        
        # Store result in state
        state.processed_text = processed_text
        state.processing_complete = True
        
        return state
```

## Properties

### `name: str`

The agent's name, used for identification and logging.

```python
agent = MyAgent("DataProcessor")
print(agent.name)  # "DataProcessor"
```

### `agent_id: str`

Unique identifier for the agent instance (auto-generated).

```python
agent = MyAgent()
print(agent.agent_id)  # "MyAgent_abc123def456"
```

### `execution_count: int`

Number of times this agent has been executed.

```python
agent = MyAgent()
print(agent.execution_count)  # 0

await agent.execute(state)
print(agent.execution_count)  # 1
```

### `last_execution_time: Optional[datetime]`

Timestamp of the last execution.

```python
from datetime import datetime

agent = MyAgent()
print(agent.last_execution_time)  # None

await agent.execute(state)
print(agent.last_execution_time)  # datetime(2023, 12, 01, 10, 30, 45)
```

## Methods

### `validate_state(state: BaseState) -> bool`

Validates the input state before execution.

**Parameters:**
- `state` (BaseState): State to validate

**Returns:**
- `bool`: True if state is valid, False otherwise

**Example:**
```python
class ValidatingAgent(BaseAgent):
    def validate_state(self, state: BaseState) -> bool:
        # Check if required fields exist
        required_fields = ['input_data', 'data_type']
        return all(hasattr(state, field) for field in required_fields)
    
    async def execute(self, state: BaseState) -> BaseState:
        if not self.validate_state(state):
            raise StateValidationError("Missing required fields")
        
        # Continue with execution
        return state
```

### `setup() -> None`

Called once before the first execution. Override for initialization logic.

**Example:**
```python
class DatabaseAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.connection = None
    
    async def setup(self):
        """Initialize database connection."""
        self.connection = await create_db_connection()
    
    async def execute(self, state: BaseState) -> BaseState:
        if not self.connection:
            await self.setup()
        
        # Use self.connection...
        return state
```

### `teardown() -> None`

Called after the last execution. Override for cleanup logic.

**Example:**
```python
class ResourceAgent(BaseAgent):
    async def teardown(self):
        """Clean up resources."""
        if hasattr(self, 'connection') and self.connection:
            await self.connection.close()
```

### `get_metrics() -> Dict[str, Any]`

Returns execution metrics for the agent.

**Returns:**
- `Dict[str, Any]`: Dictionary containing metrics

**Example:**
```python
agent = MyAgent()
await agent.execute(state)

metrics = agent.get_metrics()
print(metrics)
# {
#     'execution_count': 1,
#     'total_execution_time': 0.123,
#     'average_execution_time': 0.123,
#     'last_execution_time': '2023-12-01T10:30:45',
#     'success_rate': 1.0
# }
```

## Error Handling

### Built-in Error Handling

The base class provides automatic error handling and metrics collection:

```python
class ErrorProneAgent(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        # This might raise an exception
        risky_operation()
        return state

# Errors are automatically caught and recorded
try:
    await agent.execute(state)
except AgentExecutionError as e:
    print(f"Agent failed: {e.message}")
    print(f"Original error: {e.original_error}")
```

### Custom Error Handling

```python
class CustomErrorAgent(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        try:
            # Your logic here
            result = await some_operation()
            state.result = result
        except SpecificException as e:
            # Handle specific error
            state.error = f"Specific error: {e}"
            state.success = False
        except Exception as e:
            # Handle general errors
            state.error = f"Unexpected error: {e}"
            state.success = False
        
        return state
```

## Lifecycle Hooks

### Execution Lifecycle

The agent execution follows this lifecycle:

1. `validate_state()` - Validate input state
2. `on_before_execute()` - Pre-execution hook
3. `execute()` - Main execution logic
4. `on_after_execute()` - Post-execution hook
5. `on_error()` - Error handling (if needed)

```python
class LifecycleAgent(BaseAgent):
    async def on_before_execute(self, state: BaseState):
        """Called before execute()."""
        self.start_time = time.time()
        print(f"Starting {self.name}")
    
    async def execute(self, state: BaseState) -> BaseState:
        # Main logic
        return state
    
    async def on_after_execute(self, state: BaseState):
        """Called after successful execute()."""
        duration = time.time() - self.start_time
        print(f"{self.name} completed in {duration:.2f}s")
    
    async def on_error(self, state: BaseState, error: Exception):
        """Called when execute() raises an exception."""
        print(f"{self.name} failed: {error}")
```

## Advanced Usage

### Generic Agents

Use type hints for better type safety:

```python
from typing import TypeVar, Generic

T = TypeVar('T', bound=BaseState)

class GenericAgent(BaseAgent, Generic[T]):
    async def execute(self, state: T) -> T:
        # Type-safe agent implementation
        return state

# Usage with specific state type
class MyState(BaseState):
    data: str = ""

agent: GenericAgent[MyState] = GenericAgent()
result: MyState = await agent.execute(MyState())
```

### Configurable Agents

```python
from dataclasses import dataclass

@dataclass
class ProcessorConfig:
    batch_size: int = 100
    timeout: float = 30.0
    retry_count: int = 3

class ConfigurableAgent(BaseAgent):
    def __init__(self, config: ProcessorConfig):
        super().__init__()
        self.config = config
    
    async def execute(self, state: BaseState) -> BaseState:
        # Use self.config.batch_size, etc.
        return state
```

### Stateful Agents

While agents should generally be stateless, you can maintain state for caching or optimization:

```python
class CachingAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self._cache = {}
    
    async def execute(self, state: BaseState) -> BaseState:
        # Check cache first
        cache_key = self._get_cache_key(state)
        if cache_key in self._cache:
            state.result = self._cache[cache_key]
            state.cache_hit = True
        else:
            # Compute result
            result = await self._compute_result(state)
            self._cache[cache_key] = result
            state.result = result
            state.cache_hit = False
        
        return state
    
    def _get_cache_key(self, state: BaseState) -> str:
        # Generate cache key from state
        return f"{state.input_data}_{state.parameters}"
```

## Best Practices

### 1. Single Responsibility

Each agent should have one clear responsibility:

```python
# ✅ Good
class TextExtractor(BaseAgent):
    """Extracts text from documents."""
    async def execute(self, state: BaseState) -> BaseState:
        # Only extract text
        pass

# ❌ Bad
class TextExtractorAndAnalyzer(BaseAgent):
    """Extracts and analyzes text."""  # Too many responsibilities
    pass
```

### 2. Immutable State Updates

Don't modify existing state fields, add new ones:

```python
# ✅ Good
async def execute(self, state: BaseState) -> BaseState:
    state.processed_data = self.process(state.raw_data)
    return state

# ❌ Bad
async def execute(self, state: BaseState) -> BaseState:
    state.raw_data = self.process(state.raw_data)  # Loses original
    return state
```

### 3. Error Handling

Always handle errors gracefully:

```python
async def execute(self, state: BaseState) -> BaseState:
    try:
        result = await self.risky_operation()
        state.result = result
        state.success = True
    except Exception as e:
        state.error = str(e)
        state.success = False
    
    return state
```

### 4. Resource Management

Clean up resources properly:

```python
class ResourceAgent(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        resource = None
        try:
            resource = await acquire_resource()
            # Use resource
            return state
        finally:
            if resource:
                await resource.cleanup()
```

### 5. Documentation

Document your agents clearly:

```python
class DocumentedAgent(BaseAgent):
    """
    Processes customer data and generates insights.
    
    This agent takes customer interaction data and:
    1. Cleans and validates the data
    2. Extracts key metrics
    3. Generates actionable insights
    
    State Requirements:
        - customer_data: Dict[str, Any]
        - time_period: str
    
    State Outputs:
        - metrics: Dict[str, float]
        - insights: List[str]
        - processing_success: bool
    """
    
    async def execute(self, state: BaseState) -> BaseState:
        # Implementation
        pass
```

## See Also

- [BaseState API](base-state.md) - State management
- [AgentConfig API](agent-config.md) - Agent configuration
- [Workflow API](../workflows/workflow.md) - Workflow orchestration
- [Custom Agents Tutorial](../../tutorials/custom-agents.md) - Detailed tutorial

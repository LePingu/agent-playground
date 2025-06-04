# Workflow API Reference

The `Workflow` class is the core orchestration component that manages the execution of agents in Agent Playground. It provides the foundation for building and executing multi-agent workflows with monitoring, error handling, and state management.

## Class Definition

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from agent_playground.core.base import BaseAgent, BaseState
from agent_playground.workflows.monitor import WorkflowMonitor
from agent_playground.utils.logging import get_logger

T = TypeVar('T', bound=BaseState)

class Workflow(ABC, Generic[T]):
    """Abstract base class for all workflows."""
    
    def __init__(
        self,
        name: str,
        agents: List[BaseAgent],
        state_class: type[T],
        description: str = "",
        version: str = "1.0.0"
    ):
        """Initialize the workflow."""
        self.name = name
        self.agents = agents
        self.state_class = state_class
        self.description = description
        self.version = version
        self.logger = get_logger(f"workflow.{name}")
    
    @abstractmethod
    async def execute(
        self,
        initial_state: T,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> T:
        """Execute the workflow with the given initial state."""
        pass
    
    # Additional methods...
```

## Core Properties

### `name: str`

Unique identifier for the workflow.

**Usage:** Workflow identification, logging, and monitoring

```python
workflow = MyWorkflow(
    name="document_processing",
    agents=[extractor, analyzer],
    state_class=DocumentState
)
print(workflow.name)  # "document_processing"
```

### `agents: List[BaseAgent]`

List of agents that participate in the workflow.

**Usage:** Agent execution and dependency management

```python
agents = [
    TextExtractionAgent(),
    ContentAnalysisAgent(),
    ClassificationAgent()
]

workflow = SequentialWorkflow(
    name="analysis_pipeline",
    agents=agents,
    state_class=AnalysisState
)
```

### `state_class: type[T]`

The state class used throughout the workflow execution.

**Usage:** Type safety and state validation

```python
class ProcessingState(BaseState):
    input_data: str = ""
    results: Dict[str, Any] = {}

workflow = MyWorkflow(
    name="processor",
    agents=agents,
    state_class=ProcessingState  # Enforces type safety
)
```

### `description: str`

Human-readable description of the workflow's purpose.

**Default:** Empty string  
**Usage:** Documentation and monitoring dashboards

```python
workflow = DataAnalysisWorkflow(
    name="customer_insights",
    agents=analysis_agents,
    state_class=CustomerState,
    description="Analyzes customer data to generate actionable insights"
)
```

### `version: str`

Version identifier for the workflow.

**Default:** "1.0.0"  
**Usage:** Deployment tracking and compatibility management

```python
workflow = MLPipelineWorkflow(
    name="recommendation_engine",
    agents=ml_agents,
    state_class=MLState,
    version="2.3.1"
)
```

## Abstract Methods

### `execute(initial_state: T, monitor: Optional[WorkflowMonitor] = None, **kwargs) -> T`

**Required.** Execute the workflow with the provided initial state.

**Parameters:**
- `initial_state` (T): The starting state for workflow execution
- `monitor` (Optional[WorkflowMonitor]): Optional monitoring instance
- `**kwargs`: Additional execution parameters

**Returns:**
- `T`: The final state after workflow completion

**Raises:**
- `WorkflowExecutionError`: When workflow execution fails
- `StateValidationError`: When state validation fails

**Example:**
```python
class SequentialWorkflow(Workflow[T]):
    async def execute(
        self,
        initial_state: T,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> T:
        """Execute agents sequentially."""
        state = initial_state
        
        for agent in self.agents:
            if monitor:
                monitor.on_agent_start(agent, state)
            
            try:
                state = await agent.execute(state)
                
                if monitor:
                    monitor.on_agent_complete(agent, state)
                    
            except Exception as e:
                if monitor:
                    monitor.on_agent_error(agent, state, e)
                raise WorkflowExecutionError(f"Agent {agent.name} failed: {e}")
        
        return state
```

## Common Methods

### `validate_state(state: T) -> bool`

Validate the provided state against the workflow's state schema.

**Parameters:**
- `state` (T): State to validate

**Returns:**
- `bool`: True if state is valid

**Example:**
```python
state = MyState(input_data="test")
if workflow.validate_state(state):
    result = await workflow.execute(state)
else:
    print("Invalid state provided")
```

### `get_agent_by_name(name: str) -> Optional[BaseAgent]`

Retrieve an agent by its name.

**Parameters:**
- `name` (str): Agent name to search for

**Returns:**
- `Optional[BaseAgent]`: Agent instance or None

**Example:**
```python
extractor = workflow.get_agent_by_name("TextExtractionAgent")
if extractor:
    print(f"Found agent: {extractor.name}")
```

### `get_execution_plan() -> List[Dict[str, Any]]`

Get a description of the workflow's execution plan.

**Returns:**
- `List[Dict[str, Any]]`: List of execution steps

**Example:**
```python
plan = workflow.get_execution_plan()
for step in plan:
    print(f"Step {step['order']}: {step['agent']} - {step['description']}")
```

### `estimate_duration() -> float`

Estimate the total execution duration in seconds.

**Returns:**
- `float`: Estimated duration in seconds

**Example:**
```python
estimated_time = workflow.estimate_duration()
print(f"Estimated execution time: {estimated_time:.1f} seconds")
```

### `clone() -> Workflow[T]`

Create a copy of the workflow with the same configuration.

**Returns:**
- `Workflow[T]`: New workflow instance

**Example:**
```python
workflow_copy = workflow.clone()
workflow_copy.name = "copied_workflow"
```

## Execution Patterns

### Sequential Execution

```python
class SequentialWorkflow(Workflow[T]):
    """Executes agents one after another."""
    
    async def execute(
        self,
        initial_state: T,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> T:
        state = initial_state
        
        for i, agent in enumerate(self.agents):
            self.logger.info(f"Executing agent {i+1}/{len(self.agents)}: {agent.name}")
            
            if monitor:
                monitor.record_agent_start(agent.name)
            
            start_time = time.time()
            try:
                state = await agent.execute(state)
                duration = time.time() - start_time
                
                if monitor:
                    monitor.record_agent_completion(agent.name, duration)
                    
            except Exception as e:
                if monitor:
                    monitor.record_agent_error(agent.name, str(e))
                self.logger.error(f"Agent {agent.name} failed: {e}")
                raise WorkflowExecutionError(f"Sequential workflow failed at {agent.name}")
        
        return state
```

### Parallel Execution

```python
class ParallelWorkflow(Workflow[T]):
    """Executes agents in parallel with aggregation."""
    
    def __init__(
        self,
        name: str,
        agents: List[BaseAgent],
        aggregator_agent: BaseAgent,
        state_class: type[T],
        max_concurrent: Optional[int] = None,
        **kwargs
    ):
        super().__init__(name, agents, state_class, **kwargs)
        self.aggregator_agent = aggregator_agent
        self.max_concurrent = max_concurrent or len(agents)
    
    async def execute(
        self,
        initial_state: T,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> T:
        # Execute agents in parallel
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def execute_agent(agent: BaseAgent, state: T) -> T:
            async with semaphore:
                if monitor:
                    monitor.record_agent_start(agent.name)
                
                try:
                    result = await agent.execute(state.clone())
                    if monitor:
                        monitor.record_agent_completion(agent.name)
                    return result
                except Exception as e:
                    if monitor:
                        monitor.record_agent_error(agent.name, str(e))
                    raise
        
        # Execute all agents concurrently
        tasks = [execute_agent(agent, initial_state) for agent in self.agents]
        parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for errors
        errors = [r for r in parallel_results if isinstance(r, Exception)]
        if errors:
            raise WorkflowExecutionError(f"Parallel execution failed: {errors}")
        
        # Aggregate results
        aggregated_state = initial_state.clone()
        aggregated_state.parallel_results = parallel_results
        
        return await self.aggregator_agent.execute(aggregated_state)
```

### Conditional Execution

```python
class ConditionalWorkflow(Workflow[T]):
    """Executes different agent paths based on conditions."""
    
    def __init__(
        self,
        name: str,
        condition_func: callable,
        agent_paths: Dict[str, List[BaseAgent]],
        state_class: type[T],
        **kwargs
    ):
        # Flatten all agents for the parent class
        all_agents = []
        for agents in agent_paths.values():
            all_agents.extend(agents)
        
        super().__init__(name, all_agents, state_class, **kwargs)
        self.condition_func = condition_func
        self.agent_paths = agent_paths
    
    async def execute(
        self,
        initial_state: T,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> T:
        # Determine which path to take
        path_key = self.condition_func(initial_state)
        
        if path_key not in self.agent_paths:
            raise WorkflowExecutionError(f"Invalid path key: {path_key}")
        
        selected_agents = self.agent_paths[path_key]
        self.logger.info(f"Taking path '{path_key}' with {len(selected_agents)} agents")
        
        # Execute the selected path sequentially
        state = initial_state
        for agent in selected_agents:
            if monitor:
                monitor.record_agent_start(agent.name)
            
            state = await agent.execute(state)
            
            if monitor:
                monitor.record_agent_completion(agent.name)
        
        # Record which path was taken
        state.execution_path_taken = path_key
        return state
```

## Error Handling

### Built-in Error Recovery

```python
class ResilientWorkflow(Workflow[T]):
    """Workflow with built-in error recovery."""
    
    def __init__(
        self,
        name: str,
        agents: List[BaseAgent],
        state_class: type[T],
        recovery_strategy: str = "continue",
        **kwargs
    ):
        super().__init__(name, agents, state_class, **kwargs)
        self.recovery_strategy = recovery_strategy
    
    async def execute(
        self,
        initial_state: T,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> T:
        state = initial_state
        
        for agent in self.agents:
            try:
                state = await agent.execute(state)
                
            except Exception as e:
                self.logger.error(f"Agent {agent.name} failed: {e}")
                
                # Add error to state
                state.add_error(agent.name, str(e))
                
                # Apply recovery strategy
                if self.recovery_strategy == "stop":
                    raise WorkflowExecutionError(f"Workflow stopped due to error in {agent.name}")
                elif self.recovery_strategy == "continue":
                    self.logger.warning(f"Continuing workflow despite error in {agent.name}")
                    continue
                elif self.recovery_strategy == "retry":
                    retry_result = await self._retry_agent(agent, state)
                    if retry_result:
                        state = retry_result
                    else:
                        raise WorkflowExecutionError(f"Retry failed for {agent.name}")
        
        return state
    
    async def _retry_agent(self, agent: BaseAgent, state: T, max_retries: int = 3) -> Optional[T]:
        """Retry a failed agent with exponential backoff."""
        for attempt in range(max_retries):
            try:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                return await agent.execute(state)
            except Exception as e:
                self.logger.warning(f"Retry {attempt + 1} failed for {agent.name}: {e}")
        
        return None
```

### Custom Error Handling

```python
class CustomErrorWorkflow(Workflow[T]):
    """Workflow with custom error handling logic."""
    
    def __init__(
        self,
        name: str,
        agents: List[BaseAgent],
        state_class: type[T],
        error_handlers: Dict[str, callable] = None,
        **kwargs
    ):
        super().__init__(name, agents, state_class, **kwargs)
        self.error_handlers = error_handlers or {}
    
    async def execute(
        self,
        initial_state: T,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> T:
        state = initial_state
        
        for agent in self.agents:
            try:
                state = await agent.execute(state)
                
            except Exception as e:
                # Check for custom error handler
                handler = self.error_handlers.get(agent.name)
                if handler:
                    state = await handler(agent, state, e)
                else:
                    # Default error handling
                    state.add_error(agent.name, str(e))
                    self.logger.error(f"Unhandled error in {agent.name}: {e}")
        
        return state
```

## Monitoring Integration

### Real-time Monitoring

```python
class MonitoredWorkflow(Workflow[T]):
    """Workflow with comprehensive monitoring."""
    
    async def execute(
        self,
        initial_state: T,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> T:
        # Create monitor if not provided
        if monitor is None:
            monitor = WorkflowMonitor()
        
        # Start workflow monitoring
        monitor.start_workflow(self.name)
        
        try:
            state = initial_state
            
            for agent in self.agents:
                # Pre-execution monitoring
                monitor.on_agent_start(agent, state)
                
                start_time = time.time()
                start_memory = self._get_memory_usage()
                
                # Execute agent
                state = await agent.execute(state)
                
                # Post-execution monitoring
                duration = time.time() - start_time
                memory_delta = self._get_memory_usage() - start_memory
                
                monitor.on_agent_complete(
                    agent, state, duration, memory_delta
                )
            
            # Workflow completed successfully
            monitor.complete_workflow(self.name, True)
            return state
            
        except Exception as e:
            # Workflow failed
            monitor.complete_workflow(self.name, False, str(e))
            raise
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        import psutil
        return psutil.Process().memory_info().rss
```

### Performance Tracking

```python
class PerformanceTrackingWorkflow(Workflow[T]):
    """Workflow that tracks detailed performance metrics."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.performance_metrics = {
            'total_duration': 0.0,
            'agent_durations': {},
            'memory_usage': {},
            'cpu_usage': {},
            'execution_count': 0
        }
    
    async def execute(
        self,
        initial_state: T,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> T:
        workflow_start = time.time()
        self.performance_metrics['execution_count'] += 1
        
        state = initial_state
        
        for agent in self.agents:
            # Track agent performance
            agent_start = time.time()
            
            state = await agent.execute(state)
            
            agent_duration = time.time() - agent_start
            self.performance_metrics['agent_durations'][agent.name] = agent_duration
        
        # Track total workflow performance
        total_duration = time.time() - workflow_start
        self.performance_metrics['total_duration'] = total_duration
        
        # Add performance data to state
        state.performance_metrics = self.performance_metrics.copy()
        
        return state
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        total_agent_time = sum(self.performance_metrics['agent_durations'].values())
        
        return {
            'total_executions': self.performance_metrics['execution_count'],
            'avg_total_duration': self.performance_metrics['total_duration'],
            'total_agent_time': total_agent_time,
            'overhead_time': self.performance_metrics['total_duration'] - total_agent_time,
            'slowest_agent': max(
                self.performance_metrics['agent_durations'].items(),
                key=lambda x: x[1],
                default=("None", 0)
            )
        }
```

## Best Practices

### 1. Workflow Design

```python
# ✅ Good: Clear, single-purpose workflow
class DocumentAnalysisWorkflow(Workflow[DocumentState]):
    """Analyzes documents for content, sentiment, and classification."""
    
    def __init__(self):
        agents = [
            TextExtractionAgent(),
            SentimentAnalysisAgent(),
            ContentClassificationAgent(),
            ReportGenerationAgent()
        ]
        super().__init__(
            name="document_analysis",
            agents=agents,
            state_class=DocumentState,
            description="Comprehensive document analysis pipeline"
        )

# ❌ Bad: Generic, unclear purpose
class GenericWorkflow(Workflow[BaseState]):
    """Does various things."""  # Unclear purpose
    pass
```

### 2. Error Handling Strategy

```python
class RobustWorkflow(Workflow[T]):
    """Workflow with comprehensive error handling."""
    
    async def execute(self, initial_state: T, **kwargs) -> T:
        state = initial_state
        
        for agent in self.agents:
            try:
                # Validate input state
                if not self._validate_agent_input(agent, state):
                    raise StateValidationError(f"Invalid input for {agent.name}")
                
                # Execute with timeout
                state = await asyncio.wait_for(
                    agent.execute(state),
                    timeout=agent.config.timeout if hasattr(agent, 'config') else 300
                )
                
                # Validate output state
                if not self._validate_agent_output(agent, state):
                    raise StateValidationError(f"Invalid output from {agent.name}")
                
            except Exception as e:
                # Log error with context
                self.logger.error(f"Agent {agent.name} failed", extra={
                    'agent': agent.name,
                    'state_id': getattr(state, 'id', 'unknown'),
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                
                # Add to state error collection
                state.add_error(agent.name, str(e), {'error_type': type(e).__name__})
        
        return state
```

### 3. State Management

```python
class StateAwareWorkflow(Workflow[T]):
    """Workflow that carefully manages state transitions."""
    
    async def execute(self, initial_state: T, **kwargs) -> T:
        # Create execution context
        state = initial_state.clone()
        state.workflow_name = self.name
        state.execution_id = str(uuid.uuid4())
        state.started_at = datetime.utcnow()
        
        try:
            for agent in self.agents:
                # Checkpoint state before agent execution
                checkpoint = state.clone()
                
                # Execute agent
                state = await agent.execute(state)
                
                # Verify state integrity
                if not self._verify_state_integrity(checkpoint, state):
                    self.logger.warning(f"State integrity check failed for {agent.name}")
                
                # Update execution path
                state.execution_path.append(agent.name)
            
            # Mark completion
            state.completed_at = datetime.utcnow()
            state.success = True
            
        except Exception as e:
            state.completed_at = datetime.utcnow()
            state.success = False
            state.failure_reason = str(e)
            raise
        
        return state
```

### 4. Resource Management

```python
class ResourceManagedWorkflow(Workflow[T]):
    """Workflow with proper resource management."""
    
    def __init__(self, *args, max_memory_mb: int = 1024, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_memory_mb = max_memory_mb
        self._resources = []
    
    async def execute(self, initial_state: T, **kwargs) -> T:
        try:
            # Initialize resources
            await self._initialize_resources()
            
            # Monitor memory usage
            memory_monitor = asyncio.create_task(self._monitor_memory())
            
            # Execute workflow
            state = await self._execute_workflow(initial_state, **kwargs)
            
            return state
            
        finally:
            # Always cleanup resources
            memory_monitor.cancel()
            await self._cleanup_resources()
    
    async def _monitor_memory(self):
        """Monitor memory usage during execution."""
        while True:
            memory_mb = self._get_memory_usage() / (1024 * 1024)
            if memory_mb > self.max_memory_mb:
                self.logger.warning(f"Memory usage ({memory_mb:.1f}MB) exceeds limit ({self.max_memory_mb}MB)")
            await asyncio.sleep(1)
    
    async def _cleanup_resources(self):
        """Clean up all allocated resources."""
        for resource in self._resources:
            try:
                await resource.close()
            except Exception as e:
                self.logger.error(f"Error cleaning up resource: {e}")
```

## See Also

- [BaseAgent API](../core/base-agent.md) - Agent base class
- [BaseState API](../core/base-state.md) - State management
- [WorkflowMonitor API](../monitor/workflow-monitor.md) - Execution monitoring
- [Workflow Templates](../../workflow-templates.md) - Pre-built workflow patterns
- [Workflow Building Tutorial](../../tutorials/workflow-building.md) - Detailed workflow tutorial

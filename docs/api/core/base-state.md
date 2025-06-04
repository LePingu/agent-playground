# BaseState API Reference

The `BaseState` class is the foundation for all state objects in Agent Playground workflows. It provides the core data structure that flows through agent pipelines, ensuring type safety and validation.

## Class Definition

```python
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class BaseState(BaseModel):
    """Base state class for all workflow states."""
    
    # Core metadata
    id: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    
    # Execution tracking
    current_agent: Optional[str] = None
    execution_path: List[str] = []
    
    # Error handling
    errors: List[Dict[str, Any]] = []
    warnings: List[str] = []
    
    # Additional properties...
```

## Core Properties

### `id: str`

Unique identifier for the state instance.

**Default:** Empty string  
**Usage:** Automatically set during workflow execution

```python
state = MyState(id="workflow_123")
print(state.id)  # "workflow_123"
```

### `created_at: datetime`

Timestamp when the state was created.

**Default:** `None` (set automatically on creation)  
**Usage:** Tracking workflow creation time

```python
state = MyState()
print(state.created_at)  # 2024-01-15T10:30:00
```

### `updated_at: datetime`

Timestamp of the last state update.

**Default:** `None` (updated automatically)  
**Usage:** Tracking last modification time

### `current_agent: Optional[str]`

Name of the currently executing agent.

**Default:** `None`  
**Usage:** Set automatically during agent execution

```python
# Set automatically by framework
assert state.current_agent == "DataProcessorAgent"
```

### `execution_path: List[str]`

List of agents that have processed this state.

**Default:** Empty list  
**Usage:** Tracking workflow execution history

```python
# After execution
print(state.execution_path)
# ["PreprocessorAgent", "AnalysisAgent", "FormatterAgent"]
```

### `errors: List[Dict[str, Any]]`

Collection of errors encountered during execution.

**Default:** Empty list  
**Structure:** Each error contains agent name, message, timestamp, and details

```python
# Error structure
{
    "agent": "ProcessorAgent",
    "message": "Invalid input format",
    "timestamp": "2024-01-15T10:30:00",
    "details": {"input_type": "invalid"}
}
```

### `warnings: List[str]`

Non-fatal warnings generated during execution.

**Default:** Empty list  
**Usage:** Storing advisory messages

```python
state.warnings.append("Input data quality is low")
```

## Methods

### `add_error(agent_name: str, message: str, details: Dict[str, Any] = None)`

Add an error to the state error collection.

**Parameters:**
- `agent_name` (str): Name of the agent that encountered the error
- `message` (str): Error message
- `details` (Dict[str, Any], optional): Additional error details

**Example:**
```python
state.add_error(
    agent_name="ValidationAgent",
    message="Schema validation failed",
    details={"field": "email", "value": "invalid-email"}
)
```

### `add_warning(message: str)`

Add a warning message to the state.

**Parameters:**
- `message` (str): Warning message

**Example:**
```python
state.add_warning("Processing with incomplete data")
```

### `has_errors() -> bool`

Check if the state contains any errors.

**Returns:**
- `bool`: True if errors exist, False otherwise

**Example:**
```python
if state.has_errors():
    print(f"Found {len(state.errors)} errors")
    for error in state.errors:
        print(f"  {error['agent']}: {error['message']}")
```

### `clear_errors()`

Remove all errors from the state.

**Example:**
```python
state.clear_errors()
assert len(state.errors) == 0
```

### `get_last_error() -> Optional[Dict[str, Any]]`

Get the most recent error, if any.

**Returns:**
- `Optional[Dict[str, Any]]`: Latest error or None

**Example:**
```python
last_error = state.get_last_error()
if last_error:
    print(f"Last error: {last_error['message']}")
```

### `clone() -> BaseState`

Create a deep copy of the state.

**Returns:**
- `BaseState`: New state instance with copied data

**Example:**
```python
new_state = state.clone()
new_state.id = "new_workflow"
# Original state unchanged
```

### `to_dict() -> Dict[str, Any]`

Convert state to dictionary representation.

**Returns:**
- `Dict[str, Any]`: Dictionary containing all state data

**Example:**
```python
state_dict = state.to_dict()
print(state_dict["execution_path"])
```

### `from_dict(data: Dict[str, Any]) -> BaseState`

Create state instance from dictionary.

**Parameters:**
- `data` (Dict[str, Any]): Dictionary containing state data

**Returns:**
- `BaseState`: New state instance

**Example:**
```python
data = {"id": "test", "execution_path": ["agent1"]}
state = MyState.from_dict(data)
```

## Custom State Classes

### Basic Custom State

```python
class DocumentProcessingState(BaseState):
    """State for document processing workflows."""
    
    # Input data
    document_path: str = ""
    document_type: str = ""
    
    # Processing results
    extracted_text: str = ""
    analysis_results: Dict[str, Any] = {}
    
    # Status tracking
    processing_complete: bool = False
    quality_score: float = 0.0
```

### Advanced Custom State

```python
from pydantic import validator, Field
from typing import List, Optional
from enum import Enum

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DataAnalysisState(BaseState):
    """Advanced state with validation and constraints."""
    
    # Input configuration
    dataset_path: str = Field(..., description="Path to input dataset")
    analysis_type: str = Field(..., regex="^(statistical|predictive|descriptive)$")
    
    # Processing parameters
    batch_size: int = Field(default=1000, gt=0, le=10000)
    confidence_threshold: float = Field(default=0.95, ge=0.0, le=1.0)
    
    # Results
    status: ProcessingStatus = ProcessingStatus.PENDING
    processed_records: int = 0
    results: Dict[str, Any] = {}
    
    # Validation
    @validator('dataset_path')
    def validate_dataset_path(cls, v):
        if not v.endswith(('.csv', '.json', '.parquet')):
            raise ValueError('Dataset must be CSV, JSON, or Parquet format')
        return v
    
    @validator('results')
    def validate_results(cls, v):
        if v and 'accuracy' in v:
            if not 0 <= v['accuracy'] <= 1:
                raise ValueError('Accuracy must be between 0 and 1')
        return v
```

## State Validation

### Built-in Validation

BaseState uses Pydantic for automatic validation:

```python
class ValidatedState(BaseState):
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=0, le=150)
    score: float = Field(default=0.0, ge=0.0, le=100.0)

# Validation happens automatically
try:
    state = ValidatedState(
        email="invalid-email",  # Will raise ValidationError
        age=-5                  # Will raise ValidationError
    )
except ValidationError as e:
    print(e.errors())
```

### Custom Validators

Add domain-specific validation:

```python
class BusinessState(BaseState):
    revenue: float = 0.0
    expenses: float = 0.0
    profit: float = 0.0
    
    @validator('profit', always=True)
    def calculate_profit(cls, v, values):
        """Automatically calculate profit from revenue and expenses."""
        return values.get('revenue', 0) - values.get('expenses', 0)
    
    @validator('expenses')
    def validate_expenses(cls, v, values):
        """Ensure expenses don't exceed revenue."""
        revenue = values.get('revenue', 0)
        if v > revenue:
            raise ValueError('Expenses cannot exceed revenue')
        return v
```

## Serialization

### JSON Serialization

```python
# To JSON
state_json = state.model_dump_json()
print(state_json)

# From JSON
state = MyState.model_validate_json(state_json)
```

### Dictionary Serialization

```python
# To dict
state_dict = state.model_dump()

# From dict
state = MyState.model_validate(state_dict)
```

### Selective Serialization

```python
# Exclude sensitive fields
public_data = state.model_dump(exclude={'errors', 'warnings'})

# Include only specific fields
summary = state.model_dump(include={'id', 'status', 'results'})
```

## Error Handling

### Error Collection

```python
class RobustAgent(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        try:
            # Risky operation
            result = await self.process_data(state)
            state.result = result
        except ValidationError as e:
            state.add_error(
                agent_name=self.name,
                message="Data validation failed",
                details={"validation_errors": e.errors()}
            )
        except Exception as e:
            state.add_error(
                agent_name=self.name,
                message=f"Unexpected error: {str(e)}",
                details={"error_type": type(e).__name__}
            )
        
        return state
```

### Error Recovery

```python
class ErrorRecoveryWorkflow:
    async def execute_with_recovery(self, state: BaseState):
        # Execute primary workflow
        result = await self.primary_workflow.execute(state)
        
        # Check for errors and attempt recovery
        if result.has_errors():
            logger.warning(f"Primary workflow failed with {len(result.errors)} errors")
            
            # Clear non-critical errors
            critical_errors = [e for e in result.errors if e.get('critical', False)]
            result.errors = critical_errors
            
            # Attempt recovery workflow
            if not critical_errors:
                result = await self.recovery_workflow.execute(result)
        
        return result
```

## Performance Considerations

### Memory Management

```python
class EfficientState(BaseState):
    """State optimized for memory usage."""
    
    # Use slots for better memory efficiency
    __slots__ = ('_large_data',)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._large_data = None
    
    @property
    def large_data(self):
        """Lazy load large data only when needed."""
        if self._large_data is None:
            self._large_data = self._load_large_data()
        return self._large_data
    
    def _load_large_data(self):
        # Load large dataset on demand
        pass
```

### Efficient Updates

```python
# ✅ Efficient: Update specific fields
state.status = ProcessingStatus.COMPLETED
state.processed_records += batch_size

# ❌ Inefficient: Full state reconstruction
state = state.model_copy(update={
    'status': ProcessingStatus.COMPLETED,
    'processed_records': state.processed_records + batch_size
})
```

## Best Practices

### 1. State Design

```python
# ✅ Good: Clear, specific state fields
class DocumentState(BaseState):
    document_path: str
    document_type: str
    extracted_text: str
    word_count: int
    processing_time: float

# ❌ Bad: Generic, unclear fields
class GenericState(BaseState):
    data: Dict[str, Any]  # Too generic
    result: Any           # No type safety
```

### 2. Validation Strategy

```python
class WellValidatedState(BaseState):
    # Use appropriate field types
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=0, le=150)
    
    # Provide meaningful defaults
    processing_status: str = "pending"
    confidence_score: float = 0.0
    
    # Add helpful descriptions
    batch_size: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Number of records to process in each batch"
    )
```

### 3. Error Handling

```python
class ErrorAwareState(BaseState):
    def is_recoverable(self) -> bool:
        """Check if errors are recoverable."""
        return all(
            not error.get('critical', False) 
            for error in self.errors
        )
    
    def get_error_summary(self) -> str:
        """Get human-readable error summary."""
        if not self.errors:
            return "No errors"
        
        return f"{len(self.errors)} errors: " + "; ".join(
            f"{e['agent']}: {e['message']}" for e in self.errors[-3:]
        )
```

### 4. Documentation

```python
class DocumentedState(BaseState):
    """
    State for customer data processing workflow.
    
    This state manages customer information through various
    processing stages including validation, enrichment, and
    analysis.
    
    Attributes:
        customer_id: Unique identifier for the customer
        raw_data: Original customer data from source system
        validated_data: Data after validation and cleaning
        enriched_data: Data after external enrichment
        analysis_results: Results from analysis algorithms
        
    Usage:
        state = CustomerState(customer_id="CUST123")
        state.raw_data = load_customer_data()
        result = await workflow.execute(state)
    """
    
    customer_id: str = Field(..., description="Unique customer identifier")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Original data")
    # ... other fields with descriptions
```

## See Also

- [BaseAgent API](base-agent.md) - Agent base class
- [AgentConfig API](agent-config.md) - Agent configuration
- [Workflow API](../workflows/workflow.md) - Workflow orchestration  
- [State Management Tutorial](../../tutorials/state-management.md) - Detailed tutorial

# AgentConfig API Reference

The `AgentConfig` class provides configuration management for agents, enabling flexible customization of agent behavior, timeouts, retry policies, and execution parameters.

## Class Definition

```python
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum

class RetryPolicy(Enum):
    """Retry policy options."""
    NONE = "none"
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"

class LogLevel(Enum):
    """Logging level options."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class AgentConfig(BaseModel):
    """Configuration class for agent behavior and execution."""
    
    # Basic configuration
    name: str = Field(..., description="Agent name")
    description: str = Field(default="", description="Agent description")
    version: str = Field(default="1.0.0", description="Agent version")
    
    # Execution configuration
    timeout: float = Field(default=300.0, gt=0, description="Execution timeout in seconds")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    retry_policy: RetryPolicy = Field(default=RetryPolicy.EXPONENTIAL, description="Retry strategy")
    retry_delay: float = Field(default=1.0, gt=0, description="Initial retry delay in seconds")
    
    # Logging configuration
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_context: Dict[str, Any] = Field(default_factory=dict, description="Additional logging context")
    
    # Performance configuration
    max_memory_mb: Optional[int] = Field(default=None, gt=0, description="Memory limit in MB")
    max_cpu_percent: Optional[float] = Field(default=None, gt=0, le=100, description="CPU usage limit")
    
    # Custom configuration
    custom_config: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific configuration")
```

## Core Properties

### Basic Configuration

#### `name: str`

The unique name identifier for the agent.

**Required:** Yes  
**Usage:** Agent identification and logging

```python
config = AgentConfig(name="DataProcessorAgent")
print(config.name)  # "DataProcessorAgent"
```

#### `description: str`

Human-readable description of the agent's purpose.

**Default:** Empty string  
**Usage:** Documentation and monitoring

```python
config = AgentConfig(
    name="AnalysisAgent",
    description="Performs statistical analysis on customer data"
)
```

#### `version: str`

Version identifier for the agent.

**Default:** "1.0.0"  
**Usage:** Deployment tracking and compatibility

```python
config = AgentConfig(
    name="ProcessorAgent",
    version="2.1.0"
)
```

### Execution Configuration

#### `timeout: float`

Maximum execution time allowed for the agent in seconds.

**Default:** 300.0 (5 minutes)  
**Constraints:** Must be greater than 0  
**Usage:** Preventing runaway processes

```python
# Short timeout for quick operations
config = AgentConfig(
    name="ValidatorAgent",
    timeout=30.0  # 30 seconds
)

# Long timeout for complex processing
config = AgentConfig(
    name="MLModelAgent",
    timeout=3600.0  # 1 hour
)
```

#### `max_retries: int`

Maximum number of retry attempts on failure.

**Default:** 3  
**Constraints:** Must be >= 0  
**Usage:** Handling transient failures

```python
# No retries for critical operations
config = AgentConfig(
    name="PaymentAgent",
    max_retries=0
)

# Multiple retries for API calls
config = AgentConfig(
    name="APIAgent",
    max_retries=5
)
```

#### `retry_policy: RetryPolicy`

Strategy for spacing retry attempts.

**Default:** `RetryPolicy.EXPONENTIAL`  
**Options:**
- `NONE`: No retries
- `FIXED`: Fixed delay between retries
- `EXPONENTIAL`: Exponentially increasing delays
- `LINEAR`: Linearly increasing delays

```python
# Fixed 2-second delays
config = AgentConfig(
    name="DatabaseAgent",
    retry_policy=RetryPolicy.FIXED,
    retry_delay=2.0
)

# Exponential backoff (1s, 2s, 4s, 8s...)
config = AgentConfig(
    name="ExternalAPIAgent",
    retry_policy=RetryPolicy.EXPONENTIAL,
    retry_delay=1.0
)
```

#### `retry_delay: float`

Initial delay between retry attempts in seconds.

**Default:** 1.0  
**Constraints:** Must be greater than 0  
**Usage:** Base delay for retry calculations

### Logging Configuration

#### `log_level: LogLevel`

Minimum logging level for the agent.

**Default:** `LogLevel.INFO`  
**Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`

```python
# Debug logging for development
config = AgentConfig(
    name="DebugAgent",
    log_level=LogLevel.DEBUG
)

# Error-only logging for production
config = AgentConfig(
    name="ProductionAgent",
    log_level=LogLevel.ERROR
)
```

#### `log_context: Dict[str, Any]`

Additional context to include in log messages.

**Default:** Empty dictionary  
**Usage:** Structured logging metadata

```python
config = AgentConfig(
    name="CustomerAgent",
    log_context={
        "service": "customer-processing",
        "version": "2.1.0",
        "environment": "production"
    }
)
```

### Performance Configuration

#### `max_memory_mb: Optional[int]`

Maximum memory usage limit in megabytes.

**Default:** None (no limit)  
**Usage:** Resource constraint enforcement

```python
# Limit memory usage to 512MB
config = AgentConfig(
    name="MemoryEfficientAgent",
    max_memory_mb=512
)
```

#### `max_cpu_percent: Optional[float]`

Maximum CPU usage percentage (0-100).

**Default:** None (no limit)  
**Usage:** CPU resource management

```python
# Limit CPU usage to 50%
config = AgentConfig(
    name="BackgroundAgent",
    max_cpu_percent=50.0
)
```

### Custom Configuration

#### `custom_config: Dict[str, Any]`

Agent-specific configuration parameters.

**Default:** Empty dictionary  
**Usage:** Domain-specific settings

```python
config = AgentConfig(
    name="MLAgent",
    custom_config={
        "model_path": "/models/classifier.pkl",
        "batch_size": 1000,
        "confidence_threshold": 0.95,
        "feature_columns": ["age", "income", "score"]
    }
)
```

## Methods

### `get_retry_delay(attempt: int) -> float`

Calculate the delay before the specified retry attempt.

**Parameters:**
- `attempt` (int): The retry attempt number (1-based)

**Returns:**
- `float`: Delay in seconds before the retry

**Example:**
```python
config = AgentConfig(
    name="APIAgent",
    retry_policy=RetryPolicy.EXPONENTIAL,
    retry_delay=1.0
)

# Calculate delays for each attempt
for attempt in range(1, 4):
    delay = config.get_retry_delay(attempt)
    print(f"Attempt {attempt}: wait {delay}s")
# Output:
# Attempt 1: wait 1.0s
# Attempt 2: wait 2.0s  
# Attempt 3: wait 4.0s
```

### `should_retry(attempt: int, error: Exception) -> bool`

Determine if a retry should be attempted for the given error.

**Parameters:**
- `attempt` (int): Current attempt number
- `error` (Exception): The exception that occurred

**Returns:**
- `bool`: True if retry should be attempted

**Example:**
```python
import requests

config = AgentConfig(name="APIAgent", max_retries=3)

try:
    response = requests.get("https://api.example.com/data")
except requests.RequestException as e:
    if config.should_retry(1, e):
        print("Retrying request...")
```

### `get_custom_value(key: str, default: Any = None) -> Any`

Get a value from the custom configuration.

**Parameters:**
- `key` (str): Configuration key
- `default` (Any): Default value if key not found

**Returns:**
- `Any`: Configuration value or default

**Example:**
```python
config = AgentConfig(
    name="ProcessorAgent",
    custom_config={"batch_size": 500, "threshold": 0.8}
)

batch_size = config.get_custom_value("batch_size", 100)
threshold = config.get_custom_value("threshold", 0.5)
missing_value = config.get_custom_value("missing_key", "default")

print(f"Batch size: {batch_size}")  # 500
print(f"Threshold: {threshold}")    # 0.8
print(f"Missing: {missing_value}")  # "default"
```

### `set_custom_value(key: str, value: Any)`

Set a value in the custom configuration.

**Parameters:**
- `key` (str): Configuration key
- `value` (Any): Configuration value

**Example:**
```python
config = AgentConfig(name="DynamicAgent")
config.set_custom_value("batch_size", 1000)
config.set_custom_value("model_path", "/new/model/path")
```

### `merge_config(other: AgentConfig) -> AgentConfig`

Merge this configuration with another, returning a new config.

**Parameters:**
- `other` (AgentConfig): Configuration to merge

**Returns:**
- `AgentConfig`: New merged configuration

**Example:**
```python
base_config = AgentConfig(
    name="BaseAgent",
    timeout=300.0,
    max_retries=3
)

override_config = AgentConfig(
    name="SpecializedAgent",
    timeout=600.0,  # Override
    custom_config={"feature": "enabled"}
)

merged = base_config.merge_config(override_config)
print(merged.timeout)  # 600.0
print(merged.max_retries)  # 3 (inherited)
```

### `validate_config() -> List[str]`

Validate the configuration and return any issues found.

**Returns:**
- `List[str]`: List of validation error messages

**Example:**
```python
config = AgentConfig(
    name="TestAgent",
    timeout=-10.0,  # Invalid
    max_retries=-1  # Invalid
)

issues = config.validate_config()
for issue in issues:
    print(f"Config issue: {issue}")
```

## Configuration Patterns

### Production Configuration

```python
def create_production_config(agent_name: str) -> AgentConfig:
    """Create a production-ready agent configuration."""
    return AgentConfig(
        name=agent_name,
        timeout=300.0,
        max_retries=3,
        retry_policy=RetryPolicy.EXPONENTIAL,
        retry_delay=2.0,
        log_level=LogLevel.INFO,
        log_context={
            "environment": "production",
            "service": "agent-workflow"
        },
        max_memory_mb=1024,
        max_cpu_percent=80.0
    )
```

### Development Configuration

```python
def create_debug_config(agent_name: str) -> AgentConfig:
    """Create a development/debug agent configuration."""
    return AgentConfig(
        name=agent_name,
        timeout=60.0,  # Shorter timeout for quick feedback
        max_retries=1,  # Fewer retries for faster failure
        retry_policy=RetryPolicy.FIXED,
        log_level=LogLevel.DEBUG,  # Verbose logging
        log_context={
            "environment": "development",
            "debug": True
        }
    )
```

### Resource-Constrained Configuration

```python
def create_lightweight_config(agent_name: str) -> AgentConfig:
    """Create a resource-efficient configuration."""
    return AgentConfig(
        name=agent_name,
        timeout=30.0,
        max_retries=1,
        retry_policy=RetryPolicy.NONE,
        log_level=LogLevel.WARNING,  # Minimal logging
        max_memory_mb=256,  # Low memory limit
        max_cpu_percent=25.0  # Low CPU usage
    )
```

## Integration with Agents

### Basic Integration

```python
class ConfigurableAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(name=config.name)
        self.config = config
        
        # Setup logging based on config
        self.logger = get_logger(
            name=config.name,
            level=config.log_level.value,
            context=config.log_context
        )
    
    async def execute(self, state: BaseState) -> BaseState:
        self.logger.info(f"Starting execution with config: {self.config.name}")
        
        # Use timeout from config
        try:
            async with asyncio.timeout(self.config.timeout):
                result = await self._do_work(state)
                
        except asyncio.TimeoutError:
            self.logger.error(f"Agent timed out after {self.config.timeout}s")
            state.add_error(
                agent_name=self.config.name,
                message=f"Execution timeout ({self.config.timeout}s)"
            )
        
        return state
```

### Advanced Integration with Retries

```python
class RetryableAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(name=config.name)
        self.config = config
    
    async def execute(self, state: BaseState) -> BaseState:
        last_error = None
        
        for attempt in range(1, self.config.max_retries + 2):  # +1 for initial attempt
            try:
                result = await self._attempt_execution(state)
                self.logger.info(f"Execution succeeded on attempt {attempt}")
                return result
                
            except Exception as e:
                last_error = e
                
                if attempt <= self.config.max_retries and self.config.should_retry(attempt, e):
                    delay = self.config.get_retry_delay(attempt)
                    self.logger.warning(
                        f"Attempt {attempt} failed, retrying in {delay}s: {str(e)}"
                    )
                    await asyncio.sleep(delay)
                else:
                    break
        
        # All attempts failed
        state.add_error(
            agent_name=self.config.name,
            message=f"All {self.config.max_retries + 1} attempts failed",
            details={"last_error": str(last_error)}
        )
        return state
```

### Custom Configuration Usage

```python
class MLAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(name=config.name)
        self.config = config
        
        # Extract ML-specific configuration
        self.model_path = config.get_custom_value("model_path", "/default/model")
        self.batch_size = config.get_custom_value("batch_size", 100)
        self.threshold = config.get_custom_value("confidence_threshold", 0.5)
        
        # Load model based on config
        self.model = self._load_model(self.model_path)
    
    async def execute(self, state: BaseState) -> BaseState:
        # Use configuration in processing
        predictions = await self._predict(
            data=state.input_data,
            batch_size=self.batch_size,
            threshold=self.threshold
        )
        
        state.predictions = predictions
        return state
```

## Configuration Validation

### Schema Validation

```python
from pydantic import validator

class StrictAgentConfig(AgentConfig):
    """Agent config with additional validation rules."""
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Agent name cannot be empty')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Agent name must be alphanumeric with _ or -')
        return v
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v > 3600:  # 1 hour
            raise ValueError('Timeout cannot exceed 1 hour')
        return v
    
    @validator('custom_config')
    def validate_custom_config(cls, v):
        # Ensure certain required keys exist
        required_keys = ['model_path', 'batch_size']
        missing_keys = [key for key in required_keys if key not in v]
        if missing_keys:
            raise ValueError(f'Missing required config keys: {missing_keys}')
        return v
```

### Runtime Validation

```python
def validate_agent_config(config: AgentConfig, agent_type: str) -> List[str]:
    """Validate agent configuration for specific agent types."""
    issues = []
    
    # Type-specific validation
    if agent_type == "ml_agent":
        model_path = config.get_custom_value("model_path")
        if not model_path:
            issues.append("ML agents require 'model_path' in custom_config")
        elif not os.path.exists(model_path):
            issues.append(f"Model path does not exist: {model_path}")
    
    elif agent_type == "api_agent":
        base_url = config.get_custom_value("base_url")
        if not base_url:
            issues.append("API agents require 'base_url' in custom_config")
        
        if config.timeout < 10:
            issues.append("API agents should have timeout >= 10 seconds")
    
    # General validation
    if config.max_retries > 10:
        issues.append("Excessive retry count may cause delays")
    
    return issues
```

## Best Practices

### 1. Environment-Specific Configs

```python
class ConfigFactory:
    """Factory for creating environment-specific configurations."""
    
    @staticmethod
    def create_config(agent_name: str, environment: str) -> AgentConfig:
        base_config = {
            "name": agent_name,
            "version": "1.0.0"
        }
        
        if environment == "development":
            return AgentConfig(
                **base_config,
                timeout=60.0,
                max_retries=1,
                log_level=LogLevel.DEBUG
            )
        elif environment == "staging":
            return AgentConfig(
                **base_config,
                timeout=180.0,
                max_retries=2,
                log_level=LogLevel.INFO
            )
        elif environment == "production":
            return AgentConfig(
                **base_config,
                timeout=300.0,
                max_retries=3,
                log_level=LogLevel.WARNING,
                max_memory_mb=1024
            )
        else:
            raise ValueError(f"Unknown environment: {environment}")
```

### 2. Configuration Inheritance

```python
class BaseAgentConfig(AgentConfig):
    """Base configuration with sensible defaults."""
    
    def __init__(self, **data):
        defaults = {
            "timeout": 300.0,
            "max_retries": 3,
            "retry_policy": RetryPolicy.EXPONENTIAL,
            "log_level": LogLevel.INFO
        }
        defaults.update(data)
        super().__init__(**defaults)

class APIAgentConfig(BaseAgentConfig):
    """Configuration specialized for API agents."""
    
    def __init__(self, **data):
        api_defaults = {
            "timeout": 30.0,  # Shorter timeout for API calls
            "max_retries": 5,  # More retries for network issues
            "retry_delay": 2.0
        }
        api_defaults.update(data)
        super().__init__(**api_defaults)
```

### 3. Configuration Documentation

```python
class DocumentedConfig(AgentConfig):
    """
    Configuration for data processing agents.
    
    This configuration is optimized for agents that process
    large datasets and may require significant computational
    resources.
    
    Custom Configuration Keys:
        batch_size (int): Number of records to process per batch
        memory_limit (str): Memory limit (e.g., "2GB", "512MB")
        parallel_workers (int): Number of parallel processing workers
        checkpoint_interval (int): Save progress every N batches
    
    Example:
        config = DocumentedConfig(
            name="DataProcessor",
            custom_config={
                "batch_size": 1000,
                "memory_limit": "1GB",
                "parallel_workers": 4,
                "checkpoint_interval": 100
            }
        )
    """
    pass
```

## See Also

- [BaseAgent API](base-agent.md) - Agent base class
- [BaseState API](base-state.md) - State management
- [Workflow API](../workflows/workflow.md) - Workflow orchestration
- [Configuration Tutorial](../../tutorials/configuration.md) - Detailed configuration guide

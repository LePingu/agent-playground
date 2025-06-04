# Custom Agents Tutorial

Learn how to create powerful custom agents that form the building blocks of your workflows. This tutorial covers everything from basic agent structure to advanced patterns.

## What Are Agents?

Agents are the fundamental units of computation in Agent Playground. Each agent:

- Performs a specific task or transformation
- Receives state as input and returns modified state
- Can be combined into workflows
- Is stateless and reusable

## Basic Agent Structure

### Minimal Agent

```python
from agent_playground.core import BaseAgent, BaseState

class GreetingAgent(BaseAgent):
    """A simple agent that adds a greeting message."""
    
    def __init__(self, name: str = "GreetingAgent"):
        super().__init__(name)
    
    async def execute(self, state: BaseState) -> BaseState:
        # Add greeting to state
        if not hasattr(state, 'messages'):
            state.messages = []
        
        state.messages.append(f"Hello from {self.name}!")
        return state
```

### Agent with Configuration

```python
from agent_playground.core import BaseAgent, BaseState, AgentConfig
from typing import Dict, Any

class ConfigurableAgent(BaseAgent):
    """Agent that uses configuration parameters."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config.get('name', 'ConfigurableAgent'))
        self.greeting = config.get('greeting', 'Hello')
        self.language = config.get('language', 'en')
        self.max_messages = config.get('max_messages', 10)
    
    async def execute(self, state: BaseState) -> BaseState:
        if not hasattr(state, 'messages'):
            state.messages = []
        
        # Respect max_messages limit
        if len(state.messages) < self.max_messages:
            message = f"{self.greeting} in {self.language}!"
            state.messages.append(message)
        
        return state

# Usage
config = {
    'name': 'FrenchGreeter',
    'greeting': 'Bonjour',
    'language': 'French',
    'max_messages': 5
}
agent = ConfigurableAgent(config)
```

## State Interaction Patterns

### Reading from State

```python
class DataValidator(BaseAgent):
    """Validates data from state."""
    
    async def execute(self, state: BaseState) -> BaseState:
        # Read data from state
        data = getattr(state, 'input_data', None)
        
        if data is None:
            state.validation_error = "No input data found"
            state.is_valid = False
            return state
        
        # Perform validation
        is_valid = self._validate_data(data)
        state.is_valid = is_valid
        
        if not is_valid:
            state.validation_error = "Data validation failed"
        
        return state
    
    def _validate_data(self, data) -> bool:
        # Your validation logic here
        return isinstance(data, dict) and 'required_field' in data
```

### Modifying State

```python
class DataProcessor(BaseAgent):
    """Processes and transforms data."""
    
    async def execute(self, state: BaseState) -> BaseState:
        # Check if data is valid first
        if not getattr(state, 'is_valid', False):
            state.processing_error = "Cannot process invalid data"
            return state
        
        # Get input data
        input_data = state.input_data
        
        # Process data
        processed_data = self._process_data(input_data)
        
        # Store results in state
        state.processed_data = processed_data
        state.processing_complete = True
        state.processing_timestamp = self._get_timestamp()
        
        return state
    
    def _process_data(self, data: Dict) -> Dict:
        # Your processing logic here
        return {k: v.upper() if isinstance(v, str) else v 
                for k, v in data.items()}
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
```

### Conditional Logic

```python
class ConditionalProcessor(BaseAgent):
    """Agent with conditional logic based on state."""
    
    async def execute(self, state: BaseState) -> BaseState:
        data_type = getattr(state, 'data_type', 'unknown')
        
        if data_type == 'text':
            state.result = await self._process_text(state)
        elif data_type == 'image':
            state.result = await self._process_image(state)
        elif data_type == 'audio':
            state.result = await self._process_audio(state)
        else:
            state.error = f"Unsupported data type: {data_type}"
        
        return state
    
    async def _process_text(self, state: BaseState) -> str:
        # Text processing logic
        return f"Processed text: {getattr(state, 'input_data', '')}"
    
    async def _process_image(self, state: BaseState) -> str:
        # Image processing logic
        return "Processed image data"
    
    async def _process_audio(self, state: BaseState) -> str:
        # Audio processing logic
        return "Processed audio data"
```

## Advanced Agent Patterns

### Agent with External API

```python
import httpx
from typing import Optional

class APIAgent(BaseAgent):
    """Agent that interacts with external APIs."""
    
    def __init__(self, api_url: str, api_key: Optional[str] = None):
        super().__init__("APIAgent")
        self.api_url = api_url
        self.api_key = api_key
        self.client = httpx.AsyncClient()
    
    async def execute(self, state: BaseState) -> BaseState:
        try:
            # Prepare request
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Get data to send
            request_data = getattr(state, 'api_request_data', {})
            
            # Make API call
            response = await self.client.post(
                self.api_url,
                json=request_data,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            # Store response
            state.api_response = response.json()
            state.api_success = True
            
        except httpx.HTTPError as e:
            state.api_error = str(e)
            state.api_success = False
        
        return state
    
    async def cleanup(self):
        """Cleanup resources."""
        await self.client.aclose()
```

### Agent with Retry Logic

```python
import asyncio
from typing import Optional

class RetryableAgent(BaseAgent):
    """Agent with built-in retry logic."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__("RetryableAgent")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def execute(self, state: BaseState) -> BaseState:
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Attempt the operation
                return await self._do_work(state)
                
            except Exception as e:
                last_error = e
                
                if attempt < self.max_retries:
                    # Log retry attempt
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {self.retry_delay}s...")
                    await asyncio.sleep(self.retry_delay)
                    # Exponential backoff
                    self.retry_delay *= 2
                else:
                    # All retries exhausted
                    state.error = f"All {self.max_retries + 1} attempts failed. Last error: {e}"
                    break
        
        return state
    
    async def _do_work(self, state: BaseState) -> BaseState:
        # Your actual work logic here
        # This is where you'd put code that might fail
        
        # Simulate potential failure
        import random
        if random.random() < 0.3:  # 30% chance of failure
            raise Exception("Simulated failure")
        
        state.work_completed = True
        return state
```

### Agent with Logging

```python
import logging
from agent_playground.utils.logging import get_logger

class LoggingAgent(BaseAgent):
    """Agent with comprehensive logging."""
    
    def __init__(self, name: str = "LoggingAgent"):
        super().__init__(name)
        self.logger = get_logger(f"agents.{name}")
    
    async def execute(self, state: BaseState) -> BaseState:
        self.logger.info(f"Starting execution for {self.name}")
        
        try:
            # Log input state
            self.logger.debug(f"Input state: {state.__dict__}")
            
            # Perform work
            result = await self._do_work(state)
            
            # Log success
            self.logger.info(f"Successfully completed {self.name}")
            self.logger.debug(f"Output state: {result.__dict__}")
            
            return result
            
        except Exception as e:
            # Log error
            self.logger.error(f"Error in {self.name}: {e}", exc_info=True)
            
            # Store error in state
            state.error = str(e)
            state.failed = True
            
            return state
    
    async def _do_work(self, state: BaseState) -> BaseState:
        # Your work logic here
        self.logger.debug("Performing work...")
        
        # Simulate work
        await asyncio.sleep(0.1)
        
        state.work_result = "Work completed successfully"
        return state
```

### Agent with Validation

```python
from pydantic import BaseModel, validator
from typing import List, Dict, Any

class ValidationAgent(BaseAgent):
    """Agent that validates inputs and outputs."""
    
    class InputModel(BaseModel):
        data: Dict[str, Any]
        data_type: str
        
        @validator('data_type')
        def validate_data_type(cls, v):
            allowed_types = ['text', 'image', 'audio', 'video']
            if v not in allowed_types:
                raise ValueError(f'data_type must be one of {allowed_types}')
            return v
    
    class OutputModel(BaseModel):
        processed_data: Dict[str, Any]
        processing_time: float
        success: bool
    
    async def execute(self, state: BaseState) -> BaseState:
        try:
            # Validate input
            input_data = self.InputModel(
                data=getattr(state, 'input_data', {}),
                data_type=getattr(state, 'data_type', 'text')
            )
            
            # Process data
            start_time = time.time()
            processed_data = await self._process(input_data.data)
            processing_time = time.time() - start_time
            
            # Validate output
            output_data = self.OutputModel(
                processed_data=processed_data,
                processing_time=processing_time,
                success=True
            )
            
            # Update state
            state.processed_data = output_data.processed_data
            state.processing_time = output_data.processing_time
            state.success = output_data.success
            
        except ValueError as e:
            state.validation_error = str(e)
            state.success = False
        
        return state
    
    async def _process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Your processing logic
        return {"processed": True, "original": data}
```

## Specialized Agent Types

### LLM Agent

```python
from openai import AsyncOpenAI

class LLMAgent(BaseAgent):
    """Agent that uses Language Models."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str = None):
        super().__init__("LLMAgent")
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def execute(self, state: BaseState) -> BaseState:
        try:
            # Get prompt from state
            prompt = getattr(state, 'prompt', '')
            system_message = getattr(state, 'system_message', 'You are a helpful assistant.')
            
            # Make LLM request
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Store response
            state.llm_response = response.choices[0].message.content
            state.llm_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
        except Exception as e:
            state.llm_error = str(e)
        
        return state
```

### Database Agent

```python
import asyncpg
from typing import List, Dict

class DatabaseAgent(BaseAgent):
    """Agent that interacts with databases."""
    
    def __init__(self, connection_url: str):
        super().__init__("DatabaseAgent")
        self.connection_url = connection_url
        self.pool = None
    
    async def initialize(self):
        """Initialize database connection pool."""
        self.pool = await asyncpg.create_pool(self.connection_url)
    
    async def execute(self, state: BaseState) -> BaseState:
        if not self.pool:
            await self.initialize()
        
        try:
            query = getattr(state, 'sql_query', '')
            params = getattr(state, 'sql_params', [])
            
            async with self.pool.acquire() as connection:
                if query.strip().upper().startswith('SELECT'):
                    # Query operation
                    rows = await connection.fetch(query, *params)
                    state.query_results = [dict(row) for row in rows]
                else:
                    # Modification operation
                    result = await connection.execute(query, *params)
                    state.execution_result = result
            
            state.database_success = True
            
        except Exception as e:
            state.database_error = str(e)
            state.database_success = False
        
        return state
    
    async def cleanup(self):
        """Cleanup database connections."""
        if self.pool:
            await self.pool.close()
```

### File Processing Agent

```python
import aiofiles
import json
import csv
from pathlib import Path

class FileProcessingAgent(BaseAgent):
    """Agent for file operations."""
    
    def __init__(self, base_path: str = "."):
        super().__init__("FileProcessingAgent")
        self.base_path = Path(base_path)
    
    async def execute(self, state: BaseState) -> BaseState:
        operation = getattr(state, 'file_operation', 'read')
        file_path = getattr(state, 'file_path', '')
        
        try:
            if operation == 'read':
                await self._read_file(state, file_path)
            elif operation == 'write':
                await self._write_file(state, file_path)
            elif operation == 'process_csv':
                await self._process_csv(state, file_path)
            elif operation == 'process_json':
                await self._process_json(state, file_path)
            
            state.file_success = True
            
        except Exception as e:
            state.file_error = str(e)
            state.file_success = False
        
        return state
    
    async def _read_file(self, state: BaseState, file_path: str):
        full_path = self.base_path / file_path
        async with aiofiles.open(full_path, 'r') as f:
            state.file_content = await f.read()
    
    async def _write_file(self, state: BaseState, file_path: str):
        full_path = self.base_path / file_path
        content = getattr(state, 'file_content', '')
        async with aiofiles.open(full_path, 'w') as f:
            await f.write(content)
    
    async def _process_csv(self, state: BaseState, file_path: str):
        full_path = self.base_path / file_path
        with open(full_path, 'r') as f:
            reader = csv.DictReader(f)
            state.csv_data = list(reader)
    
    async def _process_json(self, state: BaseState, file_path: str):
        full_path = self.base_path / file_path
        async with aiofiles.open(full_path, 'r') as f:
            content = await f.read()
            state.json_data = json.loads(content)
```

## Testing Agents

### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock, patch
from agent_playground.core import BaseState

@pytest.mark.asyncio
async def test_greeting_agent():
    """Test the greeting agent."""
    # Arrange
    agent = GreetingAgent("TestGreeter")
    state = BaseState()
    
    # Act
    result = await agent.execute(state)
    
    # Assert
    assert hasattr(result, 'messages')
    assert len(result.messages) == 1
    assert "Hello from TestGreeter!" in result.messages

@pytest.mark.asyncio
async def test_api_agent_success():
    """Test API agent with successful response."""
    # Mock httpx
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock
        mock_response = AsyncMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.post.return_value = mock_response
        
        # Arrange
        agent = APIAgent("https://api.example.com", "test-key")
        state = BaseState()
        state.api_request_data = {"test": "data"}
        
        # Act
        result = await agent.execute(state)
        
        # Assert
        assert result.api_success is True
        assert result.api_response == {"result": "success"}

@pytest.mark.asyncio
async def test_retryable_agent_failure():
    """Test retryable agent with all retries failing."""
    # Arrange
    agent = RetryableAgent(max_retries=2, retry_delay=0.1)
    state = BaseState()
    
    # Mock the _do_work method to always fail
    async def mock_do_work(self, state):
        raise Exception("Always fails")
    
    agent._do_work = lambda state: mock_do_work(agent, state)
    
    # Act
    result = await agent.execute(state)
    
    # Assert
    assert hasattr(result, 'error')
    assert "All 3 attempts failed" in result.error
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_agent_workflow_integration():
    """Test agents working together in a workflow."""
    from agent_playground.workflows import workflow_templates
    
    # Create agents
    validator = DataValidator()
    processor = DataProcessor()
    
    # Create workflow
    workflow = workflow_templates.create_workflow(
        template_name="sequential",
        agents=[validator, processor],
        state_class=BaseState
    )
    
    # Create test state
    initial_state = BaseState()
    initial_state.input_data = {"required_field": "test_value"}
    
    # Execute workflow
    result = await workflow.execute(initial_state)
    
    # Assert workflow completed successfully
    assert result.is_valid is True
    assert result.processing_complete is True
    assert hasattr(result, 'processed_data')
```

## Best Practices

### 1. Single Responsibility

Each agent should have one clear responsibility:

```python
# ✅ Good - Single responsibility
class TextExtractor(BaseAgent):
    """Extracts text from documents."""
    pass

class TextAnalyzer(BaseAgent):
    """Analyzes extracted text."""
    pass

# ❌ Bad - Multiple responsibilities
class TextExtractorAndAnalyzer(BaseAgent):
    """Extracts and analyzes text."""
    pass
```

### 2. State Immutability

Avoid modifying existing state fields, add new ones:

```python
# ✅ Good - Add new fields
async def execute(self, state: BaseState) -> BaseState:
    state.processed_text = self.process(state.raw_text)
    return state

# ❌ Bad - Modify existing fields
async def execute(self, state: BaseState) -> BaseState:
    state.raw_text = self.process(state.raw_text)  # Loses original data
    return state
```

### 3. Error Handling

Always handle errors gracefully:

```python
async def execute(self, state: BaseState) -> BaseState:
    try:
        # Agent logic
        result = await self.do_work()
        state.result = result
        state.success = True
    except Exception as e:
        state.error = str(e)
        state.success = False
    
    return state
```

### 4. Resource Cleanup

Clean up resources properly:

```python
class ResourceAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.client = None
    
    async def execute(self, state: BaseState) -> BaseState:
        try:
            self.client = SomeClient()
            # Use client
            return state
        finally:
            if self.client:
                await self.client.close()
```

### 5. Documentation

Document your agents clearly:

```python
class DocumentedAgent(BaseAgent):
    """
    Processes documents and extracts metadata.
    
    This agent takes document data from state.document_data and:
    1. Extracts text content
    2. Identifies document type
    3. Extracts metadata (author, creation date, etc.)
    
    State Requirements:
        - document_data: bytes or str
        - document_type: Optional[str]
    
    State Outputs:
        - extracted_text: str
        - document_metadata: Dict[str, Any]
        - processing_success: bool
    
    Raises:
        - DocumentProcessingError: If document cannot be processed
    """
    
    async def execute(self, state: BaseState) -> BaseState:
        # Implementation
        pass
```

---

**Next Steps:**
- Learn about [Workflow Building](workflow-building.md)
- Explore [State Management](state-management.md)
- Check out [Integration Patterns](integrations.md)

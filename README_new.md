# Agent Playground 🚀

A modular, reusable AI Agent framework built with LangGraph and LangChain, featuring specialized Source of Wealth verification workflows.

## ✨ Features

- **🏗️ Modular Architecture**: Clean separation between agents, workflows, and utilities
- **🔧 Type-Safe**: Full Pydantic integration with comprehensive type hints
- **📊 Workflow Builder**: Fluent interface for creating complex agent workflows
- **🎯 Agent Registry**: Dynamic agent discovery and factory pattern
- **📝 Rich Logging**: Structured logging with loguru integration
- **⚙️ Configuration Management**: Environment-based configuration with validation
- **🧪 Testing Framework**: Comprehensive test coverage with pytest
- **📋 Source of Wealth**: Specialized agents for financial verification workflows

## 🚀 Quick Start

### Installation

```bash
# Install in development mode
pip install -e ".[dev]"

# Or install from requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Configuration

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration with your API keys
vim .env
```

### Basic Usage

```python
from agent_playground import BaseAgent, AgentConfig, WorkflowBuilder

# Create a simple agent
config = AgentConfig(
    name="hello_agent",
    description="A simple greeting agent"
)

# Build a workflow
workflow = (WorkflowBuilder(name="greeting_workflow")
    .add_step("greet", lambda state: {"message": f"Hello {state.get('name', 'World')}!"})
    .add_step("respond", lambda state: {"response": f"Response: {state['message']}"})
    .chain("greet", "respond")
    .start_with("greet")
    .chain_to_end("respond")
    .build())

# Run the workflow
result = await workflow.ainvoke({"name": "Agent Playground"})
print(result["response"])  # Response: Hello Agent Playground!
```

### CLI Usage

```bash
# Show environment info
agent-playground info --verbose

# List registered agents
agent-playground list-agents

# Initialize a new project
agent-playground init-project my-agent-project

# Source of Wealth verification
sow-agent verify CLIENT_123 "John Doe" --id documents/id.pdf --payslip documents/payslip.pdf
```

## 🏗️ Architecture

```
src/agent_playground/
├── core/                 # Core framework components
│   ├── base.py          # Base agent classes
│   └── registry.py      # Agent registry
├── workflows/           # Workflow building tools
│   └── builder.py       # Workflow builder
├── utils/               # Utilities
│   ├── config.py        # Configuration management
│   └── logging.py       # Logging utilities
├── sow/                 # Source of Wealth specific components
│   ├── agents/          # SOW specialized agents
│   ├── workflows/       # SOW workflows
│   └── cli.py           # SOW CLI
└── cli.py               # Main CLI interface
```

## 🔧 Development

### Setup Development Environment

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Run linting and formatting
make check

# View all available commands
make help
```

### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# With coverage
make test-cov
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Run all quality checks
make check
```

## 📊 Creating Custom Agents

### Simple Agent

```python
from agent_playground.core import BaseAgent, AgentConfig, AgentState
from langgraph.graph import StateGraph, END

class CustomAgent(BaseAgent[AgentState]):
    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        
        # Add your processing nodes
        graph.add_node("process", self._process_step)
        graph.add_node("finalize", self._finalize_step)
        
        # Define workflow
        graph.add_edge("process", "finalize")
        graph.add_edge("finalize", END)
        graph.set_entry_point("process")
        
        return graph
    
    async def _process_step(self, state):
        # Your processing logic here
        return state
    
    async def _finalize_step(self, state):
        return {**state, "completed": True}

# Register and use
config = AgentConfig(name="custom_agent")
agent = CustomAgent(config)
result = await agent.run({"input": "data"})
```

### Complex Workflow

```python
from agent_playground.workflows import WorkflowBuilder

# Create a conditional workflow
workflow = (WorkflowBuilder(name="complex_workflow")
    .add_step("input_validation", validate_input)
    .add_step("process_a", process_option_a)
    .add_step("process_b", process_option_b)
    .add_step("merge_results", merge_results)
    
    # Conditional branching
    .chain("input_validation", "decision")
    .branch("decision", decide_path, {
        "path_a": "process_a",
        "path_b": "process_b"
    })
    .chain("process_a", "merge_results")
    .chain("process_b", "merge_results")
    
    .start_with("input_validation")
    .chain_to_end("merge_results")
    .build())
```

## 🎯 Source of Wealth Verification

The framework includes specialized agents for financial verification:

```python
from agent_playground.sow.workflows import create_sow_workflow

# Create SOW verification workflow
workflow = create_sow_workflow()

# Run verification
result = await workflow.ainvoke({
    "client_id": "12345",
    "client_name": "John Doe",
    "documents": {
        "id_document": "path/to/id.pdf",
        "payslip": "path/to/payslip.pdf"
    }
})

print(f"Risk Level: {result['risk_assessment']['risk_level']}")
```

## 📋 Configuration

The framework uses environment variables for configuration:

```bash
# Model Configuration
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=openai/gpt-4-turbo

# Agent Behavior
MAX_ITERATIONS=10
TIMEOUT=300
ENABLE_HUMAN_IN_LOOP=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=detailed
LOG_FILE=logs/agent-playground.log

# Tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_key
LANGSMITH_PROJECT=my-project
```

## 🧪 Testing

The framework includes comprehensive testing:

- **Unit Tests**: Core component testing
- **Integration Tests**: Agent workflow testing  
- **E2E Tests**: Complete system testing

```python
# Example test
@pytest.mark.asyncio
async def test_custom_agent(test_agent_config):
    agent = CustomAgent(test_agent_config)
    result = await agent.run({"test": "data"})
    assert result.completed
```

## 📚 Documentation

- [Implementation Plan](implementation_plan.md)
- [Running Instructions](RUNNING.md)
- [Human-in-the-Loop](HUMAN_IN_THE_LOOP.md)
- [Workflow Diagrams](workflow_diagram.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Run quality checks: `make check`
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Related Projects

- [LangGraph](https://github.com/langchain-ai/langgraph) - State-based agent framework
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation library

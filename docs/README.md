# Agent Playground Documentation

Welcome to the Agent Playground documentation! This is a comprehensive multi-agent framework for building, executing, and monitoring complex workflows.

## Documentation Structure

- [**Quick Start Guide**](quickstart.md) - Get up and running in minutes
- [**Framework Overview**](framework-overview.md) - Understanding the architecture and concepts
- [**API Reference**](api/) - Complete API documentation
- [**Tutorials**](tutorials/) - Step-by-step guides and examples
- [**Workflow Templates**](workflow-templates.md) - Built-in workflow patterns
- [**Examples**](examples/) - Real-world workflow examples
- [**Best Practices**](best-practices.md) - Guidelines for effective workflow design
- [**Integration Guide**](integration.md) - Integrating with external systems
- [**Performance Guide**](performance.md) - Optimization tips and benchmarking
- [**CLI Reference**](cli-reference.md) - Command-line interface documentation

## What is Agent Playground?

Agent Playground is a modern, type-safe framework for building multi-agent workflows that can:

- **Execute Complex Workflows**: Orchestrate multiple AI agents in sophisticated patterns
- **Monitor Performance**: Track execution metrics and visualize agent interactions
- **Scale Efficiently**: Handle concurrent workflows with built-in monitoring
- **Integrate Seamlessly**: Work with popular AI frameworks like LangChain and LangGraph
- **Visualize Results**: Generate beautiful reports and interactive visualizations

## Key Features

### 🎯 **Workflow Templates**
Pre-built patterns for common workflow types:
- Sequential workflows
- Parallel processing with aggregation  
- Conditional branching
- Human-in-the-loop workflows
- Data validation pipelines
- Analysis workflows
- Transformation workflows

### 📊 **Rich Visualization**
- Interactive workflow graphs
- Execution timeline charts
- Performance metrics dashboards
- HTML report generation
- Real-time monitoring

### 🔧 **Developer Experience**
- Type-safe agent definitions
- Modern Python packaging
- Comprehensive CLI tools
- Rich console output
- Async/await support

### 📈 **Production Ready**
- Error handling and recovery
- Workflow persistence
- Metrics collection
- Audit trail logging
- Scalable execution

## Quick Example

```python
from agent_playground.workflows import workflow_templates
from agent_playground.core import BaseAgent, BaseState

# Define your agents
class AnalysisAgent(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        # Your agent logic here
        return state

# Create a workflow from template
workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents=[AnalysisAgent()],
    state_class=BaseState
)

# Execute the workflow
result = await workflow.execute(initial_state)
```

## Getting Help

- 📖 **Documentation**: Browse the guides and API reference
- 💡 **Examples**: Check out the [examples directory](examples/)
- 🐛 **Issues**: Report bugs or request features on GitHub
- 💬 **Discussions**: Join the community discussions

## Version Information

This documentation covers Agent Playground v1.0.0+, which includes:
- Modern workflow template system
- Enhanced visualization capabilities
- Comprehensive CLI tools
- Production-ready monitoring
- Type-safe framework design

---

*Ready to get started? Check out the [Quick Start Guide](quickstart.md)!*

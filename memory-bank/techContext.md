# Technical Context: Source of Wealth Multi-Agent System

## Technologies Used

### Core Frameworks
- **LangChain**: Framework for building applications with language models
  - Version: langchain-core==0.3.59
  - Used for: Agent creation, prompt management, and model interaction
- **LangGraph**: Framework for building stateful, multi-agent workflows
  - Version: langgraph>=0.1.0
  - Used for: Workflow orchestration, agent coordination, and state management

### Language Models
- **OpenRouter**
  - Models: qwen3-110b, deepseek (free models)
  - Used for: External data analysis, web reference checking, financial report analysis
  - Integration: langchain-openai>=0.0.1
- **Ollama**
  - Models: mistral-small3.1
  - Used for: Processing sensitive information (ID verification, payslip analysis)
  - Integration: langchain-ollama>=0.3.2
  - Deployment: Local server at [ip]:11434

### Development Environment
- **Jupyter**: Interactive notebook environment
  - Version: jupyter>=1.0.0
  - Used for: Interactive execution and visualization
- **Python**: Programming language
  - Version: 3.8+ (compatible with all dependencies)
  - Used for: All implementation code

### Visualization
- **Matplotlib**: Data visualization library
  - Version: matplotlib>=3.10.3
  - Used for: Creating charts and visualizations of results
- **NetworkX**: Network analysis library
  - Version: networkx>=3.0
  - Used for: Creating agent interaction graphs

### Utilities
- **Pydantic**: Data validation library
  - Version: pydantic>=2.0.0
  - Used for: Type validation and state management
- **HTTPX**: HTTP client
  - Version: httpx>=0.24.0
  - Used for: API requests
- **Python-dotenv**: Environment variable management
  - Version: python-dotenv>=1.0.0
  - Used for: Managing API keys and configuration

## Development Setup

### Environment Setup
1. **Python Environment**:
   - Python 3.8 or higher
   - Virtual environment recommended

2. **Dependencies Installation**:
   ```bash
   pip install -r requirements.txt
   ```

3. **API Keys**:
   - OpenRouter API key for external model access
   - Environment variables configured in .env file

4. **Ollama Setup**:
   - Local Ollama instance running on [ip]:11434
   - Mistral model installed and available

### Project Structure
```
source_of_wealth_agent/
├── agents/                 # Agent implementations
│   ├── id_verification_agent.py
│   ├── payslip_verification_agent.py
│   ├── web_references_agent.py
│   ├── financial_reports_agent.py
│   ├── corroboration_agents.py
│   ├── human_advisory_agent.py
│   ├── risk_assessment_agent.py
│   └── report_generation_agent.py
├── core/                   # Core functionality
│   ├── state.py            # State management
│   └── models.py           # Model initialization
├── notebooks/              # Jupyter notebooks
│   ├── source_of_wealth_checker.py
│   └── source_of_wealth_checker_refactored.py
├── workflow/               # Workflow orchestration
│   ├── orchestration.py    # Workflow definition
│   ├── tracing.py          # Tracing functionality
│   ├── runner.py           # Workflow execution
│   └── visualization.py    # Visualization tools
└── requirements.txt        # Project dependencies
```

## Technical Constraints

### 1. Model Access and Availability
- **Constraint**: Sensitive information must be processed using local models
- **Impact**: Requires Ollama setup with appropriate models
- **Mitigation**: Clear separation between sensitive and non-sensitive data processing

### 2. Performance Considerations
- **Constraint**: Language model inference can be slow, especially for local models
- **Impact**: Workflow execution may take time, especially with multiple agents
- **Mitigation**: Asynchronous processing where possible, progress indicators

### 3. API Rate Limits
- **Constraint**: OpenRouter has rate limits for API calls
- **Impact**: May limit throughput for processing multiple clients simultaneously
- **Mitigation**: Implement rate limiting and queuing for high-volume scenarios

### 4. Data Privacy
- **Constraint**: Client financial data is highly sensitive
- **Impact**: Requires careful handling of data and model selection
- **Mitigation**: Use of local models for sensitive data, data minimization principles

### 5. Interactive Requirements
- **Constraint**: System must support human interaction for approvals
- **Impact**: Workflow cannot be fully automated
- **Mitigation**: Clear user interface for human input points, timeout handling

### 6. Asynchronous Execution
- **Constraint**: Workflow must support asynchronous execution for better performance
- **Impact**: Requires async-compatible code throughout the system
- **Mitigation**: Use of async/await pattern, proper error handling for async operations

## Dependencies

### Direct Dependencies
```
langchain-core==0.3.59
langgraph>=0.1.0
langchain-openai>=0.0.1
langchain-community>=0.0.1
pydantic>=2.0.0
jupyter>=1.0.0
httpx>=0.24.0
python-dotenv>=1.0.0
langchain-ollama>=0.3.2
matplotlib>=3.10.3
networkx>=3.0
```

### Indirect Dependencies
- OpenAI API (via OpenRouter)
- Ollama API
- Various Python standard libraries

## Tool Usage Patterns

### 1. Asynchronous Agent Implementation Pattern
```python
async def agent_name(state: AgentState) -> AgentState:
    # Process the state asynchronously
    # ...
    
    # Create minimal state update
    state_update = {"result_key": result}
    
    # Log the action and return the state update
    return log_action(state_update, "Agent_Name", "Action description", result)
```

### 2. Dynamic Workflow Definition Pattern
```python
# Create workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("risk_assessment_node", risk_assessment_agent)
workflow.add_node("id_verification_node", id_agent.run)
# ...add other nodes...

# Define workflow entry point - start with risk assessment for planning
workflow.add_edge("__start__", "risk_assessment_node")

# Add dynamic routing with conditional edges
workflow.add_conditional_edges(
    "risk_assessment_node",
    route_after_risk_assessment,
    {
        "id_verification_node": "id_verification_node",
        "payslip_verification_node": "payslip_verification_node",
        "web_references_node": "web_references_node",
        "summarization_node": "summarization_node",
        "human_advisory_node": "human_advisory_node"
    }
)

# After each verification, check for issues and route to human review if needed
workflow.add_conditional_edges(
    "id_verification_node",
    verification_needs_human_review,
    {
        "human_advisory_node": "human_advisory_node",
        "risk_assessment_node": "risk_assessment_node"
    }
)

# Compile workflow
graph = workflow.compile()
```

### 3. Asynchronous Workflow Execution Pattern
```python
# Initialize state
initial_state = create_initial_state(client_id, client_name)

# Execute workflow asynchronously
result = await graph.ainvoke(initial_state)
```

### 4. Enhanced Visualization Pattern
```python
# Start tracing with context
tracer.start_tracing()

# Execute workflow with tracing
try:
    result = await graph.ainvoke(initial_state)
    
    # Generate visualizations
    tracer.visualize_interactions()
    tracer.display_execution_statistics()
    
    # Optional: save visualization to file
    tracer.save_visualization("workflow_execution.html")
finally:
    # Always stop tracing
    tracer.stop_tracing()

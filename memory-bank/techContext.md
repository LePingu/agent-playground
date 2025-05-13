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

### 1. Agent Implementation Pattern
```python
def agent_name(state: AgentState) -> AgentState:
    # Process the state
    # ...
    
    # Update the state with results
    new_state = state.copy()
    new_state["result_key"] = result
    
    # Log the action
    return log_action(new_state, "Agent_Name", "Action description", result)
```

### 2. Workflow Definition Pattern
```python
# Create workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("node_name", agent_function)

# Add edges
workflow.add_edge("source_node", "target_node")

# Add conditional edges
workflow.add_conditional_edges(
    "source_node",
    routing_function,
    {
        "condition1": "target_node1",
        "condition2": "target_node2"
    }
)

# Compile workflow
graph = workflow.compile()
```

### 3. Workflow Execution Pattern
```python
# Initialize state
initial_state = create_initial_state(client_id, client_name)

# Execute workflow
result = graph.invoke(initial_state)
```

### 4. Visualization Pattern
```python
# Record interaction
tracer.record_interaction(from_agent, to_agent, data)

# Visualize interactions
tracer.visualize_interactions()
tracer.display_execution_statistics()

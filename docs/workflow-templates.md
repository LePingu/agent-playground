# Workflow Templates Reference

Agent Playground provides seven built-in workflow templates that cover common multi-agent patterns. This guide details each template, its parameters, and use cases.

## Overview

Workflow templates are pre-built patterns that simplify workflow creation. Instead of manually building workflows, you can use templates with your custom agents:

```python
from agent_playground.workflows import workflow_templates

# Use a template
workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents=[agent1, agent2, agent3],
    state_class=MyState
)
```

## Template Categories

Templates are organized by execution pattern:

- **Sequential**: One agent after another
- **Parallel**: Concurrent execution with aggregation
- **Conditional**: Dynamic routing based on state
- **Interactive**: Human-in-the-loop workflows
- **Validation**: Multi-stage validation pipelines
- **Analysis**: Multi-perspective analysis
- **Transformation**: Data transformation workflows

## Sequential Workflow Template

**Pattern**: Executes agents in a linear sequence, passing state from one to the next.

### Parameters

```python
workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents: List[BaseAgent],           # Required: List of agents to execute
    state_class: Type[BaseState],      # Required: State class to use
    error_handling: str = "stop",      # Optional: "stop", "skip", "retry"
    max_retries: int = 3               # Optional: Max retries per agent
)
```

### Use Cases

- **Data Processing Pipelines**: Extract → Transform → Load
- **Document Workflows**: Parse → Analyze → Classify
- **Step-by-step Analysis**: Collect → Process → Report

### Example

```python
from agent_playground.workflows.examples import (
    TextExtractionAgent, ContentAnalysisAgent, DocumentClassificationAgent
)

# Create agents
extractor = TextExtractionAgent()
analyzer = ContentAnalysisAgent()
classifier = DocumentClassificationAgent()

# Create sequential workflow
workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents=[extractor, analyzer, classifier],
    state_class=DocumentProcessingState,
    error_handling="retry",
    max_retries=2
)

# Execute
result = await workflow.execute(initial_state)
```

### Execution Flow

```
State → Agent1 → State → Agent2 → State → Agent3 → Final State
```

## Parallel Workflow Template

**Pattern**: Executes agents concurrently, then aggregates results.

### Parameters

```python
workflow = workflow_templates.create_workflow(
    template_name="parallel",
    agents: List[BaseAgent],              # Required: Agents to run in parallel
    aggregator_agent: BaseAgent,          # Required: Agent to aggregate results
    state_class: Type[BaseState],         # Required: State class to use
    timeout: float = 300.0,               # Optional: Timeout for parallel execution
    max_concurrent: int = None            # Optional: Max concurrent agents
)
```

### Use Cases

- **Independent Analysis**: Multiple perspectives on same data
- **Concurrent API Calls**: Fetch data from multiple sources
- **Parallel Processing**: CPU-intensive tasks

### Example

```python
from agent_playground.workflows.examples import (
    StatisticalAnalysisAgent, PredictiveAnalysisAgent, InsightGenerationAgent
)

# Create parallel analyzers
stat_analyzer = StatisticalAnalysisAgent()
pred_analyzer = PredictiveAnalysisAgent()

# Create aggregator
insight_generator = InsightGenerationAgent()

# Create parallel workflow
workflow = workflow_templates.create_workflow(
    template_name="parallel",
    agents=[stat_analyzer, pred_analyzer],
    aggregator_agent=insight_generator,
    state_class=DataAnalysisState,
    timeout=120.0,
    max_concurrent=2
)
```

### Execution Flow

```
             ┌─ Agent1 ─┐
State ───────┤          ├──→ Aggregator → Final State  
             └─ Agent2 ─┘
```

## Conditional Workflow Template

**Pattern**: Routes execution to different agent paths based on state conditions.

### Parameters

```python
def condition_func(state: BaseState) -> str:
    # Return path key based on state
    return "path_a" if state.condition else "path_b"

workflow = workflow_templates.create_workflow(
    template_name="conditional",
    condition_func: Callable,             # Required: Function to determine path
    agent_paths: Dict[str, List[BaseAgent]], # Required: Path name -> agents
    state_class: Type[BaseState],         # Required: State class to use
    default_path: str = None              # Optional: Default path if condition fails
)
```

### Use Cases

- **Dynamic Routing**: Route based on data type or content
- **Error Recovery**: Different handling for different error types
- **Business Logic**: Different processes for different conditions

### Example

```python
def route_by_document_type(state):
    if state.document_type == "pdf":
        return "pdf_path"
    elif state.document_type == "image":
        return "image_path"
    else:
        return "generic_path"

workflow = workflow_templates.create_workflow(
    template_name="conditional",
    condition_func=route_by_document_type,
    agent_paths={
        "pdf_path": [pdf_extractor, pdf_analyzer],
        "image_path": [ocr_agent, image_analyzer],
        "generic_path": [generic_processor]
    },
    state_class=DocumentProcessingState,
    default_path="generic_path"
)
```

### Execution Flow

```
State → Condition → Path A → Agent1 → Agent2 → Final State
                 └─ Path B → Agent3 → Agent4 → Final State
```

## Human-in-the-Loop Workflow Template

**Pattern**: Incorporates human review and approval at key decision points.

### Parameters

```python
workflow = workflow_templates.create_workflow(
    template_name="human_in_loop",
    agents: List[BaseAgent],              # Required: Primary workflow agents
    review_agent: BaseAgent,              # Required: Human review agent
    approval_required: bool = True,       # Optional: Whether approval is required
    review_timeout: float = 3600.0,       # Optional: Timeout for human review
    escalation_agent: BaseAgent = None    # Optional: Agent for escalation
)
```

### Use Cases

- **Quality Assurance**: Human verification of AI outputs
- **Compliance Review**: Regulatory approval requirements
- **Critical Decisions**: High-stakes decisions requiring human judgment

### Example

```python
class HumanReviewAgent(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        # Present data for human review
        state.needs_human_review = True
        state.review_prompt = "Please review the analysis results"
        
        # Wait for human input (implementation depends on your UI)
        human_response = await self.get_human_input(state)
        state.human_approved = human_response.approved
        state.human_feedback = human_response.feedback
        
        return state

# Create workflow with human review
workflow = workflow_templates.create_workflow(
    template_name="human_in_loop",
    agents=[analysis_agent, risk_assessment_agent],
    review_agent=HumanReviewAgent(),
    approval_required=True,
    review_timeout=1800.0  # 30 minutes
)
```

### Execution Flow

```
State → Agent1 → Review Point → Human Review → Agent2 → Final State
                              ↓
                         (Approval Required)
```

## Validation Workflow Template

**Pattern**: Multi-stage validation pipeline with configurable validation rules.

### Parameters

```python
workflow = workflow_templates.create_workflow(
    template_name="validation",
    validators: List[BaseAgent],          # Required: Validation agents
    processor_agent: BaseAgent,           # Required: Main processing agent
    state_class: Type[BaseState],         # Required: State class to use
    validation_mode: str = "all",         # Optional: "all", "any", "majority"
    continue_on_failure: bool = False     # Optional: Continue if validation fails
)
```

### Use Cases

- **Data Quality**: Validate data before processing
- **Input Validation**: Check user inputs against multiple criteria
- **Content Moderation**: Multi-stage content safety checks

### Example

```python
class FormatValidator(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        state.format_valid = self.check_format(state.input_data)
        return state

class ContentValidator(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        state.content_valid = self.check_content(state.input_data)
        return state

class DataProcessor(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        if state.format_valid and state.content_valid:
            state.processed_data = self.process(state.input_data)
        return state

workflow = workflow_templates.create_workflow(
    template_name="validation",
    validators=[FormatValidator(), ContentValidator()],
    processor_agent=DataProcessor(),
    state_class=ValidationState,
    validation_mode="all",
    continue_on_failure=False
)
```

### Execution Flow

```
State → Validator1 → Validator2 → ... → Processor → Final State
      ↓           ↓                   ↓
  (validation) (validation)      (only if valid)
```

## Analysis Workflow Template

**Pattern**: Multi-perspective analysis with preprocessing and synthesis.

### Parameters

```python
workflow = workflow_templates.create_workflow(
    template_name="analysis",
    preprocessor_agent: BaseAgent,        # Required: Data preprocessing
    analysis_agents: List[BaseAgent],     # Required: Analysis agents
    synthesizer_agent: BaseAgent,         # Required: Synthesis agent
    state_class: Type[BaseState],         # Required: State class to use
    parallel_analysis: bool = True        # Optional: Run analysis in parallel
)
```

### Use Cases

- **Research Analysis**: Multiple analytical perspectives
- **Decision Support**: Comprehensive analysis from different angles
- **Comparative Evaluation**: Compare multiple approaches

### Example

```python
# Create analysis workflow
workflow = workflow_templates.create_workflow(
    template_name="analysis",
    preprocessor_agent=DataCleaningAgent(),
    analysis_agents=[
        StatisticalAnalysisAgent(),
        TrendAnalysisAgent(),
        PredictiveAnalysisAgent()
    ],
    synthesizer_agent=InsightGenerationAgent(),
    state_class=DataAnalysisState,
    parallel_analysis=True
)
```

### Execution Flow

```
State → Preprocessor → Analysis1 → Synthesizer → Final State
                    → Analysis2 ↗
                    → Analysis3 ↗
```

## Transformation Workflow Template

**Pattern**: Data transformation pipeline with validation and error handling.

### Parameters

```python
workflow = workflow_templates.create_workflow(
    template_name="transformation",
    transformer_agents: List[BaseAgent],  # Required: Transformation agents
    validator_agent: BaseAgent,           # Required: Output validation
    state_class: Type[BaseState],         # Required: State class to use
    validate_intermediate: bool = False,  # Optional: Validate after each step
    rollback_on_failure: bool = True      # Optional: Rollback on validation failure
)
```

### Use Cases

- **Data Migration**: Transform data between formats
- **ETL Processes**: Extract, Transform, Load pipelines
- **Format Conversion**: Convert between different data formats

### Example

```python
class JSONToXMLTransformer(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        state.xml_data = self.json_to_xml(state.json_data)
        return state

class XMLValidator(BaseAgent):
    async def execute(self, state: BaseState) -> BaseState:
        state.validation_passed = self.validate_xml(state.xml_data)
        return state

workflow = workflow_templates.create_workflow(
    template_name="transformation",
    transformer_agents=[
        JSONToXMLTransformer(),
        XMLEnrichmentAgent(),
        XMLFormatterAgent()
    ],
    validator_agent=XMLValidator(),
    state_class=TransformationState,
    validate_intermediate=True,
    rollback_on_failure=True
)
```

### Execution Flow

```
State → Transform1 → Transform2 → ... → Validator → Final State
      ↓          ↓                   ↓
  (optional)  (optional)        (required)
  validation  validation        validation
```

## Template Registry

### Listing Available Templates

```python
from agent_playground.workflows import workflow_templates

# List all templates
templates = workflow_templates.list_templates()
for template in templates:
    print(f"{template.name}: {template.description}")

# Get template info
info = workflow_templates.get_template_info("sequential")
print(f"Parameters: {info.parameters}")
print(f"Use cases: {info.use_cases}")
```

### Custom Templates

You can create and register custom templates:

```python
from agent_playground.workflows.templates import WorkflowTemplate

@workflow_templates.register_template("custom")
class CustomWorkflowTemplate(WorkflowTemplate):
    def create_workflow(self, **kwargs):
        # Custom workflow creation logic
        return workflow

# Use custom template
workflow = workflow_templates.create_workflow(
    template_name="custom",
    custom_param="value",
    state_class=MyState
)
```

## Best Practices

### 1. Choose the Right Template

- **Sequential**: For dependent, ordered operations
- **Parallel**: For independent operations that can run concurrently
- **Conditional**: For dynamic routing based on data
- **Human-in-Loop**: For critical decisions requiring human judgment
- **Validation**: For data quality and input validation
- **Analysis**: For comprehensive multi-perspective analysis
- **Transformation**: For data format conversion and migration

### 2. State Design

Design your state classes to work well with templates:

```python
class WellDesignedState(BaseState):
    # Clear, descriptive field names
    input_data: Dict[str, Any] = {}
    processing_status: str = "pending"
    validation_results: List[str] = []
    
    # Helper methods for template logic
    def is_valid(self) -> bool:
        return len(self.validation_results) == 0
    
    def ready_for_processing(self) -> bool:
        return self.processing_status == "validated"
```

### 3. Error Handling

Configure appropriate error handling for your use case:

```python
# For critical workflows - stop on first error
workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents=agents,
    error_handling="stop",
    state_class=MyState
)

# For resilient workflows - skip failed agents
workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents=agents,
    error_handling="skip",
    state_class=MyState
)
```

### 4. Performance Optimization

- Use parallel templates for independent operations
- Set appropriate timeouts for long-running agents
- Limit concurrent agents to prevent resource exhaustion

```python
workflow = workflow_templates.create_workflow(
    template_name="parallel",
    agents=agents,
    aggregator_agent=aggregator,
    timeout=120.0,           # 2 minutes max
    max_concurrent=4,        # Limit concurrent agents
    state_class=MyState
)
```

---

**Next**: Learn how to create [custom agents](tutorials/custom-agents.md) and explore [workflow examples](examples/).

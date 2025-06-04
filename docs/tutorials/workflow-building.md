# Workflow Building Tutorial

Learn how to design and build powerful workflows that orchestrate multiple agents to solve complex problems. This tutorial covers everything from basic workflow patterns to advanced orchestration techniques.

## What Are Workflows?

Workflows are orchestration systems that coordinate the execution of multiple agents to achieve a common goal. They define:

- **Execution Order**: How agents are sequenced or parallelized
- **Data Flow**: How state flows between agents
- **Error Handling**: How failures are managed and recovered
- **Monitoring**: How execution is tracked and observed

## Basic Workflow Concepts

### Workflow Components

Every workflow consists of:

1. **Agents**: The processing units that perform work
2. **State**: The data that flows through the workflow
3. **Orchestration Logic**: Rules for agent execution order
4. **Error Handling**: Strategies for managing failures

```python
from agent_playground.workflows import WorkflowBuilder
from agent_playground.core import BaseAgent, BaseState

# Basic workflow structure
workflow = (WorkflowBuilder()
    .add_agent(preprocessing_agent)
    .add_agent(analysis_agent)
    .add_agent(reporting_agent)
    .build())
```

## Template-Based Workflow Building

### Using Pre-built Templates

The fastest way to create workflows is using built-in templates:

```python
from agent_playground.workflows import workflow_templates

# Sequential processing
sequential_workflow = workflow_templates.create_workflow(
    template_name="sequential",
    agents=[agent1, agent2, agent3],
    state_class=MyState
)

# Parallel processing with aggregation
parallel_workflow = workflow_templates.create_workflow(
    template_name="parallel",
    agents=[analyzer1, analyzer2, analyzer3],
    aggregator_agent=aggregator,
    state_class=AnalysisState
)

# Conditional branching
conditional_workflow = workflow_templates.create_workflow(
    template_name="conditional",
    condition_func=lambda state: "path_a" if state.priority == "high" else "path_b",
    agent_paths={
        "path_a": [urgent_agent, escalation_agent],
        "path_b": [standard_agent, routine_agent]
    },
    state_class=RequestState
)
```

### Available Templates

| Template | Use Case | Key Features |
|----------|----------|--------------|
| `sequential` | Step-by-step processing | Linear execution, simple error handling |
| `parallel` | Independent analysis | Concurrent execution, result aggregation |
| `conditional` | Dynamic routing | State-based branching, multiple paths |
| `human_in_loop` | Quality assurance | Human review points, approval gates |
| `validation` | Data quality | Multi-stage validation, early exit |
| `analysis` | Multi-perspective evaluation | Preprocessing, analysis, synthesis |
| `transformation` | Data migration | Sequential transformation, validation |

## Programmatic Workflow Building

### Using WorkflowBuilder

For more control, use the programmatic builder:

```python
from agent_playground.workflows import WorkflowBuilder

builder = WorkflowBuilder()

# Sequential building
workflow = (builder
    .set_name("document_processor")
    .set_description("Processes documents through multiple stages")
    .add_agent(text_extractor)
    .add_agent(content_analyzer)
    .add_agent(classifier)
    .add_conditional_branch(
        condition=lambda state: state.document_type,
        branches={
            "legal": [legal_processor],
            "financial": [financial_processor],
            "general": [general_processor]
        }
    )
    .add_agent(report_generator)
    .set_error_handling("retry")
    .build())
```

### Advanced Builder Patterns

```python
# Parallel sections with synchronization
workflow = (WorkflowBuilder()
    .add_agent(preprocessor)
    .start_parallel_section()
        .add_agent(sentiment_analyzer)
        .add_agent(topic_extractor)
        .add_agent(entity_recognizer)
    .end_parallel_section(aggregator_agent)
    .add_agent(final_processor)
    .build())

# Human-in-the-loop with timeout
workflow = (WorkflowBuilder()
    .add_agent(validation_agent)
    .add_human_review(
        review_prompt="Please review the validation results",
        timeout_seconds=3600,  # 1 hour timeout
        fallback_agent=auto_approval_agent
    )
    .add_agent(processing_agent)
    .build())

# Error recovery patterns
workflow = (WorkflowBuilder()
    .add_agent(primary_processor)
    .add_error_handler(
        error_type=ValidationError,
        handler_agent=validation_recovery_agent
    )
    .add_error_handler(
        error_type=TimeoutError,
        handler_agent=timeout_recovery_agent
    )
    .build())
```

## Custom Workflow Classes

### Creating Custom Workflows

For maximum flexibility, create custom workflow classes:

```python
from agent_playground.workflows import Workflow
from typing import List, Optional

class DataPipelineWorkflow(Workflow[DataState]):
    """Custom workflow for data processing pipelines."""
    
    def __init__(
        self,
        extractors: List[BaseAgent],
        transformers: List[BaseAgent],
        loaders: List[BaseAgent],
        batch_size: int = 1000
    ):
        all_agents = extractors + transformers + loaders
        super().__init__(
            name="data_pipeline",
            agents=all_agents,
            state_class=DataState
        )
        self.extractors = extractors
        self.transformers = transformers
        self.loaders = loaders
        self.batch_size = batch_size
    
    async def execute(
        self,
        initial_state: DataState,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> DataState:
        """Execute ETL pipeline with batching."""
        state = initial_state
        
        # Extract phase
        self.logger.info("Starting extraction phase")
        for extractor in self.extractors:
            state = await extractor.execute(state)
        
        # Transform phase with batching
        self.logger.info(f"Starting transformation phase with batch size {self.batch_size}")
        state = await self._process_in_batches(
            self.transformers, state, self.batch_size
        )
        
        # Load phase
        self.logger.info("Starting load phase")
        for loader in self.loaders:
            state = await loader.execute(state)
        
        return state
    
    async def _process_in_batches(
        self,
        agents: List[BaseAgent],
        state: DataState,
        batch_size: int
    ) -> DataState:
        """Process data in batches to manage memory."""
        total_records = len(state.records)
        batches = [
            state.records[i:i + batch_size]
            for i in range(0, total_records, batch_size)
        ]
        
        processed_records = []
        
        for batch_idx, batch in enumerate(batches):
            self.logger.info(f"Processing batch {batch_idx + 1}/{len(batches)}")
            
            # Create batch state
            batch_state = state.clone()
            batch_state.records = batch
            
            # Process batch through all transformers
            for transformer in agents:
                batch_state = await transformer.execute(batch_state)
            
            processed_records.extend(batch_state.records)
        
        # Update state with all processed records
        state.records = processed_records
        return state
```

### Specialized Workflow Patterns

```python
class MLPipelineWorkflow(Workflow[MLState]):
    """Machine learning pipeline with model training and validation."""
    
    def __init__(self, config: MLConfig):
        self.config = config
        
        agents = [
            DataValidationAgent(config.validation_rules),
            FeatureEngineeringAgent(config.feature_config),
            ModelTrainingAgent(config.model_config),
            ModelValidationAgent(config.validation_config),
            ModelDeploymentAgent(config.deployment_config)
        ]
        
        super().__init__(
            name="ml_pipeline",
            agents=agents,
            state_class=MLState
        )
    
    async def execute(
        self,
        initial_state: MLState,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> MLState:
        """Execute ML pipeline with checkpointing and rollback."""
        state = initial_state
        checkpoints = []
        
        for agent in self.agents:
            # Create checkpoint before each critical step
            checkpoint = state.clone()
            checkpoints.append(checkpoint)
            
            try:
                state = await agent.execute(state)
                
                # Validate critical metrics
                if isinstance(agent, ModelValidationAgent):
                    if state.model_metrics.accuracy < self.config.min_accuracy:
                        self.logger.warning("Model accuracy below threshold, rolling back")
                        return await self._rollback_and_retry(checkpoints, state)
                
            except Exception as e:
                self.logger.error(f"Pipeline failed at {agent.name}: {e}")
                
                # Attempt recovery
                if self.config.enable_recovery:
                    return await self._attempt_recovery(checkpoints, agent, e)
                else:
                    raise
        
        return state
    
    async def _rollback_and_retry(
        self,
        checkpoints: List[MLState],
        failed_state: MLState
    ) -> MLState:
        """Rollback to last checkpoint and retry with different parameters."""
        if not checkpoints:
            raise WorkflowExecutionError("No checkpoints available for rollback")
        
        # Rollback to feature engineering stage
        rollback_state = checkpoints[-2]  # Before model training
        
        # Adjust hyperparameters
        rollback_state.model_config.learning_rate *= 0.5
        rollback_state.model_config.max_epochs += 10
        
        # Retry from training stage
        remaining_agents = self.agents[-3:]  # Training, validation, deployment
        
        for agent in remaining_agents:
            rollback_state = await agent.execute(rollback_state)
        
        return rollback_state
```

## Workflow Composition

### Combining Workflows

Create complex systems by composing simpler workflows:

```python
class DocumentProcessingSystem:
    """System that combines multiple specialized workflows."""
    
    def __init__(self):
        # Create specialized workflows
        self.ingestion_workflow = self._create_ingestion_workflow()
        self.analysis_workflow = self._create_analysis_workflow()
        self.reporting_workflow = self._create_reporting_workflow()
    
    async def process_documents(
        self,
        document_paths: List[str]
    ) -> ProcessingResults:
        """Process documents through the complete pipeline."""
        
        results = ProcessingResults()
        
        for doc_path in document_paths:
            # Initial state
            state = DocumentState(document_path=doc_path)
            
            # Ingestion phase
            state = await self.ingestion_workflow.execute(state)
            
            # Skip analysis if ingestion failed
            if state.has_errors():
                results.add_failed_document(doc_path, state.errors)
                continue
            
            # Analysis phase
            state = await self.analysis_workflow.execute(state)
            
            # Reporting phase (always run to capture partial results)
            state = await self.reporting_workflow.execute(state)
            
            results.add_processed_document(doc_path, state)
        
        return results
    
    def _create_ingestion_workflow(self):
        """Create document ingestion workflow."""
        return workflow_templates.create_workflow(
            template_name="validation",
            validators=[
                FileExistenceValidator(),
                FileFormatValidator(),
                FileSizeValidator()
            ],
            processor_agent=DocumentLoaderAgent(),
            state_class=DocumentState
        )
    
    def _create_analysis_workflow(self):
        """Create document analysis workflow."""
        return workflow_templates.create_workflow(
            template_name="parallel",
            agents=[
                TextExtractionAgent(),
                MetadataExtractionAgent(),
                StructureAnalysisAgent()
            ],
            aggregator_agent=AnalysisAggregatorAgent(),
            state_class=DocumentState
        )
    
    def _create_reporting_workflow(self):
        """Create reporting workflow."""
        return workflow_templates.create_workflow(
            template_name="sequential",
            agents=[
                ReportGeneratorAgent(),
                ReportFormatterAgent(),
                ReportPersistenceAgent()
            ],
            state_class=DocumentState
        )
```

### Workflow Hierarchies

```python
class HierarchicalWorkflow(Workflow[HierarchicalState]):
    """Workflow that manages sub-workflows."""
    
    def __init__(self):
        self.sub_workflows = {
            "preprocessing": PreprocessingWorkflow(),
            "analysis": AnalysisWorkflow(),
            "postprocessing": PostprocessingWorkflow()
        }
        
        # Create coordinator agents
        agents = [
            WorkflowCoordinatorAgent(self.sub_workflows),
            ResultsAggregatorAgent(),
            QualityAssuranceAgent()
        ]
        
        super().__init__(
            name="hierarchical_processor",
            agents=agents,
            state_class=HierarchicalState
        )
    
    async def execute(
        self,
        initial_state: HierarchicalState,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> HierarchicalState:
        """Execute hierarchical workflow."""
        state = initial_state
        
        # Execute sub-workflows based on state requirements
        for workflow_name, workflow in self.sub_workflows.items():
            if self._should_execute_workflow(workflow_name, state):
                self.logger.info(f"Executing sub-workflow: {workflow_name}")
                
                # Create sub-monitor if monitoring is enabled
                sub_monitor = monitor.create_sub_monitor(workflow_name) if monitor else None
                
                # Execute sub-workflow
                state = await workflow.execute(state, sub_monitor)
                
                # Check for critical failures
                if self._has_critical_failure(state):
                    self.logger.error(f"Critical failure in {workflow_name}")
                    break
        
        # Final coordination and aggregation
        for agent in self.agents:
            state = await agent.execute(state)
        
        return state
    
    def _should_execute_workflow(self, workflow_name: str, state: HierarchicalState) -> bool:
        """Determine if a sub-workflow should be executed."""
        requirements = state.workflow_requirements.get(workflow_name, {})
        
        # Check conditions
        if requirements.get("condition"):
            return requirements["condition"](state)
        
        # Check dependencies
        dependencies = requirements.get("dependencies", [])
        for dep in dependencies:
            if not state.workflow_results.get(dep, {}).get("success", False):
                return False
        
        return True
```

## Dynamic Workflow Construction

### Runtime Workflow Building

Build workflows dynamically based on input data:

```python
class DynamicWorkflowFactory:
    """Factory for creating workflows based on input characteristics."""
    
    def __init__(self):
        self.agent_registry = {
            "text_extraction": TextExtractionAgent(),
            "image_analysis": ImageAnalysisAgent(),
            "data_validation": DataValidationAgent(),
            "sentiment_analysis": SentimentAnalysisAgent(),
            "topic_modeling": TopicModelingAgent(),
            "translation": TranslationAgent(),
            "summarization": SummarizationAgent()
        }
    
    def create_workflow_for_content(self, content_info: ContentInfo) -> Workflow:
        """Create a workflow tailored to the content type and requirements."""
        builder = WorkflowBuilder()
        builder.set_name(f"dynamic_workflow_{content_info.id}")
        
        # Always start with validation
        builder.add_agent(self.agent_registry["data_validation"])
        
        # Add content-specific agents
        if content_info.has_text:
            builder.add_agent(self.agent_registry["text_extraction"])
            
            if content_info.requires_sentiment:
                builder.add_agent(self.agent_registry["sentiment_analysis"])
            
            if content_info.requires_topics:
                builder.add_agent(self.agent_registry["topic_modeling"])
            
            if content_info.target_language != content_info.source_language:
                builder.add_agent(self.agent_registry["translation"])
        
        if content_info.has_images:
            builder.add_agent(self.agent_registry["image_analysis"])
        
        # Add summarization if content is large
        if content_info.estimated_size > 10000:  # Large content
            builder.add_agent(self.agent_registry["summarization"])
        
        return builder.build()
    
    def create_parallel_workflow(self, analysis_types: List[str]) -> Workflow:
        """Create a parallel workflow for multiple analysis types."""
        analysis_agents = [
            self.agent_registry[analysis_type]
            for analysis_type in analysis_types
            if analysis_type in self.agent_registry
        ]
        
        return workflow_templates.create_workflow(
            template_name="parallel",
            agents=analysis_agents,
            aggregator_agent=AnalysisAggregatorAgent(),
            state_class=AnalysisState
        )
```

### Adaptive Workflows

Workflows that adapt based on intermediate results:

```python
class AdaptiveWorkflow(Workflow[AdaptiveState]):
    """Workflow that adapts its execution based on intermediate results."""
    
    def __init__(self):
        # Define agent pools for different scenarios
        self.agent_pools = {
            "high_confidence": [
                StandardProcessorAgent(),
                LightValidationAgent()
            ],
            "medium_confidence": [
                EnhancedProcessorAgent(),
                StandardValidationAgent(),
                QualityCheckAgent()
            ],
            "low_confidence": [
                RobustProcessorAgent(),
                StrictValidationAgent(),
                ManualReviewAgent(),
                QualityAssuranceAgent()
            ]
        }
        
        super().__init__(
            name="adaptive_workflow",
            agents=[],  # Agents selected dynamically
            state_class=AdaptiveState
        )
    
    async def execute(
        self,
        initial_state: AdaptiveState,
        monitor: Optional[WorkflowMonitor] = None,
        **kwargs
    ) -> AdaptiveState:
        """Execute workflow with adaptive agent selection."""
        state = initial_state
        
        # Initial assessment
        assessment_agent = InitialAssessmentAgent()
        state = await assessment_agent.execute(state)
        
        # Select processing strategy based on confidence
        confidence_level = self._determine_confidence_level(state)
        selected_agents = self.agent_pools[confidence_level]
        
        self.logger.info(f"Selected {confidence_level} confidence path with {len(selected_agents)} agents")
        
        # Execute selected agents
        for agent in selected_agents:
            state = await agent.execute(state)
            
            # Re-evaluate confidence after each step
            new_confidence = self._evaluate_current_confidence(state)
            
            # Adapt if confidence has changed significantly
            if new_confidence != confidence_level:
                self.logger.info(f"Confidence changed from {confidence_level} to {new_confidence}")
                confidence_level = new_confidence
                
                # Switch to appropriate agent pool for remaining steps
                remaining_agents = self._get_remaining_agents(
                    confidence_level, agent, selected_agents
                )
                selected_agents = selected_agents[:selected_agents.index(agent) + 1] + remaining_agents
        
        return state
    
    def _determine_confidence_level(self, state: AdaptiveState) -> str:
        """Determine confidence level based on state assessment."""
        confidence_score = state.confidence_metrics.get("overall_confidence", 0.5)
        
        if confidence_score >= 0.8:
            return "high_confidence"
        elif confidence_score >= 0.5:
            return "medium_confidence"
        else:
            return "low_confidence"
    
    def _get_remaining_agents(
        self,
        confidence_level: str,
        current_agent: BaseAgent,
        original_agents: List[BaseAgent]
    ) -> List[BaseAgent]:
        """Get remaining agents for the new confidence level."""
        current_index = original_agents.index(current_agent)
        new_agents = self.agent_pools[confidence_level]
        
        # Return agents that haven't been executed yet in the new pool
        return new_agents[current_index + 1:]
```

## Testing Workflows

### Unit Testing Workflows

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_sequential_workflow():
    """Test sequential workflow execution."""
    # Create mock agents
    agent1 = Mock(spec=BaseAgent)
    agent1.name = "Agent1"
    agent1.execute = AsyncMock(side_effect=lambda state: state)
    
    agent2 = Mock(spec=BaseAgent)
    agent2.name = "Agent2"
    agent2.execute = AsyncMock(side_effect=lambda state: state)
    
    # Create workflow
    workflow = workflow_templates.create_workflow(
        template_name="sequential",
        agents=[agent1, agent2],
        state_class=BaseState
    )
    
    # Execute workflow
    initial_state = BaseState()
    result = await workflow.execute(initial_state)
    
    # Verify execution
    agent1.execute.assert_called_once()
    agent2.execute.assert_called_once()
    assert result is not None

@pytest.mark.asyncio
async def test_workflow_error_handling():
    """Test workflow error handling."""
    # Create agent that fails
    failing_agent = Mock(spec=BaseAgent)
    failing_agent.name = "FailingAgent"
    failing_agent.execute = AsyncMock(side_effect=Exception("Test error"))
    
    # Create workflow with error recovery
    workflow = ResilientWorkflow(
        name="test_workflow",
        agents=[failing_agent],
        state_class=BaseState,
        recovery_strategy="continue"
    )
    
    # Execute workflow
    initial_state = BaseState()
    result = await workflow.execute(initial_state)
    
    # Verify error was captured
    assert len(result.errors) == 1
    assert "Test error" in result.errors[0]["message"]
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_complete_document_workflow():
    """Integration test for document processing workflow."""
    # Create real agents (not mocks)
    workflow = DocumentProcessingWorkflow(
        extractors=[TextExtractionAgent()],
        analyzers=[ContentAnalysisAgent(), SentimentAnalysisAgent()],
        generators=[ReportGenerationAgent()]
    )
    
    # Create test state with sample document
    test_state = DocumentState(
        document_path="test_documents/sample.pdf",
        processing_options={
            "extract_text": True,
            "analyze_sentiment": True,
            "generate_report": True
        }
    )
    
    # Execute workflow
    result = await workflow.execute(test_state)
    
    # Verify results
    assert result.extracted_text is not None
    assert result.sentiment_score is not None
    assert result.analysis_report is not None
    assert not result.has_errors()

@pytest.mark.asyncio
async def test_workflow_performance():
    """Test workflow performance characteristics."""
    workflow = create_performance_test_workflow()
    
    # Measure execution time
    start_time = time.time()
    
    initial_state = PerformanceTestState(
        data_size=10000,
        complexity_level="medium"
    )
    
    result = await workflow.execute(initial_state)
    
    execution_time = time.time() - start_time
    
    # Performance assertions
    assert execution_time < 30.0  # Should complete within 30 seconds
    assert result.processed_records == 10000
    assert result.performance_metrics["memory_peak"] < 512 * 1024 * 1024  # Under 512MB
```

## Best Practices

### 1. Workflow Design Principles

```python
# ✅ Good: Clear, focused workflow
class CustomerAnalysisWorkflow(Workflow[CustomerState]):
    """Analyzes customer data for insights and recommendations."""
    
    def __init__(self):
        agents = [
            DataValidationAgent(),          # Validate input
            CustomerSegmentationAgent(),    # Segment customers
            BehaviorAnalysisAgent(),       # Analyze behavior
            RecommendationAgent(),         # Generate recommendations
            ReportGenerationAgent()        # Create report
        ]
        
        super().__init__(
            name="customer_analysis",
            agents=agents,
            state_class=CustomerState,
            description="End-to-end customer analysis pipeline"
        )

# ❌ Bad: Unclear, monolithic workflow
class GenericWorkflow(Workflow[BaseState]):
    """Does everything."""  # Too vague
    
    def __init__(self):
        # Too many disparate responsibilities
        agents = [data_agent, ml_agent, report_agent, email_agent, file_agent]
        super().__init__("generic", agents, BaseState)
```

### 2. Error Handling Strategy

```python
class RobustWorkflow(Workflow[T]):
    """Workflow with comprehensive error handling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_strategy = kwargs.get("error_strategy", "fail_fast")
        self.max_retries = kwargs.get("max_retries", 3)
    
    async def execute(self, initial_state: T, **kwargs) -> T:
        state = initial_state
        
        for agent in self.agents:
            retry_count = 0
            
            while retry_count <= self.max_retries:
                try:
                    state = await agent.execute(state)
                    break  # Success, move to next agent
                    
                except Exception as e:
                    retry_count += 1
                    
                    # Log the error
                    self.logger.error(f"Agent {agent.name} failed (attempt {retry_count}): {e}")
                    
                    # Decide on retry strategy
                    if retry_count <= self.max_retries:
                        if self._is_retryable_error(e):
                            await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                            continue
                    
                    # Handle final failure
                    state.add_error(agent.name, str(e))
                    
                    if self.error_strategy == "fail_fast":
                        raise WorkflowExecutionError(f"Workflow failed at {agent.name}")
                    elif self.error_strategy == "continue":
                        self.logger.warning(f"Continuing despite failure in {agent.name}")
                        break
        
        return state
```

### 3. State Management

```python
class StateAwareWorkflow(Workflow[T]):
    """Workflow that carefully manages state transitions."""
    
    async def execute(self, initial_state: T, **kwargs) -> T:
        # Initialize execution context
        state = initial_state.clone()
        state.execution_context = {
            "workflow_name": self.name,
            "execution_id": str(uuid.uuid4()),
            "started_at": datetime.utcnow(),
            "agent_history": []
        }
        
        try:
            for agent in self.agents:
                # Pre-execution state validation
                if not self._validate_state_for_agent(state, agent):
                    raise StateValidationError(f"Invalid state for {agent.name}")
                
                # Create checkpoint
                checkpoint = {
                    "agent": agent.name,
                    "timestamp": datetime.utcnow(),
                    "state_snapshot": state.to_dict()
                }
                
                # Execute agent
                state = await agent.execute(state)
                
                # Post-execution validation
                if not self._validate_agent_output(state, agent):
                    # Restore from checkpoint if needed
                    state = self._restore_from_checkpoint(checkpoint)
                    raise StateValidationError(f"Invalid output from {agent.name}")
                
                # Update execution history
                state.execution_context["agent_history"].append({
                    "agent": agent.name,
                    "completed_at": datetime.utcnow(),
                    "success": True
                })
            
            # Mark successful completion
            state.execution_context["completed_at"] = datetime.utcnow()
            state.execution_context["success"] = True
            
        except Exception as e:
            # Mark failed completion
            state.execution_context["completed_at"] = datetime.utcnow()
            state.execution_context["success"] = False
            state.execution_context["error"] = str(e)
            raise
        
        return state
```

### 4. Performance Optimization

```python
class OptimizedWorkflow(Workflow[T]):
    """Workflow optimized for performance."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_caching = kwargs.get("enable_caching", True)
        self.cache = {} if self.enable_caching else None
        self.max_parallel_agents = kwargs.get("max_parallel", 4)
    
    async def execute(self, initial_state: T, **kwargs) -> T:
        # Check cache for similar executions
        if self.enable_caching:
            cache_key = self._generate_cache_key(initial_state)
            if cache_key in self.cache:
                self.logger.info("Returning cached result")
                return self.cache[cache_key].clone()
        
        # Identify parallelizable agents
        parallel_groups = self._identify_parallel_groups()
        
        state = initial_state
        
        for group in parallel_groups:
            if len(group) == 1:
                # Sequential execution
                state = await group[0].execute(state)
            else:
                # Parallel execution
                state = await self._execute_parallel_group(group, state)
        
        # Cache result if enabled
        if self.enable_caching:
            self.cache[cache_key] = state.clone()
        
        return state
    
    async def _execute_parallel_group(
        self,
        agents: List[BaseAgent],
        state: T
    ) -> T:
        """Execute a group of agents in parallel."""
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.max_parallel_agents)
        
        async def execute_with_semaphore(agent: BaseAgent) -> T:
            async with semaphore:
                return await agent.execute(state.clone())
        
        # Execute all agents concurrently
        tasks = [execute_with_semaphore(agent) for agent in agents]
        results = await asyncio.gather(*tasks)
        
        # Merge results back into main state
        return self._merge_parallel_results(state, results)
```

## Next Steps

After mastering workflow building, explore:

- [State Management Tutorial](state-management.md) - Design effective state classes
- [Error Handling Tutorial](error-handling.md) - Robust error handling strategies
- [Monitoring Tutorial](monitoring.md) - Track and monitor workflow execution
- [Performance Tutorial](performance.md) - Optimize workflow performance

## See Also

- [Workflow Templates Reference](../workflow-templates.md) - Pre-built workflow patterns
- [Workflow API Reference](../api/workflows/workflow.md) - Complete API documentation
- [Example Workflows](../examples/) - Real-world workflow examples

"""Workflow templates for common agent patterns."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, TypeVar, Generic
from enum import Enum

from ..core.base import BaseAgent, BaseWorkflow, BaseState
from ..utils.logging import get_logger
from .builder import WorkflowBuilder

T = TypeVar('T', bound=BaseState)


class WorkflowTemplate(ABC, Generic[T]):
    """Abstract base class for workflow templates."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = get_logger(f"template_{name}")
    
    @abstractmethod
    def create_workflow(self, **kwargs) -> BaseWorkflow:
        """Create a workflow instance from this template."""
        pass
    
    @abstractmethod
    def get_required_parameters(self) -> List[str]:
        """Get list of required parameters for this template."""
        pass
    
    @abstractmethod
    def get_optional_parameters(self) -> Dict[str, Any]:
        """Get dict of optional parameters with default values."""
        pass


class WorkflowPattern(Enum):
    """Common workflow patterns."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    HUMAN_IN_LOOP = "human_in_loop"
    VALIDATION = "validation"
    ANALYSIS = "analysis"
    TRANSFORMATION = "transformation"


class SequentialWorkflowTemplate(WorkflowTemplate[T]):
    """Template for sequential agent workflows."""
    
    def __init__(self):
        super().__init__(
            name="sequential",
            description="Sequential workflow where agents execute one after another"
        )
    
    def create_workflow(
        self,
        agents: List[BaseAgent],
        state_class: type = BaseState,
        **kwargs
    ) -> BaseWorkflow:
        """Create a sequential workflow."""
        if not agents:
            raise ValueError("At least one agent is required")
        
        builder = WorkflowBuilder(
            name=f"sequential_{self.name}",
            description=f"Sequential workflow with {len(agents)} agents"
        )
        
        # Add all agents
        for agent in agents:
            builder.add_agent(agent)
        
        # Connect agents in sequence
        for i in range(len(agents) - 1):
            builder.connect(agents[i].name, agents[i + 1].name)
        
        return builder.build()
    
    def get_required_parameters(self) -> List[str]:
        return ["agents"]
    
    def get_optional_parameters(self) -> Dict[str, Any]:
        return {
            "state_class": BaseState,
            "error_handling": "continue",
            "logging_level": "INFO"
        }


class ParallelWorkflowTemplate(WorkflowTemplate[T]):
    """Template for parallel agent workflows."""
    
    def __init__(self):
        super().__init__(
            name="parallel",
            description="Parallel workflow where agents execute simultaneously"
        )
    
    def create_workflow(
        self,
        agents: List[BaseAgent],
        aggregator_agent: BaseAgent,
        state_class: type = BaseState,
        **kwargs
    ) -> BaseWorkflow:
        """Create a parallel workflow."""
        if not agents:
            raise ValueError("At least one agent is required")
        if not aggregator_agent:
            raise ValueError("Aggregator agent is required")
        
        builder = WorkflowBuilder(
            name=f"parallel_{self.name}",
            description=f"Parallel workflow with {len(agents)} agents"
        )
        
        # Add all agents
        for agent in agents:
            builder.add_agent(agent)
        builder.add_agent(aggregator_agent)
        
        # Connect all agents to aggregator
        for agent in agents:
            builder.connect(agent.name, aggregator_agent.name)
        
        return builder.build()
    
    def get_required_parameters(self) -> List[str]:
        return ["agents", "aggregator_agent"]
    
    def get_optional_parameters(self) -> Dict[str, Any]:
        return {
            "state_class": BaseState,
            "timeout": 300,
            "error_handling": "partial_results"
        }


class ConditionalWorkflowTemplate(WorkflowTemplate[T]):
    """Template for conditional workflows with branching logic."""
    
    def __init__(self):
        super().__init__(
            name="conditional",
            description="Conditional workflow with branching based on state conditions"
        )
    
    def create_workflow(
        self,
        decision_agent: BaseAgent,
        branch_agents: Dict[str, BaseAgent],
        condition_func: Callable[[T], str],
        state_class: type = BaseState,
        **kwargs
    ) -> BaseWorkflow:
        """Create a conditional workflow."""
        if not decision_agent:
            raise ValueError("Decision agent is required")
        if not branch_agents:
            raise ValueError("At least one branch agent is required")
        
        builder = WorkflowBuilder(
            name=f"conditional_{self.name}",
            description=f"Conditional workflow with {len(branch_agents)} branches"
        )
        
        # Add decision agent
        builder.add_agent(decision_agent)
        
        # Add branch agents
        for condition, agent in branch_agents.items():
            builder.add_agent(agent)
            # Note: Conditional connections would need to be handled
            # by the workflow engine - this is a simplified example
            builder.connect(decision_agent.name, agent.name)
        
        return builder.build()
    
    def get_required_parameters(self) -> List[str]:
        return ["decision_agent", "branch_agents", "condition_func"]
    
    def get_optional_parameters(self) -> Dict[str, Any]:
        return {
            "state_class": BaseState,
            "default_branch": None,
            "error_handling": "raise"
        }


class HumanInLoopWorkflowTemplate(WorkflowTemplate[T]):
    """Template for workflows requiring human interaction."""
    
    def __init__(self):
        super().__init__(
            name="human_in_loop",
            description="Workflow with human review and approval steps"
        )
    
    def create_workflow(
        self,
        agents: List[BaseAgent],
        human_agent: BaseAgent,
        review_points: List[str],
        state_class: type = BaseState,
        **kwargs
    ) -> BaseWorkflow:
        """Create a human-in-the-loop workflow."""
        if not agents:
            raise ValueError("At least one agent is required")
        if not human_agent:
            raise ValueError("Human agent is required")
        
        builder = WorkflowBuilder(
            name=f"human_in_loop_{self.name}",
            description=f"Human-in-the-loop workflow with {len(agents)} agents"
        )
        
        # Add all agents
        for agent in agents:
            builder.add_agent(agent)
        builder.add_agent(human_agent)
        
        # Connect agents with human review points
        for i, agent in enumerate(agents):
            if agent.name in review_points:
                builder.connect(agent.name, human_agent.name)
                if i < len(agents) - 1:
                    builder.connect(human_agent.name, agents[i + 1].name)
            elif i < len(agents) - 1:
                builder.connect(agent.name, agents[i + 1].name)
        
        return builder.build()
    
    def get_required_parameters(self) -> List[str]:
        return ["agents", "human_agent", "review_points"]
    
    def get_optional_parameters(self) -> Dict[str, Any]:
        return {
            "state_class": BaseState,
            "timeout": 3600,
            "auto_approve": False
        }


class ValidationWorkflowTemplate(WorkflowTemplate[T]):
    """Template for data validation workflows."""
    
    def __init__(self):
        super().__init__(
            name="validation",
            description="Workflow for validating data through multiple stages"
        )
    
    def create_workflow(
        self,
        validation_agents: List[BaseAgent],
        aggregator_agent: BaseAgent,
        state_class: type = BaseState,
        **kwargs
    ) -> BaseWorkflow:
        """Create a validation workflow."""
        if not validation_agents:
            raise ValueError("At least one validation agent is required")
        if not aggregator_agent:
            raise ValueError("Aggregator agent is required")
        
        builder = WorkflowBuilder(
            name=f"validation_{self.name}",
            description=f"Validation workflow with {len(validation_agents)} validators"
        )
        
        # Add all agents
        for agent in validation_agents:
            builder.add_agent(agent)
        builder.add_agent(aggregator_agent)
        
        # Connect validators to aggregator
        for agent in validation_agents:
            builder.connect(agent.name, aggregator_agent.name)
        
        return builder.build()
    
    def get_required_parameters(self) -> List[str]:
        return ["validation_agents", "aggregator_agent"]
    
    def get_optional_parameters(self) -> Dict[str, Any]:
        return {
            "state_class": BaseState,
            "fail_fast": False,
            "minimum_validations": 1
        }


class AnalysisWorkflowTemplate(WorkflowTemplate[T]):
    """Template for data analysis workflows."""
    
    def __init__(self):
        super().__init__(
            name="analysis",
            description="Workflow for analyzing data through multiple perspectives"
        )
    
    def create_workflow(
        self,
        preprocessor_agent: BaseAgent,
        analysis_agents: List[BaseAgent],
        synthesizer_agent: BaseAgent,
        state_class: type = BaseState,
        **kwargs
    ) -> BaseWorkflow:
        """Create an analysis workflow."""
        if not analysis_agents:
            raise ValueError("At least one analysis agent is required")
        
        builder = WorkflowBuilder(
            name=f"analysis_{self.name}",
            description=f"Analysis workflow with {len(analysis_agents)} analyzers"
        )
        
        # Add preprocessor if provided
        if preprocessor_agent:
            builder.add_agent(preprocessor_agent)
        
        # Add analysis agents
        for agent in analysis_agents:
            builder.add_agent(agent)
        
        # Add synthesizer if provided
        if synthesizer_agent:
            builder.add_agent(synthesizer_agent)
        
        # Connect workflow
        if preprocessor_agent:
            for agent in analysis_agents:
                builder.connect(preprocessor_agent.name, agent.name)
        
        if synthesizer_agent:
            for agent in analysis_agents:
                builder.connect(agent.name, synthesizer_agent.name)
        
        return builder.build()
    
    def get_required_parameters(self) -> List[str]:
        return ["analysis_agents"]
    
    def get_optional_parameters(self) -> Dict[str, Any]:
        return {
            "state_class": BaseState,
            "preprocessor_agent": None,
            "synthesizer_agent": None,
            "parallel_analysis": True
        }


class TransformationWorkflowTemplate(WorkflowTemplate[T]):
    """Template for data transformation workflows."""
    
    def __init__(self):
        super().__init__(
            name="transformation",
            description="Workflow for transforming data through multiple stages"
        )
    
    def create_workflow(
        self,
        transformation_agents: List[BaseAgent],
        state_class: type = BaseState,
        **kwargs
    ) -> BaseWorkflow:
        """Create a transformation workflow."""
        if not transformation_agents:
            raise ValueError("At least one transformation agent is required")
        
        builder = WorkflowBuilder(
            name=f"transformation_{self.name}",
            description=f"Transformation workflow with {len(transformation_agents)} transformers"
        )
        
        # Add all agents
        for agent in transformation_agents:
            builder.add_agent(agent)
        
        # Connect agents in sequence
        for i in range(len(transformation_agents) - 1):
            builder.connect(
                transformation_agents[i].name,
                transformation_agents[i + 1].name
            )
        
        return builder.build()
    
    def get_required_parameters(self) -> List[str]:
        return ["transformation_agents"]
    
    def get_optional_parameters(self) -> Dict[str, Any]:
        return {
            "state_class": BaseState,
            "error_handling": "rollback",
            "checkpoint_frequency": 1
        }


class WorkflowTemplateRegistry:
    """Registry for workflow templates."""
    
    def __init__(self):
        self._templates: Dict[str, WorkflowTemplate] = {}
        self.logger = get_logger("workflow_template_registry")
        
        # Register built-in templates
        self._register_builtin_templates()
    
    def _register_builtin_templates(self):
        """Register built-in workflow templates."""
        templates = [
            SequentialWorkflowTemplate(),
            ParallelWorkflowTemplate(),
            ConditionalWorkflowTemplate(),
            HumanInLoopWorkflowTemplate(),
            ValidationWorkflowTemplate(),
            AnalysisWorkflowTemplate(),
            TransformationWorkflowTemplate(),
        ]
        
        for template in templates:
            self.register(template)
    
    def register(self, template: WorkflowTemplate):
        """Register a workflow template."""
        self._templates[template.name] = template
        self.logger.info(f"Registered workflow template: {template.name}")
    
    def get(self, name: str) -> Optional[WorkflowTemplate]:
        """Get a workflow template by name."""
        return self._templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all registered template names."""
        return list(self._templates.keys())
    
    def get_template_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a template."""
        template = self.get(name)
        if not template:
            return None
        
        return {
            "name": template.name,
            "description": template.description,
            "required_parameters": template.get_required_parameters(),
            "optional_parameters": template.get_optional_parameters(),
            "pattern": self._infer_pattern(template)
        }
    
    def _infer_pattern(self, template: WorkflowTemplate) -> str:
        """Infer the workflow pattern from template name."""
        name = template.name.lower()
        for pattern in WorkflowPattern:
            if pattern.value in name:
                return pattern.value
        return "custom"
    
    def create_workflow(self, template_name: str, **kwargs) -> Optional[BaseWorkflow]:
        """Create a workflow from a template."""
        template = self.get(template_name)
        if not template:
            self.logger.error(f"Template not found: {template_name}")
            return None
        
        try:
            return template.create_workflow(**kwargs)
        except Exception as e:
            self.logger.error(f"Failed to create workflow from template {template_name}: {e}")
            return None


# Global registry instance
workflow_templates = WorkflowTemplateRegistry()

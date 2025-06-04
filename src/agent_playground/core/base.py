"""Base agent classes and interfaces for the Agent Playground framework."""

import operator
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union, Annotated
from pydantic import BaseModel, Field, validator
from langchain.schema import BaseMessage
from langgraph.graph import StateGraph, END

from ..utils.logging import LoggingMixin
from ..utils.config import get_settings

T = TypeVar('T', bound=BaseModel)


class AgentConfig(BaseModel):
    """Base configuration for all agents."""
    
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    
    # Execution parameters
    max_iterations: int = Field(default=10, ge=1, le=100, description="Maximum iterations")
    timeout: int = Field(default=300, ge=1, description="Timeout in seconds")
    retry_attempts: int = Field(default=3, ge=0, description="Number of retry attempts")
    
    # Model parameters
    model_name: str = Field(default="gpt-4", description="Model name to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: Optional[int] = Field(default=None, gt=0, description="Maximum tokens")
    
    # Behavior flags
    enable_tracing: bool = Field(default=True, description="Enable execution tracing")
    enable_validation: bool = Field(default=True, description="Enable input/output validation")
    parallel_execution: bool = Field(default=False, description="Enable parallel execution")
    
    class Config:
        validate_assignment = True
        extra = "allow"  # Allow additional fields for specialized agents


class AgentState(BaseModel):
    """Base state model for all agents."""
    
    # Core execution state
    messages: List[BaseMessage] = Field(default_factory=list, description="Message history")
    context: Dict[str, Any] = Field(default_factory=dict, description="Agent context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    
    # Execution tracking
    iteration: int = Field(default=0, ge=0, description="Current iteration")
    completed: bool = Field(default=False, description="Whether execution is completed")
    error: Optional[str] = Field(default=None, description="Error message if any")
    
    # Timestamps
    start_time: Optional[datetime] = Field(default=None, description="Execution start time")
    end_time: Optional[datetime] = Field(default=None, description="Execution end time")
    
    # Results
    result: Optional[Dict[str, Any]] = Field(default=None, description="Agent execution result")
    
    @validator("start_time", "end_time", pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v
    
    @property
    def duration(self) -> Optional[float]:
        """Get execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


class BaseAgent(ABC, Generic[T], LoggingMixin):
    """
    Base class for all reusable agents in the playground.
    
    This class provides:
    - Type-safe state management
    - Configuration validation
    - Graph building patterns
    - Error handling
    - Logging integration
    - Extensible architecture
    """
    
    def __init__(
        self, 
        config: AgentConfig, 
        state_class: Type[T] = AgentState,
        **kwargs: Any
    ):
        """
        Initialize the base agent.
        
        Args:
            config: Agent configuration
            state_class: State class to use for type safety
            **kwargs: Additional arguments for specialized agents
        """
        self.config = config
        self.state_class = state_class
        self._graph: Optional[StateGraph] = None
        self._compiled_graph = None
        
        # Initialize from global settings if needed
        settings = get_settings()
        if not hasattr(config, 'model_name') or not config.model_name:
            self.config.model_name = settings.model.openrouter_model
        
        self.log_info(f"Initialized agent: {config.name}", agent_type=self.__class__.__name__)
    
    @property
    def graph(self) -> StateGraph:
        """Lazy-loaded compiled graph."""
        if self._compiled_graph is None:
            if self._graph is None:
                self.log_debug("Building agent graph")
                self._graph = self._build_graph()
            
            self.log_debug("Compiling agent graph")
            self._compiled_graph = self._graph.compile()
        
        return self._compiled_graph
    
    @abstractmethod
    def _build_graph(self) -> StateGraph:
        """
        Build the agent's state graph. Must be implemented by subclasses.
        
        Returns:
            StateGraph instance defining the agent's workflow
        """
        pass
    
    @abstractmethod
    async def _process_step(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single step of the agent's workflow.
        
        Args:
            state: Current state dictionary
            
        Returns:
            Updated state dictionary
        """
        pass
    
    def validate_state(self, state: Dict[str, Any]) -> T:
        """
        Validate and return typed state.
        
        Args:
            state: State dictionary to validate
            
        Returns:
            Validated state instance
            
        Raises:
            ValidationError: If state is invalid
        """
        try:
            return self.state_class(**state)
        except Exception as e:
            self.log_error(f"State validation failed", error=e, state_keys=list(state.keys()))
            raise
    
    async def run(self, initial_state: Dict[str, Any]) -> T:
        """
        Run the agent with the given initial state.
        
        Args:
            initial_state: Initial state dictionary
            
        Returns:
            Final state after processing
        """
        start_time = datetime.now()
        
        # Prepare initial state
        state = {
            **initial_state,
            "start_time": start_time,
            "iteration": 0,
            "completed": False,
            "error": None,
        }
        
        self.log_info(
            f"Starting agent execution: {self.config.name}",
            agent_name=self.config.name,
            initial_state_keys=list(initial_state.keys())
        )
        
        try:
            # Validate initial state if enabled
            if self.config.enable_validation:
                validated_state = self.validate_state(state)
                state = validated_state.model_dump()
            
            # Run the graph
            result = await self.graph.ainvoke(state)
            
            # Mark as completed and add end time
            result.update({
                "completed": True,
                "end_time": datetime.now(),
            })
            
            final_state = self.validate_state(result)
            
            self.log_info(
                f"Agent execution completed: {self.config.name}",
                agent_name=self.config.name,
                duration_seconds=final_state.duration,
                iterations=final_state.iteration
            )
            
            return final_state
            
        except Exception as e:
            error_state = {
                **state,
                "error": str(e),
                "completed": False,
                "end_time": datetime.now(),
            }
            
            self.log_error(
                f"Agent execution failed: {self.config.name}",
                error=e,
                agent_name=self.config.name
            )
            
            return self.validate_state(error_state)
    
    def validate_config(self) -> bool:
        """
        Validate agent configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            AgentConfig(**self.config.model_dump())
            return True
        except Exception as e:
            self.log_error("Configuration validation failed", error=e)
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get agent information for debugging and monitoring.
        
        Returns:
            Dictionary with agent information
        """
        return {
            "name": self.config.name,
            "description": self.config.description,
            "type": self.__class__.__name__,
            "module": self.__class__.__module__,
            "config": self.config.model_dump(),
            "state_class": self.state_class.__name__,
            "graph_compiled": self._compiled_graph is not None,
        }


class SimpleAgent(BaseAgent[AgentState]):
    """
    Simple agent implementation for basic workflows.
    
    This class provides a simple implementation that can be used directly
    or as a starting point for more complex agents.
    """
    
    def __init__(self, config: AgentConfig, process_func: Optional[callable] = None):
        """
        Initialize simple agent.
        
        Args:
            config: Agent configuration
            process_func: Optional processing function
        """
        super().__init__(config)
        self._process_func = process_func
    
    def _build_graph(self) -> StateGraph:
        """Build a simple linear graph."""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("process", self._process_step)
        graph.add_node("finalize", self._finalize_step)
        
        # Add edges
        graph.add_edge("process", "finalize")
        graph.add_edge("finalize", END)
        
        # Set entry point
        graph.set_entry_point("process")
        
        return graph
    
    async def _process_step(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process step implementation."""
        self.log_debug("Processing step", iteration=state.get("iteration", 0))
        
        if self._process_func:
            result = await self._process_func(state)
            if isinstance(result, dict):
                state.update(result)
        
        state["iteration"] = state.get("iteration", 0) + 1
        return state
    
    async def _finalize_step(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Finalization step."""
        self.log_debug("Finalizing", iteration=state.get("iteration", 0))
        state["completed"] = True
        return state

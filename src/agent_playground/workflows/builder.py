"""Workflow builder for creating reusable agent workflows."""

from typing import Dict, List, Callable, Any, Optional, Union
from langgraph.graph import StateGraph, END
from ..core.base import BaseAgent, AgentState
from ..utils.logging import LoggingMixin


class WorkflowBuilder(LoggingMixin):
    """
    Fluent interface for building reusable workflows.
    
    Features:
    - Chainable method calls
    - Type-safe state management
    - Conditional routing
    - Error handling
    - Reusable workflow templates
    """
    
    def __init__(self, state_class: type = AgentState, name: str = "workflow"):
        """
        Initialize workflow builder.
        
        Args:
            state_class: State class to use for the workflow
            name: Name of the workflow for logging
        """
        self.name = name
        self.state_class = state_class
        self.graph = StateGraph(state_class)
        self.nodes: Dict[str, Callable] = {}
        self._entry_point: Optional[str] = None
        
        self.log_info(f"Initialized workflow builder: {name}")
    
    def add_step(self, name: str, func: Callable, **kwargs: Any) -> 'WorkflowBuilder':
        """
        Add a processing step to the workflow.
        
        Args:
            name: Step name
            func: Processing function
            **kwargs: Additional arguments for the function
            
        Returns:
            Self for chaining
        """
        async def wrapped_func(state):
            self.log_debug(f"Executing step: {name}", workflow=self.name, step=name)
            
            try:
                # Handle both sync and async functions
                if callable(func):
                    if hasattr(func, '__call__'):
                        result = func(state, **kwargs)
                        # Handle async functions
                        if hasattr(result, '__await__'):
                            result = await result
                    else:
                        result = func
                else:
                    result = func
                
                # Update state if result is a dictionary
                if isinstance(result, dict):
                    state.update(result)
                elif result is not None:
                    state['result'] = result
                
                self.log_debug(f"Completed step: {name}", workflow=self.name, step=name)
                return state
                
            except Exception as e:
                self.log_error(f"Step failed: {name}", error=e, workflow=self.name, step=name)
                return {**state, "error": str(e), "completed": False}
        
        self.nodes[name] = wrapped_func
        self.graph.add_node(name, wrapped_func)
        
        self.log_debug(f"Added step: {name}", workflow=self.name)
        return self
    
    def add_agent_step(self, name: str, agent: BaseAgent) -> 'WorkflowBuilder':
        """
        Add an agent as a workflow step.
        
        Args:
            name: Step name
            agent: Agent instance to add
            
        Returns:
            Self for chaining
        """
        async def agent_step(state):
            self.log_debug(f"Executing agent step: {name}", workflow=self.name, agent=agent.config.name)
            
            try:
                result = await agent.run(state)
                return result.model_dump()
            except Exception as e:
                self.log_error(f"Agent step failed: {name}", error=e, workflow=self.name, agent=agent.config.name)
                return {**state, "error": str(e), "completed": False}
        
        return self.add_step(name, agent_step)
    
    def add_lambda_step(self, name: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> 'WorkflowBuilder':
        """
        Add a simple lambda function as a step.
        
        Args:
            name: Step name
            func: Lambda function that takes and returns state dict
            
        Returns:
            Self for chaining
        """
        return self.add_step(name, func)
    
    def chain(self, from_step: str, to_step: str) -> 'WorkflowBuilder':
        """
        Chain two steps together.
        
        Args:
            from_step: Source step name
            to_step: Target step name
            
        Returns:
            Self for chaining
        """
        self.graph.add_edge(from_step, to_step)
        self.log_debug(f"Added edge: {from_step} -> {to_step}", workflow=self.name)
        return self
    
    def chain_to_end(self, step: str) -> 'WorkflowBuilder':
        """
        Chain a step to the end of the workflow.
        
        Args:
            step: Step name to chain to end
            
        Returns:
            Self for chaining
        """
        self.graph.add_edge(step, END)
        self.log_debug(f"Added edge to END: {step}", workflow=self.name)
        return self
    
    def branch(self, from_step: str, condition: Callable, branches: Dict[str, str]) -> 'WorkflowBuilder':
        """
        Add conditional branching.
        
        Args:
            from_step: Source step name
            condition: Function that determines which branch to take
            branches: Mapping of condition results to target steps
            
        Returns:
            Self for chaining
        """
        def wrapped_condition(state):
            try:
                result = condition(state)
                self.log_debug(f"Branch condition result: {result}", workflow=self.name, step=from_step)
                return result
            except Exception as e:
                self.log_error(f"Branch condition failed", error=e, workflow=self.name, step=from_step)
                return "error"  # Default error branch
        
        self.graph.add_conditional_edges(from_step, wrapped_condition, branches)
        self.log_debug(f"Added conditional edges from: {from_step}", workflow=self.name, branches=list(branches.keys()))
        return self
    
    def start_with(self, step_name: str) -> 'WorkflowBuilder':
        """
        Set the entry point of the workflow.
        
        Args:
            step_name: Name of the starting step
            
        Returns:
            Self for chaining
        """
        self._entry_point = step_name
        self.graph.set_entry_point(step_name)
        self.log_debug(f"Set entry point: {step_name}", workflow=self.name)
        return self
    
    def build(self) -> StateGraph:
        """
        Build and compile the workflow.
        
        Returns:
            Compiled StateGraph
            
        Raises:
            ValueError: If no entry point is set
        """
        if not self._entry_point:
            raise ValueError("Must set entry point with start_with()")
        
        self.log_info(f"Building workflow: {self.name}", steps=list(self.nodes.keys()), entry_point=self._entry_point)
        
        return self.graph.compile()
    
    @classmethod
    def sequential(
        cls, 
        steps: List[tuple[str, Callable]], 
        state_class: type = AgentState,
        name: str = "sequential_workflow"
    ) -> StateGraph:
        """
        Create a simple sequential workflow.
        
        Args:
            steps: List of (name, function) tuples
            state_class: State class to use
            name: Workflow name
            
        Returns:
            Compiled StateGraph
        """
        builder = cls(state_class, name)
        
        for i, (step_name, func) in enumerate(steps):
            builder.add_step(step_name, func)
            
            if i > 0:
                builder.chain(steps[i-1][0], step_name)
        
        if steps:
            builder.start_with(steps[0][0])
            builder.chain_to_end(steps[-1][0])
        
        return builder.build()
    
    @classmethod
    def parallel_then_merge(
        cls,
        parallel_steps: List[tuple[str, Callable]],
        merge_step: tuple[str, Callable],
        state_class: type = AgentState,
        name: str = "parallel_workflow"
    ) -> StateGraph:
        """
        Create a workflow that runs steps in parallel then merges.
        
        Args:
            parallel_steps: List of (name, function) tuples to run in parallel
            merge_step: (name, function) tuple for merging results
            state_class: State class to use
            name: Workflow name
            
        Returns:
            Compiled StateGraph
        """
        builder = cls(state_class, name)
        
        # Add all parallel steps
        for step_name, func in parallel_steps:
            builder.add_step(step_name, func)
        
        # Add merge step
        merge_name, merge_func = merge_step
        builder.add_step(merge_name, merge_func)
        
        # Connect all parallel steps to merge step
        for step_name, _ in parallel_steps:
            builder.chain(step_name, merge_name)
        
        # Set first parallel step as entry point
        if parallel_steps:
            builder.start_with(parallel_steps[0][0])
        
        builder.chain_to_end(merge_name)
        
        return builder.build()
    
    @classmethod
    def conditional_workflow(
        cls,
        initial_step: tuple[str, Callable],
        condition_step: tuple[str, Callable],
        branches: Dict[str, List[tuple[str, Callable]]],
        final_step: Optional[tuple[str, Callable]] = None,
        state_class: type = AgentState,
        name: str = "conditional_workflow"
    ) -> StateGraph:
        """
        Create a workflow with conditional branching.
        
        Args:
            initial_step: (name, function) for initial step
            condition_step: (name, function) that returns branch key
            branches: Map of branch keys to list of steps
            final_step: Optional final merge step
            state_class: State class to use
            name: Workflow name
            
        Returns:
            Compiled StateGraph
        """
        builder = cls(state_class, name)
        
        # Add initial step
        init_name, init_func = initial_step
        builder.add_step(init_name, init_func)
        
        # Add condition step
        cond_name, cond_func = condition_step
        builder.add_step(cond_name, cond_func)
        
        # Chain initial to condition
        builder.chain(init_name, cond_name)
        
        # Add branch steps
        branch_mapping = {}
        for branch_key, branch_steps in branches.items():
            for i, (step_name, func) in enumerate(branch_steps):
                builder.add_step(step_name, func)
                
                if i > 0:
                    builder.chain(branch_steps[i-1][0], step_name)
            
            if branch_steps:
                branch_mapping[branch_key] = branch_steps[0][0]
                
                # Connect to final step or END
                if final_step:
                    builder.chain(branch_steps[-1][0], final_step[0])
                else:
                    builder.chain_to_end(branch_steps[-1][0])
        
        # Add conditional edges
        def condition_router(state):
            return cond_func(state)
        
        builder.branch(cond_name, condition_router, branch_mapping)
        
        # Add final step if provided
        if final_step:
            final_name, final_func = final_step
            builder.add_step(final_name, final_func)
            builder.chain_to_end(final_name)
        
        builder.start_with(init_name)
        
        return builder.build()

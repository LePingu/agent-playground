"""
Agent Playground - Reusable AI Agent Framework.

A modular framework for building AI agents using LangGraph and LangChain,
with specialized support for Source of Wealth verification workflows.
"""

__version__ = "0.1.0"
__author__ = "Agent Playground Team"
__description__ = "Reusable AI Agent Framework with LangGraph"

from .core import BaseAgent, AgentConfig, AgentState, AgentRegistry
from .workflows import WorkflowBuilder
from .utils import get_settings, setup_logging

__all__ = [
    # Core components
    "BaseAgent",
    "AgentConfig", 
    "AgentState",
    "AgentRegistry",
    # Workflows
    "WorkflowBuilder",
    # Utilities
    "get_settings",
    "setup_logging",
    # Version info
    "__version__",
    "__author__",
    "__description__",
]

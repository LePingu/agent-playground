"""Core components for the Agent Playground framework."""

from .base import BaseAgent, AgentConfig, AgentState, SimpleAgent
from .registry import AgentRegistry, agent_registry

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentConfig", 
    "AgentState",
    "SimpleAgent",
    # Registry
    "AgentRegistry",
    "agent_registry",
]

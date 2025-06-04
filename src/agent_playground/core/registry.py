"""Agent registry for managing and creating agent instances."""

from typing import Dict, Type, Optional, Any, List
from .base import BaseAgent, AgentConfig, AgentState
from ..utils.logging import LoggingMixin


class AgentRegistry(LoggingMixin):
    """
    Registry for managing reusable agents.
    
    Enables:
    - Dynamic agent discovery
    - Factory pattern for agent creation
    - Configuration management
    - Plugin-style architecture
    """
    
    def __init__(self):
        """Initialize the agent registry."""
        self._agents: Dict[str, Type[BaseAgent]] = {}
        self._configs: Dict[str, AgentConfig] = {}
        self._instances: Dict[str, BaseAgent] = {}
        
        self.log_info("Agent registry initialized")
    
    def register(
        self, 
        name: str, 
        agent_class: Type[BaseAgent], 
        config: AgentConfig,
        singleton: bool = False
    ) -> None:
        """
        Register a new agent type.
        
        Args:
            name: Unique name for the agent
            agent_class: Agent class to register
            config: Default configuration for the agent
            singleton: If True, only one instance will be created and reused
        """
        if name in self._agents:
            self.log_warning(f"Overriding existing agent registration: {name}")
        
        self._agents[name] = agent_class
        self._configs[name] = config
        
        # Store singleton flag in config metadata
        if hasattr(config, 'metadata'):
            config.metadata = config.metadata or {}
        else:
            config.metadata = {}
        config.metadata['singleton'] = singleton
        
        self.log_info(
            f"Registered agent: {name}", 
            agent_class=agent_class.__name__,
            singleton=singleton
        )
    
    def create(self, name: str, **config_overrides: Any) -> BaseAgent:
        """
        Create an agent instance with optional config overrides.
        
        Args:
            name: Name of the registered agent
            **config_overrides: Configuration overrides
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If agent is not registered
        """
        if name not in self._agents:
            available = list(self._agents.keys())
            raise ValueError(f"Agent '{name}' not registered. Available: {available}")
        
        base_config = self._configs[name]
        is_singleton = base_config.metadata.get('singleton', False)
        
        # Return existing instance if singleton
        if is_singleton and name in self._instances:
            self.log_debug(f"Returning existing singleton instance: {name}")
            return self._instances[name]
        
        # Create new configuration with overrides
        config_dict = base_config.model_dump()
        config_dict.update(config_overrides)
        new_config = AgentConfig(**config_dict)
        
        # Create new instance
        agent_class = self._agents[name]
        instance = agent_class(new_config)
        
        # Store singleton instance
        if is_singleton:
            self._instances[name] = instance
        
        self.log_info(
            f"Created agent instance: {name}",
            agent_class=agent_class.__name__,
            overrides=list(config_overrides.keys()) if config_overrides else None
        )
        
        return instance
    
    def get_or_create(self, name: str, **config_overrides: Any) -> BaseAgent:
        """
        Get existing instance or create new one.
        
        Args:
            name: Name of the registered agent
            **config_overrides: Configuration overrides
            
        Returns:
            Agent instance
        """
        if name in self._instances:
            return self._instances[name]
        
        return self.create(name, **config_overrides)
    
    def list_agents(self) -> List[str]:
        """
        List all registered agent names.
        
        Returns:
            List of agent names
        """
        return list(self._agents.keys())
    
    def get_config(self, name: str) -> Optional[AgentConfig]:
        """
        Get the configuration for a registered agent.
        
        Args:
            name: Agent name
            
        Returns:
            Agent configuration or None if not found
        """
        return self._configs.get(name)
    
    def get_agent_class(self, name: str) -> Optional[Type[BaseAgent]]:
        """
        Get the agent class for a registered agent.
        
        Args:
            name: Agent name
            
        Returns:
            Agent class or None if not found
        """
        return self._agents.get(name)
    
    def unregister(self, name: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            name: Agent name to unregister
            
        Returns:
            True if agent was unregistered, False if not found
        """
        if name not in self._agents:
            return False
        
        # Clean up
        del self._agents[name]
        del self._configs[name]
        if name in self._instances:
            del self._instances[name]
        
        self.log_info(f"Unregistered agent: {name}")
        return True
    
    def clear(self) -> None:
        """Clear all registered agents."""
        agent_count = len(self._agents)
        self._agents.clear()
        self._configs.clear()
        self._instances.clear()
        
        self.log_info(f"Cleared {agent_count} registered agents")
    
    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get information about the registry.
        
        Returns:
            Dictionary with registry information
        """
        return {
            "total_registered": len(self._agents),
            "total_instances": len(self._instances),
            "agents": {
                name: {
                    "class": agent_class.__name__,
                    "module": agent_class.__module__,
                    "config": config.model_dump(),
                    "has_instance": name in self._instances,
                }
                for name, (agent_class, config) in zip(
                    self._agents.keys(),
                    zip(self._agents.values(), self._configs.values())
                )
            }
        }
    
    def register_from_module(self, module_path: str) -> int:
        """
        Auto-register agents from a module.
        
        Args:
            module_path: Python module path
            
        Returns:
            Number of agents registered
        """
        import importlib
        
        try:
            module = importlib.import_module(module_path)
            registered_count = 0
            
            # Look for agent classes and configurations
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Check if it's an agent class
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseAgent) and 
                    attr != BaseAgent):
                    
                    # Look for corresponding config
                    config_name = f"{attr_name.replace('Agent', '')}Config"
                    if hasattr(module, config_name):
                        config_class = getattr(module, config_name)
                        if isinstance(config_class, type) and issubclass(config_class, AgentConfig):
                            # Create default config and register
                            default_config = config_class(name=attr_name.lower())
                            self.register(attr_name.lower(), attr, default_config)
                            registered_count += 1
            
            self.log_info(f"Auto-registered {registered_count} agents from {module_path}")
            return registered_count
            
        except Exception as e:
            self.log_error(f"Failed to auto-register from {module_path}", error=e)
            return 0


# Global registry instance
agent_registry = AgentRegistry()

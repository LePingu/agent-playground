"""Unit tests for core agent functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from agent_playground.core.base import BaseAgent, AgentConfig, AgentState, SimpleAgent
from agent_playground.core.registry import AgentRegistry
from langgraph.graph import StateGraph


class TestAgent(BaseAgent[AgentState]):
    """Test agent implementation."""
    
    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("test_step", self._process_step)
        graph.set_entry_point("test_step")
        graph.add_edge("test_step", "__end__")
        return graph
    
    async def _process_step(self, state):
        return {**state, "test_completed": True, "iteration": state.get("iteration", 0) + 1}


class TestAgentConfig:
    """Test AgentConfig functionality."""
    
    def test_agent_config_creation(self):
        """Test creating agent configuration."""
        config = AgentConfig(
            name="test_agent",
            description="Test agent",
            max_iterations=5,
            temperature=0.5,
        )
        
        assert config.name == "test_agent"
        assert config.description == "Test agent"
        assert config.max_iterations == 5
        assert config.temperature == 0.5
        assert config.model_name == "gpt-4"  # default
    
    def test_agent_config_validation(self):
        """Test agent configuration validation."""
        # Valid config
        config = AgentConfig(name="test", temperature=0.5)
        assert config.temperature == 0.5
        
        # Invalid temperature
        with pytest.raises(ValueError):
            AgentConfig(name="test", temperature=3.0)  # > 2.0
        
        # Invalid max_iterations
        with pytest.raises(ValueError):
            AgentConfig(name="test", max_iterations=0)  # < 1


class TestAgentState:
    """Test AgentState functionality."""
    
    def test_agent_state_creation(self, test_agent_state):
        """Test creating agent state."""
        assert test_agent_state.iteration == 0
        assert not test_agent_state.completed
        assert test_agent_state.error is None
        assert test_agent_state.context == {"test": True}
    
    def test_agent_state_duration(self):
        """Test duration calculation."""
        from datetime import datetime, timedelta
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=5)
        
        state = AgentState(start_time=start_time, end_time=end_time)
        assert abs(state.duration - 5.0) < 0.1


class TestBaseAgent:
    """Test BaseAgent functionality."""
    
    def test_agent_initialization(self, test_agent_config):
        """Test agent initialization."""
        agent = TestAgent(test_agent_config)
        
        assert agent.config.name == "test_agent"
        assert agent.state_class == AgentState
        assert agent._graph is None  # Lazy loading
    
    def test_agent_graph_building(self, test_agent_config):
        """Test agent graph building."""
        agent = TestAgent(test_agent_config)
        
        # Graph should be built lazily
        graph = agent.graph
        assert graph is not None
        assert agent._compiled_graph is not None
    
    @pytest.mark.asyncio
    async def test_agent_execution(self, test_agent_config, sample_state_data):
        """Test agent execution."""
        agent = TestAgent(test_agent_config)
        
        result = await agent.run(sample_state_data)
        
        assert isinstance(result, AgentState)
        assert result.completed
        assert result.test_completed
        assert result.iteration == 1
        assert result.client_id == "test_123"
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self, test_agent_config):
        """Test agent error handling."""
        class FailingAgent(BaseAgent[AgentState]):
            def _build_graph(self) -> StateGraph:
                graph = StateGraph(AgentState)
                graph.add_node("fail_step", self._process_step)
                graph.set_entry_point("fail_step")
                graph.add_edge("fail_step", "__end__")
                return graph
            
            async def _process_step(self, state):
                raise ValueError("Test error")
        
        agent = FailingAgent(test_agent_config)
        result = await agent.run({"test": True})
        
        assert isinstance(result, AgentState)
        assert not result.completed
        assert result.error == "Test error"
    
    def test_agent_validation(self, test_agent_config):
        """Test agent configuration validation."""
        agent = TestAgent(test_agent_config)
        assert agent.validate_config()
    
    def test_agent_info(self, test_agent_config):
        """Test agent info retrieval."""
        agent = TestAgent(test_agent_config)
        info = agent.get_info()
        
        assert info["name"] == "test_agent"
        assert info["type"] == "TestAgent"
        assert "config" in info
        assert "state_class" in info


class TestSimpleAgent:
    """Test SimpleAgent functionality."""
    
    def test_simple_agent_creation(self, test_agent_config):
        """Test simple agent creation."""
        def process_func(state):
            return {"processed": True}
        
        agent = SimpleAgent(test_agent_config, process_func)
        assert agent._process_func == process_func
    
    @pytest.mark.asyncio
    async def test_simple_agent_execution(self, test_agent_config):
        """Test simple agent execution."""
        def process_func(state):
            return {"processed": True, "data": "test_data"}
        
        agent = SimpleAgent(test_agent_config, process_func)
        result = await agent.run({"input": "test"})
        
        assert result.completed
        assert result.processed
        assert result.data == "test_data"


class TestAgentRegistry:
    """Test AgentRegistry functionality."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = AgentRegistry()
        assert len(registry.list_agents()) == 0
    
    def test_agent_registration(self, test_agent_config):
        """Test agent registration."""
        registry = AgentRegistry()
        
        registry.register("test_agent", TestAgent, test_agent_config)
        
        assert "test_agent" in registry.list_agents()
        assert registry.get_config("test_agent") == test_agent_config
        assert registry.get_agent_class("test_agent") == TestAgent
    
    def test_agent_creation(self, test_agent_config):
        """Test agent creation from registry."""
        registry = AgentRegistry()
        registry.register("test_agent", TestAgent, test_agent_config)
        
        agent = registry.create("test_agent")
        assert isinstance(agent, TestAgent)
        assert agent.config.name == "test_agent"
    
    def test_agent_creation_with_overrides(self, test_agent_config):
        """Test agent creation with config overrides."""
        registry = AgentRegistry()
        registry.register("test_agent", TestAgent, test_agent_config)
        
        agent = registry.create("test_agent", temperature=0.8, max_iterations=20)
        assert agent.config.temperature == 0.8
        assert agent.config.max_iterations == 20
    
    def test_singleton_agent(self, test_agent_config):
        """Test singleton agent creation."""
        registry = AgentRegistry()
        registry.register("singleton_agent", TestAgent, test_agent_config, singleton=True)
        
        agent1 = registry.create("singleton_agent")
        agent2 = registry.create("singleton_agent")
        
        assert agent1 is agent2  # Same instance
    
    def test_registry_info(self, test_agent_config):
        """Test registry information retrieval."""
        registry = AgentRegistry()
        registry.register("test_agent", TestAgent, test_agent_config)
        
        info = registry.get_registry_info()
        assert info["total_registered"] == 1
        assert "test_agent" in info["agents"]
    
    def test_agent_unregistration(self, test_agent_config):
        """Test agent unregistration."""
        registry = AgentRegistry()
        registry.register("test_agent", TestAgent, test_agent_config)
        
        assert registry.unregister("test_agent")
        assert "test_agent" not in registry.list_agents()
        assert not registry.unregister("nonexistent_agent")
    
    def test_registry_clear(self, test_agent_config):
        """Test registry clearing."""
        registry = AgentRegistry()
        registry.register("test_agent1", TestAgent, test_agent_config)
        registry.register("test_agent2", TestAgent, test_agent_config)
        
        registry.clear()
        assert len(registry.list_agents()) == 0

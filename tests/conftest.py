"""Test configuration and fixtures for Agent Playground."""

import pytest
import asyncio
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import MagicMock

from agent_playground.utils.config import Settings
from agent_playground.core.base import AgentConfig, AgentState


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Provide test settings."""
    return Settings(
        environment="test",
        debug=True,
        data_dir=Path("test_data"),
        reports_dir=Path("test_reports"),
        memory_bank_dir=Path("test_memory"),
        model=Settings.ModelConfig(
            openrouter_model="mock/gpt-4",
            temperature=0.0,
            max_tokens=100,
        ),
        agent=Settings.AgentConfig(
            max_iterations=3,
            timeout=30,
            retry_attempts=1,
        ),
        logging=Settings.LoggingConfig(
            log_level="DEBUG",
            log_format="simple",
        ),
    )


@pytest.fixture
def test_agent_config() -> AgentConfig:
    """Provide test agent configuration."""
    return AgentConfig(
        name="test_agent",
        description="Test agent for unit tests",
        max_iterations=3,
        timeout=30,
        model_name="mock/gpt-4",
        temperature=0.0,
    )


@pytest.fixture
def test_agent_state() -> AgentState:
    """Provide test agent state."""
    return AgentState(
        messages=[],
        context={"test": True},
        metadata={"test_run": True},
    )


@pytest.fixture
def mock_llm():
    """Provide a mock LLM for testing."""
    mock = MagicMock()
    mock.ainvoke.return_value = "Mock response"
    mock.invoke.return_value = "Mock response"
    return mock


@pytest.fixture
def sample_state_data() -> Dict[str, Any]:
    """Provide sample state data for testing."""
    return {
        "client_id": "test_123",
        "client_name": "Test Client",
        "messages": [],
        "context": {"test_mode": True},
        "metadata": {"created_by": "test"},
        "iteration": 0,
        "completed": False,
    }


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide temporary directory for tests."""
    return tmp_path


@pytest.fixture(autouse=True)
def setup_test_environment(test_settings: Settings, monkeypatch):
    """Set up test environment for all tests."""
    # Mock the settings function to return test settings
    monkeypatch.setattr("agent_playground.utils.config.get_settings", lambda: test_settings)
    
    # Create test directories
    test_settings.data_dir.mkdir(parents=True, exist_ok=True)
    test_settings.reports_dir.mkdir(parents=True, exist_ok=True)
    test_settings.memory_bank_dir.mkdir(parents=True, exist_ok=True)

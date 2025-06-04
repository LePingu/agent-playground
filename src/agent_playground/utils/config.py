"""Configuration management for Agent Playground."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class ModelConfig(BaseSettings):
    """Model-specific configuration."""
    
    # OpenRouter configuration
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field("openai/gpt-4-turbo", env="OPENROUTER_MODEL")
    openrouter_base_url: str = Field("https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")
    
    # Ollama configuration
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field("llama3", env="OLLAMA_MODEL")
    
    # OpenAI configuration (fallback)
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4", env="OPENAI_MODEL")
    
    # Model parameters
    temperature: float = Field(0.1, env="MODEL_TEMPERATURE", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, env="MODEL_MAX_TOKENS", gt=0)
    
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}


class TracingConfig(BaseSettings):
    """Tracing and observability configuration."""
    
    # LangSmith configuration
    langsmith_tracing: bool = Field(False, env="LANGSMITH_TRACING")
    langsmith_endpoint: str = Field("https://api.smith.langchain.com", env="LANGSMITH_ENDPOINT")
    langsmith_api_key: Optional[str] = Field(None, env="LANGSMITH_API_KEY")
    langsmith_project: str = Field("agent-playground", env="LANGSMITH_PROJECT")
    
    # Local tracing
    enable_tracing: bool = Field(True, env="ENABLE_TRACING")
    trace_output_dir: Path = Field(Path("traces"), env="TRACE_OUTPUT_DIR")
    
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}


class AgentConfig(BaseSettings):
    """General agent configuration."""
    
    # Agent behavior
    max_iterations: int = Field(10, env="MAX_ITERATIONS", ge=1, le=100)
    timeout: int = Field(300, env="TIMEOUT", ge=1)
    retry_attempts: int = Field(3, env="RETRY_ATTEMPTS", ge=0)
    
    # Workflow configuration
    enable_human_in_loop: bool = Field(True, env="ENABLE_HUMAN_IN_LOOP")
    parallel_execution: bool = Field(True, env="PARALLEL_EXECUTION")
    
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("detailed", env="LOG_FORMAT")  # simple, detailed, json
    log_file: Optional[Path] = Field(None, env="LOG_FILE")
    log_rotation: str = Field("1 day", env="LOG_ROTATION")
    log_retention: str = Field("30 days", env="LOG_RETENTION")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v):
        valid_formats = ["simple", "detailed", "json"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Log format must be one of {valid_formats}")
        return v.lower()
    
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    
    # Application info
    app_name: str = Field("Agent Playground", env="APP_NAME")
    app_version: str = Field("0.1.0", env="APP_VERSION")
    
    # Data directories
    data_dir: Path = Field(Path("data"), env="DATA_DIR")
    reports_dir: Path = Field(Path("reports"), env="REPORTS_DIR")
    memory_bank_dir: Path = Field(Path("memory-bank"), env="MEMORY_BANK_DIR")
    
    # Sub-configurations
    model: ModelConfig = Field(default_factory=ModelConfig)
    tracing: TracingConfig = Field(default_factory=TracingConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    @field_validator("data_dir", "reports_dir", "memory_bank_dir", mode="before")
    @classmethod
    def ensure_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
    
    def model_post_init(self, __context: Any) -> None:
        """Create directories if they don't exist."""
        for dir_attr in ["data_dir", "reports_dir", "memory_bank_dir"]:
            dir_path = getattr(self, dir_attr)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache()
def get_settings(env_file: Optional[str] = None) -> Settings:
    """
    Get cached application settings.
    
    Args:
        env_file: Optional path to environment file
        
    Returns:
        Settings instance
    """
    if env_file:
        return Settings(_env_file=env_file)
    
    # Try multiple env file locations
    env_files = [
        Path(".env"),
        Path("env/.env"),
        Path("config/.env"),
    ]
    
    for env_file_path in env_files:
        if env_file_path.exists():
            return Settings(_env_file=str(env_file_path))
    
    # Fall back to environment variables only
    return Settings()


def get_env_info() -> Dict[str, Any]:
    """Get environment information for debugging."""
    settings = get_settings()
    
    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "python_version": os.sys.version,
        "working_directory": os.getcwd(),
        "env_files_checked": [
            str(Path(".env").absolute()),
            str(Path("env/.env").absolute()),
            str(Path("config/.env").absolute()),
        ],
        "env_files_exist": [
            Path(".env").exists(),
            Path("env/.env").exists(), 
            Path("config/.env").exists(),
        ],
    }

"""Logging utilities for Agent Playground."""

import sys
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger
from .config import get_settings, LoggingConfig


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """
    Set up logging configuration using loguru.
    
    Args:
        config: Optional logging configuration. If None, uses settings from config.
    """
    if config is None:
        settings = get_settings()
        config = settings.logging
    
    # Remove default logger
    logger.remove()
    
    # Configure format based on config
    if config.log_format == "json":
        format_string = "{time} | {level} | {name}:{function}:{line} | {message}"
        serialize = True
    elif config.log_format == "detailed":
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        serialize = False
    else:  # simple
        format_string = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        serialize = False
    
    # Add console handler
    logger.add(
        sys.stderr,
        format=format_string,
        level=config.log_level,
        colorize=not serialize,
        serialize=serialize,
    )
    
    # Add file handler if specified
    if config.log_file:
        log_file_path = Path(config.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            str(log_file_path),
            format=format_string,
            level=config.log_level,
            rotation=config.log_rotation,
            retention=config.log_retention,
            serialize=serialize,
            enqueue=True,  # Thread-safe logging
        )
    
    # Set up structured logging
    logger.configure(
        handlers=[
            {
                "sink": sys.stderr,
                "format": format_string,
                "level": config.log_level,
                "colorize": not serialize,
                "serialize": serialize,
            }
        ]
    )


def get_logger(name: str) -> "logger":
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)


def log_agent_execution(
    agent_name: str,
    action: str,
    duration: Optional[float] = None,
    **kwargs: Any
) -> None:
    """
    Log agent execution with structured data.
    
    Args:
        agent_name: Name of the agent
        action: Action being performed
        duration: Optional execution duration in seconds
        **kwargs: Additional structured data to log
    """
    log_data = {
        "agent": agent_name,
        "action": action,
        **kwargs
    }
    
    if duration is not None:
        log_data["duration_seconds"] = duration
    
    logger.info(f"Agent execution: {action}", **log_data)


def log_workflow_step(
    workflow_name: str,
    step_name: str,
    status: str,
    **kwargs: Any
) -> None:
    """
    Log workflow step execution.
    
    Args:
        workflow_name: Name of the workflow
        step_name: Name of the step
        status: Status (started, completed, failed, etc.)
        **kwargs: Additional structured data
    """
    log_data = {
        "workflow": workflow_name,
        "step": step_name,
        "status": status,
        **kwargs
    }
    
    if status == "failed":
        logger.error(f"Workflow step failed: {step_name}", **log_data)
    elif status == "completed":
        logger.info(f"Workflow step completed: {step_name}", **log_data)
    else:
        logger.debug(f"Workflow step {status}: {step_name}", **log_data)


def log_error(
    error: Exception,
    context: str,
    **kwargs: Any
) -> None:
    """
    Log an error with context and structured data.
    
    Args:
        error: The exception that occurred
        context: Context where the error occurred
        **kwargs: Additional structured data
    """
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        **kwargs
    }
    
    logger.error(f"Error in {context}: {error}", **log_data)


class LoggingMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> "logger":
        """Get a logger instance for this class."""
        if not hasattr(self, '_logger'):
            class_name = self.__class__.__name__
            module_name = self.__class__.__module__
            self._logger = logger.bind(name=f"{module_name}.{class_name}")
        return self._logger
    
    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log an info message with structured data."""
        self.logger.info(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message with structured data."""
        self.logger.warning(message, **kwargs)
    
    def log_error(self, message: str, error: Optional[Exception] = None, **kwargs: Any) -> None:
        """Log an error message with optional exception and structured data."""
        if error:
            kwargs.update({
                "error_type": type(error).__name__,
                "error_message": str(error),
            })
        self.logger.error(message, **kwargs)
    
    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message with structured data."""
        self.logger.debug(message, **kwargs)

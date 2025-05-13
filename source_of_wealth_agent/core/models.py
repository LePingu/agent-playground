"""
Language model initialization and configuration for the Source of Wealth Agent system.
"""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM


def initialize_openrouter_model(
    model_name: str = "qwen/qwen3-110b",
    api_key: Optional[str] = None,
    temperature: float = 0.1,
) -> ChatOpenAI:
    """
    Initialize an OpenRouter-based model.
    
    Args:
        model_name: The name of the model to use
        api_key: The API key for OpenRouter (if None, uses environment variables)
        temperature: Controls randomness in outputs (0.0 to 1.0)
        
    Returns:
        Configured ChatOpenAI instance
    """
    if api_key is None:
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        
    return ChatOpenAI(
        model=model_name,
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=api_key,
        temperature=temperature
    )


def initialize_ollama_model(
    model_name: str = "mistral-small3.1",
    base_url: str = "http://[ip]:11434",
    temperature: float = 0.1,
) -> OllamaLLM:
    """
    Initialize a local Ollama model.
    
    Args:
        model_name: The name of the model to use
        base_url: URL for the Ollama instance
        temperature: Controls randomness in outputs (0.0 to 1.0)
        
    Returns:
        Configured OllamaLLM instance
    """
    return OllamaLLM(
        model=model_name,
        base_url=base_url,
        temperature=temperature
    )
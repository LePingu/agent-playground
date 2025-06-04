#!/usr/bin/env python3
"""Main entry point for your Agent Playground project."""

import asyncio
from agent_playground import get_settings, setup_logging

async def main():
    """Main function."""
    settings = get_settings()
    setup_logging()
    
    print(f"Agent Playground project initialized!")
    print(f"Environment: {settings.environment}")

if __name__ == "__main__":
    asyncio.run(main())

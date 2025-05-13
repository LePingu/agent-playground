#!/usr/bin/env python3
"""
Basic test of the summarization agent.
"""

import sys
import os
print(f"Python Version: {sys.version}")
print(f"Current Directory: {os.getcwd()}")
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Parent Directory: {parent_dir}")
print(f"Files in parent directory: {os.listdir(parent_dir)}")
print(f"Files in source_of_wealth_agent: {os.listdir(os.path.join(parent_dir, 'source_of_wealth_agent'))}")
print(f"Files in agents directory: {os.listdir(os.path.join(parent_dir, 'source_of_wealth_agent/agents'))}")
# Adjust path to include parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Starting test")
try:
    from source_of_wealth_agent.agents.summarization_agent import summarization_agent
    print("Successfully imported summarization agent")
except Exception as e:
    print(f"Error importing summarization_agent: {str(e)}")
    import traceback
    traceback.print_exc()

print("Import test complete")

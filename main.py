#!/usr/bin/env python3
"""
Main entry point for the Source of Wealth Agent system.
Run this script to execute the workflow with configuration from environment variables.

Usage:
    python main.py [--trace] [--use-config] [--graph {main,verification_only}]

Options:
    --trace         Enable tracing and visualization
    --use-config    Use LangGraph JSON configuration
    --graph         Select which graph to use from the configuration

Environment variables (in env/.env file):
    CLIENT_ID                Client identifier
    CLIENT_NAME              Client name
    OPENROUTER_API_KEY       API key for OpenRouter
    OPENROUTER_MODEL         Model name for OpenRouter
    OLLAMA_BASE_URL          Base URL for Ollama API
    OLLAMA_MODEL             Model name for Ollama
    LANGSMITH_TRACING     Enable LangChain tracing (true/false)
    LANGSMITH_ENDPOINT       LangChain API endpoint
    LANGSMITH_API_KEY        API key for LangChain
    LANGSMITH_PROJECT        LangChain project name
"""

import os
import sys
import json
import argparse
from typing import Dict, Optional
from dotenv import load_dotenv
import asyncio

# Add the project root to the path
sys.path.append(os.path.abspath('.'))

# Import workflow modules
from source_of_wealth_agent.core.models import initialize_openrouter_model, initialize_ollama_model
from source_of_wealth_agent.workflow.runner import run_workflow


def load_environment() -> Dict[str, str]:
    """
    Load environment variables from .env file.
    
    Returns:
        Dictionary of environment variables
    """
    # Try to load from env/.env file
    env_path = os.path.join(os.path.dirname(__file__), 'env', '.env')
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ Loaded environment from {env_path}")
    else:
        print(f"⚠️ No .env file found at {env_path}, using existing environment variables")
    
    return {
        'client_id': os.getenv('CLIENT_ID', '12345'),
        'client_name': os.getenv('CLIENT_NAME', 'John Doe'),
        'openrouter_api_key': os.getenv('OPENROUTER_API_KEY'),
        'openrouter_model': os.getenv('OPENROUTER_MODEL', 'openai/gpt-4-turbo'),
        'ollama_base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
        'ollama_model': os.getenv('OLLAMA_MODEL', 'openhermes'),
        'langchain_tracing': os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true'
    }


def setup_langchain_tracing():
    """Configure LangChain tracing based on environment variables."""
    if os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true':
        os.environ['LANGSMITH_TRACING'] = 'true'
        
        # Set other LangChain environment variables if they exist
        for var in ['LANGSMITH_ENDPOINT', 'LANGSMITH_API_KEY', 'LANGSMITH_PROJECT']:
            if os.getenv(var):
                os.environ[var] = os.getenv(var)
                
        print("🔍 LangChain tracing enabled")
    else:
        os.environ['LANGSMITH_TRACING'] = 'false'
        print("ℹ️ LangChain tracing disabled")


async def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Source of Wealth Agent system')
    parser.add_argument('--trace', action='store_true', help='Enable tracing and visualization')
    parser.add_argument('--use-config', action='store_true', help='Use LangGraph JSON configuration')
    parser.add_argument('--graph', choices=['main', 'verification_only'], 
                      default='main', help='Which graph to use from the configuration')
    parser.add_argument('--import-state', type=str, help='Import state from this file')
    parser.add_argument('--export-state', type=str, default='output_state.json', help='Export state to this file')
    parser.add_argument('--client_id', type=str, help='Client ID override')
    parser.add_argument('--client_name', type=str, help='Client name override')
    args = parser.parse_args()
    
    # Load environment variables
    env = load_environment()
    
    # Setup LangChain tracing
    setup_langchain_tracing()
    
    print("\n=== Source of Wealth Verification System ===\n")
    print(f"Client: {env['client_name']} (ID: {env['client_id']})")
    print(f"OpenRouter Model: {env['openrouter_model']}")
    print(f"Ollama Model: {env['ollama_model']} @ {env['ollama_base_url']}")
    print(f"Tracing: {'Enabled' if args.trace or env['langchain_tracing'] else 'Disabled'}")
    print("\n" + "="*45 + "\n")
    
    # Initialize models
    try:
        openrouter_model = initialize_openrouter_model(
            model_name=env['openrouter_model'],
            api_key=env['openrouter_api_key'],
            temperature=0.1
        )
        
        ollama_model = initialize_ollama_model(
            model_name=env['ollama_model'],
            base_url=env['ollama_base_url'],
            temperature=0.1
        )
        
        # Check if we should use the LangGraph JSON configuration
        use_config = args.use_config
        config_path = os.path.join(os.path.dirname(__file__), 'source_of_wealth_agent', 'langgraph.json')
        graph_name = args.graph
        
        if use_config and os.path.exists(config_path):
            print(f"📋 Using LangGraph configuration from: {config_path}")
            print(f"🔄 Selected graph: {graph_name}")
            
            # Import here to avoid dependencies if not using config
            from langgraph.graph import Graph
            import json
            
            try:
                # Load the graph configuration
                with open(config_path, 'r') as f:
                    graph_config = json.load(f)
                
                # Check if the requested graph exists
                if "graphs" in graph_config and graph_name in graph_config["graphs"]:
                    selected_graph = graph_config["graphs"][graph_name]
                    print(f"✅ Successfully loaded LangGraph configuration")
                    print(f"📊 Graph: {selected_graph['description']}")
                else:
                    print(f"⚠️ Graph '{graph_name}' not found in configuration")
                    if "graphs" in graph_config and "main" in graph_config["graphs"]:
                        print(f"ℹ️ Falling back to 'main' graph")
                        graph_name = "main"
                    else:
                        print(f"ℹ️ No valid graph found, falling back to standard workflow")
                        use_config = False
                
                # In a real implementation, you would use the Graph.from_json method
                # to instantiate the graph from the configuration
                
                # For now, fall back to our standard implementation
                print(f"ℹ️ Using standard workflow implementation with configuration-aware settings")
            except Exception as e:
                print(f"⚠️ Error loading LangGraph configuration: {str(e)}")
                print(f"ℹ️ Falling back to standard workflow implementation")
                use_config = False
        
        # Import state if specified
        initial_state = None
        if args.import_state and os.path.exists(args.import_state):
            print(f"📥 Importing state from {args.import_state}")
            try:
                with open(args.import_state, 'r') as f:
                    initial_state = json.load(f)
                print("✅ State imported successfully")
            except Exception as e:
                print(f"⚠️ Error importing state: {str(e)}")
                initial_state = None
        
        # Get client information (override from environment if provided in args)
        client_id = args.client_id or env['client_id']
        client_name = args.client_name or env['client_name']
        
        # Run workflow with or without tracing based on arguments
        # Make sure we use await for both branches since run_workflow is async
        if args.trace or env['langchain_tracing']:
            result = await run_workflow(
                traceable=True,  # Set to True if tracing is enabled
                client_id=client_id,
                client_name=client_name,
                openrouter_model=openrouter_model,
                ollama_model=ollama_model,
                initial_state=initial_state
            )
        else:
            result = await run_workflow(
                client_id=client_id,
                client_name=client_name,
                traceable=False,
                openrouter_model=openrouter_model,
                ollama_model=ollama_model,
                use_config=use_config,
                initial_state=initial_state
            )
        
        # Export state if specified
        if args.export_state:
            print(f"📤 Exporting state to {args.export_state}")
            try:
                with open(args.export_state, 'w') as f:
                    json.dump(result, f, indent=2)
                print("✅ State exported successfully")
            except Exception as e:
                print(f"⚠️ Error exporting state: {str(e)}")
        
        # Display verification status
        print("\n=== Verification Results ===\n")
        
        if 'verification_summary' in result:
            summary = result['verification_summary']
            print(f"Overall Status: {summary.get('overall_status', 'Unknown')}")
            print(f"Risk Level: {summary.get('risk_level', 'Unknown')}")
        
        # Display report if available
        if 'report' in result:
            print("\n=== Final Report ===\n")
            print(result['report'])
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

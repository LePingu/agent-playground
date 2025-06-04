"""Command-line interface for Agent Playground."""

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from agent_playground.utils.config import get_env_info, get_settings
from agent_playground.core.registry import agent_registry
from agent_playground.utils.logging import setup_logging
from agent_playground.workflows.builder import WorkflowBuilder

app = typer.Typer(
    name="agent-playground",
    help="AI Agent Playground Framework with LangGraph",
    no_args_is_help=True,
)

console = Console()


@app.command()
def info(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information")
):
    """Show information about the Agent Playground environment."""
    settings = get_settings()
    
    # Basic info
    info_table = Table(title="Agent Playground Information")
    info_table.add_column("Setting", style="cyan")
    info_table.add_column("Value", style="green")
    
    info_table.add_row("Version", "0.1.0")
    info_table.add_row("Environment", settings.environment)
    info_table.add_row("Debug Mode", str(settings.debug))
    info_table.add_row("Data Directory", str(settings.data_dir))
    info_table.add_row("Reports Directory", str(settings.reports_dir))
    
    console.print(info_table)
    
    if verbose:
        # Show environment details
        env_info = get_env_info()
        env_panel = Panel.fit(
            f"Python: {env_info['python_version']}\n"
            f"Working Dir: {env_info['working_directory']}\n"
            f"Env Files: {', '.join(f for f, exists in zip(env_info['env_files_checked'], env_info['env_files_exist']) if exists)}",
            title="Environment Details",
            border_style="blue"
        )
        console.print(env_panel)
        
        # Show registry info
        registry_info = agent_registry.get_registry_info()
        registry_table = Table(title="Agent Registry")
        registry_table.add_column("Agent", style="cyan")
        registry_table.add_column("Class", style="yellow")
        registry_table.add_column("Instance", style="green")
        
        for name, info in registry_info["agents"].items():
            registry_table.add_row(
                name,
                info["class"],
                "✓" if info["has_instance"] else "✗"
            )
        
        console.print(registry_table)


@app.command()
def list_agents():
    """List all registered agents."""
    agents = agent_registry.list_agents()
    
    if not agents:
        rprint("[yellow]No agents registered[/yellow]")
        return
    
    table = Table(title="Registered Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Class", style="yellow")
    table.add_column("Description", style="green")
    
    for name in agents:
        config = agent_registry.get_config(name)
        agent_class = agent_registry.get_agent_class(name)
        
        table.add_row(
            name,
            agent_class.__name__ if agent_class else "Unknown",
            config.description if config and config.description else "No description"
        )
    
    console.print(table)


@app.command()
def create_agent(
    name: str = typer.Argument(..., help="Agent name to create"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be created without executing")
):
    """Create and run an agent instance."""
    
    if name not in agent_registry.list_agents():
        rprint(f"[red]Agent '{name}' not registered[/red]")
        available = agent_registry.list_agents()
        if available:
            rprint(f"Available agents: {', '.join(available)}")
        return
    
    try:
        # Load config overrides from file if provided
        config_overrides = {}
        if config_file and config_file.exists():
            import json
            with open(config_file) as f:
                config_overrides = json.load(f)
        
        if dry_run:
            config = agent_registry.get_config(name)
            rprint(f"[blue]Would create agent:[/blue] {name}")
            rprint(f"[blue]Base config:[/blue] {config.model_dump()}")
            if config_overrides:
                rprint(f"[blue]Overrides:[/blue] {config_overrides}")
            return
        
        # Create agent
        agent = agent_registry.create(name, **config_overrides)
        rprint(f"[green]Created agent:[/green] {agent.config.name}")
        
        # Show agent info
        info = agent.get_info()
        info_panel = Panel.fit(
            f"Type: {info['type']}\n"
            f"Module: {info['module']}\n"
            f"Description: {info['config'].get('description', 'No description')}",
            title=f"Agent: {name}",
            border_style="green"
        )
        console.print(info_panel)
        
    except Exception as e:
        rprint(f"[red]Error creating agent:[/red] {e}")


@app.command() 
def run_workflow(
    workflow_file: Path = typer.Argument(..., help="Workflow definition file"),
    input_file: Optional[Path] = typer.Option(None, "--input", "-i", help="Input data file"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    trace: bool = typer.Option(False, "--trace", help="Enable tracing")
):
    """Run a workflow from a definition file."""
    
    if not workflow_file.exists():
        rprint(f"[red]Workflow file not found:[/red] {workflow_file}")
        return
    
    async def run():
        try:
            # Setup logging if tracing enabled
            if trace:
                setup_logging()
            
            # Load workflow definition
            import json
            with open(workflow_file) as f:
                workflow_def = json.load(f)
            
            # Load input data
            input_data = {}
            if input_file and input_file.exists():
                with open(input_file) as f:
                    input_data = json.load(f)
            
            rprint(f"[blue]Running workflow:[/blue] {workflow_def.get('name', 'unnamed')}")
            
            # Build workflow (simplified example)
            builder = WorkflowBuilder(name=workflow_def.get('name', 'cli_workflow'))
            
            # Add steps from definition
            for step in workflow_def.get('steps', []):
                if step['type'] == 'function':
                    # Simple function step
                    def step_func(state, step_config=step):
                        rprint(f"[yellow]Executing step:[/yellow] {step_config['name']}")
                        return state
                    
                    builder.add_step(step['name'], step_func)
            
            # Chain steps sequentially (simplified)
            steps = workflow_def.get('steps', [])
            for i in range(len(steps) - 1):
                builder.chain(steps[i]['name'], steps[i+1]['name'])
            
            if steps:
                builder.start_with(steps[0]['name'])
                builder.chain_to_end(steps[-1]['name'])
            
            # Build and run
            graph = builder.build()
            result = await graph.ainvoke(input_data)
            
            # Save output
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                rprint(f"[green]Output saved to:[/green] {output_file}")
            else:
                rprint("[green]Workflow completed successfully[/green]")
                rprint(f"Result: {result}")
                
        except Exception as e:
            rprint(f"[red]Workflow execution failed:[/red] {e}")
    
    asyncio.run(run())


@app.command()
def init_project(
    path: Path = typer.Argument(".", help="Project directory"),
    template: str = typer.Option("basic", help="Project template (basic, sow)")
):
    """Initialize a new Agent Playground project."""
    
    project_path = Path(path).resolve()
    
    if project_path.exists() and any(project_path.iterdir()):
        if not typer.confirm(f"Directory {project_path} is not empty. Continue?"):
            raise typer.Abort()
    
    project_path.mkdir(parents=True, exist_ok=True)
    
    rprint(f"[blue]Initializing project in:[/blue] {project_path}")
    
    # Create basic structure
    directories = [
        "agents",
        "workflows", 
        "config",
        "data",
        "tests",
    ]
    
    for dir_name in directories:
        (project_path / dir_name).mkdir(exist_ok=True)
        (project_path / dir_name / "__init__.py").touch()
    
    # Create basic files
    files = {
        ".env.example": """# Agent Playground Configuration
ENVIRONMENT=development
DEBUG=false

# Model Configuration
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4-turbo

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agent-playground.log

# Tracing
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=your_key_here
LANGSMITH_PROJECT=agent-playground
""",
        "README.md": f"""# Agent Playground Project

This project was created using the Agent Playground framework.

## Getting Started

1. Copy `.env.example` to `.env` and configure your settings
2. Install dependencies: `pip install agent-playground`
3. Run your first agent: `agent-playground list-agents`

## Template: {template}

Generated on: {typer.get_app_dir('agent-playground')}
""",
        "main.py": """#!/usr/bin/env python3
\"\"\"Main entry point for your Agent Playground project.\"\"\"

import asyncio
from agent_playground import get_settings, setup_logging

async def main():
    \"\"\"Main function.\"\"\"
    settings = get_settings()
    setup_logging()
    
    print(f"Agent Playground project initialized!")
    print(f"Environment: {settings.environment}")

if __name__ == "__main__":
    asyncio.run(main())
""",
    }
    
    for filename, content in files.items():
        file_path = project_path / filename
        with open(file_path, 'w') as f:
            f.write(content)
    
    rprint(f"[green]Project initialized successfully![/green]")
    rprint(f"[yellow]Next steps:[/yellow]")
    rprint("1. Copy .env.example to .env and configure your settings")
    rprint("2. Run: python main.py")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    validate: bool = typer.Option(False, "--validate", help="Validate configuration"),
):
    """Manage configuration."""
    
    if show:
        settings = get_settings()
        
        config_table = Table(title="Current Configuration")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        # Flatten settings for display (hide sensitive data)
        def add_settings(obj, prefix=""):
            for key, value in obj.model_dump().items():
                if isinstance(value, dict):
                    add_settings(type('', (), value)(), f"{prefix}{key}.")
                else:
                    # Hide sensitive values
                    if "key" in key.lower() or "secret" in key.lower():
                        value = "***" if value else "not set"
                    config_table.add_row(f"{prefix}{key}", str(value))
        
        add_settings(settings)
        console.print(config_table)
    
    if validate:
        try:
            settings = get_settings()
            rprint("[green]✓ Configuration is valid[/green]")
            
            # Check for common issues
            warnings = []
            if not settings.model.openrouter_api_key and not settings.model.openai_api_key:
                warnings.append("No API keys configured")
            
            if warnings:
                rprint("[yellow]Warnings:[/yellow]")
                for warning in warnings:
                    rprint(f"  • {warning}")
        
        except Exception as e:
            rprint(f"[red]✗ Configuration validation failed:[/red] {e}")


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()

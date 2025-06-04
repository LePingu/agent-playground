"""CLI for workflow templates and examples."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich import print as rprint

from .templates import workflow_templates, WorkflowTemplateRegistry
from .examples import get_example_workflows
from .monitor import WorkflowExecutor, WorkflowScheduler
from ..utils.logging import get_logger

app = typer.Typer(name="workflows", help="Workflow templates and examples management")
console = Console()
logger = get_logger("workflow_cli")


@app.command("list-templates")
def list_templates():
    """List all available workflow templates."""
    templates = workflow_templates.list_templates()
    
    if not templates:
        console.print("[yellow]No workflow templates found.[/yellow]")
        return
    
    table = Table(title="Available Workflow Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Required Parameters", style="green")
    table.add_column("Pattern", style="magenta")
    
    for template_name in templates:
        info = workflow_templates.get_template_info(template_name)
        if info:
            table.add_row(
                info["name"],
                info["description"],
                ", ".join(info["required_parameters"]),
                info["pattern"]
            )
    
    console.print(table)


@app.command("template-info")
def template_info(
    name: str = typer.Argument(..., help="Template name")
):
    """Get detailed information about a workflow template."""
    info = workflow_templates.get_template_info(name)
    
    if not info:
        console.print(f"[red]Template '{name}' not found.[/red]")
        raise typer.Exit(1)
    
    # Display template information
    console.print(Panel(
        f"[bold cyan]{info['name']}[/bold cyan]\n\n"
        f"[white]{info['description']}[/white]\n\n"
        f"[green]Pattern:[/green] {info['pattern']}\n\n"
        f"[yellow]Required Parameters:[/yellow]\n" +
        "\n".join(f"  • {param}" for param in info['required_parameters']) + "\n\n" +
        f"[blue]Optional Parameters:[/blue]\n" +
        "\n".join(f"  • {param}: {value}" for param, value in info['optional_parameters'].items()),
        title=f"Template: {name}",
        border_style="blue"
    ))


@app.command("list-examples")
def list_examples():
    """List all available workflow examples."""
    examples = get_example_workflows()
    
    if not examples:
        console.print("[yellow]No workflow examples found.[/yellow]")
        return
    
    table = Table(title="Available Workflow Examples")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Description", style="green")
    table.add_column("State Class", style="magenta")
    
    for key, example in examples.items():
        table.add_row(
            key,
            example["name"],
            example["description"],
            example["state_class"].__name__
        )
    
    console.print(table)


@app.command("run-example")
def run_example(
    example_key: str = typer.Argument(..., help="Example workflow key"),
    output_dir: str = typer.Option("workflow_reports", help="Output directory for reports"),
    monitor: bool = typer.Option(True, help="Enable workflow monitoring"),
    generate_report: bool = typer.Option(True, help="Generate execution report")
):
    """Run an example workflow."""
    examples = get_example_workflows()
    
    if example_key not in examples:
        console.print(f"[red]Example '{example_key}' not found.[/red]")
        console.print(f"Available examples: {', '.join(examples.keys())}")
        raise typer.Exit(1)
    
    example = examples[example_key]
    console.print(Panel(
        f"[bold cyan]{example['name']}[/bold cyan]\n\n"
        f"[white]{example['description']}[/white]",
        title="Running Example Workflow",
        border_style="green"
    ))
    
    # Create workflow and initial state
    workflow = example["create_func"]()
    initial_state = example["state_class"](**example["example_input"])
    
    # Run workflow
    asyncio.run(_run_workflow_async(
        workflow, 
        initial_state, 
        output_dir, 
        monitor, 
        generate_report
    ))


async def _run_workflow_async(workflow, initial_state, output_dir, monitor, generate_report):
    """Run workflow asynchronously with progress tracking."""
    executor = WorkflowExecutor()
    
    try:
        with Progress() as progress:
            task = progress.add_task("Executing workflow...", total=100)
            
            # Execute workflow
            final_state, workflow_monitor = await executor.execute_workflow(
                workflow=workflow,
                initial_state=initial_state,
                monitor=monitor,
                generate_report=generate_report,
                output_dir=output_dir
            )
            
            progress.update(task, completed=100)
        
        # Display results
        console.print("\n[green]✅ Workflow completed successfully![/green]")
        
        if hasattr(final_state, 'completed_steps'):
            console.print(f"[blue]Completed steps:[/blue] {len(final_state.completed_steps)}")
        
        if workflow_monitor:
            status = workflow_monitor.get_current_status()
            metrics = status["metrics"]
            
            console.print(Panel(
                f"[yellow]Execution Time:[/yellow] {metrics.get('total_execution_time', 0):.2f}s\n"
                f"[yellow]Steps:[/yellow] {metrics.get('step_count', 0)}\n"
                f"[yellow]Success Rate:[/yellow] {metrics.get('success_rate', 0):.1%}\n"
                f"[yellow]Errors:[/yellow] {metrics.get('error_count', 0)}",
                title="Execution Metrics",
                border_style="yellow"
            ))
        
        if generate_report:
            console.print(f"[green]📊 Reports generated in:[/green] {output_dir}")
    
    except Exception as e:
        console.print(f"[red]❌ Workflow failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("create-from-template")
def create_from_template(
    template_name: str = typer.Argument(..., help="Template name"),
    config_file: Optional[str] = typer.Option(None, help="JSON config file with parameters"),
    output_dir: str = typer.Option("workflow_reports", help="Output directory for reports")
):
    """Create and run a workflow from a template."""
    if not workflow_templates.get(template_name):
        console.print(f"[red]Template '{template_name}' not found.[/red]")
        raise typer.Exit(1)
    
    # Load configuration
    if config_file:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except Exception as e:
            console.print(f"[red]Error loading config file: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print("[yellow]No config file provided. You'll need to implement agent creation manually.[/yellow]")
        return
    
    # Create workflow from template
    try:
        workflow = workflow_templates.create_workflow(template_name, **config)
        if not workflow:
            console.print(f"[red]Failed to create workflow from template '{template_name}'[/red]")
            raise typer.Exit(1)
        
        console.print(f"[green]✅ Created workflow from template: {template_name}[/green]")
        console.print("[yellow]Note: You'll need to provide initial state and run the workflow manually.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error creating workflow: {e}[/red]")
        raise typer.Exit(1)


@app.command("generate-template-config")
def generate_template_config(
    template_name: str = typer.Argument(..., help="Template name"),
    output_file: str = typer.Option("template_config.json", help="Output config file")
):
    """Generate a sample configuration file for a template."""
    info = workflow_templates.get_template_info(template_name)
    
    if not info:
        console.print(f"[red]Template '{template_name}' not found.[/red]")
        raise typer.Exit(1)
    
    # Create sample configuration
    config = {
        "template": template_name,
        "description": f"Sample configuration for {template_name} template",
        "required_parameters": {
            param: f"TODO: Provide {param}"
            for param in info["required_parameters"]
        },
        "optional_parameters": info["optional_parameters"]
    }
    
    # Save configuration
    try:
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2, default=str)
        
        console.print(f"[green]✅ Generated sample config: {output_file}[/green]")
        console.print("[yellow]Please edit the config file to provide actual values.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error saving config file: {e}[/red]")
        raise typer.Exit(1)


@app.command("monitor")
def monitor_workflows():
    """Monitor active workflows."""
    executor = WorkflowExecutor()
    active_workflows = executor.get_active_workflows()
    
    if not active_workflows:
        console.print("[yellow]No active workflows found.[/yellow]")
        return
    
    table = Table(title="Active Workflows")
    table.add_column("Workflow", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Current Agent", style="green")
    table.add_column("Progress", style="yellow")
    table.add_column("Duration", style="magenta")
    
    for name, status in active_workflows.items():
        table.add_row(
            name,
            status["status"],
            status.get("current_agent", "N/A"),
            f"{status.get('progress', 0):.1f}%",
            f"{status['metrics'].get('total_execution_time', 0):.1f}s"
        )
    
    console.print(table)


@app.command("schedule")
def schedule_workflow():
    """Schedule workflow execution (placeholder)."""
    console.print("[yellow]Workflow scheduling feature coming soon![/yellow]")
    console.print("This will allow you to:")
    console.print("  • Schedule workflows for future execution")
    console.print("  • Set up recurring workflow runs")
    console.print("  • Manage scheduled workflow queue")


@app.command("visualize")
def visualize_workflow(
    report_dir: str = typer.Argument(..., help="Directory containing workflow reports"),
    interactive: bool = typer.Option(False, help="Open interactive visualization")
):
    """Visualize workflow execution results."""
    report_path = Path(report_dir)
    
    if not report_path.exists():
        console.print(f"[red]Report directory not found: {report_dir}[/red]")
        raise typer.Exit(1)
    
    # Find report files
    html_reports = list(report_path.glob("*_report_*.html"))
    interactive_reports = list(report_path.glob("*_interactive_*.html"))
    
    if not html_reports and not interactive_reports:
        console.print(f"[yellow]No workflow reports found in: {report_dir}[/yellow]")
        return
    
    # Display available reports
    console.print(Panel(
        f"[green]Found {len(html_reports)} HTML reports and {len(interactive_reports)} interactive reports[/green]",
        title="Available Reports",
        border_style="green"
    ))
    
    if html_reports:
        console.print("\n[cyan]HTML Reports:[/cyan]")
        for report in html_reports:
            console.print(f"  • {report.name}")
    
    if interactive_reports:
        console.print("\n[magenta]Interactive Reports:[/magenta]")
        for report in interactive_reports:
            console.print(f"  • {report.name}")
    
    if interactive and interactive_reports:
        import webbrowser
        latest_interactive = max(interactive_reports, key=lambda p: p.stat().st_mtime)
        webbrowser.open(f"file://{latest_interactive.absolute()}")
        console.print(f"[green]Opened interactive report: {latest_interactive.name}[/green]")


if __name__ == "__main__":
    app()

"""Command-line interface for Source of Wealth analysis."""

import asyncio
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from ..utils import get_settings, setup_logging
from .workflow import SOWWorkflow, create_sow_workflow
from .state import SOWState

app = typer.Typer(
    name="sow-agent",
    help="Source of Wealth Analysis Agent",
    no_args_is_help=True,
)

console = Console()


@app.command()
def analyze(
    client_id: str = typer.Argument(..., help="Client ID for analysis"),
    client_name: str = typer.Argument(..., help="Client name for analysis"),
    id_document: Optional[str] = typer.Option(None, "--id-doc", help="Path to ID document"),
    payslip_document: Optional[str] = typer.Option(None, "--payslip-doc", help="Path to payslip document"),
    financial_reports: Optional[str] = typer.Option(None, "--financial-reports", help="Comma-separated paths to financial reports"),
    use_mock: bool = typer.Option(False, "--use-mock", help="Use mock results for testing"),
    output_file: Optional[str] = typer.Option(None, "--output", help="Output file for report"),
):
    """Run Source of Wealth analysis for a client."""
    
    # Setup
    setup_logging()
    settings = get_settings()
    
    console.print(Panel(
        f"[bold blue]Source of Wealth Analysis[/bold blue]\n"
        f"Client: {client_name} (ID: {client_id})",
        title="SOW Analysis",
        border_style="blue"
    ))
    
    # Parse financial reports
    financial_report_paths = []
    if financial_reports:
        financial_report_paths = [p.strip() for p in financial_reports.split(",")]
    
    # Run analysis
    result = asyncio.run(_run_analysis(
        client_id=client_id,
        client_name=client_name,
        id_document_path=id_document,
        payslip_document_path=payslip_document,
        financial_report_paths=financial_report_paths,
        use_mock=use_mock
    ))
    
    # Display results
    _display_results(result)
    
    # Save report if requested
    if output_file and result.final_report:
        Path(output_file).write_text(result.final_report)
        console.print(f"✅ Report saved to: {output_file}")


@app.command()
def status(
    client_id: str = typer.Argument(..., help="Client ID to check status"),
):
    """Check the status of an ongoing SOW analysis."""
    console.print(f"[yellow]Checking status for client ID: {client_id}[/yellow]")
    console.print("[dim]Note: Status checking not yet implemented[/dim]")


@app.command()
def resume(
    client_id: str = typer.Argument(..., help="Client ID to resume analysis"),
    feedback: Optional[str] = typer.Option(None, "--feedback", help="Human review feedback"),
):
    """Resume SOW analysis after human review."""
    console.print(f"[yellow]Resuming analysis for client ID: {client_id}[/yellow]")
    if feedback:
        console.print(f"Feedback: {feedback}")
    console.print("[dim]Note: Resume functionality not yet implemented[/dim]")


async def _run_analysis(
    client_id: str,
    client_name: str,
    id_document_path: Optional[str] = None,
    payslip_document_path: Optional[str] = None,
    financial_report_paths: Optional[list] = None,
    use_mock: bool = False
) -> SOWState:
    """Run the SOW analysis workflow."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Initializing SOW workflow...", total=None)
        
        # Create workflow
        workflow_config = {"use_mock_results": use_mock}
        workflow = create_sow_workflow(workflow_config)
        
        progress.update(task, description="Running SOW analysis...")
        
        # Run workflow
        result = await workflow.run(
            client_id=client_id,
            client_name=client_name,
            id_document_path=id_document_path,
            payslip_document_path=payslip_document_path,
            financial_report_paths=financial_report_paths or []
        )
        
        progress.update(task, description="Analysis completed!", advance=100)
    
    return result


def _display_results(state: SOWState):
    """Display analysis results in a formatted way."""
    
    # Overall status
    console.print(f"\n[bold green]Analysis Complete[/bold green]")
    console.print(f"Progress: {state.get_progress_percentage():.1f}%")
    
    # Verification Results Table
    table = Table(title="Verification Results")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")
    
    # ID Verification
    if state.id_verification:
        status = "✅ VERIFIED" if state.id_verification.verified else "❌ FAILED"
        details = f"Confidence: {state.id_verification.confidence_score:.2f}"
        if state.id_verification.issues_found:
            details += f", Issues: {len(state.id_verification.issues_found)}"
        table.add_row("ID Verification", status, details)
    
    # Payslip Verification
    if state.payslip_verification:
        status = "✅ VERIFIED" if state.payslip_verification.verified else "❌ FAILED"
        details = f"Confidence: {state.payslip_verification.confidence_score:.2f}"
        if state.payslip_verification.monthly_income:
            details += f", Income: ${state.payslip_verification.monthly_income:,.2f}"
        table.add_row("Payslip Verification", status, details)
    
    # Web References
    if state.web_references:
        status = "✅ FOUND" if state.web_references.verified else "❌ NOT FOUND"
        details = f"Sources: {state.web_references.sources_found}"
        if state.web_references.risk_flags:
            details += f", Risk Flags: {len(state.web_references.risk_flags)}"
        table.add_row("Web References", status, details)
    
    # Financial Reports
    if state.financial_reports:
        status = "✅ VERIFIED" if state.financial_reports.verified else "❌ FAILED"
        details = f"Reports: {len(state.financial_reports.reports_analyzed)}"
        table.add_row("Financial Reports", status, details)
    
    console.print(table)
    
    # Risk Assessment
    if state.risk_assessment:
        risk_color = "green" if state.risk_assessment.risk_level == "low" else "yellow" if state.risk_assessment.risk_level == "medium" else "red"
        console.print(f"\n[bold]Risk Assessment:[/bold]")
        console.print(f"Risk Level: [{risk_color}]{state.risk_assessment.risk_level.upper()}[/{risk_color}]")
        console.print(f"Risk Score: {state.risk_assessment.risk_score}/100")
        
        if state.risk_assessment.risk_factors:
            console.print("\n[bold]Risk Factors:[/bold]")
            for factor in state.risk_assessment.risk_factors:
                console.print(f"• {factor}")
        
        if state.risk_assessment.recommendations:
            console.print("\n[bold]Recommendations:[/bold]")
            for rec in state.risk_assessment.recommendations:
                console.print(f"• {rec}")
    
    # Human Review Status
    if state.needs_human_review:
        console.print(f"\n[yellow]⚠️  Human review required[/yellow]")
        if not state.human_review_completed:
            console.print("Use 'sow-agent resume' command after human review is complete.")
    
    # Messages
    if state.messages:
        console.print("\n[bold]Process Messages:[/bold]")
        for msg in state.messages[-5:]:  # Show last 5 messages
            msg_color = "green" if msg["type"] == "success" else "yellow" if msg["type"] == "warning" else "red" if msg["type"] == "error" else "white"
            console.print(f"[{msg_color}]{msg['agent']}:[/{msg_color}] {msg['message']}")


def main():
    """Main entry point for SOW CLI."""
    app()


if __name__ == "__main__":
    main()

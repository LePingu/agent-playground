"""Source of Wealth (SOW) Agent CLI implementation."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click
from pydantic import BaseModel

from ..utils.logging import get_logger
from ..utils.config import get_settings
from .workflow import SOWWorkflow
from .state import SOWState, SOWDocuments


logger = get_logger(__name__)


class SOWVerificationRequest(BaseModel):
    """Request model for SOW verification."""
    client_id: str
    client_name: str
    documents: SOWDocuments


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def main(ctx, verbose):
    """Source of Wealth (SOW) Agent CLI.
    
    Verify client identity and income sources through document analysis.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        # Don't try to set level on our custom logger - it's handled by the logging system


@main.command()
@click.argument('client_id')
@click.argument('client_name')
@click.option('--id', 'id_document', type=click.Path(exists=True), 
              help='Path to ID document (PDF, image)')
@click.option('--payslip', type=click.Path(exists=True), 
              help='Path to payslip document (PDF, image)')
@click.option('--bank-statement', type=click.Path(exists=True), 
              help='Path to bank statement (PDF)')
@click.option('--employment-letter', type=click.Path(exists=True), 
              help='Path to employment letter (PDF)')
@click.option('--tax-document', type=click.Path(exists=True), 
              help='Path to tax document (PDF)')
@click.option('--output', '-o', type=click.Path(), 
              help='Output file for verification report (JSON)')
@click.option('--interactive', '-i', is_flag=True, 
              help='Enable interactive mode for human-in-the-loop decisions')
@click.pass_context
def verify(ctx, client_id: str, client_name: str, 
           id_document: Optional[str] = None,
           payslip: Optional[str] = None,
           bank_statement: Optional[str] = None,
           employment_letter: Optional[str] = None,
           tax_document: Optional[str] = None,
           output: Optional[str] = None,
           interactive: bool = False):
    """Verify client's source of wealth through document analysis.
    
    CLIENT_ID: Unique identifier for the client
    CLIENT_NAME: Full name of the client
    
    Examples:
        sow-agent verify CLIENT_123 "John Doe" --id documents/id.pdf --payslip documents/payslip.pdf
        sow-agent verify CLIENT_456 "Jane Smith" --id id.pdf --payslip payslip.pdf --bank-statement statement.pdf -o report.json
    """
    verbose = ctx.obj.get('verbose', False)
    
    if verbose:
        click.echo(f"Starting SOW verification for client: {client_id} ({client_name})")
    
    # Validate required documents
    if not id_document and not payslip:
        click.echo("Error: At least one document (--id or --payslip) is required", err=True)
        sys.exit(1)
    
    # Prepare document paths
    documents = SOWDocuments()
    
    if id_document:
        documents.id_document = Path(id_document).resolve()
        if verbose:
            click.echo(f"ID document: {documents.id_document}")
    
    if payslip:
        documents.payslip = Path(payslip).resolve()
        if verbose:
            click.echo(f"Payslip: {documents.payslip}")
    
    if bank_statement:
        documents.bank_statement = Path(bank_statement).resolve()
        if verbose:
            click.echo(f"Bank statement: {documents.bank_statement}")
    
    if employment_letter:
        documents.employment_letter = Path(employment_letter).resolve()
        if verbose:
            click.echo(f"Employment letter: {documents.employment_letter}")
    
    if tax_document:
        documents.tax_document = Path(tax_document).resolve()
        if verbose:
            click.echo(f"Tax document: {documents.tax_document}")
    
    # Verify all document files exist and are readable
    for doc_name, doc_path in documents.dict().items():
        if doc_path and not os.access(doc_path, os.R_OK):
            click.echo(f"Error: Cannot read {doc_name} at {doc_path}", err=True)
            sys.exit(1)
    
    # Create verification request
    request = SOWVerificationRequest(
        client_id=client_id,
        client_name=client_name,
        documents=documents
    )
    
    try:
        # Run the verification workflow
        result = asyncio.run(_run_verification(request, interactive, verbose))
        
        # Output results
        if output:
            _save_results(result, output, verbose)
        else:
            _display_results(result, verbose)
            
    except Exception as e:
        click.echo(f"Error during verification: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


async def _run_verification(request: SOWVerificationRequest, interactive: bool, verbose: bool) -> dict:
    """Run the SOW verification workflow."""
    if verbose:
        click.echo("Initializing SOW workflow...")
    
    # Import the original runner functionality
    import sys
    sys.path.append('/workspaces/agent-playground/source_of_wealth_agent')
    
    from source_of_wealth_agent.workflow.runner import run_workflow
    from source_of_wealth_agent.core.state import create_initial_state
    
    # Create initial state for the original workflow
    initial_state = create_initial_state(request.client_id, request.client_name)
    
    # Set document paths in the state if provided
    if request.documents.id_document:
        initial_state["id_document_path"] = str(request.documents.id_document)
    if request.documents.payslip:
        initial_state["payslip_document_path"] = str(request.documents.payslip)
    
    if verbose:
        click.echo(f"Starting verification workflow for {request.client_id}...")
    
    # Run the original workflow
    try:
        final_state = await run_workflow(
            client_id=request.client_id,
            client_name=request.client_name,
            traceable=verbose,
            initial_state=initial_state
        )
        
        if verbose:
            click.echo("Verification workflow completed")
        
        return final_state
        
    except Exception as e:
        if verbose:
            click.echo(f"Workflow execution error: {str(e)}")
        # Return a minimal result structure for error cases
        return {
            'client_id': request.client_id,
            'client_name': request.client_name,
            'current_step': 'error',
            'error': str(e),
            'verification_completed': False
        }


def _save_results(result: dict, output_path: str, verbose: bool):
    """Save verification results to a file."""
    import json
    
    try:
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        if verbose:
            click.echo(f"Results saved to: {output_path}")
        else:
            click.echo(f"Verification complete. Results saved to: {output_path}")
            
    except Exception as e:
        click.echo(f"Error saving results: {str(e)}", err=True)
        raise


def _display_results(result: dict, verbose: bool):
    """Display verification results to the console."""
    click.echo("\n" + "="*60)
    click.echo("SOW VERIFICATION RESULTS")
    click.echo("="*60)
    
    # Display key information
    client_id = result.get('client_id', 'Unknown')
    client_name = result.get('client_name', 'Unknown')
    current_step = result.get('current_step', 'Unknown')
    progress = result.get('progress_percentage', 0)
    
    click.echo(f"Client ID: {client_id}")
    click.echo(f"Client Name: {client_name}")
    click.echo(f"Current Step: {current_step}")
    click.echo(f"Progress: {progress:.1f}%")
    
    # Display risk assessment if available
    risk_assessment = result.get('risk_assessment')
    if risk_assessment:
        click.echo(f"Risk Level: {risk_assessment.get('risk_level', 'Unknown')}")
        click.echo(f"Risk Score: {risk_assessment.get('risk_score', 'N/A')}")
    
    # Display verification details if available
    verification_statuses = {}
    if result.get('id_verification'):
        verification_statuses['ID Verification'] = result['id_verification'].get('verified', False)
    if result.get('payslip_verification'):
        verification_statuses['Payslip Verification'] = result['payslip_verification'].get('verified', False)
    if result.get('web_references'):
        verification_statuses['Web References'] = result['web_references'].get('verified', False)
    if result.get('financial_reports'):
        verification_statuses['Financial Reports'] = result['financial_reports'].get('verified', False)
    
    if verification_statuses:
        click.echo("\nVerification Details:")
        click.echo("-" * 30)
        for verification_type, status in verification_statuses.items():
            status_str = "✓ Verified" if status else "✗ Failed"
            click.echo(f"  {verification_type}: {status_str}")
    
    # Display recommendations if available
    if risk_assessment and risk_assessment.get('recommendations'):
        recommendations = risk_assessment['recommendations']
        click.echo("\nRecommendations:")
        click.echo("-" * 30)
        for i, rec in enumerate(recommendations, 1):
            click.echo(f"  {i}. {rec}")
    
    # Display full results in verbose mode
    if verbose:
        click.echo("\nFull Results (JSON):")
        click.echo("-" * 30)
        import json
        click.echo(json.dumps(result, indent=2, default=str))
    
    click.echo("="*60)


@main.command()
def status():
    """Check the status of the SOW agent system."""
    click.echo("SOW Agent Status:")
    click.echo("-" * 20)
    
    # Check configuration
    try:
        settings = get_settings()
        click.echo("✓ Configuration loaded successfully")
    except Exception as e:
        click.echo(f"✗ Configuration error: {str(e)}")
        return
    
    # Check workflow availability
    try:
        workflow = SOWWorkflow()
        click.echo("✓ SOW workflow initialized successfully")
    except Exception as e:
        click.echo(f"✗ Workflow initialization error: {str(e)}")
        return
    
    click.echo("✓ SOW agent system is ready")


if __name__ == '__main__':
    main()
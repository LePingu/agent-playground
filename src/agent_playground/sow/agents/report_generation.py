"""Report Generation Agent for Source of Wealth analysis."""

from datetime import datetime
from typing import Dict, Any, Optional

from ...core.base import BaseAgent, AgentConfig
from ...utils.logging import get_logger
from ..state import SOWState


class ReportGenerationAgent(BaseAgent):
    """Agent for generating final SOW reports."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="report_generation_agent",
            description="Generates comprehensive SOW analysis reports",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: SOWState) -> SOWState:
        """Generate final report for the given state."""
        self.logger.info(f"Generating final report for client: {state.client_name}")
        
        # Generate comprehensive report
        report = self._generate_report(state)
        state.final_report = report
        
        # Generate summary
        summary = self._generate_summary(state)
        state.summary = summary
        
        state.mark_step_completed("report_generation")
        state.add_message(
            agent=self.name,
            message="Final report generated successfully",
            message_type="success"
        )
        
        return state
    
    def _generate_report(self, state: SOWState) -> str:
        """Generate detailed SOW report."""
        report_parts = [
            f"# Source of Wealth Analysis Report",
            f"**Client:** {state.client_name}",
            f"**Client ID:** {state.client_id}",
            f"**Report Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Analysis Progress:** {state.get_progress_percentage():.1f}%",
            "",
            "## Executive Summary",
        ]
        
        # Add risk assessment summary
        if state.risk_assessment:
            report_parts.extend([
                f"**Risk Level:** {state.risk_assessment.risk_level.upper()}",
                f"**Risk Score:** {state.risk_assessment.risk_score}/100",
                ""
            ])
        
        # Add verification results
        report_parts.append("## Verification Results")
        
        if state.id_verification:
            status = "✅ VERIFIED" if state.id_verification.verified else "❌ FAILED"
            report_parts.append(f"**ID Verification:** {status}")
        
        if state.payslip_verification:
            status = "✅ VERIFIED" if state.payslip_verification.verified else "❌ FAILED"
            report_parts.append(f"**Payslip Verification:** {status}")
            if state.payslip_verification.monthly_income:
                report_parts.append(f"  - Monthly Income: ${state.payslip_verification.monthly_income:,.2f}")
        
        if state.web_references:
            status = "✅ FOUND" if state.web_references.verified else "❌ NOT FOUND"
            report_parts.append(f"**Web References:** {status}")
        
        if state.financial_reports:
            status = "✅ VERIFIED" if state.financial_reports.verified else "❌ FAILED"
            report_parts.append(f"**Financial Reports:** {status}")
        
        # Add recommendations
        if state.risk_assessment and state.risk_assessment.recommendations:
            report_parts.extend([
                "",
                "## Recommendations",
                *[f"- {rec}" for rec in state.risk_assessment.recommendations]
            ])
        
        return "\n".join(report_parts)
    
    def _generate_summary(self, state: SOWState) -> str:
        """Generate executive summary."""
        if state.risk_assessment:
            return f"Source of Wealth analysis completed for {state.client_name}. " \
                   f"Risk Level: {state.risk_assessment.risk_level.upper()} " \
                   f"({state.risk_assessment.risk_score}/100). " \
                   f"Analysis progress: {state.get_progress_percentage():.1f}%."
        else:
            return f"Source of Wealth analysis initiated for {state.client_name}. " \
                   f"Analysis progress: {state.get_progress_percentage():.1f}%."
    
    def get_node_config(self) -> Dict[str, Any]:
        """Get LangGraph node configuration."""
        return {
            "name": self.name,
            "function": self.process,
            "input_schema": SOWState,
            "output_schema": SOWState,
        }

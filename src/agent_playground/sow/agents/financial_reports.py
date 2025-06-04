"""Financial Reports Agent for Source of Wealth analysis."""

from typing import Dict, Any, Optional

from ...core.base import BaseAgent, AgentConfig
from ...utils.logging import get_logger
from ..state import SOWState, FinancialReportResult


class FinancialReportsAgent(BaseAgent):
    """Agent for analyzing financial reports."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="financial_reports_agent",
            description="Analyzes financial reports and statements",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: SOWState) -> SOWState:
        """Process financial report analysis for the given state."""
        self.logger.info(f"Starting financial report analysis for client: {state.client_name}")
        
        # For now, use mock results
        state.financial_reports = FinancialReportResult(
            verified=True,
            confidence_score=0.85,
            reports_analyzed=["Bank Statement", "Tax Return"],
            annual_income_range="$60,000 - $70,000",
            investment_assets="$50,000",
            credit_score="Good (720-750)",
            financial_stability="stable"
        )
        
        state.mark_step_completed("financial_reports")
        state.add_message(
            agent=self.name,
            message="Financial report analysis completed",
            message_type="success"
        )
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        """Get LangGraph node configuration."""
        return {
            "name": self.name,
            "function": self.process,
            "input_schema": SOWState,
            "output_schema": SOWState,
        }

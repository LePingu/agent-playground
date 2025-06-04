"""Human Advisory Agent for Source of Wealth analysis."""

from typing import Dict, Any, Optional

from ...core.base import BaseAgent, AgentConfig
from ...utils.logging import get_logger
from ..state import SOWState


class HumanAdvisoryAgent(BaseAgent):
    """Agent for handling human-in-the-loop interactions."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="human_advisory_agent",
            description="Manages human review and advisory processes",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: SOWState) -> SOWState:
        """Process human advisory interaction."""
        self.logger.info(f"Human advisory check for client: {state.client_name}")
        
        # Check if human review is needed
        if self._needs_human_review(state):
            state.needs_human_review = True
            state.add_message(
                agent=self.name,
                message="Human review required due to high risk or verification issues",
                message_type="warning"
            )
        else:
            state.needs_human_review = False
            state.human_review_completed = True
            state.add_message(
                agent=self.name,
                message="Automated processing approved",
                message_type="success"
            )
        
        return state
    
    def _needs_human_review(self, state: SOWState) -> bool:
        """Determine if human review is needed."""
        # High risk score requires human review
        if state.risk_assessment and state.risk_assessment.risk_score >= 70:
            return True
        
        # Failed verifications require human review
        if state.id_verification and not state.id_verification.verified:
            return True
        
        if state.payslip_verification and not state.payslip_verification.verified:
            return True
        
        return False
    
    def get_node_config(self) -> Dict[str, Any]:
        """Get LangGraph node configuration."""
        return {
            "name": self.name,
            "function": self.process,
            "input_schema": SOWState,
            "output_schema": SOWState,
        }

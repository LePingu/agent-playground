"""Web References Agent for Source of Wealth analysis."""

from typing import Dict, Any, Optional

from ...core.base import BaseAgent, AgentConfig
from ...utils.logging import get_logger
from ..state import SOWState, WebReferenceResult


class WebReferencesAgent(BaseAgent):
    """Agent for searching and analyzing web references."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="web_references_agent",
            description="Searches for and analyzes web references about the client",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: SOWState) -> SOWState:
        """Process web reference search for the given state."""
        self.logger.info(f"Starting web reference search for client: {state.client_name}")
        
        # For now, use mock results
        state.web_references = WebReferenceResult(
            verified=True,
            confidence_score=0.8,
            mentions=[{"source": "LinkedIn", "content": "Professional profile found"}],
            risk_flags=[],
            sources_found=1,
            credibility_score=0.8
        )
        
        state.mark_step_completed("web_references")
        state.add_message(
            agent=self.name,
            message="Web reference search completed",
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

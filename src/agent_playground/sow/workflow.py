"""Source of Wealth analysis workflow implementation."""

from typing import Dict, Any, Optional, List
from langgraph.graph import StateGraph, END

from ..workflows.builder import WorkflowBuilder
from ..utils.logging import get_logger
from .state import SOWState
from .agents import (
    IDVerificationAgent,
    PayslipVerificationAgent,
    WebReferencesAgent,
    FinancialReportsAgent,
    RiskAssessmentAgent,
    ReportGenerationAgent,
    HumanAdvisoryAgent,
)


class SOWWorkflow:
    """Source of Wealth analysis workflow."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "sow_workflow"
        self.description = "Complete Source of Wealth verification and analysis workflow"
        self.config = config or {}
        self.logger = get_logger(self.name)
        self._setup_agents()
    
    def _setup_agents(self):
        """Initialize all SOW agents."""
        self.agents = {
            "id_verification": IDVerificationAgent(),
            "payslip_verification": PayslipVerificationAgent(),
            "web_references": WebReferencesAgent(),
            "financial_reports": FinancialReportsAgent(),
            "risk_assessment": RiskAssessmentAgent(),
            "human_advisory": HumanAdvisoryAgent(),
            "report_generation": ReportGenerationAgent(),
        }
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(SOWState)
        
        # Add all agent nodes
        for agent_name, agent in self.agents.items():
            workflow.add_node(agent_name, agent.process)
        
        # Define the workflow flow
        workflow.set_entry_point("id_verification")
        
        # Parallel verification phase
        workflow.add_edge("id_verification", "payslip_verification")
        workflow.add_edge("payslip_verification", "web_references")
        workflow.add_edge("web_references", "financial_reports")
        
        # Analysis phase
        workflow.add_edge("financial_reports", "risk_assessment")
        workflow.add_edge("risk_assessment", "human_advisory")
        
        # Conditional routing based on human review
        workflow.add_conditional_edges(
            "human_advisory",
            self._should_continue_to_report,
            {
                "continue": "report_generation",
                "human_review": "__end__"  # Pause for human review
            }
        )
        
        workflow.add_edge("report_generation", END)
        
        return workflow
    
    def _should_continue_to_report(self, state: SOWState) -> str:
        """Determine if workflow should continue to report generation."""
        if state.needs_human_review and not state.human_review_completed:
            return "human_review"
        return "continue"
    
    async def run(
        self,
        client_id: str,
        client_name: str,
        id_document_path: Optional[str] = None,
        payslip_document_path: Optional[str] = None,
        financial_report_paths: Optional[List[str]] = None,
        **kwargs
    ) -> SOWState:
        """Run the SOW workflow."""
        
        # Initialize state
        initial_state = SOWState(
            client_id=client_id,
            client_name=client_name,
            id_document_path=id_document_path,
            payslip_document_path=payslip_document_path,
            financial_report_paths=financial_report_paths or [],
            **kwargs
        )
        
        self.logger.info(f"Starting SOW workflow for client: {client_name} (ID: {client_id})")
        
        # Build and compile the graph
        graph = self.build_graph()
        compiled_graph = graph.compile()
        
        # Run the workflow
        try:
            result = await compiled_graph.ainvoke(initial_state)
            
            self.logger.info(f"SOW workflow completed for client: {client_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in SOW workflow: {str(e)}")
            # Return state with error information
            initial_state.add_message(
                agent="workflow",
                message=f"Workflow error: {str(e)}",
                message_type="error"
            )
            return initial_state
    
    async def resume_after_human_review(
        self,
        state: SOWState,
        human_feedback: Optional[str] = None
    ) -> SOWState:
        """Resume workflow after human review."""
        
        # Update state with human feedback
        state.human_review_completed = True
        if human_feedback:
            state.human_feedback = human_feedback
            state.add_message(
                agent="human_reviewer",
                message=f"Human review completed: {human_feedback}",
                message_type="info"
            )
        
        # Continue with report generation
        report_agent = self.agents["report_generation"]
        final_state = await report_agent.process(state)
        
        self.logger.info(f"SOW workflow resumed and completed for client: {state.client_name}")
        return final_state
    
    def get_workflow_status(self, state: SOWState) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            "client_id": state.client_id,
            "client_name": state.client_name,
            "current_step": state.current_step,
            "progress_percentage": state.get_progress_percentage(),
            "completed_steps": state.completed_steps,
            "needs_human_review": state.needs_human_review,
            "human_review_completed": state.human_review_completed,
            "risk_level": state.risk_assessment.risk_level if state.risk_assessment else None,
            "risk_score": state.risk_assessment.risk_score if state.risk_assessment else None,
        }


def create_sow_workflow(config: Optional[Dict[str, Any]] = None) -> SOWWorkflow:
    """Factory function to create SOW workflow."""
    return SOWWorkflow(config)


# Alternative builder pattern approach
def build_sow_workflow_with_builder() -> WorkflowBuilder:
    """Build SOW workflow using the WorkflowBuilder."""
    
    # Create agents
    id_agent = IDVerificationAgent()
    payslip_agent = PayslipVerificationAgent()
    web_agent = WebReferencesAgent()
    finance_agent = FinancialReportsAgent()
    risk_agent = RiskAssessmentAgent()
    human_agent = HumanAdvisoryAgent()
    report_agent = ReportGenerationAgent()
    
    # Build workflow using builder pattern
    builder = WorkflowBuilder(name="sow_workflow_builder")
    
    workflow = (builder
        .add_agent(id_agent)
        .add_agent(payslip_agent)
        .add_agent(web_agent)
        .add_agent(finance_agent)
        .add_agent(risk_agent)
        .add_agent(human_agent)
        .add_agent(report_agent)
        .connect("id_verification_agent", "payslip_verification_agent")
        .connect("payslip_verification_agent", "web_references_agent")
        .connect("web_references_agent", "financial_reports_agent")
        .connect("financial_reports_agent", "risk_assessment_agent")
        .connect("risk_assessment_agent", "human_advisory_agent")
        .connect("human_advisory_agent", "report_generation_agent")
        .build())
    
    return workflow

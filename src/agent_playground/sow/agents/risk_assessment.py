"""Risk Assessment Agent for Source of Wealth analysis."""

from datetime import datetime
from typing import Dict, Any, Optional, List

from langchain_core.messages import HumanMessage, SystemMessage

from ...core.base import BaseAgent, AgentConfig
from ...utils.logging import get_logger
from ..state import SOWState, RiskAssessmentResult


class RiskAssessmentAgent(BaseAgent):
    """Agent for conducting comprehensive risk assessment."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="risk_assessment_agent",
            description="Conducts comprehensive risk assessment based on all verification results",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: SOWState) -> SOWState:
        """Process risk assessment for the given state."""
        self.logger.info(f"Starting risk assessment for client: {state.client_name}")
        
        try:
            # Ensure we have verification results to assess
            if not self._has_verification_data(state):
                self.logger.warning("Insufficient verification data for risk assessment")
                state.risk_assessment = RiskAssessmentResult(
                    risk_score=100,  # High risk due to lack of data
                    risk_level="high",
                    risk_factors=["Insufficient verification data"],
                    recommendations=["Complete all verification steps before assessment"]
                )
                return state
            
            # Perform risk assessment
            risk_result = await self._conduct_risk_assessment(state)
            state.risk_assessment = risk_result
            
            # Add progress tracking
            state.mark_step_completed("risk_assessment")
            state.add_message(
                agent=self.name,
                message=f"Risk assessment completed: {risk_result.risk_level} risk ({risk_result.risk_score}/100)",
                message_type="info"
            )
            
            self.logger.info(f"Risk assessment completed: {risk_result.risk_level} risk")
            return state
            
        except Exception as e:
            self.logger.error(f"Error in risk assessment: {str(e)}")
            state.risk_assessment = RiskAssessmentResult(
                risk_score=100,
                risk_level="high",
                risk_factors=[f"Assessment error: {str(e)}"],
                recommendations=["Manual review required due to processing error"]
            )
            return state
    
    def _has_verification_data(self, state: SOWState) -> bool:
        """Check if we have sufficient verification data."""
        return any([
            state.id_verification is not None,
            state.payslip_verification is not None,
            state.web_references is not None,
            state.financial_reports is not None
        ])
    
    async def _conduct_risk_assessment(self, state: SOWState) -> RiskAssessmentResult:
        """Conduct comprehensive risk assessment."""
        
        try:
            # Check if we should use mock results
            if self.config.use_mock_results:
                return self._get_mock_result(state.client_id)
            
            # Collect all verification data
            verification_summary = self._compile_verification_summary(state)
            
            # Get AI risk assessment
            system_prompt = self._get_system_prompt()
            human_prompt = self._get_human_prompt(state.client_name, verification_summary)
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            analysis = self._parse_ai_response(response.content)
            
            # Calculate final risk score
            risk_score = self._calculate_risk_score(state, analysis)
            
            return RiskAssessmentResult(
                risk_score=risk_score,
                risk_level=self._determine_risk_level(risk_score),
                risk_factors=analysis.get("risk_factors", []),
                recommendations=analysis.get("recommendations", [])
            )
            
        except Exception as e:
            self.logger.error(f"Error in risk assessment analysis: {str(e)}")
            return RiskAssessmentResult(
                risk_score=80,
                risk_level="high",
                risk_factors=[f"Analysis error: {str(e)}"],
                recommendations=["Manual review required"]
            )
    
    def _compile_verification_summary(self, state: SOWState) -> str:
        """Compile summary of all verification results."""
        summary_parts = []
        
        # ID Verification
        if state.id_verification:
            id_status = "VERIFIED" if state.id_verification.verified else "FAILED"
            summary_parts.append(f"ID Verification: {id_status}")
            if state.id_verification.issues_found:
                summary_parts.append(f"ID Issues: {', '.join(state.id_verification.issues_found)}")
        
        # Payslip Verification
        if state.payslip_verification:
            pay_status = "VERIFIED" if state.payslip_verification.verified else "FAILED"
            summary_parts.append(f"Payslip Verification: {pay_status}")
            if state.payslip_verification.monthly_income:
                summary_parts.append(f"Monthly Income: ${state.payslip_verification.monthly_income:,.2f}")
            if state.payslip_verification.employer:
                summary_parts.append(f"Employer: {state.payslip_verification.employer}")
        
        # Web References
        if state.web_references:
            web_status = "FOUND" if state.web_references.verified else "NOT_FOUND"
            summary_parts.append(f"Web References: {web_status}")
            if state.web_references.risk_flags:
                summary_parts.append(f"Web Risk Flags: {', '.join(state.web_references.risk_flags)}")
        
        # Financial Reports
        if state.financial_reports:
            finance_status = "VERIFIED" if state.financial_reports.verified else "FAILED"
            summary_parts.append(f"Financial Reports: {finance_status}")
            if state.financial_reports.annual_income_range:
                summary_parts.append(f"Annual Income Range: {state.financial_reports.annual_income_range}")
        
        return "\n".join(summary_parts)
    
    def _calculate_risk_score(self, state: SOWState, ai_analysis: Dict[str, Any]) -> int:
        """Calculate numerical risk score (0-100, where 100 is highest risk)."""
        risk_score = 0
        
        # Base score from AI analysis
        ai_score = ai_analysis.get("risk_score", 50)
        risk_score += ai_score * 0.6  # 60% weight to AI assessment
        
        # ID verification impact
        if state.id_verification:
            if not state.id_verification.verified:
                risk_score += 20
            elif state.id_verification.confidence_score < 0.7:
                risk_score += 10
        else:
            risk_score += 25  # No ID verification
        
        # Payslip verification impact
        if state.payslip_verification:
            if not state.payslip_verification.verified:
                risk_score += 15
            elif state.payslip_verification.confidence_score < 0.7:
                risk_score += 8
        else:
            risk_score += 20  # No payslip verification
        
        # Web references impact
        if state.web_references and state.web_references.risk_flags:
            risk_score += len(state.web_references.risk_flags) * 5
        
        # Cap at 100
        return min(int(risk_score), 100)
    
    def _determine_risk_level(self, risk_score: int) -> str:
        """Determine risk level from numerical score."""
        if risk_score >= 70:
            return "high"
        elif risk_score >= 40:
            return "medium"
        elif risk_score >= 20:
            return "low"
        else:
            return "very_low"
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for risk assessment."""
        return """
        You are an expert risk assessment agent for Source of Wealth verification. Your task is to analyze all verification results and provide a comprehensive risk assessment.
        
        Please analyze the verification data and return a JSON response with the following structure:
        {
            "risk_score": integer (0-100, where 100 is highest risk),
            "risk_factors": [list of identified risk factors],
            "recommendations": [list of recommended actions],
            "analysis": "detailed analysis explanation"
        }
        
        Consider these factors:
        - Document authenticity and verification status
        - Income consistency and verification
        - Web presence and reputation
        - Financial history and stability
        - Any discrepancies or red flags
        - Missing or incomplete information
        
        Risk levels:
        - 0-19: Very Low Risk
        - 20-39: Low Risk  
        - 40-69: Medium Risk
        - 70-100: High Risk
        """
    
    def _get_human_prompt(self, client_name: str, verification_summary: str) -> str:
        """Get human prompt for risk assessment."""
        return f"""
        Please conduct a comprehensive risk assessment for client: {client_name}
        
        Verification Summary:
        {verification_summary}
        
        Assess the overall risk level considering:
        1. Are all required documents verified successfully?
        2. Are there any inconsistencies in the data?
        3. What are the potential risk factors?
        4. What additional verification might be needed?
        5. What is the recommended course of action?
        
        Provide your assessment in the JSON format specified in the system prompt.
        """
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured data."""
        try:
            import json
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return {
                    "risk_score": 50,
                    "risk_factors": ["Could not parse structured response"],
                    "recommendations": ["Manual review recommended"],
                    "analysis": response
                }
        except json.JSONDecodeError:
            return {
                "risk_score": 60,
                "risk_factors": ["Invalid response format"],
                "recommendations": ["Manual review required"],
                "analysis": "Failed to parse AI response"
            }
    
    def _get_mock_result(self, client_id: str) -> RiskAssessmentResult:
        """Get mock risk assessment result for testing."""
        mock_data = {
            "12345": {
                "risk_score": 25,
                "risk_level": "low",
                "risk_factors": [
                    "All documents verified successfully",
                    "Income levels are consistent",
                    "No negative web references found"
                ],
                "recommendations": [
                    "Approved for processing",
                    "Standard monitoring recommended"
                ]
            }
        }
        
        data = mock_data.get(client_id, {
            "risk_score": 70,
            "risk_level": "high",
            "risk_factors": ["Mock data not available for this client"],
            "recommendations": ["Complete manual review required"]
        })
        
        return RiskAssessmentResult(**data)
    
    def get_node_config(self) -> Dict[str, Any]:
        """Get LangGraph node configuration."""
        return {
            "name": self.name,
            "function": self.process,
            "input_schema": SOWState,
            "output_schema": SOWState,
        }

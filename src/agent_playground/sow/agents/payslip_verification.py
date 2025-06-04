"""Payslip Verification Agent for Source of Wealth analysis."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from ...core.base import BaseAgent, AgentConfig
from ...utils.logging import get_logger
from ..state import SOWState, PayslipVerificationResult


class PayslipVerificationAgent(BaseAgent):
    """Agent for verifying payslip documents."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="payslip_verification_agent",
            description="Analyzes and verifies payslip documents for income verification",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: SOWState) -> SOWState:
        """Process payslip verification for the given state."""
        self.logger.info(f"Starting payslip verification for client: {state.client_name}")
        
        try:
            # Check if payslip document path is provided
            if not state.payslip_document_path:
                self.logger.warning("No payslip document path provided")
                state.payslip_verification = PayslipVerificationResult(
                    verified=False,
                    issues_found=["No payslip document provided"]
                )
                return state
            
            # Verify document exists
            doc_path = Path(state.payslip_document_path)
            if not doc_path.exists():
                self.logger.error(f"Payslip document not found: {state.payslip_document_path}")
                state.payslip_verification = PayslipVerificationResult(
                    verified=False,
                    issues_found=[f"Document not found: {state.payslip_document_path}"]
                )
                return state
            
            # Process the document
            verification_result = await self._analyze_payslip_document(doc_path, state)
            state.payslip_verification = verification_result
            
            # Add progress tracking
            state.mark_step_completed("payslip_verification")
            state.add_message(
                agent=self.name,
                message=f"Payslip verification completed with result: {verification_result.verified}",
                message_type="success" if verification_result.verified else "warning"
            )
            
            self.logger.info(f"Payslip verification completed: {verification_result.verified}")
            return state
            
        except Exception as e:
            self.logger.error(f"Error in payslip verification: {str(e)}")
            state.payslip_verification = PayslipVerificationResult(
                verified=False,
                issues_found=[f"Processing error: {str(e)}"]
            )
            return state
    
    async def _analyze_payslip_document(self, doc_path: Path, state: SOWState) -> PayslipVerificationResult:
        """Analyze the payslip document using AI model."""
        
        try:
            # Check if we should use mock results (for testing)
            if self.config.use_mock_results:
                return self._get_mock_result(state.client_id)
            
            # Extract text from document (assuming PDF/image processing)
            document_text = await self._extract_document_text(doc_path)
            
            # Prepare AI prompt
            system_prompt = self._get_system_prompt()
            human_prompt = self._get_human_prompt(state.client_name, document_text)
            
            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            # Get AI analysis
            response = await self.llm.ainvoke(messages)
            analysis = self._parse_ai_response(response.content)
            
            # Create verification result
            return PayslipVerificationResult(
                verified=analysis.get("verified", False),
                confidence_score=analysis.get("confidence", 0.0),
                monthly_income=analysis.get("monthly_income"),
                employer=analysis.get("employer"),
                position=analysis.get("position"),
                pay_period=analysis.get("pay_period"),
                deductions=analysis.get("deductions", {}),
                issues_found=analysis.get("issues", [])
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing payslip document: {str(e)}")
            return PayslipVerificationResult(
                verified=False,
                issues_found=[f"Analysis error: {str(e)}"]
            )
    
    async def _extract_document_text(self, doc_path: Path) -> str:
        """Extract text from document (placeholder for OCR/PDF parsing)."""
        # This would integrate with PyMuPDF, OCR, or other text extraction tools
        # For now, return a placeholder
        try:
            if doc_path.suffix.lower() == '.pdf':
                # TODO: Implement PDF text extraction
                return f"[PDF content from {doc_path.name}]"
            else:
                # TODO: Implement OCR for images
                return f"[Image content from {doc_path.name}]"
        except Exception as e:
            raise Exception(f"Failed to extract text from document: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for payslip verification."""
        return """
        You are an expert payslip verification agent. Your task is to analyze payslip documents and extract relevant employment and income information.
        
        Please analyze the provided payslip document and return a JSON response with the following structure:
        {
            "verified": boolean,
            "confidence": float (0.0-1.0),
            "monthly_income": float,
            "employer": string,
            "position": string,
            "pay_period": string,
            "deductions": {
                "tax": float,
                "social_security": float,
                "other": float
            },
            "issues": [list of any issues found]
        }
        
        Look for:
        - Employer name and authenticity
        - Employee name matching
        - Gross and net pay amounts
        - Pay period (weekly, bi-weekly, monthly)
        - Tax and other deductions
        - Consistency in formatting and data
        - Any signs of tampering or forgery
        """
    
    def _get_human_prompt(self, client_name: str, document_text: str) -> str:
        """Get human prompt for payslip verification."""
        return f"""
        Please analyze this payslip document for client: {client_name}
        
        Document content:
        {document_text}
        
        Verify:
        1. Is this a legitimate payslip document?
        2. Does the employee name match the client name?
        3. What is the monthly income (calculate if needed)?
        4. Who is the employer and what position does the client hold?
        5. Are the deductions reasonable and properly calculated?
        6. Are there any inconsistencies or suspicious elements?
        
        Provide your analysis in the JSON format specified in the system prompt.
        """
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured data."""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing with regex
                income_match = re.search(r'income[:\s]+(\d+[.,]\d+|\d+)', response, re.IGNORECASE)
                employer_match = re.search(r'employer[:\s]+([^\n]+)', response, re.IGNORECASE)
                
                return {
                    "verified": "valid" in response.lower() or "legitimate" in response.lower(),
                    "confidence": 0.5,
                    "monthly_income": float(income_match.group(1).replace(',', '')) if income_match else None,
                    "employer": employer_match.group(1).strip() if employer_match else None,
                    "issues": ["Could not parse structured response"]
                }
        except (json.JSONDecodeError, ValueError) as e:
            return {
                "verified": False,
                "confidence": 0.0,
                "issues": [f"Invalid response format: {str(e)}"]
            }
    
    def _get_mock_result(self, client_id: str) -> PayslipVerificationResult:
        """Get mock verification result for testing."""
        mock_data = {
            "12345": {
                "verified": True,
                "confidence_score": 0.92,
                "monthly_income": 5500.0,
                "employer": "Tech Corp Inc.",
                "position": "Software Engineer",
                "pay_period": "monthly",
                "deductions": {
                    "tax": 1100.0,
                    "social_security": 330.0,
                    "health_insurance": 200.0
                },
                "issues_found": []
            }
        }
        
        data = mock_data.get(client_id, {
            "verified": False,
            "confidence_score": 0.0,
            "issues_found": ["Mock data not available for this client"]
        })
        
        return PayslipVerificationResult(**data)
    
    def get_node_config(self) -> Dict[str, Any]:
        """Get LangGraph node configuration."""
        return {
            "name": self.name,
            "function": self.process,
            "input_schema": SOWState,
            "output_schema": SOWState,
        }

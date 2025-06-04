"""ID Verification Agent for Source of Wealth analysis."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import base64
import json

from langchain_core.messages import HumanMessage, SystemMessage
from PIL import Image

from ...core.base import BaseAgent, AgentConfig
from ...utils.logging import get_logger
from ..state import SOWState, IDVerificationResult


class IDVerificationAgent(BaseAgent):
    """Agent for verifying identity documents."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="id_verification_agent",
            description="Analyzes and verifies identity documents for SOW analysis",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: SOWState) -> SOWState:
        """Process ID verification for the given state."""
        self.logger.info(f"Starting ID verification for client: {state.client_name}")
        
        try:
            # Check if ID document path is provided
            if not state.id_document_path:
                self.logger.warning("No ID document path provided")
                state.id_verification = IDVerificationResult(
                    verified=False,
                    issues_found=["No ID document provided"]
                )
                return state
            
            # Verify document exists
            doc_path = Path(state.id_document_path)
            if not doc_path.exists():
                self.logger.error(f"ID document not found: {state.id_document_path}")
                state.id_verification = IDVerificationResult(
                    verified=False,
                    issues_found=[f"Document not found: {state.id_document_path}"]
                )
                return state
            
            # Process the document
            verification_result = await self._analyze_id_document(doc_path, state)
            state.id_verification = verification_result
            
            # Add progress tracking
            state.mark_step_completed("id_verification")
            state.add_message(
                agent=self.name,
                message=f"ID verification completed with result: {verification_result.verified}",
                message_type="success" if verification_result.verified else "warning"
            )
            
            self.logger.info(f"ID verification completed: {verification_result.verified}")
            return state
            
        except Exception as e:
            self.logger.error(f"Error in ID verification: {str(e)}")
            state.id_verification = IDVerificationResult(
                verified=False,
                issues_found=[f"Processing error: {str(e)}"]
            )
            return state
    
    async def _analyze_id_document(self, doc_path: Path, state: SOWState) -> IDVerificationResult:
        """Analyze the ID document using AI model."""
        
        try:
            # Check if we should use mock results (for testing)
            if self.config.use_mock_results:
                return self._get_mock_result(state.client_id)
            
            # Read and encode image
            image_data = self._encode_image(doc_path)
            
            # Prepare AI prompt
            system_prompt = self._get_system_prompt()
            human_prompt = self._get_human_prompt(state.client_name)
            
            # Create messages for vision model
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=[
                    {"type": "text", "text": human_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                    }
                ])
            ]
            
            # Get AI analysis
            response = await self.llm.ainvoke(messages)
            analysis = self._parse_ai_response(response.content)
            
            # Create verification result
            return IDVerificationResult(
                verified=analysis.get("verified", False),
                confidence_score=analysis.get("confidence", 0.0),
                id_type=analysis.get("id_type"),
                document_quality=analysis.get("quality", "unknown"),
                extracted_info=analysis.get("extracted_info", {}),
                issues_found=analysis.get("issues", [])
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing ID document: {str(e)}")
            return IDVerificationResult(
                verified=False,
                issues_found=[f"Analysis error: {str(e)}"]
            )
    
    def _encode_image(self, image_path: Path) -> str:
        """Encode image to base64."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to encode image: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for ID verification."""
        return """
        You are an expert ID verification agent. Your task is to analyze identity documents and determine their authenticity and validity.
        
        Please analyze the provided ID document and return a JSON response with the following structure:
        {
            "verified": boolean,
            "confidence": float (0.0-1.0),
            "id_type": string,
            "quality": string ("excellent", "good", "fair", "poor"),
            "extracted_info": {
                "name": string,
                "date_of_birth": string,
                "id_number": string,
                "expiry_date": string,
                "issuing_authority": string
            },
            "issues": [list of any issues found]
        }
        
        Look for:
        - Document authenticity indicators
        - Photo quality and matching
        - Text clarity and consistency
        - Security features (if visible)
        - Expiry date validity
        - Any signs of tampering or forgery
        """
    
    def _get_human_prompt(self, client_name: str) -> str:
        """Get human prompt for ID verification."""
        return f"""
        Please analyze this ID document for client: {client_name}
        
        Verify:
        1. Is this a valid, authentic identity document?
        2. Is the document clear and readable?
        3. Does the name match the provided client name?
        4. Is the document expired?
        5. Are there any suspicious elements?
        
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
                # Fallback parsing
                return {
                    "verified": "valid" in response.lower() or "authentic" in response.lower(),
                    "confidence": 0.5,
                    "issues": ["Could not parse structured response"]
                }
        except json.JSONDecodeError:
            return {
                "verified": False,
                "confidence": 0.0,
                "issues": ["Invalid response format"]
            }
    
    def _get_mock_result(self, client_id: str) -> IDVerificationResult:
        """Get mock verification result for testing."""
        mock_data = {
            "12345": {
                "verified": True,
                "confidence_score": 0.95,
                "id_type": "Driver's License",
                "document_quality": "excellent",
                "extracted_info": {
                    "name": "John Doe",
                    "date_of_birth": "1990-01-01",
                    "id_number": "DL123456789",
                    "expiry_date": "2026-01-01"
                },
                "issues_found": []
            }
        }
        
        data = mock_data.get(client_id, {
            "verified": False,
            "confidence_score": 0.0,
            "issues_found": ["Mock data not available for this client"]
        })
        
        return IDVerificationResult(**data)
    
    def get_node_config(self) -> Dict[str, Any]:
        """Get LangGraph node configuration."""
        return {
            "name": self.name,
            "function": self.process,
            "input_schema": SOWState,
            "output_schema": SOWState,
        }

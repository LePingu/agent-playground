import asyncio
from datetime import datetime
from io import BytesIO
import os
import base64
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage, SystemMessage, ChatMessage
from PIL import Image

from source_of_wealth_agent.core.mock_results.id_verification_results import get_mock_id_verification_result
from source_of_wealth_agent.core.state import log_action, AgentState # Added AgentState

class IDVerificationAgent:
    def __init__(self, model):
        self.name = "ID_Verification_Agent"
        self.model = model
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        
        # Configure handler if not already set up
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
        # Set up ID document storage location
        self.id_docs_path = Path(os.environ.get("ID_DOCS_PATH", "/workspaces/agent-playground/source_of_wealth_agent/data/id_documents"))
        os.makedirs(self.id_docs_path, exist_ok=True)

    def encode_image(self, image_path: str) -> Optional[str]:
        """Encode image file to base64"""
        try:

            pil_image = Image.open(image_path)
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG")  # You can change the format if needed
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            # with open(image_path, "rb") as image_file:
            return img_str
        except Exception as e:
            self.logger.error(f"Error encoding image {image_path}: {str(e)}")
            return None

    def find_id_document(self, client_id: str) -> Optional[str]:
        """Find ID document for the given client_id"""
        # Look for common ID document formats
        extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        
        for ext in extensions:
            file_path = self.id_docs_path / f"{client_id}_id{ext}"
            if file_path.exists():
                return str(file_path)
                
        # If no exact match, try looking for any file containing the client_id
        for file in self.id_docs_path.glob(f"*{client_id}*"):
            if file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.pdf']:
                return str(file)
                
        return None

    async def extract_id_information(self, image_path: str) -> Dict[str, Any]:
        """Use Ollama Llama model to extract information from ID document"""
        # base64_image = await asyncio.to_thread(self.encode_image(image_path))
        # if not base64_image:
        #     return {"verified": False, "error": "Failed to encode image"}
        base64_image = None
        try:
            # Create prompt for vision model
            system_prompt = """You are an expert ID document analyzer. 
            Extract the following information from the ID document image:
            1. Document type (Passport, Driver's License, National ID, etc.)
            2. Full name
            3. Date of birth
            4. Nationality
            5. Document number
            6. Issue date
            7. Expiry date
            8. Any security features you can identify
            9. Potential issues or signs of tampering
            
            Format your response as JSON with the following structure:
            {
                "document_type": "string",
                "full_name": "string",
                "date_of_birth": "YYYY-MM-DD",
                "nationality": "string",
                "document_number": "string",
                "issue_date": "YYYY-MM-DD",
                "expiry_date": "YYYY-MM-DD",
                "security_features": ["feature1", "feature2"],
                "potential_issues": ["issue1", "issue2"] 
            }"""
            
            # Call the model with image content
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=[
                    {"type": "text", "text": "Please analyze this ID document image and extract the required information."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}} # Ensure correct MIME type
                ])
            ]
            
            # Use bind for image content if needed
            if hasattr(self.model, 'bind'):
                llm_with_image_context = self.model.bind(images=[base64_image])
                response = await llm_with_image_context.ainvoke(system_prompt + "\n\nPlease analyze this ID document image and extract the required information.")
            else:
                response = await self.model.ainvoke(messages)
            
            # Extract JSON from the response
            content = response.content if hasattr(response, 'content') else response
            
            # Look for JSON in the content (it might be wrapped in markdown code blocks)
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
                
            extracted_data = json.loads(json_str)
            self.logger.info(f"Successfully extracted information from ID document {image_path}")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error extracting information from ID: {str(e)}")
            return {"verified": False, "error": str(e)}

    async def verify_id(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify the extracted ID information"""
        issues_found = []
        
        # Check for required fields
        required_fields = ["full_name", "date_of_birth", "document_number", "expiry_date"]
        for field in required_fields:
            if field not in extracted_data or not extracted_data[field]:
                issues_found.append(f"Missing {field.replace('_', ' ')}")
        
        # Check expiry date
        if "expiry_date" in extracted_data and extracted_data["expiry_date"]:
            try:
                expiry_date = datetime.strptime(extracted_data["expiry_date"], "%Y-%m-%d")
                if expiry_date < datetime.now():
                    issues_found.append("ID document has expired")
            except ValueError:
                issues_found.append("Invalid expiry date format")
        
        # Add any issues identified by the model
        if "potential_issues" in extracted_data and extracted_data["potential_issues"]:
            issues_found.extend(extracted_data["potential_issues"])
        
        # Prepare verification result
        verification_result = {
            # "verified": len(issues_found) == 0,
            "verified": False,
            "id_type": extracted_data.get("document_type", "Unknown"),
            "full_name": extracted_data.get("full_name", "Unknown"),
            "date_of_birth": extracted_data.get("date_of_birth", "Unknown"),
            "document_number": extracted_data.get("document_number", "Unknown"),
            "id_expiry": extracted_data.get("expiry_date", "Unknown"),
            "issues_found": issues_found,
            "verification_date": datetime.now().isoformat()
        }
        
        return verification_result

    async def run(self, state: AgentState) -> AgentState: # Updated type hint for state
        client_id = state["client_id"]
        client_name = state.get("client_name", "Unknown")
        self.logger.info(f"🔍 Verifying ID for client: {client_id} ({client_name})")
        
        # Step 1: Find the ID document for this client
        id_document_path = self.find_id_document(client_id)
        if not id_document_path:
            self.logger.warning(f"No ID document found for client {client_id}")
            # Create dummy verification result for testing/demo purposes when no document is available
            verification_result = {
                "verified": False,
                "id_expiry": "2028-05-13",
                "id_type": "Passport",
                "issues_found": ["No ID document found"],
                "verification_date": datetime.now().isoformat()
            }
        else:
            if state.get('mocked'):
                verification_result = get_mock_id_verification_result(client_id="12345", client_name="Hatim Nourbay")
            else:
                # Step 2: Extract information from the ID document
                extracted_data = await self.extract_id_information(id_document_path)

                # Step 3: Verify the extracted information
                verification_result = await self.verify_id(extracted_data)

            # Step 4: Log action and prepare for potential human review by orchestrator
            # The 'verified' status here is based on automated checks.
            # Human review will be handled by the HumanAdvisoryAgent if routed by the orchestrator.
            self.logger.info(f"Automated ID verification completed for client {client_id}. Issues found: {verification_result.get('issues_found')}")

        # Step 5: Update state with verification result
        state["id_verification"] = verification_result
        log_action(self.name, "ID verification automated checks completed", verification_result)
        
        return state
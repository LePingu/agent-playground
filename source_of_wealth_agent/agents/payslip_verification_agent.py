from datetime import datetime
import os
import logging
import base64
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import io
import re

# Import libraries for PDF processing
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from source_of_wealth_agent.core.state import log_action, AgentState, request_human_review # Added request_human_review

class PayslipVerificationAgent:
    def __init__(self, model):
        self.name = "Payslip_Verification_Agent"
        self.model = model
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        
        # Configure handler if not already set up
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Set up payslip document storage location
        self.payslip_docs_path = Path(os.environ.get("PAYSLIP_DOCS_PATH", "/workspaces/agent-playground/source_of_wealth_agent/data/payslip_documents"))
        os.makedirs(self.payslip_docs_path, exist_ok=True)
        
        # Check if PDF processing is available
        if fitz is None:
            self.logger.warning("PyMuPDF (fitz) is not installed. PDF processing will be limited.")
            self.logger.warning("Install with: pip install pymupdf")

    def queue_payslip_review(self, verification_result: Dict[str, Any], client_id: str) -> Dict[str, Any]:
        """Queue a non-blocking human review request for payslip verification.
        
        Args:
            verification_result: The payslip verification result containing issues
            client_id: Client ID for the review
            
        Returns:
            Dictionary with review request details
        """
        self.logger.info(f"Queueing payslip review for client {client_id}")
        
        # Use the request_human_review function to add to pending reviews
        return request_human_review(
            verification_type="payslip_verification_review",
            client_id=client_id,
            verification_data=verification_result,
            issues=verification_result.get("issues_found", [])
        )

    def find_payslip_document(self, client_id: str) -> Optional[str]:
        """Find payslip document for the given client_id"""
        # Look for common document formats
        extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        
        for ext in extensions:
            file_path = self.payslip_docs_path / f"{client_id}_payslip{ext}"
            if file_path.exists():
                return str(file_path)
                
        # If no exact match, try looking for any file containing the client_id
        for file in self.payslip_docs_path.glob(f"*{client_id}*"):
            if file.suffix.lower() in ['.pdf', '.jpg', '.jpeg', '.png']:
                return str(file)
                
        return None

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF file"""
        if fitz is None:
            self.logger.error("PyMuPDF not installed, cannot extract text from PDF")
            return "ERROR: PyMuPDF not installed"
            
        try:
            text = ""
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
                
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            return f"Error: {str(e)}"

    def encode_document(self, doc_path: str) -> Optional[str]:
        """Encode document file to base64"""
        try:
            with open(doc_path, "rb") as file:
                return base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error encoding document {doc_path}: {str(e)}")
            return None

    async def extract_payslip_information(self, doc_path: str) -> Dict[str, Any]:
        """Extract information from payslip using the model"""
        # First try to extract text from PDF
        extracted_text = ""
        if doc_path.lower().endswith('.pdf') and fitz is not None:
            extracted_text = self.extract_text_from_pdf(doc_path)
        
        # Encode document for vision model if needed
        base64_doc = None
        if not extracted_text or len(extracted_text) < 100:  # If text extraction failed or yielded little text
            base64_doc = self.encode_document(doc_path)
            
        if not extracted_text and not base64_doc:
            return {"verified": False, "error": "Failed to process document"}
            
        try:
            # Create prompt for model
            system_prompt = """You are an expert payslip analyzer. 
            Extract the following information from the payslip document:
            1. Employee name
            2. Employer/company name
            3. Position/job title
            4. Gross pay amount
            5. Net pay amount
            6. Pay period (month/date)
            7. Tax deductions
            8. Other deductions
            9. Year-to-date figures if available
            10. Any potential issues or inconsistencies
            
            Format your response as JSON with the following structure:
            {
                "employee_name": "string",
                "employer": "string",
                "position": "string",
                "gross_pay": "number",
                "net_pay": "number",
                "pay_period": "string",
                "tax_deductions": "number",
                "other_deductions": "number",
                "ytd_gross": "number",
                "ytd_net": "number",
                "currency": "string",
                "issues_found": ["issue1", "issue2"]
            }"""
            
            if base64_doc:
                # Use vision model capabilities
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Please analyze this payslip document and extract the required information."},
                        {"type": "image_url", "image_url": {"url": f"data:application/pdf;base64,{base64_doc}"}}
                    ]}
                ]
                
                # Use bind for image content if needed
                if hasattr(self.model, 'bind'):
                    llm_with_doc_context = self.model.bind(images=[base64_doc])
                    response = await llm_with_doc_context.ainvoke(system_prompt + "\n\nPlease analyze this payslip document and extract the required information.")
                else:
                    response = await self.model.ainvoke(messages)
            else:
                # Use text only if we have extracted text
                prompt = f"{system_prompt}\n\nHere is the extracted text from the payslip:\n\n{extracted_text}\n\nPlease analyze this text and extract the required information."
                response = await self.model.ainvoke(prompt)
            
            # Extract JSON from the response
            content = response.content if hasattr(response, 'content') else response
            
            # Look for JSON in the content (it might be wrapped in markdown code blocks)
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
                
            # Try to convert string values to numeric values where appropriate
            extracted_data = json.loads(json_str)
            
            # Convert financial figures to numbers if they're strings
            for field in ["gross_pay", "net_pay", "tax_deductions", "other_deductions", "ytd_gross", "ytd_net"]:
                if field in extracted_data and isinstance(extracted_data[field], str):
                    # Try to extract numeric value
                    numeric_str = re.sub(r'[^\d.]', '', extracted_data[field])
                    try:
                        extracted_data[field] = float(numeric_str) if numeric_str else 0
                    except ValueError:
                        pass  # Keep as string if conversion fails
            
            self.logger.info(f"Successfully extracted information from payslip document")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error extracting information from payslip: {str(e)}")
            return {"verified": False, "error": str(e)}

    def verify_payslip(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify the extracted payslip information"""
        issues_found = []
        
        # Check for required fields
        required_fields = ["employee_name", "employer", "gross_pay", "net_pay"]
        for field in required_fields:
            if field not in extracted_data or not extracted_data[field]:
                issues_found.append(f"Missing {field.replace('_', ' ')}")
        
        # Check if net pay is less than gross pay
        if "gross_pay" in extracted_data and "net_pay" in extracted_data:
            if isinstance(extracted_data["gross_pay"], (int, float)) and isinstance(extracted_data["net_pay"], (int, float)):
                if extracted_data["net_pay"] > extracted_data["gross_pay"]:
                    issues_found.append("Net pay is greater than gross pay")
        
        # Add any issues identified by the model
        if "issues_found" in extracted_data and extracted_data["issues_found"]:
            issues_found.extend(extracted_data["issues_found"])
        
        # Calculate monthly income from the extracted data
        monthly_income = None
        if "pay_period" in extracted_data and "gross_pay" in extracted_data:
            pay_period = extracted_data.get("pay_period", "").lower()
            gross_pay = extracted_data["gross_pay"]
            
            if isinstance(gross_pay, (int, float)):
                if "week" in pay_period:
                    monthly_income = gross_pay * 4.33  # Average weeks in a month
                elif "bi-week" in pay_period or "fortnight" in pay_period:
                    monthly_income = gross_pay * 2.17  # Bi-weekly to monthly
                elif "month" in pay_period:
                    monthly_income = gross_pay  # Already monthly
                elif "year" in pay_period or "annual" in pay_period:
                    monthly_income = gross_pay / 12  # Annual to monthly
            
        # Prepare verification result
        verification_result = {
            "verified": len(issues_found) == 0,
            "monthly_income": monthly_income or extracted_data.get("gross_pay", 0),
            "employer": extracted_data.get("employer", "Unknown"),
            "position": extracted_data.get("position", "Unknown"),
            "employee_name": extracted_data.get("employee_name", "Unknown"),
            "gross_pay": extracted_data.get("gross_pay", 0),
            "net_pay": extracted_data.get("net_pay", 0),
            "pay_period": extracted_data.get("pay_period", "Unknown"),
            "issues_found": issues_found,
            "verification_date": datetime.now().isoformat()
        }
        
        return verification_result

    async def run(self, state: AgentState) -> AgentState: # Updated type hint for state
        client_id = state["client_id"]
        client_name = state.get("client_name", "Unknown")
        self.logger.info(f"📄 Verifying payslips for client: {client_id} ({client_name})")
        
        # Step 1: Find the payslip document for this client
        payslip_path = self.find_payslip_document(client_id)
        if not payslip_path:
            self.logger.warning(f"No payslip document found for client {client_id}")
            # Create dummy verification result for testing/demo purposes when no document is available
            verification_result = {
                "verified": False,
                "monthly_income": 15000,  # Sample value for demo
                "employer": "Global Bank Ltd",
                "position": "Senior Manager",
                "issues_found": ["No payslip document found"],
                "verification_date": datetime.now().isoformat()
            }
        else:
            # Step 2: Extract information from the payslip document
            extracted_data = await self.extract_payslip_information(payslip_path)
            
            # Step 3: Verify the extracted information
            verification_result = self.verify_payslip(extracted_data)

        # Step 3.5: Queue non-blocking human review if issues are found
        if verification_result.get("issues_found"):
            self.logger.info(f"Issues found in payslip for client {client_id}. Queueing human review.")
            
            # Queue the review in the state without blocking
            review_request = self.queue_payslip_review(verification_result, client_id)
            
            # Add the review request to state
            if "pending_reviews" not in state:
                state["pending_reviews"] = []
            state["pending_reviews"].extend(review_request.get("pending_reviews", []))
            
            # Mark verification result as requiring review
            verification_result["requires_human_review"] = True
            verification_result["verified"] = False  # Default to false until reviewed
            
            # Log the action
            log_update = log_action(self.name, f"Payslip review queued for client {client_id}", 
                        {"issues": verification_result.get("issues_found", [])})
            
            # Add log update to state
            if "audit_log" in log_update:
                if "audit_log" not in state:
                    state["audit_log"] = []
                state["audit_log"].extend(log_update["audit_log"])


        # Step 4: Update state with verification result
        state["payslip_verification"] = verification_result
        log_action(self.name, "Payslip verification completed", verification_result)
        return state
"""
Mock model implementations for testing various agents in the source of wealth system.
"""
import asyncio
import json
from typing import Any, Dict, List, Mapping, Optional, Type
from langchain_ollama import OllamaLLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import HumanMessage, SystemMessage

class BaseMockResponse:
    """
    Base class for mock responses that simulate the response from OllamaLLM.
    """
    def __init__(self, client_id=None, client_name=None, **kwargs):
        self.client_id = client_id
        self.client_name = client_name
        self.kwargs = kwargs
        
        # Subclasses should define these
        self.verified_content = ""
        self.unverified_content = ""
        
        # Initialize response content
        self._initialize_content()
    
    def _initialize_content(self):
        """Initialize the response content. Override in subclasses."""
        pass
    
    def _is_verified_client(self):
        """Check if this is a verified client based on ID and name."""
        return self.client_id == "12345" and self.client_name == "Hatim Nourbay"
    
    async def ainvoke(self, *args, **kwargs):
        """Simulate the async invoke method of OllamaLLM with predetermined response."""
        if self._is_verified_client():
            return self.verified_content
        else:
            return self.unverified_content
            
    @property
    def content(self):
        """Return content property for compatibility with some callers."""
        if self._is_verified_client():
            return self.verified_content
        else:
            return self.unverified_content

class MockVerifiedIDResponse(BaseMockResponse):
    """
    A mock class that simulates the response from OllamaLLM for ID verification.
    This mock returns a verified ID response for client ID 12345 with name Hatim Nourbay.
    """
    def _initialize_content(self):
        """Initialize the ID verification response content."""
        self.verified_content = """```json
{
    "document_type": "Passport",
    "full_name": "Hatim Nourbay",
    "date_of_birth": "1990-06-22",
    "nationality": "France",
    "document_number": "AB123456",
    "issue_date": "2020-01-15",
    "expiry_date": "2030-01-15",
    "security_features": ["Hologram", "Microprint", "UV Reactive Ink", "Machine Readable Zone"],
    "potential_issues": []
}
```"""
        self.unverified_content = """```json
{
    "document_type": "Unknown",
    "full_name": "",
    "date_of_birth": "",
    "nationality": "",
    "document_number": "",
    "issue_date": "",
    "expiry_date": "",
    "security_features": [],
    "potential_issues": ["Document not found", "Unable to verify identity"]
}
```"""

class MockWebReferencesResponse(BaseMockResponse):
    """
    A mock class that simulates the response from OllamaLLM for web references verification.
    """
    def _initialize_content(self):
        """Initialize the web references response content."""
        employer = self.kwargs.get("employer", "Global Bank Ltd")
        
        self.verified_content = f"""```json
{{
    "verified": true,
    "mentions": [
        {{
            "source": "LinkedIn",
            "url": "https://www.linkedin.com/in/hatim-nourbay-12345/",
            "details": "Profile for Hatim Nourbay, Senior Investment Manager at {employer}"
        }},
        {{
            "source": "Bloomberg",
            "url": "https://www.bloomberg.com/news/articles/2024-03-15/financial-sector-growth",
            "details": "{employer} announces expansion plans, quotes from senior management"
        }},
        {{
            "source": "Sentiment Analysis Summary",
            "details": "Analysis of web mentions for Hatim Nourbay shows predominantly positive sentiment. Professional reputation appears strong, particularly in relation to role at {employer}.",
            "sentiment": "Positive",
            "confidence": 0.85
        }}
    ],
    "risk_flags": [],
    "search_date": "2025-05-19T03:47:00Z"
}}
```"""
        self.unverified_content = f"""```json
{{
    "verified": false,
    "mentions": [
        {{
            "source": "LinkedIn",
            "url": "https://www.linkedin.com/in/unknown-profile/",
            "details": "No matching profile found"
        }},
        {{
            "source": "Financial Times",
            "url": "https://www.ft.com/content/financial-sector-investigation",
            "details": "Investigation into financial sector practices mentions several institutions"
        }},
        {{
            "source": "Sentiment Analysis Summary",
            "details": "Insufficient data to perform sentiment analysis",
            "sentiment": "Unknown",
            "confidence": 0.0
        }}
    ],
    "risk_flags": ["No verifiable online presence", "Inconsistent employment history"],
    "search_date": "2025-05-19T03:47:00Z"
}}
```"""

class MockFinancialReportsResponse(BaseMockResponse):
    """
    A mock class that simulates the response from OllamaLLM for financial reports verification.
    """
    def _initialize_content(self):
        """Initialize the financial reports response content."""
        annual_income = self.kwargs.get("annual_income_range", "100,000 - 200,000")
        investment_assets = self.kwargs.get("investment_assets", "500,000+")
        
        self.verified_content = f"""```json
{{
    "verified": true,
    "reports_analyzed": ["Credit Report", "Investment Portfolio", "Tax Returns"],
    "annual_income_range": "{annual_income}",
    "investment_assets": "{investment_assets}",
    "credit_score": "Excellent",
    "issues_found": [],
    "detailed_analysis": {{
        "credit_report": {{
            "score": 800,
            "payment_history": "Excellent",
            "utilization": "Low",
            "derogatory_marks": 0
        }},
        "investment_portfolio": {{
            "asset_classes": ["Stocks", "Bonds", "Real Estate", "Alternative Investments"],
            "diversification": "Well diversified",
            "risk_profile": "Moderate"
        }},
        "tax_returns": {{
            "years_analyzed": ["2022", "2023", "2024"],
            "income_consistency": "High",
            "income_sources": ["Employment", "Investments", "Rental Income"],
            "tax_compliance": "Compliant"
        }}
    }},
    "analysis_date": "2025-05-19T03:47:00Z"
}}
```"""
        self.unverified_content = f"""```json
{{
    "verified": false,
    "reports_analyzed": ["Credit Report", "Investment Portfolio", "Tax Returns"],
    "annual_income_range": "{annual_income}",
    "investment_assets": "{investment_assets}",
    "credit_score": "Fair",
    "issues_found": ["Inconsistent income reporting across documents", "Unexplained large transactions"],
    "analysis_date": "2025-05-19T03:47:00Z"
}}
```"""

class MockPayslipsResponse(BaseMockResponse):
    """
    A mock class that simulates the response from OllamaLLM for payslips extraction.
    """
    def _initialize_content(self):
        """Initialize the payslips response content."""
        employer = self.kwargs.get("employer", "Global Bank Ltd")
        position = self.kwargs.get("position", "Senior Manager")
        monthly_income = self.kwargs.get("monthly_income", 15000.0)
        
        self.verified_content = f"""```json
{{
    "verified": true,
    "monthly_income": {monthly_income},
    "employer": "{employer}",
    "position": "{position}",
    "employee_name": "{self.client_name or f'Client {self.client_id}'}",
    "gross_pay": {monthly_income},
    "net_pay": {monthly_income * 0.7},
    "pay_period": "Monthly",
    "issues_found": [],
    "verification_date": "2025-05-19T03:47:00Z"
}}
```"""
        self.unverified_content = f"""```json
{{
    "verified": false,
    "monthly_income": {monthly_income},
    "employer": "{employer}",
    "position": "{position}",
    "employee_name": "{self.client_name or f'Client {self.client_id}'}",
    "gross_pay": {monthly_income},
    "net_pay": {monthly_income * 0.7},
    "pay_period": "Monthly",
    "issues_found": ["Inconsistent income figures", "Missing employer details"],
    "verification_date": "2025-05-19T03:47:00Z"
}}
```"""

class MockedOllamaLLM:
    """
    A mocked version of OllamaLLM that returns predefined responses.
    """
    def __init__(self, response_class: Type[BaseMockResponse], client_id=None, client_name=None, *args, **kwargs):
        self.client_id = client_id
        self.client_name = client_name
        self.kwargs = kwargs
        
        # Store the response class type
        self.response_class = response_class
        
        # For convenience, create a response object to reuse
        self.response_obj = response_class(self.client_id, self.client_name, **kwargs)
    
    def bind(self, **kwargs):
        """Return mock class that has ainvoke method."""
        return self.response_obj
    
    async def ainvoke(self, messages=None, *args, **kwargs):
        """Handle ainvoke method directly."""
        return self.response_obj
        
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Override the _acall method to return mock responses."""
        return self.response_obj.content

def get_mocked_id_verification_model(client_id, client_name):
    """
    Returns a mocked instance of OllamaLLM configured for ID verification.
    
    Args:
        client_id: The client ID to create a mock response for
        client_name: The name of the client to create a mock response for
        
    Returns:
        Configured MockedOllamaLLM instance
    """
    return MockedOllamaLLM(
        response_class=MockVerifiedIDResponse,
        client_id=client_id,
        client_name=client_name,
        model="openhermes", 
        temperature=0.1
    )

def get_mocked_web_references_model(client_id, client_name, employer="Global Bank Ltd"):
    """
    Returns a mocked instance of OllamaLLM configured for web references verification.
    
    Args:
        client_id: The client ID to create a mock response for
        client_name: The name of the client to create a mock response for
        employer: The employer name to include in the response (default: "Global Bank Ltd")
        
    Returns:
        Configured MockedOllamaLLM instance
    """
    return MockedOllamaLLM(
        response_class=MockWebReferencesResponse,
        client_id=client_id,
        client_name=client_name,
        employer=employer,
        model="openhermes", 
        temperature=0.1
    )

def get_mocked_financial_reports_model(client_id, client_name, annual_income_range="100,000 - 200,000", investment_assets="500,000+"):
    """
    Returns a mocked instance of OllamaLLM configured for financial reports verification.
    
    Args:
        client_id: The client ID to create a mock response for
        client_name: The name of the client to create a mock response for
        annual_income_range: The annual income range to include in the response (default: "100,000 - 200,000")
        investment_assets: The investment assets value to include in the response (default: "500,000+")
        
    Returns:
        Configured MockedOllamaLLM instance
    """
    return MockedOllamaLLM(
        response_class=MockFinancialReportsResponse,
        client_id=client_id,
        client_name=client_name,
        annual_income_range=annual_income_range,
        investment_assets=investment_assets,
        model="openhermes", 
        temperature=0.1
    )

def get_mocked_payslips_model(client_id, client_name, employer="Global Bank Ltd", position="Senior Manager", monthly_income=15000.0):
    """
    Returns a mocked instance of OllamaLLM configured for payslips extraction.
    
    Args:
        client_id: The client ID to create a mock response for
        client_name: The name of the client to create a mock response for
        employer: The employer name to include in the response (default: "Global Bank Ltd")
        position: The job position to include in the response (default: "Senior Manager")
        monthly_income: The monthly income to include in the response (default: 15000.0)
        
    Returns:
        Configured MockedOllamaLLM instance
    """
    return MockedOllamaLLM(
        response_class=MockPayslipsResponse,
        client_id=client_id,
        client_name=client_name,
        employer=employer,
        position=position,
        monthly_income=monthly_income,
        model="openhermes", 
        temperature=0.1
    )

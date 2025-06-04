"""Example workflows demonstrating various agent patterns."""

from typing import Dict, Any, List, Optional
from pathlib import Path

from ..core.base import BaseAgent, BaseState, AgentConfig
from ..utils.logging import get_logger
from .templates import workflow_templates


class DocumentProcessingState(BaseState):
    """State for document processing workflow."""
    
    def __init__(self, **data):
        super().__init__(**data)
        self.documents: List[str] = data.get("documents", [])
        self.extracted_text: Dict[str, str] = data.get("extracted_text", {})
        self.analysis_results: Dict[str, Any] = data.get("analysis_results", {})
        self.processed_documents: List[str] = data.get("processed_documents", [])


class TextExtractionAgent(BaseAgent):
    """Agent for extracting text from documents."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="text_extraction_agent",
            description="Extracts text from various document formats",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: DocumentProcessingState) -> DocumentProcessingState:
        """Extract text from documents."""
        self.logger.info(f"Extracting text from {len(state.documents)} documents")
        
        for doc_path in state.documents:
            # Simulate text extraction
            if doc_path.endswith('.pdf'):
                text = f"Extracted PDF text from {doc_path}"
            elif doc_path.endswith('.docx'):
                text = f"Extracted Word text from {doc_path}"
            elif doc_path.endswith('.txt'):
                text = f"Plain text content from {doc_path}"
            else:
                text = f"Generic text extraction from {doc_path}"
            
            state.extracted_text[doc_path] = text
        
        state.mark_step_completed("text_extraction")
        return state


class ContentAnalysisAgent(BaseAgent):
    """Agent for analyzing document content."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="content_analysis_agent",
            description="Analyzes extracted document content",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: DocumentProcessingState) -> DocumentProcessingState:
        """Analyze document content."""
        self.logger.info(f"Analyzing content from {len(state.extracted_text)} documents")
        
        for doc_path, text in state.extracted_text.items():
            # Simulate content analysis
            analysis = {
                "word_count": len(text.split()),
                "sentiment": "neutral",
                "topics": ["business", "technology"],
                "key_phrases": ["document processing", "agent workflow"],
                "language": "english"
            }
            state.analysis_results[doc_path] = analysis
        
        state.mark_step_completed("content_analysis")
        return state


class DocumentClassificationAgent(BaseAgent):
    """Agent for classifying documents."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="document_classification_agent",
            description="Classifies documents by type and content",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: DocumentProcessingState) -> DocumentProcessingState:
        """Classify documents."""
        self.logger.info(f"Classifying {len(state.analysis_results)} documents")
        
        for doc_path, analysis in state.analysis_results.items():
            # Simulate document classification
            classification = {
                "document_type": "report" if "report" in doc_path.lower() else "general",
                "category": "business_document",
                "confidence": 0.85,
                "tags": ["processed", "analyzed"]
            }
            
            # Update analysis with classification
            state.analysis_results[doc_path].update(classification)
            state.processed_documents.append(doc_path)
        
        state.mark_step_completed("document_classification")
        return state


class DataAnalysisState(BaseState):
    """State for data analysis workflow."""
    
    def __init__(self, **data):
        super().__init__(**data)
        self.raw_data: Dict[str, Any] = data.get("raw_data", {})
        self.cleaned_data: Dict[str, Any] = data.get("cleaned_data", {})
        self.analysis_results: Dict[str, Any] = data.get("analysis_results", {})
        self.insights: List[str] = data.get("insights", [])
        self.recommendations: List[str] = data.get("recommendations", [])


class DataCleaningAgent(BaseAgent):
    """Agent for cleaning and preprocessing data."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="data_cleaning_agent",
            description="Cleans and preprocesses raw data",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: DataAnalysisState) -> DataAnalysisState:
        """Clean and preprocess data."""
        self.logger.info("Cleaning raw data")
        
        # Simulate data cleaning
        for key, data in state.raw_data.items():
            cleaned = {
                "records": data.get("records", []),
                "nulls_removed": 15,
                "duplicates_removed": 3,
                "outliers_handled": 2,
                "normalization_applied": True
            }
            state.cleaned_data[key] = cleaned
        
        state.mark_step_completed("data_cleaning")
        return state


class StatisticalAnalysisAgent(BaseAgent):
    """Agent for statistical analysis."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="statistical_analysis_agent",
            description="Performs statistical analysis on data",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: DataAnalysisState) -> DataAnalysisState:
        """Perform statistical analysis."""
        self.logger.info("Performing statistical analysis")
        
        # Simulate statistical analysis
        stats = {
            "descriptive_stats": {
                "mean": 45.6,
                "median": 42.0,
                "std_dev": 12.3,
                "count": 1000
            },
            "correlation_analysis": {
                "strong_correlations": ["var1_var2", "var3_var4"],
                "correlation_matrix": "computed"
            },
            "trend_analysis": {
                "trend": "increasing",
                "seasonal_patterns": True,
                "growth_rate": 0.05
            }
        }
        
        state.analysis_results["statistical"] = stats
        state.mark_step_completed("statistical_analysis")
        return state


class PredictiveAnalysisAgent(BaseAgent):
    """Agent for predictive analysis."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="predictive_analysis_agent",
            description="Performs predictive analysis and modeling",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: DataAnalysisState) -> DataAnalysisState:
        """Perform predictive analysis."""
        self.logger.info("Performing predictive analysis")
        
        # Simulate predictive analysis
        predictions = {
            "model_type": "random_forest",
            "accuracy": 0.87,
            "feature_importance": {
                "feature_1": 0.35,
                "feature_2": 0.28,
                "feature_3": 0.22,
                "feature_4": 0.15
            },
            "predictions": {
                "next_quarter": 152.3,
                "confidence_interval": [145.1, 159.5]
            }
        }
        
        state.analysis_results["predictive"] = predictions
        state.mark_step_completed("predictive_analysis")
        return state


class InsightGenerationAgent(BaseAgent):
    """Agent for generating insights from analysis results."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="insight_generation_agent",
            description="Generates insights and recommendations from analysis",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: DataAnalysisState) -> DataAnalysisState:
        """Generate insights and recommendations."""
        self.logger.info("Generating insights and recommendations")
        
        # Generate insights based on analysis results
        if "statistical" in state.analysis_results:
            stats = state.analysis_results["statistical"]
            if stats["descriptive_stats"]["std_dev"] > 10:
                state.insights.append("High variability detected in the data")
            
            if stats["trend_analysis"]["trend"] == "increasing":
                state.insights.append("Positive growth trend identified")
        
        if "predictive" in state.analysis_results:
            pred = state.analysis_results["predictive"]
            if pred["accuracy"] > 0.8:
                state.insights.append("High-accuracy predictive model achieved")
                state.recommendations.append("Deploy predictive model for forecasting")
        
        # General recommendations
        state.recommendations.extend([
            "Monitor key performance indicators regularly",
            "Consider additional data sources for improved accuracy",
            "Implement automated reporting dashboard"
        ])
        
        state.mark_step_completed("insight_generation")
        return state


class CustomerServiceState(BaseState):
    """State for customer service workflow."""
    
    def __init__(self, **data):
        super().__init__(**data)
        self.customer_query: str = data.get("customer_query", "")
        self.customer_id: str = data.get("customer_id", "")
        self.intent: str = data.get("intent", "")
        self.sentiment: str = data.get("sentiment", "")
        self.resolution: str = data.get("resolution", "")
        self.escalated: bool = data.get("escalated", False)
        self.satisfaction_score: Optional[float] = data.get("satisfaction_score")


class IntentClassificationAgent(BaseAgent):
    """Agent for classifying customer intent."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="intent_classification_agent",
            description="Classifies customer query intent",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: CustomerServiceState) -> CustomerServiceState:
        """Classify customer intent."""
        self.logger.info(f"Classifying intent for customer: {state.customer_id}")
        
        # Simulate intent classification
        query_lower = state.customer_query.lower()
        if "refund" in query_lower or "return" in query_lower:
            state.intent = "refund_request"
        elif "billing" in query_lower or "charge" in query_lower:
            state.intent = "billing_inquiry"
        elif "support" in query_lower or "help" in query_lower:
            state.intent = "technical_support"
        elif "cancel" in query_lower:
            state.intent = "cancellation"
        else:
            state.intent = "general_inquiry"
        
        state.mark_step_completed("intent_classification")
        return state


class SentimentAnalysisAgent(BaseAgent):
    """Agent for analyzing customer sentiment."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="sentiment_analysis_agent",
            description="Analyzes customer sentiment",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: CustomerServiceState) -> CustomerServiceState:
        """Analyze customer sentiment."""
        self.logger.info(f"Analyzing sentiment for customer: {state.customer_id}")
        
        # Simulate sentiment analysis
        query_lower = state.customer_query.lower()
        negative_words = ["angry", "frustrated", "terrible", "awful", "hate"]
        positive_words = ["great", "excellent", "love", "amazing", "wonderful"]
        
        if any(word in query_lower for word in negative_words):
            state.sentiment = "negative"
        elif any(word in query_lower for word in positive_words):
            state.sentiment = "positive"
        else:
            state.sentiment = "neutral"
        
        state.mark_step_completed("sentiment_analysis")
        return state


class ResponseGenerationAgent(BaseAgent):
    """Agent for generating customer responses."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="response_generation_agent",
            description="Generates appropriate customer responses",
            config=config or AgentConfig()
        )
        self.logger = get_logger(self.name)
    
    async def process(self, state: CustomerServiceState) -> CustomerServiceState:
        """Generate customer response."""
        self.logger.info(f"Generating response for {state.intent} with {state.sentiment} sentiment")
        
        # Generate response based on intent and sentiment
        responses = {
            "refund_request": "I understand you'd like to request a refund. Let me help you with that process.",
            "billing_inquiry": "I can help you with your billing question. Let me review your account details.",
            "technical_support": "I'm here to help with your technical issue. Can you provide more details?",
            "cancellation": "I'm sorry to hear you're considering cancellation. Let's see how we can help.",
            "general_inquiry": "Thank you for contacting us. I'm here to assist you with your question."
        }
        
        base_response = responses.get(state.intent, "Thank you for contacting us. How can I help?")
        
        # Adjust tone based on sentiment
        if state.sentiment == "negative":
            state.resolution = f"I sincerely apologize for any inconvenience. {base_response}"
        elif state.sentiment == "positive":
            state.resolution = f"Thank you for your positive feedback! {base_response}"
        else:
            state.resolution = base_response
        
        # Check if escalation is needed
        if state.sentiment == "negative" and state.intent in ["refund_request", "cancellation"]:
            state.escalated = True
            state.resolution += " I'm escalating this to a senior representative for immediate attention."
        
        state.mark_step_completed("response_generation")
        return state


def create_document_processing_workflow():
    """Create a document processing workflow example."""
    from .templates import workflow_templates
    
    # Create agents
    extractor = TextExtractionAgent()
    analyzer = ContentAnalysisAgent()
    classifier = DocumentClassificationAgent()
    
    # Create workflow using sequential template
    workflow = workflow_templates.create_workflow(
        template_name="sequential",
        agents=[extractor, analyzer, classifier],
        state_class=DocumentProcessingState
    )
    
    return workflow


def create_data_analysis_workflow():
    """Create a data analysis workflow example."""
    from .templates import workflow_templates
    
    # Create agents
    cleaner = DataCleaningAgent()
    stat_analyzer = StatisticalAnalysisAgent()
    pred_analyzer = PredictiveAnalysisAgent()
    insight_generator = InsightGenerationAgent()
    
    # Create workflow using analysis template
    workflow = workflow_templates.create_workflow(
        template_name="analysis",
        preprocessor_agent=cleaner,
        analysis_agents=[stat_analyzer, pred_analyzer],
        synthesizer_agent=insight_generator,
        state_class=DataAnalysisState
    )
    
    return workflow


def create_customer_service_workflow():
    """Create a customer service workflow example."""
    from .templates import workflow_templates
    
    # Create agents
    intent_classifier = IntentClassificationAgent()
    sentiment_analyzer = SentimentAnalysisAgent()
    response_generator = ResponseGenerationAgent()
    
    # Create workflow using parallel template for analysis, then response
    # This is a simplified example - a real implementation might be more complex
    workflow = workflow_templates.create_workflow(
        template_name="sequential",
        agents=[intent_classifier, sentiment_analyzer, response_generator],
        state_class=CustomerServiceState
    )
    
    return workflow


def get_example_workflows() -> Dict[str, Any]:
    """Get all available example workflows."""
    return {
        "document_processing": {
            "name": "Document Processing",
            "description": "Process documents through extraction, analysis, and classification",
            "create_func": create_document_processing_workflow,
            "state_class": DocumentProcessingState,
            "example_input": {
                "documents": ["report.pdf", "memo.docx", "notes.txt"]
            }
        },
        "data_analysis": {
            "name": "Data Analysis",
            "description": "Analyze data through cleaning, statistical analysis, and insight generation",
            "create_func": create_data_analysis_workflow,
            "state_class": DataAnalysisState,
            "example_input": {
                "raw_data": {"dataset1": {"records": [1, 2, 3, 4, 5]}}
            }
        },
        "customer_service": {
            "name": "Customer Service",
            "description": "Handle customer queries through intent classification and response generation",
            "create_func": create_customer_service_workflow,
            "state_class": CustomerServiceState,
            "example_input": {
                "customer_query": "I need help with my billing",
                "customer_id": "CUST123"
            }
        }
    }

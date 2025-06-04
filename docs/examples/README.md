# Examples Directory

Real-world examples demonstrating Agent Playground capabilities and patterns.

## Available Examples

### 📄 Document Processing
Complete document processing pipeline with text extraction, analysis, and classification.

- [**Document Processing Pipeline**](document-processing-pipeline.md) - Full end-to-end example
- [**PDF Processing**](pdf-processing.md) - PDF-specific processing
- [**Multi-format Documents**](multi-format-documents.md) - Handle various document formats

### 📊 Data Analysis
Comprehensive data analysis workflows from cleaning to insight generation.

- [**Sales Data Analysis**](sales-data-analysis.md) - Analyze sales performance data
- [**Customer Behavior Analysis**](customer-behavior-analysis.md) - Customer journey analytics
- [**Financial Data Processing**](financial-data-processing.md) - Financial reporting and analysis

### 🤖 Customer Service
Intelligent customer service automation with intent classification and response generation.

- [**Customer Support Bot**](customer-support-bot.md) - Complete support automation
- [**Ticket Classification**](ticket-classification.md) - Support ticket routing
- [**Sentiment Analysis Pipeline**](sentiment-analysis-pipeline.md) - Customer sentiment tracking

### 💰 Financial Services
Source of Wealth verification and financial analysis workflows.

- [**SOW Verification**](sow-verification.md) - Complete source of wealth verification
- [**Risk Assessment**](risk-assessment.md) - Financial risk analysis
- [**Compliance Workflows**](compliance-workflows.md) - Regulatory compliance automation

### 🔄 Integration Examples
Examples showing integration with external systems and frameworks.

- [**LangChain Integration**](langchain-integration.md) - Migrate from LangChain
- [**LangGraph Integration**](langgraph-integration.md) - Integrate with LangGraph
- [**API Integration**](api-integration.md) - External API workflows
- [**Database Workflows**](database-workflows.md) - Database operations

### 🧪 Testing Examples
Examples demonstrating testing strategies and patterns.

- [**Unit Testing Agents**](unit-testing-agents.md) - Test individual agents
- [**Integration Testing**](integration-testing.md) - Test complete workflows
- [**Mock Agents**](mock-agents.md) - Testing with mock agents
- [**Performance Testing**](performance-testing.md) - Benchmark workflows

## Quick Start Examples

### Simple Sequential Workflow

```python
# simple_sequential.py
import asyncio
from agent_playground.core import BaseAgent, BaseState
from agent_playground.workflows import workflow_templates

class ProcessingState(BaseState):
    input_text: str = ""
    processed_text: str = ""
    analysis_result: str = ""

class TextProcessor(BaseAgent):
    async def execute(self, state: ProcessingState) -> ProcessingState:
        state.processed_text = state.input_text.upper()
        return state

class TextAnalyzer(BaseAgent):
    async def execute(self, state: ProcessingState) -> ProcessingState:
        word_count = len(state.processed_text.split())
        state.analysis_result = f"Word count: {word_count}"
        return state

async def main():
    # Create workflow
    workflow = workflow_templates.create_workflow(
        template_name="sequential",
        agents=[TextProcessor(), TextAnalyzer()],
        state_class=ProcessingState
    )
    
    # Execute
    initial_state = ProcessingState()
    initial_state.input_text = "hello world"
    
    result = await workflow.execute(initial_state)
    print(f"Result: {result.analysis_result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Parallel Processing with Aggregation

```python
# parallel_processing.py
import asyncio
from typing import List
from agent_playground.core import BaseAgent, BaseState
from agent_playground.workflows import workflow_templates

class AnalysisState(BaseState):
    data: List[int] = []
    statistical_analysis: dict = {}
    trend_analysis: dict = {}
    combined_insights: dict = {}

class StatisticalAnalyzer(BaseAgent):
    async def execute(self, state: AnalysisState) -> AnalysisState:
        data = state.data
        state.statistical_analysis = {
            "mean": sum(data) / len(data),
            "max": max(data),
            "min": min(data)
        }
        return state

class TrendAnalyzer(BaseAgent):
    async def execute(self, state: AnalysisState) -> AnalysisState:
        data = state.data
        trend = "increasing" if data[-1] > data[0] else "decreasing"
        state.trend_analysis = {
            "trend": trend,
            "change": data[-1] - data[0]
        }
        return state

class InsightAggregator(BaseAgent):
    async def execute(self, state: AnalysisState) -> AnalysisState:
        state.combined_insights = {
            "summary": f"Data shows {state.trend_analysis['trend']} trend",
            "stats": state.statistical_analysis,
            "trend": state.trend_analysis
        }
        return state

async def main():
    # Create parallel workflow
    workflow = workflow_templates.create_workflow(
        template_name="parallel",
        agents=[StatisticalAnalyzer(), TrendAnalyzer()],
        aggregator_agent=InsightAggregator(),
        state_class=AnalysisState
    )
    
    # Execute
    initial_state = AnalysisState()
    initial_state.data = [10, 15, 12, 18, 25, 22, 30]
    
    result = await workflow.execute(initial_state)
    print(f"Insights: {result.combined_insights}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Conditional Workflow

```python
# conditional_workflow.py
import asyncio
from agent_playground.core import BaseAgent, BaseState
from agent_playground.workflows import workflow_templates

class DocumentState(BaseState):
    document_type: str = ""
    content: str = ""
    processed_content: str = ""

class PDFProcessor(BaseAgent):
    async def execute(self, state: DocumentState) -> DocumentState:
        state.processed_content = f"PDF: {state.content}"
        return state

class ImageProcessor(BaseAgent):
    async def execute(self, state: DocumentState) -> DocumentState:
        state.processed_content = f"IMAGE: {state.content}"
        return state

class TextProcessor(BaseAgent):
    async def execute(self, state: DocumentState) -> DocumentState:
        state.processed_content = f"TEXT: {state.content}"
        return state

def route_by_type(state: DocumentState) -> str:
    """Route documents based on type."""
    type_mapping = {
        "pdf": "pdf_path",
        "image": "image_path", 
        "text": "text_path"
    }
    return type_mapping.get(state.document_type, "text_path")

async def main():
    # Create conditional workflow
    workflow = workflow_templates.create_workflow(
        template_name="conditional",
        condition_func=route_by_type,
        agent_paths={
            "pdf_path": [PDFProcessor()],
            "image_path": [ImageProcessor()],
            "text_path": [TextProcessor()]
        },
        state_class=DocumentState
    )
    
    # Test with different document types
    for doc_type in ["pdf", "image", "text"]:
        state = DocumentState()
        state.document_type = doc_type
        state.content = f"Sample {doc_type} content"
        
        result = await workflow.execute(state)
        print(f"{doc_type}: {result.processed_content}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Human-in-the-Loop Workflow

```python
# human_review_workflow.py
import asyncio
from agent_playground.core import BaseAgent, BaseState
from agent_playground.workflows import workflow_templates

class ReviewState(BaseState):
    document: str = ""
    ai_analysis: str = ""
    needs_review: bool = False
    human_approved: bool = False
    final_decision: str = ""

class DocumentAnalyzer(BaseAgent):
    async def execute(self, state: ReviewState) -> ReviewState:
        # Simulate AI analysis
        state.ai_analysis = f"Analysis of: {state.document}"
        # Flag for human review if needed
        state.needs_review = "sensitive" in state.document.lower()
        return state

class HumanReviewer(BaseAgent):
    async def execute(self, state: ReviewState) -> ReviewState:
        if state.needs_review:
            # In real implementation, this would wait for human input
            print(f"Human review needed for: {state.document}")
            print(f"AI Analysis: {state.ai_analysis}")
            
            # Simulate human approval (in practice, get from UI)
            user_input = input("Approve? (y/n): ").lower()
            state.human_approved = user_input == 'y'
        else:
            state.human_approved = True
        return state

class DecisionMaker(BaseAgent):
    async def execute(self, state: ReviewState) -> ReviewState:
        if state.human_approved:
            state.final_decision = "Approved"
        else:
            state.final_decision = "Rejected"
        return state

async def main():
    # Create human-in-the-loop workflow
    workflow = workflow_templates.create_workflow(
        template_name="human_in_loop",
        agents=[DocumentAnalyzer(), DecisionMaker()],
        review_agent=HumanReviewer(),
        approval_required=True,
        state_class=ReviewState
    )
    
    # Test documents
    documents = [
        "Regular business document",
        "Sensitive financial information"
    ]
    
    for doc in documents:
        state = ReviewState()
        state.document = doc
        
        result = await workflow.execute(state)
        print(f"Document: {doc}")
        print(f"Decision: {result.final_decision}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
```

## Example Categories

### By Complexity

**Beginner Examples:**
- Simple text processing
- Basic data validation
- File operations

**Intermediate Examples:**
- Multi-agent workflows
- External API integration
- Database operations

**Advanced Examples:**
- Complex business logic
- Performance optimization
- Production deployment

### By Domain

**Text Processing:**
- Document analysis
- Content generation
- Translation workflows

**Data Science:**
- Data cleaning pipelines
- Statistical analysis
- Machine learning workflows

**Business Automation:**
- Customer service
- Financial processing
- Compliance automation

**System Integration:**
- API orchestration
- Database synchronization
- ETL processes

## Running Examples

### Prerequisites

```bash
# Install Agent Playground
pip install -e .

# Install example dependencies
pip install -r examples/requirements.txt
```

### Running Individual Examples

```bash
# Run a specific example
python examples/document-processing-pipeline.py

# Run with custom data
python examples/sales-data-analysis.py --data-file my_data.csv

# Run in verbose mode
python examples/customer-support-bot.py --verbose
```

### Running All Examples

```bash
# Run example test suite
python examples/run_all_examples.py

# Run with performance benchmarking
python examples/run_all_examples.py --benchmark
```

## Contributing Examples

We welcome contributions of new examples! See our [contribution guidelines](../CONTRIBUTING.md) for details.

### Example Template

```python
"""
Example: [Brief Description]

This example demonstrates [what it shows].

Requirements:
- [List any special requirements]

Usage:
    python this_example.py [options]
"""

import asyncio
from agent_playground.core import BaseAgent, BaseState
from agent_playground.workflows import workflow_templates

# Your example code here

if __name__ == "__main__":
    asyncio.run(main())
```

---

**Explore Examples:**
- Browse by category above
- Try the quick start examples
- Check out the [tutorials](../tutorials/) for guided learning

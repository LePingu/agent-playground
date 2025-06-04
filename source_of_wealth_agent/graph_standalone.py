# Create a checkpointer for the graph to support interrupts
import os
from typing import Dict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from source_of_wealth_agent.agents.human_advisory_agent import human_advisory_agent
from source_of_wealth_agent.agents.id_verification_agent import IDVerificationAgent
from source_of_wealth_agent.agents.payslip_verification_agent import PayslipVerificationAgent
from source_of_wealth_agent.agents.report_generation_agent import report_generation_agent
from source_of_wealth_agent.agents.risk_assessment_agent import risk_assessment_agent
from source_of_wealth_agent.agents.summarization_agent import summarization_agent
from source_of_wealth_agent.agents.web_references_agent import WebReferencesAgent
from source_of_wealth_agent.agents.financial_reports_agent import FinancialReportsAgent
from source_of_wealth_agent.core.mocked_model import get_mocked_financial_reports_model, get_mocked_id_verification_model, get_mocked_payslips_model, get_mocked_web_references_model
from source_of_wealth_agent.core.models import initialize_ollama_model, initialize_openrouter_model
from source_of_wealth_agent.core.state import AgentState

from dotenv import load_dotenv



def load_environment() -> Dict[str, str]:
    """
    Load environment variables from .env file.
    
    Returns:
        Dictionary of environment variables
    """
    # Try to load from env/.env file
    env_path = os.path.join(os.path.dirname(__file__), 'env', '.env')
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ Loaded environment from {env_path}")
    else:
        print(f"⚠️ No .env file found at {env_path}, using existing environment variables")
    
    return {
        'client_id': os.getenv('CLIENT_ID', '12345'),
        'client_name': os.getenv('CLIENT_NAME', 'John Doe'),
        'openrouter_api_key': os.getenv('OPENROUTER_API_KEY'),
        'openrouter_model': os.getenv('OPENROUTER_MODEL', 'openai/gpt-4-turbo'),
        'ollama_base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
        'ollama_model': os.getenv('OLLAMA_MODEL', 'openhermes'),
        'langchain_tracing': os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true'
    }


def setup_langchain_tracing():
    """Configure LangChain tracing based on environment variables."""
    if os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true':
        os.environ['LANGSMITH_TRACING'] = 'true'
        
        # Set other LangChain environment variables if they exist
        for var in ['LANGSMITH_ENDPOINT', 'LANGSMITH_API_KEY', 'LANGSMITH_PROJECT']:
            if os.getenv(var):
                os.environ[var] = os.getenv(var)
                
        print("🔍 LangChain tracing enabled")
    else:
        os.environ['LANGSMITH_TRACING'] = 'false'
        print("ℹ️ LangChain tracing disabled")



def route_after_risk_assessment(state: AgentState) -> str:
    """
    Determine where to route after risk assessment agent runs,
    ensuring ID verification has priority and must complete first.
    
    ID verification now uses LangGraph's Interrupt pattern for blocking human review.
    Other verification steps will continue to run asynchronously while waiting for
    other types of human review responses.
    """
    # First, check if there are any review responses to process
    if state.get("review_responses") and len(state.get("review_responses", [])) > 0:
        print(f"ℹ️ Found {len(state.get('review_responses', []))} review responses to process")
        return "human_advisory_node"
    
    # Always check if ID verification has been completed
    # This enforces ID verification as a sequential prerequisite for any other steps
    id_verified = state.get("id_verification", {}).get("verified", None)
    id_approved = state.get("human_approvals", {}).get("id_verification", {}).get("approved", False)
    
    # If ID verification hasn't been completed yet and isn't the next step,
    # override any other routing and enforce ID verification first
    if id_verified is None and state.get("next_verification") != "id_verification":
        print("⚠️ SEQUENTIAL ENFORCEMENT: ID verification must be completed first - overriding next step")
        return "id_verification_node"
    
    # If ID verification failed and no human approval, we need to handle it
    if id_verified is False and not id_approved:
        # Check if we already have a pending review for ID verification
        if state.get("pending_reviews"):
            has_id_review_pending = any(
                review.get("verification_type") == "id_verification" 
                for review in state.get("pending_reviews", [])
            )
            if has_id_review_pending:
                print("⚠️ ID verification failed - waiting for human review (non-blocking)")
                # Since ID verification is sequential, we still need to block here
                # However, we've logged the request asynchronously so human can respond anytime
                return "human_advisory_node"
        
        print("⚠️ ID verification failed - must get human review before proceeding")
        return "human_advisory_node"
        
    # Only if ID verification passed or has human override, check normal routing logic
    if id_verified is True or id_approved:
        # If the risk assessment indicates a next agent, use that
        if "next_agent" in state:
            return state["next_agent"]
        
        # If there's a next verification step, return the corresponding node
        if "next_verification" in state:
            next_step = state["next_verification"]
                
            # Route to the appropriate node based on next_verification
            if next_step == "id_verification":
                return "id_verification_node"
            elif next_step == "payslip_verification":
                return "payslip_verification_node"
            elif next_step == "web_references_node":
                return "web_references_node"
            elif next_step == "financial_reports":
                return "financial_reports_node"
            elif next_step == "summarization":
                # Before going to summarization, check if we need to wait for any pending reviews
                if state.get("pending_reviews") and not state.get("human_approvals", {}).get("data_readiness_override", {}).get("approved", False):
                    print("ℹ️ There are pending reviews before summarization - requesting review")
                    return "human_advisory_node"
                return "summarization_node"
    
    # Default to human advisory if we can't determine the next step
    return "human_advisory_node"


def verification_needs_human_review(state: AgentState) -> str:
    """
    Determine if a verification step needs human review based on issues found.
    ID verification is a critical first step that blocks all other steps,
    so its issues are always prioritized for human review.
    
    With the new asynchronous human review system, this function now checks
    for issues and routes to the human advisory agent to register them for review,
    but will not block execution of other verification steps.
    """
    # Check if we have pending reviews and if there's a need to check status
    if state.get("pending_reviews") and len(state.get("pending_reviews", [])) > 0:
        print(f"ℹ️ There are {len(state.get('pending_reviews', []))} pending human reviews")
        # Still route to human advisory to check if any responses have been provided
        return "human_advisory_node"
    
    # Handle ID verification issues with highest priority
    # This is critical since ID verification is a sequential prerequisite
    if "id_verification" in state and state["id_verification"].get("issues_found"):
        print("⚠️ CRITICAL: ID verification issues detected - requesting human review")
        # Mark this as requiring special attention since it blocks the entire workflow
        state["id_verification_critical_issues"] = True
        return "human_advisory_node"
    
    # Only check other verification issues if ID verification was successful
    # or has been approved by human override - this enforces the sequential requirement
    id_verified = state.get("id_verification", {}).get("verified", False)
    human_approved_id = state.get("human_approvals", {}).get("id_verification", {}).get("approved", False)
    
    if id_verified or human_approved_id:
        needs_review = False
        
        if "payslip_verification" in state and state["payslip_verification"].get("issues_found"):
            print("⚠️ Payslip verification issues detected - requesting human review")
            needs_review = True
        
        if "web_references" in state and state["web_references"].get("risk_flags"):
            print("⚠️ Web references risk flags detected - requesting human review")
            needs_review = True
        
        if "financial_reports" in state and state["financial_reports"].get("issues_found"):
            print("⚠️ Financial reports issues detected - requesting human review")
            needs_review = True
            
        if needs_review:
            return "human_advisory_node"
    else:
        # If ID verification hasn't completed successfully and there's no human override,
        # route back to risk assessment which will enforce ID verification first
        print("⚠️ SEQUENTIAL ENFORCEMENT: Cannot proceed with verification review until ID is verified")
        return "risk_assessment_node"
    
    # If no human review needed, return to risk assessment for next steps
    return "risk_assessment_node"


def route_after_summarization(state: AgentState) -> str:
    """
    Determine where to route after summarization agent runs
    """
    # After summarization, we want to perform the final risk assessment
    # new_state = state.copy()
    state["risk_assessment_action"] = "perform_assessment"
    return "risk_assessment_node"


env = load_environment()
setup_langchain_tracing()


openrouter_model = initialize_openrouter_model(
            model_name="qwen/qwen3-110b",
            api_key="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",
            temperature=0.1
        )
        
ollama_model = initialize_ollama_model(
            model_name="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",
            base_url="https://api.smith.langchain.com",
            temperature=0.1
        )

mocked_id_model = get_mocked_id_verification_model("12345", "Hatim Nourbay")
mocked_payslip_model = get_mocked_payslips_model("12345", "Hatim Nourbay")
mocked_financial_model = get_mocked_financial_reports_model("12345", "Hatim Nourbay")
mocked_web_model = get_mocked_web_references_model("12345", "Hatim Nourbay")

id_agent = IDVerificationAgent(model=mocked_id_model)  # Uses local model for sensitive ID data
payslip_agent = PayslipVerificationAgent(model=mocked_payslip_model)  # Uses local model for sensitive financial data
web_agent = WebReferencesAgent(model=mocked_web_model)  # Uses OpenRouter for web searches
financial_agent = FinancialReportsAgent(model=mocked_financial_model)  # Uses OpenRouter for web searches

# checkpointer = MemorySaver()
    
    # Build the workflow graph
workflow = StateGraph(AgentState)

# Add the verification agent nodes
workflow.add_node("id_verification_node", id_agent.run)
workflow.add_node("payslip_verification_node", payslip_agent.run)
workflow.add_node("web_references_node", web_agent.run)
# if financial_agent:
workflow.add_node("financial_reports_node", financial_agent.run)

# Add the human advisory node that now handles interrupts
workflow.add_node("human_advisory_node", human_advisory_agent)

# Add planning, summarization, and final processing nodes
workflow.add_node("risk_assessment_node", risk_assessment_agent)
workflow.add_node("summarization_node", summarization_agent)
workflow.add_node("report_generation_node", report_generation_agent)

# Define workflow entry point - start with risk assessment for planning
workflow.add_edge("__start__", "risk_assessment_node")

# Connect ID verification directly to human advisory
# The human advisory agent will interrupt if human review is needed
workflow.add_edge("id_verification_node", "human_advisory_node")

# Risk assessment node determines the next verification step
# workflow.add_conditional_edges(
#     "risk_assessment_node",
#     route_after_risk_assessment,
#     {
#         "id_verification_node": "id_verification_node",
#         "payslip_verification_node": "payslip_verification_node",
#         "web_references_node": "web_references_node",
#         "financial_reports_node": "financial_reports_node" if financial_agent else "risk_assessment_node",
#         "summarization_node": "summarization_node",
#         "human_advisory_node": "human_advisory_node"
#     }
# )

# After each verification (except ID which already goes to human advisory), 
# check for issues and route to human review if needed
for node in ["payslip_verification_node", "web_references_node", "financial_reports_node" if financial_agent else None]:
    if node:
        workflow.add_conditional_edges(
            node,
            verification_needs_human_review,
            {
                "human_advisory_node": "human_advisory_node",
                "risk_assessment_node": "risk_assessment_node"
            }
        )



# After summarization, go to risk assessment for final assessment
# workflow.add_conditional_edges("summarization_node", route_after_summarization, {
#     "report_generation_node": "report_generation_node",
# })

# After final risk assessment, generate report
workflow.add_conditional_edges(
    "risk_assessment_node", 
    lambda state: "report_generation_node" if "risk_assessment" in state else route_after_risk_assessment(state),
    {
        "report_generation_node": "report_generation_node",
        "id_verification_node": "id_verification_node",
        "payslip_verification_node": "payslip_verification_node", 
        "web_references_node": "web_references_node",
        "financial_reports_node": "financial_reports_node" if financial_agent else "risk_assessment_node",
        "summarization_node": "summarization_node",
        "human_advisory_node": "human_advisory_node"
    }
)
workflow.add_conditional_edges(
    "summarization_node",
    route_after_summarization,
    {
        "risk_assessment_node": "risk_assessment_node",
        "report_generation_node": "report_generation_node"
    }
)

# End the workflow after report generation
workflow.add_edge("report_generation_node", END)

# Compile the workflow with checkpointer for interrupt support
graph = workflow.compile()
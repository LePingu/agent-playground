"""
Report Generation Agent for the Source of Wealth Agent system.

This module provides functionality to create formatted final reports based on
the verification and assessment results.
"""

from datetime import datetime
from typing import List, Dict, Any

from source_of_wealth_agent.core.state import AgentState, log_action


def report_generation_agent(state: AgentState) -> AgentState:
    """
    Agent that generates a final formatted report based on all verification results.
    Works with the simplified workflow, primarily relying on summarization data.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with the final report
    """
    print("📝 Generating final report...")
    
    # Check if we have the verification summary
    has_summary = "verification_summary" in state
    summary = state.get("verification_summary", {}) if has_summary else {}
    
    # Extract client info
    client_info = summary.get("client_info", {}) if has_summary else {}
    client_id = state.get("client_id", "Unknown")
    client_name = client_info.get("client_name", state.get("client_name", "Unknown"))
    
    # Extract verification statuses
    verification_status = summary.get("verification_status", {}) if has_summary else {}
    identity_details = summary.get("identity_details", {}) if has_summary else {}
    employment_details = summary.get("employment_details", {}) if has_summary else {}
    web_presence = summary.get("web_presence", {}) if has_summary else {}
    
    # Get verification status - first check summary, then fall back to direct checks
    id_verified = verification_status.get("id_verified", False) or state.get('id_verification', {}).get("verified", False)
    payslip_verified = verification_status.get("payslip_verified", False) or state.get('payslip_verification', {}).get("verified", False)
    web_verified = verification_status.get("web_references_verified", False) or state.get('web_references', {}).get("verified", False)
    
    # Create a structured markdown report
    report = f"""# Source of Wealth Verification Report
    
## Client Information
- **Client ID**: {client_id}
- **Client Name**: {client_name}
- **Verification Date**: {datetime.now().strftime('%Y-%m-%d')}

## Verification Results

### Identity Verification
{"✅ Passed" if id_verified else "❌ Failed or Incomplete"}
- ID Type: {identity_details.get("id_type") or state.get('id_verification', {}).get("id_type", "Unknown")}
- ID Number: {identity_details.get("id_number") or state.get('id_verification', {}).get("id_number", "Unknown")}
- Expiry: {identity_details.get("id_expiry") or state.get('id_verification', {}).get("id_expiry", "Unknown")}
- Full Name: {identity_details.get("name_on_id") or state.get('id_verification', {}).get("name", "Unknown")}

### Employment Details
{"✅ Verified" if payslip_verified else "❌ Not Verified"}
- Employer: {employment_details.get("employer") or state.get('payslip_verification', {}).get("employer", "Unknown")}
- Position: {employment_details.get("position") or state.get('payslip_verification', {}).get("position", "Unknown")}
- Monthly Income: ${employment_details.get("monthly_income") or state.get('payslip_verification', {}).get("monthly_income", "Unknown")}
- Employment Start: {employment_details.get("employment_start") or state.get('payslip_verification', {}).get("employment_start", "Unknown")}

### Web References
{"✅ Verified" if web_verified else "❌ Not Verified"}
"""

    # Add web mentions if available
    if web_verified:
        # First try to get mentions from summary
        if has_summary and web_presence.get("available") and web_presence.get("mentions_count", 0) > 0:
            report += f"- Found {web_presence.get('mentions_count', 0)} mentions\n\n"
            
            if web_presence.get("top_mentions"):
                report += "#### Top Mentions\n"
                for i, mention in enumerate(web_presence.get("top_mentions", [])):
                    report += f"""**Source {i+1}**: {mention.get('source', 'Unknown')}
- Summary: {mention.get('summary', 'No summary available')}
- Sentiment: {mention.get('sentiment', 'Neutral')}

"""
        # Fall back to direct web references if available
        elif "web_references" in state and "mentions" in state["web_references"]:
            mentions = state["web_references"]["mentions"]
            report += f"- Found {len(mentions)} mentions\n\n"
            
            if mentions:
                report += "#### Top Mentions\n"
                for i, mention in enumerate(mentions[:3]):  # Show only top 3
                    summary = mention.get("analysis", {}).get("summary", "No summary available")
                    sentiment = mention.get("analysis", {}).get("sentiment", "Neutral")
                    source = mention.get("source", "Unknown")
                    
                    report += f"""**Source {i+1}**: {source}
- Summary: {summary}
- Sentiment: {sentiment}

"""
        else:
            report += "- No detailed web references information available\n"
    else:
        report += "- No web references found or verification failed\n"
    
    # Add risk assessment
    report += """
## Risk Assessment
"""
    
    if "risk_assessment" in state:
        risk_assessment = state["risk_assessment"]
        report += f"""- **Risk Level**: {risk_assessment.get("risk_level", "Unknown")}
- **Risk Score**: {risk_assessment.get("risk_score", "Unknown")}/100

### Risk Factors
{"No risk factors identified." if not risk_assessment.get("risk_factors") else '\\n'.join(f"- {factor}" for factor in risk_assessment.get("risk_factors", []))}
"""
    else:
        report += "- Risk assessment not available\n"
    
    # Add human oversight (if any)
    if "human_approvals" in state and state["human_approvals"]:
        report += """
## Human Oversight
""" + '\\n'.join(f"- {check}: {'Approved' if approved else 'Rejected'}" for check, approved in state.get('human_approvals', {}).items())
    
    # Add recommendation based on risk assessment
    report += """

## Recommendation
"""
    
    if "risk_assessment" in state:
        report += "Further investigation required" if state.get('risk_assessment', {}).get("risk_level") in ["Medium-High", "High"] else "Proceed with client relationship"
    else:
        report += "Insufficient information to provide a recommendation"
    
    report += "\n"
    
    # Save the report to the state
    new_state = state.copy()
    new_state["final_report"] = report
    print("\nReport Generation Complete!")
    
    return log_action(new_state, "Report_Generation_Agent", "Final report generated", {"report_length": len(report)})
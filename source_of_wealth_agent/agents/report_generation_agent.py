"""
Report Generation Agent for the Source of Wealth Agent system.

This module provides functionality to create formatted final reports based on
the verification and assessment results, and saves them as PDF files.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF
import markdown
import tempfile

from source_of_wealth_agent.core.state import AgentState, log_action


def get_risk_color(risk_level: str) -> Tuple[float, float, float]:
    """Return RGB color tuple based on risk level"""
    risk_colors = {
        "Low": (0, 0.7, 0),       # Green
        "Medium-Low": (0.5, 0.7, 0),  # Yellow-Green
        "Medium": (1, 0.7, 0),    # Orange
        "Medium-High": (0.9, 0.4, 0), # Dark Orange
        "High": (0.8, 0, 0)       # Red
    }
    return risk_colors.get(risk_level, (0.5, 0.5, 0.5))  # Default gray


def generate_pdf_report(markdown_text: str, client_id: str, client_name: str, state: AgentState = None) -> str:
    """
    Convert markdown report to PDF using PyMuPDF's direct text insertion.
    
    Args:
        markdown_text: The markdown text to convert
        client_id: Client ID for the filename
        client_name: Client name for the document title
        state: Current workflow state for additional context (e.g., risk levels)
        
    Returns:
        Path to the saved PDF file
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename based on client info and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_client_name = "".join(c if c.isalnum() else "_" for c in client_name)
        filename = f"sow_report_{client_id}_{safe_client_name}_{timestamp}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        # Make sure reports directory exists
        os.makedirs(output_dir, exist_ok=True)
        print(f"Report will be saved to: {output_path}")
        
        # Create a new PDF document
        doc = fitz.open()
        
        # First create a text file with the markdown content
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as temp_file:
            temp_file.write(markdown_text)
            temp_md_path = temp_file.name
        
        # Split markdown into sections for better formatting
        sections = markdown_text.split("\n## ")
        
        # Create a title page
        title_page = doc.new_page()
        
        # Add title and header
        title = "Source of Wealth Verification Report"
        client_info = f"Client: {client_name} (ID: {client_id})"
        date_str = f"Date: {datetime.now().strftime('%Y-%m-%d')}"
        
        # Calculate text widths for center positioning
        title_width = len(title) * 14  # Approximation
        title_x = (title_page.rect.width - title_width) / 2
        
        client_width = len(client_info) * 8  # Approximation
        client_x = (title_page.rect.width - client_width) / 2
        
        date_width = len(date_str) * 8  # Approximation
        date_x = (title_page.rect.width - date_width) / 2
        
        # Add centered text
        title_page.insert_text((title_x, 200), title, fontsize=24, color=(0, 0, 0.8))
        title_page.insert_text((client_x, 240), client_info, fontsize=14)
        title_page.insert_text((date_x, 260), date_str, fontsize=14)
        
        # Add company logo or branding placeholder
        confidential_width = len("CONFIDENTIAL") * 12  # Approximation
        confidential_x = (title_page.rect.width - confidential_width) / 2
        title_page.insert_text((confidential_x, 400), "CONFIDENTIAL", fontsize=20, color=(0.8, 0, 0))
        
        # Add a border to the title page
        border_rect = fitz.Rect(40, 40, title_page.rect.width-40, title_page.rect.height-40)
        title_page.draw_rect(border_rect, color=(0, 0, 0.5), width=2)
        
        # Add risk assessment visual indicator based on the state
        if "risk_assessment" in state and "risk_level" in state["risk_assessment"]:
            risk_level = state["risk_assessment"]["risk_level"]
            risk_color = get_risk_color(risk_level)
            risk_text = f"Risk Level: {risk_level}"
            
            # Add risk indicator
            risk_width = len(risk_text) * 10  # Approximate
            risk_x = (title_page.rect.width - risk_width) / 2
            
            # Draw risk level box with appropriate color
            risk_rect = fitz.Rect(risk_x - 10, 310, risk_x + risk_width + 10, 340)
            title_page.draw_rect(risk_rect, color=risk_color, fill=risk_color, width=0)
            
            # Add risk text in white
            title_page.insert_text((risk_x, 330), risk_text, fontsize=16, fontname="helvetica-bold", color=(1, 1, 1))
        
        # Add each section as a new page
        font_size = 11
        line_height = font_size * 1.5
        
        for i, section in enumerate(sections):
            # Skip the first empty section if it exists
            if i == 0 and not section.strip():
                continue
                
            # Add section header back for all but the first section
            if i > 0:
                section = "## " + section
                
            # Create a new page for this section
            page = doc.new_page()
            
            # Insert text with simple formatting
            y_pos = 50  # Starting y position
            
            for line in section.split('\n'):
                # Apply some basic formatting
                if line.startswith('# '):
                    # Level 1 header
                    text = line[2:].strip()
                    page.insert_text((50, y_pos), text, fontsize=20, fontname="helvetica-bold")
                    y_pos += line_height * 2
                elif line.startswith('## '):
                    # Level 2 header
                    text = line[3:].strip()
                    page.insert_text((50, y_pos), text, fontsize=16, fontname="helvetica-bold")
                    y_pos += line_height * 1.5
                elif line.startswith('### '):
                    # Level 3 header
                    text = line[4:].strip()
                    page.insert_text((50, y_pos), text, fontsize=14, fontname="helvetica-bold")
                    y_pos += line_height * 1.2
                elif line.startswith('- '):
                    # List item
                    text = line.strip()
                    page.insert_text((70, y_pos), text, fontsize=font_size)
                    y_pos += line_height
                elif line.startswith('**'):
                    # Bold text (for source mentions)
                    text = line.replace('**', '')
                    page.insert_text((50, y_pos), text, fontsize=font_size, fontname="helvetica-bold")
                    y_pos += line_height
                elif line.startswith('✅'):
                    # Success indicator
                    page.insert_text((50, y_pos), line.strip(), fontsize=font_size, color=(0, 0.5, 0))
                    y_pos += line_height
                elif line.startswith('❌'):
                    # Failure indicator
                    page.insert_text((50, y_pos), line.strip(), fontsize=font_size, color=(0.8, 0, 0))
                    y_pos += line_height
                elif line.strip() == "":
                    # Empty line
                    y_pos += line_height
                else:
                    # Regular text
                    page.insert_text((50, y_pos), line.strip(), fontsize=font_size)
                    y_pos += line_height
                
                # Check if we need a new page
                if y_pos > 750:
                    page = doc.new_page()
                    y_pos = 50
        
        # Add page numbers
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page.insert_text((500, 800), f"Page {page_num + 1} of {doc.page_count}", 
                            fontsize=9, color=(0.5, 0.5, 0.5))
        
        # Save the PDF
        doc.save(output_path)
        doc.close()
        
        # Clean up the temp file
        os.unlink(temp_md_path)
        
        return output_path
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        # Return None or empty string if PDF generation fails
        return ""


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
    
    # Generate PDF report
    pdf_path = generate_pdf_report(report, client_id, client_name, state)
    new_state["pdf_report_path"] = pdf_path
    
    print(f"\nReport Generation Complete! PDF saved at: {pdf_path}")
    
    return log_action("Report_Generation_Agent", "Final report generated", 
                     {"report_length": len(report), "pdf_path": pdf_path})
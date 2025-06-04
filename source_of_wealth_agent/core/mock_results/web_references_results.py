"""
Mock results for the Web References Agent.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

def get_mock_web_references_result(
    client_id: str, 
    client_name: str = None, 
    verified: bool = True,
    employer: str = "Global Bank Ltd",
    risk_flags: List[str] = None
) -> Dict[str, Any]:
    """
    Generate a mock web references verification result.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        verified: Whether the web references are verified (default: True)
        employer: The employer name (default: "Global Bank Ltd")
        risk_flags: List of risk flags (default: None)
        
    Returns:
        A mock web references verification result
    """
    current_date = datetime.now().isoformat()
    
    # Default client name if not provided
    if client_name is None:
        client_name = f"Client {client_id}"
    
    # Default risk flags if not provided
    if risk_flags is None:
        risk_flags = [] if verified else ["Negative news mentions", "Inconsistent employment history"]
    
    # Generate LinkedIn mentions
    linkedin_mentions = [
        {
            "source": "LinkedIn",
            "url": f"https://www.linkedin.com/in/{client_name.lower().replace(' ', '-')}-{client_id}/",
            "details": f"Profile for {client_name}, {get_position_for_employer(employer)} at {employer}"
        },
        {
            "source": "LinkedIn Analysis",
            "details": f"Profile confirms employment at {employer} for 5+ years",
            "analysis": {
                "found": True,
                "name_match": True,
                "position": get_position_for_employer(employer),
                "company": employer,
                "profile_summary": f"Senior professional with 10+ years experience in financial services, currently at {employer}"
            }
        }
    ]
    
    # Generate financial news mentions
    financial_mentions = []
    
    if verified and not risk_flags:
        # Positive or neutral mentions for verified profiles
        financial_mentions = [
            {
                "source": "Bloomberg",
                "url": f"https://www.bloomberg.com/news/articles/2024-03-15/financial-sector-growth",
                "details": f"{employer} announces expansion plans, quotes from senior management"
            },
            {
                "source": "Financial News Analysis",
                "details": f"Neutral to positive mentions related to {employer}, no specific mentions of {client_name}",
                "analysis": {
                    "found": True,
                    "relevance": 6,
                    "summary": f"Mentions related to {employer} are generally positive, focusing on company growth and industry leadership",
                    "risk_flags": []
                }
            }
        ]
    elif risk_flags:
        # Add negative mentions if risk flags are present
        financial_mentions = [
            {
                "source": "Financial Times",
                "url": f"https://www.ft.com/content/financial-sector-investigation",
                "details": f"Investigation into financial sector practices mentions several institutions including {employer}"
            },
            {
                "source": "Financial News Analysis",
                "details": f"Some concerning mentions related to {employer}, potential regulatory issues",
                "analysis": {
                    "found": True,
                    "relevance": 8,
                    "summary": f"Some negative mentions related to {employer} regarding regulatory compliance. No direct mentions of {client_name}, but association risk exists.",
                    "risk_flags": risk_flags
                }
            }
        ]
    
    # Combine all mentions
    all_mentions = linkedin_mentions + financial_mentions
    
    # Add sentiment analysis if there are mentions
    if all_mentions:
        sentiment_analysis = {
            "source": "Sentiment Analysis Summary",
            "details": get_sentiment_summary(client_name, employer, verified),
            "sentiment": "Positive" if verified and not risk_flags else "Mixed",
            "confidence": 0.85 if verified and not risk_flags else 0.65,
            "analysis_result": {
                "overall_sentiment": "Positive" if verified and not risk_flags else "Mixed",
                "confidence_score": 0.85 if verified and not risk_flags else 0.65,
                "summary_of_findings": get_sentiment_summary(client_name, employer, verified),
                "themes": get_sentiment_themes(client_name, employer, verified),
                "nuances_and_conflicts": get_sentiment_nuances(client_name, employer, verified),
                "risk_factors": risk_flags
            }
        }
        all_mentions.append(sentiment_analysis)
    
    # Create the final result
    return {
        "verified": verified,
        "mentions": all_mentions,
        "risk_flags": risk_flags,
        "search_date": current_date,
        "detailed_sentiment_analysis": sentiment_analysis["analysis_result"] if all_mentions else None
    }

def get_mock_web_references_result_with_specific_risk_flags(
    client_id: str, 
    client_name: str = None, 
    risk_flags: List[str] = None,
    employer: str = "Global Bank Ltd"
) -> Dict[str, Any]:
    """
    Generate a mock web references verification result with specific risk flags.
    
    Args:
        client_id: The client ID
        client_name: The client name (optional)
        risk_flags: List of specific risk flags to include (required)
        employer: The employer name (default: "Global Bank Ltd")
        
    Returns:
        A mock web references verification result with the specified risk flags
    """
    # Ensure risk_flags is a list
    if risk_flags is None:
        risk_flags = []
    
    # Determine if verified based on presence of risk flags
    verified = len(risk_flags) == 0
    
    return get_mock_web_references_result(
        client_id=client_id,
        client_name=client_name,
        verified=verified,
        employer=employer,
        risk_flags=risk_flags
    )

# Helper functions for generating realistic mock data

def get_position_for_employer(employer: str) -> str:
    """Get a realistic position title based on the employer name."""
    if "Bank" in employer or "Financial" in employer:
        return "Senior Investment Manager"
    elif "Tech" in employer or "Software" in employer:
        return "Senior Software Engineer"
    elif "Legal" in employer or "Law" in employer:
        return "Senior Partner"
    elif "Health" in employer or "Medical" in employer:
        return "Chief Medical Officer"
    else:
        return "Senior Manager"

def get_sentiment_summary(client_name: str, employer: str, positive: bool) -> str:
    """Generate a sentiment summary based on the client name and employer."""
    if positive:
        return f"Analysis of web mentions for {client_name} shows predominantly positive sentiment. Professional reputation appears strong, particularly in relation to role at {employer}. No significant negative mentions or risk factors identified."
    else:
        return f"Analysis of web mentions for {client_name} shows mixed sentiment. While professional credentials at {employer} appear legitimate, there are some concerning mentions that may warrant further investigation. Potential risk factors have been identified."

def get_sentiment_themes(client_name: str, employer: str, positive: bool) -> List[Dict[str, Any]]:
    """Generate sentiment themes based on the client name and employer."""
    if positive:
        return [
            {
                "theme": "Professional Reputation",
                "sentiment_for_theme": "Positive",
                "evidence": [
                    f"LinkedIn profile shows consistent career progression at {employer}",
                    "Industry recognition mentioned in multiple sources"
                ]
            },
            {
                "theme": "Financial Conduct",
                "sentiment_for_theme": "Neutral to Positive",
                "evidence": [
                    "No negative mentions related to financial conduct",
                    f"Association with reputable institution ({employer})"
                ]
            }
        ]
    else:
        return [
            {
                "theme": "Professional Reputation",
                "sentiment_for_theme": "Mixed",
                "evidence": [
                    f"LinkedIn profile shows employment at {employer}",
                    "Some inconsistencies in reported role and responsibilities"
                ]
            },
            {
                "theme": "Financial Conduct",
                "sentiment_for_theme": "Concerning",
                "evidence": [
                    "Mentions in articles discussing regulatory investigations",
                    "Association with controversial financial practices"
                ]
            }
        ]

def get_sentiment_nuances(client_name: str, employer: str, positive: bool) -> str:
    """Generate sentiment nuances based on the client name and employer."""
    if positive:
        return "While sentiment is generally positive, it's worth noting that most mentions are professional in nature and may be curated (e.g., LinkedIn profile). Limited personal mentions provide a somewhat incomplete picture."
    else:
        return "The sentiment analysis reveals significant nuances. While professional credentials appear legitimate, there are concerning associations with regulatory issues. It's unclear if these are direct involvement or guilt by association with the employer."

# Sample usage:
# result = get_mock_web_references_result("12345", "John Doe", True)
# result_with_risk_flags = get_mock_web_references_result("12345", "John Doe", False)
# result_with_specific_risk_flags = get_mock_web_references_result_with_specific_risk_flags(
#     "12345", "John Doe", ["PEP status identified", "Negative news mentions"]
# )

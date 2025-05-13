from datetime import datetime
import os
import logging
import time
import requests
import json
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from source_of_wealth_agent.core.state import log_action

class WebReferencesAgent:
    def __init__(self, model, retry_attempts=3):
        self.name = "Web_References_Agent"
        self.model = model
        self.retry_attempts = retry_attempts
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        
        # Configure handler if not already set up
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def search_linkedin(self, client_name: str, employer: Optional[str] = None) -> List[Dict[str, str]]:
        """Search for LinkedIn profile information"""
        self.logger.info(f"Searching LinkedIn for {client_name}")
        
        query = f"{client_name}"
        if employer:
            query += f" {employer}"
            
        search_url = f"https://www.google.com/search?q=site:linkedin.com+{quote_plus(query)}"
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = []
            
            # Extract search result links and snippets
            for result in soup.select('div.g'):
                link_elem = result.select_one('a')
                snippet_elem = result.select_one('div.VwiC3b')
                
                if link_elem and snippet_elem:
                    link = link_elem.get('href')
                    snippet = snippet_elem.get_text()
                    
                    if 'linkedin.com/in/' in link:
                        search_results.append({
                            "source": "LinkedIn",
                            "url": link,
                            "details": snippet
                        })
            
            # Use the model to analyze results
            if search_results:
                analysis_prompt = f"""
                Analyze these LinkedIn search results for {client_name}:
                {json.dumps(search_results)}
                
                Return a JSON object with the following fields:
                - found: boolean indicating if a likely profile was found
                - name_match: boolean indicating if the name matches closely
                - position: any position/title mentioned
                - company: any company mentioned
                - profile_summary: brief summary of what was found
                """
                
                analysis = self.model.invoke(analysis_prompt)
                
                try:
                    # Try to extract JSON from the response
                    analysis_text = analysis.content if hasattr(analysis, 'content') else analysis
                    if "```json" in analysis_text:
                        analysis_json = json.loads(analysis_text.split("```json")[1].split("```")[0].strip())
                    elif "```" in analysis_text:
                        analysis_json = json.loads(analysis_text.split("```")[1].split("```")[0].strip())
                    else:
                        analysis_json = json.loads(analysis_text)
                        
                    search_results.append({
                        "source": "LinkedIn Analysis",
                        "details": analysis_json["profile_summary"] if "profile_summary" in analysis_json else "Analysis performed",
                        "analysis": analysis_json
                    })
                except Exception as e:
                    self.logger.error(f"Error parsing LinkedIn analysis: {str(e)}")
                    search_results.append({
                        "source": "LinkedIn Analysis Error", 
                        "details": f"Failed to analyze: {str(e)}"
                    })
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"LinkedIn search error: {str(e)}")
            return [{"source": "LinkedIn", "details": f"Search failed: {str(e)}"}]

    def search_financial_news(self, client_name: str, company: Optional[str] = None) -> List[Dict[str, str]]:
        """Search for financial news mentions"""
        self.logger.info(f"Searching financial news for {client_name}")
        
        query = f"{client_name}"
        if company:
            query += f" {company}"
            
        search_sites = ["site:finance.yahoo.com", "site:bloomberg.com", "site:ft.com", "site:cnbc.com"]
        search_results = []
        
        for site in search_sites:
            try:
                search_url = f"https://www.google.com/search?q={site}+{quote_plus(query)}"
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(search_url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract search result links and snippets
                for result in soup.select('div.g'):
                    link_elem = result.select_one('a')
                    snippet_elem = result.select_one('div.VwiC3b')
                    
                    if link_elem and snippet_elem:
                        link = link_elem.get('href')
                        snippet = snippet_elem.get_text()
                        
                        site_name = site.replace("site:", "").replace(".com", "").title()
                        search_results.append({
                            "source": site_name,
                            "url": link,
                            "details": snippet
                        })
                
                # Limit to top 3 results per site
                if len(search_results) > 3 * len(search_sites):
                    break
                    
            except Exception as e:
                self.logger.error(f"Financial news search error ({site}): {str(e)}")
                
        # Use the model to analyze results
        if search_results:
            analysis_prompt = f"""
            Analyze these financial news search results for {client_name}:
            {json.dumps(search_results)}
            
            Return a JSON object with the following fields:
            - found: boolean indicating if relevant mentions were found
            - relevance: rating from 0-10 of how relevant the mentions are
            - summary: brief summary of what was found
            - risk_flags: list of any potential risk flags or negative mentions
            """
            
            analysis = self.model.invoke(analysis_prompt)
            
            try:
                # Try to extract JSON from the response
                analysis_text = analysis.content if hasattr(analysis, 'content') else analysis
                if "```json" in analysis_text:
                    analysis_json = json.loads(analysis_text.split("```json")[1].split("```")[0].strip())
                elif "```" in analysis_text:
                    analysis_json = json.loads(analysis_text.split("```")[1].split("```")[0].strip())
                else:
                    analysis_json = json.loads(analysis_text)
                    
                search_results.append({
                    "source": "Financial News Analysis",
                    "details": analysis_json["summary"] if "summary" in analysis_json else "Analysis performed",
                    "analysis": analysis_json
                })
            except Exception as e:
                self.logger.error(f"Error parsing financial news analysis: {str(e)}")
                search_results.append({
                    "source": "Financial News Analysis Error", 
                    "details": f"Failed to analyze: {str(e)}"
                })
        
        return search_results

    def run(self, state):
        client_name = state.get("client_name", "Unknown")
        self.logger.info(f"🌐 Checking web references for: {client_name}")

        # Get employer if available from payslip verification
        employer = None
        if "payslip_verification" in state and state["payslip_verification"]:
            employer = state["payslip_verification"].get("employer")

        attempts = 0
        while attempts < self.retry_attempts:
            try:
                # Perform the web searches
                linkedin_results = self.search_linkedin(client_name, employer)
                financial_results = self.search_financial_news(client_name, employer)
                
                # Combine results
                all_mentions = linkedin_results + financial_results
                
                # Extract risk flags
                risk_flags = []
                for result in all_mentions:
                    if "analysis" in result and "risk_flags" in result["analysis"]:
                        risk_flags.extend(result["analysis"]["risk_flags"])

                # Construct the results
                web_results = {
                    "mentions": all_mentions,
                    "risk_flags": risk_flags,
                    "search_date": datetime.now().isoformat(),
                    "verified": True
                }

                # Update the state
                state["web_references"] = web_results
                log_action(state, self.name, "Web references check completed", web_results)
                return state

            except Exception as e:
                attempts += 1
                self.logger.error(f"Error in web reference check (attempt {attempts}): {str(e)}")
                if attempts >= self.retry_attempts:
                    # Return partial results or error state
                    web_results = {
                        "verified": False,
                        "error": str(e),
                        "search_date": datetime.now().isoformat()
                    }
                    state["web_references"] = web_results
                    log_action(state, self.name, "Web references check failed", {"error": str(e)})
                    return state
                time.sleep(2 ** attempts)  # Exponential backoff
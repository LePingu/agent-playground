from datetime import datetime
from langchain_openai import ChatOpenAI

from source_of_wealth_agent.core.state import log_action

class FinancialReportsAgent:
    def __init__(self, model):
        self.name = "Financial_Reports_Agent"
        self.model = model

    def run(self, state):
        print(f"📊 Checking financial reports for client: {state['client_id']}")

        financial_data = {
            "reports_analyzed": ["Credit Report", "Investment Portfolio", "Tax Returns"],
            "annual_income_range": "100,000 - 200,000",
            "investment_assets": "500,000+",
            "credit_score": "Excellent",
            "analysis_date": datetime.now().isoformat()
        }

        state.financial_reports = financial_data
        log_action(state, self.name, "Financial reports analysis completed", financial_data)
        return state
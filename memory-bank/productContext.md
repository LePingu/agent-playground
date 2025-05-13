# Product Context: Source of Wealth Multi-Agent System

## Business Need
Banks and financial institutions are required by regulatory bodies to verify the source of wealth for their clients as part of Anti-Money Laundering (AML) and Know Your Customer (KYC) compliance. This verification process is traditionally manual, time-consuming, and prone to human error. The Source of Wealth Multi-Agent System addresses these challenges by automating and enhancing the verification process while maintaining human oversight.

## Problems Solved

### 1. Efficiency and Scalability
- **Problem**: Manual verification of source of wealth is time-consuming and difficult to scale.
- **Solution**: The multi-agent system automates the collection and analysis of client data, allowing for faster processing and the ability to handle more clients simultaneously.

### 2. Consistency and Standardization
- **Problem**: Manual verification can lead to inconsistent assessments depending on the reviewer.
- **Solution**: The system applies standardized criteria and risk assessment methodologies, ensuring consistent evaluation across all clients.

### 3. Comprehensive Data Analysis
- **Problem**: Human reviewers may miss connections or inconsistencies across different data sources.
- **Solution**: The multi-agent system correlates information from multiple sources (ID documents, payslips, web references, financial reports) to identify discrepancies and verify consistency.

### 4. Risk Assessment
- **Problem**: Risk assessment can be subjective and may not consider all relevant factors.
- **Solution**: The system uses a quantitative risk scoring methodology based on multiple verification points, providing objective risk assessments.

### 5. Audit Trail and Compliance
- **Problem**: Maintaining comprehensive records for regulatory compliance can be challenging.
- **Solution**: The system automatically logs all verification steps, decisions, and human approvals, creating a complete audit trail for regulatory compliance.

## User Experience Goals

### For Bank Compliance Officers
1. **Streamlined Workflow**: Reduce manual data collection and analysis
2. **Clear Risk Assessment**: Provide clear, quantitative risk assessments with supporting evidence
3. **Human Control**: Maintain oversight and approval at critical decision points
4. **Comprehensive Reporting**: Generate detailed reports for internal review and regulatory compliance
5. **Visualization**: Provide visual representations of verification workflow and results

### For Bank Management
1. **Efficiency**: Reduce time and resources required for source of wealth verification
2. **Compliance Assurance**: Ensure consistent compliance with regulatory requirements
3. **Risk Management**: Improve identification of high-risk clients
4. **Scalability**: Handle increasing verification requirements without proportional increase in staff
5. **Audit Readiness**: Maintain comprehensive documentation for regulatory audits

## Key Differentiators

### 1. Multi-Agent Architecture
The system uses specialized agents for different aspects of verification, allowing for deep expertise in each area while maintaining coordination through the orchestrator.

### 2. Human-in-the-Loop Design
Unlike fully automated systems, this solution maintains human oversight at critical decision points, combining the efficiency of automation with human judgment.

### 3. Dual-Model Approach
The system uses different language models based on data sensitivity:
- Local models (Ollama) for sensitive client data
- Cloud models (OpenRouter) for external data analysis

### 4. Comprehensive Corroboration
The system doesn't just collect data; it actively corroborates information across multiple sources to verify consistency and identify discrepancies.

### 5. Interactive Jupyter Interface
The Jupyter notebook interface allows for interactive use, enabling compliance officers to provide input and review results in real-time.

## Success Metrics
1. **Time Reduction**: Reduce time required for source of wealth verification by 70%
2. **Accuracy Improvement**: Improve accuracy of risk assessments by 50% compared to manual process
3. **Compliance Rate**: Achieve 100% compliance with regulatory requirements
4. **User Adoption**: Achieve 90% adoption rate among compliance officers
5. **Cost Reduction**: Reduce cost of compliance operations by 40%

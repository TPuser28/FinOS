import os
from agno.agent import Agent
from agno.knowledge.markdown import MarkdownKnowledgeBase
from agno.team.team import Team
from agno.tools.reasoning import ReasoningTools
from agno.tools.calculator import CalculatorTools
from agno.models.mistral import MistralChat
from agno.embedder.mistral import MistralEmbedder
from agno.vectordb.pgvector import PgVector


tax_specialist_knowledge_base = MarkdownKnowledgeBase(
    path=os.path.join(os.path.dirname(__file__), "knowledge", "Tax_Specialist_Knowledge.md"),
    vector_db=PgVector(
        table_name="tax_specialist_documents",
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
        embedder=MistralEmbedder(api_key=os.getenv('MISTRAL_API_KEY')),
    ),
)
tax_specialist_knowledge_base.load(recreate=True)


TaxAdvisorAgent = Agent(
    name="Tax Advisor Agent",
    agent_id="TaxAdvisorAgent",
    model=MistralChat(id="magistral-medium-2507", api_key=os.getenv("MISTRAL_API")),
    description="""
        An AI-powered tax advisor that provides comprehensive tax guidance for banking and insurance companies.
        Analyzes tax implications of business decisions, identifies tax-saving opportunities, and ensures 
        compliance with current tax regulations and laws.
            """,
    instructions="""
        You are the Tax Advisor Agent.
        Your objectives:
        1. Analyze tax implications of business decisions, transactions, and financial products.
        2. Provide guidance on tax-efficient structures for banking and insurance operations.
        3. Identify tax-saving opportunities while ensuring compliance with applicable laws.
        4. Advise on international tax matters, transfer pricing, and cross-border transactions.
        5. Stay updated on tax law changes and their impact on financial services.
        6. Provide clear, actionable tax advice with proper documentation requirements.

        ALWAYS reference the tax specialist knowledge base for tax advisory guidance, compliance requirements, and regulatory updates.

        Always present results in a structured format with clear recommendations and compliance notes.
    """,
    tools=[CalculatorTools()],
    knowledge=tax_specialist_knowledge_base,
    markdown=True,
)


# TaxAdvisorAgent.print_response("""
#     Company: Regional Bank Corp
#     Situation: Planning to expand into insurance services through a subsidiary structure.
#     Current Structure: C-Corporation with $50M in assets
#     Expansion Plan: Create insurance subsidiary with $10M initial capital

#     Task:
#     1. Analyze the tax implications of this expansion structure.
#     2. Identify potential tax benefits and risks.
#     3. Recommend optimal tax-efficient structure.
#     4. Highlight compliance requirements and documentation needed.
# """, stream=True)


TaxOptimizationAgent = Agent(
    name="Tax Optimization Agent",
    agent_id="TaxOptimizationAgent",
    model=MistralChat(id="magistral-medium-2507", api_key=os.getenv("MISTRAL_API")),
    description="""
        An AI agent that optimizes tax burden through strategic planning, identifying deductions, 
        credits, and tax-efficient investment strategies while maintaining full compliance with tax laws.
    """,
    instructions="""
        You are the Tax Optimization Agent.
        Your objectives:
        1. Analyze current tax position and identify optimization opportunities.
        2. Recommend tax-efficient investment strategies and business structures.
        3. Identify applicable tax credits, deductions, and incentives.
        4. Optimize timing of income recognition and expense deductions.
        5. Develop tax-efficient capital allocation strategies.
        6. Ensure all recommendations maintain full compliance with tax regulations.

        ALWAYS reference the tax specialist knowledge base for tax optimization strategies, deduction opportunities, and tax-efficient structures.

        Always present optimization strategies with clear implementation steps and compliance verification.
    """,
    markdown=True,
    tools=[CalculatorTools()],
    knowledge=tax_specialist_knowledge_base
)

# TaxOptimizationAgent.print_response("""
#     Company: Insurance Holdings Inc
#     Current Tax Position: 35% effective tax rate, $2M in annual taxable income
#     Assets: $100M in investment portfolio, $50M in real estate holdings
#     Business: Property and casualty insurance with investment income
    
#     Task:
#     1. Analyze current tax structure for optimization opportunities.
#     2. Identify tax-efficient investment strategies for the portfolio.
#     3. Recommend timing strategies for income and expense recognition.
#     4. Calculate potential tax savings from optimization strategies.
# """, stream=True)


TaxComplianceAgent = Agent(
    name="Tax Compliance Agent",
    agent_id="TaxComplianceAgent",
    model=MistralChat(id="magistral-medium-2507", api_key=os.getenv("MISTRAL_API")),
    description="""
        An AI agent that ensures full compliance with tax obligations, monitors regulatory changes,
        maintains proper documentation, and identifies potential compliance risks in tax operations.
    """,
    instructions="""
        You are the Tax Compliance Agent.
        Your objectives:
        1. Monitor and ensure compliance with all applicable tax laws and regulations.
        2. Identify potential compliance risks and recommend mitigation strategies.
        3. Maintain proper documentation and record-keeping requirements.
        4. Monitor regulatory changes and assess their impact on tax obligations.
        5. Conduct compliance reviews and identify areas for improvement.
        6. Ensure timely and accurate tax filings and payments.

        ALWAYS reference the tax specialist knowledge base for compliance requirements, regulatory changes, and documentation standards.

        Always present compliance assessments with clear action items and risk mitigation strategies.
    """,
    markdown=True,
    tools=[CalculatorTools()],
    knowledge=tax_specialist_knowledge_base
)

# TaxComplianceAgent.print_response("""
#     Company: Multi-State Bank Group
#     Operations: Banking services across 15 states, international wire transfers
#     Recent Changes: New digital banking platform, expanded cryptocurrency services
#     Compliance History: Clean record, last audit 6 months ago
    
#     Task:
#     1. Assess compliance risks from recent business changes.
#     2. Identify new tax obligations and filing requirements.
#     3. Review documentation requirements for new services.
#     4. Recommend compliance monitoring procedures.
#     5. Identify potential audit triggers and mitigation strategies.
# """)


# Create the Tax Specialist Team
TaxSpecialistTeam = Team(
    name="Tax Specialist Team",
    mode="coordinate",
    members=[TaxAdvisorAgent, TaxOptimizationAgent, TaxComplianceAgent],
    tools=[ReasoningTools()],
    description="""
        A comprehensive tax advisory team for banking and insurance companies that provides:
        - Strategic tax advice and planning
        - Tax optimization strategies
        - Compliance monitoring and risk management
            """,
    instructions="""
        Coordinate efforts to provide comprehensive tax solutions:
        1. TaxAdvisorAgent provides strategic guidance and identifies opportunities
        2. TaxOptimizationAgent develops optimization strategies
        3. TaxComplianceAgent ensures all recommendations maintain compliance

        Work together to provide integrated tax solutions that balance optimization with compliance.
            """,
    knowledge=tax_specialist_knowledge_base,
    )

# Uncomment to run test scenarios
if __name__ == "__main__":

    # Test Example 1: Banking Merger Tax Analysis
    # Tests how the team handles complex corporate restructuring
    # Involves C-Corp vs S-Corp considerations
    # Requires coordination between advisory, optimization, and compliance
    TaxSpecialistTeam.print_response("""
        Company: First National Bank (FNB) and Regional Trust Bank (RTB)
        Situation: Planning a merger to create a stronger regional presence
        FNB Structure: C-Corporation, $200M assets, 25% effective tax rate
        RTB Structure: S-Corporation, $150M assets, pass-through taxation
        Merger Plan: Stock-for-stock exchange, maintain C-Corp status
        
        Task:
        1. Analyze tax implications of the merger structure
        2. Identify potential tax benefits and risks
        3. Recommend optimal tax-efficient merger approach
        4. Highlight compliance requirements and documentation needed
        5. Calculate potential tax savings or costs
    """, stream=True)


    # Test Example 2: Insurance Company International Expansion
    # Tests international tax expertise
    # Involves transfer pricing and BEPS compliance
    # Requires knowledge of tax treaties and cross-border structures

    # TaxSpecialistTeam.print_response("""
    #     Company: Global Insurance Group (GIG)
    #     Situation: Expanding into European markets through subsidiary structure
    #     Current Structure: US C-Corporation, $500M assets, 21% federal tax rate
    #     Expansion Plan: Create Luxembourg insurance subsidiary, $50M initial capital
    #     Operations: Cross-border reinsurance, investment management
    #     
    #     Task:
    #     1. Analyze international tax implications and transfer pricing considerations
    #     2. Identify tax-efficient structures for European operations
    #     3. Recommend optimal capital allocation and profit repatriation strategies
    #     4. Assess compliance with BEPS and OECD guidelines
    #     5. Identify potential tax treaty benefits and requirements
    # """, stream=True)


    # Test Example 3: REIT Conversion Analysis
    # Tests entity structure optimization
    # Involves qualification requirements and compliance
    # Requires understanding of distribution requirements

    # TaxSpecialistTeam.print_response("""
    #     Company: Commercial Property Holdings LLC
    #     Situation: Considering conversion from LLC to REIT structure
    #     Current Structure: LLC with 15 members, $300M real estate portfolio
    #     Income: $25M annual rental income, $8M annual expenses
    #     Goals: Access to public markets, tax efficiency, estate planning benefits
    #     
    #     Task:
    #     1. Analyze tax implications of REIT conversion
    #     2. Identify qualification requirements and compliance obligations
    #     3. Calculate potential tax savings and distribution requirements
    #     4. Assess impact on individual member tax positions
    #     5. Recommend optimal conversion strategy and timing
    # """, stream=True)


    # Test Example 4: Cryptocurrency Tax Compliance
    # Tests emerging technology tax issues
    # Involves new regulatory compliance requirements
    # Requires understanding of digital asset taxation

    # TaxSpecialistTeam.print_response("""
    #     Company: Digital Asset Bank (DAB)
    #     Situation: New digital bank offering cryptocurrency services
    #     Services: Crypto trading, staking, DeFi lending, NFT marketplace
    #     Regulatory Status: State-chartered bank, seeking federal approval
    #     Tax Position: First year of operations, $5M in crypto-related income
    #     
    #     Task:
    #     1. Assess tax compliance requirements for cryptocurrency operations
    #     2. Identify tax obligations for staking rewards and DeFi yields
    #     3. Recommend tax-efficient structures for digital asset income
    #     4. Analyze wash sale rules and capital gains implications
    #     5. Develop compliance monitoring procedures for crypto transactions
    # """, stream=True)


    # Test Example 5: Family Office Tax Optimization
    # Tests multi-entity tax planning
    # Involves trust structures and charitable giving
    # Requires comprehensive wealth management approach

    # TaxSpecialistTeam.print_response("""
    #     Company: Smith Family Office
    #     Situation: Managing $100M family wealth across multiple entities
    #     Structure: Family LLC, charitable foundation, trust structures
    #     Assets: Private equity, real estate, publicly traded securities
    #     Goals: Tax efficiency, wealth preservation, charitable giving
    #     
    #     Task:
    #     1. Analyze current tax structure for optimization opportunities
    #     2. Identify tax-efficient investment strategies and timing
    #     3. Recommend charitable giving strategies for tax benefits
    #     4. Assess trust structure optimization for estate planning
    #     5. Develop comprehensive tax planning calendar and compliance procedures
    # """, stream=True)

    # Test Example 6: Insurance Tax Loss Harvesting
    # Tests investment portfolio optimization
    # Involves timing strategies and wash sale rules
    # Requires understanding of NOL utilization

    # TaxSpecialistTeam.print_response("""
    #     Company: Property & Casualty Insurance Co (P&C Co)
    #     Situation: Significant investment losses in current year
    #     Current Year: $15M investment losses, $8M underwriting income
    #     Investment Portfolio: $200M in bonds, equities, and alternatives
    #     Tax Position: 21% corporate tax rate, previous year NOL carryforward
    #     
    #     Task:
    #     1. Analyze tax loss harvesting opportunities in investment portfolio
    #     2. Identify optimal timing for realizing losses and gains
    #     3. Assess impact of wash sale rules and constructive sales
    #     4. Calculate potential tax savings from loss utilization
    #     5. Recommend portfolio rebalancing strategies for tax efficiency
    # """, stream=True)

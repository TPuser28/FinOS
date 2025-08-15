from agno.agent import Agent
from agno.team.team import Team
from agno.models.mistral import MistralChat
from agno.tools.file import FileTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.calculator import CalculatorTools
from dotenv import load_dotenv
import os
import statistics
from datetime import datetime
from agno.knowledge.markdown import MarkdownKnowledgeBase
from agno.vectordb.pgvector import PgVector


load_dotenv()


knowledge_base = MarkdownKnowledgeBase(
    path="Knowledge/Accounting_Standards.md",
    vector_db=PgVector(
        table_name="accounting_standards_documents",
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
    )
)

def validate_transaction(transaction_data):
    """
    Validate a single transaction for required fields and data integrity.
    Returns (bool, list_of_errors).
    """
    errors = []
    # Required fields
    required_fields = ["date", "amount", "account_code", "description", "type"]  
    for field in required_fields:
        if field not in transaction_data or transaction_data[field] in [None, "", " "]:
            errors.append(f"Missing or empty field: {field}")
    # Date validation
    try:
        datetime.strptime(transaction_data.get("date", ""), "%Y-%m-%d")
    except ValueError:
        errors.append("Invalid date format, expected YYYY-MM-DD")
    # Amount validation
    if not isinstance(transaction_data.get("amount"), (int, float)):
        errors.append("Amount must be numeric")
    # Account code validation (example: must be numeric and length 4)
    if not str(transaction_data.get("account_code", "")).isdigit():
        errors.append("Invalid account code: must be numeric")
    return (len(errors) == 0, errors)


def correct_common_errors(transaction_data):
    """
    Apply automatic corrections to common transaction errors.
    Returns corrected transaction_data and list of applied corrections.
    """
    corrections = []
    # Trim description
    if transaction_data.get("description"):
        transaction_data["description"] = transaction_data["description"].strip()
    # Normalize account code to string with leading zeros
    if "account_code" in transaction_data and transaction_data["account_code"]:
        if isinstance(transaction_data["account_code"], int):
            transaction_data["account_code"] = str(transaction_data["account_code"]).zfill(4)
            corrections.append("Normalized account code format")
    # Ensure amount is float
    if "amount" in transaction_data:
        try:
            transaction_data["amount"] = float(transaction_data["amount"])
        except ValueError:
            corrections.append("Amount correction failed - non-numeric")
    return transaction_data, corrections


def check_duplicate_transactions(transactions):
    """
    Check for potential duplicate transactions based on amount, account, and date.
    Returns list of (transaction, duplicate_info) for potential duplicates.
    """
    duplicates = []
    for i, t1 in enumerate(transactions):
        for j, t2 in enumerate(transactions[i+1:], i+1):
            # Check for exact duplicates
            if (t1.get("amount") == t2.get("amount") and 
                t1.get("account_code") == t2.get("account_code") and
                t1.get("date") == t2.get("date") and
                t1.get("description") == t2.get("description")):
                duplicates.append((t1, {"type": "exact_duplicate", "duplicate_of": t2}))
            # Check for near-duplicates (same amount, account, same day)
            elif (t1.get("amount") == t2.get("amount") and 
                  t1.get("account_code") == t2.get("account_code") and
                  t1.get("date") == t2.get("date")):
                duplicates.append((t1, {"type": "near_duplicate", "duplicate_of": t2}))
    return duplicates


def validate_business_rules(transaction_data, business_rules=None):
    """
    Validate transaction against business rules and account code ranges.
    Returns (bool, list_of_violations).
    """
    if business_rules is None:
        business_rules = {
            "account_code_ranges": {
                "assets": (1000, 1999),
                "liabilities": (2000, 2999),
                "equity": (3000, 3999),
                "revenue": (4000, 4999),
                "expenses": (5000, 5999)
            },
            "max_amount": 1000000,
            "min_amount": 0.01,
            "prohibited_accounts": ["0000", "9999"]
        }
    
    violations = []
    
    # Account code range validation
    account_code = int(transaction_data.get("account_code", 0))
    valid_range = False
    for category, (min_code, max_code) in business_rules["account_code_ranges"].items():
        if min_code <= account_code <= max_code:
            valid_range = True
            break
    
    if not valid_range:
        violations.append(f"Account code {account_code} is outside valid ranges")
    
    # Amount validation
    amount = transaction_data.get("amount", 0)
    if amount > business_rules["max_amount"]:
        violations.append(f"Amount {amount} exceeds maximum allowed {business_rules['max_amount']}")
    if amount < business_rules["min_amount"]:
        violations.append(f"Amount {amount} is below minimum allowed {business_rules['min_amount']}")
    
    # Prohibited accounts
    if str(transaction_data.get("account_code")) in business_rules["prohibited_accounts"]:
        violations.append(f"Account code {transaction_data.get('account_code')} is prohibited")
    
    return (len(violations) == 0, violations)


AccountingEntryValidator = Agent(
    name="Accounting Entry Validator",
    model=MistralChat(id="magistral-medium-2507", api_key=os.getenv("MISTRAL_API")),
    tools=[FileTools(), ReasoningTools(), CalculatorTools(), validate_transaction, correct_common_errors, check_duplicate_transactions, validate_business_rules],
    description="""
        You are an Accounting Entry Validator Agent responsible for performing the first level of verification 
        on accounting transactions. Your role is to detect and correct common errors, validate data integrity, 
        and ensure transactions meet basic accounting standards before they proceed to compliance auditing.
        
        Your primary responsibilities include:
        - Validating required fields (date, amount, account_code, description, type)
        - Checking data format and type consistency
        - Detecting and correcting common formatting errors
        - Identifying duplicate or near-duplicate transactions
        - Enforcing business rules and account code ranges
        - Outputting validation results to a structured file for the Compliance Audit Agent
        
        You work as the first line of defense in the accounting workflow, ensuring only properly formatted 
        and validated transactions reach the compliance stage.
    """,
    instructions="""
        When processing accounting transactions:
        
        1. **Initial Validation**: Use validate_transaction() to check each transaction for required fields, 
           data types, and format compliance.
        
        2. **Error Correction**: Apply correct_common_errors() to automatically fix common issues like 
           whitespace, account code formatting, and data type conversions.
        
        3. **Duplicate Detection**: Use check_duplicate_transactions() to identify potential duplicate 
           entries that could cause accounting errors.
        
        4. **Business Rule Validation**: Apply validate_business_rules() to ensure transactions follow 
           established accounting standards and account code ranges.
        
        5. **Error Handling**: For transactions that cannot be automatically corrected, clearly document 
           the issues and mark them for manual review. This step is crucial before creating the output file.
        
        6. **Output Generation**: Create a comprehensive validation report file containing:
           - List of validated transactions with corrections applied
           - Summary of validation errors found and resolved
           - Duplicate transaction alerts
           - Business rule violations
           - Overall validation status for each transaction
           - List of transactions requiring manual review
        
        7. **File Output Using FileTools**: Use FileTools to save your validation results to 
           "validated_transactions.json" in the current directory. This file will be used by the 
           Compliance Audit Agent for further analysis. Use the write_file() method from FileTools 
           to create this structured JSON file.
        
        Always prioritize data accuracy and provide clear audit trails of all changes made.
    """,
    knowledge=knowledge_base,
    markdown=True,
    stream=True,
)


def detect_anomalies(transactions):
    """
    Detect statistical anomalies based on transaction amounts.
    Returns list of (transaction, reason) for anomalies.
    """
    anomalies = []
    amounts = [t["amount"] for t in transactions if isinstance(t.get("amount"), (int, float))]
    if not amounts:
        return anomalies
    mean_val = statistics.mean(amounts)
    stdev_val = statistics.stdev(amounts) if len(amounts) > 1 else 0
    for t in transactions:
        if isinstance(t.get("amount"), (int, float)) and stdev_val > 0:
            z_score = abs((t["amount"] - mean_val) / stdev_val)
            if z_score > 3:  # Threshold for anomaly
                anomalies.append((t, f"Amount anomaly (z-score {z_score:.2f})"))
    return anomalies


def identify_patterns(transactions):
    """
    Identify recurring patterns (e.g., frequent same amount, repeated account codes).
    Returns dict of detected patterns.
    """
    patterns = {
        "frequent_amounts": {},
        "frequent_accounts": {}
    }
    for t in transactions:
        amt = t.get("amount")
        acc = t.get("account_code")
        if amt:
            patterns["frequent_amounts"][amt] = patterns["frequent_amounts"].get(amt, 0) + 1
        if acc:
            patterns["frequent_accounts"][acc] = patterns["frequent_accounts"].get(acc, 0) + 1
    # Filter to only show frequent items (>= 3 occurrences)
    patterns["frequent_amounts"] = {k: v for k, v in patterns["frequent_amounts"].items() if v >= 3}
    patterns["frequent_accounts"] = {k: v for k, v in patterns["frequent_accounts"].items() if v >= 3}
    return patterns


def check_compliance(transaction, standards):
    """
    Check transaction against a set of compliance rules.
    `standards` is expected to be a dict containing accounting rules.
    Returns list of violations.
    """
    violations = []
    # Example compliance checks
    if "max_amount" in standards and transaction.get("amount") > standards["max_amount"]:
        violations.append(f"Amount exceeds maximum allowed ({standards['max_amount']})")
    if "prohibited_accounts" in standards and transaction.get("account_code") in standards["prohibited_accounts"]:
        violations.append(f"Use of prohibited account code: {transaction.get('account_code')}")
    return violations


def generate_compliance_report(transactions):
    """
    Generate a compliance report for all transactions.
    Returns dict with summary and violations.
    """
    report = {
        "total_transactions": len(transactions),
        "violations": [],
        "summary": ""
    }
    # Example: Load compliance rules
    compliance_rules = {
        "max_amount": 100000,  # Example: max allowed amount
        "prohibited_accounts": ["9999"]
    }
    for t in transactions:
        violations = check_compliance(t, compliance_rules)
        if violations:
            report["violations"].append({"transaction": t, "violations": violations})
    report["summary"] = f"Found {len(report['violations'])} transactions with compliance issues."
    return report


def cross_reference_regulatory_database(transaction, regulatory_db=None):
    """
    Cross-reference transaction with external regulatory database for compliance.
    Returns list of regulatory findings.
    """
    if regulatory_db is None:
        # Mock regulatory database - in real implementation, this would connect to external API
        regulatory_db = {
            "suspicious_patterns": [
                {"pattern": "round_amounts", "threshold": 10000, "risk": "medium"},
                {"pattern": "frequent_small_amounts", "threshold": 100, "risk": "high"}
            ],
            "regulated_entities": ["12345", "67890"],
            "restricted_transactions": ["gambling", "cryptocurrency"]
        }
    
    findings = []
    
    # Check for suspicious patterns
    amount = transaction.get("amount", 0)
    if amount >= 10000 and amount % 1000 == 0:  # Round amounts
        findings.append("Large round amount detected - may require additional scrutiny")
    
    # Check for frequent small amounts (would need transaction history)
    if amount <= 100:
        findings.append("Small amount transaction - monitor for structuring patterns")
    
    # Check against restricted transaction types
    description = transaction.get("description", "").lower()
    for restricted in regulatory_db["restricted_transactions"]:
        if restricted in description:
            findings.append(f"Transaction description contains restricted term: {restricted}")
    
    return findings


def analyze_historical_compliance_trends(transactions, historical_data=None):
    """
    Analyze historical compliance trends and patterns over time.
    Returns dict with trend analysis and risk indicators.
    """
    if historical_data is None:
        # Mock historical data - in real implementation, this would query database
        historical_data = {
            "monthly_violations": [5, 3, 7, 2, 4, 6, 3, 5, 4, 3, 6, 4],
            "common_violation_types": ["amount_limit", "account_code", "duplicate"],
            "seasonal_patterns": {"Q4": "high", "Q1": "low", "Q2": "medium", "Q3": "medium"}
        }
    
    analysis = {
        "trend_direction": "",
        "risk_level": "",
        "seasonal_factors": [],
        "recommendations": []
    }
    
    # Analyze violation trends
    violations = historical_data["monthly_violations"]
    if len(violations) >= 2:
        recent_avg = sum(violations[-3:]) / 3
        older_avg = sum(violations[:-3]) / (len(violations) - 3) if len(violations) > 3 else violations[0]
        
        if recent_avg > older_avg * 1.2:
            analysis["trend_direction"] = "increasing"
            analysis["risk_level"] = "high"
            analysis["recommendations"].append("Implement stricter validation rules")
        elif recent_avg < older_avg * 0.8:
            analysis["trend_direction"] = "decreasing"
            analysis["risk_level"] = "low"
        else:
            analysis["trend_direction"] = "stable"
            analysis["risk_level"] = "medium"
    
    # Identify seasonal patterns
    current_month = datetime.now().month
    if current_month in [10, 11, 12]:  # Q4
        analysis["seasonal_factors"].append("Q4 typically shows higher violation rates")
        analysis["recommendations"].append("Increase monitoring during Q4")
    
    # Add recommendations based on common violations
    if "amount_limit" in historical_data["common_violation_types"]:
        analysis["recommendations"].append("Review and adjust amount limits")
    
    return analysis


ComplianceAuditAgent = Agent(
    name="Compliance Audit Agent",
    model=MistralChat(id="mistral-large-latest", api_key=os.getenv("MISTRAL_API")),
    tools=[FileTools(), ReasoningTools(), CalculatorTools(), detect_anomalies, identify_patterns, check_compliance, generate_compliance_report, cross_reference_regulatory_database, analyze_historical_compliance_trends],
    description="""
        You are a Compliance Audit Agent responsible for performing in-depth checks on validated accounting 
        transactions to ensure compliance with accounting and regulatory standards. You receive pre-validated 
        transactions from the Accounting Entry Validator and perform advanced compliance analysis.
        
        Your primary responsibilities include:
        - Reading validated transaction data from the Accounting Entry Validator's output file
        - Performing statistical anomaly detection on transaction amounts and patterns
        - Identifying recurring transaction patterns that may indicate compliance risks
        - Cross-referencing transactions against regulatory databases and compliance rules
        - Analyzing historical compliance trends to identify risk patterns
        - Generating comprehensive compliance reports with actionable recommendations
        
        You are the second line of defense in the accounting workflow, focusing on regulatory compliance, 
        fraud detection, and risk assessment after basic validation is complete.
    """,
    instructions="""
        When performing compliance audits:
        
        1. **Input Processing**: Read the validated transactions from "validated_transactions.json" 
           (output from Accounting Entry Validator) using FileTools. This file contains pre-validated 
           transactions ready for compliance analysis.
        
        2. **Anomaly Detection**: Use detect_anomalies() to identify statistical outliers in transaction 
           amounts that may indicate unusual activity or potential fraud.
        
        3. **Pattern Analysis**: Apply identify_patterns() to detect recurring transaction patterns, 
           frequent amounts, and account usage that could signal compliance risks.
        
        4. **Compliance Checking**: Use check_compliance() to validate transactions against established 
           compliance rules, amount limits, and prohibited account codes.
        
        5. **Regulatory Cross-Reference**: Apply cross_reference_regulatory_database() to check 
           transactions against external regulatory requirements and identify suspicious patterns.
        
        6. **Historical Trend Analysis**: Use analyze_historical_compliance_trends() to examine 
           compliance patterns over time and identify emerging risks or seasonal factors.
        
        7. **Report Generation**: Create a comprehensive compliance audit report using 
           generate_compliance_report() that includes:
           - Summary of all compliance violations found
           - Risk assessment and trend analysis
           - Regulatory findings and cross-references
           - Recommendations for compliance improvements
           - Action items for follow-up
        
        8. **Output**: Save your compliance audit report to "compliance_audit_report.json" and 
           generate a human-readable summary in "compliance_summary.md".
        
        9. **Risk Escalation**: For high-risk findings, clearly mark them for immediate attention 
           and provide specific action steps for resolution.
        
        Always maintain audit trails and ensure your findings are actionable and compliance-focused.
    """,
    knowledge=knowledge_base,
    markdown=True,
    stream=True,
)
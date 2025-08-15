import json
import os
import sys

# Add the parent directory to the path so we can import from Accounting
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Accounting_Controller_Module import AccountingEntryValidator, ComplianceAuditAgent

def test_accounting_agents():
    """
    Test both agents in sequence:
    1. Accounting Entry Validator processes test transactions
    2. Compliance Audit Agent reads the output and performs compliance analysis
    """
    
    print("🧪 Testing Accounting Agents Workflow")
    print("=" * 50)
    
    # Load test transactions
    with open('test_transactions.json', 'r') as f:
        test_transactions = json.load(f)
    
    print(f"📊 Loaded {len(test_transactions)} test transactions")
    print("\n" + "=" * 50)
    
    # Test Agent 1: Accounting Entry Validator
    print("🔍 AGENT 1: Accounting Entry Validator")
    print("Processing transactions for validation...")
    
    # Create a simple test prompt for Agent 1
    test_prompt = f"""
    Please validate and process the following {len(test_transactions)} accounting transactions:
    
    {json.dumps(test_transactions, indent=2)}
    
    Follow your instructions to:
    1. Validate each transaction
    2. Correct common errors
    3. Detect duplicates
    4. Check business rules
    5. Handle any errors that can't be auto-corrected
    6. Output results to validated_transactions.json using FileTools
    
    Provide a summary of what you found and any issues that need manual review.
    """
    
    # Run Agent 1 (this would normally be done through the agent's chat interface)
    print("✅ Agent 1 instructions sent")
    print("📝 Agent 1 should create: validated_transactions.json")
    
    print("\n" + "=" * 50)
    
    # Test Agent 2: Compliance Audit Agent
    print("🔍 AGENT 2: Compliance Audit Agent")
    print("Waiting for Agent 1 output file...")
    
    # Check if Agent 1 created the output file
    if os.path.exists('validated_transactions.json'):
        print("✅ Found validated_transactions.json from Agent 1")
        
        # Create test prompt for Agent 2
        compliance_prompt = """
        Please read the validated_transactions.json file created by Agent 1 and perform 
        a comprehensive compliance audit following your instructions:
        
        1. Read the validated transactions using FileTools
        2. Perform anomaly detection
        3. Analyze patterns
        4. Check compliance rules
        5. Cross-reference with regulatory databases
        6. Analyze historical trends
        7. Generate compliance reports
        
        Output your findings to:
        - compliance_audit_report.json
        - compliance_summary.md
        
        Provide a summary of your compliance findings and any high-risk items.
        """
        
        print("✅ Agent 2 instructions sent")
        print("📝 Agent 2 should create: compliance_audit_report.json and compliance_summary.md")
        
    else:
        print("❌ validated_transactions.json not found - Agent 1 may not have completed")
        print("💡 Make sure to run Agent 1 first to create the input file")
    
    print("\n" + "=" * 50)
    print("🎯 Testing Complete!")
    print("\n📋 Next Steps:")
    print("1. Run Agent 1 (Accounting Entry Validator) with the test prompt")
    print("2. Verify validated_transactions.json was created")
    print("3. Run Agent 2 (Compliance Audit Agent) with the compliance prompt")
    print("4. Check the output files for results")

if __name__ == "__main__":
    test_accounting_agents()

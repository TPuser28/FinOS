import os
import json
import sys

# Add the parent directory to the path so we can import from Accounting
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_agent2():
    """
    Test Agent 2: Compliance Audit Agent
    """
    print("🔍 Testing Agent 2: Compliance Audit Agent")
    print("=" * 50)
    
    # Check if Agent 1 output exists
    if not os.path.exists('validated_transactions.json'):
        print("❌ validated_transactions.json not found!")
        print("💡 Please run Agent 1 first to create this file")
        return
    
    print("✅ Found validated_transactions.json from Agent 1")
    
    # Show what Agent 1 created
    try:
        with open('validated_transactions.json', 'r') as f:
            validated_data = json.load(f)
        print(f"📊 Agent 1 processed {len(validated_data.get('transactions', []))} transactions")
    except:
        print("⚠️  Could not read validated_transactions.json")
    
    print("\n🎯 Agent 2 should:")
    print("1. Read validated_transactions.json using FileTools")
    print("2. Perform anomaly detection")
    print("3. Analyze transaction patterns")
    print("4. Check compliance rules")
    print("5. Cross-reference with regulatory databases")
    print("6. Analyze historical trends")
    print("7. Generate compliance reports")
    
    print("\n💬 Copy this prompt to test Agent 2:")
    print("-" * 50)
    print("""
Please read the validated_transactions.json file created by Agent 1 and perform 
a comprehensive compliance audit following your instructions:

1. Read the validated transactions using FileTools
2. Perform anomaly detection on transaction amounts
3. Analyze patterns for recurring transactions
4. Check compliance against established rules
5. Cross-reference with regulatory databases
6. Analyze historical compliance trends
7. Generate comprehensive compliance reports

Output your findings to:
- compliance_audit_report.json (detailed report)
- compliance_summary.md (human-readable summary)

Focus on identifying any high-risk transactions, compliance violations, and suspicious patterns.
    """)
    print("-" * 50)
    
    print("\n📝 Expected outputs:")
    print("- compliance_audit_report.json")
    print("- compliance_summary.md")

if __name__ == "__main__":
    test_agent2()

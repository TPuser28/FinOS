import json
import sys
import os

# Add the parent directory to the path so we can import from Accounting
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Accounting_Controller_Module import AccountingEntryValidator

def test_agent1():
    """
    Test Agent 1: Accounting Entry Validator
    """
    print("🔍 Testing Agent 1: Accounting Entry Validator")
    print("=" * 50)
    
    # Load test transactions
    with open('test_transactions.json', 'r') as f:
        test_transactions = json.load(f)
    
    print(f"📊 Loaded {len(test_transactions)} test transactions")
    print("\n📋 Test transactions include:")
    print("- Valid transactions")
    print("- Duplicate transactions")
    print("- Invalid data (wrong date format, non-numeric amounts)")
    print("- Business rule violations (prohibited account codes, excessive amounts)")
    print("- Formatting issues (extra whitespace)")
    
    print("\n🎯 Agent 1 should:")
    print("1. Validate all transactions")
    print("2. Correct formatting issues")
    print("3. Detect duplicates")
    print("4. Flag business rule violations")
    print("5. Create validated_transactions.json")
    
    print("\n💬 Copy this prompt to test Agent 1:")
    print("-" * 50)
    print(f"""
Please validate and process these {len(test_transactions)} accounting transactions:

{json.dumps(test_transactions, indent=2)}

Follow your instructions to validate, correct errors, detect duplicates, check business rules, 
and output results to validated_transactions.json using FileTools.
    """)
    print("-" * 50)

if __name__ == "__main__":
    test_agent1()

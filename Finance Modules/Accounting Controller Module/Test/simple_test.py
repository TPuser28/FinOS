import json
import os
import sys

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("🧪 Testing Basic Functionality")
    print("=" * 50)
    
    # Test 1: Check if test data exists
    try:
        with open('test_transactions.json', 'r') as f:
            test_data = json.load(f)
        print(f"✅ Test data loaded: {len(test_data)} transactions")
        
        # Show sample transaction
        if test_data:
            print(f"📊 Sample transaction: {test_data[0]}")
            
    except FileNotFoundError:
        print("❌ test_transactions.json not found")
        return
    except json.JSONDecodeError:
        print("❌ Invalid JSON in test_transactions.json")
        return
    
    # Test 2: Check if we can access the Accounting module
    try:
        # Add parent directory to path
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Try to import the module
        import Accounting_Controller_Module
        print("✅ Accounting_Controller_Module imported successfully")
        
        # Check what's available
        print(f"📋 Available classes/functions: {dir(Accounting_Controller_Module)}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 This might be due to missing dependencies (agno, etc.)")
    
    # Test 3: Check file structure
    print("\n📁 File structure check:")
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    print(f"Backend directory: {parent_dir}")
    
    if os.path.exists(os.path.join(parent_dir, 'Accounting')):
        print("✅ Accounting directory found")
    else:
        print("❌ Accounting directory not found")
    
    print("\n🎯 Basic tests completed!")

if __name__ == "__main__":
    test_basic_functionality()

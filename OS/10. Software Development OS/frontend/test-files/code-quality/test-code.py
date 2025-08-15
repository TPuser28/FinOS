#!/usr/bin/env python3
"""
Sample Python code for testing Code Quality module
This file contains various code quality issues to test the module's capabilities
"""

import os
import sys
from typing import List, Dict, Optional

# Missing type hints
def process_data(data):
    """Process data without proper type hints"""
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

# Unused import
import json  # This import is never used

# Long function that could be split
def very_long_function_that_does_too_many_things():
    """This function is too long and does too many things"""
    # Step 1: Read configuration
    config = {}
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Config file not found")
        return None
    
    # Step 2: Process data
    data = []
    for i in range(100):
        data.append(i * 2)
    
    # Step 3: Validate results
    for item in data:
        if item < 0:
            print(f"Invalid item: {item}")
    
    # Step 4: Save results
    with open('output.txt', 'w') as f:
        for item in data:
            f.write(f"{item}\n")
    
    return data

# Hardcoded values
MAX_RETRIES = 3  # Should be configurable
TIMEOUT = 30     # Should be configurable

# Inconsistent naming
def get_user_data():
    """Get user data with inconsistent naming"""
    user_info = {}
    userInfo = {}  # Inconsistent camelCase
    user_info = {} # Inconsistent snake_case
    
    return user_info

# Missing error handling
def risky_operation():
    """Operation without proper error handling"""
    result = 10 / 0  # This will crash
    return result

# TODO comment
# TODO: Implement proper error handling
# FIXME: This is broken
# HACK: Temporary workaround

if __name__ == "__main__":
    # Main execution without proper structure
    data = [1, 2, 3, 4, 5]
    result = process_data(data)
    print(result)

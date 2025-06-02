#!/usr/bin/env python3
"""
Quick script to find deprecated functions in GitHub Manager
"""

import os
import re
from pathlib import Path

def search_for_function(search_terms):
    """Search for specific function names"""
    
    project_root = Path(".")
    all_files = []
    
    # Get all Python files
    for ext in ['.py', '.txt', '.md']:
        all_files.extend(project_root.rglob(f"*{ext}"))
    
    # Exclude venv and cache
    all_files = [f for f in all_files if 'venv' not in str(f) and '__pycache__' not in str(f)]
    
    found_items = []
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for i, line in enumerate(content.split('\n'), 1):
                line_lower = line.lower()
                for term in search_terms:
                    if term.lower() in line_lower:
                        found_items.append({
                            'file': str(file_path),
                            'line': i,
                            'content': line.strip(),
                            'term': term
                        })
        except Exception as e:
            continue
    
    return found_items

# Search terms
search_terms = [
    'pharcefuntion',
    'pharce',
    'pharse', 
    'parsefunction',
    'deprecated',
    'old_parse',
    'legacy_parse'
]

print("🔍 Searching for deprecated functions...")
results = search_for_function(search_terms)

if results:
    print(f"\n✅ Found {len(results)} matches:")
    for result in results:
        print(f"\n📄 {result['file']}:{result['line']}")
        print(f"   {result['content']}")
        print(f"   (searching for: {result['term']})")
else:
    print("\n❌ No deprecated functions found!")
    print("\n💡 The function might be:")
    print("   1. Already removed")
    print("   2. In a different directory")
    print("   3. A typo in the name")
    print("   4. In external libraries")

print("\n🚀 To clean up your code anyway:")
print("   1. Remove unused imports")
print("   2. Update to modern Python patterns")
print("   3. Check requirements.txt for old packages")

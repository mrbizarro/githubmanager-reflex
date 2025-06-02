#!/usr/bin/env python3
"""
Test the new label system in GitHub Manager
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

from utils.parsing import extract_labels_from_content

def test_new_label_system():
    """Test the new colored label system"""
    
    print("🧪 Testing New Label System")
    print("=" * 40)
    
    # Test cases based on your current issues
    test_cases = [
        ("Fix database error masking in chat API", "Critical database error that needs immediate attention"),
        ("Refactor massive chat route handler", "Large route handler needs to be broken down for maintainability"),
        ("Document security practices", "Create documentation for security best practices"),
        ("Remove inline script injection", "Security vulnerability in frontend needs fixing"),
        ("Centralize scattered configuration", "Configuration files are spread across multiple locations"),
        ("Implement user authentication", "Add secure user login and registration system"),
        ("Review analytics data collection", "Check privacy compliance for user data collection"),
        ("Test API endpoints", "Add comprehensive testing for all API routes"),
        ("Improve user experience", "Update UI components for better usability"),
        ("Update workflow requirements", "Document new development workflow procedures")
    ]
    
    for title, description in test_cases:
        labels = extract_labels_from_content(description, title)
        
        print(f"\n📝 Issue: {title}")
        print(f"   Labels: {', '.join(labels)}")
        
        # Show priority
        priority_labels = [l for l in labels if 'priority-' in l]
        if priority_labels:
            priority = priority_labels[0]
            if '🚨' in priority:
                print(f"   Priority: CRITICAL 🚨")
            elif '⚡' in priority:
                print(f"   Priority: HIGH ⚡")
            elif '📋' in priority:
                print(f"   Priority: MEDIUM 📋")
            elif '📝' in priority:
                print(f"   Priority: LOW 📝")

if __name__ == "__main__":
    test_new_label_system()

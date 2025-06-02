#!/usr/bin/env python3
"""
Quick Label Color Fix for GitHub Manager
Adds missing colored labels to your repository
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_label_colors():
    """Fix all label colors in the repository"""
    
    # GitHub configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_OWNER = os.getenv("REPO_OWNER") 
    REPO_NAME = os.getenv("REPO_NAME")
    
    if not all([GITHUB_TOKEN, REPO_OWNER, REPO_NAME]):
        print("❌ Missing GitHub configuration in .env file")
        return False
    
    BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    HEADERS = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    def update_label(name, color, description=""):
        """Update or create a label with proper color"""
        color = color.replace("#", "")
        
        # Try to update existing label
        update_url = f"{BASE_URL}/labels/{name}"
        update_data = {
            "name": name,
            "color": color,
            "description": description
        }
        
        response = requests.patch(update_url, headers=HEADERS, json=update_data)
        
        if response.status_code == 200:
            print(f"✅ Updated: {name}")
            return True
        else:
            # Try to create new label
            create_url = f"{BASE_URL}/labels"
            response = requests.post(create_url, headers=HEADERS, json=update_data)
            
            if response.status_code == 201:
                print(f"✅ Created: {name}")
                return True
            else:
                print(f"⚠️  Skipped: {name}")
                return False
    
    print(f"🎨 Fixing label colors for {REPO_OWNER}/{REPO_NAME}...")
    
    # Essential colored labels based on your issues
    labels_to_fix = [
        # Priority labels
        ("🚨 priority-critical", "B60205", "Critical issues"),
        ("⚡ priority-high", "D93F0B", "High priority"),
        ("📋 priority-medium", "FBCA04", "Medium priority"),
        ("📝 priority-low", "0E8A16", "Low priority"),
        
        # Area labels (based on your existing issues)
        ("backend", "FF7F0E", "Backend/API related"),
        ("frontend", "1F77B4", "Frontend/UI related"), 
        ("database", "2CA02C", "Database related"),
        ("security", "D73A4A", "Security issues"),
        ("privacy", "6A1B9A", "Privacy related"),
        ("user-experience", "E91E63", "UX improvements"),
        ("documentation", "0075CA", "Documentation"),
        ("requirements", "795548", "Requirements"),
        ("workflow", "607D8B", "Workflow improvements"),
        
        # Type labels
        ("enhancement", "A2EEEF", "New features"),
        ("bug", "D73A4A", "Bug fixes"),
        ("maintenance", "7057FF", "Code maintenance"),
        
        # Status labels
        ("high-priority", "D93F0B", "High priority items"),
        ("good-first-issue", "7057FF", "Good for newcomers"),
        ("help-wanted", "008672", "Help wanted"),
        ("wontfix", "FFFFFF", "Will not fix")
    ]
    
    success_count = 0
    for name, color, desc in labels_to_fix:
        if update_label(name, color, desc):
            success_count += 1
    
    print(f"\n🎉 Updated {success_count}/{len(labels_to_fix)} labels!")
    print("💡 Refresh your GitHub issues page to see the colors")
    
    return success_count > 0

if __name__ == "__main__":
    fix_label_colors()

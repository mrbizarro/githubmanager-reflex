#!/usr/bin/env python3
"""
GitHub API Test Script
Test your GitHub configuration and API access
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_github_config():
    """Test GitHub API configuration and access"""
    
    print("🔍 Testing GitHub Configuration...")
    print("=" * 50)
    
    # Get environment variables
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("REPO_OWNER") 
    repo = os.getenv("REPO_NAME")
    
    print(f"📋 Configuration:")
    print(f"   Token: {token[:10]}..." if token else "   Token: ❌ Missing")
    print(f"   Owner: {owner}")
    print(f"   Repo:  {repo}")
    print()
    
    if not all([token, owner, repo]):
        print("❌ Missing required configuration!")
        return False
    
    # Test basic authentication
    print("🔐 Testing authentication...")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    try:
        # Test user access
        response = requests.get("https://api.github.com/user", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Authentication successful!")
            print(f"   Logged in as: {user_data.get('login', 'Unknown')}")
            print(f"   Name: {user_data.get('name', 'Not set')}")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Test repository access
    print(f"\n🏗️ Testing repository access: {owner}/{repo}")
    
    try:
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(repo_url, headers=headers)
        
        if response.status_code == 200:
            repo_data = response.json()
            print(f"✅ Repository access successful!")
            print(f"   Full name: {repo_data.get('full_name')}")
            print(f"   Private: {repo_data.get('private', False)}")
            print(f"   Has issues: {repo_data.get('has_issues', False)}")
            
            # Check permissions
            permissions = repo_data.get('permissions', {})
            print(f"   Permissions:")
            print(f"     - Read: {permissions.get('pull', False)}")
            print(f"     - Write: {permissions.get('push', False)}")
            print(f"     - Admin: {permissions.get('admin', False)}")
            
            if not permissions.get('push', False):
                print("⚠️ Warning: You may not have write access to this repository!")
                
        elif response.status_code == 404:
            print(f"❌ Repository not found!")
            print(f"   Make sure '{owner}/{repo}' exists and you have access")
            return False
        else:
            print(f"❌ Repository access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Repository access error: {e}")
        return False
    
    # Test creating a milestone (dry run)
    print(f"\n🎯 Testing milestone creation (dry run)...")
    
    try:
        milestone_url = f"https://api.github.com/repos/{owner}/{repo}/milestones"
        
        # First, check existing milestones
        response = requests.get(milestone_url, headers=headers)
        
        if response.status_code == 200:
            milestones = response.json()
            print(f"✅ Milestone API access successful!")
            print(f"   Existing milestones: {len(milestones)}")
        else:
            print(f"❌ Milestone API access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Milestone API error: {e}")
        return False
    
    print(f"\n🎉 All tests passed! Your GitHub configuration is working.")
    return True

if __name__ == "__main__":
    success = test_github_config()
    
    if not success:
        print(f"\n🔧 Possible fixes:")
        print(f"1. Check your GitHub token has 'repo' scope")
        print(f"2. Verify the repository name and owner are correct") 
        print(f"3. Make sure you have write access to the repository")
        print(f"4. Try regenerating your GitHub personal access token")

import os
import requests
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

# Load environment variables
load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("REPO_OWNER") 
REPO = os.getenv("REPO_NAME")

def create_milestone_simple(title: str, description: str = '') -> int:
    """
    Simple milestone creation following GitHub API docs exactly.
    
    Args:
        title: Milestone title
        description: Milestone description
        
    Returns:
        Milestone number
    """
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/milestones"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    data = {
        "title": title,
        "description": description
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        print(f"Milestone API Response Status: {response.status_code}")
        print(f"Response Content: {response.text[:500]}")
        
        if response.status_code == 201:  # Created
            result = response.json()
            return result.get("number", 0)
        else:
            raise Exception(f"Milestone creation failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Milestone creation error: {e}")
        raise

def create_issue_simple(title: str, body: str, milestone: Optional[int] = None, 
                       labels: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Simple issue creation following GitHub API docs exactly.
    
    Args:
        title: Issue title
        body: Issue body/description
        milestone: Milestone number (optional)
        labels: List of labels (optional)
        
    Returns:
        Issue data
    """
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"
    
    headers = {
        "Accept": "application/vnd.github+json", 
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    data = {
        "title": title,
        "body": body
    }
    
    # Add optional fields
    if milestone is not None:
        data["milestone"] = milestone
    if labels:
        data["labels"] = [label for label in labels if label.strip()]
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        print(f"Issue API Response Status: {response.status_code}")
        print(f"Response Content: {response.text[:500]}")
        
        if response.status_code == 201:  # Created
            return response.json()
        else:
            raise Exception(f"Issue creation failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Issue creation error: {e}")
        raise

def test_api_access():
    """Test basic GitHub API access"""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Repository API Status: {response.status_code}")
        
        if response.status_code == 200:
            repo_data = response.json()
            print(f"Repository: {repo_data.get('full_name')}")
            print(f"Has Issues: {repo_data.get('has_issues')}")
            return True
        else:
            print(f"Repository access failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"API test error: {e}")
        return False

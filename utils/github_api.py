"""
GitHub API integration utilities
"""

import os
import requests
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from config.settings import Config

class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    pass

class GitHubAPI:
    """GitHub API wrapper class"""
    
    def __init__(self):
        self.token = Config.get_github_token()
        self.owner = Config.get_repo_owner()
        self.repo = Config.get_repo_name()
        self.base_url = "https://api.github.com"
        
        if not all([self.token, self.owner, self.repo]):
            raise GitHubAPIError("GitHub configuration incomplete")
        
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Issues-Manager/6.0"
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def validate_connection(self) -> Tuple[bool, str]:
        """Validate GitHub API connection and permissions"""
        
        try:
            response = self.session.get(f"{self.base_url}/repos/{self.owner}/{self.repo}")
            
            if response.status_code == 200:
                return True, "Connection successful"
            elif response.status_code == 404:
                return False, "Repository not found or no access"
            elif response.status_code == 401:
                return False, "Invalid token or no authorization"
            else:
                return False, f"API error: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def create_milestone(self, title: str, description: str = "", due_date: str = None, state: str = "open") -> Dict[str, Any]:
        """Create a new milestone or return existing one if it already exists"""
        
        # First, check if milestone already exists
        try:
            existing_milestones = self.get_milestones(state="all")
            for milestone in existing_milestones:
                if milestone['title'].lower() == title.lower():
                    print(f"⚠️ Milestone '{title}' already exists (#{milestone['number']})")
                    return milestone
        except Exception as e:
            print(f"Warning: Could not check existing milestones: {e}")
        
        # Create new milestone
        data = {
            "title": title,
            "description": description,
            "state": state
        }
        
        if due_date:
            data["due_on"] = due_date
        
        try:
            response = self.session.post(
                f"{self.base_url}/repos/{self.owner}/{self.repo}/milestones",
                json=data
            )
            
            if response.status_code == 201:
                return response.json()
            elif response.status_code == 422:
                # Handle "already exists" error by finding the existing milestone
                try:
                    existing_milestones = self.get_milestones(state="all")
                    for milestone in existing_milestones:
                        if milestone['title'].lower() == title.lower():
                            print(f"✅ Found existing milestone '{title}' (#{milestone['number']})")
                            return milestone
                    
                    # If we can't find it, raise the original error
                    raise GitHubAPIError(f"Milestone '{title}' already exists but could not be found")
                    
                except Exception as find_error:
                    raise GitHubAPIError(f"Failed to create milestone: {response.status_code} - {response.text}")
            else:
                raise GitHubAPIError(f"Failed to create milestone: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error creating milestone: {str(e)}")
    
    def create_issue(self, title: str, body: str = "", milestone_number: int = None, 
                    labels: List[str] = None, assignees: List[str] = None) -> Dict[str, Any]:
        """Create a new issue with better error handling for milestones"""
        
        data = {
            "title": title,
            "body": body
        }
        
        if milestone_number:
            # Verify milestone exists before trying to assign it
            try:
                milestone_response = self.session.get(
                    f"{self.base_url}/repos/{self.owner}/{self.repo}/milestones/{milestone_number}"
                )
                if milestone_response.status_code != 200:
                    print(f"⚠️ Warning: Milestone #{milestone_number} not found, creating issue without milestone")
                    milestone_number = None
                else:
                    data["milestone"] = milestone_number
            except Exception as e:
                print(f"⚠️ Warning: Could not verify milestone #{milestone_number}: {e}")
                milestone_number = None
        
        if labels:
            # Filter out invalid labels (too long, invalid characters, etc.)
            valid_labels = []
            for label in labels:
                if len(label) <= 50 and label.strip():  # GitHub label limit is 50 chars
                    valid_labels.append(label.strip())
                else:
                    print(f"⚠️ Warning: Skipping invalid label '{label}' (too long or empty)")
            data["labels"] = valid_labels
        
        if assignees:
            data["assignees"] = assignees
        
        try:
            response = self.session.post(
                f"{self.base_url}/repos/{self.owner}/{self.repo}/issues",
                json=data
            )
            
            if response.status_code == 201:
                return response.json()
            elif response.status_code == 422:
                # Try to parse the error and provide helpful info
                try:
                    error_data = response.json()
                    if 'errors' in error_data:
                        error_details = ', '.join([f"{err.get('field', 'unknown')}: {err.get('code', 'unknown')}" for err in error_data['errors']])
                        raise GitHubAPIError(f"Validation failed for issue '{title}': {error_details}")
                    else:
                        raise GitHubAPIError(f"Failed to create issue '{title}': {response.text}")
                except json.JSONDecodeError:
                    raise GitHubAPIError(f"Failed to create issue '{title}': {response.status_code} - {response.text}")
            else:
                raise GitHubAPIError(f"Failed to create issue '{title}': {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error creating issue '{title}': {str(e)}")
    
    def get_issues(self, state: str = "all", sort: str = "created", 
                  direction: str = "desc", per_page: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get repository issues with pagination support"""
        
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": min(per_page, 100),  # GitHub max is 100
            "page": page
        }
        
        try:
            response = self.session.get(
                f"{self.base_url}/repos/{self.owner}/{self.repo}/issues",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise GitHubAPIError(f"Failed to get issues: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error getting issues: {str(e)}")
    
    def get_all_issues(self, state: str = "all", sort: str = "created", 
                      direction: str = "desc", progress_callback=None) -> List[Dict[str, Any]]:
        """Get ALL repository issues with automatic pagination"""
        
        all_issues = []
        page = 1
        per_page = 100  # GitHub's max per page
        
        while True:
            if progress_callback:
                progress_callback(f"Loading page {page}...")
            
            page_issues = self.get_issues(
                state=state,
                sort=sort,
                direction=direction,
                per_page=per_page,
                page=page
            )
            
            if not page_issues:  # No more issues
                break
            
            # Filter out pull requests (GitHub includes them in issues endpoint)
            issues_only = [issue for issue in page_issues if 'pull_request' not in issue]
            all_issues.extend(issues_only)
            
            # If we got fewer issues than per_page, we're done
            if len(page_issues) < per_page:
                break
                
            page += 1
        
        if progress_callback:
            progress_callback(f"Loaded {len(all_issues)} issues total")
        
        return all_issues
    
    def get_milestones(self, state: str = "open", sort: str = "created", 
                      direction: str = "desc") -> List[Dict[str, Any]]:
        """Get repository milestones"""
        
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": 100  # Ensure we get all milestones
        }
        
        try:
            response = self.session.get(
                f"{self.base_url}/repos/{self.owner}/{self.repo}/milestones",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise GitHubAPIError(f"Failed to get milestones: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error getting milestones: {str(e)}")
    
    def close_issue(self, issue_number: int) -> Dict[str, Any]:
        """Close an issue"""
        
        data = {
            "state": "closed",
            "state_reason": "completed"  # Mark as completed
        }
        
        try:
            response = self.session.patch(
                f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}",
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise GitHubAPIError(f"Issue #{issue_number} not found")
            else:
                raise GitHubAPIError(f"Failed to close issue #{issue_number}: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error closing issue #{issue_number}: {str(e)}")
    
    def delete_milestone(self, milestone_number: int) -> bool:
        """Delete a milestone"""
        
        try:
            response = self.session.delete(
                f"{self.base_url}/repos/{self.owner}/{self.repo}/milestones/{milestone_number}"
            )
            
            if response.status_code == 204:  # No Content - Success
                return True
            elif response.status_code == 404:
                raise GitHubAPIError(f"Milestone #{milestone_number} not found")
            else:
                raise GitHubAPIError(f"Failed to delete milestone: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error deleting milestone: {str(e)}")
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """Get repository labels"""
        
        try:
            response = self.session.get(f"{self.base_url}/repos/{self.owner}/{self.repo}/labels")
            
            if response.status_code == 200:
                return response.json()
            else:
                raise GitHubAPIError(f"Failed to get labels: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error getting labels: {str(e)}")
    
    def create_label(self, name: str, color: str, description: str = "") -> Dict[str, Any]:
        """Create a new label"""
        
        data = {
            "name": name,
            "color": color.lstrip('#'),  # Remove # if present
            "description": description
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/repos/{self.owner}/{self.repo}/labels",
                json=data
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                raise GitHubAPIError(f"Failed to create label: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error creating label: {str(e)}")
    
    def delete_label(self, name: str) -> bool:
        """Delete a label"""
        
        try:
            response = self.session.delete(f"{self.base_url}/repos/{self.owner}/{self.repo}/labels/{name}")
            
            if response.status_code == 204:
                return True
            else:
                raise GitHubAPIError(f"Failed to delete label: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error deleting label: {str(e)}")
    
    def setup_standard_labels(self, progress_callback=None) -> Dict[str, Any]:
        """Set up the standard organized project labels"""
        
        # Define our standard labels with emojis, colors, and descriptions
        standard_labels = [
            {
                'name': '🧪 testing-qa',
                'color': '7B68EE',  # Medium slate blue
                'description': 'Testing & Quality Assurance tasks'
            },
            {
                'name': '🗄️ database-migration',
                'color': '2E8B57',  # Sea green
                'description': 'Database & Migration Strategy'
            },
            {
                'name': '⚡ code-quality',
                'color': 'FFD700',  # Gold
                'description': 'Code Quality & Optimization'
            },
            {
                'name': '🔍 feature-analysis',
                'color': '4169E1',  # Royal blue
                'description': 'Core Feature Analysis'
            },
            {
                'name': '🛠️ tech-stack',
                'color': '808080',  # Gray
                'description': 'Technology Stack Assessment'
            },
            {
                'name': '📚 documentation',
                'color': '32CD32',  # Lime green
                'description': 'Documentation & Guides'
            },
            {
                'name': '🐛 bug',
                'color': 'DC143C',  # Crimson
                'description': 'Bug fixes and issues'
            },
            {
                'name': '✨ enhancement',
                'color': '9370DB',  # Medium purple
                'description': 'New features and improvements'
            },
            {
                'name': '🚀 deployment',
                'color': 'FF6347',  # Tomato
                'description': 'Deployment and DevOps'
            },
            {
                'name': '🔒 security',
                'color': '8B0000',  # Dark red
                'description': 'Security-related tasks'
            },
            {
                'name': 'high-priority',
                'color': 'FF0000',  # Red
                'description': 'High priority tasks'
            },
            {
                'name': 'medium-priority',
                'color': 'FFA500',  # Orange
                'description': 'Medium priority tasks'
            },
            {
                'name': 'low-priority',
                'color': '90EE90',  # Light green
                'description': 'Low priority tasks'
            }
        ]
        
        results = {
            'created': 0,
            'skipped': 0,
            'errors': []
        }
        
        # Get existing labels
        try:
            existing_labels = self.get_labels()
            existing_names = {label['name'] for label in existing_labels}
        except GitHubAPIError as e:
            results['errors'].append(f"Failed to get existing labels: {str(e)}")
            return results
        
        # Create each standard label if it doesn't exist
        for i, label_config in enumerate(standard_labels, 1):
            if progress_callback:
                progress_callback(f"Setting up label {i}/{len(standard_labels)}: {label_config['name']}")
            
            label_name = label_config['name']
            
            if label_name in existing_names:
                results['skipped'] += 1
                continue
            
            try:
                self.create_label(
                    name=label_name,
                    color=label_config['color'],
                    description=label_config['description']
                )
                results['created'] += 1
                time.sleep(0.1)  # Rate limiting
                
            except GitHubAPIError as e:
                results['errors'].append(f"Failed to create label '{label_name}': {str(e)}")
        
        return results
    
    def search_issues(self, query: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """Search issues using GitHub search API"""
        
        # Add repository qualifier to query
        full_query = f"{query} repo:{self.owner}/{self.repo}"
        
        params = {
            "q": full_query,
            "sort": "updated",
            "order": "desc",
            "per_page": min(per_page, 100)  # GitHub search API max is 100
        }
        
        try:
            response = self.session.get(f"{self.base_url}/search/issues", params=params)
            
            if response.status_code == 200:
                return response.json().get("items", [])
            else:
                raise GitHubAPIError(f"Failed to search issues: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error searching issues: {str(e)}")
    
    def bulk_close_issues(self, issue_numbers: List[int], progress_callback=None) -> Tuple[int, int, List[str]]:
        """Close multiple issues in bulk"""
        
        successful = 0
        failed = 0
        errors = []
        total = len(issue_numbers)
        
        for i, issue_number in enumerate(issue_numbers, 1):
            if progress_callback:
                progress_callback(f"Closing issue #{issue_number} ({i}/{total})")
            
            try:
                self.close_issue(issue_number)
                successful += 1
                # Add small delay to avoid rate limiting
                time.sleep(0.1)
            except GitHubAPIError as e:
                failed += 1
                errors.append(f"Issue #{issue_number}: {str(e)}")
        
        return successful, failed, errors
    
    def deploy_project(self, project: Dict[str, Any], progress_callback=None) -> Dict[str, Any]:
        """Deploy entire project structure to GitHub"""
        
        results = {
            'milestones_created': 0,
            'issues_created': 0,
            'errors': [],
            'milestone_mapping': {}  # milestone_name -> milestone_number
        }
        
        total_milestones = len(project)
        total_issues = sum(len(m.get('issues', [])) for m in project.values())
        total_steps = total_milestones + total_issues
        current_step = 0
        
        try:
            # Create milestones first
            for milestone_name, milestone_data in project.items():
                current_step += 1
                
                if progress_callback:
                    progress_callback(
                        step=current_step,
                        total=total_steps,
                        action=f"Creating milestone: {milestone_name}"
                    )
                
                try:
                    milestone_response = self.create_milestone(
                        title=milestone_name,
                        description=milestone_data.get('description', '')
                    )
                    
                    milestone_number = milestone_response['number']
                    results['milestone_mapping'][milestone_name] = milestone_number
                    results['milestones_created'] += 1
                    
                    # Create issues for this milestone
                    for issue in milestone_data.get('issues', []):
                        current_step += 1
                        
                        if progress_callback:
                            progress_callback(
                                step=current_step,
                                total=total_steps,
                                action=f"Creating issue: {issue['title'][:40]}..."
                            )
                        
                        try:
                            self.create_issue(
                                title=issue['title'],
                                body=issue['body'],
                                milestone_number=milestone_number,
                                labels=issue.get('labels', []),
                                assignees=issue.get('assignees', [])
                            )
                            
                            results['issues_created'] += 1
                            
                        except GitHubAPIError as e:
                            results['errors'].append(f"Failed to create issue '{issue['title']}': {str(e)}")
                        
                        # Rate limiting
                        time.sleep(0.1)
                
                except GitHubAPIError as e:
                    results['errors'].append(f"Failed to create milestone '{milestone_name}': {str(e)}")
                
                # Rate limiting between milestones
                time.sleep(0.2)
        
        except Exception as e:
            results['errors'].append(f"Unexpected error during deployment: {str(e)}")
        
        return results

# Convenience functions for backward compatibility
def validate_github_config() -> Tuple[bool, str]:
    """Validate GitHub configuration"""
    try:
        api = GitHubAPI()
        return api.validate_connection()
    except GitHubAPIError as e:
        return False, str(e)

def create_milestone_simple(title: str, description: str = "") -> int:
    """Simple milestone creation"""
    try:
        api = GitHubAPI()
        response = api.create_milestone(title, description)
        return response['number']
    except GitHubAPIError as e:
        raise e

def create_issue_simple(title: str, body: str = "", milestone: int = None, labels: List[str] = None) -> Dict[str, Any]:
    """Simple issue creation"""
    try:
        api = GitHubAPI()
        return api.create_issue(title, body, milestone, labels)
    except GitHubAPIError as e:
        raise e

def setup_project_labels(progress_callback=None) -> Dict[str, Any]:
    """Set up standard labels for organized project management"""
    try:
        api = GitHubAPI()
        return api.setup_standard_labels(progress_callback)
    except GitHubAPIError as e:
        return {'created': 0, 'skipped': 0, 'errors': [str(e)]}

def get_repository_info() -> Dict[str, Any]:
    """Get basic repository information"""
    try:
        api = GitHubAPI()
        response = api.session.get(f"{api.base_url}/repos/{api.owner}/{api.repo}")
        
        if response.status_code == 200:
            repo_data = response.json()
            return {
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'description': repo_data['description'],
                'private': repo_data['private'],
                'open_issues_count': repo_data['open_issues_count'],
                'default_branch': repo_data['default_branch'],
                'created_at': repo_data['created_at'],
                'updated_at': repo_data['updated_at'],
                'url': repo_data['html_url']
            }
        else:
            raise GitHubAPIError(f"Failed to get repository info: {response.status_code}")
            
    except GitHubAPIError:
        raise
    except Exception as e:
        raise GitHubAPIError(f"Error getting repository info: {str(e)}")

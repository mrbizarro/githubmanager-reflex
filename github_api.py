import os
import requests
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, retry_if_not_exception_type
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get environment variables with validation
TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("REPO_OWNER")
REPO = os.getenv("REPO_NAME")
API_VERSION = "2022-11-28"  # Explicitly set API version for stability

class GitHubError(Exception):
    """Custom exception for GitHub API errors with additional context."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"{message} (Status: {status_code}): {response_text}")

class RateLimitError(GitHubError):
    """Specific exception for rate limit errors."""
    def __init__(self, message: str, reset_time: Optional[int] = None, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.reset_time = reset_time
        super().__init__(message, status_code, response_text)

class RepositoryError(GitHubError):
    """Specific exception for repository-related errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message, status_code, response_text)

class AuthenticationError(GitHubError):
    """Specific exception for authentication-related errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message, status_code, response_text)

class PermissionError(GitHubError):
    """Specific exception for permission-related errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message, status_code, response_text)

def validate_github_config() -> None:
    """
    Validate that all required GitHub configuration is present.
    
    Raises:
        GitHubError: If any required configuration is missing
    """
    missing = []
    if not TOKEN:
        missing.append("GITHUB_TOKEN")
    if not OWNER:
        missing.append("REPO_OWNER")
    if not REPO:
        missing.append("REPO_NAME")
        
    if missing:
        raise GitHubError(f"Missing required GitHub configuration: {', '.join(missing)}")

# Create a session with proper headers if token is available
session = requests.Session()
if TOKEN:
    session.headers.update({
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": "md-to-gh-issues"
    })

def handle_rate_limit(response: requests.Response) -> None:
    """
    Check for rate limit headers and raise appropriate exception if rate limited.
    
    Args:
        response: The HTTP response to check
        
    Raises:
        RateLimitError: If the request was rate limited
    """
    if response.status_code == 429:
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        limit = int(response.headers.get('X-RateLimit-Limit', 0))
        
        reset_datetime = datetime.fromtimestamp(reset_time).strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"Rate limit exceeded. {remaining}/{limit} requests remaining. Resets at {reset_datetime}"
        raise RateLimitError(message, reset_time, response.status_code, response.text)

def handle_error_response(response: requests.Response) -> None:
    """
    Handle error responses from the GitHub API and raise appropriate exceptions.
    
    Args:
        response: The HTTP response to check
        
    Raises:
        AuthenticationError: If authentication failed
        RepositoryError: If repository doesn't exist or is inaccessible
        PermissionError: If user doesn't have required permissions
        GitHubError: For other API errors
    """
    if response.status_code == 401:
        raise AuthenticationError(
            "Authentication failed. Please check your GitHub token.",
            status_code=response.status_code,
            response_text=response.text
        )
    elif response.status_code == 404:
        raise RepositoryError(
            f"Repository '{OWNER}/{REPO}' not found. Please check the repository owner and name.",
            status_code=response.status_code,
            response_text=response.text
        )
    elif response.status_code == 403:
        if "Resource not accessible by integration" in response.text:
            raise PermissionError(
                f"Your token doesn't have permission to access repository '{OWNER}/{REPO}'.",
                status_code=response.status_code,
                response_text=response.text
            )
        else:
            raise PermissionError(
                "Permission denied. Please check your token's scopes.",
                status_code=response.status_code,
                response_text=response.text
            )
    elif response.status_code == 422:
        raise GitHubError(
            "Validation failed. Please check your request parameters.",
            status_code=response.status_code,
            response_text=response.text
        )
    elif response.status_code >= 300:
        raise GitHubError(
            f"GitHub API request failed", 
            status_code=response.status_code, 
            response_text=response.text
        )

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(5),
    retry=retry_if_not_exception_type(RateLimitError) & 
          retry_if_not_exception_type(AuthenticationError) & 
          retry_if_not_exception_type(RepositoryError) & 
          retry_if_not_exception_type(PermissionError) & 
          retry_if_exception_type(GitHubError)
)
def _request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """
    Make a request to the GitHub API with retry logic.
    
    Args:
        method: HTTP method (GET, POST, PATCH, etc.)
        url: The GitHub API endpoint URL
        **kwargs: Additional arguments to pass to requests
        
    Returns:
        JSON response from the API
        
    Raises:
        GitHubError: If the request fails
        RateLimitError: If rate limits are exceeded
        AuthenticationError: If authentication failed
        RepositoryError: If repository doesn't exist or is inaccessible
        PermissionError: If user doesn't have required permissions
    """
    try:
        response = session.request(method, url, **kwargs)
        
        # Check for rate limiting
        handle_rate_limit(response)
        
        # Handle error responses
        if response.status_code >= 300:
            handle_error_response(response)
            
        return response.json() if response.content else {}
    except requests.RequestException as e:
        raise GitHubError(f"Request error: {str(e)}")

def _get(url: str, **kwargs) -> Dict[str, Any]:
    """Make a GET request to the GitHub API."""
    return _request("GET", url, **kwargs)

def _post(url: str, **kwargs) -> Dict[str, Any]:
    """Make a POST request to the GitHub API."""
    return _request("POST", url, **kwargs)

def _patch(url: str, **kwargs) -> Dict[str, Any]:
    """Make a PATCH request to the GitHub API."""
    return _request("PATCH", url, **kwargs)

def _delete(url: str, **kwargs) -> requests.Response:
    """Make a DELETE request to the GitHub API."""
    return session.request("DELETE", url, **kwargs)

def verify_repository_access() -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verify that the configured repository exists and is accessible.
    
    Returns:
        Tuple containing:
        - Boolean indicating if repository is accessible
        - Message describing the status
        - Repository data if accessible, empty dict otherwise
    """
    try:
        validate_github_config()
        
        url = f"https://api.github.com/repos/{OWNER}/{REPO}"
        repo_data = _get(url)
        
        # Check if issues are enabled
        if not repo_data.get("has_issues", False):
            return False, f"Issues are disabled for repository '{OWNER}/{REPO}'", repo_data
        
        # Check repository permissions
        permissions = repo_data.get("permissions", {})
        if not permissions.get("push", False):
            return False, f"You don't have write access to repository '{OWNER}/{REPO}'", repo_data
        
        return True, f"Successfully connected to repository '{OWNER}/{REPO}'", repo_data
    
    except AuthenticationError as e:
        return False, str(e), {}
    except RepositoryError as e:
        return False, str(e), {}
    except PermissionError as e:
        return False, str(e), {}
    except GitHubError as e:
        return False, str(e), {}

def get_repository_info() -> Dict[str, Any]:
    """
    Get detailed information about the configured repository.
    
    Returns:
        Dictionary containing repository information
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
    """
    validate_github_config()
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}"
    return _get(url)

def get_authenticated_user() -> Dict[str, Any]:
    """
    Get information about the authenticated user.
    
    Returns:
        Dictionary containing user information
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        AuthenticationError: If authentication failed
    """
    validate_github_config()
    
    url = "https://api.github.com/user"
    return _get(url)

def get_repository_collaborators() -> List[Dict[str, Any]]:
    """
    Get all collaborators for the configured repository.
    
    Returns:
        List of collaborator data
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
    """
    validate_github_config()
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/collaborators"
    return _get(url)

def verify_assignee_access(assignees: List[str]) -> Tuple[bool, List[str], List[str]]:
    """
    Verify that all assignees have access to the repository.
    
    Args:
        assignees: List of GitHub usernames to verify
        
    Returns:
        Tuple containing:
        - Boolean indicating if all assignees have access
        - List of valid assignees
        - List of invalid assignees
    """
    if not assignees:
        return True, [], []
    
    try:
        collaborators = get_repository_collaborators()
        collaborator_logins = [c.get("login", "").lower() for c in collaborators]
        
        valid_assignees = []
        invalid_assignees = []
        
        for assignee in assignees:
            if assignee.lower() in collaborator_logins:
                valid_assignees.append(assignee)
            else:
                invalid_assignees.append(assignee)
        
        return len(invalid_assignees) == 0, valid_assignees, invalid_assignees
    
    except (GitHubError, RepositoryError):
        # If we can't get collaborators, assume all assignees are invalid
        return False, [], assignees

def get_milestones(state: str = "open", sort: str = "due_on", direction: str = "asc") -> List[Dict[str, Any]]:
    """
    Get all milestones for the configured repository.
    
    Args:
        state: Filter milestones by state: 'open', 'closed', or 'all'
        sort: Sort milestones by: 'due_on', 'completeness'
        direction: Sort direction: 'asc' or 'desc'
        
    Returns:
        List of milestone data
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
    """
    validate_github_config()
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/milestones"
    params = {
        "state": state,
        "sort": sort,
        "direction": direction
    }
    
    return _get(url, params=params)

def find_milestone_by_title(title: str) -> Optional[Dict[str, Any]]:
    """
    Find a milestone by its title.
    
    Args:
        title: The milestone title to search for
        
    Returns:
        Milestone data if found, None otherwise
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
    """
    milestones = get_milestones(state="all")
    
    for milestone in milestones:
        if milestone.get("title") == title:
            return milestone
            
    return None

def create_milestone(
    title: str, 
    description: str = '', 
    state: str = 'open',
    due_on: Optional[str] = None,
    dry_run: bool = False
) -> int:
    """
    Create a milestone in the configured GitHub repository.
    
    Args:
        title: The milestone title
        description: Optional milestone description
        state: Milestone state ('open' or 'closed')
        due_on: Optional due date in ISO 8601 format (YYYY-MM-DD)
        dry_run: If True, simulate the API call without making it
        
    Returns:
        Milestone number (or 0 for dry runs)
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
        PermissionError: If user doesn't have required permissions
    """
    if dry_run:
        return 0
        
    validate_github_config()
    
    # Verify repository access
    access_ok, message, _ = verify_repository_access()
    if not access_ok:
        raise RepositoryError(message)
    
    # Check if milestone already exists
    existing = find_milestone_by_title(title)
    if existing:
        return existing["number"]
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/milestones"
    data = {
        "title": title,
        "description": description,
        "state": state
    }
    
    if due_on:
        # Ensure due_on is in ISO 8601 format with time component
        if "T" not in due_on:
            due_on = f"{due_on}T00:00:00Z"
        data["due_on"] = due_on
    
    response = _post(url, json=data)
    if "number" not in response:
        raise GitHubError("Unexpected response format from GitHub API", response_text=str(response))
        
    return response["number"]

def update_milestone(
    number: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    state: Optional[str] = None,
    due_on: Optional[str] = None,
    dry_run: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Update an existing milestone.
    
    Args:
        number: The milestone number to update
        title: Optional new title
        description: Optional new description
        state: Optional new state ('open' or 'closed')
        due_on: Optional new due date in ISO 8601 format (YYYY-MM-DD)
        dry_run: If True, simulate the API call without making it
        
    Returns:
        Updated milestone data, or None for dry runs
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
        PermissionError: If user doesn't have required permissions
    """
    if dry_run:
        return None
        
    validate_github_config()
    
    # Verify repository access
    access_ok, message, _ = verify_repository_access()
    if not access_ok:
        raise RepositoryError(message)
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/milestones/{number}"
    data = {}
    
    if title is not None:
        data["title"] = title
    if description is not None:
        data["description"] = description
    if state is not None:
        data["state"] = state
    if due_on is not None:
        # Ensure due_on is in ISO 8601 format with time component
        if due_on and "T" not in due_on:
            due_on = f"{due_on}T00:00:00Z"
        data["due_on"] = due_on
    
    if not data:
        return None  # Nothing to update
    
    return _patch(url, json=data)

def get_labels() -> List[Dict[str, Any]]:
    """
    Get all labels for the configured repository.
    
    Returns:
        List of label data
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
    """
    validate_github_config()
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/labels"
    return _get(url)

def create_label(
    name: str,
    color: str = "ededed",
    description: Optional[str] = None,
    dry_run: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Create a label in the configured GitHub repository.
    
    Args:
        name: The label name
        color: The label color (6 character hex code without #)
        description: Optional label description
        dry_run: If True, simulate the API call without making it
        
    Returns:
        Label data, or None for dry runs
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
        PermissionError: If user doesn't have required permissions
    """
    if dry_run:
        return None
        
    validate_github_config()
    
    # Verify repository access
    access_ok, message, _ = verify_repository_access()
    if not access_ok:
        raise RepositoryError(message)
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/labels"
    data = {
        "name": name,
        "color": color.lstrip('#')  # Remove # if present
    }
    
    if description:
        data["description"] = description
    
    return _post(url, json=data)

def ensure_labels_exist(labels: List[str], dry_run: bool = False) -> None:
    """
    Ensure all specified labels exist in the repository.
    
    Args:
        labels: List of label names to ensure exist
        dry_run: If True, simulate the API calls without making them
        
    Raises:
        GitHubError: If the API calls fail or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
        PermissionError: If user doesn't have required permissions
    """
    if not labels or dry_run:
        return
        
    existing_labels = get_labels()
    existing_names = [label["name"] for label in existing_labels]
    
    for label in labels:
        if label and label not in existing_names:
            create_label(label, dry_run=dry_run)

def create_issue(
    title: str, 
    body: str, 
    milestone: Optional[int] = None, 
    labels: Optional[List[str]] = None, 
    assignees: Optional[List[str]] = None, 
    dry_run: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Create an issue in the configured GitHub repository.
    
    Args:
        title: The issue title
        body: The issue body/description
        milestone: Optional milestone number to associate with this issue
        labels: Optional list of labels to apply to the issue
        assignees: Optional list of GitHub usernames to assign to the issue
        dry_run: If True, simulate the API call without making it
        
    Returns:
        Issue data from the API response, or None for dry runs
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
        PermissionError: If user doesn't have required permissions
    """
    if dry_run:
        return None
        
    validate_github_config()
    
    # Verify repository access
    access_ok, message, repo_data = verify_repository_access()
    if not access_ok:
        raise RepositoryError(message)
    
    # Verify assignees have access to the repository
    if assignees:
        all_valid, valid_assignees, invalid_assignees = verify_assignee_access(assignees)
        if not all_valid:
            invalid_list = ", ".join(invalid_assignees)
            raise GitHubError(f"The following assignees don't have access to the repository: {invalid_list}")
        assignees = valid_assignees
    
    # Ensure all labels exist before creating the issue
    if labels:
        ensure_labels_exist(labels, dry_run=dry_run)
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"
    payload = {
        "title": title,
        "body": body
    }
    
    if milestone is not None:
        payload["milestone"] = milestone
    if labels:
        payload["labels"] = [l for l in labels if l]
    if assignees:
        payload["assignees"] = [a for a in assignees if a]
    
    return _post(url, json=payload)

def update_issue(
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    state: Optional[str] = None,
    milestone: Optional[int] = None,
    labels: Optional[List[str]] = None,
    assignees: Optional[List[str]] = None,
    dry_run: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Update an existing issue in the configured GitHub repository.
    
    Args:
        issue_number: The issue number to update
        title: Optional new title
        body: Optional new body/description
        state: Optional new state ('open' or 'closed')
        milestone: Optional milestone number to associate with this issue
        labels: Optional list of labels to apply to the issue
        assignees: Optional list of GitHub usernames to assign to the issue
        dry_run: If True, simulate the API call without making it
        
    Returns:
        Updated issue data, or None for dry runs
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
        PermissionError: If user doesn't have required permissions
    """
    if dry_run:
        return None
        
    validate_github_config()
    
    # Verify repository access
    access_ok, message, _ = verify_repository_access()
    if not access_ok:
        raise RepositoryError(message)
    
    # Verify assignees have access to the repository
    if assignees:
        all_valid, valid_assignees, invalid_assignees = verify_assignee_access(assignees)
        if not all_valid:
            invalid_list = ", ".join(invalid_assignees)
            raise GitHubError(f"The following assignees don't have access to the repository: {invalid_list}")
        assignees = valid_assignees
    
    # Ensure all labels exist before updating the issue
    if labels:
        ensure_labels_exist(labels, dry_run=dry_run)
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{issue_number}"
    payload = {}
    
    if title is not None:
        payload["title"] = title
    if body is not None:
        payload["body"] = body
    if state is not None:
        payload["state"] = state
    if milestone is not None:
        payload["milestone"] = milestone
    if labels is not None:
        payload["labels"] = [l for l in labels if l]
    if assignees is not None:
        payload["assignees"] = [a for a in assignees if a]
    
    if not payload:
        return None  # Nothing to update
    
    return _patch(url, json=payload)

def get_issues(
    state: str = "open",
    sort: str = "created",
    direction: str = "desc",
    milestone: Optional[int] = None,
    labels: Optional[List[str]] = None,
    assignee: Optional[str] = None,
    per_page: int = 100
) -> List[Dict[str, Any]]:
    """
    Get issues for the configured repository.
    
    Args:
        state: Filter issues by state: 'open', 'closed', or 'all'
        sort: Sort issues by: 'created', 'updated', 'comments'
        direction: Sort direction: 'asc' or 'desc'
        milestone: Filter by milestone number or 'none' or '*'
        labels: Filter by label names (comma-separated)
        assignee: Filter by assignee username or 'none' or '*'
        per_page: Number of issues per page (max 100)
        
    Returns:
        List of issue data
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
    """
    validate_github_config()
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"
    params = {
        "state": state,
        "sort": sort,
        "direction": direction,
        "per_page": per_page
    }
    
    if milestone is not None:
        params["milestone"] = milestone
    if labels:
        params["labels"] = ",".join(labels)
    if assignee:
        params["assignee"] = assignee
    
    return _get(url, params=params)

def delete_issue(
    issue_number: int,
    dry_run: bool = False
) -> bool:
    """
    Delete an issue from the configured GitHub repository.
    Note: GitHub doesn't allow true deletion of issues, but this closes them permanently.
    
    Args:
        issue_number: The issue number to delete/close
        dry_run: If True, simulate the API call without making it
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
        PermissionError: If user doesn't have required permissions
    """
    if dry_run:
        return True
        
    validate_github_config()
    
    # Verify repository access
    access_ok, message, _ = verify_repository_access()
    if not access_ok:
        raise RepositoryError(message)
    
    # GitHub doesn't allow true deletion, so we close the issue
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{issue_number}"
    payload = {
        "state": "closed",
        "state_reason": "not_planned"  # Mark as closed/not planned
    }
    
    try:
        _patch(url, json=payload)
        return True
    except GitHubError:
        return False

def bulk_delete_issues(
    issue_numbers: List[int],
    dry_run: bool = False,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Delete multiple issues from the configured GitHub repository.
    
    Args:
        issue_numbers: List of issue numbers to delete/close
        dry_run: If True, simulate the API calls without making them
        progress_callback: Optional callback function for progress updates
        
    Returns:
        Dictionary with success/failure counts and details
        
    Raises:
        GitHubError: If the API calls fail or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
    """
    validate_github_config()
    
    results = {
        "total": len(issue_numbers),
        "successful": 0,
        "failed": 0,
        "failed_issues": [],
        "successful_issues": []
    }
    
    for i, issue_number in enumerate(issue_numbers):
        try:
            if progress_callback:
                progress_callback(i + 1, len(issue_numbers), issue_number)
            
            success = delete_issue(issue_number, dry_run=dry_run)
            
            if success:
                results["successful"] += 1
                results["successful_issues"].append(issue_number)
            else:
                results["failed"] += 1
                results["failed_issues"].append(issue_number)
                
        except Exception as e:
            results["failed"] += 1
            results["failed_issues"].append({
                "issue_number": issue_number,
                "error": str(e)
            })
    
    return results

def delete_milestone(
    milestone_number: int,
    dry_run: bool = False
) -> bool:
    """
    Delete a milestone from the configured GitHub repository.
    
    Args:
        milestone_number: The milestone number to delete
        dry_run: If True, simulate the API call without making it
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
        PermissionError: If user doesn't have required permissions
    """
    if dry_run:
        return True
        
    validate_github_config()
    
    # Verify repository access
    access_ok, message, _ = verify_repository_access()
    if not access_ok:
        raise RepositoryError(message)
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/milestones/{milestone_number}"
    
    try:
        response = _delete(url)
        handle_rate_limit(response)
        
        if response.status_code == 204:  # No Content = Success
            return True
        else:
            handle_error_response(response)
            return False
    except GitHubError:
        return False

def get_issue_details(issue_number: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific issue.
    
    Args:
        issue_number: The issue number to fetch
        
    Returns:
        Issue data if found, None otherwise
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
        RepositoryError: If repository doesn't exist or is inaccessible
    """
    validate_github_config()
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{issue_number}"
    
    try:
        return _get(url)
    except GitHubError as e:
        if "404" in str(e):
            return None
        raise

def search_issues(
    query: str,
    state: str = "all",
    sort: str = "updated",
    order: str = "desc"
) -> List[Dict[str, Any]]:
    """
    Search issues in the configured repository using GitHub search API.
    
    Args:
        query: Search query (e.g., "bug in:title", "label:enhancement")
        state: Filter by state: 'open', 'closed', or 'all'
        sort: Sort by: 'created', 'updated', 'comments'
        order: Sort order: 'asc' or 'desc'
        
    Returns:
        List of matching issue data
        
    Raises:
        GitHubError: If the API call fails or configuration is missing
    """
    validate_github_config()
    
    # Build search query with repository scope
    full_query = f"{query} repo:{OWNER}/{REPO} type:issue"
    if state != "all":
        full_query += f" state:{state}"
    
    url = "https://api.github.com/search/issues"
    params = {
        "q": full_query,
        "sort": sort,
        "order": order
    }
    
    response = _get(url, params=params)
    return response.get("items", [])

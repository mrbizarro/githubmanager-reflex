import re
from typing import List, Tuple, Dict, Any
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("REPO_OWNER") 
REPO = os.getenv("REPO_NAME")

class LabelManager:
    """
    Enhanced label management system for GitHub issues.
    Handles label generation, validation, creation, and deduplication.
    """
    
    def __init__(self):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self._existing_labels_cache = None
    
    def generate_project_tag(self, milestone_name: str) -> str:
        """
        Generate a clean, valid GitHub label from milestone name.
        
        Args:
            milestone_name: Original milestone name
            
        Returns:
            Clean label following GitHub requirements
        """
        # Convert to lowercase and normalize
        tag = milestone_name.lower().strip()
        
        # Replace spaces and special chars with hyphens
        tag = re.sub(r'[^\w\-]', '-', tag)
        
        # Remove multiple consecutive hyphens
        tag = re.sub(r'-+', '-', tag)
        
        # Remove leading/trailing hyphens
        tag = tag.strip('-')
        
        # Add project prefix for organization
        tag = f"project-{tag}"
        
        # Ensure it fits GitHub's 50-character limit
        if len(tag) > 50:
            # Try to intelligently truncate
            words = tag.split('-')
            tag = words[0]  # Start with 'project'
            for word in words[1:]:
                if len(tag + '-' + word) <= 50:
                    tag += '-' + word
                else:
                    break
        
        return tag
    
    def get_existing_labels(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all existing labels from the repository.
        Caches results to avoid repeated API calls.
        
        Returns:
            Dictionary of label names to label data
        """
        if self._existing_labels_cache is not None:
            return self._existing_labels_cache
            
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/labels"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                labels = response.json()
                self._existing_labels_cache = {
                    label['name'].lower(): label for label in labels
                }
                return self._existing_labels_cache
            else:
                print(f"Warning: Could not fetch existing labels: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Warning: Error fetching labels: {e}")
            return {}
    
    def create_project_label(self, label_name: str, milestone_name: str) -> bool:
        """
        Create a project label with appropriate color and description.
        
        Args:
            label_name: The label name to create
            milestone_name: Original milestone name for description
            
        Returns:
            True if created or already exists, False if failed
        """
        existing_labels = self.get_existing_labels()
        
        # Check if label already exists
        if label_name.lower() in existing_labels:
            print(f"ℹ️ Label '{label_name}' already exists")
            return True
        
        # Create the label
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/labels"
        data = {
            "name": label_name,
            "color": "0366d6",  # GitHub blue
            "description": f"Issues related to: {milestone_name}"
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code == 201:
                print(f"✅ Created project label: {label_name}")
                # Update cache
                if self._existing_labels_cache is not None:
                    self._existing_labels_cache[label_name.lower()] = data
                return True
            elif response.status_code == 422:
                print(f"ℹ️ Label '{label_name}' already exists")
                return True
            else:
                print(f"⚠️ Failed to create label '{label_name}': {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating label '{label_name}': {e}")
            return False
    
    def validate_and_clean_labels(self, user_labels: List[str], project_tag: str) -> List[str]:
        """
        Validate, clean, and deduplicate labels.
        
        Args:
            user_labels: Labels from user input
            project_tag: Generated project tag
            
        Returns:
            Clean, deduplicated list of valid labels
        """
        all_labels = []
        seen_labels = set()
        
        # Process user labels
        for label in user_labels:
            if not label or not label.strip():
                continue
                
            # Clean the label
            clean_label = label.strip()
            
            # Check length
            if len(clean_label) > 50:
                print(f"⚠️ Label too long, truncating: {clean_label[:50]}...")
                clean_label = clean_label[:50]
            
            # Avoid duplicates (case-insensitive)
            if clean_label.lower() not in seen_labels:
                all_labels.append(clean_label)
                seen_labels.add(clean_label.lower())
        
        # Add project tag if not already present
        if project_tag and project_tag.lower() not in seen_labels:
            all_labels.append(project_tag)
            seen_labels.add(project_tag.lower())
        
        return all_labels
    
    def analyze_existing_labels(self) -> Dict[str, Any]:
        """
        Analyze existing labels and categorize them.
        
        Returns:
            Analysis report with categorized labels
        """
        existing_labels = self.get_existing_labels()
        
        analysis = {
            'total_labels': len(existing_labels),
            'project_labels': [],
            'standard_labels': [],
            'duplicate_candidates': [],
            'long_labels': [],
            'suggested_deletions': []
        }
        
        # Common GitHub standard labels
        standard_names = {
            'bug', 'enhancement', 'documentation', 'good first issue', 
            'help wanted', 'invalid', 'question', 'wontfix', 'duplicate',
            'feature', 'hotfix', 'priority-high', 'priority-low', 'priority-medium'
        }
        
        seen_similar = {}
        
        for label_name, label_data in existing_labels.items():
            original_name = label_data['name']  # Keep original case
            
            # Categorize labels
            if label_name.startswith('project-'):
                analysis['project_labels'].append(original_name)
            elif label_name in standard_names:
                analysis['standard_labels'].append(original_name)
            else:
                # Check for potential issues
                if len(original_name) > 45:  # Close to limit
                    analysis['long_labels'].append(original_name)
                
                # Check for potential duplicates (similar names)
                normalized = re.sub(r'[^a-z0-9]', '', label_name)
                if normalized in seen_similar:
                    analysis['duplicate_candidates'].extend([
                        seen_similar[normalized], original_name
                    ])
                else:
                    seen_similar[normalized] = original_name
                
                # Check if it looks like an old auto-generated label
                if any(keyword in label_name for keyword in ['deployment', 'auto', 'generated', 'md-']):
                    analysis['suggested_deletions'].append(original_name)
        
        return analysis
    
    def bulk_delete_labels(self, label_names: List[str], dry_run: bool = True) -> Dict[str, Any]:
        """
        Delete multiple labels from the repository.
        
        Args:
            label_names: List of label names to delete
            dry_run: If True, only simulate the deletion
            
        Returns:
            Results of the deletion operation
        """
        results = {
            'attempted': len(label_names),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'deleted': []
        }
        
        for label_name in label_names:
            if dry_run:
                print(f"[DRY RUN] Would delete label: {label_name}")
                results['successful'] += 1
                results['deleted'].append(label_name)
                continue
            
            # URL encode the label name for safety
            from urllib.parse import quote
            encoded_name = quote(label_name)
            url = f"https://api.github.com/repos/{OWNER}/{REPO}/labels/{encoded_name}"
            
            try:
                response = requests.delete(url, headers=self.headers)
                if response.status_code == 204:  # Success - No Content
                    print(f"✅ Deleted label: {label_name}")
                    results['successful'] += 1
                    results['deleted'].append(label_name)
                    # Remove from cache
                    if self._existing_labels_cache and label_name.lower() in self._existing_labels_cache:
                        del self._existing_labels_cache[label_name.lower()]
                else:
                    error_msg = f"Failed to delete '{label_name}': {response.status_code}"
                    print(f"❌ {error_msg}")
                    results['failed'] += 1
                    results['errors'].append(error_msg)
            except Exception as e:
                error_msg = f"Error deleting '{label_name}': {str(e)}"
                print(f"❌ {error_msg}")
                results['failed'] += 1
                results['errors'].append(error_msg)
        
        return results
    
    def prepare_labels_for_issue(self, user_labels: List[str], milestone_name: str) -> Tuple[List[str], str]:
        """
        Complete label preparation for an issue.
        
        Args:
            user_labels: Labels from markdown/user input
            milestone_name: Name of the milestone
            
        Returns:
            Tuple of (final_labels_list, project_tag)
        """
        # Generate project tag
        project_tag = self.generate_project_tag(milestone_name)
        
        # Create the project label if needed
        self.create_project_label(project_tag, milestone_name)
        
        # Validate and clean all labels
        final_labels = self.validate_and_clean_labels(user_labels, project_tag)
        
        return final_labels, project_tag

# Global instance
label_manager = LabelManager()

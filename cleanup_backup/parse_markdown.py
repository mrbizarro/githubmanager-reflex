import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
try:
    from deepseek_api import ai_parse_markdown, DeepSeekError
except ImportError:
    # Handle case where deepseek_api is not available
    def ai_parse_markdown(text):
        raise Exception("DeepSeek API not available")
    
    class DeepSeekError(Exception):
        pass

ISSUE_RE = re.compile(r'^##\s+Issue:\s*(.+)$', re.I)
MILESTONE_RE = re.compile(r'^#\s+Milestone:\s*(.+)$', re.I)
LABELS_RE = re.compile(r'^labels:\s*(.+)$', re.I)
ASSIGNEES_RE = re.compile(r'^assignees:\s*(.+)$', re.I)
DESC_RE = re.compile(r'^description:\s*(.+)$', re.I)
STATE_RE = re.compile(r'^state:\s*(.+)$', re.I)
DUE_DATE_RE = re.compile(r'^due_date:\s*(.+)$', re.I)

def parse_markdown(md_text: str, use_ai: bool = True) -> Tuple[Optional[str], Dict[str, Dict[str, Any]]]:
    """
    Parse a markdown file containing milestones and issues into a structured dictionary.
    
    Args:
        md_text: String containing markdown content
        use_ai: If True, use AI parsing; if False, use traditional regex parsing
        
    Returns:
        Tuple of (reasoning, structured_data) where reasoning is None for regex parsing
    """
    if not md_text or not isinstance(md_text, str):
        return None, {}
    
    if use_ai:
        try:
            reasoning, structure = ai_parse_markdown(md_text)
            return reasoning, structure
        except DeepSeekError as e:
            # Fall back to regex parsing if AI fails
            print(f"AI parsing failed, falling back to regex: {str(e)}")
            return None, parse_markdown_regex(md_text)
    else:
        return None, parse_markdown_regex(md_text)

def parse_markdown_regex(md_text: str) -> Dict[str, Dict[str, Any]]:
    """
    Parse a markdown file using traditional regex patterns.
    Creates a single milestone with properly labeled issues for better organization.
    
    Expected markdown format:
    # Project: Project Title
    description: Project description
    
    ## Section: Section Name (becomes a label)
    
    ### Issue: Issue Title
    
    Issue body text here.
    
    labels: additional, labels
    assignees: user1, user2
    
    Args:
        md_text: String containing markdown content
        
    Returns:
        Dictionary with single milestone containing properly labeled issues
    """
    if not md_text or not isinstance(md_text, str):
        return {}
        
    lines = md_text.splitlines()
    
    # Extract project title from first heading or generate one
    project_title = "Project Overview"
    project_description = "Extracted from markdown content"
    current_section = None
    all_issues = []
    current_issue = None
    
    # Map section names to label names
    section_to_label = {
        'testing': 'testing-qa',
        'quality': 'testing-qa', 
        'database': 'database-migration',
        'migration': 'database-migration',
        'code': 'code-quality',
        'optimization': 'code-quality',
        'feature': 'feature-analysis',
        'analysis': 'feature-analysis',
        'tech': 'tech-stack',
        'technology': 'tech-stack',
        'stack': 'tech-stack',
        'documentation': 'documentation',
        'docs': 'documentation',
        'deployment': 'deployment',
        'deploy': 'deployment',
        'security': 'security',
        'bug': 'bug',
        'enhancement': 'enhancement',
        'improve': 'enhancement'
    }

    def flush_issue():
        """Helper function to add the current issue to the issues list."""
        nonlocal current_issue
        if current_issue:
            # Clean up the body text
            if current_issue['body']:
                current_issue['body'] = current_issue['body'].strip()
            
            # Add section label if we have a current section
            if current_section:
                section_label = None
                # Try to match section name to a standard label
                for keyword, label in section_to_label.items():
                    if keyword.lower() in current_section.lower():
                        section_label = label
                        break
                
                if not section_label:
                    # Create a custom label from section name
                    section_label = current_section.lower().replace(' ', '-')
                
                if section_label not in current_issue['labels']:
                    current_issue['labels'].insert(0, section_label)
            
            all_issues.append(current_issue)
        current_issue = None

    for line in lines + ['']:
        line = line.strip()
        
        # Check for project title (# Project: or just #)
        if line.startswith('# '):
            flush_issue()
            if line.startswith('# Project:'):
                project_title = line[10:].strip()
            elif line.startswith('# Milestone:'):
                project_title = line[12:].strip()
            else:
                # Just use the heading as project title
                project_title = line[1:].strip()
            continue
            
        # Check for section headers (## Section: or ##)
        if line.startswith('## '):
            flush_issue()
            if line.startswith('## Section:'):
                current_section = line[11:].strip()
            else:
                current_section = line[2:].strip()
            continue
            
        # Check for issue headers (### Issue: or ## Issue:)
        issue_match = re.match(r'^#{2,3}\s+Issue:\s*(.+)$', line, re.I)
        if issue_match:
            flush_issue()
            title = issue_match.group(1).strip()
            if title:
                # Add section prefix to issue title if we have a section
                if current_section:
                    title = f"[{current_section}] {title}"
                current_issue = {'title': title, 'body': '', 'labels': [], 'assignees': []}
            continue
            
        # Process content within issues
        if current_issue:
            if line.startswith('labels:'):
                labels = [l.strip() for l in line[7:].split(',')]
                current_issue['labels'].extend([l for l in labels if l])
            elif line.startswith('assignees:'):
                assignees = [a.strip() for a in line[10:].split(',')]
                current_issue['assignees'] = [a for a in assignees if a]
            elif line.startswith('description:'):
                project_description = line[12:].strip()
            else:
                if line and not line.startswith('---'):
                    if current_issue['body']:
                        current_issue['body'] += '\n'
                    current_issue['body'] += line
    
    flush_issue()
    
    # If no issues were found, try to create some from the content
    if not all_issues:
        # Split content into basic issues
        content_lines = [line for line in md_text.splitlines() if line.strip()]
        if content_lines:
            # Create a single issue from the content
            all_issues.append({
                'title': 'Process markdown content',
                'body': '\n'.join(content_lines),
                'labels': ['documentation'],
                'assignees': []
            })
    
    # Return single milestone structure
    return {
        project_title: {
            'description': project_description,
            'state': 'open',
            'due_date': None,
            'issues': all_issues
        }
    }

def validate_milestone_data(milestone_data: Dict[str, Any]) -> List[str]:
    """
    Validate milestone data for correctness.
    
    Args:
        milestone_data: Dictionary containing milestone data
        
    Returns:
        List of validation error messages, empty if valid
    """
    errors = []
    
    # Check required fields
    if 'issues' not in milestone_data:
        errors.append("Missing 'issues' field in milestone data")
    
    # Validate state if present
    if 'state' in milestone_data and milestone_data['state'] not in ['open', 'closed']:
        errors.append(f"Invalid state value: {milestone_data['state']}. Must be 'open' or 'closed'")
    
    # Validate due date if present
    if milestone_data.get('due_date'):
        try:
            datetime.strptime(milestone_data['due_date'], '%Y-%m-%d')
        except ValueError:
            errors.append(f"Invalid due date format: {milestone_data['due_date']}. Must be YYYY-MM-DD")
    
    # Validate issues if present
    if 'issues' in milestone_data:
        for i, issue in enumerate(milestone_data['issues']):
            if 'title' not in issue or not issue['title']:
                errors.append(f"Issue at index {i} is missing a title")
    
    return errors

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from deepseek_api import ai_parse_markdown, DeepSeekError

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
    
    Expected markdown format:
    # Milestone: Milestone Title
    description: Milestone description
    state: open|closed
    due_date: YYYY-MM-DD
    
    ## Issue: Issue Title
    
    Issue body text here.
    
    labels: label1, label2
    assignees: user1, user2
    
    Args:
        md_text: String containing markdown content
        
    Returns:
        Dictionary with milestone titles as keys and milestone data (description and issues) as values
    """
    if not md_text or not isinstance(md_text, str):
        return {}
        
    lines = md_text.splitlines()
    milestones = {}
    current_milestone = None
    current_issue = None

    def flush_issue():
        """Helper function to add the current issue to the current milestone."""
        nonlocal current_issue
        if current_issue and current_milestone:
            # Clean up the body text by removing extra newlines
            if current_issue['body']:
                current_issue['body'] = current_issue['body'].strip()
            milestones[current_milestone]['issues'].append(current_issue)
        current_issue = None

    for line in lines + ['']:
        m_mile = MILESTONE_RE.match(line)
        m_issue = ISSUE_RE.match(line)
        
        if m_mile:
            flush_issue()
            current_milestone = m_mile.group(1).strip()
            milestones[current_milestone] = {
                'description': '', 
                'issues': [],
                'state': 'open',  # Default state
                'due_date': None  # Default due date
            }
            continue
            
        if m_issue:
            flush_issue()
            title = m_issue.group(1).strip()
            if not title:
                # Skip issues with empty titles
                continue
            current_issue = {'title': title, 'body': '', 'labels': [], 'assignees': []}
            continue
            
        if current_issue:
            if LABELS_RE.match(line):
                labels = [l.strip() for l in LABELS_RE.match(line).group(1).split(',')]
                current_issue['labels'] = [l for l in labels if l]  # Filter out empty labels
            elif ASSIGNEES_RE.match(line):
                assignees = [a.strip() for a in ASSIGNEES_RE.match(line).group(1).split(',')]
                current_issue['assignees'] = [a for a in assignees if a]  # Filter out empty assignees
            else:
                if not line.strip().startswith('---'):
                    current_issue['body'] += line + '\n'
        elif current_milestone:
            if DESC_RE.match(line):
                milestones[current_milestone]['description'] = DESC_RE.match(line).group(1).strip()
            elif STATE_RE.match(line):
                state = STATE_RE.match(line).group(1).strip().lower()
                # Validate state value
                if state in ['open', 'closed']:
                    milestones[current_milestone]['state'] = state
            elif DUE_DATE_RE.match(line):
                due_date = DUE_DATE_RE.match(line).group(1).strip()
                # Validate date format (YYYY-MM-DD)
                try:
                    datetime.strptime(due_date, '%Y-%m-%d')
                    milestones[current_milestone]['due_date'] = due_date
                except ValueError:
                    # Invalid date format, ignore
                    pass

    flush_issue()
    return milestones

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

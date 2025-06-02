"""
Markdown parsing utilities for both AI and standard parsing
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

def parse_markdown_content(content: str, use_ai: bool = False, filename: str = "") -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Parse markdown content using either AI or standard regex parsing
    
    Returns:
        (reasoning: str, projects: Dict) - AI reasoning and parsed project structure
    """
    
    if use_ai:
        return parse_with_ai(content, filename)
    else:
        return parse_with_regex(content, filename)

def parse_with_ai(content: str, filename: str = "") -> Tuple[str, Dict[str, Any]]:
    """
    Parse markdown using AI (DeepSeek) - mock implementation for now
    
    In production, this would call the actual DeepSeek API
    """
    
    # Mock AI reasoning and parsing
    reasoning = f"""
    AI Analysis of {filename or 'markdown file'}:
    
    🔍 **Content Analysis:**
    - Identified natural language structure
    - Found project-oriented content with multiple phases
    - Detected actionable items and tasks
    - Recognized development workflow patterns
    
    🎯 **Milestone Extraction:**
    - Parsed high-level project phases
    - Grouped related functionality
    - Identified logical development milestones
    
    📋 **Issue Generation:**
    - Converted narrative descriptions to actionable tasks
    - Generated specific, implementable issues
    - Suggested appropriate labels based on content context
    - Inferred development priorities
    
    🏷️ **Label Suggestions:**
    - Technical labels: backend, frontend, api, database
    - Functional labels: authentication, ui, security
    - Priority labels: high-priority, enhancement
    - Project-specific labels based on content
    
    ✨ **AI Enhancements:**
    - Improved task descriptions for clarity
    - Added technical context where missing
    - Suggested implementation approaches
    - Identified potential dependencies between tasks
    """
    
    # Mock parsed project structure (this would come from AI analysis)
    projects = {
        f"AI-Enhanced Project from {filename}": {
            'description': 'Intelligently parsed and enhanced project structure from natural language markdown',
            'issues': [
                {
                    'title': 'Setup Development Environment',
                    'body': 'Initialize project structure, configure development tools, and set up CI/CD pipeline for efficient development workflow.',
                    'labels': ['setup', 'devops', 'infrastructure'],
                    'assignees': []
                },
                {
                    'title': 'Implement Core Authentication System',
                    'body': 'Develop secure user authentication with JWT tokens, password hashing, and session management. Include login, registration, and password reset functionality.',
                    'labels': ['authentication', 'security', 'backend', 'high-priority'],
                    'assignees': []
                },
                {
                    'title': 'Design Responsive User Interface',
                    'body': 'Create modern, accessible UI components using contemporary design patterns. Ensure mobile responsiveness and cross-browser compatibility.',
                    'labels': ['ui', 'frontend', 'design', 'responsive'],
                    'assignees': []
                },
                {
                    'title': 'Build RESTful API Endpoints',
                    'body': 'Develop comprehensive API with proper error handling, validation, and documentation. Include rate limiting and security measures.',
                    'labels': ['api', 'backend', 'documentation'],
                    'assignees': []
                }
            ]
        }
    }
    
    return reasoning, projects

def parse_with_regex(content: str, filename: str = "") -> Tuple[str, Dict[str, Any]]:
    """
    Parse markdown using traditional regex patterns
    
    Expected format:
    # Milestone: Name
    description: Description text
    
    ## Issue: Title
    Issue description
    labels: label1, label2
    assignees: user1, user2
    """
    
    reasoning = f"""
    Standard Parsing of {filename or 'markdown file'}:
    
    📝 **Parsing Method:** Regex pattern matching
    🔍 **Pattern Recognition:** Structured markdown format
    🎯 **Milestone Pattern:** # Milestone: [Name]
    📋 **Issue Pattern:** ## Issue: [Title]
    🏷️ **Metadata:** labels:, assignees:, description:
    
    ✅ **Successfully Extracted:**
    - Milestone titles and descriptions
    - Issue titles and descriptions  
    - Label assignments
    - User assignments
    - Hierarchical project structure
    """
    
    projects = {}
    
    # Split content into sections by milestone headers
    milestone_pattern = r'^#\s+Milestone:\s*(.+?)$'
    milestone_matches = list(re.finditer(milestone_pattern, content, re.MULTILINE | re.IGNORECASE))
    
    if not milestone_matches:
        # Fallback: treat main headers as milestones
        return parse_fallback_structure(content, filename)
    
    for i, milestone_match in enumerate(milestone_matches):
        milestone_name = milestone_match.group(1).strip()
        milestone_start = milestone_match.end()
        
        # Find the next milestone or end of content
        if i + 1 < len(milestone_matches):
            milestone_end = milestone_matches[i + 1].start()
        else:
            milestone_end = len(content)
        
        milestone_content = content[milestone_start:milestone_end].strip()
        
        # Parse milestone
        milestone_data = parse_milestone_section(milestone_content)
        projects[milestone_name] = milestone_data
    
    return reasoning, projects

def generate_smart_milestone_name(content: str, filename: str = "") -> str:
    """
    Generate smart milestone name based on content analysis (4 words max)
    """
    content_lower = content.lower()
    
    # Priority-based naming (most specific first)
    if any(word in content_lower for word in ['critical', 'urgent', 'emergency', 'breaking']):
        if any(word in content_lower for word in ['security', 'vulnerability', 'exploit']):
            return "🔒 Critical Security"
        elif any(word in content_lower for word in ['bug', 'error', 'fix', 'crash']):
            return "🚨 Critical Fixes"
        else:
            return "🚨 Critical Issues"
    
    # Architecture/structure focused
    if any(word in content_lower for word in ['architecture', 'refactor', 'restructure', 'cleanup']):
        if any(word in content_lower for word in ['database', 'db', 'migration']):
            return "🏗️ Database Refactoring"
        elif any(word in content_lower for word in ['api', 'endpoint', 'service']):
            return "🏗️ API Refactoring"
        else:
            return "🏗️ Architecture Cleanup"
    
    # Technical debt
    if any(word in content_lower for word in ['debt', 'legacy', 'deprecated', 'old']):
        return "🔧 Technical Debt"
    
    # Performance focused
    if any(word in content_lower for word in ['performance', 'optimization', 'speed', 'slow']):
        return "⚡ Performance Optimization"
    
    # API focused
    if any(word in content_lower for word in ['api', 'endpoint', 'rest', 'graphql']):
        if any(word in content_lower for word in ['new', 'add', 'implement']):
            return "⚡ API Development"
        else:
            return "⚡ API Updates"
    
    # Database focused
    if any(word in content_lower for word in ['database', 'db', 'migration', 'schema']):
        return "🗄️ Database Migration"
    
    # Security focused
    if any(word in content_lower for word in ['security', 'auth', 'login', 'permission']):
        return "🔒 Security Updates"
    
    # UI/Frontend focused
    if any(word in content_lower for word in ['ui', 'frontend', 'interface', 'design']):
        return "🎨 UI Development"
    
    # Feature development
    if any(word in content_lower for word in ['feature', 'functionality', 'implement', 'add']):
        return "📋 Feature Development"
    
    # Testing focused
    if any(word in content_lower for word in ['test', 'testing', 'spec', 'coverage']):
        return "🧪 Testing Sprint"
    
    # Documentation focused
    if any(word in content_lower for word in ['documentation', 'docs', 'readme', 'guide']):
        return "📚 Documentation Update"
    
    # Deployment focused
    if any(word in content_lower for word in ['deploy', 'deployment', 'release', 'production']):
        return "🚀 Deployment Sprint"
    
    # Fallback based on filename or generic
    if filename:
        clean_name = filename.replace('.md', '').replace('.txt', '').replace('_', ' ').title()
        if len(clean_name.split()) <= 2:
            return f"📋 {clean_name} Sprint"
    
    # Final fallback
    return "📋 Development Sprint"

def parse_fallback_structure(content: str, filename: str = "") -> Tuple[str, Dict[str, Any]]:
    """
    Fallback parsing for unstructured markdown
    """
    
    reasoning = f"""
    Fallback Parsing of {filename or 'markdown file'}:
    
    ⚠️ **Standard Format Not Detected**
    🔄 **Using Fallback Strategy:**
    - Converting main headers (# ##) to milestones
    - Converting sub-headers (### ####) to issues
    - Extracting content from surrounding text
    - Applying default labels and structure
    
    📋 **Auto-Generated Structure:**
    - Created logical milestone groupings
    - Generated actionable issue titles
    - Applied contextual labels
    - Maintained content hierarchy
    """
    
    projects = {}
    
    # Find all headers and their content
    header_pattern = r'^(#{1,4})\s+(.+?)$'
    headers = list(re.finditer(header_pattern, content, re.MULTILINE))
    
    current_milestone = None
    current_milestone_data = None
    
    for i, header_match in enumerate(headers):
        level = len(header_match.group(1))
        title = header_match.group(2).strip()
        
        # Get content until next header
        start_pos = header_match.end()
        if i + 1 < len(headers):
            end_pos = headers[i + 1].start()
        else:
            end_pos = len(content)
        
        section_content = content[start_pos:end_pos].strip()
        
        if level <= 2:  # Main milestone
            # Save previous milestone
            if current_milestone and current_milestone_data:
                projects[current_milestone] = current_milestone_data
            
            # Generate smart milestone name based on content
            current_milestone = generate_smart_milestone_name(content, filename)
            current_milestone_data = {
                'description': extract_description(section_content),
                'issues': []
            }
        
        elif level >= 3 and current_milestone_data:  # Issue
            issue = {
                'title': title,
                'body': extract_description(section_content),
                'labels': extract_labels_from_content(section_content, title),
                'assignees': []
            }
            current_milestone_data['issues'].append(issue)
    
    # Save final milestone
    if current_milestone and current_milestone_data:
        projects[current_milestone] = current_milestone_data
    
    # If no structure found, create a default milestone
    if not projects:
        smart_name = generate_smart_milestone_name(content, filename)
        projects[smart_name] = {
            'description': 'Auto-generated project structure from markdown analysis',
            'issues': [
                {
                    'title': '📋 Review and organize project structure',
                    'body': 'The uploaded markdown did not follow standard format. Please review and organize the content into proper issues.',
                    'labels': ['📋 priority-medium', 'documentation', 'backend'],
                    'assignees': []
                }
            ]
        }
    
    return reasoning, projects

def parse_milestone_section(content: str) -> Dict[str, Any]:
    """Parse a milestone section to extract description and issues"""
    
    milestone_data = {
        'description': '',
        'issues': []
    }
    
    # Extract description (first line or description: field)
    desc_match = re.search(r'^description:\s*(.+?)$', content, re.MULTILINE | re.IGNORECASE)
    if desc_match:
        milestone_data['description'] = desc_match.group(1).strip()
    else:
        # Use first paragraph as description
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                milestone_data['description'] = line
                break
    
    # Find all issues in this milestone
    issue_pattern = r'^##\s+Issue:\s*(.+?)$'
    issue_matches = list(re.finditer(issue_pattern, content, re.MULTILINE | re.IGNORECASE))
    
    for i, issue_match in enumerate(issue_matches):
        issue_title = issue_match.group(1).strip()
        issue_start = issue_match.end()
        
        # Find next issue or end of content
        if i + 1 < len(issue_matches):
            issue_end = issue_matches[i + 1].start()
        else:
            issue_end = len(content)
        
        issue_content = content[issue_start:issue_end].strip()
        
        # Parse issue details
        issue_data = parse_issue_section(issue_title, issue_content)
        milestone_data['issues'].append(issue_data)
    
    return milestone_data

def parse_issue_section(title: str, content: str) -> Dict[str, Any]:
    """Parse an issue section to extract details"""
    
    issue_data = {
        'title': title,
        'body': '',
        'labels': [],
        'assignees': []
    }
    
    # Extract labels
    labels_match = re.search(r'^labels:\s*(.+?)$', content, re.MULTILINE | re.IGNORECASE)
    if labels_match:
        labels_str = labels_match.group(1).strip()
        issue_data['labels'] = [label.strip() for label in labels_str.split(',') if label.strip()]
    
    # Extract assignees
    assignees_match = re.search(r'^assignees:\s*(.+?)$', content, re.MULTILINE | re.IGNORECASE)
    if assignees_match:
        assignees_str = assignees_match.group(1).strip()
        issue_data['assignees'] = [assignee.strip() for assignee in assignees_str.split(',') if assignee.strip()]
    
    # Extract body (everything that's not metadata)
    body_lines = []
    for line in content.split('\n'):
        line = line.strip()
        if line and not re.match(r'^(labels|assignees):', line, re.IGNORECASE):
            body_lines.append(line)
    
    issue_data['body'] = '\n'.join(body_lines).strip()
    
    # If no body, use title as body
    if not issue_data['body']:
        issue_data['body'] = f"Implementation task: {title}"
    
    return issue_data

def extract_description(content: str) -> str:
    """Extract description from content section"""
    
    # Remove empty lines and get first meaningful paragraph
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    description_lines = []
    for line in lines:
        # Skip metadata lines
        if re.match(r'^(labels|assignees|description):', line, re.IGNORECASE):
            continue
        # Skip list items for description
        if re.match(r'^[-*+]\s+', line):
            break
        # Skip code blocks
        if line.startswith('```'):
            break
        
        description_lines.append(line)
        
        # Stop at first paragraph break
        if len(description_lines) > 0 and not line:
            break
    
    description = ' '.join(description_lines).strip()
    
    # Limit description length
    if len(description) > 200:
        description = description[:200] + "..."
    
    return description or "No description provided"

def extract_labels_from_content(content: str, title: str) -> List[str]:
    """Extract contextual labels from content and title with new priority system"""
    
    labels = []
    content_lower = (content + " " + title).lower()
    
    # Priority labels (most important first)
    if any(word in content_lower for word in ['critical', 'urgent', 'emergency', 'breaking', 'security', 'vulnerability']):
        labels.append('🚨 priority-critical')
    elif any(word in content_lower for word in ['important', 'major', 'significant', 'blocking']):
        labels.append('⚡ priority-high')
    elif any(word in content_lower for word in ['minor', 'small', 'documentation', 'readme']):
        labels.append('📝 priority-low')
    else:
        labels.append('📋 priority-medium')
    
    # Technical area labels
    if any(word in content_lower for word in ['api', 'endpoint', 'rest', 'graphql']):
        labels.append('backend')
    
    if any(word in content_lower for word in ['database', 'db', 'sql', 'query']):
        labels.append('database')
    
    if any(word in content_lower for word in ['frontend', 'ui', 'interface', 'component']):
        labels.append('frontend')
    
    if any(word in content_lower for word in ['backend', 'server', 'service']) and 'backend' not in labels:
        labels.append('backend')
    
    if any(word in content_lower for word in ['auth', 'login', 'authentication', 'security']):
        labels.append('security')
    
    if any(word in content_lower for word in ['test', 'testing', 'spec', 'unit']):
        labels.append('testing')
    
    if any(word in content_lower for word in ['doc', 'documentation', 'readme']):
        labels.append('documentation')
    
    if any(word in content_lower for word in ['privacy', 'data', 'user data']):
        labels.append('privacy')
    
    if any(word in content_lower for word in ['user', 'experience', 'ux', 'usability']):
        labels.append('user-experience')
    
    if any(word in content_lower for word in ['requirement', 'requirements', 'spec', 'specification']):
        labels.append('requirements')
    
    if any(word in content_lower for word in ['workflow', 'process', 'procedure']):
        labels.append('workflow')
    
    # Type labels
    if any(word in content_lower for word in ['bug', 'fix', 'error', 'issue']):
        labels.append('bug')
    
    if any(word in content_lower for word in ['feature', 'add', 'implement', 'new']):
        labels.append('enhancement')
    
    if any(word in content_lower for word in ['setup', 'install', 'configure', 'init']):
        labels.append('setup')
    
    # Ensure we have at least one area label
    area_labels = ['backend', 'frontend', 'database', 'security', 'privacy', 'user-experience', 'requirements', 'workflow', 'testing', 'documentation']
    if not any(label in labels for label in area_labels):
        labels.append('backend')  # Default area
    
    # Ensure we have enhancement if no type specified
    type_labels = ['bug', 'enhancement', 'setup']
    if not any(label in labels for label in type_labels):
        labels.append('enhancement')
    
    return labels

def validate_parsed_project(project: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate parsed project structure"""
    
    errors = []
    
    if not isinstance(project, dict):
        errors.append("Project must be a dictionary")
        return False, errors
    
    for milestone_name, milestone_data in project.items():
        if not isinstance(milestone_name, str) or not milestone_name.strip():
            errors.append(f"Invalid milestone name: {milestone_name}")
        
        if not isinstance(milestone_data, dict):
            errors.append(f"Milestone '{milestone_name}' data must be a dictionary")
            continue
        
        # Check required fields
        if 'issues' not in milestone_data:
            errors.append(f"Milestone '{milestone_name}' missing 'issues' field")
        
        if 'description' not in milestone_data:
            milestone_data['description'] = f"Milestone: {milestone_name}"
        
        # Validate issues
        issues = milestone_data.get('issues', [])
        if not isinstance(issues, list):
            errors.append(f"Milestone '{milestone_name}' issues must be a list")
            continue
        
        for i, issue in enumerate(issues):
            issue_errors = validate_issue(issue, f"{milestone_name}[{i}]")
            errors.extend(issue_errors)
    
    return len(errors) == 0, errors

def validate_issue(issue: Dict[str, Any], context: str = "") -> List[str]:
    """Validate individual issue structure"""
    
    errors = []
    
    if not isinstance(issue, dict):
        errors.append(f"{context}: Issue must be a dictionary")
        return errors
    
    # Required fields
    required_fields = ['title', 'body']
    for field in required_fields:
        if field not in issue or not isinstance(issue[field], str) or not issue[field].strip():
            errors.append(f"{context}: Missing or empty '{field}' field")
    
    # Optional fields with defaults
    if 'labels' not in issue:
        issue['labels'] = []
    elif not isinstance(issue['labels'], list):
        errors.append(f"{context}: 'labels' must be a list")
    
    if 'assignees' not in issue:
        issue['assignees'] = []
    elif not isinstance(issue['assignees'], list):
        errors.append(f"{context}: 'assignees' must be a list")
    
    # Validate label format
    for label in issue.get('labels', []):
        if not isinstance(label, str) or not label.strip():
            errors.append(f"{context}: Invalid label format")
    
    # Validate assignee format  
    for assignee in issue.get('assignees', []):
        if not isinstance(assignee, str) or not assignee.strip():
            errors.append(f"{context}: Invalid assignee format")
    
    return errors

def sanitize_parsed_project(project: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize and clean up parsed project data"""
    
    sanitized = {}
    
    for milestone_name, milestone_data in project.items():
        # Clean milestone name
        clean_name = milestone_name.strip()
        if len(clean_name) > 100:
            clean_name = clean_name[:100] + "..."
        
        # Clean milestone data
        clean_data = {
            'description': milestone_data.get('description', '').strip() or f"Milestone: {clean_name}",
            'issues': []
        }
        
        # Clean issues
        for issue in milestone_data.get('issues', []):
            clean_issue = {
                'title': issue.get('title', '').strip() or 'Untitled Issue',
                'body': issue.get('body', '').strip() or 'No description provided',
                'labels': [label.strip() for label in issue.get('labels', []) if label.strip()],
                'assignees': [assignee.strip() for assignee in issue.get('assignees', []) if assignee.strip()]
            }
            
            # Ensure reasonable length limits
            if len(clean_issue['title']) > 200:
                clean_issue['title'] = clean_issue['title'][:200] + "..."
            
            if len(clean_issue['body']) > 5000:
                clean_issue['body'] = clean_issue['body'][:5000] + "..."
            
            clean_data['issues'].append(clean_issue)
        
        sanitized[clean_name] = clean_data
    
    return sanitized

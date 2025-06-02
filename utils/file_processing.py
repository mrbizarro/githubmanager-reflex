"""
File processing utilities
"""

import streamlit as st
import re
from typing import Dict, List, Any, Optional, Tuple

def validate_uploaded_files(files: List) -> Tuple[bool, str]:
    """Validate uploaded files for processing"""
    
    if not files:
        return False, "No files uploaded"
    
    # Check file types
    valid_extensions = ['.md', '.markdown', '.txt']
    invalid_files = []
    
    for file in files:
        if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
            invalid_files.append(file.name)
    
    if invalid_files:
        return False, f"Invalid file types: {', '.join(invalid_files)}"
    
    # Check file sizes (max 10MB per file)
    max_size = 10 * 1024 * 1024  # 10MB
    large_files = []
    
    for file in files:
        if hasattr(file, 'size') and file.size > max_size:
            large_files.append(f"{file.name} ({file.size / (1024*1024):.1f}MB)")
    
    if large_files:
        return False, f"Files too large: {', '.join(large_files)}"
    
    return True, "Files are valid"

def extract_file_content(file) -> Tuple[str, str]:
    """Extract content from uploaded file"""
    
    try:
        # Read file content
        content = file.read().decode('utf-8')
        file.seek(0)  # Reset file pointer
        
        # Basic content validation
        if not content.strip():
            return "", "File is empty"
        
        return content, "Success"
    
    except UnicodeDecodeError:
        try:
            file.seek(0)
            content = file.read().decode('latin-1')
            file.seek(0)
            return content, "Success (latin-1 encoding)"
        except Exception as e:
            return "", f"Encoding error: {str(e)}"
    
    except Exception as e:
        return "", f"Read error: {str(e)}"

def preprocess_markdown_content(content: str) -> str:
    """Preprocess markdown content for better parsing"""
    
    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove extra whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Fix common markdown issues
    content = fix_markdown_headers(content)
    content = fix_markdown_lists(content)
    
    return content.strip()

def fix_markdown_headers(content: str) -> str:
    """Fix common header formatting issues"""
    
    # Ensure space after # symbols
    content = re.sub(r'^(#{1,6})([^#\s])', r'\1 \2', content, flags=re.MULTILINE)
    
    # Remove trailing #
    content = re.sub(r'^(#{1,6}.*?)#+\s*$', r'\1', content, flags=re.MULTILINE)
    
    return content

def fix_markdown_lists(content: str) -> str:
    """Fix common list formatting issues"""
    
    # Ensure proper spacing for list items
    content = re.sub(r'^(\s*[-*+])\s*([^\s])', r'\1 \2', content, flags=re.MULTILINE)
    content = re.sub(r'^(\s*\d+\.)\s*([^\s])', r'\1 \2', content, flags=re.MULTILINE)
    
    return content

def estimate_processing_time(files: List) -> float:
    """Estimate processing time based on file content"""
    
    if not files:
        return 0.0
    
    total_size = 0
    total_lines = 0
    
    for file in files:
        try:
            content = file.read().decode('utf-8')
            file.seek(0)
            
            total_size += len(content)
            total_lines += len(content.split('\n'))
        except:
            # If we can't read the file, assume average size
            total_size += 5000  # 5KB average
            total_lines += 100   # 100 lines average
    
    # Rough estimation: 1 second per 10KB or 500 lines, whichever is higher
    time_by_size = total_size / 10000
    time_by_lines = total_lines / 500
    
    estimated_time = max(time_by_size, time_by_lines)
    
    # Add AI processing overhead if enabled
    if st.session_state.get('ai_enabled', False):
        estimated_time *= 2  # AI takes roughly 2x longer
    
    # Minimum 1 second, maximum 60 seconds for UI purposes
    return max(1.0, min(estimated_time, 60.0))

def generate_file_summary(files: List) -> Dict[str, Any]:
    """Generate summary statistics for uploaded files"""
    
    if not files:
        return {
            'total_files': 0,
            'total_size': 0,
            'total_lines': 0,
            'file_types': {},
            'largest_file': None,
            'estimated_milestones': 0,
            'estimated_issues': 0
        }
    
    total_size = 0
    total_lines = 0
    file_types = {}
    largest_file = {'name': '', 'size': 0}
    estimated_milestones = 0
    estimated_issues = 0
    
    for file in files:
        # File extension
        ext = file.name.split('.')[-1].lower()
        file_types[ext] = file_types.get(ext, 0) + 1
        
        try:
            content = file.read().decode('utf-8')
            file.seek(0)
            
            file_size = len(content)
            file_lines = len(content.split('\n'))
            
            total_size += file_size
            total_lines += file_lines
            
            # Track largest file
            if file_size > largest_file['size']:
                largest_file = {'name': file.name, 'size': file_size}
            
            # Estimate content (rough heuristics)
            milestone_matches = len(re.findall(r'^#{1,2}\s+(?:milestone|phase|sprint|release)', content, re.IGNORECASE | re.MULTILINE))
            issue_matches = len(re.findall(r'^#{2,3}\s+(?:issue|task|feature|bug)', content, re.IGNORECASE | re.MULTILINE))
            
            # If no explicit matches, estimate based on structure
            if milestone_matches == 0:
                milestone_matches = max(1, len(re.findall(r'^#{1,2}\s+[^#]', content, re.MULTILINE)) // 2)
            
            if issue_matches == 0:
                issue_matches = max(1, len(re.findall(r'^#{2,4}\s+[^#]', content, re.MULTILINE)))
            
            estimated_milestones += milestone_matches
            estimated_issues += issue_matches
            
        except Exception:
            # If we can't read the file, use defaults
            total_size += 5000
            total_lines += 100
            estimated_milestones += 1
            estimated_issues += 3
    
    return {
        'total_files': len(files),
        'total_size': total_size,
        'total_lines': total_lines,
        'file_types': file_types,
        'largest_file': largest_file,
        'estimated_milestones': estimated_milestones,
        'estimated_issues': estimated_issues
    }

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe processing"""
    
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove or replace invalid characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if len(name) > 100:
        name = name[:100]
    
    return f"{name}.{ext}" if ext else name

def extract_metadata_from_content(content: str) -> Dict[str, Any]:
    """Extract metadata from markdown content"""
    
    metadata = {
        'title': '',
        'description': '',
        'author': '',
        'created_date': '',
        'tags': [],
        'estimated_complexity': 'medium'
    }
    
    lines = content.split('\n')
    
    # Look for YAML frontmatter
    if lines and lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                break
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in metadata:
                    if key == 'tags' and value:
                        metadata[key] = [tag.strip() for tag in value.split(',')]
                    else:
                        metadata[key] = value
    
    # Extract title from first header if not in frontmatter
    if not metadata['title']:
        header_match = re.search(r'^#{1,2}\s+(.+)$', content, re.MULTILINE)
        if header_match:
            metadata['title'] = header_match.group(1).strip()
    
    # Estimate complexity based on content length and structure
    word_count = len(content.split())
    header_count = len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
    list_count = len(re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE))
    
    if word_count > 2000 or header_count > 20 or list_count > 50:
        metadata['estimated_complexity'] = 'high'
    elif word_count < 500 or header_count < 5 or list_count < 10:
        metadata['estimated_complexity'] = 'low'
    
    return metadata

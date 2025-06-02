"""
Upload & Convert page - main file processing functionality
"""

import streamlit as st
import time
import json
from datetime import datetime

from utils.session import (
    update_processing_state, 
    update_deployment_state, 
    add_deployment_log,
    reset_deployment_state
)
from components.status import render_quick_stats
from config.settings import get_config

def render_upload_page():
    """Render the upload and convert page"""
    
    # Quick stats if we have processed projects
    if st.session_state.get('processed_projects'):
        render_quick_stats()
        st.markdown('<div class="modern-separator"></div>', unsafe_allow_html=True)
    
    # Upload section
    render_upload_section()
    
    # Processing section
    if st.session_state.get('uploaded_files'):
        st.markdown('<div class="modern-separator"></div>', unsafe_allow_html=True)
        render_processing_section()
    
    # Results section
    if st.session_state.get('processed_projects'):
        st.markdown('<div class="modern-separator"></div>', unsafe_allow_html=True)
        render_results_section()
    
    # Deployment section
    deployment_state = st.session_state.get('deployment_state', {})
    if deployment_state.get('status', 'pending') != 'pending':
        st.markdown('<div class="modern-separator"></div>', unsafe_allow_html=True)
        render_deployment_section()

def render_upload_section():
    """Render file upload section with modern design"""
    
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <h2 class="card-title">📁 Upload & Convert Markdown</h2>
            <p class="card-description">Upload markdown files to convert them to GitHub issues and milestones</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI toggle
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ai_enabled = st.toggle(
            "🤖 AI Parsing Mode",
            value=st.session_state.get('ai_enabled', True),
            disabled=not get_config('ai_connected', False),
            help="Use DeepSeek AI for intelligent markdown parsing"
        )
        st.session_state.ai_enabled = ai_enabled
    
    with col2:
        mode_badge = "AI Mode" if ai_enabled else "Standard Mode"
        badge_class = "badge-primary" if ai_enabled else "badge-destructive"
        st.markdown(f'<span class="modern-badge {badge_class}">{mode_badge}</span>', unsafe_allow_html=True)
    
    # Status alert
    if ai_enabled and get_config('ai_connected', False):
        render_alert(
            type="success",
            title="AI Mode Active",
            description="Upload any markdown format - AI will intelligently parse content"
        )
    elif ai_enabled and not get_config('ai_connected', False):
        render_alert(
            type="warning", 
            title="AI Unavailable",
            description="DeepSeek API not configured - falling back to standard parsing"
        )
    else:
        render_alert(
            type="info",
            title="Standard Mode",
            description="Using traditional parsing - requires specific markdown format"
        )
    
    # File upload modes
    upload_mode = st.radio(
        "Select upload mode:",
        ["📄 Single File", "📚 Batch Upload"],
        horizontal=True,
        key="upload_mode"
    )
    
    # File uploader
    multiple_files = upload_mode == "📚 Batch Upload"
    
    uploaded_files = st.file_uploader(
        "Drop your markdown files here" if multiple_files else "Drop your markdown file here",
        type=["md", "markdown", "txt"],
        accept_multiple_files=multiple_files,
        help="Supported formats: .md, .markdown, .txt",
        key="file_uploader"
    )
    
    # Store uploaded files in session state
    if uploaded_files:
        if multiple_files:
            st.session_state.uploaded_files = uploaded_files
        else:
            st.session_state.uploaded_files = [uploaded_files]
        
        # Show file info
        file_count = len(st.session_state.uploaded_files)
        total_size = sum(len(f.read()) for f in st.session_state.uploaded_files) / 1024
        
        # Reset file pointers
        for f in st.session_state.uploaded_files:
            f.seek(0)
        
        render_alert(
            type="info",
            title=f"Files Ready",
            description=f"{file_count} file(s) uploaded, {total_size:.1f} KB total"
        )
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🔄 Reset", key="reset_upload", help="Clear uploaded files"):
            st.session_state.uploaded_files = []
            st.session_state.processed_projects = None
            reset_deployment_state()
            st.rerun()
    
    with col2:
        process_disabled = not st.session_state.get('uploaded_files') or st.session_state.get('processing_state', {}).get('status') == 'processing'
        
        if st.button(
            "🚀 Process Files", 
            type="primary", 
            disabled=process_disabled,
            use_container_width=True,
            key="process_files"
        ):
            process_uploaded_files()
    
    with col3:
        if st.session_state.get('processed_projects'):
            export_data = json.dumps(st.session_state.processed_projects, indent=2)
            st.download_button(
                "💾 Export",
                data=export_data,
                file_name="github_export.json",
                mime="application/json",
                key="export_processed"
            )

def render_processing_section():
    """Render processing status and progress"""
    
    processing_state = st.session_state.get('processing_state', {})
    status = processing_state.get('status', 'idle')
    
    if status == 'processing':
        st.markdown("""
        <div class="modern-card">
            <div class="card-header">
                <h3 class="card-title">🔄 Processing Files</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progress = processing_state.get('progress', 0)
        st.progress(progress / 100, text=f"Processing... {progress}%")
        
        # Current message
        message = processing_state.get('message', '')
        if message:
            st.info(message)

def render_results_section():
    """Render processing results with editing capabilities"""
    
    projects = st.session_state.get('processed_projects', {})
    if not projects:
        return
    
    st.markdown("### ✏️ Review & Edit Results")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("📊 View Summary", key="view_summary"):
            st.session_state.show_summary = not st.session_state.get('show_summary', False)
    
    with col2:
        export_data = json.dumps(projects, indent=2)
        st.download_button(
            "💾 Export JSON",
            data=export_data,
            file_name="github_export.json", 
            mime="application/json",
            key="export_results"
        )
    
    with col3:
        github_ok = get_config('github_connected', False)
        deploy_disabled = not github_ok or st.session_state.get('deployment_state', {}).get('status') == 'running'
        
        if st.button(
            "🚀 Deploy to GitHub",
            type="primary",
            disabled=deploy_disabled,
            key="deploy_results"
        ):
            start_deployment()
    
    # Summary view
    if st.session_state.get('show_summary', False):
        render_project_summary(projects)
    
    # Edit interface
    render_project_editor(projects)

def render_project_summary(projects):
    """Render project summary statistics"""
    
    total_milestones = len(projects)
    total_issues = sum(len(m.get('issues', [])) for m in projects.values())
    
    st.markdown("#### 📊 Project Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Milestones", total_milestones)
    
    with col2:
        st.metric("Total Issues", total_issues)
    
    with col3:
        avg_issues = round(total_issues / total_milestones, 1) if total_milestones > 0 else 0
        st.metric("Avg Issues/Milestone", avg_issues)
    
    with col4:
        parsing_mode = "AI" if st.session_state.get('ai_enabled', True) else "Standard"
        st.metric("Parsing Mode", parsing_mode)

def render_project_editor(projects):
    """Render project editing interface"""
    
    st.markdown("#### ✏️ Edit Projects")
    
    edited_projects = {}
    
    for milestone_name, milestone_data in projects.items():
        with st.expander(f"🎯 {milestone_name}", expanded=False):
            
            # Edit milestone description
            new_desc = st.text_area(
                "Milestone Description",
                value=milestone_data.get('description', ''),
                key=f"desc_{milestone_name}",
                height=100
            )
            
            # Edit issues
            edited_issues = []
            issues = milestone_data.get('issues', [])
            
            st.markdown(f"**Issues ({len(issues)})**")
            
            for idx, issue in enumerate(issues):
                st.markdown(f"**Issue {idx + 1}**")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    new_title = st.text_input(
                        "Title",
                        value=issue.get('title', ''),
                        key=f"title_{milestone_name}_{idx}"
                    )
                    
                    new_body = st.text_area(
                        "Description", 
                        value=issue.get('body', ''),
                        key=f"body_{milestone_name}_{idx}",
                        height=80
                    )
                
                with col2:
                    labels_str = ",".join(issue.get('labels', []))
                    new_labels = st.text_input(
                        "Labels (comma-separated)",
                        value=labels_str,
                        key=f"labels_{milestone_name}_{idx}"
                    )
                    
                    assignees_str = ",".join(issue.get('assignees', []))
                    new_assignees = st.text_input(
                        "Assignees (comma-separated)",
                        value=assignees_str,
                        key=f"assignees_{milestone_name}_{idx}"
                    )
                
                edited_issues.append({
                    'title': new_title,
                    'body': new_body,
                    'labels': [l.strip() for l in new_labels.split(',') if l.strip()],
                    'assignees': [a.strip() for a in new_assignees.split(',') if a.strip()]
                })
                
                if idx < len(issues) - 1:
                    st.markdown("---")
            
            edited_projects[milestone_name] = {
                'description': new_desc,
                'issues': edited_issues
            }
    
    # Update session state with edited projects
    st.session_state.processed_projects = edited_projects

def render_deployment_section():
    """Render deployment progress and status"""
    
    deployment_state = st.session_state.get('deployment_state', {})
    status = deployment_state.get('status', 'pending')
    
    st.markdown("### 🚀 Deployment Progress")
    
    # Status indicator
    render_deployment_status(deployment_state)
    
    # Progress metrics
    render_deployment_metrics(deployment_state)
    
    # Deployment log
    if deployment_state.get('logs'):
        render_deployment_log(deployment_state['logs'])
    
    # Error display
    if deployment_state.get('errors'):
        render_deployment_errors(deployment_state['errors'])
    
    # Reset button
    if status in ['completed', 'error']:
        if st.button("🔄 Reset Deployment", key="reset_deployment"):
            reset_deployment_state()
            st.rerun()

def render_deployment_status(deployment_state):
    """Render deployment status indicator"""
    
    status = deployment_state.get('status', 'pending')
    
    status_config = {
        'pending': {
            'icon': 'ℹ️',
            'title': 'Ready to Deploy',
            'type': 'info'
        },
        'running': {
            'icon': '🔄',
            'title': 'Deployment in Progress...',
            'type': 'info'
        },
        'completed': {
            'icon': '✅',
            'title': 'Deployment Completed Successfully!',
            'type': 'success'
        },
        'error': {
            'icon': '❌', 
            'title': 'Deployment Failed',
            'type': 'error'
        }
    }
    
    config = status_config.get(status, status_config['pending'])
    
    render_alert(
        type=config['type'],
        title=config['title'],
        description=f"Status: {status.title()}"
    )
    
    # Progress bar
    progress = deployment_state.get('progress', 0)
    if progress > 0:
        st.progress(progress / 100, text=f"Progress: {progress}%")

def render_deployment_metrics(deployment_state):
    """Render deployment metrics cards"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Progress", f"{deployment_state.get('progress', 0)}%")
    
    with col2:
        st.metric("Milestones Created", deployment_state.get('created_milestones', 0))
    
    with col3:
        st.metric("Issues Created", deployment_state.get('created_issues', 0))
    
    with col4:
        st.metric("Errors", len(deployment_state.get('errors', [])))

def render_deployment_log(logs):
    """Render deployment log entries"""
    
    st.markdown("#### 📜 Deployment Log")
    
    # Show last 20 entries
    recent_logs = logs[-20:] if len(logs) > 20 else logs
    
    log_container = st.container()
    with log_container:
        log_html = '<div class="scroll-area">'
        
        for log_entry in recent_logs:
            icon = log_entry.get('icon', 'ℹ️')
            message = log_entry.get('message', '')
            timestamp = log_entry.get('timestamp', '')
            
            log_html += f"""
            <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.25rem 0; font-size: 0.875rem;">
                <span>{icon}</span>
                <span style="flex: 1;">{message}</span>
                <span style="color: hsl(var(--muted-foreground)); font-size: 0.75rem;">{timestamp}</span>
            </div>
            """
        
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)

def render_deployment_errors(errors):
    """Render deployment errors"""
    
    st.markdown("#### ⚠️ Deployment Errors")
    
    for i, error in enumerate(errors[-5:], 1):  # Show last 5 errors
        st.error(f"Error {i}: {error}")

def render_alert(type, title, description):
    """Render modern alert component"""
    
    alert_class = f"alert-{type}"
    icon_map = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️'
    }
    
    icon = icon_map.get(type, 'ℹ️')
    
    st.markdown(f"""
    <div class="modern-alert {alert_class}">
        <span style="font-size: 1.1rem;">{icon}</span>
        <div>
            <div class="alert-title">{title}</div>
            <div class="alert-description">{description}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def process_uploaded_files():
    """Process uploaded markdown files"""
    
    files = st.session_state.get('uploaded_files', [])
    if not files:
        st.error("No files to process")
        return
    
    # Update processing state
    update_processing_state(status='processing', progress=0, message='Starting file processing...')
    
    # Force UI update
    st.rerun()
    
    try:
        # Process files immediately without delays
        all_projects = {}
        total_files = len(files)
        
        for i, file in enumerate(files):
            # Update progress
            progress = int((i / total_files) * 50)  # First 50% for reading
            update_processing_state(
                progress=progress, 
                message=f"Reading {file.name}..."
            )
            
            # Read file content
            try:
                content = file.read().decode('utf-8')
                file.seek(0)  # Reset file pointer
            except Exception as e:
                st.error(f"Failed to read {file.name}: {str(e)}")
                continue
            
            # Update progress for parsing
            progress = int(50 + (i / total_files) * 50)  # Second 50% for parsing
            update_processing_state(
                progress=progress, 
                message=f"Parsing {file.name}..."
            )
            
            # Use AI or standard parsing
            ai_enabled = st.session_state.get('ai_enabled', True) and get_config('ai_connected', False)
            
            try:
                if ai_enabled:
                    # Try AI parsing with timeout
                    parsed_project = simulate_ai_parsing(content, file.name)
                else:
                    # Use standard parsing
                    parsed_project = simulate_standard_parsing(content, file.name)
                
                if parsed_project:
                    # Add file prefix for multiple files
                    if total_files > 1:
                        file_prefix = file.name.replace('.md', '').replace('.markdown', '').replace('.txt', '')
                        prefixed_project = {
                            f"[{file_prefix}] {name}": data 
                            for name, data in parsed_project.items()
                        }
                        all_projects.update(prefixed_project)
                    else:
                        all_projects.update(parsed_project)
                else:
                    st.warning(f"No content extracted from {file.name}")
                    
            except Exception as e:
                st.error(f"Failed to parse {file.name}: {str(e)}")
                continue
        
        # Complete processing
        update_processing_state(
            status='completed',
            progress=100,
            message='Processing completed successfully!',
            results=all_projects
        )
        
        # Store results
        st.session_state.processed_projects = all_projects
        
        st.success(f"✅ Processed {total_files} files successfully!")
        st.rerun()
        
    except Exception as e:
        update_processing_state(
            status='error',
            message=f'Processing failed: {str(e)}'
        )
        st.error(f"❌ Processing failed: {str(e)}")

def simulate_ai_parsing(content, filename):
    """Use real DeepSeek AI to parse markdown content with timeout"""
    
    try:
        # Import the real parsing function
        import sys
        import os
        
        # Add the main directory to path
        main_dir = os.path.dirname(os.path.dirname(__file__))
        if main_dir not in sys.path:
            sys.path.insert(0, main_dir)
        
        from deepseek_api import ai_parse_markdown
        
        # Use real AI parsing with progress indication
        update_processing_state(message=f"AI analyzing {filename}...")
        reasoning, structure = ai_parse_markdown(content)
        
        return structure
        
    except ImportError as e:
        st.warning(f"AI module not available: {str(e)}. Using standard parsing.")
        return simulate_standard_parsing(content, filename)
    except Exception as e:
        # If AI fails, fall back to standard parsing
        st.warning(f"AI parsing failed for {filename}: {str(e)}. Using standard parsing.")
        return simulate_standard_parsing(content, filename)

def simulate_standard_parsing(content, filename):
    """Use real regex parsing of markdown content"""
    
    try:
        # Import the real parsing function
        import sys
        import os
        
        # Add the cleanup_backup directory to path
        cleanup_dir = os.path.join(os.path.dirname(__file__), '..', 'cleanup_backup')
        cleanup_dir = os.path.abspath(cleanup_dir)
        
        if cleanup_dir not in sys.path:
            sys.path.insert(0, cleanup_dir)
        
        from parse_markdown import parse_markdown_regex
        
        # Use real regex parsing
        update_processing_state(message=f"Standard parsing {filename}...")
        structure = parse_markdown_regex(content)
        
        return structure
        
    except ImportError as e:
        st.error(f"Standard parsing module not found: {str(e)}")
        return {}
    except Exception as e:
        st.error(f"Standard parsing failed for {filename}: {str(e)}")
        return {}

def start_deployment():
    """Start GitHub deployment process"""
    
    projects = st.session_state.get('processed_projects', {})
    if not projects:
        st.error("No projects to deploy")
        return
    
    # Reset deployment state
    reset_deployment_state()
    
    # Initialize deployment
    update_deployment_state(
        status='running',
        progress=0,
        current_action='Initializing deployment...',
        start_time=datetime.now()
    )
    
    add_deployment_log('ℹ️', 'Deployment started')
    
    # Simulate deployment process
    simulate_github_deployment(projects)

def simulate_github_deployment(projects):
    """Use real GitHub API for deployment"""
    
    total_milestones = len(projects)
    total_issues = sum(len(m.get('issues', [])) for m in projects.values())
    total_steps = total_milestones + total_issues
    current_step = 0
    
    try:
        # Import real GitHub API functions
        from utils.github_api import GitHubAPI, GitHubAPIError
        
        # Initialize GitHub API
        api = GitHubAPI()
        
        # Process each milestone and its issues
        for milestone_name, milestone_data in projects.items():
            current_step += 1
            progress = int((current_step / total_steps) * 100)
            
            # Update progress
            update_deployment_state(
                progress=progress,
                current_action=f"Creating milestone: {milestone_name}"
            )
            
            add_deployment_log('🎯', f'Creating milestone: {milestone_name}')
            
            # Create milestone using real API
            try:
                milestone_response = api.create_milestone(
                    title=milestone_name,
                    description=milestone_data.get('description', ''),
                    state=milestone_data.get('state', 'open'),
                    due_date=milestone_data.get('due_date')
                )
                
                milestone_number = milestone_response['number']
                
                # Add small delay to avoid rate limiting
                time.sleep(0.5)
                
                # Update milestone count
                update_deployment_state(created_milestones=st.session_state.deployment_state['created_milestones'] + 1)
                add_deployment_log('✅', f'Created milestone #{milestone_number}: {milestone_name}')
                
                # Process issues for this milestone
                for issue_index, issue in enumerate(milestone_data.get('issues', [])):
                    current_step += 1
                    progress = int((current_step / total_steps) * 100)
                    
                    issue_title = issue.get('title', f'Issue {issue_index + 1}')
                    short_title = issue_title[:40] + '...' if len(issue_title) > 40 else issue_title
                    
                    update_deployment_state(
                        progress=progress,
                        current_action=f"Creating issue: {short_title}"
                    )
                    
                    add_deployment_log('📋', f'Creating issue: {short_title}')
                    
                    # Create issue using real API
                    try:
                        issue_response = api.create_issue(
                            title=issue_title,
                            body=issue.get('body', ''),
                            milestone_number=milestone_number,
                            labels=issue.get('labels', []),
                            assignees=issue.get('assignees', [])
                        )
                        
                        issue_number = issue_response['number']
                        
                        # Add delay to avoid rate limiting
                        time.sleep(0.5)
                        
                        # Update issue count
                        update_deployment_state(created_issues=st.session_state.deployment_state['created_issues'] + 1)
                        add_deployment_log('✅', f'Created issue #{issue_number}: {short_title}')
                        
                    except GitHubAPIError as e:
                        error_msg = f"Failed to create issue '{issue_title}': {str(e)}"
                        st.session_state.deployment_state['errors'].append(error_msg)
                        add_deployment_log('❌', error_msg)
                        continue
                        
            except GitHubAPIError as e:
                error_msg = f"Failed to create milestone '{milestone_name}': {str(e)}"
                st.session_state.deployment_state['errors'].append(error_msg)
                add_deployment_log('❌', error_msg)
                continue
        
        # Deployment completed
        update_deployment_state(
            status='completed',
            progress=100,
            current_action='',
            end_time=datetime.now()
        )
        
        completion_msg = f"Deployment completed! Created {st.session_state.deployment_state['created_milestones']} milestones and {st.session_state.deployment_state['created_issues']} issues"
        add_deployment_log('✅', completion_msg)
        
        st.success("🚀 Deployment completed successfully!")
        st.rerun()
        
    except Exception as e:
        update_deployment_state(
            status='error',
            end_time=datetime.now()
        )
        
        error_msg = f"Deployment failed: {str(e)}"
        st.session_state.deployment_state['errors'].append(error_msg)
        add_deployment_log('❌', error_msg)
        
        st.error(f"❌ Deployment failed: {str(e)}")
        st.rerun()

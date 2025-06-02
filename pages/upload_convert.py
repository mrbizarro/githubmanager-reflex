"""
Upload & Convert page - main file processing functionality
With async processing for improved performance
THREAD-SAFE VERSION - No session state access in background threads
"""

import streamlit as st
import time
import json
import threading
import concurrent.futures
from datetime import datetime
import queue

from utils.session import (
    update_processing_state, 
    update_deployment_state, 
    add_deployment_log,
    reset_deployment_state
)
from components.status import render_quick_stats
from config.settings import get_config

# Thread-safe queue for communication between background thread and main thread
processing_queue = queue.Queue()

def render_upload_page():
    """Render the upload and convert page"""
    
    # Check for updates from background processing
    process_background_updates()
    
    # Quick stats if we have processed projects
    if st.session_state.get('processed_projects'):
        render_quick_stats()
        st.markdown('<div class="modern-separator"></div>', unsafe_allow_html=True)
    
    # Check if async processing is active
    if st.session_state.get('async_processing', False):
        render_async_processing_status()
        return
    
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

def process_background_updates():
    """Process updates from background thread in a thread-safe way"""
    try:
        while not processing_queue.empty():
            update = processing_queue.get_nowait()
            if update['type'] == 'progress':
                st.session_state.processing_progress = update['progress']
                st.session_state.processing_status = update['status']
            elif update['type'] == 'error':
                if 'processing_errors' not in st.session_state:
                    st.session_state.processing_errors = []
                st.session_state.processing_errors.append(update['error'])
            elif update['type'] == 'complete':
                st.session_state.processing_progress = 100
                st.session_state.processing_status = "⚡ Processing completed!"
                st.session_state.processed_projects = update['results']
                st.session_state.async_processing = False
                st.session_state.processing_total_time = update['total_time']
    except queue.Empty:
        pass

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
            title="AI Mode Active ⚡",
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
            st.session_state.async_processing = False
            st.session_state.processing_errors = []
            reset_deployment_state()
            st.rerun()
    
    with col2:
        process_disabled = not st.session_state.get('uploaded_files') or st.session_state.get('async_processing', False)
        
        if st.button(
            "⚡ Process Files", 
            type="primary", 
            disabled=process_disabled,
            use_container_width=True,
            key="process_files"
        ):
            start_async_processing(st.session_state.uploaded_files)
    
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

def start_async_processing(files):
    """Start async processing with real-time updates"""
    
    # Initialize processing state safely
    st.session_state.async_processing = True
    st.session_state.processing_results = {}
    st.session_state.processing_progress = 0
    st.session_state.processing_status = "Starting processing..."
    st.session_state.processing_errors = []
    st.session_state.processing_start_time = time.time()
    
    # Clear the queue
    while not processing_queue.empty():
        try:
            processing_queue.get_nowait()
        except queue.Empty:
            break
    
    # Start background thread
    threading.Thread(
        target=background_file_processor,
        args=(files,),
        daemon=True
    ).start()
    
    # Force UI refresh
    st.rerun()

def background_file_processor(files):
    """
    COMPLETELY THREAD-SAFE background processing 
    NO access to st.session_state - only queue communication
    """
    
    start_time = time.time()
    
    try:
        total_files = len(files)
        completed_files = 0
        all_results = {}
        
        print(f"🚀 Starting background processing of {total_files} files")
        
        # Use ThreadPoolExecutor for concurrent processing
        max_workers = min(2, total_files)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            
            # Submit all files for processing
            future_to_file = {
                executor.submit(process_single_file_thread_safe, file): file 
                for file in files
            }
            
            # Process completed futures
            for future in concurrent.futures.as_completed(future_to_file):
                file = future_to_file[future]
                completed_files += 1
                
                # Update progress through queue
                progress = int((completed_files / total_files) * 100)
                
                try:
                    processing_queue.put({
                        'type': 'progress',
                        'progress': progress,
                        'status': f"Completed {file.name} ({progress}%)"
                    })
                except Exception as queue_error:
                    print(f"❌ Queue error during progress update: {queue_error}")
                
                try:
                    result = future.result(timeout=90)
                    if result:
                        # Handle multiple files with prefixes
                        if total_files > 1:
                            file_prefix = file.name.replace('.md', '').replace('.markdown', '').replace('.txt', '')
                            prefixed_result = {
                                f"[{file_prefix}] {name}": data 
                                for name, data in result.items()
                            }
                            all_results.update(prefixed_result)
                        else:
                            all_results.update(result)
                        
                        print(f"✅ Successfully processed {file.name}")
                    
                except concurrent.futures.TimeoutError:
                    error_msg = f"Timeout processing {file.name} (>90s)"
                    print(f"⏰ {error_msg}")
                    try:
                        processing_queue.put({
                            'type': 'error',
                            'error': error_msg
                        })
                    except Exception as queue_error:
                        print(f"❌ Queue error during timeout: {queue_error}")
                    
                except Exception as e:
                    error_msg = f"Error processing {file.name}: {str(e)}"
                    print(f"❌ {error_msg}")
                    try:
                        processing_queue.put({
                            'type': 'error',
                            'error': error_msg
                        })
                    except Exception as queue_error:
                        print(f"❌ Queue error during error: {queue_error}")
        
        # Complete processing
        total_time = time.time() - start_time
        
        try:
            processing_queue.put({
                'type': 'complete',
                'results': all_results,
                'total_time': total_time
            })
        except Exception as queue_error:
            print(f"❌ Queue error during completion: {queue_error}")
        
        print(f"⚡ Background processing completed in {total_time:.2f}s")
        
    except Exception as e:
        # Handle any other errors
        error_msg = f"Background processing failed: {str(e)}"
        print(f"💥 {error_msg}")
        
        try:
            processing_queue.put({
                'type': 'error',
                'error': error_msg
            })
            processing_queue.put({
                'type': 'complete',
                'results': {},
                'total_time': time.time() - start_time
            })
        except Exception as queue_error:
            print(f"❌ Final queue error: {queue_error}")

def process_single_file_thread_safe(file):
    """Thread-safe single file processing - NO session state access"""
    
    start_time = time.time()
    
    try:
        # Read file content efficiently
        content = file.read().decode('utf-8')
        file.seek(0)  # Reset file pointer
        
        # Quick preprocessing
        cleaned_content = preprocess_content_fast(content)
        
        # Use optimized AI parsing
        try:
            # Import optimized AI function
            import sys
            import os
            
            # Add the main directory to path
            main_dir = os.path.dirname(os.path.dirname(__file__))
            if main_dir not in sys.path:
                sys.path.insert(0, main_dir)
            
            from deepseek_api import ai_parse_markdown
            
            # Use optimized AI parsing
            _, structure = ai_parse_markdown(cleaned_content)
            
            processing_time = time.time() - start_time
            print(f"⚡ AI processed {file.name} in {processing_time:.2f}s")
            
            return structure
            
        except Exception as ai_error:
            print(f"❌ AI parsing failed for {file.name}: {ai_error}")
            # Fallback to fast regex parsing
            return fallback_regex_parsing(cleaned_content, file.name)
        
    except Exception as e:
        print(f"❌ File processing failed for {file.name}: {e}")
        return fallback_regex_parsing("# Error Processing File\n\nFailed to read file content.", file.name)

def preprocess_content_fast(content: str) -> str:
    """Lightning-fast content preprocessing"""
    
    # Remove excessive whitespace and empty lines
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    cleaned = '\n'.join(lines)
    
    # Remove very long lines that might be data/logs
    lines = []
    for line in cleaned.split('\n'):
        if len(line) > 500:  # Skip very long lines
            lines.append(line[:500] + "...")
        else:
            lines.append(line)
    
    cleaned = '\n'.join(lines)
    
    # Truncate if too long
    if len(cleaned) > 8000:
        cleaned = cleaned[:8000] + "\n\n[Content truncated for processing efficiency]"
    
    return cleaned

def fallback_regex_parsing(content: str, filename: str):
    """Fast regex fallback parsing"""
    
    try:
        # Simple header-based parsing
        lines = content.split('\n')
        current_project = None
        projects = {}
        current_issues = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Main project header
            if line.startswith('# '):
                if current_project and current_issues:
                    projects[current_project] = {
                        'description': f'Project: {current_project}',
                        'issues': current_issues
                    }
                
                current_project = line[2:].strip()
                current_issues = []
            
            # Sub-headers as issues
            elif line.startswith('## ') and current_project:
                issue_title = line[3:].strip()
                current_issues.append({
                    'title': f'[Implementation] {issue_title}',
                    'body': f'Implement {issue_title} as described in the requirements.',
                    'labels': ['enhancement', 'task'],
                    'assignees': []
                })
        
        # Add final project
        if current_project and current_issues:
            projects[current_project] = {
                'description': f'Project: {current_project}',
                'issues': current_issues
            }
        
        # Fallback if no structure found
        if not projects:
            project_name = filename.replace('.md', '').replace('.markdown', '').replace('.txt', '')
            projects[f"Project from {project_name}"] = {
                'description': 'Auto-generated project from markdown',
                'issues': [{
                    'title': '[Review] Organize project structure',
                    'body': 'Review the uploaded markdown and organize into proper issues.',
                    'labels': ['documentation', 'task'],
                    'assignees': []
                }]
            }
        
        return projects
        
    except Exception as e:
        print(f"❌ Regex parsing failed: {e}")
        # Return minimal structure as last resort
        project_name = filename.replace('.md', '').replace('.markdown', '').replace('.txt', '')
        return {
            f"Emergency Project - {project_name}": {
                'description': 'Failed to parse content - manual review needed',
                'issues': [{
                    'title': '[Emergency] Manual review required',
                    'body': 'Content parsing failed. Please review the original file manually.',
                    'labels': ['bug', 'high-priority'],
                    'assignees': []
                }]
            }
        }

def render_async_processing_status():
    """Render real-time async processing status"""
    
    st.markdown("### ⚡ Processing Files")
    
    # Progress bar
    progress = st.session_state.get('processing_progress', 0)
    status = st.session_state.get('processing_status', 'Processing...')
    
    st.progress(progress / 100, text=f"{status}")
    
    # Processing info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.get('processing_start_time'):
            elapsed = time.time() - st.session_state.processing_start_time
            st.metric("Elapsed Time", f"{elapsed:.1f}s")
    
    with col2:
        files_total = len(st.session_state.get('uploaded_files', []))
        files_done = int((progress / 100) * files_total) if progress > 0 else 0
        st.metric("Files", f"{files_done}/{files_total}")
    
    with col3:
        errors = st.session_state.get('processing_errors', [])
        st.metric("Errors", len(errors))
    
    # Show errors if any
    if errors:
        with st.expander(f"❌ Errors ({len(errors)})", expanded=False):
            for error in errors[-3:]:  # Show last 3 errors
                st.error(error)
    
    # Auto-refresh during processing
    if st.session_state.async_processing:
        time.sleep(0.8)  # Refresh rate
        st.rerun()
    else:
        # Processing completed
        if st.session_state.get('processed_projects'):
            total_time = st.session_state.get('processing_total_time', 0)
            project_count = len(st.session_state.processed_projects)
            
            st.success(f"✅ Processing completed in {total_time:.2f}s!")
            st.info(f"⚡ Created {project_count} project(s) ready for deployment")
            
            # Performance metrics
            files_count = len(st.session_state.get('uploaded_files', []))
            avg_time = total_time / files_count if files_count > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Time per File", f"{avg_time:.1f}s")
            with col2:
                st.metric("Processing Time", f"{total_time:.1f}s")
            
            # Reset button
            if st.button("🔄 Process New Files", use_container_width=True):
                st.session_state.async_processing = False
                st.session_state.uploaded_files = []
                st.session_state.processed_projects = None
                st.session_state.processing_errors = []
                st.rerun()

def render_processing_section():
    """Render processing status and progress"""
    
    # Show async processing status if active
    if st.session_state.get('async_processing', False):
        render_async_processing_status()
        return
    
    # Legacy processing status (kept for compatibility)
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
        parsing_mode = "AI ⚡" if st.session_state.get('ai_enabled', True) else "Standard"
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

# Legacy function maintained for compatibility
def process_uploaded_files():
    """Legacy sync processing function - maintained for compatibility"""
    
    files = st.session_state.get('uploaded_files', [])
    if not files:
        st.error("No files to process")
        return
    
    # Redirect to async processing
    start_async_processing(files)

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

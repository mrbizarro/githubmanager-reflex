# Quick Fix for Enhanced Deployment
# Add this enhanced deployment function directly to your app.py

def create_enhanced_deployment_ui(projects, dry_run, github_ok):
    """Create enhanced deployment UI with progress tracking"""
    
    import streamlit as st
    import time
    from datetime import datetime
    
    # Initialize deployment state
    if 'deployment_state' not in st.session_state:
        st.session_state.deployment_state = {
            'status': 'pending',
            'progress': 0,
            'current_action': '',
            'logs': [],
            'errors': [],
            'created_milestones': 0,
            'created_issues': 0,
            'start_time': None,
            'end_time': None
        }
    
    total_milestones = len(projects)
    total_issues = sum(len(proj_data.get('issues', [])) for proj_data in projects.values())
    
    st.markdown("---")
    st.markdown("## 🚀 Enhanced Deploy to GitHub")
    
    # Deployment mode indicator
    deployment_mode = "🧪 Test Deployment" if dry_run else "🚀 Live Deployment"
    deployment_color = "warning" if dry_run else "success"
    
    st.markdown(f"""
    <div class="message-box {deployment_color}">
        <h4 class="message-title">{deployment_mode}</h4>
        <p class="message-content">
            {'No changes will be made to your repository' if dry_run else 'Changes will be applied to your repository'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Status display
    state = st.session_state.deployment_state
    status_colors = {
        'pending': ('🟡', '#fbbf24', 'Ready to deploy'),
        'running': ('🔵', '#3b82f6', 'Deployment in progress...'),
        'completed': ('🟢', '#10b981', 'Deployment completed successfully!'),
        'error': ('🔴', '#ef4444', 'Deployment failed')
    }
    
    icon, color, message = status_colors.get(state['status'], ('🟡', '#fbbf24', 'Unknown status'))
    
    st.markdown(f"""
    <div style="
        display: flex; 
        align-items: center; 
        gap: 10px; 
        padding: 15px; 
        background: #1e293b; 
        border-radius: 10px; 
        border-left: 4px solid {color};
        margin: 20px 0;
    ">
        <span style="font-size: 1.2rem;">{icon}</span>
        <span style="color: #e2e8f0; font-weight: 500;">{message}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Progress", f"{state['progress']}%")
    with col2:
        st.metric("Milestones Created", state['created_milestones'])
    with col3:
        st.metric("Issues Created", state['created_issues'])
    with col4:
        st.metric("Errors", len(state['errors']))
    
    # Progress bar
    if state['progress'] > 0:
        st.progress(state['progress'] / 100)
    
    # Current action
    if state['status'] == 'running' and state['current_action']:
        st.markdown(f"""
        <div style="
            background: #334155; 
            padding: 15px; 
            border-radius: 10px; 
            border-left: 4px solid #6366f1;
            margin: 20px 0;
        ">
            <div style="color: #e2e8f0; font-weight: 500;">
                🔄 {state['current_action']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Deployment controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        deploy_button = st.button(
            f"🚀 Deploy {total_milestones} milestones & {total_issues} issues",
            disabled=(not github_ok and not dry_run) or state['status'] == 'running',
            type="primary",
            key="enhanced_deploy_button"
        )
    
    with col2:
        if st.button("🔄 Reset Progress", key="reset_enhanced_progress"):
            st.session_state.deployment_state = {
                'status': 'pending',
                'progress': 0,
                'current_action': '',
                'logs': [],
                'errors': [],
                'created_milestones': 0,
                'created_issues': 0,
                'start_time': None,
                'end_time': None
            }
            st.rerun()
    
    with col3:
        st.download_button(
            "💾 Export JSON",
            data=json.dumps(projects, indent=2),
            file_name="github_export.json",
            mime="application/json"
        )
    
    # Deployment log
    if state['logs']:
        st.subheader("📜 Deployment Log")
        
        log_html = """
        <div style="
            background: #0f172a; 
            border: 1px solid #334155; 
            border-radius: 10px; 
            padding: 15px; 
            max-height: 300px; 
            overflow-y: auto;
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
        ">
        """
        
        for log_entry in state['logs'][-20:]:  # Show last 20 entries
            log_html += f"""
            <div style="
                display: flex; 
                align-items: center; 
                gap: 8px; 
                padding: 4px 0;
                color: #e2e8f0;
            ">
                <span>{log_entry.get('icon', 'ℹ️')}</span>
                <span style="flex: 1;">{log_entry.get('message', '')}</span>
                <span style="color: #64748b; font-size: 0.75rem;">{log_entry.get('timestamp', '')}</span>
            </div>
            """
        
        log_html += "</div>"
        st.markdown(log_html, unsafe_allow_html=True)
    
    # Error details
    if state['errors']:
        st.subheader("⚠️ Errors")
        for i, error in enumerate(state['errors'][-5:], 1):
            st.error(f"Error {i}: {error}")
    
    # Handle deployment
    if deploy_button and state['status'] != 'running':
        # Start deployment
        st.session_state.deployment_state.update({
            'status': 'running',
            'progress': 0,
            'current_action': 'Initializing deployment...',
            'logs': [{
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'icon': 'ℹ️',
                'message': f"{'[DRY RUN] ' if dry_run else ''}Deployment started"
            }],
            'errors': [],
            'created_milestones': 0,
            'created_issues': 0,
            'start_time': datetime.now(),
            'end_time': None
        })
        
        st.rerun()
    
    # Process deployment if running
    if state['status'] == 'running':
        with st.spinner("Processing deployment..."):
            try:
                total_steps = total_milestones + total_issues
                current_step = 0
                
                # Process each milestone and its issues
                for milestone_name, milestone_data in projects.items():
                    current_step += 1
                    progress = int((current_step / total_steps) * 100)
                    
                    # Update progress
                    st.session_state.deployment_state.update({
                        'progress': progress,
                        'current_action': f"Creating milestone: {milestone_name}"
                    })
                    
                    # Add log entry
                    st.session_state.deployment_state['logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'icon': '🎯',
                        'message': f"{'[DRY RUN] ' if dry_run else ''}Creating milestone: {milestone_name}"
                    })
                    
                    if dry_run:
                        time.sleep(0.5)
                        milestone_num = 999
                    else:
                        from github_api import create_milestone
                        milestone_num = create_milestone(
                            title=milestone_name,
                            description=milestone_data.get('description', ''),
                            dry_run=False
                        )
                        time.sleep(1)
                    
                    st.session_state.deployment_state['created_milestones'] += 1
                    st.session_state.deployment_state['logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'icon': '✅',
                        'message': f"{'[DRY RUN] ' if dry_run else ''}Created milestone #{milestone_num}: {milestone_name}"
                    })
                    
                    # Process issues
                    for issue_index, issue in enumerate(milestone_data.get('issues', [])):
                        current_step += 1
                        progress = int((current_step / total_steps) * 100)
                        
                        issue_title = issue.get('title', f'Issue {issue_index + 1}')
                        short_title = issue_title[:40] + '...' if len(issue_title) > 40 else issue_title
                        
                        st.session_state.deployment_state.update({
                            'progress': progress,
                            'current_action': f"Creating issue: {short_title}"
                        })
                        
                        st.session_state.deployment_state['logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'icon': '📋',
                            'message': f"{'[DRY RUN] ' if dry_run else ''}Creating issue: {short_title}"
                        })
                        
                        if dry_run:
                            time.sleep(0.3)
                            issue_num = 999 + issue_index
                        else:
                            from github_api import create_issue
                            issue_result = create_issue(
                                title=issue_title,
                                body=issue.get('body', ''),
                                milestone=milestone_num,
                                labels=issue.get('labels', []),
                                assignees=issue.get('assignees', []),
                                dry_run=False
                            )
                            issue_num = issue_result.get('number', 'Unknown') if issue_result else 'Failed'
                            time.sleep(1)
                        
                        st.session_state.deployment_state['created_issues'] += 1
                        st.session_state.deployment_state['logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'icon': '✅',
                            'message': f"{'[DRY RUN] ' if dry_run else ''}Created issue #{issue_num}: {short_title}"
                        })
                
                # Deployment completed
                st.session_state.deployment_state.update({
                    'status': 'completed',
                    'progress': 100,
                    'current_action': '',
                    'end_time': datetime.now()
                })
                
                completion_msg = f"Deployment completed! Created {st.session_state.deployment_state['created_milestones']} milestones and {st.session_state.deployment_state['created_issues']} issues"
                st.session_state.deployment_state['logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'icon': '✅',
                    'message': f"{'[DRY RUN] ' if dry_run else ''}{completion_msg}"
                })
                
                st.rerun()
                
            except Exception as e:
                st.session_state.deployment_state.update({
                    'status': 'error',
                    'end_time': datetime.now()
                })
                st.session_state.deployment_state['errors'].append(str(e))
                st.session_state.deployment_state['logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'icon': '❌',
                    'message': f"Deployment failed: {str(e)}"
                })
                st.rerun()

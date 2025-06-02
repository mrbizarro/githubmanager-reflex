import streamlit as st
import time
import json
from typing import Dict, List, Any, Optional, Callable
from github_api import create_milestone, create_issue, GitHubError, verify_repository_access, OWNER, REPO
from datetime import datetime
import threading
import queue

class DeploymentManager:
    """Enhanced deployment manager with real-time progress tracking and user feedback."""
    
    def __init__(self):
        self.is_running = False
        self.current_step = 0
        self.total_steps = 0
        self.progress_queue = queue.Queue()
        self.deployment_thread = None
        
    def calculate_total_steps(self, projects: Dict[str, Any]) -> int:
        """Calculate total deployment steps (milestones + issues)."""
        milestones = len(projects)
        issues = sum(len(proj_data.get('issues', [])) for proj_data in projects.values())
        return milestones + issues
    
    def deploy_with_progress(self, projects: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """
        Deploy projects with real-time progress tracking.
        
        Args:
            projects: Dictionary of project data to deploy
            dry_run: Whether to simulate deployment without making changes
            
        Returns:
            Dictionary with deployment results
        """
        if self.is_running:
            return {"error": "Deployment already in progress"}
        
        self.is_running = True
        self.current_step = 0
        self.total_steps = self.calculate_total_steps(projects)
        
        # Initialize session state for tracking
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
        
        # Reset state
        st.session_state.deployment_state.update({
            'status': 'running',
            'progress': 0,
            'current_action': 'Initializing deployment...',
            'logs': [self._create_log_entry('info', 'Deployment started', dry_run)],
            'errors': [],
            'created_milestones': 0,
            'created_issues': 0,
            'start_time': datetime.now(),
            'end_time': None
        })
        
        try:
            return self._execute_deployment(projects, dry_run)
        except Exception as e:
            self.is_running = False
            st.session_state.deployment_state['status'] = 'error'
            st.session_state.deployment_state['errors'].append(str(e))
            return {"error": str(e)}
    
    def _create_log_entry(self, level: str, message: str, dry_run: bool = False) -> Dict[str, Any]:
        """Create a standardized log entry."""
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'milestone': '🎯',
            'issue': '📋'
        }
        
        prefix = "[DRY RUN] " if dry_run else ""
        
        return {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': level,
            'icon': icons.get(level, 'ℹ️'),
            'message': f"{prefix}{message}"
        }
    
    def _update_progress(self, action: str, dry_run: bool = False):
        """Update deployment progress and state."""
        self.current_step += 1
        progress_percent = min(100, int((self.current_step / self.total_steps) * 100))
        
        st.session_state.deployment_state.update({
            'progress': progress_percent,
            'current_action': action
        })
    
    def _execute_deployment(self, projects: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Execute the actual deployment process."""
        results = {
            'total_milestones': 0,
            'total_issues': 0,
            'created_milestones': 0,
            'created_issues': 0,
            'errors': [],
            'milestone_mapping': {}
        }
        
        try:
            # Verify repository access
            self._update_progress("Verifying repository access...", dry_run)
            st.session_state.deployment_state['logs'].append(
                self._create_log_entry('info', 'Verifying repository access...', dry_run)
            )
            
            if not dry_run:
                access_ok, message, _ = verify_repository_access()
                if not access_ok:
                    raise GitHubError(f"Repository access failed: {message}")
            
            st.session_state.deployment_state['logs'].append(
                self._create_log_entry('success', 'Repository access verified', dry_run)
            )
            
            # Process each milestone and its issues
            for milestone_name, milestone_data in projects.items():
                try:
                    # Create milestone
                    self._update_progress(f"Creating milestone: {milestone_name}", dry_run)
                    st.session_state.deployment_state['logs'].append(
                        self._create_log_entry('milestone', f"Creating milestone: {milestone_name}", dry_run)
                    )
                    
                    milestone_num = None
                    if dry_run:
                        # Simulate API delay
                        time.sleep(0.5)
                        milestone_num = 999  # Fake number for dry run
                    else:
                        milestone_num = create_milestone(
                            title=milestone_name,
                            description=milestone_data.get('description', ''),
                            dry_run=False
                        )
                        time.sleep(1)  # Rate limiting
                    
                    results['created_milestones'] += 1
                    results['milestone_mapping'][milestone_name] = milestone_num
                    st.session_state.deployment_state['created_milestones'] += 1
                    
                    success_msg = f"Created milestone #{milestone_num}: {milestone_name}"
                    st.session_state.deployment_state['logs'].append(
                        self._create_log_entry('success', success_msg, dry_run)
                    )
                    
                    # Process issues for this milestone
                    issues = milestone_data.get('issues', [])
                    for issue_index, issue in enumerate(issues):
                        issue_title = issue.get('title', f'Issue {issue_index + 1}')
                        short_title = issue_title[:50] + '...' if len(issue_title) > 50 else issue_title
                        
                        self._update_progress(f"Creating issue: {short_title}", dry_run)
                        st.session_state.deployment_state['logs'].append(
                            self._create_log_entry('issue', f"Creating issue: {short_title}", dry_run)
                        )
                        
                        try:
                            if dry_run:
                                time.sleep(0.3)
                                issue_result = {'number': 999 + issue_index}
                            else:
                                issue_result = create_issue(
                                    title=issue_title,
                                    body=issue.get('body', ''),
                                    milestone=milestone_num,
                                    labels=issue.get('labels', []),
                                    assignees=issue.get('assignees', []),
                                    dry_run=False
                                )
                                time.sleep(1)  # Rate limiting
                            
                            if issue_result:
                                issue_num = issue_result.get('number', 'Unknown')
                                results['created_issues'] += 1
                                st.session_state.deployment_state['created_issues'] += 1
                                
                                success_msg = f"Created issue #{issue_num}: {short_title}"
                                st.session_state.deployment_state['logs'].append(
                                    self._create_log_entry('success', success_msg, dry_run)
                                )
                            else:
                                error_msg = f"Issue creation returned None: {short_title}"
                                results['errors'].append(error_msg)
                                st.session_state.deployment_state['errors'].append(error_msg)
                                st.session_state.deployment_state['logs'].append(
                                    self._create_log_entry('error', error_msg, dry_run)
                                )
                        
                        except Exception as e:
                            error_msg = f"Failed to create issue '{short_title}': {str(e)}"
                            results['errors'].append(error_msg)
                            st.session_state.deployment_state['errors'].append(error_msg)
                            st.session_state.deployment_state['logs'].append(
                                self._create_log_entry('error', error_msg, dry_run)
                            )
                
                except Exception as e:
                    error_msg = f"Failed to create milestone '{milestone_name}': {str(e)}"
                    results['errors'].append(error_msg)
                    st.session_state.deployment_state['errors'].append(error_msg)
                    st.session_state.deployment_state['logs'].append(
                        self._create_log_entry('error', error_msg, dry_run)
                    )
            
            # Deployment completed
            st.session_state.deployment_state['status'] = 'completed'
            st.session_state.deployment_state['end_time'] = datetime.now()
            st.session_state.deployment_state['progress'] = 100
            
            completion_msg = f"Deployment completed! Created {results['created_milestones']} milestones and {results['created_issues']} issues"
            st.session_state.deployment_state['logs'].append(
                self._create_log_entry('success', completion_msg, dry_run)
            )
            
            if results['errors']:
                warning_msg = f"Completed with {len(results['errors'])} errors"
                st.session_state.deployment_state['logs'].append(
                    self._create_log_entry('warning', warning_msg, dry_run)
                )
            
            return results
        
        except Exception as e:
            st.session_state.deployment_state['status'] = 'error'
            st.session_state.deployment_state['end_time'] = datetime.now()
            error_msg = f"Deployment failed: {str(e)}"
            st.session_state.deployment_state['logs'].append(
                self._create_log_entry('error', error_msg, dry_run)
            )
            raise
        
        finally:
            self.is_running = False

def render_deployment_progress():
    """Render the enhanced deployment progress UI."""
    if 'deployment_state' not in st.session_state:
        return
    
    state = st.session_state.deployment_state
    
    # Status indicator
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
        {('<div style="width: 16px; height: 16px; border: 2px solid #334155; border-top: 2px solid #6366f1; border-radius: 50%; animation: spin 1s linear infinite; margin-left: auto;"></div>' if state['status'] == 'running' else '')}
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
    
    # Deployment log
    if state['logs']:
        st.subheader("📜 Deployment Log")
        
        log_container = st.container()
        with log_container:
            # Create scrollable log area
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
                    <span>{log_entry['icon']}</span>
                    <span style="flex: 1;">{log_entry['message']}</span>
                    <span style="color: #64748b; font-size: 0.75rem;">{log_entry['timestamp']}</span>
                </div>
                """
            
            log_html += "</div>"
            st.markdown(log_html, unsafe_allow_html=True)
    
    # Error details
    if state['errors']:
        st.subheader("⚠️ Errors")
        for i, error in enumerate(state['errors'][-5:], 1):  # Show last 5 errors
            st.error(f"Error {i}: {error}")
    
    # Timing information
    if state['start_time']:
        duration = None
        if state['end_time']:
            duration = state['end_time'] - state['start_time']
        elif state['status'] == 'running':
            duration = datetime.now() - state['start_time']
        
        if duration:
            st.markdown(f"""
            <div style="
                text-align: center; 
                padding: 10px; 
                color: #64748b; 
                font-size: 0.9rem;
            ">
                ⏱️ Duration: {str(duration).split('.')[0]}
            </div>
            """, unsafe_allow_html=True)

def create_enhanced_deployment_section(projects: Dict[str, Any], dry_run: bool, github_ok: bool):
    """Create an enhanced deployment section with progress tracking."""
    
    deployment_manager = DeploymentManager()
    
    # Calculate totals
    total_milestones = len(projects)
    total_issues = sum(len(proj_data.get('issues', [])) for proj_data in projects.values())
    
    st.markdown("---")
    st.markdown("## 🚀 Deploy to GitHub")
    
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
    
    # Pre-deployment summary
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        deploy_button = st.button(
            f"🚀 Deploy {total_milestones} milestones & {total_issues} issues",
            disabled=not github_ok and not dry_run,
            type="primary",
            key="enhanced_deploy"
        )
    
    with col2:
        if st.button("🔄 Reset Progress", key="reset_progress"):
            if 'deployment_state' in st.session_state:
                del st.session_state.deployment_state
            st.rerun()
    
    with col3:
        st.download_button(
            "💾 Export JSON",
            data=json.dumps(projects, indent=2),
            file_name="github_export.json",
            mime="application/json"
        )
    
    # Render current deployment state
    render_deployment_progress()
    
    # Handle deployment
    if deploy_button:
        if deployment_manager.is_running:
            st.warning("⚠️ Deployment already in progress!")
        else:
            try:
                with st.spinner("Starting deployment..."):
                    results = deployment_manager.deploy_with_progress(projects, dry_run)
                
                if "error" in results:
                    st.error(f"❌ Deployment failed: {results['error']}")
                else:
                    if dry_run:
                        st.success(f"""
                        🧪 **DRY RUN COMPLETED**
                        
                        Would create:
                        - {results['created_milestones']} milestones
                        - {results['created_issues']} issues
                        - {len(results['errors'])} errors encountered
                        
                        To deploy for real, uncheck 'Dry run mode' and click deploy again.
                        """)
                    else:
                        st.success(f"""
                        ✅ **LIVE DEPLOYMENT COMPLETED!**
                        
                        Created in your repository:
                        - {results['created_milestones']} milestones
                        - {results['created_issues']} issues
                        - {len(results['errors'])} errors encountered
                        
                        🔗 **[Check your GitHub repository](https://github.com/{OWNER}/{REPO}/issues)**
                        """)
                
                # Auto-refresh to show updated progress
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ **DEPLOYMENT FAILED**: {str(e)}")
                st.exception(e)

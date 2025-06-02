"""
Manual Entry page - create milestones and issues manually
"""

import streamlit as st
import json
from datetime import datetime

from utils.session import add_deployment_log, update_deployment_state, reset_deployment_state
from config.settings import get_config

def render_manual_page():
    """Render the manual entry page"""
    
    # Initialize manual milestones if not exists
    if 'manual_milestones' not in st.session_state:
        st.session_state.manual_milestones = {}
    
    # Create milestone section
    render_create_milestone_section()
    
    st.markdown('<div class="modern-separator"></div>', unsafe_allow_html=True)
    
    # Add issue section (only if milestones exist)
    if st.session_state.manual_milestones:
        render_add_issue_section()
        
        st.markdown('<div class="modern-separator"></div>', unsafe_allow_html=True)
        
        # Preview section
        render_preview_section()
        
        st.markdown('<div class="modern-separator"></div>', unsafe_allow_html=True)
        
        # Deploy section
        render_deploy_section()
    else:
        render_getting_started()

def render_create_milestone_section():
    """Render milestone creation form"""
    
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <h2 class="card-title">✍️ Manual Entry</h2>
            <p class="card-description">Create milestones and issues manually for precise control</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("➕ Create New Milestone", expanded=True):
        
        # Milestone form
        col1, col2 = st.columns([2, 1])
        
        with col1:
            milestone_title = st.text_input(
                "🎯 Milestone Title",
                placeholder="Enter milestone name",
                help="A descriptive name for your milestone",
                key="new_milestone_title"
            )
            
            milestone_desc = st.text_area(
                "📝 Milestone Description",
                placeholder="Describe the goals and scope of this milestone",
                help="Detailed description of what this milestone represents",
                height=100,
                key="new_milestone_desc"
            )
        
        with col2:
            st.markdown("#### Quick Actions")
            
            # Due date (optional)
            due_date = st.date_input(
                "📅 Due Date (Optional)",
                value=None,
                help="Set a target completion date",
                key="milestone_due_date"
            )
            
            # State
            milestone_state = st.selectbox(
                "State",
                ["open", "closed"],
                index=0,
                help="Initial state of the milestone",
                key="milestone_state"
            )
        
        # Add milestone button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button(
                "➕ Add Milestone",
                type="primary",
                use_container_width=True,
                key="add_milestone_btn"
            ):
                if milestone_title.strip():
                    # Check for duplicates
                    if milestone_title in st.session_state.manual_milestones:
                        st.error(f"❌ Milestone '{milestone_title}' already exists!")
                    else:
                        # Add milestone
                        st.session_state.manual_milestones[milestone_title] = {
                            'description': milestone_desc,
                            'due_date': due_date.isoformat() if due_date else None,
                            'state': milestone_state,
                            'issues': [],
                            'created_at': datetime.now().isoformat()
                        }
                        
                        st.success(f"✅ Added milestone: {milestone_title}")
                        
                        # Clear form
                        st.session_state.new_milestone_title = ""
                        st.session_state.new_milestone_desc = ""
                        st.rerun()
                else:
                    st.error("❌ Please enter a milestone title")

def render_add_issue_section():
    """Render issue creation form"""
    
    with st.expander("📋 Add Issue", expanded=True):
        
        # Select milestone
        milestone_options = list(st.session_state.manual_milestones.keys())
        selected_milestone = st.selectbox(
            "🎯 Select Milestone",
            milestone_options,
            help="Choose which milestone this issue belongs to",
            key="selected_milestone"
        )
        
        # Issue form
        col1, col2 = st.columns([2, 1])
        
        with col1:
            issue_title = st.text_input(
                "📋 Issue Title",
                placeholder="Enter issue title",
                help="A clear, descriptive title for the issue",
                key="new_issue_title"
            )
            
            issue_body = st.text_area(
                "📝 Issue Description",
                placeholder="Describe the issue in detail...",
                help="Detailed description, requirements, and acceptance criteria",
                height=120,
                key="new_issue_body"
            )
        
        with col2:
            issue_labels = st.text_input(
                "🏷️ Labels",
                placeholder="bug, feature, enhancement",
                help="Comma-separated labels",
                key="new_issue_labels"
            )
            
            issue_assignees = st.text_input(
                "👤 Assignees",
                placeholder="username1, username2",
                help="Comma-separated GitHub usernames",
                key="new_issue_assignees"
            )
            
            issue_priority = st.selectbox(
                "⚡ Priority",
                ["low", "normal", "high", "critical"],
                index=1,
                help="Issue priority level",
                key="issue_priority"
            )
        
        # Add issue button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button(
                "➕ Add Issue",
                type="primary",
                use_container_width=True,
                key="add_issue_btn"
            ):
                if issue_title.strip() and selected_milestone:
                    # Process labels and assignees
                    labels = [l.strip() for l in issue_labels.split(',') if l.strip()]
                    assignees = [a.strip() for a in issue_assignees.split(',') if a.strip()]
                    
                    # Add priority label
                    if issue_priority != 'normal':
                        labels.append(f'priority-{issue_priority}')
                    
                    # Create issue
                    new_issue = {
                        'title': issue_title,
                        'body': issue_body,
                        'labels': labels,
                        'assignees': assignees,
                        'priority': issue_priority,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    # Add to milestone
                    st.session_state.manual_milestones[selected_milestone]['issues'].append(new_issue)
                    
                    st.success(f"✅ Added issue '{issue_title}' to {selected_milestone}")
                    
                    # Clear form
                    st.session_state.new_issue_title = ""
                    st.session_state.new_issue_body = ""
                    st.session_state.new_issue_labels = ""
                    st.session_state.new_issue_assignees = ""
                    st.rerun()
                else:
                    st.error("❌ Please enter an issue title and select a milestone")

def render_preview_section():
    """Render preview of manual entries"""
    
    milestones = st.session_state.manual_milestones
    total_milestones = len(milestones)
    total_issues = sum(len(m['issues']) for m in milestones.values())
    
    st.markdown("### 👀 Preview")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Milestones", total_milestones, "🎯")
    
    with col2:
        render_metric_card("Issues", total_issues, "📋")
    
    with col3:
        avg_issues = round(total_issues / total_milestones, 1) if total_milestones > 0 else 0
        render_metric_card("Avg Issues/Milestone", avg_issues, "📊")
    
    with col4:
        render_metric_card("Entry Mode", "Manual", "✍️")
    
    # Preview controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        view_mode = st.radio(
            "View Mode",
            ["Compact", "Detailed"],
            horizontal=True,
            key="preview_mode"
        )
    
    with col2:
        if st.button("🔄 Refresh", key="refresh_preview"):
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear All", key="clear_all_manual"):
            st.session_state.manual_milestones = {}
            st.success("All manual entries cleared!")
            st.rerun()
    
    # Milestone previews
    if view_mode == "Compact":
        render_compact_preview(milestones)
    else:
        render_detailed_preview(milestones)

def render_compact_preview(milestones):
    """Render compact preview of milestones"""
    
    for milestone_name, milestone_data in milestones.items():
        issues_count = len(milestone_data['issues'])
        
        with st.expander(f"🎯 {milestone_name} ({issues_count} issues)", expanded=False):
            
            # Milestone info
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Description:** {milestone_data.get('description', 'No description')}")
                
                # Issue list
                if milestone_data['issues']:
                    st.markdown("**Issues:**")
                    for i, issue in enumerate(milestone_data['issues'], 1):
                        priority_icon = get_priority_icon(issue.get('priority', 'normal'))
                        st.markdown(f"{i}. {priority_icon} {issue['title']}")
                else:
                    st.info("No issues yet")
            
            with col2:
                # Milestone metadata
                due_date = milestone_data.get('due_date')
                if due_date:
                    st.markdown(f"**Due:** {due_date}")
                
                st.markdown(f"**State:** {milestone_data.get('state', 'open').title()}")
                
                # Action buttons
                if st.button(f"✏️ Edit", key=f"edit_{milestone_name}"):
                    st.session_state[f'editing_{milestone_name}'] = True
                    st.rerun()
                
                if st.button(f"🗑️ Delete", key=f"delete_{milestone_name}"):
                    del st.session_state.manual_milestones[milestone_name]
                    st.success(f"Deleted milestone: {milestone_name}")
                    st.rerun()

def render_detailed_preview(milestones):
    """Render detailed preview of milestones"""
    
    for milestone_name, milestone_data in milestones.items():
        
        st.markdown(f"#### 🎯 {milestone_name}")
        
        # Milestone details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Description:** {milestone_data.get('description', 'No description')}")
            
            due_date = milestone_data.get('due_date')
            if due_date:
                st.markdown(f"**Due Date:** {due_date}")
            
            st.markdown(f"**State:** {milestone_data.get('state', 'open').title()}")
        
        with col2:
            created_at = milestone_data.get('created_at', '')
            if created_at:
                st.markdown(f"**Created:** {created_at[:10]}")
            
            issues_count = len(milestone_data['issues'])
            st.markdown(f"**Issues:** {issues_count}")
        
        # Issues
        if milestone_data['issues']:
            st.markdown("**Issues:**")
            
            for i, issue in enumerate(milestone_data['issues'], 1):
                priority_icon = get_priority_icon(issue.get('priority', 'normal'))
                
                with st.container():
                    st.markdown(f"**{i}. {priority_icon} {issue['title']}**")
                    
                    if issue.get('body'):
                        st.markdown(f"*{issue['body'][:100]}{'...' if len(issue['body']) > 100 else ''}*")
                    
                    # Labels and assignees
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if issue.get('labels'):
                            labels_html = ' '.join([f'<span class="modern-badge">{label}</span>' for label in issue['labels']])
                            st.markdown(f"Labels: {labels_html}", unsafe_allow_html=True)
                    
                    with col2:
                        if issue.get('assignees'):
                            st.markdown(f"Assignees: {', '.join(issue['assignees'])}")
                    
                    if i < len(milestone_data['issues']):
                        st.markdown("---")
        else:
            st.info("No issues yet")
        
        st.markdown('<div class="modern-separator"></div>', unsafe_allow_html=True)

def render_deploy_section():
    """Render deployment section for manual entries"""
    
    milestones = st.session_state.manual_milestones
    total_milestones = len(milestones)
    total_issues = sum(len(m['issues']) for m in milestones.values())
    
    st.markdown("### 🚀 Deploy Manual Entries")
    
    # Deployment status check
    github_ok = get_config('github_connected', False)
    
    if not github_ok:
        render_alert(
            type="error",
            title="GitHub Configuration Required",
            description="Please configure your GitHub settings before deploying"
        )
        return
    
    render_alert(
        type="success",
        title="Ready for Deployment",
        description="All manual entries will be created in your GitHub repository"
    )
    
    # Deployment options
    col1, col2 = st.columns(2)
    
    with col1:
        dry_run = st.checkbox(
            "🧪 Dry Run Mode",
            value=False,
            help="Preview deployment without making actual changes",
            key="manual_dry_run"
        )
    
    with col2:
        create_labels = st.checkbox(
            "🏷️ Auto-create Labels",
            value=True,
            help="Automatically create missing labels with colors",
            key="manual_create_labels"
        )
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        export_data = json.dumps(milestones, indent=2)
        st.download_button(
            "💾 Export JSON",
            data=export_data,
            file_name="manual_entries.json",
            mime="application/json",
            key="export_manual"
        )
    
    with col2:
        deploy_disabled = (
            total_milestones == 0 or 
            st.session_state.get('deployment_state', {}).get('status') == 'running'
        )
        
        button_text = f"🚀 {'Test Deploy' if dry_run else 'Deploy'} {total_milestones} milestones & {total_issues} issues"
        
        if st.button(
            button_text,
            type="primary",
            disabled=deploy_disabled,
            use_container_width=True,
            key="deploy_manual"
        ):
            deploy_manual_entries(dry_run, create_labels)
    
    with col3:
        if st.button("🗑️ Clear All", key="clear_deploy"):
            st.session_state.manual_milestones = {}
            st.success("All entries cleared!")
            st.rerun()

def render_getting_started():
    """Render getting started guide when no milestones exist"""
    
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <h3 class="card-title">🚀 Getting Started with Manual Entry</h3>
            <p class="card-description">Create your first milestone to begin organizing your project</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        #### Quick Start Guide
        
        1. **Create a Milestone** ⬆️
           - Enter a descriptive title
           - Add a detailed description
           - Set an optional due date
        
        2. **Add Issues**
           - Create tasks for your milestone
           - Add labels for organization
           - Assign team members
        
        3. **Review & Deploy**
           - Preview your structure
           - Export or deploy to GitHub
        
        ---
        
        **Tips:**
        - Use clear, descriptive titles
        - Add priority labels (high, critical)
        - Assign specific team members
        - Group related issues in milestones
        """)

def render_metric_card(title, value, icon):
    """Render a metric card component"""
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <div class="metric-content">
                <p class="metric-label">{title}</p>
                <h3 class="metric-value">{value}</h3>
            </div>
            <div class="metric-icon">
                <span style="font-size: 1.25rem;">{icon}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_alert(type, title, description):
    """Render alert component"""
    
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

def get_priority_icon(priority):
    """Get icon for issue priority"""
    
    priority_icons = {
        'low': '🟢',
        'normal': '🔵',
        'high': '🟡',
        'critical': '🔴'
    }
    
    return priority_icons.get(priority, '🔵')

def deploy_manual_entries(dry_run=False, create_labels=True):
    """Deploy manual entries to GitHub"""
    
    milestones = st.session_state.manual_milestones
    
    if not milestones:
        st.error("No milestones to deploy")
        return
    
    # Reset deployment state
    reset_deployment_state()
    
    # Initialize deployment
    update_deployment_state(
        status='running',
        progress=0,
        current_action=f'{"Testing" if dry_run else "Starting"} deployment...',
        start_time=datetime.now()
    )
    
    action_text = "Testing deployment" if dry_run else "Deployment started"
    add_deployment_log('ℹ️', action_text)
    
    # Simulate deployment process
    simulate_manual_deployment(milestones, dry_run, create_labels)

def simulate_manual_deployment(milestones, dry_run, create_labels):
    """Deploy manual entries using real GitHub API"""
    
    import time
    
    total_milestones = len(milestones)
    total_issues = sum(len(m['issues']) for m in milestones.values())
    total_steps = total_milestones + total_issues
    current_step = 0
    
    try:
        if not dry_run:
            # Import real GitHub API functions
            from utils.github_api import GitHubAPI, GitHubAPIError
            
            # Initialize GitHub API
            api = GitHubAPI()
        
        for milestone_name, milestone_data in milestones.items():
            current_step += 1
            progress = int((current_step / total_steps) * 100)
            
            # Update progress
            action = f"{'Testing' if dry_run else 'Creating'} milestone: {milestone_name}"
            update_deployment_state(
                progress=progress,
                current_action=action
            )
            
            add_deployment_log('🎯', action)
            
            if dry_run:
                # Simulate delay for dry run
                time.sleep(1)
                milestone_number = 999  # Mock number for dry run
            else:
                # Create milestone using real API
                try:
                    milestone_response = api.create_milestone(
                        title=milestone_name,
                        description=milestone_data.get('description', ''),
                        state=milestone_data.get('state', 'open'),
                        due_date=milestone_data.get('due_date')
                    )
                    
                    milestone_number = milestone_response['number']
                    
                    # Add delay to avoid rate limiting
                    time.sleep(0.5)
                    
                except GitHubAPIError as e:
                    error_msg = f"Failed to create milestone '{milestone_name}': {str(e)}"
                    st.session_state.deployment_state['errors'].append(error_msg)
                    add_deployment_log('❌', error_msg)
                    continue
            
            # Update counts
            if not dry_run:
                update_deployment_state(
                    created_milestones=st.session_state.deployment_state['created_milestones'] + 1
                )
            
            success_msg = f"{'Would create' if dry_run else 'Created'} milestone #{milestone_number}: {milestone_name}"
            add_deployment_log('✅', success_msg)
            
            # Process issues for this milestone
            for issue in milestone_data.get('issues', []):
                current_step += 1
                progress = int((current_step / total_steps) * 100)
                
                issue_title = issue['title']
                short_title = issue_title[:40] + '...' if len(issue_title) > 40 else issue_title
                
                action = f"{'Testing' if dry_run else 'Creating'} issue: {short_title}"
                update_deployment_state(
                    progress=progress,
                    current_action=action
                )
                
                add_deployment_log('📋', action)
                
                if dry_run:
                    # Simulate delay for dry run
                    time.sleep(1)
                    issue_number = 999  # Mock number for dry run
                else:
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
                        
                    except GitHubAPIError as e:
                        error_msg = f"Failed to create issue '{issue_title}': {str(e)}"
                        st.session_state.deployment_state['errors'].append(error_msg)
                        add_deployment_log('❌', error_msg)
                        continue
                
                # Update counts
                if not dry_run:
                    update_deployment_state(
                        created_issues=st.session_state.deployment_state['created_issues'] + 1
                    )
                
                success_msg = f"{'Would create' if dry_run else 'Created'} issue #{issue_number}: {short_title}"
                add_deployment_log('✅', success_msg)
        
        # Deployment completed
        update_deployment_state(
            status='completed',
            progress=100,
            current_action='',
            end_time=datetime.now()
        )
        
        completion_msg = f"{'Test completed' if dry_run else 'Deployment completed'}! {'Would create' if dry_run else 'Created'} {total_milestones} milestones and {total_issues} issues"
        add_deployment_log('✅', completion_msg)
        
        success_msg = f"🚀 {'Test deployment' if dry_run else 'Deployment'} completed successfully!"
        st.success(success_msg)
        st.rerun()
        
    except Exception as e:
        update_deployment_state(
            status='error',
            end_time=datetime.now()
        )
        
        error_msg = f"{'Test' if dry_run else 'Deployment'} failed: {str(e)}"
        st.session_state.deployment_state['errors'].append(error_msg)
        add_deployment_log('❌', error_msg)
        
        st.error(f"❌ {'Test' if dry_run else 'Deployment'} failed: {str(e)}")
        st.rerun()

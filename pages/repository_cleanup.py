"""
Repository Cleanup page - manage existing issues and milestones
FIXED: Simplified label manager that actually works with GitHub API
"""

import streamlit as st
import json
from datetime import datetime
from urllib.parse import quote

from config.settings import get_config
from utils.session import get_session_state, set_session_state

# STANDARD GITHUB LABELS - These will be preserved
STANDARD_GITHUB_LABELS = {
    'bug',
    'documentation', 
    'duplicate',
    'enhancement',
    'good first issue',
    'help wanted',
    'invalid',
    'question',
    'wontfix'
}

def render_cleanup_page():
    """Render the repository cleanup page"""
    
    # Initialize cleanup state if not exists
    if 'cleanup_state' not in st.session_state:
        st.session_state.cleanup_state = {
            'loaded_issues': [],
            'loaded_milestones': [],
            'selected_items': [],
            'filter_state': 'all',
            'sort_by': 'created',
            'sort_direction': 'desc',
            'label_analysis': None,
            'all_labels': [],
            'standard_labels': [],
            'non_standard_labels': []
        }
    
    # Header
    render_cleanup_header()
    
    # Check GitHub connection
    github_ok = get_config('github_connected', False)
    
    if not github_ok:
        render_github_required_message()
        return
    
    # Show repository info if connected
    from config.settings import check_basic_config
    config = check_basic_config()
    if config['github_configured']:
        st.markdown(f"**Repository**: `{config['repo_owner']}/{config['repo_name']}`")
        st.markdown("---")
    
    # Main cleanup interface
    render_cleanup_tabs()

def render_cleanup_header():
    """Render cleanup page header"""
    
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <h2 class="card-title">🗑️ Repository Cleanup</h2>
            <p class="card-description">Manage existing issues and milestones in your repository</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Important notice
    render_alert(
        type="warning",
        title="Important Notice",
        description="GitHub API limitations: Issues will be closed (not deleted) to preserve project history. Milestones can be fully deleted."
    )

def render_github_required_message():
    """Render message when GitHub is not configured"""
    
    render_alert(
        type="error",
        title="GitHub Configuration Required",
        description="Please configure your GitHub settings to use cleanup features"
    )
    
    # Check what specifically is missing
    from config.settings import check_basic_config
    config = check_basic_config()
    
    st.markdown("""
    ### 🔧 Quick Setup
    
    1. Create a `.env` file in your project directory
    2. Add your GitHub configuration:
    
    ```
    GITHUB_TOKEN=your_github_personal_access_token
    REPO_OWNER=your_username_or_organization
    REPO_NAME=your_repository_name
    ```
    
    3. Restart the application
    
    **Need a GitHub Token?**
    1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
    2. Generate new token with `repo` scope
    3. Copy and paste it in your .env file
    
    **Current Configuration Status:**
    """)
    
    # Show current status
    token_status = "✅ Configured" if config['github_token'] else "❌ Missing"
    owner_status = "✅ Configured" if config['repo_owner'] else "❌ Missing"
    repo_status = "✅ Configured" if config['repo_name'] else "❌ Missing"
    
    st.markdown(f"""
    - **GitHub Token**: {token_status}
    - **Repository Owner**: {owner_status}
    - **Repository Name**: {repo_status}
    """)
    
    # Test connection button if configured
    if config['github_configured']:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔗 Test Connection", key="test_github_connection"):
                from config.settings import test_github_connection
                success, message = test_github_connection()
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()  # Refresh to show issues
                else:
                    st.error(f"❌ {message}")

def render_cleanup_tabs():
    """Render main cleanup tabs"""
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Issues",
        "🎯 Milestones", 
        "🔍 Search",
        "🏷️ Label Cleanup"
    ])
    
    with tab1:
        render_issues_tab()
    
    with tab2:
        render_milestones_tab()
    
    with tab3:
        render_search_tab()
    
    with tab4:
        render_labels_tab()

def render_issues_tab():
    """Render issues management tab"""
    
    st.markdown("### 📋 Issue Management")
    
    # Filter controls
    render_issue_filters()
    
    # Load issues section
    render_load_issues_section()
    
    # Issues list and management
    if st.session_state.cleanup_state['loaded_issues']:
        render_issues_list()

def render_issue_filters():
    """Render issue filter controls"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_state = st.selectbox(
            "State",
            ["all", "open", "closed"],
            index=["all", "open", "closed"].index(st.session_state.cleanup_state['filter_state']),
            key="issue_state_filter"
        )
        st.session_state.cleanup_state['filter_state'] = filter_state
    
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["created", "updated", "comments"],
            index=["created", "updated", "comments"].index(st.session_state.cleanup_state['sort_by']),
            key="issue_sort_filter"
        )
        st.session_state.cleanup_state['sort_by'] = sort_by
    
    with col3:
        sort_direction = st.selectbox(
            "Direction",
            ["desc", "asc"],
            index=["desc", "asc"].index(st.session_state.cleanup_state['sort_direction']),
            key="issue_direction_filter"
        )
        st.session_state.cleanup_state['sort_direction'] = sort_direction
    
    with col4:
        if st.button("🔄 Load Issues", type="primary", use_container_width=True):
            load_repository_issues()

def render_load_issues_section():
    """Render load issues section with results"""
    
    # Loading message
    if st.session_state.get('loading_issues', False):
        st.info("🔄 Loading issues from repository...")
        return
    
    # Results summary
    issues = st.session_state.cleanup_state['loaded_issues']
    if issues:
        render_alert(
            type="success",
            title=f"Found {len(issues)} issues",
            description=f"Loaded from repository with current filters"
        )

def render_issues_list():
    """Render list of loaded issues with selection"""
    
    issues = st.session_state.cleanup_state['loaded_issues']
    
    st.markdown("#### Select Issues to Close")
    
    # Select all checkbox
    select_all = st.checkbox("Select all issues", key="select_all_issues")
    
    # Issues container
    with st.container():
        st.markdown('<div class="scroll-area">', unsafe_allow_html=True)
        
        selected_count = 0
        
        for i, issue in enumerate(issues):
            # Issue checkbox and info
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            
            with col1:
                selected = st.checkbox(
                    "",
                    value=select_all,
                    key=f"issue_select_{i}",
                    label_visibility="collapsed"
                )
                if selected:
                    selected_count += 1
            
            with col2:
                # Issue info
                state_emoji = "🟢" if issue['state'] == 'open' else "🔴"
                title = issue['title'][:60] + "..." if len(issue['title']) > 60 else issue['title']
                
                st.markdown(f"**{state_emoji} #{issue['number']}: {title}**")
                st.markdown(f"*Created {issue['created_at']} by {issue['author']}*")
                
                # Labels
                if issue.get('labels'):
                    labels_html = ' '.join([
                        f'<span class="modern-badge" style="margin-right: 0.25rem;">{label}</span>' 
                        for label in issue['labels']
                    ])
                    st.markdown(f"Labels: {labels_html}", unsafe_allow_html=True)
            
            with col3:
                if st.button("👁️", key=f"view_issue_{i}", help="View issue details"):
                    st.session_state[f'show_issue_{i}'] = not st.session_state.get(f'show_issue_{i}', False)
            
            # Issue details (expandable)
            if st.session_state.get(f'show_issue_{i}', False):
                with st.expander("Issue Details", expanded=True):
                    st.markdown(f"**URL:** {issue['url']}")
                    st.markdown(f"**Body:** {issue['body'][:200]}{'...' if len(issue['body']) > 200 else ''}")
                    
                    if issue.get('assignees'):
                        st.markdown(f"**Assignees:** {', '.join(issue['assignees'])}")
                    
                    if issue.get('milestone'):
                        st.markdown(f"**Milestone:** {issue['milestone']}")
            
            if i < len(issues) - 1:
                st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        if selected_count > 0:
            st.markdown(f"**{selected_count} issues selected**")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("🧪 Preview Changes", key="preview_close_issues"):
                    st.info(f"Would close {selected_count} selected issues")
            
            with col2:
                if st.button(
                    f"❌ Close {selected_count} Selected Issues",
                    type="primary",
                    use_container_width=True,
                    key="close_selected_issues"
                ):
                    close_selected_issues(issues, select_all)
            
            with col3:
                if st.button("🔄 Refresh", key="refresh_issues"):
                    load_repository_issues()

def render_milestones_tab():
    """Render milestones management tab with bulk deletion"""
    
    st.markdown("### 🎯 Milestone Management")
    
    # Enhanced info about milestone deletion
    render_alert(
        type="info",
        title="Milestone Deletion Features",
        description="✅ Single milestone deletion  ✅ Bulk milestone deletion  ✅ Preview changes before deletion"
    )
    
    # Load milestones button
    if st.button("🔄 Load Milestones", type="primary"):
        load_repository_milestones()
    
    # Loading message
    if st.session_state.get('loading_milestones', False):
        st.info("🔄 Loading milestones from repository...")
        return
    
    # Milestones list
    milestones = st.session_state.cleanup_state.get('loaded_milestones', [])
    
    if milestones and len(milestones) > 0:
        render_alert(
            type="success",
            title=f"Found {len(milestones)} milestones",
            description="Select milestones below for bulk deletion or individual management"
        )
        
        render_milestones_list_with_bulk_selection(milestones)
    else:
        st.info("No milestones loaded. Click 'Load Milestones' to fetch from repository.")

def render_milestones_list_with_bulk_selection(milestones):
    """Render list of milestones with bulk selection and management options"""
    
    st.markdown("#### Select Milestones to Delete")
    
    # Select all checkbox
    select_all = st.checkbox("Select all milestones", key="select_all_milestones")
    
    # Milestones container
    with st.container():
        st.markdown('<div class="scroll-area">', unsafe_allow_html=True)
        
        selected_count = 0
        total_affected_issues = 0
        
        for i, milestone in enumerate(milestones):
            # Milestone checkbox and info
            col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
            
            with col1:
                selected = st.checkbox(
                    "",
                    value=select_all,
                    key=f"milestone_select_{i}",
                    label_visibility="collapsed"
                )
                if selected:
                    selected_count += 1
                    total_affected_issues += milestone.get('open_issues', 0) + milestone.get('closed_issues', 0)
            
            with col2:
                # Milestone info
                state_emoji = "🟢" if milestone['state'] == 'open' else "🔴"
                title = milestone['title'][:50] + "..." if len(milestone['title']) > 50 else milestone['title']
                
                st.markdown(f"**{state_emoji} 🎯 {title}**")
                st.markdown(f"*{milestone['description'] or 'No description'}*")
                st.markdown(f"*Created {milestone['created_at']}*")
                
                # Stats
                open_issues = milestone.get('open_issues', 0)
                closed_issues = milestone.get('closed_issues', 0)
                total_issues = open_issues + closed_issues
                
                stats_html = f"""
                <div style="display: flex; gap: 0.5rem; margin: 0.25rem 0;">
                    <span class="modern-badge badge-success" style="font-size: 0.75rem;">{open_issues} open</span>
                    <span class="modern-badge" style="font-size: 0.75rem;">{closed_issues} closed</span>
                    <span class="modern-badge badge-primary" style="font-size: 0.75rem;">#{milestone['number']}</span>
                </div>
                """
                st.markdown(stats_html, unsafe_allow_html=True)
                
                # Due date
                if milestone.get('due_date'):
                    st.markdown(f"**Due:** {milestone['due_date']}")
                
                # Completion percentage
                if total_issues > 0:
                    completion = (closed_issues / total_issues) * 100
                    progress_color = "#10b981" if completion >= 80 else "#f59e0b" if completion >= 50 else "#ef4444"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin: 0.25rem 0;">
                        <div style="width: 50px; height: 6px; background: #e5e7eb; border-radius: 3px; overflow: hidden;">
                            <div style="width: {completion}%; height: 100%; background: {progress_color};"></div>
                        </div>
                        <span style="font-size: 0.75rem; color: #6b7280;">{completion:.0f}%</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                # Action buttons
                if st.button("👁️", key=f"view_milestone_{i}", help="View milestone details"):
                    st.session_state[f'show_milestone_{i}'] = not st.session_state.get(f'show_milestone_{i}', False)
                
                if st.button("🗑️", key=f"delete_single_milestone_{i}", help="Delete this milestone", type="secondary"):
                    if st.session_state.get(f'confirm_delete_milestone_{i}', False):
                        delete_milestone(milestone)
                        st.success(f"Deleted milestone: {milestone['title']}")
                        st.rerun()
                    else:
                        st.session_state[f'confirm_delete_milestone_{i}'] = True
                        st.warning("Click again to confirm deletion")
                        st.rerun()
            
            # Milestone details (expandable)
            if st.session_state.get(f'show_milestone_{i}', False):
                with st.expander("Milestone Details", expanded=True):
                    st.markdown(f"**URL:** {milestone['url']}")
                    st.markdown(f"**State:** {milestone['state']}")
                    st.markdown(f"**Number:** #{milestone['number']}")
                    st.markdown(f"**Created:** {milestone['created_at']}")
                    
                    if milestone.get('updated_at'):
                        st.markdown(f"**Updated:** {milestone['updated_at']}")
                    
                    if milestone.get('due_date'):
                        st.markdown(f"**Due Date:** {milestone['due_date']}")
                    
                    # Issue stats details
                    if total_issues > 0:
                        completion = (closed_issues / total_issues) * 100
                        st.markdown(f"**Completion:** {completion:.1f}% ({closed_issues}/{total_issues} issues)")
            
            if i < len(milestones) - 1:
                st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bulk action buttons
        if selected_count > 0:
            st.markdown("---")
            st.markdown(f"### 🎯 Bulk Actions: {selected_count} milestones selected")
            
            # Summary of impact
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Selected Milestones", selected_count)
            
            with col2:
                st.metric("Affected Issues", total_affected_issues)
            
            with col3:
                open_count = sum(1 for i, m in enumerate(milestones) 
                               if (select_all or st.session_state.get(f'milestone_select_{i}', False)) 
                               and m['state'] == 'open')
                st.metric("Open Milestones", open_count)
            
            with col4:
                closed_count = selected_count - open_count
                st.metric("Closed Milestones", closed_count)
            
            # Warning about milestone deletion
            if total_affected_issues > 0:
                render_alert(
                    type="warning",
                    title="⚠️ Impact Warning",
                    description=f"Deleting these milestones will remove milestone assignment from {total_affected_issues} issues. This action cannot be undone."
                )
            else:
                render_alert(
                    type="info",
                    title="Safe Deletion",
                    description="These milestones have no associated issues and can be safely deleted."
                )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("🧪 Preview Deletion", key="preview_delete_milestones"):
                    preview_milestone_deletion(milestones, select_all, selected_count, total_affected_issues)
            
            with col2:
                if st.button(
                    f"🗑️ Delete {selected_count} Selected Milestones",
                    type="primary",
                    use_container_width=True,
                    key="delete_selected_milestones"
                ):
                    if st.session_state.get('confirm_bulk_milestone_deletion', False):
                        delete_selected_milestones(milestones, select_all)
                    else:
                        st.session_state['confirm_bulk_milestone_deletion'] = True
                        st.error("⚠️ DANGER: This will permanently delete milestones! Click again to confirm.")
                        st.rerun()
            
            with col3:
                if st.button("🔄 Refresh", key="refresh_milestones"):
                    st.session_state['confirm_bulk_milestone_deletion'] = False
                    load_repository_milestones()
        
        # Show empty state if no milestones
        elif len(milestones) == 0:
            st.info("🎯 No milestones found in this repository.")

def preview_milestone_deletion(milestones, select_all, selected_count, total_affected_issues):
    """Preview milestone deletion with detailed impact analysis"""
    
    st.markdown("---")
    st.markdown("### 🧪 Deletion Preview")
    
    render_alert(
        type="info",
        title=f"Preview: Would delete {selected_count} milestones",
        description=f"This would affect {total_affected_issues} issues across your repository"
    )
    
    # Show which milestones would be deleted
    with st.expander("📋 Milestones to be deleted:", expanded=True):
        for i, milestone in enumerate(milestones):
            if select_all or st.session_state.get(f'milestone_select_{i}', False):
                open_issues = milestone.get('open_issues', 0)
                closed_issues = milestone.get('closed_issues', 0)
                total_issues = open_issues + closed_issues
                
                state_indicator = "🟢 Open" if milestone['state'] == 'open' else "🔴 Closed"
                
                st.markdown(f"""
                **🎯 {milestone['title']}** (#{milestone['number']}) - {state_indicator}
                - Description: {milestone['description'] or 'No description'}
                - Issues: {open_issues} open, {closed_issues} closed ({total_issues} total)
                - Created: {milestone['created_at']}
                """)
        
        # Summary of impact
        if total_affected_issues > 0:
            st.markdown("---")
            st.markdown("### ⚠️ Impact Summary")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Issues that will lose milestone assignment:**
                - {total_affected_issues} total issues
                - These issues will remain open/closed but without milestone
                """)
            
            with col2:
                st.markdown(f"""
                **Recommended actions before deletion:**
                - Review affected issues
                - Consider reassigning to other milestones
                - Export milestone data if needed
                """)
        else:
            st.success("✅ **Safe deletion**: No issues will be affected")

def delete_selected_milestones(milestones, select_all):
    """Delete selected milestones using GitHub API with progress tracking"""
    
    try:
        # Import the GitHub API utility
        from utils.github_api import GitHubAPI, GitHubAPIError
        
        # Get selected milestone numbers
        selected_milestones = []
        if select_all:
            selected_milestones = [(m['number'], m['title']) for m in milestones]
        else:
            for i in range(len(milestones)):
                if st.session_state.get(f'milestone_select_{i}', False):
                    selected_milestones.append((milestones[i]['number'], milestones[i]['title']))
        
        if not selected_milestones:
            st.warning("⚠️ No milestones selected")
            return
        
        # Initialize API
        api = GitHubAPI()
        
        # Create progress placeholder and status tracking
        progress_container = st.container()
        
        with progress_container:
            # Progress bar
            progress_bar = st.progress(0, text=f"Starting deletion of {len(selected_milestones)} milestones...")
            
            # Status metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                success_metric = st.metric("Successful", 0)
            with col2:
                failed_metric = st.metric("Failed", 0)
            with col3:
                remaining_metric = st.metric("Remaining", len(selected_milestones))
        
        # Delete milestones one by one with progress updates
        successful = 0
        failed = 0
        errors = []
        
        for i, (milestone_number, milestone_title) in enumerate(selected_milestones):
            # Update progress
            progress = (i + 1) / len(selected_milestones)
            progress_bar.progress(progress, text=f"Deleting milestone {i+1}/{len(selected_milestones)}: {milestone_title}")
            
            try:
                success = api.delete_milestone(milestone_number)
                
                if success:
                    successful += 1
                    # Update success metric
                    with col1:
                        st.metric("Successful", successful)
                else:
                    failed += 1
                    errors.append(f"Failed to delete milestone '{milestone_title}' (#{milestone_number})")
                    with col2:
                        st.metric("Failed", failed)
                
                # Update remaining count
                remaining = len(selected_milestones) - (i + 1)
                with col3:
                    st.metric("Remaining", remaining)
                
                # Small delay to avoid rate limiting and allow UI updates
                import time
                time.sleep(0.5)
                
            except GitHubAPIError as e:
                failed += 1
                errors.append(f"API Error deleting '{milestone_title}': {str(e)}")
                with col2:
                    st.metric("Failed", failed)
            
            except Exception as e:
                failed += 1
                errors.append(f"Unexpected error deleting '{milestone_title}': {str(e)}")
                with col2:
                    st.metric("Failed", failed)
        
        # Final progress update
        progress_bar.progress(1.0, text="Deletion completed!")
        
        # Show final results
        st.markdown("---")
        st.markdown("### 📊 Deletion Results")
        
        if successful > 0:
            st.success(f"✅ Successfully deleted {successful} milestones")
        
        if failed > 0:
            st.error(f"❌ Failed to delete {failed} milestones")
            with st.expander("🔍 View error details", expanded=False):
                for error in errors:
                    st.text(f"• {error}")
        
        # Show completion summary
        total_processed = successful + failed
        if total_processed > 0:
            success_rate = (successful / total_processed) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Processed", total_processed)
            with col2:
                st.metric("Success Rate", f"{success_rate:.1f}%")
            with col3:
                if errors:
                    st.metric("Errors", len(errors))
                else:
                    st.metric("Errors", "0 🎉")
        
        # Reset confirmation state
        st.session_state['confirm_bulk_milestone_deletion'] = False
        
        # Auto-refresh milestones list after a delay
        import time
        time.sleep(2)
        load_repository_milestones()
        
    except Exception as e:
        st.error(f"❌ Unexpected error during bulk deletion: {str(e)}")
        st.session_state['confirm_bulk_milestone_deletion'] = False

def delete_milestone(milestone):
    """Delete single milestone using GitHub API"""
    
    try:
        # Import the GitHub API utility
        from utils.github_api import GitHubAPI, GitHubAPIError
        
        # Initialize API
        api = GitHubAPI()
        
        # Delete milestone
        success = api.delete_milestone(milestone['number'])
        
        if success:
            st.success(f"✅ Successfully deleted milestone: {milestone['title']}")
            # Remove from local state
            milestones = st.session_state.cleanup_state['loaded_milestones']
            st.session_state.cleanup_state['loaded_milestones'] = [m for m in milestones if m['number'] != milestone['number']]
        else:
            st.error(f"❌ Failed to delete milestone: {milestone['title']}")
        
    except GitHubAPIError as e:
        st.error(f"❌ GitHub API Error: {str(e)}")
        
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")

def render_search_tab():
    """Render advanced search tab"""
    
    st.markdown("### 🔍 Advanced Search")
    
    # Search form
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search Query",
            placeholder="label:bug is:open created:<2024-01-01",
            help="Use GitHub search syntax",
            key="search_query"
        )
    
    with col2:
        if st.button("🔍 Search", type="primary", use_container_width=True):
            perform_advanced_search(search_query)
    
    # Search examples
    with st.expander("📚 Search Examples", expanded=False):
        st.markdown("""
        **Common Search Patterns:**
        
        - `label:bug is:open` - Open issues with bug label
        - `is:open no:milestone` - Open issues without milestones
        - `updated:<2023-01-01` - Items not updated since 2023
        - `no:assignee is:open` - Unassigned open issues
        - `label:enhancement is:closed` - Closed enhancement requests
        - `created:<2024-01-01 is:issue` - Issues created before 2024
        - `author:username` - Items created by specific user
        - `involves:username` - Items involving specific user
        
        **Advanced Operators:**
        - `NOT`, `AND`, `OR` - Boolean operators
        - `created:>2024-01-01` - Created after date
        - `updated:2024-01-01..2024-12-31` - Updated in date range
        - `comments:>10` - More than 10 comments
        - `state:closed` - Closed items only
        """)
    
    # Search results
    if st.session_state.get('search_results'):
        render_search_results()

def render_search_results():
    """Render search results"""
    
    results = st.session_state.get('search_results', [])
    
    if results:
        st.markdown(f"#### 🔍 Search Results ({len(results)} items)")
        
        for i, item in enumerate(results):
            render_search_result_item(item, i)
    else:
        st.info("No results found for your search query.")

def render_search_result_item(item, index):
    """Render individual search result item"""
    
    item_type = "Issue" if item['type'] == 'issue' else "Pull Request"
    state_emoji = "🟢" if item['state'] == 'open' else "🔴"
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"**{state_emoji} {item_type} #{item['number']}: {item['title']}**")
            st.markdown(f"*Created {item['created_at']} by {item['author']}*")
            
            if item.get('labels'):
                labels_html = ' '.join([
                    f'<span class="modern-badge">{label}</span>' for label in item['labels']
                ])
                st.markdown(f"Labels: {labels_html}", unsafe_allow_html=True)
        
        with col2:
            if st.button("👁️ View", key=f"view_search_result_{index}"):
                st.markdown(f"**URL:** {item['url']}")
                if item.get('body'):
                    st.markdown(f"**Description:** {item['body'][:200]}...")
        
        if index < len(st.session_state.search_results) - 1:
            st.markdown("---")

def render_labels_tab():
    """Render SIMPLIFIED labels management tab"""
    
    st.markdown("### 🏷️ Label Cleanup - Remove Non-Standard Labels")
    
    # Simple explanation
    render_alert(
        type="info",
        title="Simple Label Cleanup",
        description="This will remove ALL non-standard GitHub labels, keeping only the 9 standard ones. Perfect for preparing your repository for a clean modern label setup."
    )
    
    # Standard labels info
    with st.expander("📋 Standard GitHub Labels (These will be kept)", expanded=False):
        standard_labels_list = ', '.join(sorted(STANDARD_GITHUB_LABELS))
        st.markdown(f"**Standard Labels:** {standard_labels_list}")
        st.markdown("""
        These are the default labels that GitHub provides in new repositories. 
        They are commonly used and will be preserved during cleanup.
        """)
    
    # Main action button
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔄 Load & Analyze Labels", type="primary", use_container_width=True):
            load_and_analyze_labels()
    
    with col2:
        if st.button("🎨 Setup Modern Labels After Cleanup", use_container_width=True, disabled=True):
            st.info("Clean up non-standard labels first, then this will become available")
    
    # Show analysis results if available
    if st.session_state.cleanup_state.get('label_analysis'):
        render_simple_label_analysis()

def load_and_analyze_labels():
    """Load labels from GitHub API and analyze them"""
    
    try:
        # Import the GitHub API utility
        from utils.github_api import GitHubAPI, GitHubAPIError
        
        # Initialize API
        api = GitHubAPI()
        
        # Create progress placeholder
        progress_placeholder = st.empty()
        
        def progress_callback(message):
            progress_placeholder.info(f"🔄 {message}")
        
        # Get ALL labels from repository with pagination
        all_labels = api.get_all_labels(progress_callback=progress_callback)
        
        # Clear progress placeholder
        progress_placeholder.empty()
        
        # Categorize labels
        standard_labels = []
        non_standard_labels = []
        
        for label in all_labels:
            label_name = label['name'].lower()
            if label_name in STANDARD_GITHUB_LABELS:
                standard_labels.append(label)
            else:
                non_standard_labels.append(label)
        
        # Store in session state
        st.session_state.cleanup_state['all_labels'] = all_labels
        st.session_state.cleanup_state['standard_labels'] = standard_labels
        st.session_state.cleanup_state['non_standard_labels'] = non_standard_labels
        st.session_state.cleanup_state['label_analysis'] = {
            'total_labels': len(all_labels),
            'standard_count': len(standard_labels),
            'non_standard_count': len(non_standard_labels)
        }
        
        # Show success message with better info
        if len(all_labels) > 100:
            st.success(f"✅ Loaded all {len(all_labels)} labels from repository (fetched across multiple pages)")
        else:
            st.success(f"✅ Loaded {len(all_labels)} labels from repository")
        st.rerun()
        
    except GitHubAPIError as e:
        st.error(f"❌ GitHub API Error: {str(e)}")
        
    except Exception as e:
        st.error(f"❌ Unexpected error loading labels: {str(e)}")

def render_simple_label_analysis():
    """Render simple label analysis with two categories"""
    
    analysis = st.session_state.cleanup_state['label_analysis']
    standard_labels = st.session_state.cleanup_state['standard_labels']
    non_standard_labels = st.session_state.cleanup_state['non_standard_labels']
    
    # Summary metrics
    st.markdown("#### 📊 Label Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Labels", analysis['total_labels'])
    
    with col2:
        st.metric("✅ Standard Labels", analysis['standard_count'])
    
    with col3:
        st.metric("🗑️ Non-Standard Labels", analysis['non_standard_count'])
    
    # Show the two categories
    st.markdown("---")
    
    # Standard labels (will be kept)
    if standard_labels:
        st.markdown("#### ✅ Standard Labels (These will be KEPT)")
        
        standard_html = ' '.join([
            f'<span class="modern-badge badge-success" style="margin: 0.125rem;">{label["name"]}</span>'
            for label in standard_labels
        ])
        st.markdown(standard_html, unsafe_allow_html=True)
        
        render_alert(
            type="success",
            title="Safe Labels",
            description=f"These {len(standard_labels)} standard GitHub labels will be preserved."
        )
    
    # Non-standard labels (will be deleted)
    if non_standard_labels:
        st.markdown("#### 🗑️ Non-Standard Labels (These will be DELETED)")
        
        # Show first 20 labels, with "show more" if needed
        display_count = min(20, len(non_standard_labels))
        displayed_labels = non_standard_labels[:display_count]
        
        non_standard_html = ' '.join([
            f'<span class="modern-badge badge-destructive" style="margin: 0.125rem;">{label["name"]}</span>'
            for label in displayed_labels
        ])
        st.markdown(non_standard_html, unsafe_allow_html=True)
        
        if len(non_standard_labels) > 20:
            st.markdown(f"*... and {len(non_standard_labels) - 20} more labels*")
        
        # Warning and action buttons
        render_alert(
            type="warning",
            title="⚠️ Deletion Warning",
            description=f"This will permanently delete {len(non_standard_labels)} non-standard labels. This action cannot be undone!"
        )
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("🧪 Preview Deletion", key="preview_label_cleanup"):
                preview_label_cleanup()
        
        with col2:
            if st.button(
                f"🗑️ DELETE {len(non_standard_labels)} Non-Standard Labels",
                type="primary",
                use_container_width=True,
                key="delete_non_standard_labels"
            ):
                if st.session_state.get('confirm_label_cleanup', False):
                    delete_non_standard_labels()
                else:
                    st.session_state['confirm_label_cleanup'] = True
                    st.error("⚠️ FINAL WARNING: This will permanently delete labels! Click again to confirm.")
                    st.rerun()
        
        with col3:
            if st.button("🔄 Refresh", key="refresh_label_analysis"):
                st.session_state['confirm_label_cleanup'] = False
                load_and_analyze_labels()
    
    else:
        render_alert(
            type="success",
            title="🎉 Repository Already Clean!",
            description="Your repository only has standard GitHub labels. Ready for modern label setup!"
        )

def preview_label_cleanup():
    """Preview what the label cleanup will do"""
    
    non_standard_labels = st.session_state.cleanup_state['non_standard_labels']
    
    st.markdown("---")
    st.markdown("### 🧪 Label Cleanup Preview")
    
    render_alert(
        type="info",
        title=f"Would delete {len(non_standard_labels)} non-standard labels",
        description="All labels that are not part of GitHub's standard 9 labels will be removed"
    )
    
    # Show all labels that would be deleted
    with st.expander(f"📋 {len(non_standard_labels)} labels to be deleted:", expanded=True):
        for label in non_standard_labels:
            color = label.get('color', '000000')
            description = label.get('description', 'No description')
            
            st.markdown(f"""
            **🗑️ {label['name']}**
            - Color: #{color}
            - Description: {description}
            """)
    
    st.markdown("### ✅ After Cleanup")
    st.markdown("Your repository will have only the standard GitHub labels, making it ready for a clean modern label setup.")

def delete_non_standard_labels():
    """Delete all non-standard labels using GitHub API"""
    
    try:
        # Import the GitHub API utility
        from utils.github_api import GitHubAPI, GitHubAPIError
        
        non_standard_labels = st.session_state.cleanup_state['non_standard_labels']
        
        if not non_standard_labels:
            st.warning("⚠️ No non-standard labels to delete")
            return
        
        # Initialize API
        api = GitHubAPI()
        
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            # Progress bar
            progress_bar = st.progress(0, text=f"Starting deletion of {len(non_standard_labels)} labels...")
            
            # Status metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                success_metric = st.metric("Successful", 0)
            with col2:
                failed_metric = st.metric("Failed", 0)
            with col3:
                remaining_metric = st.metric("Remaining", len(non_standard_labels))
        
        # Delete labels one by one with progress updates
        successful = 0
        failed = 0
        errors = []
        
        for i, label in enumerate(non_standard_labels):
            label_name = label['name']
            
            # Update progress
            progress = (i + 1) / len(non_standard_labels)
            progress_bar.progress(progress, text=f"Deleting label {i+1}/{len(non_standard_labels)}: {label_name}")
            
            try:
                # URL encode the label name for safety
                encoded_name = quote(label_name)
                success = api.delete_label(encoded_name)
                
                if success:
                    successful += 1
                    with col1:
                        st.metric("Successful", successful)
                else:
                    failed += 1
                    errors.append(f"Failed to delete label '{label_name}'")
                    with col2:
                        st.metric("Failed", failed)
                
                # Update remaining count
                remaining = len(non_standard_labels) - (i + 1)
                with col3:
                    st.metric("Remaining", remaining)
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.3)
                
            except GitHubAPIError as e:
                failed += 1
                errors.append(f"API Error deleting '{label_name}': {str(e)}")
                with col2:
                    st.metric("Failed", failed)
            
            except Exception as e:
                failed += 1
                errors.append(f"Unexpected error deleting '{label_name}': {str(e)}")
                with col2:
                    st.metric("Failed", failed)
        
        # Final progress update
        progress_bar.progress(1.0, text="Label cleanup completed!")
        
        # Show final results
        st.markdown("---")
        st.markdown("### 🎉 Label Cleanup Results")
        
        if successful > 0:
            st.success(f"✅ Successfully deleted {successful} non-standard labels")
        
        if failed > 0:
            st.error(f"❌ Failed to delete {failed} labels")
            with st.expander("🔍 View error details", expanded=False):
                for error in errors:
                    st.text(f"• {error}")
        
        # Show completion summary
        total_processed = successful + failed
        if total_processed > 0:
            success_rate = (successful / total_processed) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Processed", total_processed)
            with col2:
                st.metric("Success Rate", f"{success_rate:.1f}%")
            with col3:
                if errors:
                    st.metric("Errors", len(errors))
                else:
                    st.metric("Errors", "0 🎉")
        
        # Show next steps
        if successful > 0:
            render_alert(
                type="success",
                title="🎉 Repository Ready for Modern Labels!",
                description="Your repository now has only standard GitHub labels. You can now set up the modern label system cleanly."
            )
        
        # Reset states
        st.session_state['confirm_label_cleanup'] = False
        st.session_state.cleanup_state['label_analysis'] = None
        
        # Auto-refresh after a delay
        import time
        time.sleep(2)
        load_and_analyze_labels()
        
    except Exception as e:
        st.error(f"❌ Unexpected error during label cleanup: {str(e)}")
        st.session_state['confirm_label_cleanup'] = False

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

def render_metric_card(title, value, icon):
    """Render metric card component"""
    
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

# API functions

def load_repository_issues():
    """Load issues from repository using GitHub API with pagination"""
    
    st.session_state['loading_issues'] = True
    
    try:
        # Import the GitHub API utility
        from utils.github_api import GitHubAPI, GitHubAPIError
        
        # Initialize API
        api = GitHubAPI()
        
        # Get filter settings
        filter_state = st.session_state.cleanup_state['filter_state']
        sort_by = st.session_state.cleanup_state['sort_by']
        sort_direction = st.session_state.cleanup_state['sort_direction']
        
        # Create a placeholder for loading progress
        progress_placeholder = st.empty()
        
        def progress_callback(message):
            progress_placeholder.info(f"🔄 {message}")
        
        # Load ALL issues with automatic pagination
        raw_issues = api.get_all_issues(
            state=filter_state,
            sort=sort_by,
            direction=sort_direction,
            progress_callback=progress_callback
        )
        
        # Process and format issues
        all_issues = []
        for issue in raw_issues:
            formatted_issue = {
                'number': issue['number'],
                'title': issue['title'],
                'body': issue.get('body', ''),
                'state': issue['state'],
                'created_at': issue['created_at'][:10],  # Just date part
                'updated_at': issue['updated_at'][:10],
                'author': issue['user']['login'],
                'labels': [label['name'] for label in issue.get('labels', [])],
                'assignees': [assignee['login'] for assignee in issue.get('assignees', [])],
                'milestone': issue['milestone']['title'] if issue.get('milestone') else None,
                'url': issue['html_url'],
                'comments': issue.get('comments', 0)
            }
            all_issues.append(formatted_issue)
        
        # Clear progress placeholder
        progress_placeholder.empty()
        
        # Store loaded issues
        st.session_state.cleanup_state['loaded_issues'] = all_issues
        st.session_state['loading_issues'] = False
        
        # Show success message
        st.success(f"✅ Loaded {len(all_issues)} issues from repository")
        
    except GitHubAPIError as e:
        st.session_state['loading_issues'] = False
        st.error(f"❌ GitHub API Error: {str(e)}")
        st.session_state.cleanup_state['loaded_issues'] = []
        
    except Exception as e:
        st.session_state['loading_issues'] = False
        st.error(f"❌ Unexpected error loading issues: {str(e)}")
        st.session_state.cleanup_state['loaded_issues'] = []
    
    st.rerun()

def load_repository_milestones():
    """Load milestones from repository using GitHub API"""
    
    st.session_state['loading_milestones'] = True
    
    try:
        # Import the GitHub API utility
        from utils.github_api import GitHubAPI, GitHubAPIError
        
        # Initialize API
        api = GitHubAPI()
        
        # Load all milestones (open and closed)
        raw_milestones = api.get_milestones(state="all")
        
        # Process and format milestones
        formatted_milestones = []
        for milestone in raw_milestones:
            formatted_milestone = {
                'number': milestone['number'],
                'title': milestone['title'],
                'description': milestone.get('description', ''),
                'state': milestone['state'],
                'open_issues': milestone.get('open_issues', 0),
                'closed_issues': milestone.get('closed_issues', 0),
                'due_date': milestone.get('due_on', '').split('T')[0] if milestone.get('due_on') else None,
                'created_at': milestone['created_at'][:10],
                'updated_at': milestone['updated_at'][:10],
                'url': milestone['html_url']
            }
            formatted_milestones.append(formatted_milestone)
        
        # Store loaded milestones
        st.session_state.cleanup_state['loaded_milestones'] = formatted_milestones
        st.session_state['loading_milestones'] = False
        
        # Show success message
        st.success(f"✅ Loaded {len(formatted_milestones)} milestones from repository")
        
    except GitHubAPIError as e:
        st.session_state['loading_milestones'] = False
        st.error(f"❌ GitHub API Error: {str(e)}")
        st.session_state.cleanup_state['loaded_milestones'] = []
        
    except Exception as e:
        st.session_state['loading_milestones'] = False
        st.error(f"❌ Unexpected error loading milestones: {str(e)}")
        st.session_state.cleanup_state['loaded_milestones'] = []
    
    st.rerun()

def perform_advanced_search(query):
    """Perform advanced search (mock implementation)"""
    
    if not query.strip():
        st.warning("Please enter a search query")
        return
    
    # Mock search results
    mock_results = [
        {
            'type': 'issue',
            'number': 5,
            'title': 'Search result matching your query',
            'body': 'This is a mock search result that would match your search query.',
            'state': 'open',
            'created_at': '2024-01-20',
            'author': 'search_user',
            'labels': ['bug', 'search-relevant'],
            'url': 'https://github.com/owner/repo/issues/5'
        }
    ]
    
    st.session_state['search_results'] = mock_results
    st.rerun()

def close_selected_issues(issues, select_all):
    """Close selected issues using GitHub API"""
    
    try:
        # Import the GitHub API utility
        from utils.github_api import GitHubAPI, GitHubAPIError
        
        # Get selected issue numbers
        selected_issues = []
        if select_all:
            selected_issues = [issue['number'] for issue in issues]
        else:
            for i in range(len(issues)):
                if st.session_state.get(f'issue_select_{i}', False):
                    selected_issues.append(issues[i]['number'])
        
        if not selected_issues:
            st.warning("⚠️ No issues selected")
            return
        
        # Initialize API
        api = GitHubAPI()
        
        # Create progress placeholder
        progress_placeholder = st.empty()
        
        def progress_callback(message):
            progress_placeholder.info(f"🔄 {message}")
        
        # Close issues in bulk
        successful, failed, errors = api.bulk_close_issues(
            issue_numbers=selected_issues,
            progress_callback=progress_callback
        )
        
        # Clear progress placeholder
        progress_placeholder.empty()
        
        # Show results
        if successful > 0:
            st.success(f"✅ Successfully closed {successful} issues")
        
        if failed > 0:
            st.error(f"❌ Failed to close {failed} issues")
            with st.expander("View errors", expanded=False):
                for error in errors:
                    st.text(error)
        
        # Refresh issues list
        load_repository_issues()
        
    except GitHubAPIError as e:
        st.error(f"❌ GitHub API Error: {str(e)}")
        
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")

"""
Repository Cleanup page - manage existing issues and milestones
"""

import streamlit as st
import json
from datetime import datetime

from config.settings import get_config
from utils.session import get_session_state, set_session_state

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
            'label_analysis': None
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
        "🏷️ Labels"
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
    """Render milestones management tab"""
    
    st.markdown("### 🎯 Milestone Management")
    
    # Load milestones button
    if st.button("🔄 Load Milestones", type="primary"):
        load_repository_milestones()
    
    # Loading message
    if st.session_state.get('loading_milestones', False):
        st.info("🔄 Loading milestones from repository...")
        return
    
    # Milestones list
    milestones = st.session_state.cleanup_state['loaded_milestones']
    
    if milestones:
        render_alert(
            type="success",
            title=f"Found {len(milestones)} milestones",
            description="Loaded from repository"
        )
        
        render_milestones_list(milestones)
    else:
        st.info("No milestones loaded. Click 'Load Milestones' to fetch from repository.")

def render_milestones_list(milestones):
    """Render list of milestones with management options"""
    
    st.markdown("#### Manage Milestones")
    
    for i, milestone in enumerate(milestones):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Milestone info
                st.markdown(f"**🎯 {milestone['title']}**")
                st.markdown(f"*{milestone['description'] or 'No description'}*")
                
                # Stats
                open_issues = milestone.get('open_issues', 0)
                closed_issues = milestone.get('closed_issues', 0)
                
                stats_html = f"""
                <div style="display: flex; gap: 1rem; margin: 0.5rem 0;">
                    <span class="modern-badge badge-success">{open_issues} open</span>
                    <span class="modern-badge">{closed_issues} closed</span>
                </div>
                """
                st.markdown(stats_html, unsafe_allow_html=True)
                
                # Due date
                if milestone.get('due_date'):
                    st.markdown(f"**Due:** {milestone['due_date']}")
            
            with col2:
                # Action buttons
                if st.button("👁️ View", key=f"view_milestone_{i}"):
                    st.session_state[f'show_milestone_{i}'] = not st.session_state.get(f'show_milestone_{i}', False)
                
                if st.button("🗑️ Delete", key=f"delete_milestone_{i}", type="secondary"):
                    if st.session_state.get(f'confirm_delete_milestone_{i}', False):
                        delete_milestone(milestone)
                        st.success(f"Deleted milestone: {milestone['title']}")
                        st.rerun()
                    else:
                        st.session_state[f'confirm_delete_milestone_{i}'] = True
                        st.warning("Click again to confirm deletion")
                        st.rerun()
            
            # Milestone details
            if st.session_state.get(f'show_milestone_{i}', False):
                with st.expander("Milestone Details", expanded=True):
                    st.markdown(f"**URL:** {milestone['url']}")
                    st.markdown(f"**State:** {milestone['state']}")
                    st.markdown(f"**Created:** {milestone['created_at']}")
                    
                    if milestone.get('updated_at'):
                        st.markdown(f"**Updated:** {milestone['updated_at']}")
            
            if i < len(milestones) - 1:
                st.markdown("---")

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
    """Render labels management tab"""
    
    st.markdown("### 🏷️ Label Cleanup & Management")
    
    # Modern label setup section
    st.markdown("#### 🎨 Modern Label System Setup")
    
    render_alert(
        type="info",
        title="Automatic Label Setup",
        description="Set up modern colored labels with priority system for better issue organization"
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🎨 Setup Modern Labels", type="primary", use_container_width=True):
            setup_modern_labels_ui()
    
    with col2:
        if st.button("🔄 Preview Label System", use_container_width=True):
            preview_modern_labels()
    
    # Show preview if requested
    if st.session_state.get('show_label_preview', False):
        render_label_preview()
    
    st.markdown("---")
    
    # Analyze labels section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📊 Analyze Labels", type="primary", use_container_width=True):
            analyze_repository_labels()
    
    with col2:
        if st.button("🔄 Refresh Analysis", use_container_width=True):
            st.session_state.cleanup_state['label_analysis'] = None
            analyze_repository_labels()
    
    # Show analysis results
    analysis = st.session_state.cleanup_state.get('label_analysis')
    
    if analysis:
        render_label_analysis(analysis)
    else:
        render_label_analysis_placeholder()

def render_label_analysis(analysis):
    """Render label analysis results"""
    
    # Summary metrics
    st.markdown("#### 📊 Label Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Total Labels", analysis['total_labels'], "🏷️")
    
    with col2:
        render_metric_card("Project Labels", len(analysis['project_labels']), "🎯")
    
    with col3:
        render_metric_card("Standard Labels", len(analysis['standard_labels']), "✅")
    
    with col4:
        render_metric_card("Suggested Deletions", len(analysis['suggested_deletions']), "🗑️")
    
    # Label categories
    if analysis['project_labels']:
        st.markdown("#### 🎯 Project Labels (Keep these)")
        render_label_list(analysis['project_labels'], "badge-primary")
    
    if analysis['standard_labels']:
        st.markdown("#### ✅ Standard Labels (Keep these)")
        render_label_list(analysis['standard_labels'], "badge-success")
    
    if analysis['suggested_deletions']:
        st.markdown("#### 🗑️ Suggested for Deletion")
        render_label_list(analysis['suggested_deletions'], "badge-destructive")
        
        # Quick delete option
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🧪 Preview Deletion", key="preview_label_deletion"):
                st.info(f"Would delete {len(analysis['suggested_deletions'])} labels")
        
        with col2:
            if st.button("🗑️ Delete Suggested Labels", key="delete_suggested_labels", type="secondary"):
                if st.session_state.get('confirm_label_deletion', False):
                    delete_suggested_labels(analysis['suggested_deletions'])
                    st.success(f"Deleted {len(analysis['suggested_deletions'])} labels")
                    st.session_state.cleanup_state['label_analysis'] = None
                    st.rerun()
                else:
                    st.session_state['confirm_label_deletion'] = True
                    st.warning("Click again to confirm deletion")
                    st.rerun()
    
    # Custom label deletion
    render_custom_label_deletion(analysis)

def render_label_list(labels, badge_class):
    """Render list of labels with badges"""
    
    if labels:
        labels_html = ' '.join([
            f'<span class="modern-badge {badge_class}" style="margin: 0.125rem;">{label}</span>'
            for label in labels[:20]  # Show first 20
        ])
        
        st.markdown(labels_html, unsafe_allow_html=True)
        
        if len(labels) > 20:
            st.markdown(f"*... and {len(labels) - 20} more*")

def render_custom_label_deletion(analysis):
    """Render custom label deletion interface"""
    
    st.markdown("---")
    st.markdown("#### 🎯 Custom Label Deletion")
    
    # Get all unique labels
    all_labels = set()
    for label_list in [
        analysis.get('project_labels', []),
        analysis.get('standard_labels', []),
        analysis.get('duplicate_candidates', []),
        analysis.get('long_labels', []),
        analysis.get('suggested_deletions', [])
    ]:
        all_labels.update(label_list)
    
    all_labels = sorted(list(all_labels))
    
    if all_labels:
        selected_labels = st.multiselect(
            "Select labels to delete:",
            options=all_labels,
            help="⚠️ This action cannot be undone! Select carefully.",
            key="custom_label_deletion"
        )
        
        if selected_labels:
            st.warning(f"You selected {len(selected_labels)} labels for deletion")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🧪 Preview Custom Deletion", key="preview_custom_deletion"):
                    st.info(f"Would delete {len(selected_labels)} selected labels")
            
            with col2:
                if st.button("🗑️ DELETE SELECTED LABELS", key="delete_custom_labels", type="secondary"):
                    if st.session_state.get('confirm_custom_deletion', False):
                        delete_custom_labels(selected_labels)
                        st.success(f"Deleted {len(selected_labels)} labels")
                        st.session_state.cleanup_state['label_analysis'] = None
                        st.rerun()
                    else:
                        st.session_state['confirm_custom_deletion'] = True
                        st.warning("⚠️ Last chance! This cannot be undone. Click again to confirm.")
                        st.rerun()

def render_label_analysis_placeholder():
    """Render placeholder when no analysis is available"""
    
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <h3 class="card-title">📊 Repository Label Analysis</h3>
            <p class="card-description">Analyze your repository labels to identify duplicates, unused labels, and cleanup opportunities</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **What Label Analysis Does:**
    
    - 🎯 **Identifies Project Labels**: Auto-generated project-specific labels
    - ✅ **Finds Standard Labels**: Common GitHub labels (bug, enhancement, etc.)
    - 🔍 **Detects Duplicates**: Similar or redundant labels
    - 📏 **Flags Long Labels**: Labels that might be too verbose
    - 🗑️ **Suggests Deletions**: Old or unused labels safe to remove
    
    Click **"Analyze Labels"** to start the analysis.
    """)

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

# Mock data functions (replace with real API calls)

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

def analyze_repository_labels():
    """Analyze repository labels (mock implementation)"""
    
    # Mock analysis results
    mock_analysis = {
        'total_labels': 24,
        'project_labels': [
            'project-auth-system',
            'project-ui-redesign', 
            'project-api-v2',
            'project-mobile-app'
        ],
        'standard_labels': [
            'bug',
            'enhancement',
            'documentation',
            'help wanted',
            'good first issue',
            'wontfix'
        ],
        'duplicate_candidates': [
            'bugfix',
            'docs',
            'help-wanted'
        ],
        'long_labels': [
            'needs-more-information-from-user',
            'waiting-for-external-dependency'
        ],
        'suggested_deletions': [
            'old-label-1',
            'duplicate-tag',
            'unused-label',
            'deprecated-feature',
            'legacy-system'
        ]
    }
    
    st.session_state.cleanup_state['label_analysis'] = mock_analysis
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

def delete_milestone(milestone):
    """Delete milestone using GitHub API"""
    
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

def setup_modern_labels_ui():
    """Set up modern labels through UI"""
    
    try:
        from github_api import setup_modern_labels
        
        # Show progress
        with st.spinner('🎨 Setting up modern label system...'):
            results = setup_modern_labels()
        
        # Show results
        if results['errors']:
            st.warning(f"⚠️ Label setup completed with {len(results['errors'])} errors")
            with st.expander("View Errors", expanded=False):
                for error in results['errors']:
                    st.error(error)
        else:
            st.success(f"✅ Label setup successful!")
        
        # Show summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Created", results['created'])
        
        with col2:
            st.metric("Updated", results['updated'])
        
        with col3:
            st.metric("Total", results['total'])
        
        render_alert(
            type="success",
            title="Modern Labels Ready!",
            description="Your repository now has a professional colored label system. Process new issues to see them in action."
        )
        
    except Exception as e:
        st.error(f"❌ Failed to setup labels: {str(e)}")
        
        # Show manual setup option
        render_alert(
            type="warning",
            title="Manual Setup Available",
            description="You can also run 'python fix_label_colors.py' in your project directory."
        )

def preview_modern_labels():
    """Preview the modern label system"""
    
    st.session_state['show_label_preview'] = not st.session_state.get('show_label_preview', False)
    st.rerun()

def render_label_preview():
    """Render preview of modern label system"""
    
    st.markdown("#### 👀 Modern Label System Preview")
    
    # Priority labels
    st.markdown("**Priority Labels:**")
    priority_html = """
    <div style="display: flex; gap: 0.5rem; margin: 0.5rem 0; flex-wrap: wrap;">
        <span class="modern-badge" style="background-color: #B60205; color: white;">🚨 priority-critical</span>
        <span class="modern-badge" style="background-color: #D93F0B; color: white;">⚡ priority-high</span>
        <span class="modern-badge" style="background-color: #FBCA04; color: black;">📋 priority-medium</span>
        <span class="modern-badge" style="background-color: #0E8A16; color: white;">📝 priority-low</span>
    </div>
    """
    st.markdown(priority_html, unsafe_allow_html=True)
    
    # Area labels
    st.markdown("**Area Labels:**")
    area_html = """
    <div style="display: flex; gap: 0.5rem; margin: 0.5rem 0; flex-wrap: wrap;">
        <span class="modern-badge" style="background-color: #FF7F0E; color: white;">backend</span>
        <span class="modern-badge" style="background-color: #1F77B4; color: white;">frontend</span>
        <span class="modern-badge" style="background-color: #2CA02C; color: white;">database</span>
        <span class="modern-badge" style="background-color: #D73A4A; color: white;">security</span>
        <span class="modern-badge" style="background-color: #6A1B9A; color: white;">privacy</span>
        <span class="modern-badge" style="background-color: #E91E63; color: white;">user-experience</span>
    </div>
    """
    st.markdown(area_html, unsafe_allow_html=True)
    
    # Type labels
    st.markdown("**Type Labels:**")
    type_html = """
    <div style="display: flex; gap: 0.5rem; margin: 0.5rem 0; flex-wrap: wrap;">
        <span class="modern-badge" style="background-color: #A2EEEF; color: black;">enhancement</span>
        <span class="modern-badge" style="background-color: #D73A4A; color: white;">bug</span>
        <span class="modern-badge" style="background-color: #7057FF; color: white;">maintenance</span>
        <span class="modern-badge" style="background-color: #0075CA; color: white;">documentation</span>
    </div>
    """
    st.markdown(type_html, unsafe_allow_html=True)
    
    st.markdown("""
    **Benefits:**
    - 🎨 **Visual Priority** - Instantly see what needs attention
    - 📊 **Better Organization** - Filter and sort by priority/area
    - 👥 **Team Clarity** - Everyone knows what to work on first
    - 💼 **Professional Appearance** - Looks organized and maintained
    """)

def delete_suggested_labels(labels):
    """Delete suggested labels (mock implementation)"""
    
    # In real implementation, this would call GitHub API to delete labels
    pass

def delete_custom_labels(labels):
    """Delete custom selected labels (mock implementation)"""
    
    # In real implementation, this would call GitHub API to delete labels
    pass

"""
Sidebar component with useful shortcuts and status
"""

import streamlit as st
from config.settings import get_config, check_basic_config

def render_sidebar():
    """Render the sidebar with shortcuts and status"""
    
    with st.sidebar:
        # App title and version
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid hsl(var(--border)); margin-bottom: 1rem;">
            <h2 style="margin: 0; font-size: 1.25rem; color: hsl(var(--primary));">🚀 GitHub Manager</h2>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem; color: hsl(var(--muted-foreground));">v6.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick status overview
        render_status_overview()
        
        # Quick actions
        render_quick_actions()
        
        # Navigation shortcuts
        render_navigation_shortcuts()
        
        # Settings and tools
        render_settings_tools()
        
        # Help and information
        render_help_section()

def render_status_overview():
    """Render quick status overview"""
    
    st.markdown("### 📊 Status")
    
    # Check configurations
    config = check_basic_config()
    
    # GitHub status
    github_status = "🟢 Ready" if config['github_configured'] else "🔴 Not configured"
    st.markdown(f"**GitHub API**: {github_status}")
    
    # AI status  
    ai_status = "🟢 Ready" if config['ai_configured'] else "🟡 Optional"
    st.markdown(f"**DeepSeek AI**: {ai_status}")
    
    # Repository info
    if config['github_configured']:
        st.markdown(f"**Repository**: `{config['repo_owner']}/{config['repo_name']}`")

def render_quick_actions():
    """Render quick action buttons"""
    
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Load Issues", key="sidebar_load_issues", use_container_width=True):
            st.session_state.current_page = "Repository Cleanup"
            st.session_state.auto_load_issues = True
            st.rerun()
    
    with col2:
        if st.button("📁 Upload File", key="sidebar_upload", use_container_width=True):
            st.session_state.current_page = "Upload & Convert"
            st.rerun()
    
    if st.button("✍️ Manual Entry", key="sidebar_manual", use_container_width=True):
        st.session_state.current_page = "Manual Entry"
        st.rerun()
    
    # ALWAYS CLICKABLE label setup button - no conditions!
    if st.button("🎨 Fix Repository Labels", key="sidebar_fix_labels", use_container_width=True, type="secondary"):
        st.session_state.show_label_setup = True
        st.rerun()

def render_navigation_shortcuts():
    """Render navigation shortcuts"""
    
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    
    # Page shortcuts
    pages = [
        ("📁", "Upload & Convert"),
        ("✍️", "Manual Entry"), 
        ("🗑️", "Repository Cleanup")
    ]
    
    for icon, page_name in pages:
        if st.button(f"{icon} {page_name}", key=f"nav_{page_name}", use_container_width=True):
            st.session_state.current_page = page_name
            st.rerun()

def render_settings_tools():
    """Render settings and tools section"""
    
    st.markdown("---")
    st.markdown("### ⚙️ Tools")
    
    # Configuration shortcuts
    if st.button("🔧 GitHub Config", key="sidebar_github_config", use_container_width=True):
        st.session_state.show_github_config = True
        st.rerun()
    
    if st.button("🤖 AI Settings", key="sidebar_ai_config", use_container_width=True):
        st.session_state.show_ai_config = True
        st.rerun()
    
    # ALWAYS CLICKABLE label setup - no disabled states!
    if st.button("🏷️ Setup Labels", key="sidebar_setup_labels", use_container_width=True):
        st.session_state.show_label_setup = True
        st.rerun()
    
    # Theme toggle
    current_theme = "Dark" if st.session_state.get('dark_mode', True) else "Light"
    if st.button(f"🎨 Theme: {current_theme}", key="sidebar_theme", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.get('dark_mode', True)
        st.rerun()
    
    # Export/Import
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾", key="sidebar_export", use_container_width=True, help="Export Data"):
            st.session_state.show_export = True
            st.rerun()
    
    with col2:
        if st.button("📥", key="sidebar_import", use_container_width=True, help="Import Data"):
            st.session_state.show_import = True
            st.rerun()

def render_help_section():
    """Render help and information section"""
    
    st.markdown("---")
    st.markdown("### ℹ️ Help")
    
    if st.button("📚 Setup Guide", key="sidebar_setup", use_container_width=True):
        st.session_state.show_setup_guide = True
        st.rerun()
    
    if st.button("🔍 Troubleshoot", key="sidebar_troubleshoot", use_container_width=True):
        st.session_state.show_troubleshoot = True
        st.rerun()
    
    # Quick stats if available
    if st.session_state.get('processed_projects'):
        st.markdown("---")
        st.markdown("### 📈 Session Stats")
        
        projects = st.session_state.processed_projects
        total_milestones = len(projects)
        total_issues = sum(len(m.get('issues', [])) for m in projects.values())
        
        st.markdown(f"**Milestones**: {total_milestones}")
        st.markdown(f"**Issues**: {total_issues}")
    
    # App info
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem; color: hsl(var(--muted-foreground)); font-size: 0.75rem;">
        <p style="margin: 0;">Built with Streamlit & DeepSeek AI</p>
        <p style="margin: 0;">© 2024 GitHub Issues Manager</p>
    </div>
    """, unsafe_allow_html=True)

def handle_sidebar_actions():
    """Handle sidebar action states"""
    
    # GitHub configuration modal
    if st.session_state.get('show_github_config'):
        render_github_config_modal()
    
    # AI configuration modal
    if st.session_state.get('show_ai_config'):
        render_ai_config_modal()
    
    # Label setup modal
    if st.session_state.get('show_label_setup'):
        render_label_setup_modal()
    
    # Setup guide modal
    if st.session_state.get('show_setup_guide'):
        render_setup_guide_modal()
    
    # Troubleshoot modal
    if st.session_state.get('show_troubleshoot'):
        render_troubleshoot_modal()

def render_github_config_modal():
    """Render GitHub configuration modal"""
    
    st.markdown("### 🔧 GitHub Configuration")
    
    config = check_basic_config()
    
    st.markdown("""
    **Required Environment Variables:**
    
    Create a `.env` file with:
    ```
    GITHUB_TOKEN=your_github_personal_access_token
    REPO_OWNER=your_username_or_organization
    REPO_NAME=your_repository_name
    ```
    """)
    
    # Current status
    st.markdown("**Current Status:**")
    st.markdown(f"- Token: {'✅ Set' if config['github_token'] else '❌ Missing'}")
    st.markdown(f"- Owner: {'✅ Set' if config['repo_owner'] else '❌ Missing'}")
    st.markdown(f"- Repo: {'✅ Set' if config['repo_name'] else '❌ Missing'}")
    
    if st.button("✅ Close", key="close_github_config"):
        st.session_state.show_github_config = False
        st.rerun()

def render_ai_config_modal():
    """Render AI configuration modal"""
    
    st.markdown("### 🤖 AI Configuration")
    
    config = check_basic_config()
    
    st.markdown("""
    **Optional DeepSeek AI:**
    
    Add to your `.env` file:
    ```
    DEEPSEEK_API_KEY=your_deepseek_api_key
    ```
    
    **Benefits:**
    - Intelligent markdown parsing
    - Natural language to issues conversion
    - Better content understanding
    """)
    
    st.markdown(f"**Status**: {'✅ Configured' if config['ai_configured'] else '❌ Not configured'}")
    
    if st.button("✅ Close", key="close_ai_config"):
        st.session_state.show_ai_config = False
        st.rerun()

def render_setup_guide_modal():
    """Render setup guide modal"""
    
    st.markdown("### 📚 Setup Guide")
    
    st.markdown("""
    **Quick Setup Steps:**
    
    1. **Get GitHub Token**
       - Go to GitHub Settings → Developer settings → Personal access tokens
       - Generate new token with `repo` scope
       - Copy the token
    
    2. **Create .env File**
       - Create `.env` in your project root
       - Add your configuration variables
    
    3. **Test Connection**
       - Restart the application
       - Check status indicators turn green
    
    4. **Start Using**
       - Upload markdown files
       - Create manual entries
       - Manage repository issues
    """)
    
    if st.button("✅ Close", key="close_setup_guide"):
        st.session_state.show_setup_guide = False
        st.rerun()

def render_label_setup_modal():
    """Render label setup modal"""
    
    st.markdown("### 🎨 Setup Modern Colored Labels")
    
    # Check GitHub configuration first
    config = check_basic_config()
    
    if not config['github_configured']:
        st.error("❌ GitHub configuration required!")
        st.markdown("""
        **Please configure GitHub first:**
        
        1. Create a `.env` file with:
        ```
        GITHUB_TOKEN=your_github_personal_access_token
        REPO_OWNER=your_username_or_organization
        REPO_NAME=your_repository_name
        ```
        
        2. Restart the application
        
        3. Come back to setup labels
        """)
        
        if st.button("✅ Close", key="close_label_setup_config"):
            st.session_state.show_label_setup = False
            st.rerun()
        return
    
    st.markdown("""
    This will create/update modern colored labels in your repository for better project organization:
    
    **🎨 Modern Priority Labels:**
    - 🚨 priority-critical (Red) - Critical issues requiring immediate attention
    - ⚡ priority-high (Orange) - High priority issues
    - 📋 priority-medium (Yellow) - Medium priority issues
    - 📝 priority-low (Green) - Low priority issues
    
    **🛠️ Work Stream Labels:**
    - 🧪 testing-qa (Medium Slate Blue) - Testing & Quality Assurance
    - 🗄️ database-migration (Sea Green) - Database & Migration Strategy  
    - ⚡ code-quality (Gold) - Code Quality & Optimization
    - 🔍 feature-analysis (Royal Blue) - Core Feature Analysis
    - 🛠️ tech-stack (Gray) - Technology Stack Assessment
    - 📚 documentation (Lime Green) - Documentation & Guides
    - 🐛 bug (Crimson) - Bug fixes and issues
    - ✨ enhancement (Medium Purple) - New features and improvements
    - 🚀 deployment (Tomato) - Deployment and DevOps
    - 🔒 security (Dark Red) - Security-related tasks
    
    **📋 Area Labels:**
    - backend, frontend, database, user-experience, requirements, workflow
    
    **🤝 Standard Labels:**
    - good-first-issue, help-wanted, wontfix
    
    ⚠️ **Note**: This will CREATE new labels or UPDATE existing ones with proper colors!
    """)
    
    # Show current repository
    st.info(f"🔗 Repository: `{config['repo_owner']}/{config['repo_name']}`")
    
    # Make buttons larger and more prominent
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🚀 SETUP LABELS NOW!", key="run_label_setup", type="primary", use_container_width=True, help="Click to apply colored labels to your GitHub repository"):
            setup_labels_process()
    
    with col2:
        if st.button("❌ Close", key="cancel_label_setup", use_container_width=True):
            st.session_state.show_label_setup = False
            st.rerun()

def setup_labels_process():
    """Process label setup with progress feedback - SIMPLIFIED VERSION"""
    
    st.markdown("## 🚀 Setting up labels...")
    
    # Check config first
    try:
        from config.settings import check_basic_config
        config = check_basic_config()
        
        if not config['github_configured']:
            st.error("❌ Please configure GitHub in your .env file first!")
            return
        
        st.info(f"🔗 Working on repository: {config['repo_owner']}/{config['repo_name']}")
        
    except Exception as e:
        st.error(f"❌ Configuration error: {str(e)}")
        return
    
    # Try to import and run the setup
    try:
        from utils.github_api import setup_modern_labels
        
        # Simple progress tracking
        progress_placeholder = st.empty()
        
        def progress_callback(message):
            progress_placeholder.info(f"⏳ {message}")
        
        # Run the setup
        with st.spinner("Setting up colored labels..."):
            results = setup_modern_labels(progress_callback)
        
        # Clear progress
        progress_placeholder.empty()
        
        # Show results
        if results['created'] > 0:
            st.success(f"✅ Created {results['created']} new labels!")
        
        if results.get('updated', 0) > 0:
            st.info(f"🔄 Updated {results['updated']} existing labels with new colors!")
        
        if results.get('skipped', 0) > 0:
            st.info(f"ℹ️ Skipped {results['skipped']} existing labels")
        
        if results.get('errors'):
            st.error(f"❌ {len(results['errors'])} errors occurred:")
            for error in results['errors']:
                st.text(f"• {error}")
        
        if not results.get('errors') and (results['created'] > 0 or results.get('updated', 0) > 0):
            st.balloons()  # Celebrate success!
            
            # Show link to GitHub
            github_url = f"https://github.com/{config['repo_owner']}/{config['repo_name']}/labels"
            st.markdown(f"🔗 [View your colored labels on GitHub]({github_url})")
            
            # Close the modal
            st.session_state.show_label_setup = False
    
    except ImportError as e:
        st.error(f"❌ Import error: {str(e)}")
        st.error("The utils.github_api module may not be available.")
        
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.error("Please check your GitHub configuration and try again.")

def render_troubleshoot_modal():
    """Render troubleshooting modal"""
    
    st.markdown("### 🔍 Troubleshooting")
    
    st.markdown("""
    **Common Issues:**
    
    **🔴 GitHub API Not Working**
    - Check token has `repo` scope
    - Verify repository name and owner
    - Ensure token hasn't expired
    
    **🔴 Issues Not Loading**
    - Confirm repository has issues enabled
    - Check you have read access to repository
    - Try refreshing the page
    
    **🔴 .env File Not Working**
    - Ensure file is named exactly `.env`
    - File should be in project root directory
    - Restart application after changes
    
    **🔴 AI Parsing Fails**
    - DeepSeek API key might be invalid
    - Falls back to standard parsing automatically
    - Check your API quota/billing
    """)
    
    if st.button("✅ Close", key="close_troubleshoot"):
        st.session_state.show_troubleshoot = False
        st.rerun()

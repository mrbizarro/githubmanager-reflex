"""
Modern header component with settings drawer
"""

import streamlit as st
from config.settings import Config

def render_project_selector():
    """Render project selector dropdown"""
    
    try:
        # Get user's repositories
        repos = get_user_repositories()
        
        if repos:
            current_repo = f"{Config.get_repo_owner()}/{Config.get_repo_name()}"
            
            # Create options list
            repo_options = [f"{repo['owner']}/{repo['name']}" for repo in repos]
            
            # Find current selection
            current_index = 0
            if current_repo in repo_options:
                current_index = repo_options.index(current_repo)
            
            selected_repo = st.selectbox(
                "Select Repository",
                options=repo_options,
                index=current_index,
                key="project_selector_header",
                help="Switch between your repositories"
            )
            
            # Update config if changed
            if selected_repo != current_repo:
                owner, name = selected_repo.split('/')
                update_project_config(owner, name)
                st.rerun()
        else:
            st.info("Loading repositories...")
            
    except Exception as e:
        st.error(f"Error loading repositories: {e}")

def get_user_repositories():
    """Get user's GitHub repositories"""
    
    try:
        import requests
        
        token = Config.get_github_token()
        if not token:
            return []
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get user's repos (both owned and member)
        response = requests.get(
            "https://api.github.com/user/repos?sort=updated&per_page=50", 
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            repos = response.json()
            return [
                {
                    'name': repo['name'],
                    'owner': repo['owner']['login'],
                    'full_name': repo['full_name'],
                    'updated_at': repo['updated_at']
                }
                for repo in repos
                if not repo['archived']  # Skip archived repos
            ]
        else:
            return []
            
    except Exception:
        return []

def update_project_config(owner, name):
    """Update project configuration in .env"""
    
    try:
        # Read current .env
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Update repo owner and name
        updated_lines = []
        for line in lines:
            if line.startswith('REPO_OWNER='):
                updated_lines.append(f'REPO_OWNER={owner}\n')
            elif line.startswith('REPO_NAME='):
                updated_lines.append(f'REPO_NAME={name}\n')
            else:
                updated_lines.append(line)
        
        # Write back to .env
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
        
        st.success(f"✅ Switched to {owner}/{name}")
        
    except Exception as e:
        st.error(f"Error updating config: {e}")

def render_header():
    """Render modern header with gradient background"""
    
    st.markdown("""
    <div class="modern-header">
        <h1>🚀 GitHub Issues Manager v6</h1>
        <p>AI-powered markdown to GitHub issues converter</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Settings in header row
    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
    
    with col2:
        # Theme toggle
        dark_mode = st.session_state.get('dark_mode', True)
        if st.button("🌙" if dark_mode else "☀️", key="theme_toggle", help="Toggle theme"):
            st.session_state.dark_mode = not dark_mode
            st.rerun()
    
    with col3:
        if st.button("⚙️ Settings", key="header_settings"):
            st.session_state.show_settings = not st.session_state.get('show_settings', False)
    
    with col4:
        if st.button("❓ Help", key="header_help"):
            st.session_state.show_help = not st.session_state.get('show_help', False)
    
    # Settings drawer
    if st.session_state.get('show_settings', False):
        render_settings_drawer()
    
    # Help drawer
    if st.session_state.get('show_help', False):
        render_help_drawer()

def render_settings_drawer():
    """Render settings configuration drawer"""
    
    st.markdown("---")
    st.markdown("### ⚙️ Configuration Settings")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            # Project selector (if GitHub is configured)
            if Config.get_github_token():
                st.markdown("#### Project")
                render_project_selector()
                st.markdown("---")
            
            st.markdown("#### GitHub Configuration")
            
            github_token = st.text_input(
                "GitHub Token",
                value=Config.get_github_token(),
                type="password",
                help="Personal access token with repo scope"
            )
            
            repo_owner = st.text_input(
                "Repository Owner",
                value=Config.get_repo_owner(),
                help="GitHub username or organization"
            )
            
            repo_name = st.text_input(
                "Repository Name",
                value=Config.get_repo_name(),
                help="Name of the repository"
            )
        
        with col2:
            st.markdown("#### AI Configuration")
            
            deepseek_key = st.text_input(
                "DeepSeek API Key",
                value=Config.get_deepseek_key(),
                type="password",
                help="API key from DeepSeek platform"
            )
            
            st.markdown("#### App Settings")
            
            theme = st.selectbox(
                "Theme",
                options=["auto", "light", "dark"],
                index=0,
                help="Application theme preference"
            )
        
        # Save settings button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💾 Save Settings", type="primary", use_container_width=True):
                save_settings_to_env(github_token, repo_owner, repo_name, deepseek_key, theme)
                st.session_state.show_settings = False
                st.rerun()

def save_settings_to_env(github_token, repo_owner, repo_name, deepseek_key, theme):
    """Save settings to .env file"""
    
    try:
        env_content = f"""# GitHub Issues Manager v6 Configuration

# GitHub Settings
GITHUB_TOKEN={github_token}
REPO_OWNER={repo_owner}
REPO_NAME={repo_name}

# DeepSeek AI Settings (Optional)
DEEPSEEK_API_KEY={deepseek_key}

# Application Settings
ENVIRONMENT=production
THEME={theme}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        st.success("✅ Settings saved successfully!")
        
    except Exception as e:
        st.error(f"❌ Error saving settings: {e}")

def render_help_drawer():
    """Render help and documentation drawer"""
    
    st.markdown("---")
    st.markdown("### ❓ Help & Documentation")
    
    tab1, tab2, tab3 = st.tabs(["Quick Start", "Features", "Troubleshooting"])
    
    with tab1:
        st.markdown("""
        #### 🚀 Quick Start Guide
        
        1. **Configure Settings**: Click the ⚙️ Settings button and enter your GitHub token and repository details
        2. **Upload Files**: Go to "Upload & Convert" tab and drag your markdown files
        3. **Process**: Click "Process Files" to convert markdown to issues and milestones
        4. **Review**: Edit the generated content as needed
        5. **Deploy**: Click "Deploy" to create issues in your GitHub repository
        
        #### 📋 File Format
        
        **AI Mode**: Upload any markdown file - AI will intelligently parse it
        
        **Standard Mode**: Use this format:
        ```markdown
        # Milestone: Project Name
        description: Milestone description
        
        ## Issue: Issue Title
        Issue description here
        labels: bug, feature
        assignees: username
        ```
        """)
    
    with tab2:
        st.markdown("""
        #### ✨ Features Overview
        
        - **🤖 AI-Powered Parsing**: Intelligent conversion of natural markdown
        - **📊 Real-time Metrics**: Track progress and statistics
        - **✏️ Live Editing**: Modify content before deployment
        - **🗑️ Repository Cleanup**: Manage existing issues and milestones
        - **🎯 Smart Labels**: Automatic label creation and management
        - **📋 Manual Entry**: Create issues and milestones manually
        - **🔄 Batch Processing**: Handle multiple files at once
        """)
    
    with tab3:
        st.markdown("""
        #### 🔧 Troubleshooting
        
        **AI Not Working?**
        - Check DeepSeek API key in settings
        - Verify internet connection
        - Try standard mode as fallback
        
        **GitHub Errors?**
        - Verify token has `repo` scope
        - Check repository owner/name spelling
        - Ensure repository exists and is accessible
        
        **Processing Issues?**
        - Check markdown file encoding (UTF-8)
        - Try both AI and standard modes
        - Review file format requirements
        
        **Need More Help?**
        - Check the README.md file
        - Visit the GitHub repository
        - Open an issue for support
        """)
    
    if st.button("Close Help", key="close_help"):
        st.session_state.show_help = False
        st.rerun()

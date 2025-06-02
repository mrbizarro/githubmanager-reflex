"""
Modern header component with settings drawer
"""

import streamlit as st
import requests
import os
from config.settings import Config

def render_project_selector():
    """Render project selector dropdown"""
    
    # Always show current repository from .env first
    current_repo = f"{Config.get_repo_owner()}/{Config.get_repo_name()}"
    
    if not current_repo or current_repo == "/":
        st.info("⚠️ Please configure GitHub repository in settings")
        return
    
    # Show current repository
    st.text_input(
        "Current Repository", 
        value=current_repo,
        disabled=True,
        help="Configure repository in settings below"
    )
    
    # Optional: Add a "Refresh Repositories" button for power users
    if st.button("🔄 Switch Repository", key="switch_repo_btn", help="Load available repositories"):
        st.session_state.show_repo_list = True
    
    # Only show full list if explicitly requested
    if st.session_state.get('show_repo_list', False):
        try:
            with st.spinner("Loading your repositories..."):
                repos = get_user_repositories()
            
            if repos:
                repo_options = [f"{repo['owner']}/{repo['name']}" for repo in repos]
                
                selected_repo = st.selectbox(
                    "Available Repositories",
                    options=repo_options,
                    key="repo_selector",
                    help="Select a different repository"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Switch", type="primary"):
                        owner, name = selected_repo.split('/')
                        update_project_config(owner, name)
                        st.session_state.show_repo_list = False
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancel"):
                        st.session_state.show_repo_list = False
                        st.rerun()
            else:
                st.warning("No repositories found or API error")
                if st.button("❌ Close"):
                    st.session_state.show_repo_list = False
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Error loading repositories: {e}")
            if st.button("❌ Close"):
                st.session_state.show_repo_list = False
                st.rerun()

def get_user_repositories():
    """Get user's GitHub repositories (with timeout)"""
    
    try:
        import requests
        
        token = Config.get_github_token()
        if not token:
            return []
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get user's repos (both owned and member) with shorter timeout
        response = requests.get(
            "https://api.github.com/user/repos?sort=updated&per_page=30", 
            headers=headers,
            timeout=5  # Reduced timeout
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
            
    except requests.exceptions.Timeout:
        st.warning("⏰ Repository loading timed out - using current configuration")
        return []
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not load repositories: {str(e)}")
        return []
    except Exception as e:
        st.warning(f"Unexpected error: {str(e)}")
        return []

def update_project_config(owner, name):
    """Update project configuration in .env file"""
    
    try:
        print(f"🔄 Attempting to update repository to {owner}/{name}")
        
        # Read current .env content
        env_content = ""
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_content = f.read()
                print(f"📄 Current .env content length: {len(env_content)}")
        
        # Update or add repository settings
        lines = env_content.split('\n') if env_content else []
        updated_lines = []
        found_owner = False
        found_name = False
        
        for line in lines:
            if line.startswith('REPO_OWNER='):
                old_value = line
                updated_lines.append(f'REPO_OWNER={owner}')
                found_owner = True
                print(f"📝 Updated: {old_value} → REPO_OWNER={owner}")
            elif line.startswith('REPO_NAME='):
                old_value = line
                updated_lines.append(f'REPO_NAME={name}')
                found_name = True
                print(f"📝 Updated: {old_value} → REPO_NAME={name}")
            else:
                updated_lines.append(line)
        
        # Add missing settings if not found
        if not found_owner:
            updated_lines.append(f'REPO_OWNER={owner}')
            print(f"➕ Added: REPO_OWNER={owner}")
        if not found_name:
            updated_lines.append(f'REPO_NAME={name}')
            print(f"➕ Added: REPO_NAME={name}")
        
        # Write back to .env
        new_content = '\n'.join(updated_lines)
        with open('.env', 'w') as f:
            f.write(new_content)
        
        print(f"💾 Wrote .env file with {len(new_content)} characters")
        
        # Force environment reload
        os.environ['REPO_OWNER'] = owner
        os.environ['REPO_NAME'] = name
        print(f"🔄 Updated environment variables: REPO_OWNER={owner}, REPO_NAME={name}")
        
        # Clear any session caching
        if 'project_config_cache' in st.session_state:
            del st.session_state.project_config_cache
        
        # Verify the update worked
        with open('.env', 'r') as f:
            verify_content = f.read()
            if f'REPO_OWNER={owner}' in verify_content and f'REPO_NAME={name}' in verify_content:
                print(f"✅ Verification passed: Repository updated to {owner}/{name}")
            else:
                print(f"❌ Verification failed: Content doesn't match expected values")
                print(f"Expected: REPO_OWNER={owner}, REPO_NAME={name}")
                print(f"Content: {verify_content}")
        
    except Exception as e:
        st.error(f"Error updating repository config: {e}")
        print(f"❌ Error updating config: {e}")
        import traceback
        print(traceback.format_exc())

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
                
                # Show current configuration clearly
                current_owner = Config.get_repo_owner()
                current_name = Config.get_repo_name()
                
                if current_owner and current_name:
                    st.success(f"✅ Current: {current_owner}/{current_name}")
                    
                    # Debug info
                    with st.expander("🔍 Debug Info", expanded=False):
                        st.code(f"REPO_OWNER={current_owner}\nREPO_NAME={current_name}")
                        if st.button("🔄 Reload Config", key="reload_config"):
                            from config.settings import load_environment
                            load_environment()
                            st.rerun()
                        
                        if st.button("🔍 Test Repository List", key="test_repos"):
                            st.session_state.show_debug_repos = True
                        
                        if st.session_state.get('show_debug_repos', False):
                            with st.spinner("Loading all repositories..."):
                                repos = get_user_repositories()
                            if repos:
                                st.write(f"Found {len(repos)} repositories:")
                                for repo in repos[:10]:  # Show first 10
                                    st.write(f"- {repo['owner']}/{repo['name']}")
                                if len(repos) > 10:
                                    st.write(f"... and {len(repos) - 10} more")
                            else:
                                st.write("No repositories found")
                            
                            if st.button("❌ Close Debug", key="close_debug_repos"):
                                st.session_state.show_debug_repos = False
                                st.rerun()
                    
                    # Option to switch repositories
                    if st.button("🔄 Switch Repository", key="settings_switch_repo"):
                        st.session_state.show_repo_selector = True
                    
                    if st.session_state.get('show_repo_selector', False):
                        with st.spinner("Loading repositories..."):
                            repos = get_user_repositories()
                        
                        if repos:
                            repo_options = [f"{repo['owner']}/{repo['name']}" for repo in repos]
                            
                            selected = st.selectbox(
                                "Choose Repository",
                                options=repo_options,
                                key="settings_repo_select"
                            )
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("✅ Select", key="confirm_repo_change"):
                                    owner, name = selected.split('/')
                                    # Update .env file immediately
                                    update_project_config(owner, name)
                                    st.session_state.show_repo_selector = False
                                    st.success(f"✅ Switched to {owner}/{name}")
                                    st.rerun()
                            
                            with col_b:
                                if st.button("❌ Cancel", key="cancel_repo_change"):
                                    st.session_state.show_repo_selector = False
                                    st.rerun()
                        else:
                            st.warning("Could not load repositories")
                            if st.button("❌ Close", key="close_repo_loader"):
                                st.session_state.show_repo_selector = False
                                st.rerun()
                else:
                    st.warning("⚠️ Repository not configured")
                
                st.markdown("---")
            
            st.markdown("#### GitHub Configuration")
            
            github_token = st.text_input(
                "GitHub Token",
                value=Config.get_github_token(),
                type="password",
                help="Personal access token with repo scope"
            )
            
            # Remove manual repository input - use dynamic selection only
            if not Config.get_github_token():
                st.info("ℹ️ Add your GitHub token above, then save to enable repository selection")
        
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
                save_settings_to_env(github_token, deepseek_key, theme)
                st.session_state.show_settings = False
                st.rerun()

def save_settings_to_env(github_token, deepseek_key, theme):
    """Save settings to .env file (keeping current repository config)"""
    
    try:
        # Keep current repository settings
        current_owner = Config.get_repo_owner()
        current_name = Config.get_repo_name()
        
        print(f"💾 Saving settings with repository: {current_owner}/{current_name}")
        
        env_content = f"""# GitHub Issues Manager v6 Configuration

# GitHub Settings
GITHUB_TOKEN={github_token}
REPO_OWNER={current_owner}
REPO_NAME={current_name}

# DeepSeek AI Settings (Optional)
DEEPSEEK_API_KEY={deepseek_key}

# Application Settings
ENVIRONMENT=production
THEME={theme}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print(f"📝 Saved .env with REPO_OWNER={current_owner}, REPO_NAME={current_name}")
        
        # Clear repository selector session state
        if 'show_repo_selector' in st.session_state:
            del st.session_state.show_repo_selector
        
        st.success("✅ Settings saved successfully!")
        
    except Exception as e:
        st.error(f"❌ Error saving settings: {e}")
        print(f"❌ Save error: {e}")

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

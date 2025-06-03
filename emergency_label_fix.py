"""
🎨 EMERGENCY LABEL FIXER - Multi-Repository Version
Run this directly: streamlit run emergency_label_fix.py
Now supports selecting different repositories!
"""

import streamlit as st
import os
import sys
import requests
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    st.set_page_config(
        page_title="🎨 Emergency GitHub Label Fixer",
        page_icon="🎨",
        layout="wide"
    )
    
    st.title("🎨 Emergency GitHub Label Fixer")
    st.markdown("### Fix your GitHub repository labels with beautiful colors!")
    
    # Repository selection section
    st.markdown("## 📁 Choose Repository")
    
    # Load default values from .env if available
    default_token = os.getenv('GITHUB_TOKEN', '')
    default_owner = os.getenv('REPO_OWNER', '')
    default_repo = os.getenv('REPO_NAME', '')
    
    col1, col2 = st.columns(2)
    
    with col1:
        github_token = st.text_input(
            "🔑 GitHub Token",
            value=default_token,
            type="password",
            help="Personal Access Token with 'repo' scope",
            placeholder="ghp_your_token_here"
        )
    
    with col2:
        # Repository input with default
        default_repo_string = f"{default_owner}/{default_repo}" if default_owner and default_repo else ""
        repo_input = st.text_input(
            "📁 Repository (owner/repo)",
            value=default_repo_string,
            help="Format: username/repository-name",
            placeholder="mrbizarro/tests"
        )
    
    # Parse repository info
    if repo_input and github_token:
        owner, repo = parse_repository_input(repo_input)
        
        if owner and repo:
            # Test connection
            connection_ok, message = test_github_connection(github_token, owner, repo)
            
            if connection_ok:
                st.success(f"✅ Connected to: `{owner}/{repo}`")
                render_label_setup_section(github_token, owner, repo)
            else:
                st.error(f"❌ Connection failed: {message}")
                st.markdown("""
                **Common issues:**
                - Token doesn't have 'repo' scope
                - Repository doesn't exist or is private
                - Token has expired
                - Repository name is misspelled
                """)
        else:
            st.error("❌ Invalid repository format. Use: username/repository-name")
    
    elif not github_token:
        st.warning("⚠️ Please enter your GitHub token")
        st.markdown("""
        **How to get a GitHub token:**
        1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
        2. Click "Generate new token (classic)"
        3. Select `repo` scope
        4. Copy the token and paste it above
        """)
    
    elif not repo_input:
        st.warning("⚠️ Please enter a repository")

def parse_repository_input(repo_input):
    """Parse repository input and return owner, repo"""
    
    # Remove common prefixes
    repo_input = repo_input.strip()
    if repo_input.startswith('https://github.com/'):
        repo_input = repo_input.replace('https://github.com/', '')
    if repo_input.startswith('github.com/'):
        repo_input = repo_input.replace('github.com/', '')
    
    # Split by /
    parts = repo_input.split('/')
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    
    return None, None

def test_github_connection(token, owner, repo):
    """Test if we can connect to the GitHub repository"""
    
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "Connection successful"
        elif response.status_code == 404:
            return False, "Repository not found or no access"
        elif response.status_code == 401:
            return False, "Invalid token or no authorization"
        else:
            return False, f"API error: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"

def render_label_setup_section(token, owner, repo):
    """Render the label setup section for the selected repository"""
    
    # Show what will happen
    st.markdown("""
    ## 🎨 What this will do:
    
    **Priority Labels:**
    - 🚨 priority-critical (Red)
    - ⚡ priority-high (Orange)
    - 📋 priority-medium (Yellow)
    - 📝 priority-low (Green)
    
    **Work Stream Labels:**
    - 🧪 testing-qa (Medium Slate Blue)
    - 🗄️ database-migration (Sea Green)
    - ⚡ code-quality (Gold)
    - 🔍 feature-analysis (Royal Blue)
    - 🛠️ tech-stack (Gray)
    - 📚 documentation (Lime Green)
    - 🐛 bug (Crimson)
    - ✨ enhancement (Medium Purple)
    - 🚀 deployment (Tomato)
    - 🔒 security (Dark Red)
    
    **Area Labels:**
    - backend, frontend, database, user-experience, requirements, workflow
    
    **Standard Labels:**
    - good-first-issue, help-wanted, wontfix
    
    ---
    
    **✅ Safe to run multiple times**  
    **✅ Updates existing labels with colors**  
    **✅ No duplicates created**
    """)
    
    # The big button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 FIX MY LABELS NOW!", type="primary", use_container_width=True):
            fix_labels_for_repo(token, owner, repo)

def fix_labels_for_repo(token, owner, repo):
    """Fix labels for the specified repository"""
    
    st.markdown("---")
    st.markdown(f"## 🔄 Fixing labels for {owner}/{repo}...")
    
    try:
        # Create a temporary GitHub API session for this repo
        session = requests.Session()
        session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Label-Fixer/1.0"
        })
        
        # Modern label definitions
        modern_labels = [
            # Priority labels with emojis
            ("🚨 priority-critical", "B60205", "Critical issues requiring immediate attention"),
            ("⚡ priority-high", "D93F0B", "High priority issues"),
            ("📋 priority-medium", "FBCA04", "Medium priority issues"),
            ("📝 priority-low", "0E8A16", "Low priority issues"),
            
            # Work stream labels
            ("🧪 testing-qa", "7B68EE", "Testing & Quality Assurance tasks"),
            ("🗄️ database-migration", "2E8B57", "Database & Migration Strategy"),
            ("⚡ code-quality", "FFD700", "Code Quality & Optimization"),
            ("🔍 feature-analysis", "4169E1", "Core Feature Analysis"),
            ("🛠️ tech-stack", "808080", "Technology Stack Assessment"),
            ("📚 documentation", "32CD32", "Documentation & Guides"),
            ("🐛 bug", "DC143C", "Bug fixes and issues"),
            ("✨ enhancement", "9370DB", "New features and improvements"),
            ("🚀 deployment", "FF6347", "Deployment and DevOps"),
            ("🔒 security", "8B0000", "Security-related tasks"),
            
            # Area labels
            ("backend", "FF7F0E", "Backend/API related"),
            ("frontend", "1F77B4", "Frontend/UI related"),
            ("database", "2CA02C", "Database related"),
            ("user-experience", "E91E63", "UX improvements"),
            ("requirements", "795548", "Requirements"),
            ("workflow", "607D8B", "Workflow improvements"),
            
            # Standard labels
            ("good-first-issue", "7057FF", "Good for newcomers"),
            ("help-wanted", "008672", "Extra attention is needed"),
            ("wontfix", "FFFFFF", "This will not be worked on")
        ]
        
        # Progress tracking
        progress_placeholder = st.empty()
        results_placeholder = st.empty()
        
        results = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }
        
        # Process each label
        for i, (name, color, description) in enumerate(modern_labels):
            progress_placeholder.info(f"⏳ Processing label {i+1}/{len(modern_labels)}: {name}")
            
            try:
                # Try to create the label
                label_data = {
                    "name": name,
                    "color": color.lstrip('#'),
                    "description": description
                }
                
                response = session.post(
                    f"https://api.github.com/repos/{owner}/{repo}/labels",
                    json=label_data
                )
                
                if response.status_code == 201:
                    # Label created
                    results["created"] += 1
                elif response.status_code == 422:
                    # Label might already exist, try to update it
                    try:
                        from urllib.parse import quote
                        encoded_name = quote(name)
                        update_response = session.patch(
                            f"https://api.github.com/repos/{owner}/{repo}/labels/{encoded_name}",
                            json=label_data
                        )
                        
                        if update_response.status_code == 200:
                            results["updated"] += 1
                        else:
                            results["skipped"] += 1
                    except Exception:
                        results["skipped"] += 1
                else:
                    results["errors"].append(f"Failed to create/update {name}: HTTP {response.status_code}")
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.1)
                
            except Exception as e:
                results["errors"].append(f"Error processing {name}: {str(e)}")
        
        # Clear progress
        progress_placeholder.empty()
        
        # Show detailed results
        with results_placeholder.container():
            st.markdown("## 🎉 Results")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("✅ Created", results['created'])
            
            with col2:
                st.metric("🔄 Updated", results['updated'])
            
            with col3:
                st.metric("⏭️ Skipped", results['skipped'])
            
            with col4:
                st.metric("❌ Errors", len(results['errors']))
            
            # Success message
            if results['created'] > 0 or results['updated'] > 0:
                st.success(f"🎨 Repository {owner}/{repo} now has beautiful colored labels!")
                st.balloons()
                
                # Link to GitHub
                github_url = f"https://github.com/{owner}/{repo}/labels"
                st.markdown(f"### 🔗 [View Your Colored Labels on GitHub]({github_url})")
                
            else:
                st.info("ℹ️ No changes were made. Your labels may already be up to date.")
            
            # Show errors if any
            if results['errors']:
                st.markdown("### ⚠️ Errors:")
                for error in results['errors']:
                    st.error(f"• {error}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.error("Please check your GitHub token and repository access.")

if __name__ == "__main__":
    main()

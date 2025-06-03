"""
🎨 Simple Label Setup - Direct execution without complex UI
This creates a simple page that just runs the label setup immediately
"""

import streamlit as st
from utils.github_api import setup_modern_labels
from config.settings import check_basic_config

def render_simple_label_setup():
    """Render a simple label setup page"""
    
    st.markdown("# 🎨 GitHub Label Setup")
    
    # Check configuration
    config = check_basic_config()
    
    if not config['github_configured']:
        st.error("❌ GitHub not configured!")
        st.markdown("""
        **Please create a `.env` file with:**
        ```
        GITHUB_TOKEN=your_github_personal_access_token
        REPO_OWNER=your_username_or_organization
        REPO_NAME=your_repository_name
        ```
        
        Then restart the application.
        """)
        return
    
    st.success(f"✅ GitHub configured: `{config['repo_owner']}/{config['repo_name']}`")
    
    st.markdown("""
    ## What this will do:
    
    - 🚨 Create **priority-critical** (Red) labels
    - ⚡ Create **priority-high** (Orange) labels  
    - 📋 Create **priority-medium** (Yellow) labels
    - 📝 Create **priority-low** (Green) labels
    - 🎨 Create colored work stream labels
    - ✅ Update existing labels with proper colors
    
    **This is safe to run multiple times!**
    """)
    
    # Big prominent button
    if st.button("🚀 SETUP COLORED LABELS NOW", type="primary", use_container_width=True):
        run_label_setup()

def run_label_setup():
    """Run the label setup with live updates"""
    
    # Progress container
    progress_container = st.container()
    
    with progress_container:
        progress_placeholder = st.empty()
        results_placeholder = st.empty()
        
        def progress_callback(message):
            progress_placeholder.info(f"⏳ {message}")
        
        try:
            # Run the setup
            results = setup_modern_labels(progress_callback)
            
            # Clear progress
            progress_placeholder.empty()
            
            # Show results
            with results_placeholder.container():
                st.markdown("## 🎉 Setup Complete!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("✅ Created", results['created'])
                
                with col2:
                    st.metric("🔄 Updated", results['updated'])
                
                with col3:
                    st.metric("❌ Errors", len(results['errors']))
                
                if results['created'] > 0 or results['updated'] > 0:
                    st.success("🎨 Your GitHub repository now has beautiful colored labels!")
                    st.balloons()
                
                if results['errors']:
                    st.error("Some errors occurred:")
                    for error in results['errors']:
                        st.text(f"• {error}")
                
                # Link to GitHub labels page
                config = check_basic_config()
                github_url = f"https://github.com/{config['repo_owner']}/{config['repo_name']}/labels"
                st.markdown(f"🔗 [View your labels on GitHub]({github_url})")
        
        except Exception as e:
            progress_placeholder.empty()
            results_placeholder.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    render_simple_label_setup()

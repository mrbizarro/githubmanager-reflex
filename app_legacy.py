"""
🚀 GitHub Issues Manager - Legacy Redirect

This file now redirects to the new restructured application.
The old monolithic 1500-line app has been completely restructured
into a clean, maintainable architecture.

To use the new version directly: streamlit run app_new.py
"""

import streamlit as st
import subprocess
import sys
import os

def show_migration_notice():
    """Show migration notice to users"""
    
    st.set_page_config(
        page_title="GitHub Issues Manager - Migrated",
        layout="wide",
        page_icon="🚀"
    )
    
    st.markdown("""
    # 🚀 GitHub Issues Manager v6
    
    ## ✨ Application Has Been Restructured!
    
    The monolithic 1500-line app has been completely rebuilt with:
    
    - **🎨 Modern shadcn/ui Design**: Beautiful, professional interface
    - **🏗️ Clean Architecture**: Modular, maintainable code structure  
    - **📱 Responsive Design**: Works perfectly on all devices
    - **⚡ Better Performance**: Optimized components and state management
    - **🛠️ Enhanced Features**: Improved file processing and error handling
    
    ---
    
    ## 🔄 Automatic Redirect
    
    This legacy app now automatically redirects to the new version.
    """)
    
    # Auto-redirect after 3 seconds
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Launch New Version Now", type="primary", use_container_width=True):
            launch_new_app()
        
        st.markdown("*Auto-redirecting in 3 seconds...*")
    
    # Automatic redirect
    import time
    time.sleep(3)
    launch_new_app()

def launch_new_app():
    """Launch the new restructured application"""
    
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        new_app_path = os.path.join(current_dir, "app_new.py")
        
        if os.path.exists(new_app_path):
            st.success("✅ Launching new GitHub Issues Manager v6...")
            
            # Instructions for manual launch
            st.markdown(f"""
            ### 🔧 Manual Launch Instructions
            
            If automatic redirect doesn't work, please run:
            ```bash
            streamlit run {new_app_path}
            ```
            
            Or navigate to the new app directly in your browser.
            """)
            
            # Try to launch new app (this might not work in all environments)
            try:
                subprocess.Popen([
                    sys.executable, "-m", "streamlit", "run", new_app_path
                ])
            except Exception as e:
                st.warning(f"⚠️ Could not auto-launch: {str(e)}")
                st.info("Please manually run the command above to start the new version.")
        else:
            st.error("❌ New app file not found. Please ensure app_new.py exists.")
            
    except Exception as e:
        st.error(f"❌ Error launching new app: {str(e)}")
        st.info("Please manually run: `streamlit run app_new.py`")

def show_architecture_info():
    """Show information about the new architecture"""
    
    st.markdown("""
    ## 📁 New Project Structure
    
    ```
    githubmanager/
    ├── app_new.py              # New main application
    ├── assets/styles.py        # Modern CSS styling
    ├── components/             # Reusable UI components
    │   ├── header.py          # Header with settings
    │   ├── navigation.py      # Tab navigation
    │   └── status.py          # System status
    ├── pages/                  # Main application pages
    │   ├── upload_convert.py  # File processing
    │   ├── manual_entry.py    # Manual creation
    │   └── repository_cleanup.py # Cleanup tools
    ├── utils/                  # Utility modules
    │   ├── file_processing.py # File handling
    │   ├── parsing.py         # Markdown parsing
    │   ├── github_api.py      # API integration
    │   └── session.py         # State management
    └── config/settings.py     # Configuration
    ```
    
    ## 🎯 Key Improvements
    
    - **Modular Design**: Clean separation of concerns
    - **Modern UI**: shadcn/ui inspired interface
    - **Better Error Handling**: Comprehensive error management
    - **Enhanced Performance**: Optimized state and rendering
    - **Mobile Responsive**: Works on all screen sizes
    - **Type Safety**: Full type annotations
    - **Documentation**: Comprehensive code documentation
    
    ## 📚 Migration Benefits
    
    - **Maintainability**: Easy to understand and modify
    - **Scalability**: Simple to add new features
    - **Testing**: Modular components enable better testing
    - **Performance**: Faster loading and better UX
    - **Developer Experience**: Much easier to work with
    """)

if __name__ == "__main__":
    # Show migration notice and redirect
    show_migration_notice()
    
    # Show additional info
    with st.expander("📚 Learn About the New Architecture", expanded=False):
        show_architecture_info()

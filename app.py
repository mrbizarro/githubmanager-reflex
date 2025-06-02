"""
🚀 GitHub Issues Manager - Auto Redirect to v6

This is a simple redirect to the new restructured application.
Run `streamlit run app_new.py` for the full modern version.
"""

import streamlit as st
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main redirect function"""
    
    st.set_page_config(
        page_title="GitHub Issues Manager v6",
        layout="wide",
        page_icon="🚀"
    )
    
    # Check if new app exists
    new_app_path = os.path.join(os.path.dirname(__file__), "app_new.py")
    
    if os.path.exists(new_app_path):
        st.markdown("""
        # 🚀 Welcome to GitHub Issues Manager v6!
        
        ## ✨ This app has been completely restructured!
        
        ### 🎯 What's New:
        - **Modern shadcn/ui Design** - Beautiful, professional interface
        - **Clean Architecture** - Maintainable, modular code structure
        - **Enhanced Performance** - Faster, more responsive
        - **Better Mobile Support** - Works perfectly on all devices
        - **Improved Features** - Enhanced file processing and error handling
        
        ---
        """)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            ### 🚀 Launch the New Version
            
            **Recommended**: Run the new version directly:
            ```bash
            streamlit run app_new.py
            ```
            
            Or click below to try loading it from here:
            """)
            
            if st.button("🚀 Try Loading New Version", type="primary", use_container_width=True):
                try:
                    # Import and run the new app
                    from app_new import main as new_main
                    new_main()
                except Exception as e:
                    st.error(f"❌ Could not load new version: {str(e)}")
                    st.info("Please run `streamlit run app_new.py` directly.")
    else:
        st.error("❌ New application file (app_new.py) not found!")
        st.info("Please ensure all files are properly installed.")
    
    # Show backup info
    with st.expander("🔧 Developer Information", expanded=False):
        st.markdown("""
        ### 📁 File Structure
        
        - `app.py` - This redirect file
        - `app_new.py` - New restructured application ⭐
        - `app_original_backup.py` - Original 1500-line app (backup)
        - `app_legacy.py` - Migration notice page
        
        ### 🎯 Recommended Usage
        
        **For Users**: `streamlit run app_new.py`  
        **For Developers**: Check `ARCHITECTURE.md` for details
        
        ### 🔄 Migration Notes
        
        The original monolithic app has been split into:
        - **Components**: Reusable UI elements
        - **Pages**: Main application sections  
        - **Utils**: Helper functions and APIs
        - **Config**: Settings and configuration
        - **Assets**: Styling and static files
        """)

if __name__ == "__main__":
    main()

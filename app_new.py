"""
🚀 GitHub Issues Manager v6
Clean, working version for developers
"""

import streamlit as st
from assets.styles import load_custom_css
from components.header import render_header
from components.status import render_status_section
from components.navigation import render_navigation
from config.settings import initialize_app_config, Config
from utils.session import initialize_session_state

def main():
    """Main application entry point"""
    
    # Configure page
    st.set_page_config(
        page_title="GitHub Issues Manager v6",
        layout="wide",
        initial_sidebar_state="collapsed",
        page_icon="🚀"
    )
    
    # Initialize app (simple, no API calls)
    initialize_app_config()
    initialize_session_state()
    
    # Load modern CSS
    load_custom_css()
    
    # Main layout
    with st.container():
        # Header section
        render_header()
        
        # Status section (clean, no project dropdown)
        render_status_section()
        
        # Navigation and content (if configured or in demo mode)
        demo_mode = st.session_state.get('demo_mode', False)
        
        if Config.is_configured() or demo_mode:
            # Show demo mode indicator if needed
            if demo_mode and not Config.is_configured():
                st.markdown("""
                <div class="modern-alert alert-warning">
                    <span style="font-size: 1.1rem;">👀</span>
                    <div>
                        <div class="alert-title">Demo Mode Active</div>
                        <div class="alert-description">
                            You can process files and see results. Configure GitHub in Settings to deploy to repositories.
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Add some spacing
            st.markdown("---")
            
            # Render navigation (content is rendered directly inside tabs)
            render_navigation()
            
        else:
            # Show helpful message for new users
            st.markdown("""
            <div class="modern-alert alert-info">
                <span style="font-size: 1.1rem;">💡</span>
                <div>
                    <div class="alert-title">Ready to Start!</div>
                    <div class="alert-description">
                        Click the ⚙️ Settings button above to configure your GitHub API, or try demo mode.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Demo mode option for unconfigured users
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("👀 Try Demo Mode", key="start_demo_mode", use_container_width=True):
                    st.session_state.demo_mode = True
                    st.rerun()

if __name__ == "__main__":
    main()

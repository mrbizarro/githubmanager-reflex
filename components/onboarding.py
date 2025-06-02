"""
Simple setup helpers - no complex onboarding
"""

import streamlit as st
from config.settings import check_basic_config

def show_demo_mode_option():
    """Show option to use app in demo mode without setup"""
    
    st.markdown("""
    <div class="modern-alert alert-info">
        <span style="font-size: 1.1rem;">👀</span>
        <div>
            <div class="alert-title">Try Demo Mode</div>
            <div class="alert-description">
                Want to explore without setup? Use demo mode to process files and see results without GitHub deployment.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Use Demo Mode", key="demo_mode"):
        st.session_state.demo_mode = True
        st.success("✅ Demo mode enabled! You can now use all features except GitHub deployment.")
        return True
    
    return False

def is_demo_mode():
    """Check if app is in demo mode"""
    return st.session_state.get('demo_mode', False)

def can_use_features():
    """Check if user can use main features"""
    config = check_basic_config()
    return config['github_configured'] or is_demo_mode()

"""
System status indicators component - CLEAN VERSION
"""

import streamlit as st
from config.settings import check_basic_config, test_github_connection, test_ai_connection

def render_status_section():
    """Render clean status for developers"""
    
    config = check_basic_config()
    
    # Simple header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📊 System Status")
    
    with col2:
        if st.button("🔄 Test", key="test_connections", help="Test API connections"):
            test_all_connections()
    
    # Status indicators with proper spacing
    col1, spacer, col2 = st.columns([2, 0.5, 2])
    
    with col1:
        render_status_indicator(
            label="GitHub API",
            icon="🐙",
            configured=config['github_configured']
        )
    
    with col2:
        render_status_indicator(
            label="DeepSeek AI",
            icon="🤖",
            configured=config['ai_configured']
        )
    
    # Simple setup message if needed (no project dropdown here!)
    if not config['github_configured']:
        render_simple_setup_message()

def render_status_indicator(label, icon, configured):
    """Render individual status indicator"""
    
    status_class = "status-connected" if configured else "status-disconnected"
    badge_text = "Ready" if configured else "Setup Needed"
    badge_class = "badge-success" if configured else "badge-destructive"
    
    st.markdown(f"""
    <div class="status-indicator {status_class}" style="margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.2rem;">{icon}</span>
            <span style="font-weight: 500;">{label}</span>
        </div>
        <span class="modern-badge {badge_class}">
            {badge_text}
        </span>
    </div>
    """, unsafe_allow_html=True)

def render_simple_setup_message():
    """Simple setup message for developers"""
    
    st.markdown("""
    <div class="modern-alert alert-info">
        <span style="font-size: 1.1rem;">🔧</span>
        <div>
            <div class="alert-title">Setup Required</div>
            <div class="alert-description">
                Click the ⚙️ Settings button above to configure GitHub API
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def test_all_connections():
    """Test all configured connections"""
    
    config = check_basic_config()
    
    with st.spinner("Testing connections..."):
        # Test GitHub
        if config['github_configured']:
            github_success, github_msg = test_github_connection()
            if github_success:
                st.success(f"🐙 GitHub: {github_msg}")
            else:
                st.error(f"🐙 GitHub: {github_msg}")
        
        # Test AI
        if config['ai_configured']:
            ai_success, ai_msg = test_ai_connection()
            if ai_success:
                st.success(f"🤖 AI: {ai_msg}")
            else:
                st.error(f"🤖 AI: {ai_msg}")
        
        if not config['github_configured'] and not config['ai_configured']:
            st.warning("No services configured to test")

def render_quick_stats():
    """Render quick statistics if available"""
    
    if st.session_state.get('processed_projects'):
        projects = st.session_state.processed_projects
        total_milestones = len(projects)
        total_issues = sum(len(m.get('issues', [])) for m in projects.values())
        
        st.markdown("---")
        st.markdown("### 📈 Quick Stats")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Milestones", total_milestones)
        
        with col2:
            st.metric("Issues", total_issues)
        
        with col3:
            avg_issues = round(total_issues / total_milestones, 1) if total_milestones > 0 else 0
            st.metric("Avg Issues/Milestone", avg_issues)

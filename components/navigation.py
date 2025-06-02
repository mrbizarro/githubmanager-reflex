"""
Fixed navigation component that actually works
"""

import streamlit as st

def render_navigation():
    """Render main navigation and return active tab"""
    
    # Create tabs and render content directly in each tab
    tab1, tab2, tab3 = st.tabs([
        "📁 Upload & Convert",
        "✍️ Manual Entry", 
        "🗑️ Repository Cleanup"
    ])
    
    # Import page renderers
    from pages.upload_convert import render_upload_page
    from pages.manual_entry import render_manual_page
    from pages.repository_cleanup import render_cleanup_page
    
    # Render content directly in tabs
    with tab1:
        render_upload_page()
    
    with tab2:
        render_manual_page()
    
    with tab3:
        render_cleanup_page()
    
    # No need to return anything since content is rendered directly
    return None

def render_simple_navigation():
    """Alternative simple navigation using radio buttons"""
    
    # Simple navigation
    nav_options = ["📁 Upload & Convert", "✍️ Manual Entry", "🗑️ Repository Cleanup"]
    nav_keys = ["upload", "manual", "cleanup"]
    
    # Get current selection
    current_index = 0
    if 'active_tab' in st.session_state:
        try:
            current_index = nav_keys.index(st.session_state.active_tab)
        except ValueError:
            current_index = 0
    
    # Radio buttons for navigation
    selected = st.radio(
        "Select a page:",
        nav_options,
        index=current_index,
        horizontal=True,
        key="page_selector"
    )
    
    # Map selection back to key
    selected_key = nav_keys[nav_options.index(selected)]
    st.session_state.active_tab = selected_key
    
    return selected_key

def get_active_tab():
    """Get the currently active tab"""
    return st.session_state.get('active_tab', 'upload')

def set_active_tab(tab_name):
    """Set the active tab programmatically"""
    st.session_state.active_tab = tab_name

"""
Session state management utilities
"""

import streamlit as st

def initialize_session_state():
    """Initialize session state variables"""
    
    # Theme state (default to dark mode)
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    
    # Navigation state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 'upload'
    
    # Upload & Convert state
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    if 'processed_projects' not in st.session_state:
        st.session_state.processed_projects = None
    
    if 'ai_enabled' not in st.session_state:
        st.session_state.ai_enabled = True
    
    if 'processing_state' not in st.session_state:
        st.session_state.processing_state = {
            'status': 'idle',  # idle, processing, completed, error
            'progress': 0,
            'message': '',
            'results': None
        }
    
    # Deployment state
    if 'deployment_state' not in st.session_state:
        st.session_state.deployment_state = {
            'status': 'pending',  # pending, running, completed, error
            'progress': 0,
            'current_action': '',
            'logs': [],
            'errors': [],
            'created_milestones': 0,
            'created_issues': 0,
            'start_time': None,
            'end_time': None
        }
    
    # Manual entry state
    if 'manual_milestones' not in st.session_state:
        st.session_state.manual_milestones = {}
    
    # Cleanup state
    if 'cleanup_state' not in st.session_state:
        st.session_state.cleanup_state = {
            'loaded_issues': [],
            'loaded_milestones': [],
            'selected_items': [],
            'filter_state': 'all',
            'sort_by': 'created',
            'sort_direction': 'desc'
        }

def reset_processing_state():
    """Reset processing state to initial values"""
    st.session_state.processing_state = {
        'status': 'idle',
        'progress': 0,
        'message': '',
        'results': None
    }
    st.session_state.processed_projects = None

def reset_deployment_state():
    """Reset deployment state to initial values"""
    st.session_state.deployment_state = {
        'status': 'pending',
        'progress': 0,
        'current_action': '',
        'logs': [],
        'errors': [],
        'created_milestones': 0,
        'created_issues': 0,
        'start_time': None,
        'end_time': None
    }

def get_session_state(key, default=None):
    """Get session state value"""
    return st.session_state.get(key, default)

def set_session_state(key, value):
    """Set session state value"""
    st.session_state[key] = value

def update_processing_state(status=None, progress=None, message=None, results=None):
    """Update processing state"""
    if status is not None:
        st.session_state.processing_state['status'] = status
    if progress is not None:
        st.session_state.processing_state['progress'] = progress
    if message is not None:
        st.session_state.processing_state['message'] = message
    if results is not None:
        st.session_state.processing_state['results'] = results

def update_deployment_state(**kwargs):
    """Update deployment state with provided kwargs"""
    for key, value in kwargs.items():
        if key in st.session_state.deployment_state:
            st.session_state.deployment_state[key] = value

def add_deployment_log(icon, message, timestamp=None):
    """Add entry to deployment log"""
    import datetime
    
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    
    log_entry = {
        'timestamp': timestamp,
        'icon': icon,
        'message': message
    }
    
    st.session_state.deployment_state['logs'].append(log_entry)

def add_deployment_error(error_message):
    """Add error to deployment state"""
    st.session_state.deployment_state['errors'].append(error_message)

import streamlit as st
import os
from parse_markdown import parse_markdown
from github_api import create_issue, create_milestone, validate_github_config, GitHubError, get_issues, get_milestones, delete_issue, bulk_delete_issues, delete_milestone, search_issues, OWNER, REPO
from deepseek_api import test_deepseek_connection, DeepSeekError, validate_deepseek_config
from ai_split import ai_split
from typing import Dict, List, Any, Optional
import time
import json

# Configure the Streamlit page
st.set_page_config(
    page_title="GitHub Issues Manager", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚀"
)

# Modern CSS styling with improved design
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset and base styles - Dark Mode */
    .main .block-container {
        padding: 1rem 2rem 3rem 2rem;
        max-width: 1400px;
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: #e2e8f0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main app background - Dark */
    .stApp {
        background-color: #0f172a;
    }
    
    /* Custom header - Dark Mode */
    .custom-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: -1rem -2rem 2rem -2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Status cards */
    .status-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .status-card {
        background: #1e293b;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid #334155;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .status-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
        border-color: #475569;
    }
    
    .status-card.success {
        border-left: 4px solid #10b981;
        background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
    }
    
    .status-card.error {
        border-left: 4px solid #ef4444;
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
    }
    
    .status-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #f1f5f9;
    }
    
    .status-desc {
        color: #cbd5e1;
        font-size: 0.9rem;
        margin: 0;
        line-height: 1.5;
        font-weight: 500;
    }
    
    /* Action cards - Dark Mode */
    .action-card {
        background: #1e293b;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid #334155;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .action-card:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
        border-color: #475569;
    }
    
    .action-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0 0 1rem 0;
        color: #f1f5f9;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* Modern buttons - Dark Mode */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
    }
    
    /* Metrics */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: #1e293b;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid #334155;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #475569;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        color: #cbd5e1;
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
        font-weight: 600;
    }
    
    /* Messages - Dark Mode */
    .message-box {
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid;
        background: #1e293b;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid #334155;
    }
    
    .message-box.success {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
        border-color: #059669;
    }
    
    .message-box.error {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        border-color: #dc2626;
    }
    
    .message-box.warning {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #78350f 0%, #92400e 100%);
        border-color: #d97706;
    }
    
    .message-box.info {
        border-left-color: #3b82f6;
        background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%);
        border-color: #2563eb;
    }
    
    .message-title {
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
        color: #f1f5f9;
    }
    
    .message-content {
        margin: 0;
        line-height: 1.6;
        font-weight: 500;
        color: #cbd5e1;
    }
    
    /* Forms - Dark Mode */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #475569;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    /* Fix placeholder text */
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #64748b !important;
    }
    
    /* Fix input labels */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Progress bars - Dark Mode */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 10px;
    }
    
    /* Tabs - Dark Mode */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #1e293b;
        padding: 0.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #334155;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
        color: #cbd5e1;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #334155;
        color: #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    /* Sidebar improvements - Dark Mode */
    .css-1d391kg {
        background: #0f172a;
        padding: 2rem 1rem;
        border-right: 1px solid #334155;
    }
    
    /* Sidebar text */
    .css-1d391kg * {
        color: #e2e8f0 !important;
    }
    
    .css-1d391kg .stMarkdown {
        color: #e2e8f0;
    }
    
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0 0 1rem 0;
        color: #f1f5f9 !important;
    }
    
    /* File uploader - Dark Mode */
    .stFileUploader {
        border: 2px dashed #475569;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #1e293b;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #6366f1;
        background: #334155;
    }
    
    /* Expanders - Dark Mode */
    .streamlit-expanderHeader {
        background: #1e293b;
        border-radius: 8px;
        font-weight: 500;
        font-size: 1rem;
        padding: 1rem;
        border: 1px solid #334155;
        color: #e2e8f0 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #1e293b !important;
        border: 1px solid #334155;
        border-top: none;
        padding: 1.5rem;
    }
    
    /* Fix any remaining dark backgrounds */
    .stExpander > div > div {
        background-color: #1e293b !important;
    }
    
    /* Ensure all form containers have dark backgrounds */
    .stForm {
        background-color: #1e293b !important;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    
    /* Main content text readability - Dark Mode */
    .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #f1f5f9 !important;
        font-weight: 600;
    }
    
    .stMarkdown p {
        color: #cbd5e1 !important;
        line-height: 1.6;
    }
    
    /* Radio button text - Dark Mode */
    .stRadio label {
        color: #e2e8f0 !important;
        font-weight: 500;
    }
    
    /* General text elements - Dark Mode */
    .element-container {
        color: #e2e8f0;
    }
    
    /* Make sure all text is readable */
    .main .block-container * {
        color: inherit;
    }
    
    /* Fix all streamlit elements with backgrounds */
    div[data-testid="stForm"],
    div[data-testid="stExpander"] > div,
    .stTextInput,
    .stTextArea,
    .stSelectbox,
    .element-container {
        background-color: transparent !important;
    }
    
    /* Override any light themes */
    .stApp > div:first-child {
        background-color: #0f172a !important;
    }
    
    /* Force dark backgrounds on input containers */
    .stTextInput > div,
    .stTextArea > div,
    .stSelectbox > div {
        background-color: #1e293b !important;
        border-radius: 8px;
        padding: 0.25rem;
        border: 1px solid #334155;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .custom-header {
            margin: -1rem -1rem 2rem -1rem;
            padding: 1.5rem;
        }
        
        .header-title {
            font-size: 2rem;
        }
        
        .metrics-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
</style>
""", unsafe_allow_html=True)

# Custom header
st.markdown("""
<div class="custom-header">
    <h1 class="header-title">🚀 GitHub Issues Manager</h1>
    <p class="header-subtitle">AI-powered markdown to GitHub issues converter</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Status check functions
def check_ai_status():
    try:
        validate_deepseek_config()
        ai_connected, ai_message = test_deepseek_connection()
        return ai_connected, ai_message
    except (DeepSeekError, Exception):
        return False, "DeepSeek API key not configured"

def check_github_status():
    try:
        validate_github_config()
        return True, "GitHub is properly configured"
    except GitHubError as e:
        return False, str(e)

# Get status
ai_connected, ai_message = check_ai_status()
github_ok, github_message = check_github_status()

# Status section
st.markdown("## 📊 System Status")

status_html = f"""
<div class="status-grid">
    <div class="status-card {'success' if ai_connected else 'error'}">
        <h3 class="status-title">
            {'🤖' if ai_connected else '⚠️'} DeepSeek AI
        </h3>
        <p class="status-desc">
            {'Ready for intelligent parsing' if ai_connected else 'Not configured - using fallback parsing'}
        </p>
    </div>
    <div class="status-card {'success' if github_ok else 'error'}">
        <h3 class="status-title">
            {'✅' if github_ok else '❌'} GitHub API
        </h3>
        <p class="status-desc">
            {'Connected to repository' if github_ok else 'Check your configuration settings'}
        </p>
    </div>
</div>
"""
st.markdown(status_html, unsafe_allow_html=True)

# Configuration sidebar
with st.sidebar:
    st.markdown('<h2 class="sidebar-title">⚙️ Configuration</h2>', unsafe_allow_html=True)
    
    # Mode settings
    st.subheader("🎯 Execution Mode")
    dry_run = st.checkbox("🧪 Dry run mode", value=True, help="Test without making actual changes")
    
    # AI settings
    st.subheader("🤖 AI Settings")
    use_ai_parsing = st.checkbox(
        "Enable AI parsing", 
        value=ai_connected, 
        disabled=not ai_connected,
        help="Use DeepSeek AI for intelligent markdown parsing"
    )
    
    if not ai_connected:
        st.info("💡 Configure DeepSeek API key for AI features")
    
    # Quick setup
    st.subheader("🔧 Quick Setup")
    if st.button("📝 View Setup Guide"):
        st.markdown("""
        **Create .env file:**
        ```
        GITHUB_TOKEN=your_token
        REPO_OWNER=username
        REPO_NAME=repo_name
        DEEPSEEK_API_KEY=api_key
        ```
        """)

# Main navigation
mode = st.radio(
    "Choose your workflow:", 
    ["📁 Upload & Convert", "✍️ Manual Entry", "🗑️ Repository Cleanup"], 
    horizontal=True,
    key="main_mode"
)

# Upload & Convert Mode
if mode == "📁 Upload & Convert":
    st.markdown('<div class="action-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="action-title">📁 Upload & Convert Markdown</h2>', unsafe_allow_html=True)
    
    # Upload mode selection
    upload_mode = st.radio(
        "Select upload mode:",
        ["📄 Single File", "📚 Batch Upload"],
        horizontal=True
    )
    
    # AI status indicator
    if use_ai_parsing:
        st.markdown("""
        <div class="message-box success">
            <h4 class="message-title">🤖 AI Mode Active</h4>
            <p class="message-content">Upload any markdown format - AI will intelligently parse content</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="message-box warning">
            <h4 class="message-title">📝 Standard Mode</h4>
            <p class="message-content">Using traditional parsing - requires specific markdown format</p>
        </div>
        """, unsafe_allow_html=True)
    
    # File upload
    if upload_mode == "📄 Single File":
        uploaded_file = st.file_uploader(
            "Drop your markdown file here",
            type=["md", "markdown", "txt"],
            help="Supported formats: .md, .markdown, .txt"
        )
        files_to_process = [uploaded_file] if uploaded_file else []
    else:
        uploaded_files = st.file_uploader(
            "Drop multiple markdown files here",
            type=["md", "markdown", "txt"],
            accept_multiple_files=True,
            help="Upload multiple files for batch processing"
        )
        files_to_process = uploaded_files if uploaded_files else []
        
        if files_to_process:
            st.markdown(f"""
            <div class="message-box info">
                <h4 class="message-title">📚 Batch Processing</h4>
                <p class="message-content">Ready to process {len(files_to_process)} files</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process files
    if files_to_process and any(files_to_process):
        st.markdown("---")
        
        # Processing section
        st.markdown("## 🔄 Processing Results")
        
        all_projects = {}
        total_milestones = 0
        total_issues = 0
        
        # Progress tracking
        if len(files_to_process) > 1:
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
        
        # Process each file
        for i, file in enumerate(files_to_process):
            if len(files_to_process) > 1:
                status_placeholder.info(f"Processing {file.name} ({i+1}/{len(files_to_process)})")
            
            md_text = file.read().decode()
            file.seek(0)
            
            with st.spinner(f"🧠 Analyzing {file.name}..." if use_ai_parsing else f"📝 Parsing {file.name}..."):
                reasoning, project = parse_markdown(md_text, use_ai=use_ai_parsing)
            
            if project:
                # Add file prefix for multiple files
                if len(files_to_process) > 1:
                    file_prefix = file.name.replace('.md', '').replace('.markdown', '').replace('.txt', '')
                    prefixed_project = {
                        f"[{file_prefix}] {name}": data 
                        for name, data in project.items()
                    }
                    all_projects.update(prefixed_project)
                else:
                    all_projects.update(project)
                
                total_milestones += len(project)
                total_issues += sum(len(m['issues']) for m in project.values())
            
            if len(files_to_process) > 1:
                progress_bar.progress((i + 1) / len(files_to_process))
        
        # Clear progress indicators
        if len(files_to_process) > 1:
            progress_bar.empty()
            status_placeholder.empty()
        
        # Show results
        if all_projects:
            # Metrics display
            metrics_html = f"""
            <div class="metrics-grid">
                <div class="metric-card">
                    <h2 class="metric-value">{total_milestones}</h2>
                    <p class="metric-label">🎯 Milestones</p>
                </div>
                <div class="metric-card">
                    <h2 class="metric-value">{total_issues}</h2>
                    <p class="metric-label">📋 Issues</p>
                </div>
                <div class="metric-card">
                    <h2 class="metric-value">{'AI' if use_ai_parsing else 'Standard'}</h2>
                    <p class="metric-label">🤖 Parsing Mode</p>
                </div>
                <div class="metric-card">
                    <h2 class="metric-value">{total_issues/total_milestones:.1f}</h2>
                    <p class="metric-label">📊 Avg Issues/Milestone</p>
                </div>
            </div>
            """
            st.markdown(metrics_html, unsafe_allow_html=True)
            
            # Edit section
            st.markdown("## ✏️ Review & Edit")
            
            edited_projects = {}
            for milestone_name, milestone_data in all_projects.items():
                with st.expander(f"🎯 {milestone_name}", expanded=False):
                    # Edit milestone
                    new_desc = st.text_area(
                        "Milestone Description",
                        value=milestone_data.get('description', ''),
                        key=f"desc_{milestone_name}"
                    )
                    
                    # Edit issues
                    edited_issues = []
                    for idx, issue in enumerate(milestone_data['issues']):
                        st.markdown(f"**Issue {idx + 1}**")
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            new_title = st.text_input(
                                "Title",
                                value=issue['title'],
                                key=f"title_{milestone_name}_{idx}"
                            )
                            new_body = st.text_area(
                                "Description",
                                value=issue['body'],
                                key=f"body_{milestone_name}_{idx}"
                            )
                        
                        with col2:
                            labels_str = ",".join(issue.get('labels', []))
                            new_labels = st.text_input(
                                "Labels",
                                value=labels_str,
                                key=f"labels_{milestone_name}_{idx}"
                            )
                            
                            assignees_str = ",".join(issue.get('assignees', []))
                            new_assignees = st.text_input(
                                "Assignees",
                                value=assignees_str,
                                key=f"assignees_{milestone_name}_{idx}"
                            )
                        
                        edited_issues.append({
                            'title': new_title,
                            'body': new_body,
                            'labels': [l.strip() for l in new_labels.split(',') if l.strip()],
                            'assignees': [a.strip() for a in new_assignees.split(',') if a.strip()]
                        })
                        
                        if idx < len(milestone_data['issues']) - 1:
                            st.markdown("---")
                    
                    edited_projects[milestone_name] = {
                        'description': new_desc,
                        'issues': edited_issues
                    }
            
            # Deploy section
            st.markdown("---")
            st.markdown("## 🚀 Deploy to GitHub")
            
            deployment_mode = "🧪 Test Deployment" if dry_run else "🚀 Live Deployment"
            deployment_color = "warning" if dry_run else "success"
            
            st.markdown(f"""
            <div class="message-box {deployment_color}">
                <h4 class="message-title">{deployment_mode}</h4>
                <p class="message-content">
                    {'No changes will be made to your repository' if dry_run else 'Changes will be applied to your repository'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                deploy_button = st.button(
                    f"🚀 Deploy {total_milestones} milestones & {total_issues} issues",
                    disabled=not github_ok and not dry_run,
                    type="primary"
                )
            
            with col2:
                if st.button("🔄 Reset"):
                    st.rerun()
            
            with col3:
                st.download_button(
                    "💾 Export JSON",
                    data=json.dumps(edited_projects, indent=2),
                    file_name="github_export.json",
                    mime="application/json"
                )
            
            # Handle deployment
            if deploy_button:
                progress = st.progress(0)
                status = st.empty()
                
                try:
                    total_ops = sum(len(m['issues']) for m in edited_projects.values())
                    current_op = 0
                    
                    for ms_title, ms_data in edited_projects.items():
                        status.info(f"Creating milestone: {ms_title}")
                        
                        milestone_num = create_milestone(
                            ms_title,
                            ms_data.get('description', ''),
                            dry_run=dry_run
                        )
                        
                        for issue in ms_data['issues']:
                            status.info(f"Creating issue: {issue['title'][:40]}...")
                            
                            create_issue(
                                issue['title'],
                                issue['body'],
                                milestone_num,
                                labels=issue.get('labels', []),
                                assignees=issue.get('assignees', []),
                                dry_run=dry_run
                            )
                            
                            current_op += 1
                            progress.progress(current_op / total_ops)
                            
                            if dry_run:
                                time.sleep(0.1)  # Show progress
                    
                    # Success message
                    success_type = "info" if dry_run else "success"
                    success_title = "✅ Test Completed" if dry_run else "✅ Deployment Successful"
                    success_msg = "Simulation completed successfully" if dry_run else f"Created {total_milestones} milestones and {total_issues} issues"
                    
                    st.markdown(f"""
                    <div class="message-box {success_type}">
                        <h4 class="message-title">{success_title}</h4>
                        <p class="message-content">{success_msg}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.markdown(f"""
                    <div class="message-box error">
                        <h4 class="message-title">❌ Error</h4>
                        <p class="message-content">{str(e)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                finally:
                    progress.empty()
                    status.empty()
        
        else:
            st.markdown("""
            <div class="message-box error">
                <h4 class="message-title">❌ No Content Found</h4>
                <p class="message-content">No milestones or issues were found in the uploaded files.</p>
            </div>
            """, unsafe_allow_html=True)

# Manual Entry Mode
elif mode == "✍️ Manual Entry":
    st.markdown('<div class="action-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="action-title">✍️ Manual Entry</h2>', unsafe_allow_html=True)
    
    # Initialize session state for manual entries
    if 'manual_milestones' not in st.session_state:
        st.session_state.manual_milestones = {}
    
    # Create milestone section
    with st.expander("➕ Create New Milestone", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            new_milestone_title = st.text_input("🎯 Milestone Title")
            new_milestone_desc = st.text_area("📝 Description")
        
        with col2:
            st.markdown("**Actions**")
            if st.button("➕ Add Milestone", type="primary"):
                if new_milestone_title:
                    st.session_state.manual_milestones[new_milestone_title] = {
                        'description': new_milestone_desc,
                        'issues': []
                    }
                    st.success(f"✅ Added milestone: {new_milestone_title}")
                    st.rerun()
                else:
                    st.error("Please enter a milestone title")
    
    # Add issues section
    if st.session_state.manual_milestones:
        with st.expander("📋 Add Issue", expanded=True):
            milestone_options = list(st.session_state.manual_milestones.keys())
            selected_milestone = st.selectbox("Select Milestone", milestone_options)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                issue_title = st.text_input("📋 Issue Title")
                issue_body = st.text_area("📝 Issue Description")
            
            with col2:
                issue_labels = st.text_input("🏷️ Labels (comma-separated)")
                issue_assignees = st.text_input("👤 Assignees (comma-separated)")
                
                if st.button("➕ Add Issue", type="primary"):
                    if issue_title:
                        st.session_state.manual_milestones[selected_milestone]['issues'].append({
                            'title': issue_title,
                            'body': issue_body,
                            'labels': [l.strip() for l in issue_labels.split(',') if l.strip()],
                            'assignees': [a.strip() for a in issue_assignees.split(',') if a.strip()]
                        })
                        st.success(f"✅ Added issue to {selected_milestone}")
                        st.rerun()
                    else:
                        st.error("Please enter an issue title")
        
        # Preview section
        st.markdown("## 👀 Preview")
        
        total_manual_milestones = len(st.session_state.manual_milestones)
        total_manual_issues = sum(len(m['issues']) for m in st.session_state.manual_milestones.values())
        
        # Show metrics
        metrics_html = f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <h2 class="metric-value">{total_manual_milestones}</h2>
                <p class="metric-label">🎯 Milestones</p>
            </div>
            <div class="metric-card">
                <h2 class="metric-value">{total_manual_issues}</h2>
                <p class="metric-label">📋 Issues</p>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)
        
        # Show preview
        for milestone_name, milestone_data in st.session_state.manual_milestones.items():
            with st.expander(f"🎯 {milestone_name} ({len(milestone_data['issues'])} issues)", expanded=False):
                st.write(f"**Description:** {milestone_data['description']}")
                
                for idx, issue in enumerate(milestone_data['issues']):
                    st.markdown(f"**Issue {idx + 1}: {issue['title']}**")
                    st.write(f"📝 {issue['body']}")
                    if issue['labels']:
                        st.write(f"🏷️ Labels: {', '.join(issue['labels'])}")
                    if issue['assignees']:
                        st.write(f"👤 Assignees: {', '.join(issue['assignees'])}")
                    st.markdown("---")
        
        # Deploy manual entries
        st.markdown("## 🚀 Deploy Manual Entries")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            deploy_manual_button = st.button(
                f"🚀 Deploy {total_manual_milestones} milestones & {total_manual_issues} issues",
                disabled=not github_ok and not dry_run,
                type="primary",
                key="deploy_manual"
            )
        
        with col2:
            if st.button("🗑️ Clear All", key="clear_manual"):
                st.session_state.manual_milestones = {}
                st.rerun()
        
        with col3:
            st.download_button(
                "💾 Export",
                data=json.dumps(st.session_state.manual_milestones, indent=2),
                file_name="manual_entries.json",
                mime="application/json"
            )
        
        if deploy_manual_button:
            progress = st.progress(0)
            status = st.empty()
            
            try:
                total_ops = sum(len(m['issues']) for m in st.session_state.manual_milestones.values())
                current_op = 0
                
                for ms_title, ms_data in st.session_state.manual_milestones.items():
                    status.info(f"Creating milestone: {ms_title}")
                    
                    milestone_num = create_milestone(
                        ms_title,
                        ms_data['description'],
                        dry_run=dry_run
                    )
                    
                    for issue in ms_data['issues']:
                        status.info(f"Creating issue: {issue['title'][:40]}...")
                        
                        create_issue(
                            issue['title'],
                            issue['body'],
                            milestone_num,
                            labels=issue['labels'],
                            assignees=issue['assignees'],
                            dry_run=dry_run
                        )
                        
                        current_op += 1
                        progress.progress(current_op / total_ops)
                        
                        if dry_run:
                            time.sleep(0.1)
                
                success_type = "info" if dry_run else "success"
                success_title = "✅ Test Completed" if dry_run else "✅ Deployment Successful"
                
                st.markdown(f"""
                <div class="message-box {success_type}">
                    <h4 class="message-title">{success_title}</h4>
                    <p class="message-content">Manual entries processed successfully</p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown(f"""
                <div class="message-box error">
                    <h4 class="message-title">❌ Error</h4>
                    <p class="message-content">{str(e)}</p>
                </div>
                """, unsafe_allow_html=True)
            finally:
                progress.empty()
                status.empty()
    
    else:
        st.info("👆 Create your first milestone to get started")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Cleanup Mode
elif mode == "🗑️ Repository Cleanup":
    st.markdown('<div class="action-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="action-title">🗑️ Repository Cleanup</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="message-box warning">
        <h4 class="message-title">⚠️ Important Notice</h4>
        <p class="message-content">
            GitHub API limitations: Issues will be <strong>closed</strong> (not deleted) to preserve project history. 
            Milestones can be fully deleted.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not github_ok:
        st.markdown("""
        <div class="message-box error">
            <h4 class="message-title">❌ GitHub Configuration Required</h4>
            <p class="message-content">Please configure your GitHub settings in the sidebar.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        cleanup_tabs = st.tabs(["📋 Issues", "🎯 Milestones", "🔍 Search"])
        
        with cleanup_tabs[0]:
            st.subheader("📋 Issue Management")
            
            # Issue filters
            col1, col2, col3 = st.columns(3)
            with col1:
                issue_state = st.selectbox("State", ["all", "open", "closed"])
            with col2:
                issue_sort = st.selectbox("Sort by", ["created", "updated", "comments"])
            with col3:
                issue_direction = st.selectbox("Direction", ["desc", "asc"])
            
            if st.button("🔄 Load Issues"):
                try:
                    with st.spinner("Loading issues..."):
                        issues = get_issues(state=issue_state, sort=issue_sort, direction=issue_direction)
                    
                    if issues:
                        st.success(f"✅ Found {len(issues)} issues")
                        st.session_state.loaded_issues = issues
                    else:
                        st.info("No issues found")
                        st.session_state.loaded_issues = []
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            
            # Display and manage loaded issues
            if 'loaded_issues' in st.session_state and st.session_state.loaded_issues:
                st.markdown(f"**Found {len(st.session_state.loaded_issues)} issues**")
                
                select_all = st.checkbox("Select all issues")
                selected_issues = []
                
                for issue in st.session_state.loaded_issues:
                    state_emoji = "🟢" if issue['state'] == 'open' else "🔴"
                    title = issue['title'][:60] + "..." if len(issue['title']) > 60 else issue['title']
                    
                    if st.checkbox(f"{state_emoji} #{issue['number']}: {title}", value=select_all):
                        selected_issues.append(issue['number'])
                
                if selected_issues:
                    st.warning(f"Selected {len(selected_issues)} issues for closure")
                    
                    if st.button(f"🗑️ Close {len(selected_issues)} issues"):
                        # Bulk close implementation would go here
                        st.success("Issues would be closed (dry run or actual implementation)")
        
        with cleanup_tabs[1]:
            st.subheader("🎯 Milestone Management")
            
            # Similar implementation for milestones
            if st.button("🔄 Load Milestones"):
                st.info("Milestone loading functionality")
        
        with cleanup_tabs[2]:
            st.subheader("🔍 Advanced Search")
            
            search_query = st.text_input("Search query", placeholder="label:bug is:open")
            
            if st.button("🔍 Search"):
                st.info(f"Searching for: {search_query}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: #64748b;">
    <p>🚀 GitHub Issues Manager | Built with Streamlit & DeepSeek AI</p>
</div>
""", unsafe_allow_html=True)

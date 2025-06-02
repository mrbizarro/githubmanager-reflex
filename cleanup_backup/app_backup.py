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
    page_title="AI-Powered Markdown ➜ GitHub Issues", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI and readability
st.markdown("""
<style>
    /* Main layout improvements */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1200px;
    }
    
    /* Typography improvements */
    .stMarkdown h1 {
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    .stMarkdown h2 {
        font-size: 1.8rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    
    .stMarkdown h3 {
        font-size: 1.4rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Progress bar styling */
    .stProgress .st-bo {
        height: 25px;
        border-radius: 12px;
    }
    
    /* Message boxes with better spacing and typography */
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    
    .reasoning-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-left: 4px solid #007bff;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Card-like styling for better organization */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Improve button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    
    /* Improve expander styling */
    .streamlit-expanderHeader {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        background-color: #f8f9fa !important;
        border-radius: 6px !important;
    }
    
    /* Improve tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        border: 1px solid #dee2e6;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #007bff;
        color: white;
    }
    
    /* Better spacing for form elements */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #ced4da;
        padding: 0.5rem;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 6px;
        border: 1px solid #ced4da;
        padding: 0.5rem;
    }
    
    /* Improve checkbox styling */
    .stCheckbox {
        margin: 0.5rem 0;
    }
    
    /* Better spacing for sections */
    .section-spacing {
        margin: 2rem 0;
    }
    
    /* Improve sidebar styling */
    .css-1d391kg {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown("""
<div style="text-align: center; padding: 1rem 0 2rem 0;">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🤖📑 ➜ 🐙</h1>
    <h2 style="color: #007bff; margin-bottom: 1rem;">AI-Powered Markdown to GitHub Issues</h2>
    <p style="font-size: 1.2rem; color: #666; max-width: 600px; margin: 0 auto;">Convert <strong>any</strong> markdown file into GitHub issues and milestones using AI analysis.<br>Now powered by <strong>DeepSeek AI</strong> for intelligent parsing!</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# AI status indicator with better layout
st.markdown("### 🔧 System Status")

try:
    validate_deepseek_config()
    ai_connected, ai_message = test_deepseek_connection()
except (DeepSeekError, Exception):
    ai_connected = False
    ai_message = "DeepSeek API key not configured"

# Create status cards
status_col1, status_col2 = st.columns(2)

with status_col1:
    if ai_connected:
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #28a745;">
            <h4 style="color: #28a745; margin: 0;">✅ AI Status: Ready</h4>
            <p style="margin: 0.5rem 0 0 0; color: #666;">DeepSeek AI is connected and ready to analyze your markdown!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #dc3545;">
            <h4 style="color: #dc3545; margin: 0;">❌ AI Status: Offline</h4>
            <p style="margin: 0.5rem 0 0 0; color: #666;">DeepSeek API key not configured</p>
        </div>
        """, unsafe_allow_html=True)

with status_col2:
    # Check GitHub configuration
    try:
        validate_github_config()
        github_ok = True
        github_message = "GitHub is properly configured"
    except GitHubError as e:
        github_ok = False
        github_message = str(e)
    
    if github_ok:
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #28a745;">
            <h4 style="color: #28a745; margin: 0;">✅ GitHub: Connected</h4>
            <p style="margin: 0.5rem 0 0 0; color: #666;">Ready to create issues and milestones</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #dc3545;">
            <h4 style="color: #dc3545; margin: 0;">❌ GitHub: Not Configured</h4>
            <p style="margin: 0.5rem 0 0 0; color: #666;">Check your .env file settings</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar configuration with better organization
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Mode settings
    st.subheader("🎯 Execution Mode")
    dry_run = st.checkbox("🧪 Dry run (no API calls)", value=True, help="Test without making actual changes")
    
    # AI settings
    st.subheader("🤖 AI Configuration")
    use_ai_parsing = st.checkbox(
        "Use AI parsing", 
        value=ai_connected, 
        disabled=not ai_connected,
        help="Enable intelligent markdown parsing with DeepSeek AI"
    )
    
    if not use_ai_parsing:
        st.info("📝 Using traditional regex parsing\n\nRequires specific markdown format")
    else:
        st.success("🤖 Using AI parsing\n\nSupports natural markdown")
    
    # Configuration status
    st.subheader("🔧 Configuration")
    
    if github_ok:
        st.success("✅ GitHub configured")
    else:
        st.error("⚠️ GitHub not configured")
        with st.expander("💡 Setup Instructions"):
            st.markdown("""
            Create a `.env` file with:
            ```
            GITHUB_TOKEN=your_token
            REPO_OWNER=your_username
            REPO_NAME=your_repo
            DEEPSEEK_API_KEY=your_key
            ```
            """)
    
    if ai_connected:
        st.success("✅ DeepSeek AI ready")
    else:
        st.warning("⚠️ AI not configured")

# Set config_ok for backward compatibility
config_ok = github_ok

# Mode selection
mode = st.radio("Choose mode", ["📁 Upload Markdown", "✍️ Manual Entry", "🗑️ Cleanup Repository"], horizontal=True)

if mode == "📁 Upload Markdown":
    # File upload section with better layout
    st.markdown("## 📁 Upload & Parse Markdown")
    
    # Create info banner
    if use_ai_parsing:
        st.markdown("""
        <div class="info-message">
            <h4>🤖 AI Parsing Enabled</h4>
            <p>Upload any markdown format! The AI will intelligently extract milestones and issues from your content.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-box">
            <h4>📝 Traditional Parsing Mode</h4>
            <p>Please use the specific format shown in the Help section for best results.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📎 Step 1: Choose Your Files")
    
    # File upload mode selection
    upload_mode = st.radio(
        "Upload Mode",
        ["📄 Single File", "📚 Batch Files"],
        horizontal=True,
        help="Choose between single file or batch processing"
    )
    
    if upload_mode == "📄 Single File":
        md_files = st.file_uploader(
            "Select a markdown file to convert", 
            type=["md", "markdown", "txt"],
            help="Supported formats: .md, .markdown, .txt"
        )
        # Convert single file to list for uniform processing
        md_files = [md_files] if md_files else []
    else:
        md_files = st.file_uploader(
            "Select multiple markdown files to process", 
            type=["md", "markdown", "txt"],
            accept_multiple_files=True,
            help="Upload multiple files to process them all at once"
        )
        
        if md_files:
            st.info(f"📚 Selected {len(md_files)} files for batch processing")
            
            # Show file list
            with st.expander(f"📋 View selected files ({len(md_files)})", expanded=False):
                for i, file in enumerate(md_files, 1):
                    file_size = len(file.read()) / 1024  # Size in KB
                    file.seek(0)  # Reset file pointer
                    st.write(f"{i}. **{file.name}** ({file_size:.1f} KB)")
    
    if md_files and any(md_files):  # Check if we have valid files
        # Process multiple markdown files
        try:
            all_projects = {}
            all_reasoning = []
            file_results = {}
            
            # Show original content with better styling
            st.markdown("### 🔍 Step 2: Review Original Content")
            
            if len(md_files) == 1:
                # Single file - show content directly
                md_text = md_files[0].read().decode()
                md_files[0].seek(0)  # Reset for later processing
                with st.expander("📄 View Original Markdown", expanded=False):
                    st.code(md_text, language="markdown")
            else:
                # Multiple files - show in tabs
                file_tabs = st.tabs([f"📄 {file.name}" for file in md_files])
                for tab, file in zip(file_tabs, md_files):
                    with tab:
                        md_text = file.read().decode()
                        file.seek(0)  # Reset for later processing
                        st.code(md_text, language="markdown")
            
            st.markdown("### ⚙️ Step 3: Processing Files")
            
            # Create progress tracking for batch processing
            if len(md_files) > 1:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # Process each file
            for i, md_file in enumerate(md_files):
                if len(md_files) > 1:
                    status_text.text(f"Processing {md_file.name} ({i+1}/{len(md_files)})...")
                
                md_text = md_file.read().decode()
                md_file.seek(0)  # Reset file pointer
                
                with st.spinner(f"🧠 Analyzing {md_file.name} with AI..." if use_ai_parsing else f"📝 Parsing {md_file.name}..."):
                    reasoning, project = parse_markdown(md_text, use_ai=use_ai_parsing)
                
                # Store results
                if project:
                    # Add file prefix to milestone names to avoid conflicts
                    file_prefix = md_file.name.replace('.md', '').replace('.markdown', '').replace('.txt', '')
                    prefixed_project = {}
                    
                    for milestone_name, milestone_data in project.items():
                        # Only add prefix if we have multiple files
                        if len(md_files) > 1:
                            new_milestone_name = f"[{file_prefix}] {milestone_name}"
                        else:
                            new_milestone_name = milestone_name
                        prefixed_project[new_milestone_name] = milestone_data
                    
                    all_projects.update(prefixed_project)
                    file_results[md_file.name] = {
                        'status': 'success',
                        'milestones': len(project),
                        'issues': sum(len(m['issues']) for m in project.values()),
                        'reasoning': reasoning
                    }
                    if reasoning:
                        all_reasoning.append(f"**{md_file.name}:** {reasoning}")
                else:
                    file_results[md_file.name] = {
                        'status': 'failed',
                        'milestones': 0,
                        'issues': 0,
                        'reasoning': None
                    }
                
                if len(md_files) > 1:
                    progress_bar.progress((i + 1) / len(md_files))
            
            # Clear progress indicators
            if len(md_files) > 1:
                progress_bar.empty()
                status_text.empty()
            
            # Show processing results
            if len(md_files) > 1:
                st.markdown("#### 📈 Batch Processing Results")
                
                results_col1, results_col2 = st.columns(2)
                
                with results_col1:
                    successful_files = sum(1 for r in file_results.values() if r['status'] == 'success')
                    failed_files = len(md_files) - successful_files
                    
                    st.markdown("""
                    <div class="metric-card">
                        <h4 style="margin: 0; color: #28a745;">✅ Processing Summary</h4>
                        <p style="margin: 0.5rem 0 0 0;">Successful: {}/{}</p>
                        <p style="margin: 0;">Failed: {}</p>
                    </div>
                    """.format(successful_files, len(md_files), failed_files), unsafe_allow_html=True)
                
                with results_col2:
                    # Show detailed results
                    with st.expander("📄 Detailed File Results", expanded=False):
                        for filename, result in file_results.items():
                            status_emoji = "✅" if result['status'] == 'success' else "❌"
                            st.write(f"{status_emoji} **{filename}**: {result['milestones']} milestones, {result['issues']} issues")
            
            if not all_projects:
                st.markdown("""
                <div class="error-message">
                    <h3>❌ No Content Found</h3>
                    <p>No milestones or issues were found in any of the markdown files.</p>
                </div>
                """, unsafe_allow_html=True)
                if not use_ai_parsing:
                    st.info("💡 Try enabling AI parsing in the sidebar for better results with natural markdown.")
            else:
                # Use all_projects instead of project for the rest of the processing
                project = all_projects
                reasoning = "\n\n".join(all_reasoning) if all_reasoning else None
                
                # Show combined AI reasoning if available
                if all_reasoning and use_ai_parsing:
                    st.markdown("### 🧠 AI Analysis")
                    with st.expander("💭 How the AI interpreted your markdown files", expanded=True):
                        for i, reasoning_text in enumerate(all_reasoning, 1):
                            # Extract filename and reasoning from the formatted text
                            if '**' in reasoning_text and ':**' in reasoning_text:
                                parts = reasoning_text.split(':**', 1)
                                filename = parts[0].replace('**', '').strip()
                                actual_reasoning = parts[1].strip() if len(parts) > 1 else "Analysis completed successfully."
                            else:
                                filename = f"File {i}"
                                actual_reasoning = reasoning_text.strip()
                            
                            # Only show if we have substantial content
                            if actual_reasoning and len(actual_reasoning) > 10:
                                st.markdown(f"**📄 {filename}**")
                                # Use streamlit's built-in components instead of custom HTML
                                st.info(actual_reasoning)
                            else:
                                st.markdown(f"**📄 {filename}**")
                                st.success("✅ AI analysis completed successfully")
                            
                            # Add some spacing between files
                            if i < len(all_reasoning):
                                st.markdown("---")
                
                # Results overview
                st.markdown("### 📈 Step 4: Results Overview")
                
                # Display statistics in a nicer format
                total_milestones = len(project)
                total_issues = sum(len(m['issues']) for m in project.values())
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("""
                    <div class="metric-card" style="text-align: center;">
                        <h2 style="color: #007bff; margin: 0;">{}</h2>
                        <p style="margin: 0; color: #666;">🎯 Milestones</p>
                    </div>
                    """.format(total_milestones), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card" style="text-align: center;">
                        <h2 style="color: #28a745; margin: 0;">{}</h2>
                        <p style="margin: 0; color: #666;">📋 Issues</p>
                    </div>
                    """.format(total_issues), unsafe_allow_html=True)
                
                with col3:
                    ai_status = "Yes" if reasoning else "No"
                    color = "#007bff" if reasoning else "#6c757d"
                    st.markdown("""
                    <div class="metric-card" style="text-align: center;">
                        <h2 style="color: {}; margin: 0;">{}</h2>
                        <p style="margin: 0; color: #666;">🤖 AI Powered</p>
                    </div>
                    """.format(color, ai_status), unsafe_allow_html=True)
                
                with col4:
                    avg_issues = total_issues / total_milestones if total_milestones > 0 else 0
                    st.markdown("""
                    <div class="metric-card" style="text-align: center;">
                        <h2 style="color: #ffc107; margin: 0;">{:.1f}</h2>
                        <p style="margin: 0; color: #666;">📄 Avg Issues/Milestone</p>
                    </div>
                    """.format(avg_issues), unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Edit section
                st.markdown("### ✏️ Step 5: Review & Edit" if use_ai_parsing else "### ✏️ Step 5: Preview and Edit")
                
                # Allow editing of parsed content with better organization
                st.markdown("---")
                for m_title, m_data in project.items():
                    with st.expander(f"🎯 Milestone: {m_title}", expanded=True):
                        m_data['description'] = st.text_area(
                            "Description", 
                            value=m_data.get('description', ''), 
                            height=100,
                            key=f"desc_{m_title}"
                        )
                        
                        st.markdown(f"**📋 Issues in this milestone: {len(m_data['issues'])}**")
                        
                        # Show issues in a tabbed format instead of nested expanders
                        if m_data['issues']:
                            issue_tabs = st.tabs([f"Issue {idx+1}" for idx in range(len(m_data['issues']))])
                            
                            for idx, (tab, iss) in enumerate(zip(issue_tabs, m_data['issues'])):
                                with tab:
                                    st.markdown(f"**📋 {iss['title'][:50]}{'...' if len(iss['title']) > 50 else ''}**")
                                    
                                    iss['title'] = st.text_input(
                                        "Title", 
                                        value=iss['title'], 
                                        key=f"title_{m_title}_{idx}"
                                    )
                                    
                                    iss['body'] = st.text_area(
                                        "Body", 
                                        value=iss['body'], 
                                        height=150, 
                                        key=f"body_{m_title}_{idx}"
                                    )
                                    
                                    # Convert lists to comma-separated strings for UI
                                    labels_str = ",".join(iss.get('labels', []))
                                    assignees_str = ",".join(iss.get('assignees', []))
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        new_labels = st.text_input(
                                            "🏷️ Labels (comma-separated)", 
                                            value=labels_str, 
                                            key=f"labels_{m_title}_{idx}"
                                        )
                                        iss['labels'] = [l.strip() for l in new_labels.split(',') if l.strip()]
                                    
                                    with col2:
                                        new_assignees = st.text_input(
                                            "👤 Assignees (comma-separated)", 
                                            value=assignees_str, 
                                            key=f"assignees_{m_title}_{idx}"
                                        )
                                        iss['assignees'] = [a.strip() for a in new_assignees.split(',') if a.strip()]
                        else:
                            st.info("No issues found in this milestone.")
                
                # GitHub push section with better styling
                st.markdown("### 🚀 Step 6: Deploy to GitHub")
                st.markdown("---")
                
                if not config_ok:
                    st.markdown("""
                    <div class="warning-box">
                        <h4>⚠️ Configuration Required</h4>
                        <p>GitHub configuration is incomplete. Please check the settings in the sidebar before proceeding.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create deployment summary
                st.markdown("#### 📄 Deployment Summary")
                summary_col1, summary_col2 = st.columns(2)
                
                with summary_col1:
                    st.markdown("""
                    **What will be created:**
                    - {} milestone(s)
                    - {} issue(s)
                    - Labels and assignments as configured
                    """.format(total_milestones, total_issues))
                
                with summary_col2:
                    mode_text = "Dry Run Mode 🧪" if dry_run else "Live Deployment 🚀"
                    mode_color = "#ffc107" if dry_run else "#28a745"
                    st.markdown("""
                    <div class="metric-card" style="border-left: 4px solid {};">
                        <h4 style="color: {}; margin: 0;">{}</h4>
                        <p style="margin: 0.5rem 0 0 0; color: #666;">{}</p>
                    </div>
                    """.format(
                        mode_color, mode_color, mode_text,
                        "No changes will be made" if dry_run else "Changes will be applied to your repository"
                    ), unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Action buttons with better layout
                button_col1, button_col2, button_col3 = st.columns([2, 1, 1])
                
                with button_col1:
                    push_button = st.button(
                        "🚀 Deploy to GitHub" if not dry_run else "🔍 Test Deployment",
                        disabled=not config_ok and not dry_run,
                        type="primary",
                        use_container_width=True
                    )
                
                with button_col2:
                    if st.button("🔄 Reset", use_container_width=True):
                        st.rerun()
                
                with button_col3:
                    st.download_button(
                        "💾 Export JSON",
                        data=json.dumps(project, indent=2),
                        file_name="github_structure.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                if push_button:
                    total = sum(len(m['issues']) for m in project.values())
                    count = 0
                    
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        for ms_title, ms_data in project.items():
                            status_text.text(f"Creating milestone: {ms_title}")
                            
                            # Handle optional fields that might not exist
                            milestone_desc = ms_data.get('description', '')
                            milestone_state = ms_data.get('state', 'open')
                            milestone_due = ms_data.get('due_date', None)
                            
                            num = create_milestone(
                                ms_title, 
                                milestone_desc, 
                                state=milestone_state,
                                due_on=milestone_due,
                                dry_run=dry_run
                            )
                            
                            for iss in ms_data['issues']:
                                status_text.text(f"Creating issue: {iss['title'][:40]}...")
                                create_issue(
                                    iss['title'], 
                                    iss['body'], 
                                    num,
                                    labels=[l for l in iss.get('labels', []) if l],
                                    assignees=[a for a in iss.get('assignees', []) if a],
                                    dry_run=dry_run
                                )
                                count += 1
                                progress_bar.progress(count / total)
                                # Small delay to show progress in dry run mode
                                if dry_run:
                                    time.sleep(0.2)
                        
                        if dry_run:
                            st.markdown("""
                            <div class="info-message">
                                <h3>✅ Dry Run Completed Successfully</h3>
                                <p><strong>Simulation Results:</strong></p>
                                <ul>
                                    <li>{} milestones would be created</li>
                                    <li>{} issues would be created</li>
                                    <li>No actual changes were made to your repository</li>
                                </ul>
                                <p><em>Uncheck "Dry run" in the sidebar to perform the actual deployment.</em></p>
                            </div>
                            """.format(total_milestones, total_issues), unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="success-message">
                                <h3>✅ Deployment Successful!</h3>
                                <p><strong>Successfully created:</strong></p>
                                <ul>
                                    <li>{} milestones in your GitHub repository</li>
                                    <li>{} issues with proper labels and assignments</li>
                                </ul>
                                <p><em>Check your GitHub repository to see the new content!</em></p>
                            </div>
                            """.format(total_milestones, total_issues), unsafe_allow_html=True)
                            
                            # Add success actions
                            success_col1, success_col2 = st.columns(2)
                            with success_col1:
                                if st.button("🔗 Open Repository", type="secondary"):
                                    repo_url = f"https://github.com/{OWNER}/{REPO}"
                                    st.markdown(f"[Open Repository]({repo_url})")
                            with success_col2:
                                if st.button("🔄 Process Another File", type="secondary"):
                                    st.rerun()
                            
                    except (GitHubError, DeepSeekError) as e:
                        st.markdown(f"""
                        <div class="error-message">
                            <h3>❌ Error</h3>
                            <p>{str(e)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Clear the progress indicators
                    status_text.empty()
        
        except Exception as e:
            st.error(f"❌ Error processing the markdown file: {str(e)}")
            if use_ai_parsing:
                st.info("💡 Try disabling AI parsing in the sidebar to use traditional regex parsing as fallback.")

elif mode == "✍️ Manual Entry":
    st.subheader("Manual Entry Mode")
    
    # Create a new milestone
    with st.expander("➕ Create New Milestone", expanded=True):
        milestone_title = st.text_input("🎯 Milestone Title")
        milestone_desc = st.text_area("📝 Milestone Description")
        
        if st.button("Add Milestone", type="primary"):
            if not milestone_title:
                st.error("Milestone title is required")
            else:
                # Store in session state
                if 'milestones' not in st.session_state:
                    st.session_state.milestones = {}
                
                st.session_state.milestones[milestone_title] = {
                    'description': milestone_desc,
                    'issues': []
                }
                st.success(f"✅ Milestone '{milestone_title}' added")
    
    # Add issues to existing milestones
    if 'milestones' in st.session_state and st.session_state.milestones:
        with st.expander("📋 Add Issue to Milestone", expanded=True):
            milestone_options = list(st.session_state.milestones.keys())
            selected_milestone = st.selectbox("Select Milestone", milestone_options)
            
            issue_title = st.text_input("📋 Issue Title")
            issue_body = st.text_area("📝 Issue Description")
            issue_labels = st.text_input("🏷️ Labels (comma-separated)")
            issue_assignees = st.text_input("👤 Assignees (comma-separated)")
            
            if st.button("Add Issue", type="primary"):
                if not issue_title:
                    st.error("Issue title is required")
                else:
                    # Add to session state
                    st.session_state.milestones[selected_milestone]['issues'].append({
                        'title': issue_title,
                        'body': issue_body,
                        'labels': [l.strip() for l in issue_labels.split(',') if l.strip()],
                        'assignees': [a.strip() for a in issue_assignees.split(',') if a.strip()]
                    })
                    st.success(f"✅ Issue '{issue_title}' added to milestone '{selected_milestone}'")
        
        # Preview and push section
        st.subheader("👀 Preview and Push")
        
        # Display the current milestones and issues
        for m_title, m_data in st.session_state.milestones.items():
            with st.expander(f"🎯 Milestone: {m_title}", expanded=False):
                st.write(f"📝 Description: {m_data['description']}")
                
                if m_data['issues']:
                    for idx, issue in enumerate(m_data['issues']):
                        st.write(f"📋 Issue {idx+1}: {issue['title']}")
                        st.write(f"🏷️ Labels: {', '.join(issue['labels']) if issue['labels'] else 'None'}")
                        st.write(f"👤 Assignees: {', '.join(issue['assignees']) if issue['assignees'] else 'None'}")
                        st.text(issue['body'])
                        st.markdown("---")
                else:
                    st.info("No issues added to this milestone yet")
        
        # Push to GitHub button
        if not config_ok:
            st.warning("⚠️ GitHub configuration is incomplete. Please check the settings in the sidebar.")
        
        push_col1, push_col2 = st.columns([3, 1])
        with push_col1:
            manual_push_button = st.button(
                "🚀 Push Manual Entries to GitHub" if not dry_run else "🔍 Test Manual Entries (No API Calls)",
                disabled=not config_ok and not dry_run,
                type="primary"
            )
        
        with push_col2:
            if dry_run:
                st.info("🧪 Dry run mode")
        
        if manual_push_button:
            total = sum(len(m['issues']) for m in st.session_state.milestones.values())
            count = 0
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                for ms_title, ms_data in st.session_state.milestones.items():
                    status_text.text(f"Creating milestone: {ms_title}")
                    num = create_milestone(ms_title, ms_data['description'], dry_run=dry_run)
                    
                    for iss in ms_data['issues']:
                        status_text.text(f"Creating issue: {iss['title'][:40]}...")
                        create_issue(
                            iss['title'], 
                            iss['body'], 
                            num,
                            labels=iss['labels'],
                            assignees=iss['assignees'],
                            dry_run=dry_run
                        )
                        count += 1
                        progress_bar.progress(count / total)
                        # Small delay to show progress in dry run mode
                        if dry_run:
                            time.sleep(0.2)
                
                if dry_run:
                    st.markdown("""
                    <div class="info-message">
                        <h3>✅ Dry run completed successfully</h3>
                        <p>No changes were made to your GitHub repository. Uncheck "Dry run" in the sidebar to create actual issues.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="success-message">
                        <h3>✅ Success!</h3>
                        <p>All milestones and issues have been created in your GitHub repository.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except GitHubError as e:
                st.markdown(f"""
                <div class="error-message">
                    <h3>❌ Error</h3>
                    <p>{str(e)}</p>
                </div>
                """, unsafe_allow_html=True)
                
            # Clear the progress indicators
            status_text.empty()
    else:
        st.info("➕ Add a milestone first to start creating issues")

elif mode == "🗑️ Cleanup Repository":
    st.subheader("🗑️ Repository Cleanup")
    st.markdown("""
    <div class="warning-box">
    <h4>⚠️ Warning: Permanent Action</h4>
    <p>This will close issues and delete milestones in your repository. This action cannot be undone!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not config_ok:
        st.error("⚠️ GitHub configuration required for cleanup operations.")
    else:
        # Cleanup tabs
        cleanup_tab1, cleanup_tab2, cleanup_tab3 = st.tabs(["📋 Issues", "🎯 Milestones", "🔍 Search & Cleanup"])
        
        with cleanup_tab1:
            st.subheader("📋 Manage Issues")
            
            # Issue filters
            col1, col2, col3 = st.columns(3)
            with col1:
                issue_state = st.selectbox("State", ["all", "open", "closed"], index=0)
            with col2:
                issue_sort = st.selectbox("Sort by", ["created", "updated", "comments"], index=1)
            with col3:
                issue_direction = st.selectbox("Direction", ["desc", "asc"], index=0)
            
            # Fetch issues button
            if st.button("🔄 Load Issues", key="load_issues"):
                try:
                    with st.spinner("Loading issues..."):
                        issues = get_issues(state=issue_state, sort=issue_sort, direction=issue_direction)
                    
                    if issues:
                        st.success(f"✅ Found {len(issues)} issues")
                        st.session_state.loaded_issues = issues
                    else:
                        st.info("No issues found matching the criteria")
                        st.session_state.loaded_issues = []
                        
                except GitHubError as e:
                    st.error(f"❌ Error loading issues: {str(e)}")
            
            # Display loaded issues
            if 'loaded_issues' in st.session_state and st.session_state.loaded_issues:
                st.markdown(f"**📊 Loaded {len(st.session_state.loaded_issues)} issues:**")
                
                # Select all checkbox
                select_all = st.checkbox("Select all issues", key="select_all_issues")
                
                # Issue selection
                selected_issues = []
                for issue in st.session_state.loaded_issues:
                    issue_number = issue['number']
                    issue_title = issue['title']
                    issue_state_emoji = "🟢" if issue['state'] == 'open' else "🔴"
                    
                    # Truncate long titles
                    display_title = issue_title[:60] + "..." if len(issue_title) > 60 else issue_title
                    
                    is_selected = st.checkbox(
                        f"{issue_state_emoji} #{issue_number}: {display_title}",
                        value=select_all,
                        key=f"issue_{issue_number}"
                    )
                    
                    if is_selected:
                        selected_issues.append(issue_number)
                
                # Bulk delete section
                if selected_issues:
                    st.markdown(f"**🎯 Selected {len(selected_issues)} issues for deletion**")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        delete_issues_button = st.button(
                            f"🗑️ Close {len(selected_issues)} Selected Issues" if not dry_run else f"🔍 Test Close {len(selected_issues)} Issues",
                            type="primary" if not dry_run else "secondary",
                            key="delete_selected_issues"
                        )
                    
                    with col2:
                        if dry_run:
                            st.info("🧪 Dry run")
                    
                    if delete_issues_button:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        def progress_callback(current, total, issue_num):
                            progress_bar.progress(current / total)
                            status_text.text(f"Processing issue #{issue_num} ({current}/{total})")
                        
                        try:
                            results = bulk_delete_issues(
                                selected_issues, 
                                dry_run=dry_run, 
                                progress_callback=progress_callback
                            )
                            
                            # Clear progress indicators
                            progress_bar.empty()
                            status_text.empty()
                            
                            if dry_run:
                                st.markdown(f"""
                                <div class="info-message">
                                    <h3>✅ Dry run completed</h3>
                                    <p>Would close {results['total']} issues. No actual changes made.</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="success-message">
                                    <h3>✅ Cleanup completed</h3>
                                    <p>Successfully closed {results['successful']} issues. Failed: {results['failed']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if results['failed'] > 0:
                                    st.error(f"Failed to close {results['failed']} issues: {results['failed_issues']}")
                            
                            # Clear loaded issues to force refresh
                            if not dry_run:
                                del st.session_state.loaded_issues
                                
                        except GitHubError as e:
                            st.error(f"❌ Error during bulk deletion: {str(e)}")
                            progress_bar.empty()
                            status_text.empty()
        
        with cleanup_tab2:
            st.subheader("🎯 Manage Milestones")
            
            # Milestone filters
            col1, col2 = st.columns(2)
            with col1:
                milestone_state = st.selectbox("State", ["all", "open", "closed"], index=0, key="milestone_state")
            with col2:
                milestone_sort = st.selectbox("Sort by", ["due_on", "completeness"], index=0, key="milestone_sort")
            
            # Fetch milestones button
            if st.button("🔄 Load Milestones", key="load_milestones"):
                try:
                    with st.spinner("Loading milestones..."):
                        milestones = get_milestones(state=milestone_state, sort=milestone_sort)
                    
                    if milestones:
                        st.success(f"✅ Found {len(milestones)} milestones")
                        st.session_state.loaded_milestones = milestones
                    else:
                        st.info("No milestones found")
                        st.session_state.loaded_milestones = []
                        
                except GitHubError as e:
                    st.error(f"❌ Error loading milestones: {str(e)}")
            
            # Display loaded milestones
            if 'loaded_milestones' in st.session_state and st.session_state.loaded_milestones:
                st.markdown(f"**📊 Loaded {len(st.session_state.loaded_milestones)} milestones:**")
                
                selected_milestones = []
                for milestone in st.session_state.loaded_milestones:
                    milestone_number = milestone['number']
                    milestone_title = milestone['title']
                    milestone_state_emoji = "🟢" if milestone['state'] == 'open' else "🔴"
                    open_issues = milestone.get('open_issues', 0)
                    closed_issues = milestone.get('closed_issues', 0)
                    
                    # Milestone info
                    milestone_info = f"{milestone_state_emoji} {milestone_title} ({open_issues} open, {closed_issues} closed)"
                    
                    is_selected = st.checkbox(
                        milestone_info,
                        key=f"milestone_{milestone_number}"
                    )
                    
                    if is_selected:
                        selected_milestones.append(milestone_number)
                
                # Delete selected milestones
                if selected_milestones:
                    st.warning("⚠️ Deleting milestones will also remove them from associated issues!")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        delete_milestones_button = st.button(
                            f"🗑️ Delete {len(selected_milestones)} Selected Milestones" if not dry_run else f"🔍 Test Delete {len(selected_milestones)} Milestones",
                            type="primary" if not dry_run else "secondary",
                            key="delete_selected_milestones"
                        )
                    
                    with col2:
                        if dry_run:
                            st.info("🧪 Dry run")
                    
                    if delete_milestones_button:
                        successful = 0
                        failed = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, milestone_num in enumerate(selected_milestones):
                            status_text.text(f"Deleting milestone #{milestone_num}...")
                            
                            try:
                                if delete_milestone(milestone_num, dry_run=dry_run):
                                    successful += 1
                                else:
                                    failed += 1
                            except Exception as e:
                                failed += 1
                                st.error(f"Failed to delete milestone #{milestone_num}: {str(e)}")
                            
                            progress_bar.progress((i + 1) / len(selected_milestones))
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                        
                        if dry_run:
                            st.markdown(f"""
                            <div class="info-message">
                                <h3>✅ Dry run completed</h3>
                                <p>Would delete {len(selected_milestones)} milestones. No actual changes made.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="success-message">
                                <h3>✅ Cleanup completed</h3>
                                <p>Successfully deleted {successful} milestones. Failed: {failed}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Clear loaded milestones to force refresh
                            if not dry_run:
                                del st.session_state.loaded_milestones
        
        with cleanup_tab3:
            st.subheader("🔍 Search & Cleanup")
            st.markdown("Search for specific issues using GitHub's powerful search syntax.")
            
            # Search input
            search_query = st.text_input(
                "🔍 Search Query", 
                placeholder="e.g., 'label:bug', 'author:username', 'created:<2024-01-01'",
                help="Use GitHub search syntax. Examples: 'label:bug', 'is:open author:username', 'created:<2024-01-01'"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                search_state = st.selectbox("State", ["all", "open", "closed"], key="search_state")
            with col2:
                search_sort = st.selectbox("Sort by", ["updated", "created", "comments"], key="search_sort")
            
            if st.button("🔍 Search Issues", key="search_issues") and search_query:
                try:
                    with st.spinner(f"Searching for: {search_query}..."):
                        search_results = search_issues(search_query, state=search_state, sort=search_sort)
                    
                    if search_results:
                        st.success(f"✅ Found {len(search_results)} matching issues")
                        st.session_state.search_results = search_results
                    else:
                        st.info("No issues found matching your search")
                        st.session_state.search_results = []
                        
                except GitHubError as e:
                    st.error(f"❌ Search error: {str(e)}")
            
            # Display search results
            if 'search_results' in st.session_state and st.session_state.search_results:
                st.markdown(f"**🔍 Search Results ({len(st.session_state.search_results)} issues):**")
                
                selected_search_issues = []
                for issue in st.session_state.search_results:
                    issue_number = issue['number']
                    issue_title = issue['title']
                    issue_state_emoji = "🟢" if issue['state'] == 'open' else "🔴"
                    created_date = issue['created_at'][:10]  # Just the date part
                    
                    display_title = issue_title[:50] + "..." if len(issue_title) > 50 else issue_title
                    
                    is_selected = st.checkbox(
                        f"{issue_state_emoji} #{issue_number}: {display_title} (created: {created_date})",
                        key=f"search_issue_{issue_number}"
                    )
                    
                    if is_selected:
                        selected_search_issues.append(issue_number)
                
                # Bulk action on search results
                if selected_search_issues:
                    st.markdown(f"**🎯 Selected {len(selected_search_issues)} issues from search results**")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        delete_search_button = st.button(
                            f"🗑️ Close {len(selected_search_issues)} Selected Issues" if not dry_run else f"🔍 Test Close {len(selected_search_issues)} Issues",
                            type="primary" if not dry_run else "secondary",
                            key="delete_search_issues"
                        )
                    
                    with col2:
                        if dry_run:
                            st.info("🧪 Dry run")
                    
                    if delete_search_button:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        def search_progress_callback(current, total, issue_num):
                            progress_bar.progress(current / total)
                            status_text.text(f"Processing issue #{issue_num} ({current}/{total})")
                        
                        try:
                            results = bulk_delete_issues(
                                selected_search_issues, 
                                dry_run=dry_run, 
                                progress_callback=search_progress_callback
                            )
                            
                            # Clear progress indicators
                            progress_bar.empty()
                            status_text.empty()
                            
                            if dry_run:
                                st.markdown(f"""
                                <div class="info-message">
                                    <h3>✅ Dry run completed</h3>
                                    <p>Would close {results['total']} issues. No actual changes made.</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="success-message">
                                    <h3>✅ Cleanup completed</h3>
                                    <p>Successfully closed {results['successful']} issues. Failed: {results['failed']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Clear search results to force refresh
                                if not dry_run:
                                    del st.session_state.search_results
                            
                        except GitHubError as e:
                            st.error(f"❌ Error during cleanup: {str(e)}")
                            progress_bar.empty()
                            status_text.empty()
            
            # Search examples
            with st.expander("💡 Search Examples"):
                st.markdown("""
                **Common search patterns:**
                
                - `label:bug` - Find all bug issues
                - `label:enhancement is:open` - Open enhancement requests
                - `author:username` - Issues created by specific user
                - `assignee:username` - Issues assigned to specific user
                - `created:<2024-01-01` - Issues created before specific date
                - `updated:<2024-06-01` - Issues not updated since date
                - `is:open no:milestone` - Open issues without milestones
                - `is:closed` - All closed issues
                - `in:title "old feature"` - Issues with specific text in title
                - `comments:>10` - Issues with many comments
                
                **Advanced examples:**
                - `label:bug is:open created:<2024-01-01` - Old open bugs
                - `is:closed updated:<2023-01-01` - Very old closed issues
                - `no:assignee is:open` - Unassigned open issues
                """)

# Footer with help information
st.markdown("---")
st.markdown("## 📚 Help & Documentation")
with st.expander("ℹ️ View Help & Setup Instructions", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🤖 AI Parsing (Recommended)
        
        With AI parsing enabled, you can upload **any** markdown format:
        
        ```markdown
        # Project Setup
        
        We need to set up the basic project structure and configure the environment.
        
        ## Database Setup
        - Create database schema
        - Set up migrations
        - Configure connection pooling
        
        ## Authentication System
        - Implement login/logout
        - Add password reset
        - Create user roles
        ```
        
        The AI will intelligently convert this into milestones and issues!
        """)
    
    with col2:
        st.markdown("""
        ### 📝 Traditional Format (Fallback)
        
        If AI parsing is disabled, use this specific format:
        
        ```markdown
        # Milestone: Your Milestone Title
        description: Optional milestone description
        
        ## Issue: Your Issue Title
        
        Issue description goes here.
        You can use multiple paragraphs.
        
        labels: bug, enhancement
        assignees: username1, username2
        
        ## Issue: Another Issue
        
        Another issue description.
        
        labels: documentation
        assignees: username3
        ```
        """)
    
    st.markdown("""
    ### 🔧 Setup Instructions
    
    **GitHub Token:**
    You need a GitHub personal access token with `repo` scope to create issues and milestones.
    Create one at [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens).
    
    **DeepSeek API Key:**
    Get your API key from [DeepSeek Platform](https://platform.deepseek.com) to enable AI parsing.
    
    **Environment Variables:**
    Create a `.env` file in the same directory as this application with:
    
    ```
    GITHUB_TOKEN=your_github_token
    REPO_OWNER=your_username_or_org
    REPO_NAME=your_repo
    DEEPSEEK_API_KEY=your_deepseek_api_key
    ```
    
    ### 🚀 Features
    
    - **🤖 AI-Powered**: Intelligent parsing of any markdown format
    - **🧠 Reasoning Display**: See how the AI interpreted your content
    - **🔄 Fallback Mode**: Traditional regex parsing when AI is unavailable
    - **🧪 Dry Run**: Test without making actual API calls
    - **✏️ Live Editing**: Modify parsed results before pushing to GitHub
    - **📊 Real-time Stats**: Track milestones and issues counts
    - **🗑️ Repository Cleanup**: Close old issues and delete milestones
    - **🔒 Secure**: Local processing with secure API integration
    
    ### 🗑️ Repository Cleanup
    
    **⚠️ Important: GitHub API Limitations**
    
    GitHub's API **does not allow true deletion of issues**. This is intentional to:
    - Preserve project history and audit trails
    - Maintain references in commits and pull requests
    - Ensure data integrity and compliance requirements
    
    **What our cleanup tool does:**
    - **Issues**: Closes them permanently and marks as "not planned"
    - **Milestones**: True deletion (removes from all associated issues)
    - **Search**: Advanced GitHub search syntax for targeted cleanup
    
    **Search Examples:**
    - `label:bug is:open created:<2024-01-01` - Old open bugs
    - `is:open no:milestone` - Issues without milestones
    - `no:assignee is:open` - Unassigned open issues
    - `updated:<2023-01-01` - Very old issues
    
    **Why Issues Can't Be Deleted:**
    GitHub prevents issue deletion because issues contain valuable project history,
    discussions, and references that other parts of your repository depend on.
    Closed issues can always be reopened if needed later.
    """)

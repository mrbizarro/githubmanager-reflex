"""
Modern CSS styling with functional sidebar
"""

import streamlit as st

def load_custom_css():
    """Load modern CSS styling with beautiful sidebar"""
    
    # Check theme preference (default to dark)
    dark_mode = st.session_state.get('dark_mode', True)
    
    # Set CSS variables based on theme
    if dark_mode:
        root_vars = """--background: 222.2 84% 4.9%;
        --foreground: 210 40% 98%;
        --card: 222.2 84% 4.9%;
        --card-foreground: 210 40% 98%;
        --popover: 222.2 84% 4.9%;
        --popover-foreground: 210 40% 98%;
        --primary: 252 59% 48%;
        --primary-foreground: 210 40% 98%;
        --secondary: 217.2 32.6% 17.5%;
        --secondary-foreground: 210 40% 98%;
        --muted: 217.2 32.6% 17.5%;
        --muted-foreground: 215 20.2% 65.1%;
        --accent: 217.2 32.6% 17.5%;
        --accent-foreground: 210 40% 98%;
        --destructive: 0 62.8% 30.6%;
        --destructive-foreground: 210 40% 98%;
        --border: 217.2 32.6% 17.5%;
        --input: 217.2 32.6% 17.5%;
        --ring: 252 59% 48%;"""
        
        app_bg_color = "hsl(222.2 84% 4.9%)"
        app_text_color = "hsl(210 40% 98%)"
        form_bg_color = "hsl(217.2 32.6% 17.5%)"
    else:
        root_vars = """--background: 0 0% 100%;
        --foreground: 222.2 84% 4.9%;
        --card: 0 0% 100%;
        --card-foreground: 222.2 84% 4.9%;
        --popover: 0 0% 100%;
        --popover-foreground: 222.2 84% 4.9%;
        --primary: 252 59% 48%;
        --primary-foreground: 210 40% 98%;
        --secondary: 210 40% 96.1%;
        --secondary-foreground: 222.2 47.4% 11.2%;
        --muted: 210 40% 96.1%;
        --muted-foreground: 215.4 16.3% 46.9%;
        --accent: 210 40% 96.1%;
        --accent-foreground: 222.2 47.4% 11.2%;
        --destructive: 0 84.2% 60.2%;
        --destructive-foreground: 210 40% 98%;
        --border: 214.3 31.8% 91.4%;
        --input: 214.3 31.8% 91.4%;
        --ring: 252 59% 48%;"""
        
        app_bg_color = "hsl(0 0% 100%)"
        app_text_color = "hsl(222.2 84% 4.9%)"
        form_bg_color = "hsl(210 40% 96.1%)"
    
    css_content = f"""
    <style>
    /* Import Inter font for modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* CSS Custom Properties (shadcn/ui color system) */
    :root {{
        {root_vars}
        --radius: 0.75rem;
    }}
    
    /* Hide Streamlit branding but keep sidebar */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    
    /* App-wide theme */
    .stApp {{
        background-color: {app_bg_color} !important;
        color: {app_text_color} !important;
    }}
    
    /* Main container with normal sidebar layout */
    .main {{
        margin-left: 0 !important;
        width: 100% !important;
        padding: 0 !important;
    }}
    
    .main .block-container {{
        padding: 1.5rem 3rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
        font-family: 'Inter', sans-serif !important;
        background-color: {app_bg_color} !important;
        color: {app_text_color} !important;
        width: 100% !important;
    }}
    
    /* Beautiful sidebar styling */
    .css-1d391kg {{
        background: linear-gradient(180deg, hsl(var(--card)) 0%, hsl(var(--muted)) 100%) !important;
        padding: 1.5rem 1rem !important;
        border-right: 1px solid hsl(var(--border)) !important;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1) !important;
        min-height: 100vh !important;
        width: 280px !important;
    }}
    
    /* Sidebar content styling */
    .css-1d391kg * {{
        color: hsl(var(--foreground)) !important;
    }}
    
    .css-1d391kg .stMarkdown {{
        color: hsl(var(--foreground)) !important;
    }}
    
    /* Sidebar section headers */
    .sidebar-section {{
        background: hsl(var(--accent));
        padding: 0.75rem;
        border-radius: var(--radius);
        margin: 1rem 0;
        border: 1px solid hsl(var(--border));
    }}
    
    .sidebar-section h3 {{
        margin: 0 !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: hsl(var(--accent-foreground)) !important;
    }}
    
    /* Sidebar buttons */
    .css-1d391kg .stButton > button {{
        width: 100% !important;
        margin: 0.25rem 0 !important;
        background: hsl(var(--secondary)) !important;
        color: hsl(var(--secondary-foreground)) !important;
        border: 1px solid hsl(var(--border)) !important;
        font-size: 0.875rem !important;
        padding: 0.5rem 1rem !important;
        border-radius: var(--radius) !important;
    }}
    
    .css-1d391kg .stButton > button:hover {{
        background: hsl(var(--primary)) !important;
        color: hsl(var(--primary-foreground)) !important;
        border-color: hsl(var(--primary)) !important;
    }}
    
    /* Modern header */
    .modern-header {{
        background: linear-gradient(135deg, hsl(var(--primary)) 0%, #8b5cf6 100%);
        padding: 2rem;
        border-radius: var(--radius);
        margin: -1.5rem -3rem 2rem -3rem;
        color: hsl(var(--primary-foreground));
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }}
    
    .modern-header h1 {{
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.025em;
        color: hsl(var(--primary-foreground));
    }}
    
    .modern-header p {{
        font-size: 1.125rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
        color: hsl(var(--primary-foreground));
    }}
    
    /* Status indicators */
    .status-indicator {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 1.25rem;
        border-radius: var(--radius);
        border: 1px solid hsl(var(--border));
        background-color: hsl(var(--card));
        transition: all 0.2s ease;
        margin-bottom: 1rem;
    }}
    
    .status-connected {{
        border-color: hsl(142 71% 45%);
        background-color: hsl(142 71% 45% / 0.1);
    }}
    
    .status-disconnected {{
        border-color: hsl(0 84% 60%);
        background-color: hsl(0 84% 60% / 0.1);
    }}
    
    /* Modern cards */
    .modern-card {{
        background-color: hsl(var(--card));
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        transition: all 0.2s ease;
        margin: 1rem 0;
    }}
    
    .card-title {{
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        color: hsl(var(--card-foreground));
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    .card-description {{
        color: hsl(var(--muted-foreground));
        font-size: 0.875rem;
        margin: 0;
        line-height: 1.5;
    }}
    
    /* Modern tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.25rem;
        background-color: hsl(var(--muted));
        padding: 0.25rem;
        border-radius: var(--radius);
        border: none;
        margin-bottom: 2rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: calc(var(--radius) - 0.125rem);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        border: none;
        transition: all 0.2s ease;
        color: hsl(var(--muted-foreground));
        font-family: 'Inter', sans-serif;
        min-width: 180px;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: hsl(var(--accent));
        color: hsl(var(--accent-foreground));
    }}
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background-color: hsl(var(--background));
        color: hsl(var(--foreground));
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    }}
    
    /* Modern buttons */
    .stButton > button {{
        background-color: hsl(var(--primary));
        color: hsl(var(--primary-foreground)) !important;
        border: none;
        border-radius: var(--radius);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        height: auto;
    }}
    
    .stButton > button:hover {{
        background-color: hsl(var(--primary) / 0.9);
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }}
    
    /* Form elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {{
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius);
        background-color: {form_bg_color} !important;
        color: {app_text_color} !important;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
        padding: 0.75rem;
        font-size: 0.875rem;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: hsl(var(--ring));
        box-shadow: 0 0 0 2px hsl(var(--ring) / 0.2);
        outline: none;
    }}
    
    /* Form labels */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label {{
        color: {app_text_color} !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.5rem !important;
        font-family: 'Inter', sans-serif !important;
    }}
    
    /* Alerts */
    .modern-alert {{
        padding: 1rem;
        border-radius: var(--radius);
        border: 1px solid;
        margin: 1rem 0;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
    }}
    
    .alert-success {{
        border-color: hsl(142 71% 45%);
        background-color: hsl(142 71% 45% / 0.1);
        color: hsl(142 71% 45%);
    }}
    
    .alert-warning {{
        border-color: hsl(38 92% 50%);
        background-color: hsl(38 92% 50% / 0.1);
        color: hsl(38 92% 50%);
    }}
    
    .alert-error {{
        border-color: hsl(var(--destructive));
        background-color: hsl(var(--destructive) / 0.1);
        color: hsl(var(--destructive));
    }}
    
    .alert-info {{
        border-color: hsl(var(--primary));
        background-color: hsl(var(--primary) / 0.1);
        color: hsl(var(--primary));
    }}
    
    .alert-title {{
        font-weight: 600;
        margin: 0 0 0.25rem 0;
        font-size: 0.875rem;
    }}
    
    .alert-description {{
        margin: 0;
        font-size: 0.875rem;
        line-height: 1.5;
        opacity: 0.8;
    }}
    
    /* Badges */
    .modern-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.5rem;
        border-radius: calc(var(--radius) - 0.125rem);
        font-size: 0.75rem;
        font-weight: 500;
        background-color: hsl(var(--secondary));
        color: hsl(var(--secondary-foreground));
        border: 1px solid hsl(var(--border));
    }}
    
    .badge-primary {{
        background-color: hsl(var(--primary));
        color: hsl(var(--primary-foreground));
        border-color: hsl(var(--primary));
    }}
    
    .badge-success {{
        background-color: hsl(142 71% 45%);
        color: white;
        border-color: hsl(142 71% 45%);
    }}
    
    /* Responsive design */
    @media (max-width: 1200px) {{
        .main .block-container {{
            padding: 1.5rem 2rem !important;
        }}
        
        .modern-header {{
            margin: -1.5rem -2rem 2rem -2rem;
        }}
    }}
    
    @media (max-width: 768px) {{
        .main .block-container {{
            padding: 1rem !important;
        }}
        
        .modern-header {{
            margin: -1rem -1rem 2rem -1rem;
            padding: 1.5rem;
        }}
        
        .modern-header h1 {{
            font-size: 2rem;
        }}
        
        .css-1d391kg {{
            width: 250px !important;
        }}
    }}
    </style>
    """
    
    # Apply the CSS
    st.markdown(css_content, unsafe_allow_html=True)

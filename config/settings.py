"""
Configuration and settings management - SIMPLE VERSION
"""

import streamlit as st
import os
from pathlib import Path

# Load environment variables from .env file
def load_environment():
    """Load environment variables with better error handling"""
    try:
        from dotenv import load_dotenv
        if load_dotenv():
            print("✅ Loaded .env using python-dotenv")
        else:
            print("⚠️ python-dotenv found but .env not loaded")
    except ImportError:
        print("📝 python-dotenv not installed, using manual loading")
        # Manual loading fallback
        env_path = Path('.env')
        if env_path.exists():
            print(f"📁 Found .env file at {env_path.absolute()}")
            with open(env_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if key and value:  # Don't set empty values
                                os.environ[key] = value
                                print(f"✅ Loaded {key}")
                        except ValueError:
                            print(f"⚠️ Skipping malformed line {line_num}: {line}")
            print("✅ Manual .env loading complete")
        else:
            print(f"❌ .env file not found at {env_path.absolute()}")

# Load environment immediately
load_environment()

def debug_config():
    """Debug function to show what config is loaded"""
    import os
    
    print("=== CONFIG DEBUG ===")
    print(f"GITHUB_TOKEN: {'*' * 20 if os.getenv('GITHUB_TOKEN') else 'NOT SET'}")
    print(f"REPO_OWNER: {os.getenv('REPO_OWNER', 'NOT SET')}")
    print(f"REPO_NAME: {os.getenv('REPO_NAME', 'NOT SET')}")
    print(f"DEEPSEEK_API_KEY: {'*' * 20 if os.getenv('DEEPSEEK_API_KEY') else 'NOT SET'}")
    print(f"Working directory: {os.getcwd()}")
    print(f".env exists: {Path('.env').exists()}")
    print("===================")

def initialize_app_config():
    """Initialize application configuration"""
    
    if 'app_config' not in st.session_state:
        st.session_state.app_config = {
            'app_name': 'GitHub Issues Manager v6',
            'version': '6.0.0',
            'theme': 'auto',
        }

def check_basic_config():
    """Check if basic configuration exists (no API calls)"""
    github_token = os.getenv('GITHUB_TOKEN', '').strip()
    repo_owner = os.getenv('REPO_OWNER', '').strip()
    repo_name = os.getenv('REPO_NAME', '').strip()
    
    # Check if values are real (not template values)
    github_configured = bool(
        github_token and 
        repo_owner and 
        repo_name and 
        not github_token.startswith('your_') and 
        not github_token.startswith('ghp_your') and
        not repo_owner.startswith('your_') and
        not repo_name.startswith('your_') and
        github_token != 'your_github_token_here' and
        repo_owner != 'your_username_or_org' and
        repo_name != 'your_repository_name'
    )
    
    deepseek_key = os.getenv('DEEPSEEK_API_KEY', '').strip()
    ai_configured = bool(
        deepseek_key and 
        not deepseek_key.startswith('your_') and
        deepseek_key != 'your_deepseek_api_key'
    )
    
    return {
        'github_configured': github_configured,
        'ai_configured': ai_configured,
        'github_token': github_token if github_configured else '',
        'repo_owner': repo_owner if github_configured else '',
        'repo_name': repo_name if github_configured else '',
        'deepseek_key': deepseek_key if ai_configured else ''
    }

def test_github_connection():
    """Test GitHub connection when requested by user"""
    try:
        config = check_basic_config()
        if not config['github_configured']:
            return False, "GitHub not configured"
        
        import requests
        headers = {
            "Authorization": f"token {config['github_token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(
            f"https://api.github.com/repos/{config['repo_owner']}/{config['repo_name']}", 
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "Connected successfully"
        elif response.status_code == 404:
            return False, "Repository not found"
        elif response.status_code == 401:
            return False, "Invalid token"
        else:
            return False, f"API error: {response.status_code}"
            
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def test_ai_connection():
    """Test AI connection when requested by user"""
    try:
        config = check_basic_config()
        if not config['ai_configured']:
            return False, "AI not configured"
        
        import requests
        headers = {
            "Authorization": f"Bearer {config['deepseek_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 1
        }
        
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "Connected successfully"
        elif response.status_code == 401:
            return False, "Invalid API key"
        else:
            return True, "API reachable"  # Even errors mean API is working
            
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# Simple configuration class
def get_config(key, default=None):
    """Get configuration value from session state or check connections"""
    if key == 'github_connected':
        config = check_basic_config()
        return config['github_configured']
    elif key == 'ai_connected':
        config = check_basic_config()
        return config['ai_configured']
    else:
        return st.session_state.get('app_config', {}).get(key, default)

def set_config(key, value):
    """Set configuration value"""
    if 'app_config' not in st.session_state:
        initialize_app_config()
    st.session_state.app_config[key] = value

class Config:
    """Simple environment configuration"""
    
    @staticmethod
    def get_github_token():
        return os.getenv('GITHUB_TOKEN', '').strip()
    
    @staticmethod
    def get_repo_owner():
        return os.getenv('REPO_OWNER', '').strip()
    
    @staticmethod
    def get_repo_name():
        return os.getenv('REPO_NAME', '').strip()
    
    @staticmethod
    def get_deepseek_key():
        return os.getenv('DEEPSEEK_API_KEY', '').strip()
    
    @staticmethod
    def is_configured():
        """Check if minimum config is present"""
        config = check_basic_config()
        return config['github_configured']
    
    @staticmethod
    def needs_setup():
        """Check if user needs to set up configuration"""
        config = check_basic_config()
        return not config['github_configured']

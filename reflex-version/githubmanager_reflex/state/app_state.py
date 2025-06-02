"""
Main application state management
"""

import reflex as rx
from typing import Dict, Any, Optional
import os
from pathlib import Path

class AppState(rx.State):
    """Main application state"""
    
    # App configuration
    app_name: str = "GitHub Issues Manager"
    version: str = "6.0.0"
    
    # Theme and UI state
    dark_mode: bool = True
    show_settings: bool = False
    show_help: bool = False
    
    # Navigation state
    current_page: str = "home"
    
    # Configuration state
    github_token: str = ""
    repo_owner: str = ""
    repo_name: str = ""
    deepseek_api_key: str = ""
    
    # Connection status
    github_connected: bool = False
    ai_connected: bool = False
    
    # Notification state
    notification_message: str = ""
    notification_type: str = "info"  # info, success, warning, error
    show_notification: bool = False
    
    def __init__(self):
        """Initialize state and load configuration"""
        super().__init__()
        self.load_environment()
    
    def load_environment(self):
        """Load configuration from environment variables"""
        try:
            # Load from .env file if it exists
            env_path = Path('.env')
            if env_path.exists():
                from dotenv import load_dotenv
                load_dotenv()
            
            # Load configuration
            self.github_token = os.getenv('GITHUB_TOKEN', '').strip()
            self.repo_owner = os.getenv('REPO_OWNER', '').strip()
            self.repo_name = os.getenv('REPO_NAME', '').strip()
            self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', '').strip()
            
            # Check connection status
            self.check_connections()
            
        except Exception as e:
            print(f"Error loading environment: {e}")
    
    def check_connections(self):
        """Check GitHub and AI connection status (non-blocking)"""
        # Simple validation without API calls
        self.github_connected = bool(
            self.github_token and 
            self.repo_owner and 
            self.repo_name and
            not self.github_token.startswith('your_') and
            self.github_token != 'your_github_token_here'
        )
        
        self.ai_connected = bool(
            self.deepseek_api_key and
            not self.deepseek_api_key.startswith('your_') and
            self.deepseek_api_key != 'your_deepseek_api_key'
        )
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.dark_mode = not self.dark_mode
    
    def toggle_settings(self):
        """Toggle settings panel"""
        self.show_settings = not self.show_settings
    
    def toggle_help(self):
        """Toggle help panel"""
        self.show_help = not self.show_help
    
    def set_page(self, page: str):
        """Set current page"""
        self.current_page = page
    
    def update_github_config(self, token: str, owner: str, name: str):
        """Update GitHub configuration"""
        self.github_token = token.strip()
        self.repo_owner = owner.strip()
        self.repo_name = name.strip()
        self.check_connections()
    
    def update_ai_config(self, api_key: str):
        """Update AI configuration"""
        self.deepseek_api_key = api_key.strip()
        self.check_connections()
    
    def save_settings(self):
        """Save current settings to .env file"""
        try:
            env_content = f"""# GitHub Issues Manager Configuration

# GitHub Settings
GITHUB_TOKEN={self.github_token}
REPO_OWNER={self.repo_owner}
REPO_NAME={self.repo_name}

# DeepSeek AI Settings
DEEPSEEK_API_KEY={self.deepseek_api_key}

# Application Settings
ENVIRONMENT=production
THEME={'dark' if self.dark_mode else 'light'}
"""
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            self.show_notification_message("Settings saved successfully!", "success")
            self.show_settings = False
            
        except Exception as e:
            self.show_notification_message(f"Error saving settings: {str(e)}", "error")
    
    async def test_github_connection(self):
        """Test GitHub API connection"""
        if not self.github_connected:
            self.show_notification_message("GitHub not configured", "warning")
            return
        
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}",
                    headers=headers,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        self.show_notification_message("GitHub connection successful!", "success")
                    elif response.status == 404:
                        self.show_notification_message("Repository not found", "error")
                    elif response.status == 401:
                        self.show_notification_message("Invalid GitHub token", "error")
                    else:
                        self.show_notification_message(f"GitHub API error: {response.status}", "error")
        
        except Exception as e:
            self.show_notification_message(f"GitHub connection failed: {str(e)}", "error")
    
    async def test_ai_connection(self):
        """Test AI API connection"""
        if not self.ai_connected:
            self.show_notification_message("AI not configured", "warning")
            return
        
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.deepseek.com/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        self.show_notification_message("AI connection successful!", "success")
                    elif response.status == 401:
                        self.show_notification_message("Invalid AI API key", "error")
                    else:
                        self.show_notification_message("AI API reachable", "success")
        
        except Exception as e:
            self.show_notification_message(f"AI connection failed: {str(e)}", "error")
    
    def show_notification_message(self, message: str, msg_type: str = "info"):
        """Show notification message"""
        self.notification_message = message
        self.notification_type = msg_type
        self.show_notification = True
    
    def hide_notification(self):
        """Hide notification"""
        self.show_notification = False
        self.notification_message = ""

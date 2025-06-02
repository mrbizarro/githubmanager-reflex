"""
🚀 Quick start script for GitHub Issues Manager v6

This script helps you launch the new restructured application.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3.8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_streamlit():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} installed")
        return True
    except ImportError:
        print("❌ Streamlit not installed")
        return False

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing requirements...")
    
    # Basic requirements for the new app
    requirements = [
        "streamlit",
        "requests",
        "python-dotenv"
    ]
    
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def check_files():
    """Check if required files exist"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = [
        "app_new.py",
        "assets/styles.py",
        "components/header.py",
        "pages/upload_convert.py",
        "utils/github_api.py",
        "config/settings.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def create_env_template():
    """Create .env template if it doesn't exist"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, ".env")
    
    # Only create if .env doesn't exist AND doesn't contain any real tokens
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                # Check if it contains real tokens (not placeholder text)
                if "your_github_token_here" not in content and "GITHUB_TOKEN=" in content:
                    print("✅ .env file already exists with configuration")
                    return True
        except Exception:
            pass
    
    if not os.path.exists(env_path):
        env_template = """# GitHub Issues Manager v6 Configuration

# GitHub Settings (Required)
GITHUB_TOKEN=your_github_token_here
REPO_OWNER=your_username_or_org
REPO_NAME=your_repository_name

# DeepSeek AI Settings (Optional - for AI parsing)
DEEPSEEK_API_KEY=your_deepseek_api_key

# Application Settings (Optional)
ENVIRONMENT=production
"""
        
        with open(env_path, 'w') as f:
            f.write(env_template)
        
        print(f"✅ Created .env template at {env_path}")
        return True
    
    print("✅ .env file already exists")
    return True

def launch_app():
    """Launch the new application"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "app_new.py")
    
    if os.path.exists(app_path):
        print(f"\n🚀 Launching GitHub Issues Manager v6...")
        print(f"📁 App location: {app_path}")
        
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user")
        except Exception as e:
            print(f"❌ Failed to launch: {str(e)}")
            print(f"\n🔧 Manual launch command:")
            print(f"streamlit run {app_path}")
    else:
        print("❌ app_new.py not found!")

def main():
    """Main startup function"""
    print("🚀 GitHub Issues Manager v6 - Quick Start")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if Streamlit is installed
    if not check_streamlit():
        print("\n📦 Installing Streamlit...")
        if not install_requirements():
            print("❌ Failed to install requirements")
            sys.exit(1)
    
    # Check required files
    print("\n📁 Checking project files...")
    if not check_files():
        print("❌ Some required files are missing")
        print("Please ensure all project files are present")
        sys.exit(1)
    
    # Create .env template
    print("\n⚙️ Setting up configuration...")
    create_env_template()
    
    print("\n✅ All checks passed!")
    print("\n📝 Before launching:")
    print("1. Edit .env file with your GitHub token and repository details")
    print("2. Optionally add DeepSeek API key for AI parsing")
    
    print("\n🚀 Ready to launch!")
    
    # Ask user if they want to launch now
    try:
        response = input("\nLaunch application now? (y/n): ").lower().strip()
        if response in ['y', 'yes', '']:
            launch_app()
        else:
            print("\n🔧 To launch later, run:")
            print("python quick_start.py")
            print("or")
            print("streamlit run app_new.py")
    except KeyboardInterrupt:
        print("\n👋 Setup complete. Run 'streamlit run app_new.py' when ready.")

if __name__ == "__main__":
    main()

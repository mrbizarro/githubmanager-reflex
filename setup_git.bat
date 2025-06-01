@echo off
REM =============================================================================
REM GitHub Manager - Git Repository Setup Script (Windows)
REM =============================================================================
REM This script safely initializes Git for the GitHub Manager project
REM with proper security measures in place.

echo 🚀 GitHub Manager - Git Setup
echo =============================
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: Please run this script from the githubmanager directory
    echo    Expected files: app.py, .gitignore
    pause
    exit /b 1
)

if not exist ".gitignore" (
    echo ❌ Error: .gitignore file not found
    echo    This file is required for security
    pause
    exit /b 1
)

REM Check if .env file exists and warn user
if exist ".env" (
    echo 🔒 Security Check: .env file detected
    echo    ✅ This file contains your API keys and will be ignored by Git
    echo    ✅ Make sure it's not accidentally committed!
    echo.
)

REM Initialize Git repository
echo 📦 Initializing Git repository...
git init

REM Set default branch to main (modern standard)
git branch -M main

REM Add all files (except those in .gitignore)
echo 📄 Adding files to Git...
git add .

REM Show status to verify what will be committed
echo.
echo 📋 Git Status - Files to be committed:
echo ======================================
git status --short

REM Check if .env is in the staging area (it shouldn't be!)
git ls-files --stage | findstr "\.env$" >nul
if %errorlevel% equ 0 (
    echo.
    echo 🚨 SECURITY WARNING: .env file is staged for commit!
    echo    This file contains your API keys and should NOT be committed.
    echo    Please check your .gitignore file.
    pause
    exit /b 1
) else (
    echo.
    echo ✅ Security check passed: .env file is properly ignored
)

REM Prompt for commit
echo.
set /p answer="🤔 Ready to make initial commit? (y/N): "
if /i "%answer:~,1%" equ "Y" (
    echo 💾 Creating initial commit...
    git commit -m "Initial commit: GitHub Manager v5" -m "- AI-powered markdown to GitHub issues converter" -m "- Support for DeepSeek AI and regex parsing" -m "- Comprehensive GitHub API integration" -m "- Streamlit web interface" -m "- Repository cleanup tools" -m "- Security-first configuration"
    
    echo.
    echo ✅ Git repository initialized successfully!
    echo.
    echo 📋 Next steps:
    echo    1. Create a repository on GitHub
    echo    2. git remote add origin ^<your-repo-url^>
    echo    3. git push -u origin main
    echo.
    echo 🔒 Security reminders:
    echo    ✅ Your .env file is protected and won't be committed
    echo    ✅ API keys and secrets are safely ignored
    echo    ✅ Virtual environment is excluded from version control
    echo.
) else (
    echo ⏸️  Initialization cancelled. You can run 'git commit' manually when ready.
)

echo 🎉 Setup complete!
pause

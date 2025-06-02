#!/bin/bash

# =============================================================================
# GitHub Manager - Git Repository Setup Script
# =============================================================================
# This script safely initializes Git for the GitHub Manager project
# with proper security measures in place.

echo "🚀 GitHub Manager - Git Setup"
echo "============================="
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f ".gitignore" ]; then
    echo "❌ Error: Please run this script from the githubmanager directory"
    echo "   Expected files: app.py, .gitignore"
    exit 1
fi

# Check if .env file exists and warn user
if [ -f ".env" ]; then
    echo "🔒 Security Check: .env file detected"
    echo "   ✅ This file contains your API keys and will be ignored by Git"
    echo "   ✅ Make sure it's not accidentally committed!"
    echo ""
fi

# Initialize Git repository
echo "📦 Initializing Git repository..."
git init

# Set default branch to main (modern standard)
git branch -M main

# Add all files (except those in .gitignore)
echo "📄 Adding files to Git..."
git add .

# Show status to verify what will be committed
echo ""
echo "📋 Git Status - Files to be committed:"
echo "======================================"
git status --short

# Check if .env is in the staging area (it shouldn't be!)
if git ls-files --stage | grep -q "\.env$"; then
    echo ""
    echo "🚨 SECURITY WARNING: .env file is staged for commit!"
    echo "   This file contains your API keys and should NOT be committed."
    echo "   Please check your .gitignore file."
    exit 1
else
    echo ""
    echo "✅ Security check passed: .env file is properly ignored"
fi

# Prompt for commit
echo ""
read -p "🤔 Ready to make initial commit? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "💾 Creating initial commit..."
    git commit -m "Initial commit: GitHub Manager v5

- AI-powered markdown to GitHub issues converter
- Support for DeepSeek AI and regex parsing
- Comprehensive GitHub API integration
- Streamlit web interface
- Repository cleanup tools
- Security-first configuration"
    
    echo ""
    echo "✅ Git repository initialized successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Create a repository on GitHub"
    echo "   2. git remote add origin <your-repo-url>"
    echo "   3. git push -u origin main"
    echo ""
    echo "🔒 Security reminders:"
    echo "   ✅ Your .env file is protected and won't be committed"
    echo "   ✅ API keys and secrets are safely ignored"
    echo "   ✅ Virtual environment is excluded from version control"
    echo ""
else
    echo "⏸️  Initialization cancelled. You can run 'git commit' manually when ready."
fi

echo "🎉 Setup complete!"

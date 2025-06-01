# 🤖 AI-Powered Markdown ➜ GitHub Issues v5

Transform **any** markdown file into GitHub issues and milestones using AI intelligence!

## ✨ What's New in v5

- **🧠 DeepSeek AI Integration**: Intelligent parsing of natural markdown formats
- **🤖 Reasoning Display**: See how the AI interpreted your content
- **🔄 Smart Fallback**: Traditional regex parsing when AI is unavailable
- **📊 Enhanced UI**: Better visual feedback and status indicators
- **🗑️ Repository Cleanup**: Close old issues and delete milestones

## 🚀 Quick Start

Use `launch.bat` (Windows) or `launch.sh` (Linux/Mac) for full automatic setup!

## 🛠️ Manual Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd githubmanager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   Create a `.env` file with:
   ```env
   GITHUB_TOKEN=your_github_token_here
   REPO_OWNER=your_username_or_org
   REPO_NAME=your_repository_name
   DEEPSEEK_API_KEY=your_deepseek_api_key
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🎯 How It Works

### 🤖 AI Mode (Recommended)
Upload **any** markdown file and let DeepSeek AI intelligently:
- Identify project milestones and phases
- Extract actionable issues and tasks  
- Suggest appropriate labels and assignments
- Provide clear reasoning for decisions

**Example Input:**
```markdown
# Project Setup

We need to set up the basic project structure.

## Database Configuration
- Create schema
- Set up migrations  
- Configure pooling

## Authentication
- Login system
- Password reset
- User roles
```

**AI Output:**
- **Milestone**: "Project Setup" 
- **Issues**: "Database Configuration", "Authentication System"
- **Reasoning**: Detailed explanation of AI's interpretation

### 📝 Traditional Mode (Fallback)
Use structured format when AI is unavailable:
```markdown
# Milestone: Feature Development
description: Main development phase

## Issue: User Authentication
Login and registration system
labels: feature, backend
assignees: developer1
```

## 🔧 Configuration

### GitHub Token
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate new token with `repo` scope
3. Add to `.env` file

### DeepSeek API Key  
1. Visit [DeepSeek Platform](https://platform.deepseek.com)
2. Create account and generate API key
3. Add to `.env` file

## 📋 Features

- **🤖 AI-Powered Parsing**: Natural language markdown processing
- **🧠 Reasoning Transparency**: See AI decision-making process
- **🔄 Intelligent Fallback**: Regex parsing when AI unavailable
- **🧪 Dry Run Mode**: Test without making API calls
- **✏️ Live Editing**: Modify results before GitHub push
- **📊 Real-time Stats**: Track progress and metrics
- **🎯 Smart Labels**: AI suggests contextual labels
- **👥 Assignment Logic**: Intelligent assignee recommendations
- **🗑️ Repository Cleanup**: Close old issues and delete milestones

### 🗑️ Repository Cleanup Features

**⚠️ Important: GitHub API Limitations**

GitHub's API **does not allow true deletion of issues**. This is by design to:
- Maintain audit trails and project history
- Preserve references in commits and pull requests  
- Ensure data integrity and compliance

**What the cleanup tool actually does:**
- **Issues**: Closes them permanently and marks as "not planned"
- **Milestones**: True deletion (removes from all associated issues)
- **Search & Filter**: Find specific issues using GitHub's advanced search

**Cleanup Capabilities:**
- 📋 **Issue Management**: Load, filter, and bulk close issues
- 🎯 **Milestone Deletion**: Remove milestones completely
- 🔍 **Advanced Search**: Use GitHub search syntax for targeted cleanup
- 🧪 **Safe Testing**: Dry run mode shows what would happen
- 📊 **Progress Tracking**: Real-time feedback during bulk operations

**Common Cleanup Patterns:**
```bash
# Close old bugs
label:bug is:open created:<2024-01-01

# Close issues without milestones
is:open no:milestone

# Close very old issues
updated:<2023-01-01

# Close unassigned issues
no:assignee is:open
```

## 🎨 UI Improvements

- Modern, intuitive interface
- Real-time AI status indicators  
- Enhanced progress tracking
- Visual reasoning display
- Responsive design

## 🔒 Security

- Local processing of sensitive data
- Secure API integration
- No data retention by AI service
- Environment-based configuration

## 🐛 Troubleshooting

**AI Not Working?**
- Check DeepSeek API key in `.env`
- Verify internet connection
- Try traditional mode as fallback

**GitHub Errors?**
- Verify token permissions (`repo` scope)
- Check repository owner/name
- Ensure repository exists and is accessible

**Parsing Issues?**
- Try both AI and traditional modes
- Check markdown file encoding (UTF-8)
- Review file format in Help section

**Cleanup Issues?**
- Remember: Issues are **closed**, not deleted (GitHub limitation)
- Use dry run mode first to test operations
- Check that you have write access to the repository
- Milestones can be truly deleted, but this removes them from associated issues

**Why Can't I Delete Issues?**

GitHub deliberately prevents issue deletion through their API because:
- Issues contain important project history and discussions
- Deleting issues would break references in commits, PRs, and other issues
- Many organizations require maintaining audit trails for compliance
- Closed issues can always be reopened if needed

**Alternative Solutions:**
- Use issue labels like "archived" or "obsolete" to mark old issues
- Close issues and remove them from active milestones
- Filter views to hide closed issues in your workflow
- Consider migrating to a new repository if you need a "fresh start"

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make improvements
4. Test thoroughly
5. Submit pull request

## 📜 License

Open source - see LICENSE file for details.

---

**Powered by DeepSeek AI 🧠 | Built with Streamlit 🚀**

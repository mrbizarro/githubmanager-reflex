# 🚀 GitHub Issues Manager - Reflex Version

A modern, fast, and responsive web application for managing GitHub issues and milestones, built with [Reflex](https://reflex.dev). This is a complete migration from the original Streamlit version with improved performance, real-time updates, and a professional UI.

## ✨ Features

- **🤖 AI-Powered Parsing**: Intelligent conversion of natural markdown using DeepSeek AI
- **📁 File Upload & Processing**: Drag & drop markdown files for batch processing
- **✍️ Manual Entry**: Create milestones and issues manually with full control
- **🚀 Real-time Deployment**: Deploy to GitHub with live progress tracking
- **🧹 Repository Cleanup**: Manage existing issues and milestones
- **📊 Real-time Metrics**: Live statistics and progress indicators
- **🎨 Modern UI**: Clean, responsive design with dark/light theme support
- **⚡ Performance**: No page reloads, instant feedback, optimized rendering

## 🛠️ Quick Start

### Prerequisites

- Python 3.8+
- Git
- GitHub Personal Access Token

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd githubmanager_reflex

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```env
# GitHub Settings (Required)
GITHUB_TOKEN=your_github_token_here
REPO_OWNER=your_username_or_org
REPO_NAME=your_repository_name

# DeepSeek AI Settings (Optional)
DEEPSEEK_API_KEY=your_deepseek_api_key

# Application Settings
ENVIRONMENT=production
THEME=dark
```

### 3. GitHub Token Setup

1. Visit [GitHub Token Settings](https://github.com/settings/tokens)
2. Click "Generate new token" → "Generate new token (classic)"
3. Configure:
   - **Note**: "GitHub Issues Manager"
   - **Scopes**: Check `repo` (Full control of private repositories)
4. Copy the generated token to your `.env` file

### 4. Run the Application

```bash
# Development mode
reflex run

# Production mode
reflex run --env prod
```

The application will be available at `http://localhost:3000`

## 🎯 Usage Guide

### 1. **Upload & Convert**
- Upload markdown files (single or batch)
- Choose AI or standard parsing mode
- Review and edit processed content
- Deploy to GitHub with real-time progress

### 2. **Manual Entry**
- Create milestones with descriptions and due dates
- Add issues with labels, assignees, and priorities
- Preview before deployment
- Export as JSON

### 3. **Repository Cleanup**
- Load existing issues and milestones
- Filter and search content
- Bulk select and delete items
- Manage repository organization

### 4. **Settings**
- Configure GitHub API access
- Set up DeepSeek AI (optional)
- Customize application preferences
- Test connections

## 📁 Project Structure

```
githubmanager_reflex/
├── rxconfig.py                 # Reflex configuration
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation
├── .env                        # Configuration (create this)
└── githubmanager_reflex/       # Main package
    ├── __init__.py             # App entry point
    ├── state/                  # State management
    │   ├── app_state.py        # Global app state
    │   ├── file_state.py       # File processing
    │   ├── manual_state.py     # Manual entry
    │   └── deployment_state.py # GitHub deployment
    ├── components/             # UI components
    │   ├── header.py           # Header and navigation
    │   └── ui.py               # Shared UI components
    └── pages/                  # Application pages
        ├── home.py             # Dashboard
        ├── upload.py           # Upload & Convert
        ├── manual.py           # Manual Entry
        ├── cleanup.py          # Repository Cleanup
        └── settings.py         # Settings
```

## 🔧 Development

### Running in Development Mode

```bash
# Install development dependencies
pip install black flake8 pytest pytest-asyncio

# Format code
black .

# Run linting
flake8 .

# Run tests
pytest
```

### Building for Production

```bash
# Export the app
reflex export

# The built files will be in the .web directory
```

## 🚀 Deployment

### Local Deployment

The app runs locally by default. For production deployment, consider:

- **Cloud platforms**: Vercel, Netlify, Railway
- **Self-hosted**: Docker, VPS
- **Reflex Cloud**: Official hosting platform

Refer to [Reflex Deployment Guide](https://reflex.dev/docs/hosting/deploy-overview/) for detailed instructions.

## 🔄 Migration from Streamlit

This Reflex version provides the same functionality as the original Streamlit app with these improvements:

- **Performance**: No page reloads, faster rendering
- **Real-time Updates**: Live progress and instant feedback
- **Better State Management**: Proper state handling across components
- **Modern UI**: Professional design with responsive layout
- **Enhanced UX**: Smooth transitions and interactions

## 🆘 Troubleshooting

### Common Issues

**GitHub Connection Failed**
- Verify token has `repo` scope
- Check repository owner/name spelling
- Ensure repository exists and is accessible

**AI Not Working**
- Check DeepSeek API key
- Verify internet connection
- Use standard mode as fallback

**File Processing Issues**
- Ensure UTF-8 encoding
- Check markdown format
- Try smaller files first

**Installation Problems**
- Use Python 3.8+
- Create fresh virtual environment
- Update pip: `pip install --upgrade pip`

### Getting Help

1. Check the [Reflex Documentation](https://reflex.dev/docs/)
2. Review error messages in the console
3. Open an issue on the repository
4. Check the troubleshooting section in Settings

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgments

- [Reflex](https://reflex.dev) - The framework powering this application
- [DeepSeek](https://platform.deepseek.com/) - AI-powered markdown parsing
- [GitHub API](https://docs.github.com/en/rest) - Repository integration

---

**Built with ❤️ using Reflex**

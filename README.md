# 🚀 GitHub Issues Manager v6

> **Convert markdown documents into organized GitHub issues and milestones**

A modern Streamlit application that intelligently parses markdown files and creates structured GitHub project issues. Features AI-powered parsing with DeepSeek and comprehensive repository management tools.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-green.svg)](https://deepseek.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Key Features

### 🤖 **AI-Powered Markdown Parsing**
- **DeepSeek AI Integration** - Intelligent content analysis and structure recognition
- **Automatic Issue Generation** - Creates properly sized, focused GitHub issues
- **Content Type Detection** - Adapts parsing based on technical vs business content
- **Fallback Parsing** - Works with or without AI configuration

### 📁 **Flexible File Processing**
- **Single & Batch Upload** - Process one file or multiple files simultaneously
- **Real-time Processing** - Live progress updates with async background processing
- **Format Support** - `.md`, `.markdown`, and `.txt` files
- **Performance Optimized** - 60-70% faster processing with intelligent caching

### ✍️ **Manual Project Creation**
- **Interactive Issue Builder** - Create milestones and issues through a modern UI
- **Priority System** - Built-in priority labels with emoji indicators
- **Live Preview** - Review project structure before deployment
- **Bulk Operations** - Create multiple milestones and issues efficiently

### 🗑️ **Repository Management**
- **Issue Cleanup** - Bulk close existing issues with filters
- **Milestone Management** - Create, view, and delete milestones with impact analysis
- **Label System** - Automated setup of modern, color-coded labels
- **Search & Filter** - Advanced repository content discovery

### 🎨 **Modern Interface**
- **shadcn/ui Design** - Beautiful, professional interface with dark/light themes
- **Responsive Layout** - Works perfectly on desktop and mobile devices
- **Functional Sidebar** - Quick access to tools and status indicators
- **Real-time Updates** - Live progress tracking and status monitoring

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- GitHub Personal Access Token
- Git repository access

### **Option 1: Auto Launch (Windows)**
```bash
run-github-manager.bat
```

### **Option 2: Manual Setup**
```bash
# Clone and navigate to directory
git clone <repository-url>
cd githubmanager

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your credentials

# Launch application
streamlit run app_new.py
```

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
# Required: GitHub Integration
GITHUB_TOKEN=your_github_personal_access_token
REPO_OWNER=your_username_or_organization
REPO_NAME=your_repository_name

# Optional: AI Enhancement
DEEPSEEK_API_KEY=your_deepseek_api_key

# Optional: Application Settings
ENVIRONMENT=production
THEME=auto
```

### 🔑 **Getting API Keys**

**GitHub Personal Access Token:**
1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select `repo` scope for full repository access
4. Copy token to `.env` file

**DeepSeek API Key (Optional):**
1. Visit [DeepSeek Platform](https://platform.deepseek.com)
2. Create account and generate API key
3. Add to `.env` file for AI-enhanced parsing

## 📖 How to Use

### **1. Upload & Convert Markdown**
- Upload single files or batch process multiple files
- Choose between AI-powered and standard parsing modes
- Review generated milestones and issues before deployment
- Edit titles, descriptions, labels, and assignments
- Deploy directly to GitHub repository

### **2. Manual Entry**
- Create milestones with custom descriptions and due dates
- Add issues with priority levels and detailed requirements
- Assign team members and apply relevant labels
- Preview project structure before deployment
- Export project data as JSON

### **3. Repository Cleanup**
- Load and filter existing issues by state, date, and other criteria
- Bulk close issues with confirmation dialogs
- Manage milestones with impact analysis for deletions
- Setup standardized label system with colors and descriptions
- Search repository content with advanced filters

## 🏗️ Architecture

```
githubmanager/
├── app_new.py              # Main application entry point
├── components/             # Reusable UI components
│   ├── header.py          # Application header and navigation
│   ├── navigation.py      # Tab-based page routing
│   ├── sidebar.py         # Functional sidebar with tools
│   └── status.py          # Status indicators and metrics
├── pages/                  # Main application pages
│   ├── upload_convert.py  # File upload and processing
│   ├── manual_entry.py    # Manual milestone/issue creation
│   └── repository_cleanup.py # Repository management tools
├── utils/                  # Core utilities and APIs
│   ├── file_processing.py # File validation and preprocessing
│   ├── github_api.py      # GitHub API integration
│   ├── parsing.py         # Markdown parsing logic
│   └── session.py         # Session state management
├── config/                 # Configuration management
│   └── settings.py        # Environment and API configuration
├── assets/                 # Styling and static content
│   └── styles.py          # Modern CSS with shadcn/ui design
└── deepseek_api.py        # DeepSeek AI integration
```

## 🎯 Core Functionality

### **File Processing Pipeline**
1. **Upload Validation** - Check file types, sizes, and formats
2. **Content Preprocessing** - Clean markdown, fix formatting issues
3. **AI Analysis** - DeepSeek analyzes content structure and generates project plans
4. **Structure Generation** - Create milestones with properly scoped issues
5. **Review & Edit** - Modify generated content before deployment
6. **GitHub Deployment** - Create milestones, issues, and labels

### **Label Management System**
The application sets up a modern, organized label system:

**Work Stream Labels:**
- 🧪 `testing-qa` - Testing & Quality Assurance
- 🗄️ `database-migration` - Database & Migration Strategy
- ⚡ `code-quality` - Code Quality & Optimization
- 🔍 `feature-analysis` - Core Feature Analysis
- 🛠️ `tech-stack` - Technology Stack Assessment
- 📚 `documentation` - Documentation & Guides
- 🐛 `bug` - Bug fixes and issues
- ✨ `enhancement` - New features and improvements
- 🚀 `deployment` - Deployment and DevOps
- 🔒 `security` - Security-related tasks

**Priority Levels:**
- `high-priority` - Red - Urgent issues requiring immediate attention
- `medium-priority` - Orange - Standard priority tasks
- `low-priority` - Green - Nice-to-have improvements

### **Smart Issue Generation**
- **Optimal Sizing** - Issues designed for 2-8 hours of focused work
- **Complete Context** - All requirements and acceptance criteria included
- **Technology Agnostic** - No assumptions about implementation approach
- **Priority Assignment** - Automatic priority detection with emoji indicators

## 🔧 Advanced Features

### **Performance Optimizations**
- **Async Processing** - Background file processing with real-time updates
- **Intelligent Caching** - 60-70% faster processing for repeated content
- **Rate Limiting** - Built-in GitHub API throttling and retry logic
- **Concurrent Processing** - Parallel file processing with thread safety

### **Error Handling**
- **Graceful Degradation** - AI failures fall back to standard parsing
- **Detailed Logging** - Comprehensive error reporting and debugging
- **User Feedback** - Clear error messages and recovery suggestions
- **Progress Tracking** - Real-time status updates during operations

### **Data Management**
- **Export Functionality** - Download project structures as JSON
- **Session Persistence** - Maintain state across browser sessions
- **Preview Mode** - Test deployments without making changes
- **Bulk Operations** - Efficient handling of large datasets

## 📱 User Interface

### **Modern Design System**
- **shadcn/ui Components** - Professional, accessible interface
- **Dark/Light Themes** - Automatic theme switching with user preference
- **Responsive Layout** - Optimized for desktop, tablet, and mobile
- **Intuitive Navigation** - Tab-based routing with clear visual hierarchy

### **Real-time Feedback**
- **Progress Indicators** - Live updates during file processing and deployment
- **Status Alerts** - Clear success, warning, and error messages
- **Metrics Dashboard** - Session statistics and performance monitoring
- **Interactive Previews** - Edit generated content before deployment

## 🛠️ Development

### **Requirements**
- Python 3.8 or higher
- Streamlit 1.28+
- GitHub API access
- Optional: DeepSeek API for enhanced parsing

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run app_new.py --server.runOnSave true

# Environment variables for development
cp .env.template .env.dev
```

### **Project Structure Guidelines**
- **Components** - Reusable UI elements with clear interfaces
- **Pages** - Main application sections with focused functionality
- **Utils** - Pure functions for data processing and API calls
- **Config** - Environment and configuration management
- **Assets** - Static content and styling

## 🔍 Troubleshooting

### **Common Issues**

**GitHub API Connection Failed**
- Verify token has `repo` scope
- Check repository name and owner are correct
- Ensure token hasn't expired
- Test connection in Settings

**File Processing Errors**
- Check file format is supported (.md, .markdown, .txt)
- Verify file size is under 10MB
- Ensure file encoding is UTF-8
- Try preprocessing markdown manually

**AI Parsing Issues**
- DeepSeek API key may be invalid or expired
- Check API quota and billing status
- Application automatically falls back to standard parsing
- Monitor error logs for specific failure reasons

**Performance Issues**
- Clear processing cache in session state
- Reduce batch size for large file uploads
- Check network connection stability
- Monitor system memory usage

### **Debug Mode**
Enable detailed logging by setting:
```env
ENVIRONMENT=development
```

This provides:
- Detailed API call logging
- Processing performance metrics
- Session state debugging
- Error stack traces

## 📊 Performance & Limits

### **File Processing**
- **Maximum File Size**: 10MB per file
- **Supported Formats**: .md, .markdown, .txt
- **Batch Processing**: Up to 20 files simultaneously
- **Processing Speed**: 1-3 seconds per file with AI, 0.5-1 second without

### **GitHub API**
- **Rate Limits**: 5,000 requests per hour with authenticated token
- **Automatic Throttling**: Built-in delay between API calls
- **Retry Logic**: Exponential backoff for failed requests
- **Concurrent Operations**: Optimized for bulk operations

### **System Requirements**
- **Memory**: 512MB minimum, 1GB recommended
- **Storage**: 100MB for application and dependencies
- **Network**: Stable internet connection for API calls
- **Browser**: Modern browser with JavaScript enabled

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** following the existing code style
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request** with a clear description

### **Development Guidelines**
- Follow PEP 8 style guidelines
- Add type hints for new functions
- Include docstrings for modules and functions
- Test changes thoroughly before submitting
- Keep components focused and reusable

## 🙏 Acknowledgments

- **DeepSeek** - AI-powered content analysis
- **Streamlit** - Modern web application framework
- **GitHub** - Comprehensive API and platform
- **shadcn/ui** - Beautiful design system
- **Inter Font** - Modern typography

---

**Built for developers who want to transform their markdown documentation into well-organized, actionable GitHub project structures.**

🚀 **Start converting your markdown today!** → `streamlit run app_new.py`
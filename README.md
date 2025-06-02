# 🚀 GitHub Issues Manager v6 - AI Agent

> **Transform any markdown into perfectly-sized GitHub issues optimized for Claude Computer Use**

A sophisticated AI agent that intelligently converts markdown documents into professional GitHub project structures. Built specifically to create issues that are perfectly sized for Claude's context window and Computer Use capabilities.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-green.svg)](https://deepseek.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ What Makes This Special

### 🤖 **Intelligent AI Agent**
This isn't just a script - it's a proper AI agent that:
- **Analyzes content types** (technical, business, research, planning)
- **Makes autonomous decisions** about project organization
- **Adapts behavior** based on content complexity and structure
- **Optimizes output** for Claude Computer Use sessions (2-8 hours per issue)

### 🎯 **Claude-Optimized**
Every issue is perfectly sized for Claude's ~200K token context window:
- **Single-session completion** - each issue can be fully implemented in one go
- **Complete context** - all requirements included, no external research needed
- **Smart boundaries** - logical groupings that make development sense
- **Implementation-ready** - Claude can start coding immediately

### 📋 **Content-Faithful Approach**
The agent strictly adheres to your original content:
- **No inference** - only creates what you explicitly mention
- **Preserves scope** - doesn't expand or enhance your requirements
- **Original terminology** - uses your exact language and descriptions
- **Faithful translation** - organizes your content, doesn't change it

## 🚀 Quick Start

### **Option 1: Automatic Setup**
```bash
# Windows
run-github-manager.bat

# Linux/Mac
./launch.sh
```

### **Option 2: Manual Setup**
```bash
# Clone repository
git clone <your-repo-url>
cd githubmanager

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your API keys

# Launch application
streamlit run app_new.py
```

## ⚙️ Configuration

Create a `.env` file with your API credentials:

```env
# GitHub Integration
GITHUB_TOKEN=your_github_token_here
REPO_OWNER=your_username_or_org
REPO_NAME=your_repository_name

# AI Agent (Optional but Recommended)
DEEPSEEK_API_KEY=your_deepseek_api_key

# Application Settings
ENVIRONMENT=production
THEME=auto
```

### 🔑 **Getting API Keys**

**GitHub Token:**
1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Generate new token with `repo` scope
3. Copy token to `.env` file

**DeepSeek API Key:**
1. Visit [DeepSeek Platform](https://platform.deepseek.com)
2. Create account and generate API key
3. Add to `.env` file

## 🎯 How It Works

### **1. Intelligent Content Analysis**
The AI agent automatically detects your content type:
- 📊 **Technical projects** → Focuses on implementation tasks
- 💼 **Business requirements** → Emphasizes features and user stories  
- 🔬 **Research documents** → Structures investigation tasks
- 🗺️ **Planning content** → Organizes strategic initiatives
- 🔄 **Mixed content** → Balances all aspects appropriately

### **2. Smart Issue Creation**
Each issue is optimized for Claude Computer Use:
- **Perfect scope** - 2-8 hours of focused development work
- **Complete context** - All requirements and acceptance criteria included
- **Technology-agnostic** - Claude chooses the best implementation approach
- **Self-contained** - No external dependencies or missing information

### **3. Professional GitHub Structure**
- **Single milestone** approach for better project management
- **Smart labeling** system for easy filtering and organization
- **Natural groupings** based on your content structure
- **Industry standards** following GitHub best practices

## 📝 Usage Examples

### **Input: Simple Markdown**
```markdown
# User Dashboard Project

Create a dashboard for users to view their information.

## Profile Section
- Display user name and email
- Show profile picture

## Activity Timeline
- Show recent user activities
- Display timestamps
```

### **Output: Claude-Ready Issues**
- **Milestone**: `[01] User Dashboard Project`
- **Issues**:
  - `[Frontend] Build user dashboard with profile section`
  - `[Frontend] Implement activity timeline with timestamps`

Each issue includes:
- Complete functional requirements
- Acceptance criteria
- Technology-agnostic specifications
- Perfect scope for single Claude session

## 🛠️ Features

### **Core Functionality**
- 🤖 **AI-Powered Parsing** - Intelligent markdown analysis with DeepSeek
- 📊 **Dual Parsing Modes** - AI mode + traditional regex fallback
- 🎯 **Claude Optimization** - Issues sized for Computer Use sessions
- 🏷️ **Smart Labeling** - Automatic categorization and organization
- 📱 **Modern UI** - Professional interface with responsive design

### **Advanced Capabilities**
- 🗑️ **Repository Cleanup** - Manage existing issues and milestones
- 📋 **Manual Entry** - Create issues directly in the interface
- 💾 **Data Export** - Download project structure as JSON
- 🔄 **Live Editing** - Modify generated issues before deployment
- 📈 **Progress Tracking** - Real-time deployment status and metrics

### **Repository Management**
- ✏️ **Issue Creation** - Bulk create organized issues and milestones
- 🏷️ **Label Management** - Automatic setup of standardized labels
- 🧹 **Cleanup Tools** - Close old issues and remove milestones
- 🔍 **Advanced Search** - Find and filter repository content

## 🏗️ Architecture

### **Clean Modular Design**
```
githubmanager/
├── app_new.py              # Main application entry point
├── components/             # Reusable UI components
│   ├── header.py
│   ├── navigation.py
│   └── sidebar.py
├── pages/                  # Main application pages
│   ├── upload_convert.py
│   ├── manual_entry.py
│   └── repository_cleanup.py
├── utils/                  # Core utilities
│   ├── file_processing.py
│   ├── parsing.py
│   └── github_api.py
├── config/                 # Configuration management
│   └── settings.py
└── assets/                 # Styling and static files
    └── styles.py
```

### **AI Agent Components**
- **Content Analysis Engine** - Detects document types and complexity
- **Decision Making System** - Autonomous project organization
- **Adaptive Processing** - Tailored output based on content type
- **Quality Assurance** - Validates and optimizes generated structure

## 🎨 Design Philosophy

### **Content-First Approach**
- **Faithful to source** - Only creates what you explicitly mention
- **Preserves intent** - Maintains your original scope and priorities
- **No assumptions** - Doesn't add "standard" features unless specified
- **Direct translation** - Organizes content without enhancement

### **Claude Computer Use Optimization**
- **Perfect session sizing** - Each issue fits Claude's capabilities
- **Complete specifications** - All context included for implementation
- **Research-friendly** - Enough detail for Claude to investigate approaches
- **Implementation-ready** - Clear requirements and acceptance criteria

## 🔧 Troubleshooting

### **AI Agent Issues**
- **Not connecting to DeepSeek?** Check API key in `.env` file
- **Unexpected parsing results?** Try traditional mode as fallback
- **Content not recognized?** Ensure markdown uses clear structure

### **GitHub Integration**
- **API errors?** Verify token has `repo` scope and repository exists
- **Permission issues?** Ensure token has write access to target repository
- **Rate limiting?** Application includes automatic retry logic

### **Application Problems**
- **Startup issues?** Check Python version (3.8+ required)
- **Module errors?** Run `pip install -r requirements.txt`
- **Port conflicts?** Streamlit uses port 8501 by default

## 📈 Performance & Limits

### **Scalability**
- **File size** - Handles documents up to 10MB efficiently
- **Issue count** - Optimized for 5-50 issues per project
- **API rate limits** - Built-in throttling for GitHub and DeepSeek APIs
- **Concurrent users** - Single-user application design

### **Best Practices**
- **Document structure** - Use clear headers and logical organization
- **Content detail** - Provide enough context for meaningful issues
- **Scope definition** - Be specific about requirements and boundaries
- **Regular backups** - Export project data before major changes

## 🤝 Contributing

We welcome contributions! Please:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** following our code style
4. **Test thoroughly** with various markdown inputs
5. **Submit a pull request** with clear description

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Format code
black .
isort .
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DeepSeek** - For providing the AI capabilities
- **Streamlit** - For the excellent web application framework
- **GitHub** - For comprehensive API and platform
- **Claude** - For inspiring the optimization approach

---

**Built with ❤️ for developers who want their markdown converted into perfectly-sized, Claude-ready GitHub issues**

🚀 **Start converting your markdown today!** → `streamlit run app_new.py`
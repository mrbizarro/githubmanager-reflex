# Contributing to GitHub Manager

Thank you for your interest in contributing to GitHub Manager! 🎉

## Quick Start

1. **Fork** the repository
2. **Clone** your fork locally
3. **Set up** development environment
4. **Create** a feature branch
5. **Make** your changes
6. **Test** thoroughly
7. **Submit** a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- (Optional) DeepSeek API account for AI features

### Local Development

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/githubmanager.git
cd githubmanager

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.template .env
# Edit .env with your test credentials

# 5. Run the app
streamlit run app.py
```

## Project Structure

```
githubmanager/
├── app.py                 # Main Streamlit application
├── github_api.py          # GitHub API integration
├── deepseek_api.py        # AI service integration
├── parse_markdown.py      # Markdown parsing logic
├── ai_split.py           # AI content splitting
├── test_deepseek.py      # Testing utilities
├── requirements.txt       # Python dependencies
├── .env.template         # Environment template
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation
├── SECURITY.md          # Security guidelines
├── CONTRIBUTING.md      # This file
└── LICENSE              # MIT License
```

## Contributing Guidelines

### Code Style

- **Python**: Follow PEP 8 style guidelines
- **Comments**: Write clear, concise comments
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Include type hints where appropriate

### Example Code Style

```python
def create_issue(
    title: str, 
    body: str, 
    milestone: Optional[int] = None,
    labels: Optional[List[str]] = None,
    dry_run: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Create an issue in the GitHub repository.
    
    Args:
        title: The issue title
        body: The issue description
        milestone: Optional milestone number
        labels: Optional list of labels
        dry_run: If True, simulate without making API calls
        
    Returns:
        Issue data from GitHub API, or None for dry runs
        
    Raises:
        GitHubError: If the API call fails
    """
    # Implementation here
    pass
```

### Commit Messages

Use conventional commit format:

```
feat: add new AI provider support
fix: resolve markdown parsing edge case
docs: update API documentation
style: format code with black
refactor: simplify error handling
test: add unit tests for GitHub API
chore: update dependencies
```

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Adding tests

## Types of Contributions

### 🐛 Bug Reports

**Before creating a bug report:**
- Check existing issues
- Try the latest version
- Test with minimal configuration

**Include in your bug report:**
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error messages (without sensitive data!)

### ✨ Feature Requests

**Before requesting a feature:**
- Check existing issues and discussions
- Consider if it fits the project scope
- Think about implementation complexity

**Include in your feature request:**
- Clear description of the feature
- Use cases and benefits
- Possible implementation approaches
- Willingness to contribute code

### 📚 Documentation

- Fix typos and grammar
- Improve clarity and examples
- Add missing documentation
- Update outdated information

### 🧪 Testing

- Add unit tests
- Improve test coverage
- Add integration tests
- Test edge cases

## Development Guidelines

### Adding New Features

1. **Discuss first**: Open an issue to discuss the feature
2. **Keep it simple**: Follow the project's simplicity principle
3. **Test thoroughly**: Add appropriate tests
4. **Document well**: Update documentation and examples

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Never expose sensitive information in errors
- Include context for debugging

### API Integration

- Handle rate limits gracefully
- Implement proper retry logic
- Validate inputs thoroughly
- Support dry-run mode for testing

### AI Features

- Provide fallback options when AI is unavailable
- Handle API errors gracefully
- Validate AI responses before using them
- Keep prompts maintainable and clear

## Testing

### Manual Testing

```bash
# Test basic functionality
streamlit run app.py

# Test with different markdown formats
# Test with and without AI enabled
# Test dry-run mode
# Test error conditions
```

### Unit Testing

```bash
# Run existing tests
python -m pytest test_deepseek.py

# Add new tests for your changes
# Test edge cases and error conditions
```

### Integration Testing

- Test with real GitHub repositories (use test repos)
- Test with different AI providers
- Test various markdown formats
- Test error recovery

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No sensitive data in commits
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Manual testing completed
- [ ] Unit tests added/updated
- [ ] Integration tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### Review Process

1. **Automatic checks**: CI/CD runs tests and style checks
2. **Code review**: Maintainers review code and provide feedback
3. **Discussion**: Address questions and suggestions
4. **Approval**: Once approved, PR will be merged

## Security Considerations

### For Contributors

- **Never commit credentials** or API keys
- **Test with dummy data** when possible
- **Report security issues privately** (see SECURITY.md)
- **Follow secure coding practices**

### Code Review Focus

- Input validation
- Error handling
- API security
- Data sanitization

## Getting Help

### Questions?

- **GitHub Discussions**: For general questions
- **GitHub Issues**: For specific problems or features
- **Documentation**: Check README and docs first

### Stuck?

Don't hesitate to ask for help! We're here to support contributors.

## Recognition

Contributors will be:
- Listed in the project README
- Credited in release notes
- Recognized in the community

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to GitHub Manager!** 🚀

Your contributions help make this tool better for everyone.

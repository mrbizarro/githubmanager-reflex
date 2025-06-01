# Security Policy

## Supported Versions

We actively support the latest version of GitHub Manager. Security updates will be provided for:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

## Security Considerations

### 🔐 API Keys and Tokens

This application requires sensitive credentials:

- **GitHub Personal Access Token**: Required for repository access
- **DeepSeek API Key**: Optional, for AI-powered parsing

**NEVER commit these to version control!**

### 🛡️ Best Practices

1. **Environment Variables**: Always store credentials in `.env` file
2. **Token Scopes**: Use minimal required GitHub token scopes
3. **Repository Access**: Ensure tokens only have access to intended repositories
4. **Regular Rotation**: Rotate API keys and tokens regularly
5. **Local Development**: Never share `.env` files or include them in deployments

### 🚨 What We Protect Against

- ✅ Accidental credential commits (via comprehensive `.gitignore`)
- ✅ Token exposure in logs or error messages
- ✅ Unauthorized repository access
- ✅ API rate limit abuse

### 📋 Secure Configuration

1. Copy `.env.template` to `.env`
2. Fill in your credentials
3. Verify `.env` is in `.gitignore`
4. Use minimum required token permissions

### 🔍 GitHub Token Permissions

Required permissions for GitHub Personal Access Token:

- `repo` - Full repository access (for creating issues and milestones)
  
Optional permissions:
- `read:user` - For user information display
- `read:org` - If working with organization repositories

### 🌐 Network Security

- All API calls use HTTPS
- Tokens are sent in Authorization headers (not URLs)
- No credentials stored in browser localStorage/sessionStorage

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** create a public GitHub issue
2. **Do NOT** post details in discussions or forums
3. **Do** contact us privately via email
4. **Do** provide detailed information about the vulnerability

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

### Response Timeline

- **24 hours**: Initial acknowledgment
- **72 hours**: Initial assessment and response plan
- **7 days**: Fix implementation (for critical issues)
- **14 days**: Fix implementation (for non-critical issues)

## Secure Development

### Environment Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd githubmanager

# 2. Set up virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment (NEVER commit this file!)
cp .env.template .env
# Edit .env with your actual credentials

# 5. Verify .env is ignored
git status  # Should NOT show .env file
```

### Code Review Checklist

- [ ] No hardcoded credentials
- [ ] Proper error handling (no credential leaks)
- [ ] Input validation for all user inputs
- [ ] Secure API parameter handling
- [ ] No sensitive data in logs

## Third-Party Dependencies

We regularly audit our dependencies for security vulnerabilities:

- `requests` - HTTP library with security focus
- `streamlit` - Web framework with built-in security features
- `python-dotenv` - Secure environment variable handling

## Compliance

This project follows:

- OWASP security guidelines
- GitHub security best practices
- Python security recommendations
- Least privilege principle

---

**Remember**: Security is everyone's responsibility. When in doubt, err on the side of caution.

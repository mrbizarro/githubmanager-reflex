# 🚀 Deployment Checklist for GitHub Manager

## Pre-Deployment Security Checklist

### 🔒 Credential Security
- [ ] `.env` file exists and contains your actual API keys
- [ ] `.env` file is **NOT** tracked by Git (`git status` should not show it)
- [ ] `.env.template` exists with example values (no real credentials)
- [ ] All sensitive files are listed in `.gitignore`
- [ ] No hardcoded credentials anywhere in the code

### 📁 File Organization
- [ ] All source files are present and up to date
- [ ] `requirements.txt` is complete and current
- [ ] Documentation files are included (README, SECURITY, CONTRIBUTING)
- [ ] License file is present
- [ ] `.gitignore` and `.gitattributes` are configured

### 🧪 Testing
- [ ] Application runs locally without errors
- [ ] AI parsing works (if API key configured)
- [ ] GitHub integration works (if token configured)
- [ ] Dry run mode functions correctly
- [ ] Error handling works as expected

## Git Repository Setup

### 🎯 One-Time Setup

```bash
# Option 1: Use the automated script (recommended)
./setup_git.sh       # Linux/Mac
# or
setup_git.bat        # Windows

# Option 2: Manual setup
git init
git branch -M main
git add .
git status           # Verify .env is NOT listed
git commit -m "Initial commit: GitHub Manager v5"
```

### 🔍 Security Verification

Before pushing to GitHub, verify these files are **NOT** in your repository:

```bash
# Check what files Git is tracking
git ls-files | grep -E "\.(env|key|secret|credential)"

# Should return empty (no results)
# If any files are listed, they need to be removed and added to .gitignore
```

### 🌐 GitHub Repository Creation

1. **Create repository on GitHub**
   - Go to https://github.com/new
   - Repository name: `githubmanager` (or your preferred name)
   - Description: "AI-powered markdown to GitHub issues converter"
   - Set to Public (for open source) or Private
   - **Do NOT** initialize with README, .gitignore, or license (we already have these)

2. **Connect local repository to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git
   git push -u origin main
   ```

## Open Source Deployment

### 📋 Pre-Publication Checklist

- [ ] **Code Review**: All code is clean and well-documented
- [ ] **Security Audit**: No credentials or sensitive data in repository
- [ ] **Documentation**: README is comprehensive and up-to-date
- [ ] **License**: Appropriate license is included (MIT recommended)
- [ ] **Contributing Guidelines**: CONTRIBUTING.md is clear and helpful
- [ ] **Security Policy**: SECURITY.md explains security practices
- [ ] **Issue Templates**: Consider adding GitHub issue templates

### 🏷️ Repository Configuration

1. **Repository Settings**
   - Enable Issues (for bug reports and feature requests)
   - Enable Discussions (for community questions)
   - Add repository topics: `python`, `streamlit`, `github-api`, `ai`, `markdown`
   - Add description and website URL

2. **Branch Protection** (recommended for collaboration)
   - Protect main branch
   - Require pull request reviews
   - Require status checks
   - Include administrators in restrictions

3. **Security Settings**
   - Enable Dependabot alerts
   - Enable security advisories
   - Configure code scanning (if available)

### 📢 Community Features

1. **Issue Templates** (optional but recommended)
   - Bug report template
   - Feature request template
   - Question template

2. **Pull Request Template** (optional)
   - Checklist for contributors
   - Testing requirements
   - Documentation requirements

## Post-Deployment

### 🔍 Verification Steps

After pushing to GitHub:

1. **Repository Check**
   - [ ] Repository is accessible
   - [ ] All files are present
   - [ ] `.env` file is **NOT** visible in the repository
   - [ ] README displays correctly

2. **Functionality Test**
   - [ ] Clone the repository to a new location
   - [ ] Set up environment (`cp .env.template .env`)
   - [ ] Install dependencies (`pip install -r requirements.txt`)
   - [ ] Test basic functionality

3. **Security Verification**
   - [ ] Search repository for any exposed credentials
   - [ ] Verify `.env.template` contains no real values
   - [ ] Check that sensitive patterns are properly ignored

### 📊 Monitoring

- Monitor repository for security alerts
- Watch for issues and pull requests
- Keep dependencies updated
- Regular security audits

## Troubleshooting

### 🚨 If You Accidentally Commit Secrets

**IMMEDIATE ACTION REQUIRED:**

1. **Change all exposed credentials immediately**
   - Revoke GitHub tokens
   - Regenerate API keys
   - Update any affected accounts

2. **Remove from Git history**
   ```bash
   # Remove file from Git history (destructive!)
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch .env' \
   --prune-empty --tag-name-filter cat -- --all
   
   # Force push to remote
   git push origin --force --all
   ```

3. **Verify cleanup**
   - Check GitHub repository online
   - Ensure no traces of credentials remain
   - Consider making repository private temporarily

### 🔧 Common Issues

**Git won't ignore .env file:**
- Ensure `.env` is exactly as written in `.gitignore`
- If already tracked: `git rm --cached .env`
- Commit the removal: `git commit -m "Remove .env from tracking"`

**Files not being ignored:**
- Check `.gitignore` syntax
- Ensure no spaces or extra characters
- Test with `git check-ignore -v filename`

## Success Metrics

Your deployment is successful when:

- ✅ Repository is public and accessible
- ✅ No sensitive data is exposed
- ✅ Documentation is clear and helpful
- ✅ Code is well-organized and readable
- ✅ Security best practices are followed
- ✅ Community can contribute easily

## Final Security Reminder

**🔒 NEVER commit real credentials to version control!**

Even in private repositories, credentials can be:
- Accidentally exposed through repository transfers
- Visible to collaborators who shouldn't have access
- Compromised through security breaches
- Leaked through repository forks

Always use environment variables and `.env` files for sensitive data.

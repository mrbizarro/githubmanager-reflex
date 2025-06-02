# 🛠️ GitHub Manager - Troubleshooting Guide

## ✅ Quick Fix Summary

The main issue was **quotes around your DeepSeek API key** in the .env file. This has been fixed:

**Before (broken):**
```
DEEPSEEK_API_KEY='sk-454fd0c9dcdf4ad18700f84215540bc7'
```

**After (fixed):**
```
DEEPSEEK_API_KEY=sk-454fd0c9dcdf4ad18700f84215540bc7
```

## 🚀 How to Run the Fixed Application

1. **Use the improved launch script:**
   ```cmd
   cd C:\vibecode\githubmanager
   launch_improved.bat
   ```

2. **Or run manually:**
   ```cmd
   cd C:\vibecode\githubmanager
   python quick_test.py  # Test API first
   streamlit run app.py --server.port 8502
   ```

## 🧪 Testing Your Setup

Run the quick test to verify everything works:
```cmd
python quick_test.py
```

This will test:
- ✅ API key is loaded correctly
- ✅ DeepSeek API connection works
- ✅ Basic API functionality

## 🔧 Common Issues & Solutions

### Issue: "Read timed out" Error
**Cause:** Network timeout or slow API response
**Solutions:**
- ✅ **FIXED:** Increased timeout from 60s to 120s
- Check your internet connection
- Try again during off-peak hours

### Issue: "AI parsing failed, falling back to regex"
**Causes & Solutions:**
1. **API Key Issues:**
   - ✅ **FIXED:** Removed quotes from API key
   - Verify key is correct on https://platform.deepseek.com

2. **Network Issues:**
   - Check firewall/antivirus blocking connections
   - Try using a VPN if corporate network blocks API access

3. **API Rate Limits:**
   - Wait a few minutes and try again
   - Check your DeepSeek account for usage limits

### Issue: GitHub Integration Problems
**Check your .env file has:**
```
GITHUB_TOKEN=ghp_your_token_here
REPO_NAME=NotTherapy-
REPO_OWNER=mrbizarro
DEEPSEEK_API_KEY=sk-454fd0c9dcdf4ad18700f84215540bc7
```

## 🎯 Current Configuration Status

Your `.env` file is now configured with:
- ✅ GitHub Token: `ghp_1rzJPor...` (configured)
- ✅ Repository: `mrbizarro/NotTherapy-` (configured)
- ✅ DeepSeek API: `sk-454fd0c9...` (fixed - quotes removed)

## 🌐 Application URLs

When running:
- **Local:** http://localhost:8502
- **Network:** http://10.0.0.6:8502 (accessible from other devices on your network)

## 📋 What to Expect Now

1. **✅ AI Status should show "Ready"** instead of "Offline"
2. **✅ Intelligent markdown parsing** should work
3. **✅ No more timeout errors** (increased timeout)
4. **✅ Proper error handling** with detailed messages

## 🆘 If You Still Have Issues

1. **Run the diagnostics:**
   ```cmd
   python test_deepseek.py
   ```

2. **Check the quick test:**
   ```cmd
   python quick_test.py
   ```

3. **Verify your API key:**
   - Log into https://platform.deepseek.com
   - Check if your API key is still valid
   - Verify you have remaining credits/usage

4. **Network troubleshooting:**
   - Try from a different network
   - Check if corporate firewall blocks API access
   - Temporarily disable antivirus/firewall

## 💡 Pro Tips

- **Use Dry Run mode first** to test without making actual GitHub changes
- **Start with small markdown files** to test the AI parsing
- **Keep your .env file private** - don't commit it to version control
- **Regular API key rotation** for security

## 🎉 Success Indicators

When everything is working, you'll see:
- 🤖 **AI Status: Ready** (green checkmark)
- 🚀 **GitHub: Connected** (green checkmark)  
- 📝 **Intelligent markdown parsing** working on any format
- 🧠 **AI reasoning** displayed when processing files

The application should now work perfectly with your NotTherapy project!

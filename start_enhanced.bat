@echo off
echo 🚀 GitHub Issues Manager - Enhanced Deployment System
echo ================================================
echo.

echo Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo.
echo Checking required packages...
python -c "import streamlit; print('✅ Streamlit found')" 2>nul || (
    echo ⚠️ Streamlit not found. Installing...
    pip install streamlit
)

python -c "import requests; print('✅ Requests found')" 2>nul || (
    echo ⚠️ Requests not found. Installing...
    pip install requests
)

python -c "import python-dotenv; print('✅ python-dotenv found')" 2>nul || (
    echo ⚠️ python-dotenv not found. Installing...
    pip install python-dotenv
)

echo.
echo Checking .env configuration...
if exist .env (
    echo ✅ .env file found
) else (
    echo ⚠️ .env file not found. Creating template...
    echo GITHUB_TOKEN=your_github_token_here > .env
    echo REPO_OWNER=your_username >> .env
    echo REPO_NAME=your_repo_name >> .env
    echo DEEPSEEK_API_KEY=your_deepseek_api_key_here >> .env
    echo.
    echo 📝 Please edit .env file with your actual credentials before running the app.
    echo 💡 GitHub token needs 'repo' scope for full functionality.
)

echo.
echo Testing enhanced deployment system...
python test_deployment.py
if %errorlevel% neq 0 (
    echo ⚠️ Some tests failed, but the app should still work.
)

echo.
echo 🎯 Starting GitHub Issues Manager with Enhanced Deployment...
echo 📱 Your browser will open automatically.
echo 🔄 To stop the app, press Ctrl+C in this window.
echo.

streamlit run app.py

pause

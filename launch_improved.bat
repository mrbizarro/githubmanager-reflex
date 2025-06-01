@echo off
echo 🚀 Starting GitHub Manager Application
echo =====================================

echo.
echo 🔧 Checking environment...

:: Check if .env file exists
if not exist .env (
    echo ❌ .env file not found!
    echo 💡 Please create a .env file with your API keys
    echo.
    echo Example .env file:
    echo GITHUB_TOKEN=your_github_token
    echo REPO_NAME=your_repo_name
    echo REPO_OWNER=your_username
    echo DEEPSEEK_API_KEY=your_deepseek_api_key
    echo.
    pause
    exit /b 1
)

echo ✅ .env file found

:: Check if virtual environment exists
if not exist venv (
    echo ⚠️  Virtual environment not found, creating one...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        echo 💡 Make sure Python is installed and in your PATH
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

:: Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

:: Install requirements
echo 📦 Installing/updating requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

:: Run quick API test
echo.
echo 🧪 Running quick API test...
python quick_test.py

echo.
echo 🌐 Starting Streamlit application...
echo 💡 The app will open in your browser at http://localhost:8502
echo 🛑 Press Ctrl+C to stop the application
echo.

:: Start the application
streamlit run app.py --server.port 8502

echo.
echo 👋 Application stopped
pause

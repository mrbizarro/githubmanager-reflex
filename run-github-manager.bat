@echo off
echo 🚀 Starting GitHub Manager App (New Version)
echo ============================================
echo.

REM Navigate to the GitHub Manager directory
cd /d "C:\vibecode\githubmanager"

REM Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo 🔄 Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Virtual environment not found, using system Python
)

REM Check if Streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

echo 🌐 Starting Streamlit app...
echo 📍 App will open at: http://localhost:8501
echo.
echo 🎯 Ready to manage GitHub milestones and issues!
echo.

REM Run the new app version
streamlit run app_new.py

echo.
echo 🏁 GitHub Manager App closed
pause

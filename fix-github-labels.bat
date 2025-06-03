@echo off
echo 🎨 GitHub Label Fixer - Apply Modern Colored Labels
echo =====================================================
echo.

REM Check if we're in the right directory
if not exist "github_api.py" (
    echo ❌ Error: github_api.py not found!
    echo Please run this script from the githubmanager directory
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ❌ Error: .env file not found!
    echo Please create .env file with your GitHub configuration:
    echo   GITHUB_TOKEN=your_github_token
    echo   REPO_OWNER=your_username_or_org  
    echo   REPO_NAME=your_repository_name
    pause
    exit /b 1
)

echo ✅ Found required files
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment not found, using system Python
)

echo.
echo 🚀 Running GitHub label fixer...
echo.

REM Run the Python script
python fix_github_labels.py

REM Check if script ran successfully
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Script failed with error level %ERRORLEVEL%
    echo.
) else (
    echo.
    echo ✅ Script completed successfully!
    echo.
)

echo Press any key to exit...
pause >nul

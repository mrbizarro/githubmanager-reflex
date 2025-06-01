@echo off
SETLOCAL
echo Checking Python...
python --version || (
    echo Python is not installed or not in PATH. Exiting.
    pause
    exit /b 1
)

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt || (
    echo Failed to install requirements!
    pause
    exit /b 1
)

echo Launching the app...
streamlit run app.py

pause
ENDLOCAL

@echo off
echo ===============================
echo GitHub Issues Manager v6 
echo CLEAN & WORKING VERSION
echo ===============================
echo.

echo 🧪 Testing app components...
python test_clean.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Component test failed!
    echo Check the error above and fix any issues.
    pause
    exit /b 1
)

echo.
echo ✅ All tests passed! Launching app...
echo.
echo 🚀 Starting Streamlit app...
echo 👀 The app will open in your browser
echo 🛑 Press Ctrl+C to stop
echo.

streamlit run app_new.py --server.headless false

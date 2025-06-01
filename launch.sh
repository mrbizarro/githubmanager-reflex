#!/bin/bash
set -e
echo "Checking Python..."
python3 --version || { echo "Python3 not installed."; exit 1; }
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi
echo "Activating virtual environment..."
source venv/bin/activate
echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "Launching the app..."
streamlit run app.py

@echo off
title AI Resume Screening System (Flask)
echo =======================================================
echo    AI Resume Screening System - Setup and Launch
echo    Hugging Face Neural Engine (T5 + MiniLM + FAISS)
echo =======================================================

cd /d "%~dp0"

if not exist venv (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Checking / Installing dependencies...
pip install -r requirements.txt

echo [INFO] Launching NeuralScreen Flask Application...
start http://127.0.0.1:5000
python app.py

pause

@echo off
setlocal enabledelayedexpansion

echo ===========================================
echo   StrengerChat Pro - Local Setup & Start
echo ===========================================

:: 1. Check for Virtual Environment
if not exist .venv (
    echo [1/4] Creating Virtual Environment...
    python -m venv .venv
)

:: 2. Activate Venv and Install Requirements
echo [2/4] Installing/Updating Requirements...
call .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

:: 3. Check/Create .env
echo [3/4] Validating Configuration...
if not exist .env (
    echo DB_HOST=localhost > .env
    echo DB_USER=root >> .env
    echo DB_PASSWORD= >> .env
    echo DB_NAME=strengerchat_pro >> .env
    echo SECRET_KEY=!random!!random!!random! >> .env
    echo [!] Created default .env - Please edit if you have a MySQL password.
)

:: 4. Start the Application
echo [4/4] Starting Server at http://localhost:8000
echo [!] The database will be initialized automatically on first startup.
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause

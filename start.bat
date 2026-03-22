@echo off
echo ================================================
echo   Smart Hospital System - Setup ^& Start
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Install Python packages
echo [1/3] Installing Python packages...
cd backend
pip install -r requirements.txt

REM Setup SQLite DB
echo.
echo [2/3] Setting up SQLite Database...
python init_db.py

REM Start Flask
echo.
echo [3/3] Starting Flask backend on http://localhost:5000 ...
echo [4/4] Open your browser and go to: http://localhost:5000
echo.
echo ================================================
echo   DEMO CREDENTIALS:
echo   Super Admin:  superadmin / Admin@123
echo   Hospital:     HOSP001 / Admin@123
echo   Patient:      Register at signup page
echo ================================================
echo.
python app.py
echo.
echo [ERROR] The server has stopped. Check the messages above.
pause

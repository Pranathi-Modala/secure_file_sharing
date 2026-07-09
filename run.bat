@echo off
REM ============================================
REM Secure File Transfer System - Startup Script
REM ============================================
REM This script sets up and runs the Flask application

echo.
echo ========================================
echo Secure File Transfer System - Flask App
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Install requirements if not already installed
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Starting Flask Application
echo ========================================
echo.
echo Access the application at: http://127.0.0.1:5000
echo.
echo Demo Credentials:
echo   Username: alice / Password: alice123
echo   Username: bob / Password: bob123
echo   Username: admin / Password: admin123
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask app
python -m flask --app "app:create_app()" run --debug

pause

@echo off
title SmartGov - Public Complaint System
color 0A

echo ============================================
echo   SmartGov Complaint System - Starting...
echo ============================================
echo.

:: Move to backend folder
cd /d "%~dp0backend"

:: Install dependencies
echo [1/2] Installing dependencies...
pip install fastapi uvicorn[standard] python-multipart pydantic[email] >nul 2>&1
echo       Done!
echo.

:: Start server
echo [2/2] Starting server...
echo.
echo ============================================
echo   Server is running!
echo   Open in browser: http://localhost:8000
echo ============================================
echo.
echo   Press Ctrl+C to stop the server.
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause

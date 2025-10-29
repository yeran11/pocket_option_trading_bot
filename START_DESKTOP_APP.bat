@echo off
title Trading Bot Pro - Desktop Application
color 0A

echo ================================================
echo    TRADING BOT PRO - DESKTOP APPLICATION
echo ================================================
echo.
echo [INFO] No API keys or login required!
echo [INFO] Works with traditional indicators
echo [INFO] Optional AI can be added later
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo [SETUP] First-time setup - Installing dependencies...
    echo [SETUP] This will take 1-2 minutes...
    echo.
    call npm install
    echo.
    echo [DONE] Setup complete!
    echo.
)

echo [LAUNCH] Starting Trading Bot Pro...
echo [LAUNCH] Desktop window opening...
echo.

REM Start the Electron app
call npm start

REM Keep window open if error occurs
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application
    echo Please ensure Node.js is installed
    pause
)
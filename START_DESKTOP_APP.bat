@echo off
title Trading Bot Pro - Desktop Application
color 0A

echo =================================
echo    TRADING BOT PRO - DESKTOP
echo =================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

echo Launching Trading Bot Desktop Application...
echo.
echo NOTE: To create installer, run: npm run dist
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
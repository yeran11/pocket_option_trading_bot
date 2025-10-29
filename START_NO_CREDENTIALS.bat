@echo off
title Trading Bot Pro - No Credentials Version
color 0A

echo ================================================
echo    TRADING BOT PRO - NO CREDENTIALS MODE
echo ================================================
echo.
echo [INFO] No API keys or credentials required!
echo [INFO] Works with traditional indicators
echo [INFO] You log in via Pocket Option browser
echo.

REM Directly launch the simplified version
echo [LAUNCH] Starting credential-free version...
echo.

npx electron electron-main-simple.js

REM If error occurs
if errorlevel 1 (
    echo.
    echo ================================================
    echo   ERROR: Could not start application
    echo ================================================
    echo.
    echo Possible fixes:
    echo   1. Run: npm install
    echo   2. Run: FIX_NO_CREDENTIALS.bat
    echo   3. Make sure electron-main-simple.js exists
    echo.
    pause
)

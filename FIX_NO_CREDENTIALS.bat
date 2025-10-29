@echo off
title Trading Bot Pro - Fix No Credentials Mode
color 0A

echo ================================================
echo   FIX: REMOVE CREDENTIAL SCREENS
echo ================================================
echo.
echo This will switch to the credential-free version
echo.

REM Check if simplified files exist
if not exist electron-main-simple.js (
    echo ERROR: electron-main-simple.js not found!
    echo Please make sure you downloaded all files from GitHub.
    pause
    exit /b 1
)

echo [1/4] Backing up old files...
if exist electron-main.js.old del electron-main.js.old
if exist electron-preload.js.old del electron-preload.js.old
if exist electron-main.js ren electron-main.js electron-main.js.old
if exist electron-preload.js ren electron-preload.js electron-preload.js.old

echo [2/4] Installing credential-free version...
copy /Y electron-main-simple.js electron-main.js
copy /Y electron-preload-simple.js electron-preload.js

if exist electron-ui\main-window-simple.html (
    if exist electron-ui\main-window.html.old del electron-ui\main-window.html.old
    if exist electron-ui\main-window.html ren electron-ui\main-window.html main-window.html.old
    copy /Y electron-ui\main-window-simple.html electron-ui\main-window.html
)

echo [3/4] Creating .env file (to prevent errors)...
if not exist pocket_option_trading_bot mkdir pocket_option_trading_bot
if not exist pocket_option_trading_bot\.env (
    echo # No credentials needed - Bot works with traditional indicators > pocket_option_trading_bot\.env
    echo # This file prevents startup errors >> pocket_option_trading_bot\.env
    echo. >> pocket_option_trading_bot\.env
    echo # Optional: Add AI keys here later if you want AI features >> pocket_option_trading_bot\.env
    echo # OPENAI_API_KEY=your-key-here >> pocket_option_trading_bot\.env
    echo # CLAUDE_API_KEY=your-key-here >> pocket_option_trading_bot\.env
)

echo [4/4] Verifying setup...
if exist electron-main.js (
    echo.
    echo ================================================
    echo   SUCCESS! CREDENTIAL-FREE VERSION INSTALLED
    echo ================================================
    echo.
    echo The app will now:
    echo   - Launch directly to main window
    echo   - NO credential prompts
    echo   - NO API key requirements
    echo   - Work with traditional indicators
    echo.
    echo Starting the app now...
    echo.
    timeout /t 2 /nobreak >nul
    npm start
) else (
    echo.
    echo ERROR: Fix failed. Files may be missing.
    pause
)

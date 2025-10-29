@echo off
title Trading Bot Pro - Quick Setup
color 0A

echo =================================
echo    TRADING BOT PRO - QUICK SETUP
echo =================================
echo.
echo [INFO] Setting up credential-free desktop app
echo [INFO] No API keys or login screens required
echo.

REM Rename files to use simplified versions
if exist electron-main-simple.js (
    echo Applying simplified configuration...
    copy /Y electron-main-simple.js electron-main.js
    copy /Y electron-preload-simple.js electron-preload.js
    copy /Y package-fixed.json package.json
    copy /Y electron-ui\main-window-simple.html electron-ui\main-window.html
    echo Configuration applied!
) else (
    echo Error: Simplified files not found!
    echo Please make sure you extracted all files.
    pause
    exit /b 1
)

echo.
echo Cleaning old installation...
if exist node_modules rmdir /S /Q node_modules
if exist package-lock.json del package-lock.json

echo.
echo Installing clean dependencies...
call npm install electron@27.0.0 electron-updater@6.1.4

if errorlevel 1 (
    echo.
    echo Installation failed. Trying alternative method...
    call npm install electron --save-dev
    call npm install electron-updater --save
)

echo.
echo =================================
echo    SETUP COMPLETE!
echo =================================
echo.
echo Starting Trading Bot Pro...
echo.

timeout /t 2 /nobreak >nul

call npm start

if errorlevel 1 (
    echo.
    echo If the app didn't start, try running: npx electron electron-main.js
    pause
)
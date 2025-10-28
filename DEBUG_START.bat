@echo off
title Trading Bot Pro - Debug Launcher
color 0A

echo =================================
echo    TRADING BOT PRO - DEBUG
echo =================================
echo.

echo Checking Node.js installation...
node --version
if errorlevel 1 (
    echo.
    echo ERROR: Node.js is not installed!
    echo.
    echo Please install Node.js from:
    echo https://nodejs.org
    echo.
    echo Download and install Node.js, then try again.
    pause
    exit /b 1
)

echo Checking npm...
call npm --version
if errorlevel 1 (
    echo.
    echo ERROR: npm is not available!
    pause
    exit /b 1
)

echo.
echo Node.js is installed. Checking project files...
echo.

if not exist "package.json" (
    echo ERROR: package.json not found!
    echo Make sure you're running this from the correct folder.
    echo.
    echo Current folder: %CD%
    echo.
    echo Expected files:
    echo - package.json
    echo - electron-main.js
    echo - electron-ui folder
    echo.
    pause
    exit /b 1
)

echo Installing dependencies...
call npm install
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Try running these commands manually:
    echo   1. Open Command Prompt as Administrator
    echo   2. Navigate to: %CD%
    echo   3. Run: npm install
    pause
    exit /b 1
)

echo.
echo Starting Trading Bot Desktop Application...
echo.

call npm start
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application!
    echo.
    echo Try running manually:
    echo   npm start
    echo.
    pause
    exit /b 1
)

pause
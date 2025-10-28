#!/bin/bash
# Trading Bot Pro - Desktop Application Launcher

echo "================================="
echo "   TRADING BOT PRO - DESKTOP    "
echo "================================="
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if Electron is installed
if [ ! -f "node_modules/.bin/electron" ]; then
    echo "📦 Installing Electron..."
    npm install electron
fi

echo "🚀 Launching Trading Bot Desktop Application..."
echo ""

# Start the Electron app
npm start
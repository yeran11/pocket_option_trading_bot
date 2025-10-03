#!/bin/bash

echo ""
echo "=========================================================================="
echo "  🚀 STARTING POCKET OPTION TRADING BOT SERVER"
echo "=========================================================================="
echo ""

# Kill any existing server
pkill -9 -f "python3 main.py" 2>/dev/null
sleep 1

# Start the server
echo "✅ Launching Flask server on port 5000..."
echo ""
python3 main.py

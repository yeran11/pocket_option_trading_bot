#!/bin/bash

echo "========================================="
echo "🔍 MONITORING SYSTEM - WATCHING FOR RUN BUTTON"
echo "========================================="
echo ""
echo "✅ Monitoring is ACTIVE"
echo "👉 Press the RUN button NOW"
echo ""
echo "I'm watching for:"
echo "  • New Python processes"
echo "  • New bash processes"
echo "  • File access to main.py"
echo "  • Port 5000 activity"
echo ""
echo "========================================="
echo ""

# Monitor for 60 seconds
for i in {1..60}; do
    # Check for Python processes
    PYTHON_PROCS=$(ps aux | grep "python.*main.py" | grep -v grep | wc -l)

    # Check if port 5000 is in use
    PORT_CHECK=$(netstat -tuln 2>/dev/null | grep ":5000" | wc -l)

    # Check for new bash processes running .replit command
    BASH_PROCS=$(ps aux | grep -E "bash.*START|bash.*main.py|python3.*main" | grep -v grep | grep -v monitor | wc -l)

    if [ "$PYTHON_PROCS" -gt 0 ]; then
        echo "✅ DETECTED: Python process started!"
        ps aux | grep python | grep -v grep
        echo ""
    fi

    if [ "$PORT_CHECK" -gt 0 ]; then
        echo "✅ DETECTED: Port 5000 is active!"
        netstat -tuln 2>/dev/null | grep ":5000"
        echo ""
    fi

    if [ "$BASH_PROCS" -gt 0 ]; then
        echo "✅ DETECTED: Bash process started!"
        ps aux | grep bash | grep -E "START|main" | grep -v grep | grep -v monitor
        echo ""
    fi

    # Show heartbeat every 5 seconds
    if [ $((i % 5)) -eq 0 ]; then
        echo "⏱️  Still monitoring... (${i} seconds elapsed)"
    fi

    sleep 1
done

echo ""
echo "========================================="
echo "🛑 MONITORING COMPLETE"
echo "========================================="
echo ""
echo "Summary:"
ps aux | grep -E "python|bash.*main|START" | grep -v grep | grep -v monitor

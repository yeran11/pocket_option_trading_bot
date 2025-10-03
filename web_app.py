"""
Pocket Option Trading Bot - WEB INTERFACE
Run this in Replit - Access through browser!
"""
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import threading
import queue
import json
import time
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global state
bot_status = {
    'running': False,
    'logged_in': False,
    'balance': 0,
    'trades': 0,
    'wins': 0,
    'losses': 0,
    'current_asset': None,
    'message': 'Bot not started'
}

log_queue = queue.Queue()
bot_thread = None
settings = {
    'FAST_MA': 9,
    'SLOW_MA': 21,
    'RSI_ENABLED': True,
    'RSI_PERIOD': 14,
    'RSI_UPPER': 70,
    'MIN_PAYOUT': 85,
    'MIN_CONFIDENCE': 4,
    'TAKE_PROFIT_ENABLED': False,
    'TAKE_PROFIT': 100,
    'STOP_LOSS_ENABLED': False,
    'STOP_LOSS': 50,
    'MARTINGALE_ENABLED': False,
    'MARTINGALE_LIST': [1, 2, 4, 8],
    'VICE_VERSA': False,
}

def log_message(message):
    """Add message to log queue"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_queue.put(f"[{timestamp}] {message}")
    print(f"[{timestamp}] {message}")

def run_bot():
    """Run the trading bot in background"""
    global bot_status

    try:
        log_message("🚀 Starting bot...")
        bot_status['message'] = 'Initializing...'

        # Import bot components
        import asyncio
        import sys
        sys.path.insert(0, os.path.dirname(__file__))

        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        log_message("📦 Loading bot modules...")
        from po_bot_free import get_driver, wait_for_login, check_account_setup

        async def bot_main():
            global bot_status

            log_message("🌐 Opening Chrome browser...")
            bot_status['message'] = 'Opening browser...'

            driver = await get_driver()

            log_message("🔗 Navigating to Pocket Option...")
            driver.get('https://pocket2.click/')
            await asyncio.sleep(3)

            bot_status['message'] = 'Waiting for login...'
            log_message("👤 Please login in the Chrome window that opened!")
            log_message("⏳ Waiting for you to login...")

            # Wait for login
            login_success = await wait_for_login(driver)

            if not login_success:
                log_message("❌ Login timeout!")
                bot_status['running'] = False
                return

            bot_status['logged_in'] = True
            log_message("✅ Login detected!")

            # Check setup
            await check_account_setup(driver)

            bot_status['message'] = 'Trading...'
            log_message("🎯 Bot started trading!")

            # Import trading functions
            from po_bot_free import websocket_log, check_indicators, check_deposit

            # Main trading loop
            while bot_status['running']:
                try:
                    await websocket_log(driver)
                    await check_indicators(driver)
                    await check_deposit(driver)
                    await asyncio.sleep(0.5)
                except Exception as e:
                    log_message(f"⚠️ Error: {e}")
                    await asyncio.sleep(1)

        # Run the bot
        loop.run_until_complete(bot_main())

    except Exception as e:
        log_message(f"❌ Bot error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bot_status['running'] = False
        bot_status['message'] = 'Stopped'
        log_message("⏹️ Bot stopped")

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', settings=settings)

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    global bot_thread, bot_status, settings

    if bot_status['running']:
        return jsonify({'status': 'error', 'message': 'Bot already running'})

    # Update settings from request
    data = request.json
    if data:
        settings.update(data)
        log_message(f"⚙️ Settings updated: {data}")

    bot_status['running'] = True
    bot_status['trades'] = 0
    bot_status['wins'] = 0
    bot_status['losses'] = 0

    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    log_message("▶️ Bot starting...")

    return jsonify({'status': 'success', 'message': 'Bot started'})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    global bot_status

    if not bot_status['running']:
        return jsonify({'status': 'error', 'message': 'Bot not running'})

    bot_status['running'] = False
    log_message("⏸️ Stopping bot...")

    return jsonify({'status': 'success', 'message': 'Bot stopping...'})

@app.route('/api/status')
def get_status():
    """Get current bot status"""
    return jsonify(bot_status)

@app.route('/api/logs')
def get_logs():
    """Stream logs to browser"""
    def generate():
        while True:
            try:
                message = log_queue.get(timeout=1)
                yield f"data: {json.dumps({'message': message})}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Get or update settings"""
    global settings

    if request.method == 'POST':
        data = request.json
        settings.update(data)
        log_message(f"⚙️ Settings updated")
        return jsonify({'status': 'success', 'settings': settings})

    return jsonify(settings)

if __name__ == '__main__':
    log_message("=" * 60)
    log_message("🌐 POCKET OPTION WEB INTERFACE STARTING")
    log_message("=" * 60)
    log_message("")
    log_message("📱 Access the bot through your browser!")
    log_message("🔗 URL will appear above...")
    log_message("")

    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

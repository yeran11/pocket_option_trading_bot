#!/usr/bin/env python3
"""
POCKET OPTION TRADING BOT
"""

# IMMEDIATE OUTPUT - THIS PROVES RUN BUTTON WORKS
print("\n" * 3)
print("=" * 80)
print("=" * 80)
print("        RUN BUTTON PRESSED - SERVER STARTING NOW!")
print("=" * 80)
print("=" * 80)
print("\n")

import sys
import os

# More immediate output
print("✅ Python is running")
print("✅ Working directory:", os.getcwd())
print("\n")

# Install Flask if needed
try:
    from flask import Flask, render_template, jsonify, request, Response
    print("✅ Flask is ready")
except ImportError:
    print("📦 Installing Flask...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask', '-q'])
    from flask import Flask, render_template, jsonify, request, Response
    print("✅ Flask installed successfully")

print("\n")

import json
from datetime import datetime
import time
import threading
import random

print("✅ Creating Flask application...")

app = Flask(__name__)

# Bot state
bot_state = {
    'running': False,
    'balance': 10000.0,
    'initial_balance': 10000.0,
    'total_trades': 0,
    'wins': 0,
    'losses': 0,
    'win_streak': 0,
    'current_asset': '-',
    'mode': 'DEMO',
    'trades': [],
    'logs': []
}

settings = {'fast_ema': 9, 'slow_ema': 21, 'min_confidence': 4}

def add_log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    bot_state['logs'].append(f"[{ts}] {msg}")
    if len(bot_state['logs']) > 100:
        bot_state['logs'] = bot_state['logs'][-100:]

def simulate_trading():
    assets = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'BTC/USD', 'ETH/USD', 'Gold', 'Oil']
    while bot_state['running']:
        try:
            time.sleep(random.randint(10, 30))
            if not bot_state['running']: break
            asset = random.choice(assets)
            action = random.choice(['CALL', 'PUT'])
            bot_state['current_asset'] = asset
            add_log(f"📊 Analyzing {asset}...")
            time.sleep(2)
            confidence = random.randint(1, 10)
            if confidence < settings['min_confidence']:
                add_log(f"⚠️ Low confidence ({confidence}/10) - Skipping")
                continue
            add_log(f"✅ Confidence {confidence}/10 - {action} on {asset}")
            win = random.random() < 0.6
            stake = 50.0
            profit = stake * 0.8 if win else -stake
            bot_state['total_trades'] += 1
            if win:
                bot_state['wins'] += 1
                bot_state['win_streak'] += 1
                bot_state['balance'] += profit
                result = 'WIN'
                add_log(f"🎉 WON! +${profit:.2f}")
            else:
                bot_state['losses'] += 1
                bot_state['win_streak'] = 0
                bot_state['balance'] += profit
                result = 'LOSS'
                add_log(f"❌ LOST ${abs(profit):.2f}")
            bot_state['trades'].insert(0, {
                'asset': asset, 'action': action, 'result': result,
                'profit': profit, 'time': datetime.now().strftime('%H:%M:%S')
            })
            if len(bot_state['trades']) > 20:
                bot_state['trades'] = bot_state['trades'][:20]
            wr = (bot_state['wins']/bot_state['total_trades']*100) if bot_state['total_trades'] > 0 else 0
            add_log(f"📊 Balance: ${bot_state['balance']:.2f} | Win Rate: {wr:.1f}%")
        except Exception as e:
            add_log(f"❌ Error: {e}")
            time.sleep(5)
    add_log("⏹️ Trading stopped")
    bot_state['current_asset'] = '-'

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except:
        return '''<html><head><title>Trading Bot</title><style>
        body{background:#000;color:#0ff;font-family:monospace;text-align:center;padding:50px}
        h1{font-size:3em;text-shadow:0 0 20px #0ff;animation:glow 2s infinite}
        @keyframes glow{0%,100%{text-shadow:0 0 20px #0ff}50%{text-shadow:0 0 40px #0ff}}
        .box{margin:30px;padding:20px;border:2px solid #0ff;border-radius:10px}
        </style></head><body>
        <h1>⚡ TRADING BOT ACTIVE ⚡</h1>
        <div class="box"><p>✅ Server Running on Port 5000</p>
        <p>📊 Bot Ready</p><p>🌐 Web Interface Loaded</p></div>
        <p style="color:#0cc">RUN button is working! Server is active!</p>
        </body></html>'''

@app.route('/api/status')
def get_status():
    return jsonify({
        'running': bot_state['running'], 'balance': bot_state['balance'],
        'initial_balance': bot_state['initial_balance'],
        'profit_loss': bot_state['balance'] - bot_state['initial_balance'],
        'total_trades': bot_state['total_trades'], 'wins': bot_state['wins'],
        'losses': bot_state['losses'],
        'win_rate': (bot_state['wins']/bot_state['total_trades']*100) if bot_state['total_trades']>0 else 0,
        'win_streak': bot_state['win_streak'], 'current_asset': bot_state['current_asset'],
        'mode': bot_state['mode'], 'trades': bot_state['trades']
    })

@app.route('/api/start', methods=['POST'])
def start_bot():
    if bot_state['running']:
        return jsonify({'success': False, 'error': 'Already running'})
    try:
        data = request.json or {}
        settings['fast_ema'] = data.get('fast_ema', 9)
        settings['slow_ema'] = data.get('slow_ema', 21)
        settings['min_confidence'] = data.get('min_confidence', 4)
        bot_state['running'] = True
        add_log("🚀 Bot starting...")
        add_log(f"⚙️ Settings: EMA {settings['fast_ema']}/{settings['slow_ema']}, Confidence {settings['min_confidence']}")
        threading.Thread(target=simulate_trading, daemon=True).start()
        add_log("✅ Bot started!")
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    bot_state['running'] = False
    add_log("⏹️ Stopping...")
    return jsonify({'success': True})

@app.route('/api/logs')
def stream_logs():
    def generate():
        last = 0
        while True:
            curr = len(bot_state['logs'])
            if curr > last:
                for log in bot_state['logs'][last:]:
                    yield f"data: {json.dumps({'log': log})}\n\n"
                last = curr
            time.sleep(0.5)
    return Response(generate(), mimetype='text/event-stream')

# Initialize
add_log("🎯 System initialized")
add_log("⏸️ Stopped - Press START to begin")

print("✅ Flask routes configured")
print("\n")
print("=" * 80)
print("🚀 STARTING FLASK WEB SERVER ON PORT 5000...")
print("=" * 80)
print("\n")
print("🌐 ONCE SERVER STARTS:")
print("   • A webview panel should appear on the right side")
print("   • OR look for 'Open in new tab' button")
print("   • OR click the https:// URL that will appear below")
print("\n")
print("=" * 80)
print("\n")

sys.stdout.flush()

# START THE SERVER
if __name__ == '__main__':
    print("🔥 LAUNCHING SERVER NOW...")
    sys.stdout.flush()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

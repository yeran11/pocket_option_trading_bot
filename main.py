#!/usr/bin/env python3
"""
POCKET OPTION TRADING BOT - LIVE VERSION
Real trading with beautiful web interface
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
import asyncio
import base64
import json
import operator
import platform
import random
from datetime import datetime, timedelta
from threading import Thread

# More immediate output
print("✅ Python is running")
print("✅ Working directory:", os.getcwd())
print("\n")

# Install required packages if needed
try:
    from flask import Flask, render_template, jsonify, request, Response
    print("✅ Flask is ready")
except ImportError:
    print("📦 Installing Flask...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask', '-q'])
    from flask import Flask, render_template, jsonify, request, Response
    print("✅ Flask installed successfully")

try:
    import undetected_chromedriver as uc
    from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
    from selenium.webdriver.common.by import By
    print("✅ Selenium and Chrome driver ready")
except ImportError:
    print("📦 Installing Selenium and undetected-chromedriver...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'selenium', 'undetected-chromedriver', '-q'])
    import undetected_chromedriver as uc
    from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
    from selenium.webdriver.common.by import By
    print("✅ Selenium installed successfully")

print("\n")

import time

print("✅ Creating Flask application...")

app = Flask(__name__)

# Import AI Trading System
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ai_config import AITradingBrain, SelfOptimizer, INDICATOR_CONFIG, AI_STRATEGIES
    print("✅ AI Trading System loaded")
    AI_ENABLED = True
    ai_brain = AITradingBrain()
    optimizer = SelfOptimizer()
except Exception as e:
    print(f"⚠️ AI System not available: {e}")
    AI_ENABLED = False
    ai_brain = None
    optimizer = None

# Global variables
DRIVER = None
CANDLES = {}
ACTIONS = {}
CURRENT_ASSET = None
FAVORITES_REANIMATED = False
PERIOD = 1
TRADING_ALLOWED = True
INITIAL_DEPOSIT = None
LAST_TRADE_ID = None
BOT_TRADE_IDS = set()  # Track trades placed by this bot

# Bot state
bot_state = {
    'running': False,
    'balance': 0.0,
    'initial_balance': 0.0,
    'total_trades': 0,
    'wins': 0,
    'losses': 0,
    'win_streak': 0,
    'current_asset': '-',
    'mode': 'CONNECTING...',
    'trades': [],
    'logs': []
}

settings = {
    # AI Settings
    'ai_enabled': AI_ENABLED,
    'ai_min_confidence': 70,
    'ai_strategy': 'ULTRA_SCALPING',

    # Moving Averages
    'fast_ema': 9,
    'slow_ema': 21,
    'ema_enabled': True,
    'ema_weight': 15,

    # RSI
    'rsi_enabled': True,
    'rsi_period': 14,
    'rsi_upper': 70,
    'rsi_lower': 30,
    'rsi_weight': 20,

    # Bollinger Bands
    'bb_enabled': True,
    'bb_period': 20,
    'bb_std': 2,
    'bb_weight': 15,

    # MACD
    'macd_enabled': True,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'macd_weight': 15,

    # Stochastic
    'stoch_enabled': True,
    'stoch_k': 14,
    'stoch_d': 3,
    'stoch_upper': 80,
    'stoch_lower': 20,
    'stoch_weight': 10,

    # ATR (Volatility)
    'atr_enabled': True,
    'atr_period': 14,
    'atr_weight': 10,

    # Volume Analysis
    'volume_enabled': True,
    'volume_ma': 20,
    'volume_surge': 1.5,
    'volume_weight': 15,

    # Trading Settings
    'min_confidence': 4,
    'min_payout': 85,
    'max_trades_per_hour': 20,
    'risk_per_trade': 1.0,

    # Strategy Selection
    'active_strategy': 'AI_ENHANCED',  # AI_ENHANCED, TRADITIONAL, SCALPING, TREND_FOLLOW, REVERSAL

    # Risk Management
    'take_profit': 100,
    'stop_loss': 50,
    'trailing_stop': False,
    'max_consecutive_losses': 5
}

ops = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
}

POCKET_OPTION_URL = 'https://pocket2.click/cabinet/demo-quick-high-low?utm_campaign=806509&utm_source=affiliate&utm_medium=sr&a=ovlztqbPkiBiOt&ac=github'

def add_log(msg):
    """Add log message with timestamp"""
    ts = datetime.now().strftime('%H:%M:%S')
    bot_state['logs'].append(f"[{ts}] {msg}")
    if len(bot_state['logs']) > 100:
        bot_state['logs'] = bot_state['logs'][-100:]
    print(f"[{ts}] {msg}")


# ==================== CHROME DRIVER MANAGEMENT ====================

def get_chrome_version():
    """Get installed Chrome version"""
    import subprocess
    import re

    try:
        os_platform = platform.platform().lower()

        if 'windows' in os_platform:
            # Windows: Check registry or chrome.exe version
            paths = [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            ]
            for path in paths:
                if os.path.exists(path):
                    result = subprocess.run(['powershell', '-Command',
                        f"(Get-Item '{path}').VersionInfo.ProductVersion"],
                        capture_output=True, text=True)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        match = re.search(r'(\d+)', version)
                        if match:
                            return int(match.group(1))

        elif 'macos' in os_platform:
            # macOS
            result = subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                capture_output=True, text=True)
            if result.returncode == 0:
                match = re.search(r'(\d+)', result.stdout)
                if match:
                    return int(match.group(1))

        elif 'linux' in os_platform:
            # Linux
            for cmd in ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']:
                try:
                    result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        match = re.search(r'(\d+)', result.stdout)
                        if match:
                            return int(match.group(1))
                except FileNotFoundError:
                    continue
    except:
        pass

    return None


async def get_driver():
    """Initialize Chrome driver with undetected settings"""
    options = uc.ChromeOptions()
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--disable-blink-features=AutomationControlled')

    username = os.environ.get('USER', os.environ.get('USERNAME', 'runner'))
    os_platform = platform.platform().lower()

    if 'macos' in os_platform:
        path_default = fr'/Users/{username}/Library/Application Support/Google/Chrome/PO Bot Live'
    elif 'windows' in os_platform:
        path_default = fr'C:\Users\{username}\AppData\Local\Google\Chrome\User Data\PO Bot Live'
    elif 'linux' in os_platform:
        path_default = f'/home/{username}/.config/google-chrome/PO Bot Live'
    else:
        path_default = ''

    if path_default:
        options.add_argument(fr'--user-data-dir={path_default}')

    # Get Chrome version and use matching driver
    chrome_version = get_chrome_version()
    if chrome_version:
        add_log(f"Detected Chrome version: {chrome_version}")
        driver = uc.Chrome(options=options, version_main=chrome_version, use_subprocess=True)
    else:
        add_log("Chrome version auto-detection failed, using default")
        driver = uc.Chrome(options=options, use_subprocess=True)

    return driver


# ==================== TECHNICAL INDICATORS ====================

async def calculate_ema(candles, period):
    """Exponential Moving Average"""
    if len(candles) < period:
        return None

    closes = [c[2] for c in candles]
    multiplier = 2 / (period + 1)
    sma = sum(closes[:period]) / period
    ema = sma

    for price in closes[period:]:
        ema = (price - ema) * multiplier + ema

    return ema


async def calculate_rsi(candles, period=14):
    """Relative Strength Index"""
    if len(candles) < period + 1:
        return None

    closes = [c[2] for c in candles]
    gains = []
    losses = []

    for i in range(1, period + 1):
        delta = closes[i] - closes[i - 1]
        if delta > 0:
            gains.append(delta)
        else:
            losses.append(abs(delta))

    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


async def calculate_bollinger_bands(candles, period=20, std_dev=2):
    """Bollinger Bands (Upper, Middle, Lower)"""
    if len(candles) < period:
        return None, None, None

    closes = [c[2] for c in candles[-period:]]
    sma = sum(closes) / period

    variance = sum((x - sma) ** 2 for x in closes) / period
    std = variance ** 0.5

    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)

    return upper, sma, lower


async def calculate_atr(candles, period=14):
    """Average True Range (Volatility)"""
    if len(candles) < period + 1:
        return None

    true_ranges = []
    for i in range(-period, 0):
        high = candles[i][3]
        low = candles[i][4]
        prev_close = candles[i-1][2]

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        true_ranges.append(tr)

    return sum(true_ranges) / period


async def detect_support_resistance(candles, lookback=20):
    """Detect support and resistance levels"""
    if len(candles) < lookback:
        return None, None

    recent = candles[-lookback:]
    highs = [c[3] for c in recent]
    lows = [c[4] for c in recent]

    resistance = max(highs)
    support = min(lows)

    return support, resistance


# ==================== TRADING STRATEGY ====================

async def enhanced_strategy(candles):
    """
    Advanced AI-enhanced strategy with multiple indicators
    """
    if len(candles) < 50:
        return None

    current_price = candles[-1][2]

    # If AI is enabled, use it for analysis
    if AI_ENABLED and ai_brain:
        try:
            # Prepare market data for AI
            market_data = {
                'asset': CURRENT_ASSET or 'Unknown',
                'current_price': current_price,
                'change_1m': ((candles[-1][2] - candles[-2][2]) / candles[-2][2]) * 100 if len(candles) > 1 else 0,
                'change_5m': ((candles[-1][2] - candles[-5][2]) / candles[-5][2]) * 100 if len(candles) > 5 else 0,
                'volume': 'Normal',  # Would need real volume data
                'volatility': 'Medium',
                'recent_trades': f"{bot_state['wins']}/{bot_state['total_trades']}",
                'win_rate': (bot_state['wins'] / bot_state['total_trades'] * 100) if bot_state['total_trades'] > 0 else 0
            }

            # Calculate indicators for AI
            rsi = await calculate_rsi(candles, settings.get('rsi_period', 14))
            ema_fast = await calculate_ema(candles, settings.get('fast_ema', 9))
            ema_slow = await calculate_ema(candles, settings.get('slow_ema', 21))
            upper_bb, middle_bb, lower_bb = await calculate_bollinger_bands(candles, 20, 2)

            ai_indicators = {
                'rsi': rsi or 50,
                'ema_cross': 'Bullish' if ema_fast and ema_slow and ema_fast > ema_slow else 'Bearish',
                'bollinger_position': 'Above' if upper_bb and current_price > upper_bb else 'Below' if lower_bb and current_price < lower_bb else 'Middle',
                'macd_signal': 'Neutral',  # Would need MACD calculation
                'stochastic': 50,  # Would need stochastic calculation
                'volume_trend': 'Normal'
            }

            # Get AI decision
            ai_action, ai_confidence, ai_reason = await ai_brain.analyze_with_gpt4(market_data, ai_indicators)

            # If AI has high confidence, use its decision
            if ai_confidence >= settings.get('ai_min_confidence', 70):
                add_log(f"🤖 AI Decision: {ai_action.upper()} - {ai_reason} ({ai_confidence}%)")
                if ai_action != 'hold':
                    return ai_action, f'AI: {ai_reason} ({ai_confidence}%)'
        except Exception as e:
            add_log(f"⚠️ AI analysis failed: {e}, using traditional indicators")

    # Traditional indicator analysis (fallback or when AI is disabled)
    # Calculate all indicators
    ema_fast = await calculate_ema(candles, settings['fast_ema'])
    ema_slow = await calculate_ema(candles, settings['slow_ema'])
    ema_fast_prev = await calculate_ema(candles[:-1], settings['fast_ema'])
    ema_slow_prev = await calculate_ema(candles[:-1], settings['slow_ema'])

    rsi = await calculate_rsi(candles, settings['rsi_period'])
    upper_bb, middle_bb, lower_bb = await calculate_bollinger_bands(candles, 20, 2)
    atr = await calculate_atr(candles)
    support, resistance = await detect_support_resistance(candles)

    if None in [ema_fast, ema_slow, rsi, upper_bb, lower_bb]:
        return None

    # Signal counters
    call_signals = 0
    put_signals = 0

    # 1. Moving Average Crossover
    if ema_fast_prev < ema_slow_prev and ema_fast > ema_slow:
        call_signals += 3  # Strong signal
    elif ema_fast_prev > ema_slow_prev and ema_fast < ema_slow:
        put_signals += 3

    # 2. RSI Analysis
    if settings['rsi_enabled']:
        rsi_upper = settings['rsi_upper']
        rsi_lower = 100 - rsi_upper

        if rsi < rsi_lower:  # Oversold -> potential call
            call_signals += 2
        elif rsi > rsi_upper:  # Overbought -> potential put
            put_signals += 2

        # Extreme levels
        if rsi < 30:
            call_signals += 1
        elif rsi > 70:
            put_signals += 1

    # 3. Bollinger Bands
    if current_price <= lower_bb:  # Price at lower band -> potential bounce up
        call_signals += 2
    elif current_price >= upper_bb:  # Price at upper band -> potential bounce down
        put_signals += 2

    # 4. Price vs Middle BB
    if current_price < middle_bb and ema_fast > ema_slow:
        call_signals += 1
    elif current_price > middle_bb and ema_fast < ema_slow:
        put_signals += 1

    # 5. Support/Resistance
    if support and resistance:
        price_range = resistance - support
        if current_price < support + (price_range * 0.2):  # Near support
            call_signals += 1
        elif current_price > resistance - (price_range * 0.2):  # Near resistance
            put_signals += 1

    # 6. Volatility Filter (ATR)
    if atr:
        avg_price = sum([c[2] for c in candles[-20:]]) / 20
        volatility_percent = (atr / avg_price) * 100

        # Skip trading in extremely volatile conditions
        if volatility_percent > 5:  # Too volatile
            add_log(f"⚠️ High volatility: {volatility_percent:.2f}% - Skipping")
            return None

    # 7. Trend Strength
    if ema_fast > ema_slow:
        trend_strength = ((ema_fast - ema_slow) / ema_slow) * 100
        if trend_strength > 0.5:
            call_signals += 1
    else:
        trend_strength = ((ema_slow - ema_fast) / ema_fast) * 100
        if trend_strength > 0.5:
            put_signals += 1

    # Decision Logic
    signal_diff = abs(call_signals - put_signals)
    min_confidence = settings['min_confidence']

    if call_signals > put_signals and signal_diff >= min_confidence:
        confidence = (call_signals / (call_signals + put_signals)) * 100
        return 'call', f'Confidence: {confidence:.1f}% ({call_signals} signals)'
    elif put_signals > call_signals and signal_diff >= min_confidence:
        confidence = (put_signals / (call_signals + put_signals)) * 100
        return 'put', f'Confidence: {confidence:.1f}% ({put_signals} signals)'

    return None


# ==================== POCKET OPTION INTEGRATION ====================

async def websocket_log(driver):
    """Process WebSocket data and update candles"""
    global CANDLES, PERIOD, CURRENT_ASSET, FAVORITES_REANIMATED

    for wsData in driver.get_log('performance'):
        message = json.loads(wsData['message'])['message']
        response = message.get('params', {}).get('response', {})
        if response.get('opcode', 0) == 2:
            payload_str = base64.b64decode(response['payloadData']).decode('utf-8')
            data = json.loads(payload_str)

            if 'history' in data:
                if not CURRENT_ASSET:
                    CURRENT_ASSET = data['asset']
                if PERIOD != data['period']:
                    PERIOD = data['period']
                    CANDLES = {}
                    FAVORITES_REANIMATED = False

                candles = list(reversed(data['candles']))
                for tstamp, value in data['history']:
                    tstamp = int(float(tstamp))
                    candle = [tstamp, value, value, value, value]
                    candle[2] = value  # close
                    if value > candle[3]:  # high
                        candle[3] = value
                    if value < candle[4]:  # low
                        candle[4] = value
                    if tstamp % PERIOD == 0:
                        if tstamp not in [c[0] for c in candles]:
                            candles.append([tstamp, value, value, value, value])
                CANDLES[data['asset']] = candles

            try:
                asset = data[0][0]
                candles = CANDLES[asset]
                current_value = data[0][2]
                candles[-1][2] = current_value  # close
                if current_value > candles[-1][3]:  # high
                    candles[-1][3] = current_value
                if current_value < candles[-1][4]:  # low
                    candles[-1][4] = current_value
                tstamp = int(float(data[0][1]))
                if tstamp % PERIOD == 0:
                    if tstamp not in [c[0] for c in candles]:
                        candles.append([tstamp, current_value, current_value, current_value, current_value])
            except:
                pass

    if not FAVORITES_REANIMATED:
        try:
            await reanimate_favorites(driver)
        except:
            pass


async def reanimate_favorites(driver):
    """Activate all favorite assets"""
    global CURRENT_ASSET, FAVORITES_REANIMATED

    asset_favorites_items = driver.find_elements(By.CLASS_NAME, 'assets-favorites-item')
    out_of_reach = []

    for item in asset_favorites_items:
        while True:
            if 'assets-favorites-item--active' in item.get_attribute('class'):
                CURRENT_ASSET = item.get_attribute('data-id')
                break
            if 'assets-favorites-item--not-active' in item.get_attribute('class'):
                break
            try:
                item.click()
                FAVORITES_REANIMATED = True
            except ElementNotInteractableException:
                out_of_reach.append(item.get_attribute('data-id'))
                break

    # Log all out of reach assets in one message
    if out_of_reach and len(out_of_reach) <= 5:
        add_log(f"⚠️ {len(out_of_reach)} assets not visible: {', '.join(out_of_reach[:5])}")
    elif out_of_reach:
        add_log(f"⚠️ {len(out_of_reach)} assets not visible (scroll down to activate them)")


async def switch_to_asset(driver, asset):
    """Switch to specific asset"""
    global CURRENT_ASSET

    asset_favorites_items = driver.find_elements(By.CLASS_NAME, 'assets-favorites-item')
    for item in asset_favorites_items:
        if item.get_attribute('data-id') != asset:
            continue
        while True:
            await asyncio.sleep(0.1)
            if 'assets-favorites-item--active' in item.get_attribute('class'):
                CURRENT_ASSET = asset
                return True
            try:
                item.click()
            except:
                add_log(f'Asset {asset} out of reach')
                return False

    if asset == CURRENT_ASSET:
        return True


async def check_payout(driver, asset):
    """Check if payout meets minimum requirement"""
    global ACTIONS

    try:
        payout = driver.find_element(By.CLASS_NAME, 'value__val-start').text
        if int(payout[1:-1]) >= settings['min_payout']:
            return True
        add_log(f'⚠️ Payout {payout[1:]} too low for {asset}')
        ACTIONS[asset] = datetime.now() + timedelta(minutes=1)
        return False
    except:
        return True


async def create_order(driver, action, asset, reason=""):
    """Create trading order"""
    global ACTIONS, BOT_TRADE_IDS

    if ACTIONS.get(asset) and ACTIONS[asset] + timedelta(seconds=PERIOD * 2) > datetime.now():
        return False

    try:
        switch = await switch_to_asset(driver, asset)
        if not switch:
            return False

        ok_payout = await check_payout(driver, asset)
        if not ok_payout:
            return False

        driver.find_element(by=By.CLASS_NAME, value=f'btn-{action}').click()
        ACTIONS[asset] = datetime.now()
        bot_state['total_trades'] += 1
        bot_state['current_asset'] = asset

        # Create unique trade ID for this bot's trade
        trade_id = f"{asset}_{action}_{datetime.now().strftime('%H:%M:%S')}"
        BOT_TRADE_IDS.add(trade_id)

        add_log(f"{'📈' if action == 'call' else '📉'} {action.upper()} on {asset} - {reason}")
        return True
    except Exception as e:
        add_log(f"❌ Can't create order: {e}")
        return False


async def check_deposit(driver):
    """Monitor deposit and update balance"""
    global INITIAL_DEPOSIT, bot_state

    try:
        deposit_elem = driver.find_element(By.CSS_SELECTOR,
            'body > div.wrapper > div.wrapper__top > header > div.right-block.js-right-block > div.right-block__item.js-drop-down-modal-open > div > div.balance-info-block__data > div.balance-info-block__balance > span')
        deposit = float(deposit_elem.text.replace(',', ''))

        if INITIAL_DEPOSIT is None:
            INITIAL_DEPOSIT = deposit
            bot_state['initial_balance'] = deposit
            bot_state['balance'] = deposit
        else:
            bot_state['balance'] = deposit
    except:
        pass


async def check_recent_trades(driver):
    """Check recent trades for wins/losses - ONLY count bot's trades"""
    global bot_state, LAST_TRADE_ID, BOT_TRADE_IDS

    try:
        # Try to open closed trades tab first
        try:
            closed_tab = driver.find_element(By.CSS_SELECTOR,
                '#bar-chart > div > div > div.right-widget-container > div > div.widget-slot__header > div.divider > ul > li:nth-child(2) > a')
            closed_tab_parent = closed_tab.find_element(By.XPATH, '..')
            if closed_tab_parent.get_attribute('class') == '':
                closed_tab_parent.click()
                await asyncio.sleep(0.3)
        except:
            pass

        closed_trades = driver.find_elements(By.CLASS_NAME, 'deals-list__item')
        if closed_trades and len(closed_trades) > 0:
            # Use the full text as a unique ID
            current_trade_id = closed_trades[0].text

            # Skip if this is the same trade we already processed
            if current_trade_id == LAST_TRADE_ID:
                return

            LAST_TRADE_ID = current_trade_id
            last_split = current_trade_id.split('\n')

            # Parse trade result - need at least time, asset, direction, stake, profit
            if len(last_split) >= 5:
                asset = last_split[1] if len(last_split) > 1 else 'Unknown'
                action = last_split[2].upper() if len(last_split) > 2 else 'Unknown'
                trade_time = last_split[0] if last_split[0] else datetime.now().strftime('%H:%M:%S')

                # Check if this trade matches any of our bot's trades
                # Match by asset and action only (time might be slightly different)
                is_bot_trade = False
                matching_id = None
                for bot_trade_id in list(BOT_TRADE_IDS):
                    if bot_trade_id.startswith(f"{asset}_{action.lower()}_"):
                        is_bot_trade = True
                        matching_id = bot_trade_id
                        break

                # ONLY count if this is one of our bot's trades
                if not is_bot_trade:
                    # Not our trade - skip it silently
                    return

                # This is our trade - process it
                if matching_id:
                    BOT_TRADE_IDS.discard(matching_id)  # Remove from pending

                # Check if win, draw, or loss
                if '$0' != last_split[4] and '$\u202f0' != last_split[4]:  # WIN
                    profit_str = last_split[4].replace('$', '').replace(',', '').replace('\u202f', '')
                    try:
                        profit = float(profit_str)

                        bot_state['wins'] += 1
                        bot_state['win_streak'] += 1

                        bot_state['trades'].insert(0, {
                            'asset': asset,
                            'action': action,
                            'result': 'WIN',
                            'profit': profit,
                            'time': trade_time
                        })

                        # AI Learning: Track winning pattern
                        if ai_brain and optimizer:
                            try:
                                trade_data = {
                                    'asset': asset,
                                    'action': action.lower(),
                                    'result': 'WIN',
                                    'profit': profit
                                }
                                ai_brain.learn_from_trade(trade_data)

                                # Update strategy performance
                                current_strategy = settings.get('active_strategy', 'TRADITIONAL')
                                if current_strategy in optimizer.strategy_performance:
                                    optimizer.strategy_performance[current_strategy]['wins'] += 1
                                    optimizer.strategy_performance[current_strategy]['trades'] += 1
                            except:
                                pass

                        if len(bot_state['trades']) > 20:
                            bot_state['trades'] = bot_state['trades'][:20]

                        # Use bot_state['total_trades'] which only counts bot trades
                        win_rate = (bot_state['wins'] / bot_state['total_trades'] * 100) if bot_state['total_trades'] > 0 else 0
                        add_log(f"🎉 WIN! +${profit:.2f} | Win Rate: {win_rate:.1f}% ({bot_state['wins']}/{bot_state['total_trades']})")
                    except Exception as e:
                        pass

                elif '$0' == last_split[3] or '$\u202f0' == last_split[3]:  # LOSS
                    stake_str = last_split[3].replace('$', '').replace(',', '').replace('\u202f', '')
                    try:
                        stake = float(stake_str) if stake_str != '0' else 0

                        if stake > 0:
                            bot_state['losses'] += 1
                            bot_state['win_streak'] = 0

                            bot_state['trades'].insert(0, {
                                'asset': asset,
                                'action': action,
                                'result': 'LOSS',
                                'profit': -stake,
                                'time': trade_time
                            })

                            # AI Learning: Track losing pattern
                            if ai_brain and optimizer:
                                try:
                                    trade_data = {
                                        'asset': asset,
                                        'action': action.lower(),
                                        'result': 'LOSS',
                                        'profit': -stake
                                    }
                                    ai_brain.learn_from_trade(trade_data)

                                    # Update strategy performance
                                    current_strategy = settings.get('active_strategy', 'TRADITIONAL')
                                    if current_strategy in optimizer.strategy_performance:
                                        optimizer.strategy_performance[current_strategy]['trades'] += 1
                                except:
                                    pass

                            if len(bot_state['trades']) > 20:
                                bot_state['trades'] = bot_state['trades'][:20]

                            # Use bot_state['total_trades'] which only counts bot trades
                            win_rate = (bot_state['wins'] / bot_state['total_trades'] * 100) if bot_state['total_trades'] > 0 else 0
                            add_log(f"❌ LOSS -${stake:.2f} | Win Rate: {win_rate:.1f}% ({bot_state['wins']}/{bot_state['total_trades']})")
                    except Exception as e:
                        pass
    except:
        pass


async def detect_account_mode(driver):
    """Detect if using DEMO or REAL account"""
    try:
        balance_elem = driver.find_element(By.CSS_SELECTOR,
            'body > div.wrapper > div.wrapper__top > header > div.right-block.js-right-block > div.right-block__item.js-drop-down-modal-open')
        balance_text = balance_elem.text.upper()

        if 'DEMO' in balance_text:
            bot_state['mode'] = 'DEMO'
            add_log("⚠️ Using DEMO account")
        elif 'REAL' in balance_text:
            bot_state['mode'] = 'LIVE'
            add_log("✅ Using REAL LIVE account")
        else:
            bot_state['mode'] = 'LIVE'
            add_log("✅ Connected to account")

        return True
    except:
        return False


async def wait_for_login(driver):
    """Wait for user to login manually"""
    add_log("=" * 40)
    add_log("👉 WAITING FOR YOU TO LOGIN")
    add_log("=" * 40)
    add_log("")
    add_log("A Chrome window has opened")
    add_log("Please LOGIN to your Pocket Option account")
    add_log("Choose DEMO or REAL account (top-right)")
    add_log("Add 2-5 FAVORITE assets (star icon)")
    add_log("Bot will detect login automatically...")
    add_log("")

    max_wait = 300  # 5 minutes
    waited = 0

    while waited < max_wait:
        try:
            # Check if logged in
            balance = driver.find_element(By.CSS_SELECTOR,
                'body > div.wrapper > div.wrapper__top > header > div.right-block.js-right-block > div.right-block__item.js-drop-down-modal-open')

            add_log("=" * 40)
            add_log("✅ LOGIN DETECTED!")
            add_log("=" * 40)
            await asyncio.sleep(2)
            await detect_account_mode(driver)
            return True
        except:
            await asyncio.sleep(2)
            waited += 2

            if waited % 15 == 0:
                add_log(f"⏳ Still waiting for login... ({waited}s)")

    add_log("❌ Login timeout (5 minutes)")
    return False


async def check_indicators(driver):
    """Main trading logic loop"""
    global CANDLES

    # Check if we have any candle data
    if not CANDLES:
        return

    # Check each asset
    for asset, candles in CANDLES.items():
        if len(candles) < 50:
            # Log when we're still collecting data
            if len(candles) > 0 and len(candles) % 10 == 0:
                add_log(f"📊 {asset}: Collecting data ({len(candles)}/50 candles)")
            continue

        result = await enhanced_strategy(candles)

        if not result:
            continue

        action, reason = result
        order_created = await create_order(driver, action, asset, reason)

        if order_created:
            await asyncio.sleep(1)
            return


async def trading_loop():
    """Main trading loop - runs in background"""
    global DRIVER, TRADING_ALLOWED, bot_state

    try:
        add_log("🚀 Initializing Chrome driver...")
        DRIVER = await get_driver()

        add_log("🌐 Opening Pocket Option...")
        DRIVER.get(POCKET_OPTION_URL)
        await asyncio.sleep(3)

        # Wait for login
        login_success = await wait_for_login(DRIVER)

        if not login_success:
            add_log("❌ Login timeout - please restart bot")
            bot_state['running'] = False
            return

        add_log("=" * 40)
        add_log("🤖 BOT STARTED - LIVE TRADING")
        add_log("=" * 40)
        add_log("Analyzing markets...")
        add_log("")

        # Main loop
        while bot_state['running'] and TRADING_ALLOWED:
            try:
                await websocket_log(DRIVER)
                await check_indicators(DRIVER)
                await check_deposit(DRIVER)
                await check_recent_trades(DRIVER)
                await asyncio.sleep(0.5)
            except Exception as e:
                add_log(f"⚠️ Error in loop: {e}")
                await asyncio.sleep(2)

        add_log("⏹️ Trading stopped")

    except Exception as e:
        add_log(f"❌ Error: {e}")
        bot_state['running'] = False
    finally:
        if DRIVER:
            try:
                DRIVER.quit()
            except:
                pass


def start_trading_thread():
    """Start trading in a new thread"""
    def run_async_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(trading_loop())
        loop.close()

    thread = Thread(target=run_async_loop, daemon=True)
    thread.start()


# ==================== FLASK ROUTES ====================

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


@app.route('/settings')
def settings_page():
    try:
        return render_template('settings.html')
    except:
        return '<html><body><h1>Settings Page</h1><p>Error loading template</p></body></html>'


@app.route('/api/status')
def get_status():
    return jsonify({
        'running': bot_state['running'],
        'balance': bot_state['balance'],
        'initial_balance': bot_state['initial_balance'],
        'profit_loss': bot_state['balance'] - bot_state['initial_balance'],
        'total_trades': bot_state['total_trades'],
        'wins': bot_state['wins'],
        'losses': bot_state['losses'],
        'win_rate': (bot_state['wins'] / bot_state['total_trades'] * 100) if bot_state['total_trades'] > 0 else 0,
        'win_streak': bot_state['win_streak'],
        'current_asset': bot_state['current_asset'],
        'mode': bot_state['mode'],
        'trades': bot_state['trades']
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
        bot_state['mode'] = 'CONNECTING...'
        add_log("🚀 Bot starting...")
        add_log(f"⚙️ Settings: EMA {settings['fast_ema']}/{settings['slow_ema']}, Confidence {settings['min_confidence']}")

        start_trading_thread()

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


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current bot settings"""
    return jsonify(settings)


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update bot settings"""
    global settings, AI_ENABLED
    try:
        new_settings = request.json
        settings.update(new_settings)

        # Update AI status if changed
        if 'ai_enabled' in new_settings:
            AI_ENABLED = new_settings['ai_enabled']

        add_log(f"⚙️ Settings updated successfully")
        return jsonify({'success': True, 'message': 'Settings updated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/ai-status', methods=['GET'])
def get_ai_status():
    """Get AI system status"""
    return jsonify({
        'ai_enabled': AI_ENABLED,
        'ai_available': ai_brain is not None,
        'patterns_learned': len(ai_brain.pattern_database) if ai_brain else 0,
        'current_strategy': settings.get('ai_strategy', 'ULTRA_SCALPING')
    })


@app.route('/api/indicator-performance', methods=['GET'])
def get_indicator_performance():
    """Get performance metrics for each indicator"""
    if optimizer:
        return jsonify(optimizer.indicator_performance)
    return jsonify({})


@app.route('/api/strategy-stats', methods=['GET'])
def get_strategy_stats():
    """Get strategy performance statistics"""
    if optimizer:
        return jsonify(optimizer.strategy_performance)
    return jsonify({})


# Initialize
add_log("🎯 System initialized - REAL TRADING MODE")
add_log("⏸️ Stopped - Press START to begin")
add_log("⚠️ Make sure you login and set up favorites!")

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

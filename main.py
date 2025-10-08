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
from dotenv import load_dotenv
# Load .env from multiple possible locations
load_dotenv()  # Current directory
load_dotenv('../.env')  # Parent directory
# Now environment variables are available
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
AI_ENABLED = False
ai_brain = None
optimizer = None
INDICATOR_CONFIG = None
AI_STRATEGIES = None

# Import NEW ULTRA MASTER SYSTEMS
try:
    from performance_tracker import get_tracker
    from market_regime import get_detector
    from multi_timeframe import get_analyzer
    from strategy_builder import get_builder
    from backtesting_engine import get_backtest_engine
    from trade_journal import get_journal
    from pattern_recognition import get_recognizer
    from otc_anomaly_strategy import create_otc_strategy
    from reversal_catcher import create_reversal_catcher
    ULTRA_SYSTEMS_AVAILABLE = True
    print("✅ ULTRA Master Systems loaded successfully!")
except ImportError as e:
    ULTRA_SYSTEMS_AVAILABLE = False
    print(f"⚠️ Some ULTRA systems not available: {e}")

# Initialize ULTRA systems
performance_tracker = None
regime_detector = None
mtf_analyzer = None
strategy_builder = None
backtest_engine = None
trade_journal = None
pattern_recognizer = None
otc_strategy = None
reversal_catcher = None

if ULTRA_SYSTEMS_AVAILABLE:
    try:
        performance_tracker = get_tracker()
        regime_detector = get_detector()
        mtf_analyzer = get_analyzer()
        strategy_builder = get_builder()
        backtest_engine = get_backtest_engine()
        trade_journal = get_journal()
        pattern_recognizer = get_recognizer()
        otc_strategy = create_otc_strategy()
        reversal_catcher = create_reversal_catcher(sensitivity='medium')
        print("✅ All ULTRA systems initialized! (Including 🕯️ Patterns + 🎰 OTC + 🔄 Reversal Catcher)")
    except Exception as e:
        print(f"⚠️ ULTRA systems init error: {e}")

def initialize_ai_system():
    """Initialize or reinitialize the AI trading system"""
    global AI_ENABLED, ai_brain, optimizer, INDICATOR_CONFIG, AI_STRATEGIES

    # Helper function for logging when add_log may not be available
    def safe_log(msg):
        print(msg)
        if 'add_log' in globals():
            add_log(msg)

    try:
        print("🔄 Starting AI system initialization...")

        # Ensure paths are set up - try multiple locations
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Try multiple paths for ai_config.py
        possible_paths = [
            os.path.join(current_dir, 'ai_config.py'),  # Same directory
            os.path.join(os.path.dirname(current_dir), 'ai_config.py'),  # Parent directory
            os.path.join('/home/runner/workspace', 'ai_config.py'),  # Absolute path
            os.path.join('/home/runner/workspace/pocket_option_trading_bot', 'ai_config.py'),  # Absolute bot path
        ]

        # Add all paths to sys.path
        for path_dir in [current_dir, os.path.dirname(current_dir), '/home/runner/workspace', '/home/runner/workspace/pocket_option_trading_bot']:
            if path_dir not in sys.path:
                sys.path.insert(0, path_dir)

        print(f"📂 Current dir: {current_dir}")
        print(f"📂 Looking for ai_config.py in multiple locations...")

        # Try to import the AI config module
        try:
            # Find the first existing ai_config.py
            ai_config_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    ai_config_path = path
                    break

            print(f"🔍 Checking for ai_config at paths: {possible_paths}")

            if not ai_config_path:
                print(f"❌ ai_config.py not found in any location")
                safe_log("❌ AI config file not found in any location")
                return False

            print(f"✅ Found ai_config.py at {ai_config_path}")

            # Import the module
            import importlib.util
            spec = importlib.util.spec_from_file_location("ai_config", ai_config_path)
            if spec is None:
                print("❌ Failed to create module spec")
                safe_log("❌ Failed to load AI module specification")
                return False

            ai_config = importlib.util.module_from_spec(spec)
            if ai_config is None:
                print("❌ Failed to create module from spec")
                safe_log("❌ Failed to create AI module")
                return False

            spec.loader.exec_module(ai_config)
            print("✅ Successfully imported ai_config module")

            # Get the classes and configs
            AITradingBrain = ai_config.AITradingBrain
            SelfOptimizer = ai_config.SelfOptimizer
            INDICATOR_CONFIG = ai_config.INDICATOR_CONFIG
            AI_STRATEGIES = ai_config.AI_STRATEGIES

            # Also get the API key from the module
            OPENAI_API_KEY = ai_config.OPENAI_API_KEY
            OPENAI_PROJECT_ID = ai_config.OPENAI_PROJECT_ID

            # Diagnostic: Check API key value
            if OPENAI_API_KEY:
                print(f"🔑 API Key loaded: {OPENAI_API_KEY[:15]}...{OPENAI_API_KEY[-8:]} (length: {len(OPENAI_API_KEY)})")
            else:
                print(f"⚠️ API Key is: {OPENAI_API_KEY}")

            print("✅ Successfully loaded AI classes and configs")

        except Exception as import_error:
            error_msg = str(import_error)
            print(f"❌ Failed to import ai_config: {error_msg}")
            safe_log(f"❌ AI module import error: {error_msg[:100]}")
            import traceback
            traceback.print_exc()
            return False

        # Check if API key is valid before initializing
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your-api-key-here" or len(OPENAI_API_KEY) < 20:
            print("❌ Invalid or missing OpenAI API key")
            safe_log("❌ AI initialization failed - Invalid API key")
            return False

        # Initialize the AI objects
        print("🔧 Creating AI brain and optimizer instances...")
        try:
            ai_brain = AITradingBrain()
            optimizer = SelfOptimizer()
            AI_ENABLED = True
            print("✅ AI Trading System loaded successfully")
            safe_log("✅ AI Trading System initialized successfully")
        except Exception as init_error:
            print(f"❌ Failed to initialize AI objects: {init_error}")
            safe_log(f"❌ AI initialization error: {str(init_error)[:100]}")
            return False

        if ai_brain:
            try:
                ai_brain.load_patterns()
                pattern_count = len(ai_brain.pattern_database) if hasattr(ai_brain, 'pattern_database') else 0
                print(f"📊 Loaded {pattern_count} patterns")
                safe_log(f"📊 AI loaded with {pattern_count} learned patterns")
            except Exception as pattern_error:
                print(f"📊 Starting with fresh pattern database: {pattern_error}")
                safe_log("📊 AI starting with fresh pattern database")

        return True

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Failed to initialize AI: {error_msg}")
        safe_log(f"❌ AI initialization failed: {error_msg[:100]}")
        import traceback
        traceback.print_exc()
        AI_ENABLED = False
        ai_brain = None
        optimizer = None
        return False

# AI initialization will happen after add_log is defined

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

# Trade frequency tracking
TRADE_HISTORY = []  # List of (timestamp, asset) tuples
LAST_TRADE_TIME = None
CONSECUTIVE_TRADES = 0
LAST_TRADE_RESULT = None  # 'WIN' or 'LOSS'
ACTIVE_STRATEGY_ID = None  # Track which custom strategy was used
ACTIVE_STRATEGY_NAME = None

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
    'logs': [],
    'chart_data': {
        'times': [],
        'balances': [],
        'trades': []
    },
    'pattern_data': {
        'pattern_type': None,
        'pattern_strength': 0,
        'pattern_quality': 0,
        'pattern_timeframe': '1m'
    }
}

settings = {
    # AI Settings
    'ai_enabled': True,  # Default to enabled
    'use_gpt4': True,  # Enable GPT-4
    'use_claude': True,  # Enable Claude
    'ai_mode': 'ensemble',  # ensemble, any, gpt4_only, claude_only
    'ai_min_confidence': 70,
    'ai_strategy': 'ULTRA_SCALPING',

    # 🎯 ULTRA DECISION MODE SYSTEM
    'decision_mode': 'full_power',  # full_power, ai_only, patterns_only, strategy_only, indicators_only
    'active_strategy_id': None,  # For "strategy_only" mode - which strategy to use exclusively

    # 🕯️ Pattern Recognition Control
    'pattern_recognition_enabled': True,  # Toggle pattern detection on/off

    # 📊 Custom Strategies Control
    'custom_strategies_enabled': True,  # Master toggle for all custom strategies

    # Legacy settings (kept for backward compatibility)
    'require_pattern': False,  # Require chart pattern confirmation
    'check_support_resistance': True,  # Check proximity to S/R levels
    'min_indicator_alignment': 5,  # Minimum indicators that must align (out of 13)

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

    # Super Trend
    'supertrend_enabled': True,
    'supertrend_atr_period': 10,
    'supertrend_multiplier': 3,
    'supertrend_change_detection': True,
    'supertrend_use_close': True,
    'supertrend_weight': 20,

    # ADX (Average Directional Index)
    'adx_enabled': True,
    'adx_period': 14,
    'adx_threshold': 25,
    'adx_use_di_cross': True,
    'adx_weight': 15,

    # Heikin Ashi
    'heikin_ashi_enabled': True,
    'heikin_ashi_smooth': True,
    'heikin_ashi_doji': True,
    'heikin_ashi_color_change': True,
    'heikin_ashi_consecutive': 3,
    'heikin_ashi_weight': 15,

    # VWAP (Volume Weighted Average Price)
    'vwap_enabled': True,
    'vwap_std_bands': True,
    'vwap_band_mult_1': 1,
    'vwap_band_mult_2': 2,
    'vwap_reset_period': 'daily',
    'vwap_anchored': True,
    'vwap_volume_confirm': True,
    'vwap_deviation_alert': 2,
    'vwap_weight': 25,

    # 🎰 OTC Market Anomaly Detection
    'otc_strategy_enabled': True,  # Enable OTC-specific pattern detection
    'otc_min_confidence': 75,  # Minimum confidence for OTC signals (75%)
    'otc_priority_boost': 5,  # Confidence boost for OTC signals on OTC markets
    'otc_detection_types': {  # Enable/disable specific OTC detection methods
        'synthetic_pattern': True,  # Sine waves, staircases
        'artificial_level': True,  # Artificial S/R levels
        'micro_reversion': True,  # Extreme move reversions
        'sequence_pattern': True,  # Repeating price sequences
        'time_anomaly': True  # Time-based patterns
    },
    'otc_weight': 30,  # High weight for OTC signals (they're specialized)

    # 🔄 Reversal Catcher - 7 Indicator Confluence System
    'reversal_catcher_enabled': True,  # Enable reversal detection
    'reversal_sensitivity': 'medium',  # high (3+ indicators), medium (4+), low (5+)
    'reversal_min_confidence': 65,  # Minimum confidence for reversal signals (65%)
    'reversal_indicator_boost': 2,  # Confidence boost per confirming indicator (%)
    'reversal_weight': 25,  # Weight for reversal signals in decision system

    # Trading Settings
    'min_confidence': 4,
    'min_payout': 85,
    'max_trades_per_hour': 20,
    'risk_per_trade': 1.0,

    # Trade Frequency Limits
    'trade_limits_enabled': True,
    'trade_limit_5min_enabled': True,
    'trade_limit_5min': 3,      # Max trades in 5 minutes
    'trade_limit_10min_enabled': True,
    'trade_limit_10min': 5,     # Max trades in 10 minutes
    'trade_limit_20min_enabled': True,
    'trade_limit_20min': 8,     # Max trades in 20 minutes
    'trade_limit_30min_enabled': True,
    'trade_limit_30min': 10,    # Max trades in 30 minutes
    'trade_limit_60min_enabled': True,
    'trade_limit_60min': 15,    # Max trades in 60 minutes
    'cooldown_after_loss_enabled': True,
    'cooldown_after_loss': 60,  # Seconds to wait after a loss
    'cooldown_after_win_enabled': True,
    'cooldown_after_win': 30,   # Seconds to wait after a win
    'max_consecutive_trades_enabled': True,
    'max_consecutive_trades': 3, # Max trades without a break
    'break_duration': 120,       # Seconds to break after consecutive trades

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


# Try to initialize AI on startup now that add_log is available
print("\n" + "=" * 80)
print("🤖 INITIALIZING AI TRADING SYSTEM")
print("=" * 80)
if not ai_brain:
    success = initialize_ai_system()
    if success:
        print("=" * 80)
        print("✅ AI SYSTEM READY - GPT-4 TRADING GOD ONLINE!")
        print(f"   AI_ENABLED: {AI_ENABLED}")
        print(f"   ai_brain: {ai_brain is not None}")
        print(f"   optimizer: {optimizer is not None}")
        print("=" * 80 + "\n")
    else:
        print("=" * 80)
        print("❌ AI SYSTEM FAILED TO INITIALIZE")
        print("   Check errors above for details")
        print("=" * 80 + "\n")
else:
    print("✅ AI already initialized")
    print("=" * 80 + "\n")


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


async def calculate_macd(candles, fast_period=12, slow_period=26, signal_period=9):
    """
    MACD (Moving Average Convergence Divergence)
    Returns: (MACD line, Signal line, Histogram)
    """
    if len(candles) < slow_period + signal_period:
        return None, None, None

    # Calculate EMAs for MACD
    ema_fast = await calculate_ema(candles, fast_period)
    ema_slow = await calculate_ema(candles, slow_period)

    if ema_fast is None or ema_slow is None:
        return None, None, None

    # MACD Line = Fast EMA - Slow EMA
    macd_line = ema_fast - ema_slow

    # Signal Line = EMA of MACD Line (simplified - using recent MACD values)
    # For now, we'll use a simple moving average of MACD
    macd_values = []
    for i in range(max(signal_period, 1)):
        if len(candles) > slow_period + i:
            ema_f = await calculate_ema(candles[:-i] if i > 0 else candles, fast_period)
            ema_s = await calculate_ema(candles[:-i] if i > 0 else candles, slow_period)
            if ema_f and ema_s:
                macd_values.append(ema_f - ema_s)

    signal_line = sum(macd_values) / len(macd_values) if macd_values else macd_line

    # Histogram = MACD - Signal
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


async def calculate_stochastic(candles, k_period=14, d_period=3):
    """
    Stochastic Oscillator
    Returns: (%K, %D)
    """
    if len(candles) < k_period:
        return None, None

    recent = candles[-k_period:]
    current_close = candles[-1][2]

    # Get highest high and lowest low
    highest_high = max([c[3] for c in recent])
    lowest_low = min([c[4] for c in recent])

    # Calculate %K
    if highest_high == lowest_low:
        k_value = 50
    else:
        k_value = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100

    # Calculate %D (SMA of %K) - simplified
    k_values = []
    for i in range(d_period):
        if len(candles) > k_period + i:
            recent_k = candles[-(k_period+i):-i] if i > 0 else candles[-k_period:]
            close_k = candles[-(i+1)][2]
            high_k = max([c[3] for c in recent_k])
            low_k = min([c[4] for c in recent_k])
            if high_k != low_k:
                k_values.append(((close_k - low_k) / (high_k - low_k)) * 100)

    d_value = sum(k_values) / len(k_values) if k_values else k_value

    return k_value, d_value


async def calculate_supertrend(candles, atr_period=10, multiplier=3):
    """
    SuperTrend Indicator
    Returns: (supertrend_value, trend_direction)
    trend_direction: 1 = bullish, -1 = bearish
    """
    if len(candles) < atr_period + 1:
        return None, 0

    atr = await calculate_atr(candles, atr_period)
    if not atr:
        return None, 0

    # Use HL/2 as base
    current_hl2 = (candles[-1][3] + candles[-1][4]) / 2

    # Basic bands
    upper_band = current_hl2 + (multiplier * atr)
    lower_band = current_hl2 - (multiplier * atr)

    current_close = candles[-1][2]

    # Determine trend
    if current_close > upper_band:
        trend = 1  # Bullish
        supertrend = lower_band
    elif current_close < lower_band:
        trend = -1  # Bearish
        supertrend = upper_band
    else:
        # Check previous trend
        prev_close = candles[-2][2]
        prev_hl2 = (candles[-2][3] + candles[-2][4]) / 2
        if prev_close > prev_hl2:
            trend = 1
            supertrend = lower_band
        else:
            trend = -1
            supertrend = upper_band

    return supertrend, trend


async def calculate_heikin_ashi(candles):
    """
    Calculate Heikin Ashi candles and detect trend signals

    Heikin Ashi Formula:
    - HA Close = (Open + High + Low + Close) / 4
    - HA Open = (Previous HA Open + Previous HA Close) / 2
    - HA High = Max(High, HA Open, HA Close)
    - HA Low = Min(Low, HA Open, HA Close)

    Returns: (trend, consecutive_count, signal_strength)
    """
    if len(candles) < 10:
        return 'neutral', 0, 0

    ha_candles = []

    # First HA candle - use real values
    first = candles[0]
    ha_open = (first[1] + first[2]) / 2  # (Open + Close) / 2
    ha_close = (first[1] + first[3] + first[4] + first[2]) / 4  # (O+H+L+C)/4
    ha_high = max(first[3], ha_open, ha_close)
    ha_low = min(first[4], ha_open, ha_close)
    ha_candles.append([ha_open, ha_close, ha_high, ha_low])

    # Calculate rest of HA candles
    for candle in candles[1:]:
        prev_ha = ha_candles[-1]

        # HA Open = (Prev HA Open + Prev HA Close) / 2
        ha_open = (prev_ha[0] + prev_ha[1]) / 2

        # HA Close = (O + H + L + C) / 4
        ha_close = (candle[1] + candle[3] + candle[4] + candle[2]) / 4

        # HA High = Max(H, HA Open, HA Close)
        ha_high = max(candle[3], ha_open, ha_close)

        # HA Low = Min(L, HA Open, HA Close)
        ha_low = min(candle[4], ha_open, ha_close)

        ha_candles.append([ha_open, ha_close, ha_high, ha_low])

    # Analyze last 5 HA candles for trend
    recent_ha = ha_candles[-5:]
    bullish_count = sum(1 for ha in recent_ha if ha[1] > ha[0])  # Close > Open
    bearish_count = sum(1 for ha in recent_ha if ha[1] < ha[0])  # Close < Open

    # Get consecutive candles of same color
    consecutive = 1
    last_ha = ha_candles[-1]
    is_bullish = last_ha[1] > last_ha[0]

    for ha in reversed(ha_candles[-6:-1]):
        if is_bullish and ha[1] > ha[0]:
            consecutive += 1
        elif not is_bullish and ha[1] < ha[0]:
            consecutive += 1
        else:
            break

    # Determine trend and strength
    if bullish_count >= 4:
        trend = 'bullish'
        strength = min(100, bullish_count * 20 + consecutive * 10)
    elif bearish_count >= 4:
        trend = 'bearish'
        strength = min(100, bearish_count * 20 + consecutive * 10)
    else:
        trend = 'neutral'
        strength = 0

    # Check for doji (small body)
    last_ha = ha_candles[-1]
    body = abs(last_ha[1] - last_ha[0])
    total_range = last_ha[2] - last_ha[3]

    if total_range > 0 and body / total_range < 0.1:
        trend = 'doji'
        strength = 60  # Doji indicates potential reversal

    return trend, consecutive, strength


async def calculate_adx(candles, period=14):
    """
    Calculate ADX (Average Directional Index) with +DI and -DI

    ADX measures trend strength (0-100):
    - 0-25: Weak or no trend (ranging market)
    - 25-50: Strong trend
    - 50-75: Very strong trend
    - 75-100: Extremely strong trend

    +DI and -DI show direction:
    - +DI > -DI: Uptrend
    - -DI > +DI: Downtrend
    - DI Crossover: Potential entry signal

    Returns: (adx_value, plus_di, minus_di, di_cross_signal)
    """
    if len(candles) < period * 2:
        return 25, 50, 50, 'neutral'

    # Step 1: Calculate True Range (TR) and Directional Movement (+DM, -DM)
    tr_list = []
    plus_dm_list = []
    minus_dm_list = []

    for i in range(1, len(candles)):
        prev_candle = candles[i-1]
        curr_candle = candles[i]

        # Extract OHLC
        prev_high = prev_candle[3]
        prev_low = prev_candle[4]
        prev_close = prev_candle[2]
        curr_high = curr_candle[3]
        curr_low = curr_candle[4]

        # True Range = max of:
        # 1. Current High - Current Low
        # 2. |Current High - Previous Close|
        # 3. |Current Low - Previous Close|
        tr = max(
            curr_high - curr_low,
            abs(curr_high - prev_close),
            abs(curr_low - prev_close)
        )
        tr_list.append(tr)

        # Directional Movement
        high_diff = curr_high - prev_high
        low_diff = prev_low - curr_low

        # +DM: Positive if current high > previous high
        plus_dm = high_diff if high_diff > low_diff and high_diff > 0 else 0

        # -DM: Positive if previous low > current low
        minus_dm = low_diff if low_diff > high_diff and low_diff > 0 else 0

        plus_dm_list.append(plus_dm)
        minus_dm_list.append(minus_dm)

    # Step 2: Smooth TR, +DM, -DM using Wilder's smoothing
    # First value = sum of first 'period' values
    # Subsequent values = (previous_smooth * (period-1) + current_value) / period

    def wilders_smoothing(values, period):
        if len(values) < period:
            return []

        smoothed = []
        # First smoothed value
        first_smooth = sum(values[:period]) / period
        smoothed.append(first_smooth)

        # Subsequent smoothed values
        for i in range(period, len(values)):
            smooth = (smoothed[-1] * (period - 1) + values[i]) / period
            smoothed.append(smooth)

        return smoothed

    smoothed_tr = wilders_smoothing(tr_list, period)
    smoothed_plus_dm = wilders_smoothing(plus_dm_list, period)
    smoothed_minus_dm = wilders_smoothing(minus_dm_list, period)

    if not smoothed_tr or len(smoothed_tr) < period:
        return 25, 50, 50, 'neutral'

    # Step 3: Calculate +DI and -DI
    plus_di_list = []
    minus_di_list = []

    for i in range(len(smoothed_tr)):
        if smoothed_tr[i] != 0:
            plus_di = 100 * (smoothed_plus_dm[i] / smoothed_tr[i])
            minus_di = 100 * (smoothed_minus_dm[i] / smoothed_tr[i])
        else:
            plus_di = 0
            minus_di = 0

        plus_di_list.append(plus_di)
        minus_di_list.append(minus_di)

    # Step 4: Calculate DX (Directional Index)
    dx_list = []

    for i in range(len(plus_di_list)):
        di_sum = plus_di_list[i] + minus_di_list[i]
        if di_sum != 0:
            dx = 100 * abs(plus_di_list[i] - minus_di_list[i]) / di_sum
        else:
            dx = 0
        dx_list.append(dx)

    # Step 5: Calculate ADX (smoothed DX)
    adx_list = wilders_smoothing(dx_list, period)

    if not adx_list:
        return 25, 50, 50, 'neutral'

    # Get latest values
    adx_value = adx_list[-1]
    plus_di = plus_di_list[-1]
    minus_di = minus_di_list[-1]

    # Step 6: Detect DI Crossover signals
    di_cross_signal = 'neutral'

    if len(plus_di_list) >= 2 and len(minus_di_list) >= 2:
        prev_plus_di = plus_di_list[-2]
        prev_minus_di = minus_di_list[-2]

        # Bullish crossover: +DI crosses above -DI
        if prev_plus_di <= prev_minus_di and plus_di > minus_di:
            di_cross_signal = 'bullish_cross'

        # Bearish crossover: -DI crosses above +DI
        elif prev_minus_di <= prev_plus_di and minus_di > plus_di:
            di_cross_signal = 'bearish_cross'

        # Continuation signals
        elif plus_di > minus_di:
            di_cross_signal = 'bullish'
        elif minus_di > plus_di:
            di_cross_signal = 'bearish'

    return round(adx_value, 2), round(plus_di, 2), round(minus_di, 2), di_cross_signal


async def calculate_synthetic_volume(candles):
    """
    Calculate synthetic volume for binary options (Pocket Option doesn't provide real volume)

    Synthetic volume is calculated based on:
    1. Price movement (range of the candle)
    2. Volatility (how much price moved vs average)
    3. Body size (strength of directional movement)

    Returns: list of volume values (one per candle)
    """
    if len(candles) < 20:
        # Return normalized volume of 1.0 for each candle if not enough data
        return [1.0] * len(candles)

    volumes = []

    for i in range(len(candles)):
        candle = candles[i]
        open_price = candle[1]
        close_price = candle[2]
        high = candle[3]
        low = candle[4]

        # 1. Range-based volume (price movement)
        price_range = high - low
        if price_range == 0:
            price_range = 0.00001  # Avoid division by zero

        # 2. Body strength (directional conviction)
        body = abs(close_price - open_price)
        body_ratio = body / price_range if price_range > 0 else 0.5

        # 3. Volatility factor (compare to recent average range)
        if i >= 14:
            recent_candles = candles[i-14:i]
            avg_range = sum([c[3] - c[4] for c in recent_candles]) / 14
            volatility_factor = price_range / avg_range if avg_range > 0 else 1.0
        else:
            volatility_factor = 1.0

        # Synthetic volume formula
        # Higher volume when: larger range, stronger body, higher volatility
        synthetic_vol = price_range * (1 + body_ratio) * volatility_factor

        volumes.append(synthetic_vol)

    # Normalize volumes to have a mean of 1.0
    if len(volumes) > 0:
        avg_vol = sum(volumes) / len(volumes)
        if avg_vol > 0:
            volumes = [v / avg_vol for v in volumes]

    return volumes


async def analyze_volume_trend(volumes, period=14):
    """
    Analyze volume trend to detect accumulation/distribution

    Returns: (trend, strength, signal)
    - trend: 'increasing', 'decreasing', 'stable'
    - strength: 0-100 (how strong the trend is)
    - signal: 'high_volume', 'low_volume', 'normal'
    """
    if len(volumes) < period * 2:
        return 'stable', 0, 'normal'

    recent_volumes = volumes[-period:]
    older_volumes = volumes[-period*2:-period]

    recent_avg = sum(recent_volumes) / len(recent_volumes)
    older_avg = sum(older_volumes) / len(older_volumes)

    # Calculate trend
    if recent_avg > older_avg * 1.2:
        trend = 'increasing'
        strength = min(100, int((recent_avg / older_avg - 1) * 100))
    elif recent_avg < older_avg * 0.8:
        trend = 'decreasing'
        strength = min(100, int((1 - recent_avg / older_avg) * 100))
    else:
        trend = 'stable'
        strength = 0

    # Determine current volume level
    current_vol = volumes[-1]
    avg_vol = sum(volumes[-period:]) / period

    if current_vol > avg_vol * 1.5:
        signal = 'high_volume'
    elif current_vol < avg_vol * 0.5:
        signal = 'low_volume'
    else:
        signal = 'normal'

    return trend, strength, signal


async def calculate_vwap(candles, volumes):
    """
    Calculate VWAP (Volume Weighted Average Price) with standard deviation bands

    VWAP = Sum(Typical Price * Volume) / Sum(Volume)
    Typical Price = (High + Low + Close) / 3

    Returns: (vwap, upper_band_1, lower_band_1, upper_band_2, lower_band_2, position, deviation)
    """
    if len(candles) < 20 or len(volumes) < 20:
        return None, None, None, None, None, 'At VWAP', 0

    # Use last 100 candles for VWAP calculation (or all if less than 100)
    period = min(100, len(candles))
    recent_candles = candles[-period:]
    recent_volumes = volumes[-period:]

    # Calculate VWAP
    typical_prices = []
    pv_sum = 0  # Price * Volume sum
    volume_sum = 0

    for i in range(len(recent_candles)):
        candle = recent_candles[i]
        volume = recent_volumes[i]

        # Typical price (HLC/3)
        typical_price = (candle[3] + candle[4] + candle[2]) / 3
        typical_prices.append(typical_price)

        pv_sum += typical_price * volume
        volume_sum += volume

    vwap = pv_sum / volume_sum if volume_sum > 0 else recent_candles[-1][2]

    # Calculate standard deviation for bands
    squared_diff_sum = 0
    for i in range(len(recent_candles)):
        typical_price = typical_prices[i]
        volume = recent_volumes[i]
        squared_diff_sum += ((typical_price - vwap) ** 2) * volume

    variance = squared_diff_sum / volume_sum if volume_sum > 0 else 0
    std_dev = variance ** 0.5

    # VWAP bands (1 and 2 standard deviations)
    upper_band_1 = vwap + std_dev
    lower_band_1 = vwap - std_dev
    upper_band_2 = vwap + (std_dev * 2)
    lower_band_2 = vwap - (std_dev * 2)

    # Determine position relative to VWAP
    current_price = candles[-1][2]

    if current_price > upper_band_2:
        position = 'Far Above VWAP'
        deviation = 2.0
    elif current_price > upper_band_1:
        position = 'Above VWAP'
        deviation = (current_price - vwap) / std_dev if std_dev > 0 else 0
    elif current_price < lower_band_2:
        position = 'Far Below VWAP'
        deviation = -2.0
    elif current_price < lower_band_1:
        position = 'Below VWAP'
        deviation = (current_price - vwap) / std_dev if std_dev > 0 else 0
    else:
        position = 'At VWAP'
        deviation = (current_price - vwap) / std_dev if std_dev > 0 else 0

    return (
        round(vwap, 5),
        round(upper_band_1, 5),
        round(lower_band_1, 5),
        round(upper_band_2, 5),
        round(lower_band_2, 5),
        position,
        round(deviation, 2)
    )


async def detect_candlestick_patterns(candles):
    """
    Detect powerful candlestick patterns
    Returns: (pattern_name, signal_strength, direction)
    """
    if len(candles) < 3:
        return None, 0, 'neutral'

    current = candles[-1]
    prev = candles[-2]
    prev2 = candles[-3]

    open_c, high_c, low_c, close_c = current[1], current[3], current[4], current[2]
    open_p, high_p, low_p, close_p = prev[1], prev[3], prev[4], prev[2]

    body_c = abs(close_c - open_c)
    body_p = abs(close_p - open_p)

    # Bullish Patterns
    # 1. Hammer (bullish reversal)
    if body_c > 0:
        lower_shadow = min(open_c, close_c) - low_c
        upper_shadow = high_c - max(open_c, close_c)
        if lower_shadow > body_c * 2 and upper_shadow < body_c * 0.3 and close_c > open_c:
            return "Hammer", 3, 'call'

    # 2. Bullish Engulfing
    if close_p < open_p and close_c > open_c:  # prev red, current green
        if close_c > open_p and open_c < close_p:  # engulfs previous
            return "Bullish Engulfing", 4, 'call'

    # 3. Morning Star (3-candle pattern)
    if len(candles) >= 3:
        open_p2, close_p2 = prev2[1], prev2[2]
        body_p2 = abs(close_p2 - open_p2)
        if close_p2 < open_p2:  # First candle red
            if abs(close_p - open_p) < body_p2 * 0.3:  # Second small
                if close_c > open_c and close_c > (open_p2 + close_p2) / 2:  # Third green
                    return "Morning Star", 5, 'call'

    # Bearish Patterns
    # 4. Shooting Star (bearish reversal)
    if body_c > 0:
        upper_shadow = high_c - max(open_c, close_c)
        lower_shadow = min(open_c, close_c) - low_c
        if upper_shadow > body_c * 2 and lower_shadow < body_c * 0.3 and close_c < open_c:
            return "Shooting Star", 3, 'put'

    # 5. Bearish Engulfing
    if close_p > open_p and close_c < open_c:  # prev green, current red
        if close_c < open_p and open_c > close_p:  # engulfs previous
            return "Bearish Engulfing", 4, 'put'

    # 6. Evening Star
    if len(candles) >= 3:
        open_p2, close_p2 = prev2[1], prev2[2]
        body_p2 = abs(close_p2 - open_p2)
        if close_p2 > open_p2:  # First candle green
            if abs(close_p - open_p) < body_p2 * 0.3:  # Second small
                if close_c < open_c and close_c < (open_p2 + close_p2) / 2:  # Third red
                    return "Evening Star", 5, 'put'

    # Doji (indecision - neutral but useful)
    if body_c < (high_c - low_c) * 0.1:
        return "Doji", 1, 'neutral'

    return None, 0, 'neutral'


# ==================== TRADING STRATEGY ====================

async def enhanced_strategy(candles):
    """
    Advanced AI-enhanced strategy with multiple indicators
    """
    global ACTIVE_STRATEGY_ID, ACTIVE_STRATEGY_NAME

    if len(candles) < 50:
        return None

    current_price = candles[-1][2]

    # CALCULATE ALL INDICATORS FIRST (for both AI and traditional analysis)
    ema_fast = await calculate_ema(candles, settings['fast_ema'])
    ema_slow = await calculate_ema(candles, settings['slow_ema'])
    ema_fast_prev = await calculate_ema(candles[:-1], settings['fast_ema'])
    ema_slow_prev = await calculate_ema(candles[:-1], settings['slow_ema'])

    rsi = await calculate_rsi(candles, settings['rsi_period'])
    upper_bb, middle_bb, lower_bb = await calculate_bollinger_bands(candles, 20, 2)
    atr = await calculate_atr(candles)
    support, resistance = await detect_support_resistance(candles)

    # ULTRA POWERFUL INDICATORS
    macd_line, macd_signal, macd_histogram = await calculate_macd(candles)
    stoch_k, stoch_d = await calculate_stochastic(candles)
    supertrend_value, supertrend_direction = await calculate_supertrend(candles)
    pattern_name, pattern_strength, pattern_direction = await detect_candlestick_patterns(candles)

    # 🕯️ Heikin Ashi calculation
    heikin_ashi_trend = 'neutral'
    heikin_ashi_consecutive = 0
    heikin_ashi_strength = 0
    if settings.get('heikin_ashi_enabled', True):
        heikin_ashi_trend, heikin_ashi_consecutive, heikin_ashi_strength = await calculate_heikin_ashi(candles)

    # 📊 ADX (Average Directional Index) calculation
    adx_value = 25
    plus_di = 50
    minus_di = 50
    di_cross_signal = 'neutral'
    if settings.get('adx_enabled', True):
        adx_value, plus_di, minus_di, di_cross_signal = await calculate_adx(candles, settings.get('adx_period', 14))

        # Log ADX values for visibility
        adx_strength = "WEAK" if adx_value < 25 else "STRONG" if adx_value < 50 else "VERY STRONG" if adx_value < 75 else "EXTREMELY STRONG"
        trend_direction = "BULLISH" if plus_di > minus_di else "BEARISH"

        print(f"📊 ADX: {adx_value:.1f} ({adx_strength} TREND)")
        print(f"   ├─ +DI: {plus_di:.1f} | -DI: {minus_di:.1f}")
        print(f"   ├─ Direction: {trend_direction} ({di_cross_signal.upper()})")

        if di_cross_signal == 'bullish_cross':
            print(f"   └─ ✅ BULLISH CROSSOVER! +DI crossed above -DI - Strong BUY signal!")
        elif di_cross_signal == 'bearish_cross':
            print(f"   └─ ⚠️ BEARISH CROSSOVER! -DI crossed above +DI - Strong SELL signal!")

    # 📊 VOLUME & VWAP calculation (Synthetic Volume for Binary Options)
    volumes = []
    volume_trend = 'stable'
    volume_strength = 0
    volume_signal = 'normal'
    vwap_value = None
    vwap_upper_1 = None
    vwap_lower_1 = None
    vwap_upper_2 = None
    vwap_lower_2 = None
    vwap_position = 'At VWAP'
    vwap_deviation = 0

    if settings.get('vwap_enabled', True):
        # Calculate synthetic volume
        volumes = await calculate_synthetic_volume(candles)

        # Analyze volume trend
        volume_trend, volume_strength, volume_signal = await analyze_volume_trend(volumes)

        # Calculate VWAP
        vwap_value, vwap_upper_1, vwap_lower_1, vwap_upper_2, vwap_lower_2, vwap_position, vwap_deviation = await calculate_vwap(candles, volumes)

        # Log Volume & VWAP for visibility
        print(f"📊 VOLUME: {volume_signal.upper()} (Trend: {volume_trend.upper()}, Strength: {volume_strength})")
        if vwap_value:
            print(f"📊 VWAP: {vwap_value:.5f} | Current: {current_price:.5f}")
            print(f"   ├─ Position: {vwap_position}")
            print(f"   ├─ Deviation: {vwap_deviation:.2f} σ")
            print(f"   ├─ Bands: [{vwap_lower_2:.5f} | {vwap_lower_1:.5f} | {vwap_value:.5f} | {vwap_upper_1:.5f} | {vwap_upper_2:.5f}]")

            # VWAP trading signals
            if vwap_position == 'Far Below VWAP' and volume_signal == 'high_volume':
                print(f"   └─ ✅ VWAP BOUNCE OPPORTUNITY! Price far below + high volume")
            elif vwap_position == 'Far Above VWAP' and volume_signal == 'high_volume':
                print(f"   └─ ⚠️ VWAP REVERSAL RISK! Price far above + high volume")

    if None in [ema_fast, ema_slow, rsi, upper_bb, lower_bb]:
        return None

    # If AI is enabled, use it for analysis
    # Check both AI_ENABLED global and settings value
    ai_enabled_flag = AI_ENABLED or settings.get('ai_enabled', False)
    ai_brain_available = ai_brain is not None

    # DEBUG: Log AI status
    print(f"🔍 AI Check - AI_ENABLED: {AI_ENABLED}, settings.ai_enabled: {settings.get('ai_enabled', False)}, ai_brain: {ai_brain is not None}")

    if ai_enabled_flag and ai_brain_available:
        try:
            add_log(f"🤖🧠 DUAL AI ENSEMBLE ANALYSIS STARTING...")
            print(f"🤖 AI Ensemble Analysis initiated for {CURRENT_ASSET}")

            # Get recent trades for AI context
            recent_trades_list = bot_state.get('trades', [])[-10:]  # Last 10 trades

            # Calculate win streak
            streak_count = 0
            streak_type = None
            for trade in reversed(recent_trades_list):
                if trade.get('result') == 'WIN':
                    if streak_type is None or streak_type == 'WIN':
                        streak_count += 1
                        streak_type = 'WIN'
                    else:
                        break
                elif trade.get('result') == 'LOSS':
                    if streak_type is None or streak_type == 'LOSS':
                        streak_count += 1
                        streak_type = 'LOSS'
                    else:
                        break
            streak = f"{streak_count}W" if streak_type == 'WIN' else f"{streak_count}L" if streak_type == 'LOSS' else "New"

            # 🚀 ULTRA MASTER SYSTEMS INTEGRATION
            market_regime = 'unknown'
            regime_confidence = 0
            regime_desc = ''
            mtf_data = None
            candles_5m = []
            candles_15m = []

            # Multi-Timeframe Analysis
            if mtf_analyzer:
                try:
                    mtf_data = mtf_analyzer.get_multi_timeframe_data(candles)
                    candles_5m = mtf_data.get('5m', [])
                    candles_15m = mtf_data.get('15m', [])
                    htf_context = mtf_analyzer.get_higher_timeframe_context(candles_5m, candles_15m)
                    print(f"📊 Multi-Timeframe: {htf_context}")
                except Exception as e:
                    print(f"⚠️ MTF Analysis error: {e}")

            # Market Regime Detection
            if regime_detector:
                try:
                    # Prepare indicators dict for regime detection
                    regime_indicators = {
                        'rsi': rsi or 50,
                        'ema_cross': 'Bullish' if ema_fast and ema_slow and ema_fast > ema_slow else 'Bearish',
                        'supertrend': 'BUY' if supertrend_direction == 1 else 'SELL' if supertrend_direction == -1 else 'Neutral',
                        'adx': 25
                    }
                    market_regime, regime_confidence, regime_desc = await regime_detector.detect_regime(
                        candles,
                        candles_5m,
                        candles_15m,
                        regime_indicators
                    )
                    print(f"🎯 Market Regime: {market_regime.upper()} ({regime_confidence:.0f}%) - {regime_desc}")
                except Exception as e:
                    print(f"⚠️ Regime Detection error: {e}")

            # 🕯️ CANDLESTICK PATTERN RECOGNITION (Multi-Timeframe)
            pattern_data = {}
            pattern_type = None
            pattern_strength = 0
            pattern_quality = 0
            if pattern_recognizer and settings.get('pattern_recognition_enabled', True):
                try:
                    # Detect patterns across all timeframes
                    pattern_data = pattern_recognizer.detect_all_patterns_mtf(
                        candles,
                        candles_5m,
                        candles_15m
                    )

                    strongest = pattern_data.get('strongest_signal', {})
                    if strongest.get('pattern'):
                        pattern_type = strongest['pattern']
                        pattern_strength = strongest.get('strength', 0)
                        timeframe = strongest.get('timeframe', '1m')

                        print(f"🕯️ PATTERN DETECTED: {pattern_type.upper().replace('_', ' ')} on {timeframe} (Strength: {pattern_strength}%)")

                        # Evaluate pattern quality with context
                        temp_indicators = {
                            'rsi': rsi or 50,
                            'macd_histogram': macd_histogram or 0,
                            'regime': market_regime
                        }
                        quality_eval = pattern_recognizer.evaluate_pattern_quality(
                            strongest.get('data', {}),
                            temp_indicators,
                            market_regime
                        )
                        pattern_quality = quality_eval.get('quality_score', 0)

                        print(f"   └─ Quality Score: {pattern_quality}/100 - {quality_eval.get('trade_recommendation', 'neutral').upper()}")
                        if quality_eval.get('reasons'):
                            for reason in quality_eval['reasons'][:3]:  # Show top 3 reasons
                                print(f"      {reason}")

                        # Update bot_state with pattern data for UI
                        bot_state['pattern_data'] = {
                            'pattern_type': pattern_type,
                            'pattern_strength': pattern_strength,
                            'pattern_quality': pattern_quality,
                            'pattern_timeframe': timeframe
                        }
                    else:
                        # Clear pattern data if no pattern detected
                        bot_state['pattern_data'] = {
                            'pattern_type': None,
                            'pattern_strength': 0,
                            'pattern_quality': 0,
                            'pattern_timeframe': '1m'
                        }

                except Exception as e:
                    print(f"⚠️ Pattern Recognition error: {e}")

            # 🎰 OTC MARKET ANOMALY DETECTION
            otc_signal = None
            otc_confidence = 0
            otc_details = {}
            is_otc_market = False
            if otc_strategy and settings.get('otc_strategy_enabled', True):
                try:
                    # Check if current asset is OTC
                    is_otc_market = otc_strategy.is_otc_asset(CURRENT_ASSET or '')

                    if is_otc_market:
                        # Run OTC anomaly detection
                        otc_signal, otc_confidence, otc_details = otc_strategy.analyze_otc_tick(
                            price=current_price,
                            timestamp=datetime.now(),
                            asset_name=CURRENT_ASSET
                        )

                        if otc_signal and otc_confidence > 0:
                            print(f"🎰 OTC ANOMALY DETECTED: {otc_signal.upper()} @ {otc_confidence:.1%}")
                            print(f"   ├─ Detections: {otc_details.get('final_decision', {}).get('signal_count', 0)}")

                            # Show individual detection types
                            if 'synthetic_pattern' in otc_details:
                                sp = otc_details['synthetic_pattern']
                                print(f"   ├─ 🔮 Synthetic Pattern: {sp['direction']} @ {sp['confidence']:.1%}")
                            if 'artificial_level' in otc_details:
                                al = otc_details['artificial_level']
                                print(f"   ├─ 🎯 Artificial Level: {al['direction']} @ {al['confidence']:.1%}")
                            if 'micro_reversion' in otc_details:
                                mr = otc_details['micro_reversion']
                                print(f"   ├─ ⚡ Micro Reversion: {mr['direction']} @ {mr['confidence']:.1%}")
                            if 'sequence_pattern' in otc_details:
                                seq = otc_details['sequence_pattern']
                                print(f"   ├─ 🔄 Sequence Pattern: {seq['direction']} @ {seq['confidence']:.1%}")
                            if 'time_anomaly' in otc_details:
                                ta = otc_details['time_anomaly']
                                print(f"   └─ ⏰ Time Anomaly: {ta['direction']} @ {ta['confidence']:.1%}")
                        else:
                            print(f"🎰 OTC Market Detected - No significant anomalies (waiting for high-probability setup)")

                except Exception as e:
                    print(f"⚠️ OTC Anomaly Detection error: {e}")

            # 🔄 REVERSAL CATCHER - 7 INDICATOR CONFLUENCE SYSTEM
            reversal_signal = None
            reversal_confidence = 0
            reversal_details = {}
            if reversal_catcher and settings.get('reversal_catcher_enabled', True):
                try:
                    # Feed price data to reversal catcher
                    # Use synthetic volume from VWAP calculation
                    current_volume = volumes[-1] if volumes and len(volumes) > 0 else 1.0

                    reversal_signal, reversal_confidence, reversal_details = reversal_catcher.add_price(
                        price=current_price,
                        volume=current_volume,
                        timestamp=datetime.now()
                    )

                    if reversal_signal and reversal_confidence > 0:
                        confirming_indicators = reversal_details.get('indicators', [])
                        total_confirming = reversal_details.get('total_confirming', 0)
                        conflicting = reversal_details.get('conflicting', 0)

                        print(f"🔄 REVERSAL DETECTED: {reversal_signal.upper()} @ {reversal_confidence:.1%}")
                        print(f"   ├─ Confirming Indicators: {total_confirming}/7")
                        print(f"   ├─ Conflicting: {conflicting}")
                        print(f"   └─ Top Signals:")

                        # Show top 3 indicators
                        for ind in confirming_indicators[:3]:
                            ind_name = ind['name'].replace('_', ' ').title()
                            ind_type = ind['details'].get('type', 'N/A').replace('_', ' ').title()
                            print(f"      • {ind_name}: {ind['strength']:.1%} ({ind_type})")

                except Exception as e:
                    print(f"⚠️ Reversal Catcher error: {e}")

            # Prepare COMPLETE market data for AI
            market_data = {
                'asset': CURRENT_ASSET or 'Unknown',
                'current_price': current_price,
                'change_1m': ((candles[-1][2] - candles[-2][2]) / candles[-2][2]) * 100 if len(candles) > 1 else 0,
                'change_5m': ((candles[-1][2] - candles[-5][2]) / candles[-5][2]) * 100 if len(candles) > 5 else 0,
                'volume': 'Normal',  # TODO: Parse real volume from WebSocket
                'recent_trades': recent_trades_list,
                'win_rate': (bot_state['wins'] / bot_state['total_trades'] * 100) if bot_state['total_trades'] > 0 else 0,
                'total_trades': bot_state['total_trades'],
                'streak': streak
            }

            # Prepare ALL indicators for AI (13-point analysis)
            ai_indicators = {
                # Trend indicators
                'rsi': rsi or 50,
                'ema_cross': 'Bullish' if ema_fast and ema_slow and ema_fast > ema_slow else 'Bearish',
                'supertrend': 'BUY' if supertrend_direction == 1 else 'SELL' if supertrend_direction == -1 else 'Neutral',
                'adx': adx_value,
                'plus_di': plus_di,
                'minus_di': minus_di,
                'di_cross': di_cross_signal,

                # Momentum indicators
                'macd_line': macd_line or 0,
                'macd_signal_line': macd_signal or 0,
                'macd_histogram': macd_histogram or 0,
                'stochastic_k': stoch_k or 50,
                'stochastic_d': stoch_d or 50,
                'bollinger_position': 'Above' if upper_bb and current_price > upper_bb else 'Below' if lower_bb and current_price < lower_bb else 'Middle',

                # Volume & patterns
                'heikin_ashi': heikin_ashi_trend,
                'heikin_ashi_consecutive': heikin_ashi_consecutive,
                'heikin_ashi_strength': heikin_ashi_strength,
                'vwap_position': vwap_position,
                'vwap_deviation': vwap_deviation,
                'vwap_value': vwap_value,
                'vwap_upper_band_1': vwap_upper_1,
                'vwap_lower_band_1': vwap_lower_1,
                'vwap_upper_band_2': vwap_upper_2,
                'vwap_lower_band_2': vwap_lower_2,
                'volume_trend': volume_trend,
                'volume_signal': volume_signal,
                'volume_strength': volume_strength,

                # Support/Resistance
                'support': support or 0,
                'resistance': resistance or 0,
                'atr': atr or 0,

                # Chart patterns (legacy)
                'pattern_name': pattern_name,
                'pattern_strength': pattern_strength or 0,
                'pattern_direction': pattern_direction or 'neutral',

                # 🕯️ Candlestick Patterns (NEW - Multi-Timeframe)
                'pattern_type': pattern_type,  # bullish_engulfing, bearish_engulfing, doji, hammer, etc.
                'pattern_strength': pattern_strength,  # 0-100
                'pattern_quality': pattern_quality,  # 0-100 (quality based on context)
                'pattern_data': pattern_data,  # Full pattern data for AI context
                'regime': market_regime,  # Current market regime

                # 🎰 OTC Market Anomaly Detection
                'is_otc_market': is_otc_market,
                'otc_signal': otc_signal,  # CALL/PUT or None
                'otc_confidence': otc_confidence * 100 if otc_confidence else 0,  # 0-100
                'otc_details': otc_details,  # Full OTC detection details

                # 🔄 Reversal Catcher - 7 Indicator Confluence
                'reversal_signal': reversal_signal,  # CALL/PUT or None
                'reversal_confidence': reversal_confidence * 100 if reversal_confidence else 0,  # 0-100
                'reversal_confirming': reversal_details.get('total_confirming', 0),  # How many indicators agree
                'reversal_details': reversal_details  # Full reversal detection details
            }

            # 🎯 DECISION MODE SYSTEM - Determine what systems to use
            decision_mode = settings.get('decision_mode', 'full_power')
            ai_enabled = settings.get('ai_enabled', True)

            # Initialize decision variables
            ai_action = 'hold'
            ai_confidence = 0
            ai_reason = 'AI not used in this mode'

            # AI ANALYSIS (Skip if not needed by decision mode)
            should_run_ai = (
                decision_mode in ['full_power', 'ai_only'] and
                ai_enabled
            )

            if should_run_ai:
                ai_mode = settings.get('ai_mode', 'ensemble')
                use_gpt4 = settings.get('use_gpt4', True)
                use_claude = settings.get('use_claude', True)

                print(f"📊 Calling AI (Mode: {ai_mode.upper()}, GPT-4: {use_gpt4}, Claude: {use_claude})...")
                # Get AI ENSEMBLE decision with user settings
                ai_action, ai_confidence, ai_reason = await ai_brain.analyze_with_ensemble(
                    market_data,
                    ai_indicators,
                    ai_mode=ai_mode,
                    use_gpt4=use_gpt4,
                    use_claude=use_claude
                )
                print(f"✅ AI Response: {ai_action.upper()} @ {ai_confidence}%")
            else:
                print(f"⏭️  Skipping AI analysis (Decision Mode: {decision_mode.upper()})")

            # 🎯 EVALUATE CUSTOM STRATEGIES (Skip if not needed by decision mode)
            custom_strategy_signals = []
            custom_strategies_enabled = settings.get('custom_strategies_enabled', True)

            should_run_strategies = (
                strategy_builder and
                ULTRA_SYSTEMS_AVAILABLE and
                custom_strategies_enabled and
                decision_mode in ['full_power', 'strategy_only']
            )

            if should_run_strategies:
                try:
                    # Get active strategies (or specific strategy if in strategy_only mode)
                    if decision_mode == 'strategy_only':
                        active_strategy_id = settings.get('active_strategy_id')
                        if active_strategy_id:
                            strategy = strategy_builder.get_strategy(active_strategy_id)
                            if strategy:
                                active_strategies = {active_strategy_id: strategy}
                            else:
                                active_strategies = {}
                                print(f"⚠️  Strategy '{active_strategy_id}' not found")
                        else:
                            active_strategies = {}
                            print(f"⚠️  No strategy selected for 'strategy_only' mode")
                    else:
                        active_strategies = strategy_builder.get_active_strategies()

                    for strategy_id, strategy in active_strategies.items():
                        # Check if timeframe alignment is required
                        mtf_aligned = True
                        if mtf_analyzer and strategy.get('timeframe_alignment', False):
                            alignment_data = mtf_analyzer.analyze_trend_alignment(candles, candles_5m, candles_15m)
                            mtf_aligned = alignment_data.get('aligned', False)

                        # Evaluate strategy with AI decision as input
                        strategy_action, strategy_confidence, strategy_reason = strategy_builder.evaluate_strategy(
                            strategy_id,
                            market_data,
                            ai_indicators,
                            market_regime,
                            mtf_aligned,
                            ai_decision=(ai_action, ai_confidence, ai_reason)
                        )

                        if strategy_action:
                            custom_strategy_signals.append({
                                'strategy_id': strategy_id,
                                'strategy_name': strategy['name'],
                                'action': strategy_action,
                                'confidence': strategy_confidence,
                                'reason': strategy_reason
                            })
                            print(f"📋 Strategy '{strategy['name']}': {strategy_action.upper()} @ {strategy_confidence:.0f}% - {strategy_reason}")

                    # If any custom strategies triggered, use the highest confidence one
                    if custom_strategy_signals:
                        best_strategy = max(custom_strategy_signals, key=lambda x: x['confidence'])
                        print(f"✨ BEST CUSTOM STRATEGY: {best_strategy['strategy_name']} - {best_strategy['action'].upper()} @ {best_strategy['confidence']:.0f}%")

                        # Override AI decision with custom strategy if confidence is higher
                        if best_strategy['confidence'] > ai_confidence:
                            ACTIVE_STRATEGY_ID = best_strategy['strategy_id']
                            ACTIVE_STRATEGY_NAME = best_strategy['strategy_name']
                            ai_action = best_strategy['action']
                            ai_confidence = best_strategy['confidence']
                            ai_reason = f"Custom Strategy '{best_strategy['strategy_name']}': {best_strategy['reason']}"
                            print(f"🔄 STRATEGY OVERRIDE: Using custom strategy decision")

                except Exception as e:
                    print(f"⚠️ Custom strategy evaluation error: {e}")
            else:
                if decision_mode in ['full_power', 'strategy_only']:
                    print(f"⏭️  No active custom strategies")

            # 🎯 FINAL DECISION LOGIC BASED ON DECISION MODE
            print(f"\n{'='*60}")
            print(f"🎯 DECISION MODE: {decision_mode.upper()}")
            print(f"{'='*60}")

            final_action = 'hold'
            final_confidence = 0
            final_reason = 'No signal'

            if decision_mode == 'ai_only':
                # AI ONLY MODE: Use AI decision exclusively
                if ai_confidence >= settings.get('ai_min_confidence', 70):
                    final_action = ai_action
                    final_confidence = ai_confidence
                    final_reason = f"🤖 AI ONLY: {ai_reason[:100]}"
                    print(f"✅ AI Decision: {ai_action.upper()} @ {ai_confidence}%")
                else:
                    print(f"⏭️  AI Confidence too low ({ai_confidence}% < {settings.get('ai_min_confidence', 70)}%)")

            elif decision_mode == 'patterns_only':
                # PATTERNS ONLY MODE: Use pattern quality score for decision
                if pattern_type and pattern_quality >= 70:
                    # Determine action from pattern type
                    if 'bullish' in pattern_type or pattern_type == 'hammer':
                        final_action = 'call'
                    elif 'bearish' in pattern_type or pattern_type == 'shooting_star':
                        final_action = 'put'
                    else:
                        final_action = 'hold'  # Doji = indecision

                    final_confidence = pattern_quality
                    final_reason = f"🕯️ PATTERN: {pattern_type.upper()} (Quality: {pattern_quality}%)"
                    print(f"✅ Pattern Decision: {final_action.upper()} @ {pattern_quality}%")
                else:
                    print(f"⏭️  No high-quality pattern (Quality: {pattern_quality}% < 70%)")

            elif decision_mode == 'strategy_only':
                # STRATEGY ONLY MODE: Use selected custom strategy exclusively
                if custom_strategy_signals:
                    best_strategy = max(custom_strategy_signals, key=lambda x: x['confidence'])
                    ACTIVE_STRATEGY_ID = best_strategy['strategy_id']
                    ACTIVE_STRATEGY_NAME = best_strategy['strategy_name']
                    final_action = best_strategy['action']
                    final_confidence = best_strategy['confidence']
                    final_reason = f"📋 STRATEGY: {best_strategy['strategy_name']} - {best_strategy['reason']}"
                    print(f"✅ Strategy Decision: {final_action.upper()} @ {final_confidence}%")
                else:
                    print(f"⏭️  Strategy did not trigger")

            elif decision_mode == 'full_power':
                # FULL POWER MODE: Combine AI + Patterns + Strategies (best decision wins)
                candidates = []

                # Add AI decision
                if ai_confidence >= settings.get('ai_min_confidence', 70) and ai_action != 'hold':
                    candidates.append({
                        'source': '🤖 AI',
                        'action': ai_action,
                        'confidence': ai_confidence,
                        'reason': ai_reason[:100]
                    })

                # Add pattern decision
                if pattern_type and pattern_quality >= 70:
                    if 'bullish' in pattern_type or pattern_type == 'hammer':
                        pattern_action = 'call'
                    elif 'bearish' in pattern_type or pattern_type == 'shooting_star':
                        pattern_action = 'put'
                    else:
                        pattern_action = 'hold'

                    if pattern_action != 'hold':
                        candidates.append({
                            'source': '🕯️ Pattern',
                            'action': pattern_action,
                            'confidence': pattern_quality,
                            'reason': f"{pattern_type.upper()} (Quality: {pattern_quality}%)"
                        })

                # Add custom strategy decisions
                for strategy_signal in custom_strategy_signals:
                    candidates.append({
                        'source': f"📋 {strategy_signal['strategy_name']}",
                        'action': strategy_signal['action'],
                        'confidence': strategy_signal['confidence'],
                        'reason': strategy_signal['reason']
                    })

                # Add OTC anomaly signal (if market is OTC and signal is strong)
                min_otc_confidence = settings.get('otc_min_confidence', 75)
                if otc_signal and otc_confidence >= min_otc_confidence / 100 and is_otc_market:
                    otc_conf_percent = otc_confidence * 100
                    # OTC signals on OTC markets get priority boost
                    boosted_confidence = min(otc_conf_percent + 5, 95)  # +5% boost for OTC specialty
                    candidates.append({
                        'source': '🎰 OTC Anomaly',
                        'action': otc_signal.lower(),
                        'confidence': boosted_confidence,
                        'reason': f"OTC Market Exploit ({len([k for k in otc_details.keys() if k != 'final_decision'])} patterns detected)"
                    })

                # Add Reversal Catcher signal (if reversal detected with high confidence)
                min_reversal_confidence = settings.get('reversal_min_confidence', 65)
                if reversal_signal and reversal_confidence >= min_reversal_confidence / 100:
                    reversal_conf_percent = reversal_confidence * 100
                    confirming_count = reversal_details.get('total_confirming', 0)
                    # Reversal signals get boost for multiple confirming indicators
                    boost = min(confirming_count * 2, 10)  # Up to +10% for 5+ indicators
                    boosted_confidence = min(reversal_conf_percent + boost, 95)
                    candidates.append({
                        'source': '🔄 Reversal Catcher',
                        'action': reversal_signal.lower(),
                        'confidence': boosted_confidence,
                        'reason': f"7-Indicator Confluence ({confirming_count}/7 indicators agree)"
                    })

                # Pick the highest confidence decision
                if candidates:
                    best = max(candidates, key=lambda x: x['confidence'])
                    final_action = best['action']
                    final_confidence = best['confidence']
                    final_reason = f"{best['source']}: {best['reason']}"

                    print(f"\n📊 ALL CANDIDATES:")
                    for c in candidates:
                        print(f"   {c['source']}: {c['action'].upper()} @ {c['confidence']}%")
                    print(f"\n✨ WINNER: {best['source']} - {best['action'].upper()} @ {best['confidence']}%")

                    # Track which system was used
                    if '📋' in best['source']:
                        for sig in custom_strategy_signals:
                            if sig['strategy_name'] in best['source']:
                                ACTIVE_STRATEGY_ID = sig['strategy_id']
                                ACTIVE_STRATEGY_NAME = sig['strategy_name']
                                break
                else:
                    print(f"⏭️  No signals from any system")

            elif decision_mode == 'indicators_only':
                # INDICATORS ONLY MODE: Fall through to traditional indicator analysis below
                # This will be handled by the existing traditional indicator logic
                print(f"⏭️  Using traditional indicators (legacy code below)")
                # Don't return here, let it continue to traditional analysis

            print(f"{'='*60}\n")

            # If we have a final decision from the new decision modes, return it
            if final_action != 'hold' and decision_mode != 'indicators_only':
                add_log(f"🎯 {decision_mode.upper()}: {final_action.upper()} - {final_reason} ({final_confidence}%)")
                return final_action, final_reason
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            add_log(f"❌ AI analysis failed: {str(e)}")
            print(f"❌ AI ERROR:\n{error_trace}")
    else:
        if not ai_enabled_flag:
            print(f"ℹ️ AI disabled (AI_ENABLED={AI_ENABLED}, settings={settings.get('ai_enabled', False)})")
        if not ai_brain_available:
            print(f"⚠️ AI brain not available (ai_brain={ai_brain})")

    # Traditional indicator analysis (fallback or when AI is disabled)
    # NOTE: All indicators already calculated above for AI use

    # WEIGHTED SIGNAL SCORING SYSTEM (Ultra Powerful!)
    call_score = 0.0
    put_score = 0.0

    # 1. Moving Average Crossover (Weight: 15%)
    if ema_fast_prev < ema_slow_prev and ema_fast > ema_slow:
        call_score += 15.0  # Golden cross - STRONG bullish
        add_log("📈 GOLDEN CROSS detected!")
    elif ema_fast_prev > ema_slow_prev and ema_fast < ema_slow:
        put_score += 15.0  # Death cross - STRONG bearish
        add_log("📉 DEATH CROSS detected!")
    elif ema_fast > ema_slow:
        call_score += 5.0  # Trend continuation
    else:
        put_score += 5.0  # Trend continuation

    # 2. RSI Analysis (Weight: 12%)
    if settings['rsi_enabled']:
        rsi_upper = settings['rsi_upper']
        rsi_lower = 100 - rsi_upper

        if rsi < 20:  # EXTREME oversold
            call_score += 12.0
            add_log(f"💪 RSI EXTREME OVERSOLD: {rsi:.1f}")
        elif rsi < rsi_lower:  # Oversold
            call_score += 8.0
        elif rsi > 80:  # EXTREME overbought
            put_score += 12.0
            add_log(f"💪 RSI EXTREME OVERBOUGHT: {rsi:.1f}")
        elif rsi > rsi_upper:  # Overbought
            put_score += 8.0

        # RSI Divergence bonus (momentum shift)
        if 45 < rsi < 55:  # Neutral zone - trend may reverse
            pass  # No points in neutral

    # 3. Bollinger Bands (Weight: 10%)
    bb_range = upper_bb - lower_bb
    bb_position = (current_price - lower_bb) / bb_range if bb_range > 0 else 0.5

    if bb_position <= 0.1:  # Price at/below lower band
        call_score += 10.0
        add_log(f"🎯 Price at LOWER BB - Bounce expected!")
    elif bb_position <= 0.3:  # Near lower band
        call_score += 6.0
    elif bb_position >= 0.9:  # Price at/above upper band
        put_score += 10.0
        add_log(f"🎯 Price at UPPER BB - Pullback expected!")
    elif bb_position >= 0.7:  # Near upper band
        put_score += 6.0

    # BB Squeeze detection (low volatility = breakout coming)
    bb_width = (bb_range / middle_bb) * 100
    if bb_width < 2.0:  # Tight squeeze
        add_log(f"⚡ BB SQUEEZE detected - Breakout imminent!")
        # Wait for direction confirmation from other indicators

    # 4. Support/Resistance (Weight: 8%)
    if support and resistance:
        price_range = resistance - support
        support_distance = (current_price - support) / price_range if price_range > 0 else 0.5

        if support_distance <= 0.15:  # Very near support
            call_score += 8.0
            add_log(f"🛡️ Price near SUPPORT level!")
        elif support_distance <= 0.3:  # Near support
            call_score += 4.0
        elif support_distance >= 0.85:  # Very near resistance
            put_score += 8.0
            add_log(f"🧱 Price near RESISTANCE level!")
        elif support_distance >= 0.7:  # Near resistance
            put_score += 4.0

    # 6. Volatility Filter (ATR)
    if atr:
        avg_price = sum([c[2] for c in candles[-20:]]) / 20
        volatility_percent = (atr / avg_price) * 100

        # Skip trading in extremely volatile conditions
        if volatility_percent > 5:  # Too volatile
            add_log(f"⚠️ High volatility: {volatility_percent:.2f}% - Skipping")
            return None

    # 7. Trend Strength (Weight: 7%)
    if ema_fast > ema_slow:
        trend_strength = ((ema_fast - ema_slow) / ema_slow) * 100
        if trend_strength > 1.0:  # STRONG uptrend
            call_score += 7.0
        elif trend_strength > 0.3:  # Moderate uptrend
            call_score += 4.0
    else:
        trend_strength = ((ema_slow - ema_fast) / ema_fast) * 100
        if trend_strength > 1.0:  # STRONG downtrend
            put_score += 7.0
        elif trend_strength > 0.3:  # Moderate downtrend
            put_score += 4.0

    # 8. 🚀 MACD ULTRA POWER (Weight: 15%)
    if macd_line is not None and macd_signal is not None and macd_histogram is not None:
        # MACD Crossover
        if macd_line > macd_signal and macd_histogram > 0:
            call_score += 15.0
            add_log("🚀 MACD BULLISH CROSSOVER!")
        elif macd_line < macd_signal and macd_histogram < 0:
            put_score += 15.0
            add_log("🚀 MACD BEARISH CROSSOVER!")

        # Histogram strength
        if abs(macd_histogram) > 0.0001:  # Strong momentum
            if macd_histogram > 0:
                call_score += 5.0
            else:
                put_score += 5.0

    # 9. 💎 STOCHASTIC POWER (Weight: 12%)
    if stoch_k is not None and stoch_d is not None:
        if stoch_k < 20 and stoch_d < 20:  # EXTREME oversold
            call_score += 12.0
            add_log(f"💎 STOCHASTIC EXTREME OVERSOLD: K={stoch_k:.1f}")
        elif stoch_k < 30:  # Oversold
            call_score += 8.0

        if stoch_k > 80 and stoch_d > 80:  # EXTREME overbought
            put_score += 12.0
            add_log(f"💎 STOCHASTIC EXTREME OVERBOUGHT: K={stoch_k:.1f}")
        elif stoch_k > 70:  # Overbought
            put_score += 8.0

        # Stochastic Crossover
        if stoch_k > stoch_d and stoch_k < 50:  # Bullish cross in lower zone
            call_score += 6.0
        elif stoch_k < stoch_d and stoch_k > 50:  # Bearish cross in upper zone
            put_score += 6.0

    # 10. ⚡ SUPERTREND ULTRA (Weight: 18%)
    if supertrend_direction != 0:
        if supertrend_direction == 1:  # Bullish trend
            call_score += 18.0
            add_log("⚡ SUPERTREND: BULLISH!")
        elif supertrend_direction == -1:  # Bearish trend
            put_score += 18.0
            add_log("⚡ SUPERTREND: BEARISH!")

    # 11. 🎯 CANDLESTICK PATTERNS (Weight: Variable)
    if pattern_name and pattern_direction != 'neutral':
        pattern_score = pattern_strength * 2.0  # Multiply strength for weight
        if pattern_direction == 'call':
            call_score += pattern_score
            add_log(f"🎯 PATTERN: {pattern_name} (Bullish +{pattern_score})")
        elif pattern_direction == 'put':
            put_score += pattern_score
            add_log(f"🎯 PATTERN: {pattern_name} (Bearish +{pattern_score})")

    # === ULTRA DECISION LOGIC ===
    total_score = call_score + put_score
    if total_score == 0:
        return None

    # Calculate confidence percentage
    call_confidence = (call_score / total_score) * 100 if total_score > 0 else 0
    put_confidence = (put_score / total_score) * 100 if total_score > 0 else 0

    # Minimum score threshold (adjustable)
    min_score_threshold = 40.0  # Out of 100 possible points

    # Strong directional bias required
    score_diff = abs(call_score - put_score)

    # Determine traditional decision
    trad_action = None
    trad_confidence = 0
    trad_reason = ""

    if call_score > put_score and call_score >= min_score_threshold and score_diff >= 15:
        trad_action = 'call'
        trad_confidence = call_confidence
        trad_reason = f'🎯 Ultra Score: {call_score:.1f}/100 ({call_confidence:.0f}% conf)'
        add_log(f"✅ CALL Signal - Score: {call_score:.1f} vs {put_score:.1f} | Confidence: {call_confidence:.1f}%")
    elif put_score > call_score and put_score >= min_score_threshold and score_diff >= 15:
        trad_action = 'put'
        trad_confidence = put_confidence
        trad_reason = f'🎯 Ultra Score: {put_score:.1f}/100 ({put_confidence:.0f}% conf)'
        add_log(f"✅ PUT Signal - Score: {put_score:.1f} vs {call_score:.1f} | Confidence: {put_confidence:.1f}%")
    else:
        trad_action = 'hold'
        trad_confidence = 0
        trad_reason = f'No clear signal - CALL: {call_score:.1f} | PUT: {put_score:.1f}'
        add_log(f"⚖️ {trad_reason}")

    # === ULTRA COMBINED STRATEGY DECISION ===
    # Check if we have stored AI decision for combination
    if 'ai_decision_stored' in locals() and ai_decision_stored:
        decision_mode = settings.get('decision_mode', 'ultra_safe')
        ai_action = ai_decision_stored['action']
        ai_confidence = ai_decision_stored['confidence']
        ai_reason = ai_decision_stored['reason']

        if decision_mode == 'ultra_safe':
            # ULTRA SAFE: Both AI and Traditional must agree
            if ai_action == trad_action and ai_action != 'hold':
                combined_conf = (ai_confidence + trad_confidence) / 2
                add_log(f"🎯 ULTRA CONSENSUS! AI({ai_confidence:.0f}%) + Traditional({trad_confidence:.0f}%) = {combined_conf:.0f}%")
                return ai_action, f'🎯 ULTRA SAFE CONSENSUS: {ai_action.upper()} @ {combined_conf:.0f}%'
            else:
                add_log(f"⚠️ ULTRA SAFE: AI({ai_action}) vs Traditional({trad_action}) - HOLDING for safety")
                return None

        elif decision_mode == 'ai_priority':
            # AI Priority: AI decides, Traditional validates
            if ai_confidence >= 80 and ai_action != 'hold':
                # High AI confidence, check Traditional doesn't strongly disagree
                if trad_action == ai_action or trad_action == 'hold':
                    add_log(f"✅ AI PRIORITY: High AI confidence({ai_confidence:.0f}%), Traditional agrees/neutral")
                    return ai_action, f'AI Priority: {ai_action.upper()} @ {ai_confidence:.0f}%'
                else:
                    add_log(f"⚠️ AI PRIORITY: AI confident but Traditional disagrees - HOLDING")
                    return None
            elif ai_action != 'hold' and trad_action == ai_action:
                # Lower AI confidence, need Traditional support
                combined_conf = (ai_confidence + trad_confidence) / 2
                add_log(f"✅ AI PRIORITY: AI + Traditional aligned @ {combined_conf:.0f}%")
                return ai_action, f'AI Priority (validated): {ai_action.upper()} @ {combined_conf:.0f}%'
            else:
                add_log(f"⚠️ AI PRIORITY: No strong aligned signal")
                return None

        elif decision_mode == 'traditional_priority':
            # Traditional Priority: Traditional decides, AI validates
            if trad_confidence >= 70 and trad_action != 'hold':
                # High Traditional confidence, check AI doesn't strongly disagree
                if ai_action == trad_action or ai_action == 'hold':
                    add_log(f"✅ TRADITIONAL PRIORITY: Traditional confident, AI agrees/neutral")
                    return trad_action, f'Traditional Priority: {trad_action.upper()} @ {trad_confidence:.0f}%'
                elif ai_confidence < 60:  # AI not very confident in disagreement
                    add_log(f"✅ TRADITIONAL PRIORITY: Traditional strong, AI weak disagreement")
                    return trad_action, trad_reason
                else:
                    add_log(f"⚠️ TRADITIONAL PRIORITY: Strong disagreement - HOLDING")
                    return None
            elif trad_action != 'hold' and ai_action == trad_action:
                combined_conf = (ai_confidence + trad_confidence) / 2
                add_log(f"✅ TRADITIONAL PRIORITY: Both aligned @ {combined_conf:.0f}%")
                return trad_action, f'Traditional Priority (AI validated): {trad_action.upper()} @ {combined_conf:.0f}%'
            else:
                return None

        elif decision_mode == 'aggressive':
            # Aggressive: AI OR Traditional (pick highest confidence)
            if ai_action != 'hold' and trad_action == 'hold':
                add_log(f"✅ AGGRESSIVE: AI triggers ({ai_confidence:.0f}%)")
                return ai_action, f'Aggressive (AI): {ai_action.upper()} @ {ai_confidence:.0f}%'
            elif trad_action != 'hold' and ai_action == 'hold':
                add_log(f"✅ AGGRESSIVE: Traditional triggers ({trad_confidence:.0f}%)")
                return trad_action, f'Aggressive (Traditional): {trad_action.upper()} @ {trad_confidence:.0f}%'
            elif ai_action != 'hold' and trad_action != 'hold':
                if ai_action == trad_action:
                    combined_conf = (ai_confidence + trad_confidence) / 2
                    add_log(f"✅ AGGRESSIVE: Both agree! Combined {combined_conf:.0f}%")
                    return ai_action, f'Aggressive (CONSENSUS): {ai_action.upper()} @ {combined_conf:.0f}%'
                else:
                    # Pick highest confidence
                    if ai_confidence >= trad_confidence:
                        add_log(f"✅ AGGRESSIVE: AI higher conf ({ai_confidence:.0f}% > {trad_confidence:.0f}%)")
                        return ai_action, f'Aggressive (AI higher): {ai_action.upper()} @ {ai_confidence:.0f}%'
                    else:
                        add_log(f"✅ AGGRESSIVE: Traditional higher conf ({trad_confidence:.0f}% > {ai_confidence:.0f}%)")
                        return trad_action, f'Aggressive (Trad higher): {trad_action.upper()} @ {trad_confidence:.0f}%'
            else:
                return None

    # Traditional only mode or no AI decision stored
    elif settings.get('decision_mode') == 'traditional_only':
        if trad_action != 'hold':
            return trad_action, trad_reason
        return None
    else:
        # Default behavior (legacy compatibility)
        if trad_action != 'hold':
            return trad_action, trad_reason
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


def check_trade_limits():
    """Check if we're within configured trade frequency limits"""
    global TRADE_HISTORY, LAST_TRADE_TIME, CONSECUTIVE_TRADES, LAST_TRADE_RESULT

    if not settings.get('trade_limits_enabled', True):
        return True, "Limits disabled"

    current_time = datetime.now()

    # Check cooldown periods
    if LAST_TRADE_TIME:
        time_since_last = (current_time - LAST_TRADE_TIME).total_seconds()

        # Cooldown after loss
        if settings.get('cooldown_after_loss_enabled', True) and LAST_TRADE_RESULT == 'LOSS' and time_since_last < settings.get('cooldown_after_loss', 60):
            remaining = settings['cooldown_after_loss'] - int(time_since_last)
            return False, f"Cooldown after loss ({remaining}s remaining)"

        # Cooldown after win
        if settings.get('cooldown_after_win_enabled', True) and LAST_TRADE_RESULT == 'WIN' and time_since_last < settings.get('cooldown_after_win', 30):
            remaining = settings['cooldown_after_win'] - int(time_since_last)
            return False, f"Cooldown after win ({remaining}s remaining)"

    # Check consecutive trades limit
    if settings.get('max_consecutive_trades_enabled', True) and CONSECUTIVE_TRADES >= settings.get('max_consecutive_trades', 3):
        if LAST_TRADE_TIME:
            break_elapsed = (current_time - LAST_TRADE_TIME).total_seconds()
            break_needed = settings.get('break_duration', 120)
            if break_elapsed < break_needed:
                remaining = int(break_needed - break_elapsed)
                return False, f"Break needed after {CONSECUTIVE_TRADES} consecutive trades ({remaining}s remaining)"
            else:
                # Break is over, reset counter
                CONSECUTIVE_TRADES = 0

    # Clean old trades from history (older than 60 minutes)
    TRADE_HISTORY = [(t, a) for t, a in TRADE_HISTORY if (current_time - t).total_seconds() < 3600]

    # Check time-window limits
    limits = [
        (5, 'trade_limit_5min_enabled', 'trade_limit_5min'),
        (10, 'trade_limit_10min_enabled', 'trade_limit_10min'),
        (20, 'trade_limit_20min_enabled', 'trade_limit_20min'),
        (30, 'trade_limit_30min_enabled', 'trade_limit_30min'),
        (60, 'trade_limit_60min_enabled', 'trade_limit_60min')
    ]

    for minutes, enabled_key, limit_key in limits:
        if settings.get(enabled_key, True):  # Check if this specific limit is enabled
            max_trades = settings.get(limit_key, 999)  # Default to high number if not set
            if max_trades > 0:  # Only check if limit is set
                window_start = current_time - timedelta(minutes=minutes)
                recent_trades = [t for t, _ in TRADE_HISTORY if t >= window_start]

                if len(recent_trades) >= max_trades:
                    # Find when the oldest trade in this window will expire
                    oldest_in_window = min(recent_trades)
                    wait_time = int((oldest_in_window + timedelta(minutes=minutes) - current_time).total_seconds())
                    return False, f"Limit reached: {max_trades} trades in {minutes}min (wait {wait_time}s)"

    return True, "Within limits"


async def create_order(driver, action, asset, reason=""):
    """Create trading order"""
    global ACTIONS, BOT_TRADE_IDS, TRADE_HISTORY, LAST_TRADE_TIME, CONSECUTIVE_TRADES

    if ACTIONS.get(asset) and ACTIONS[asset] + timedelta(seconds=PERIOD * 2) > datetime.now():
        return False

    # Check trade frequency limits
    can_trade, limit_reason = check_trade_limits()
    if not can_trade:
        add_log(f"⏳ Trade delayed: {limit_reason}")
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

        # Update trade frequency tracking
        TRADE_HISTORY.append((datetime.now(), asset))
        LAST_TRADE_TIME = datetime.now()
        CONSECUTIVE_TRADES += 1

        add_log(f"{'📈' if action == 'call' else '📉'} {action.upper()} on {asset} - {reason}")
        return True
    except Exception as e:
        add_log(f"❌ Can't create order: {e}")
        return False


async def check_deposit(driver):
    """Monitor deposit and update balance with chart data"""
    global INITIAL_DEPOSIT, bot_state

    try:
        deposit_elem = driver.find_element(By.CSS_SELECTOR,
            'body > div.wrapper > div.wrapper__top > header > div.right-block.js-right-block > div.right-block__item.js-drop-down-modal-open > div > div.balance-info-block__data > div.balance-info-block__balance > span')
        deposit = float(deposit_elem.text.replace(',', ''))

        # Update bot state balance
        old_balance = bot_state['balance']
        bot_state['balance'] = deposit

        if INITIAL_DEPOSIT is None:
            INITIAL_DEPOSIT = deposit
            bot_state['initial_balance'] = deposit

            # Add initial chart data point
            from datetime import datetime
            if len(bot_state['chart_data']['balances']) == 0:
                bot_state['chart_data']['times'].append(datetime.now())
                bot_state['chart_data']['balances'].append(deposit)
                add_log(f"📊 Initial balance: ${deposit:.2f}")

        # Update chart data if balance changed significantly (more than $0.01)
        elif abs(old_balance - deposit) > 0.01:
            from datetime import datetime
            bot_state['chart_data']['times'].append(datetime.now())
            bot_state['chart_data']['balances'].append(deposit)

            # Keep only last 200 data points
            if len(bot_state['chart_data']['balances']) > 200:
                bot_state['chart_data']['times'] = bot_state['chart_data']['times'][-200:]
                bot_state['chart_data']['balances'] = bot_state['chart_data']['balances'][-200:]

    except:
        pass


async def check_recent_trades(driver):
    """Check recent trades for wins/losses - ONLY count bot's trades"""
    global bot_state, LAST_TRADE_ID, BOT_TRADE_IDS, LAST_TRADE_RESULT

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

                        trade_info = {
                            'asset': asset,
                            'action': action,
                            'result': 'WIN',
                            'profit': profit,
                            'time': trade_time
                        }
                        bot_state['trades'].insert(0, trade_info)

                        # Update trade result for frequency tracking
                        LAST_TRADE_RESULT = 'WIN'

                        # Update chart data
                        from datetime import datetime
                        bot_state['chart_data']['times'].append(datetime.now())
                        bot_state['chart_data']['balances'].append(bot_state['balance'])
                        bot_state['chart_data']['trades'].append(trade_info)

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

                        # 🚀 ULTRA SYSTEMS: Record trade in performance tracker and journal
                        if ULTRA_SYSTEMS_AVAILABLE:
                            try:
                                # Record custom strategy result if one was used
                                if ACTIVE_STRATEGY_ID and strategy_builder:
                                    strategy_builder.record_strategy_result(ACTIVE_STRATEGY_ID, 'win', profit)
                                    print(f"📊 Custom Strategy '{ACTIVE_STRATEGY_NAME}' result recorded: WIN +${profit:.2f}")

                                # 🕯️ Record pattern trade result if pattern was used
                                if pattern_recognizer and pattern_type and 'pattern_quality' in locals():
                                    pattern_recognizer.record_pattern_trade(
                                        pattern_type=pattern_type,
                                        result='win',
                                        profit=profit,
                                        quality_score=pattern_quality,
                                        indicators={'rsi': ai_indicators.get('rsi', 50), 'regime': market_regime}
                                    )
                                    print(f"🕯️ Pattern '{pattern_type}' WIN recorded (Quality: {pattern_quality}%)")

                                # 🎰 Record OTC trade result if OTC signal was used
                                if otc_strategy and is_otc_market and otc_signal and 'otc_details' in locals():
                                    detected_patterns = [k for k in otc_details.keys() if k != 'final_decision']
                                    pattern_type_str = ', '.join(detected_patterns) if detected_patterns else 'combined'
                                    otc_strategy.record_trade_result(otc_signal, 'WIN', pattern_type_str)
                                    print(f"🎰 OTC Anomaly '{pattern_type_str}' WIN recorded (Confidence: {otc_confidence*100:.0f}%)")

                                # 🔄 Record Reversal trade result if reversal signal was used
                                if reversal_catcher and reversal_signal and 'reversal_details' in locals():
                                    confirming_inds = reversal_details.get('indicators', [])
                                    ind_names = [ind['name'] for ind in confirming_inds]
                                    reversal_catcher.record_trade_result(reversal_signal, 'WIN', ind_names)
                                    print(f"🔄 Reversal '{reversal_signal}' WIN recorded ({reversal_details.get('total_confirming', 0)}/7 indicators, Confidence: {reversal_confidence*100:.0f}%)")

                                if performance_tracker:
                                    performance_tracker.record_trade({
                                        'timestamp': datetime.now().isoformat(),
                                        'asset': asset,
                                        'action': action.lower(),
                                        'result': 'win',
                                        'profit': profit,
                                        'ai_confidence': ai_confidence if 'ai_confidence' in locals() else 0,
                                        'market_regime': market_regime if 'market_regime' in locals() else 'unknown',
                                        'strategy': ACTIVE_STRATEGY_NAME if ACTIVE_STRATEGY_NAME else settings.get('decision_mode', 'traditional'),
                                        'entry_price': current_price if 'current_price' in locals() else 0,
                                        'indicators': ai_indicators if 'ai_indicators' in locals() else {}
                                    })

                                if trade_journal:
                                    journal_data = {
                                        'result': 'win',
                                        'action': action.lower(),
                                        'market_regime': market_regime if 'market_regime' in locals() else 'unknown',
                                        'indicators': ai_indicators if 'ai_indicators' in locals() else {}
                                    }
                                    analysis = trade_journal.analyze_trade(journal_data)
                                    trade_journal.add_entry(journal_data, analysis)
                            except Exception as e:
                                print(f"⚠️ ULTRA systems recording error: {e}")

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

                            trade_info = {
                                'asset': asset,
                                'action': action,
                                'result': 'LOSS',
                                'profit': -stake,
                                'time': trade_time
                            }
                            bot_state['trades'].insert(0, trade_info)

                            # Update trade result for frequency tracking
                            LAST_TRADE_RESULT = 'LOSS'

                            # Update chart data
                            from datetime import datetime
                            bot_state['chart_data']['times'].append(datetime.now())
                            bot_state['chart_data']['balances'].append(bot_state['balance'])
                            bot_state['chart_data']['trades'].append(trade_info)

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

                            # 🚀 ULTRA SYSTEMS: Record trade in performance tracker and journal
                            if ULTRA_SYSTEMS_AVAILABLE:
                                try:
                                    # Record custom strategy result if one was used
                                    if ACTIVE_STRATEGY_ID and strategy_builder:
                                        strategy_builder.record_strategy_result(ACTIVE_STRATEGY_ID, 'loss', -stake)
                                        print(f"📊 Custom Strategy '{ACTIVE_STRATEGY_NAME}' result recorded: LOSS -${stake:.2f}")

                                    # 🕯️ Record pattern trade result if pattern was used
                                    if pattern_recognizer and pattern_type and 'pattern_quality' in locals():
                                        pattern_recognizer.record_pattern_trade(
                                            pattern_type=pattern_type,
                                            result='loss',
                                            profit=-stake,
                                            quality_score=pattern_quality,
                                            indicators={'rsi': ai_indicators.get('rsi', 50), 'regime': market_regime}
                                        )
                                        print(f"🕯️ Pattern '{pattern_type}' LOSS recorded (Quality: {pattern_quality}%)")

                                    # 🎰 Record OTC trade result if OTC signal was used
                                    if otc_strategy and is_otc_market and otc_signal and 'otc_details' in locals():
                                        detected_patterns = [k for k in otc_details.keys() if k != 'final_decision']
                                        pattern_type_str = ', '.join(detected_patterns) if detected_patterns else 'combined'
                                        otc_strategy.record_trade_result(otc_signal, 'LOSS', pattern_type_str)
                                        print(f"🎰 OTC Anomaly '{pattern_type_str}' LOSS recorded (Confidence: {otc_confidence*100:.0f}%)")

                                    # 🔄 Record Reversal trade result if reversal signal was used
                                    if reversal_catcher and reversal_signal and 'reversal_details' in locals():
                                        confirming_inds = reversal_details.get('indicators', [])
                                        ind_names = [ind['name'] for ind in confirming_inds]
                                        reversal_catcher.record_trade_result(reversal_signal, 'LOSS', ind_names)
                                        print(f"🔄 Reversal '{reversal_signal}' LOSS recorded ({reversal_details.get('total_confirming', 0)}/7 indicators, Confidence: {reversal_confidence*100:.0f}%)")

                                    if performance_tracker:
                                        performance_tracker.record_trade({
                                            'timestamp': datetime.now().isoformat(),
                                            'asset': asset,
                                            'action': action.lower(),
                                            'result': 'loss',
                                            'profit': -stake,
                                            'ai_confidence': ai_confidence if 'ai_confidence' in locals() else 0,
                                            'market_regime': market_regime if 'market_regime' in locals() else 'unknown',
                                            'strategy': ACTIVE_STRATEGY_NAME if ACTIVE_STRATEGY_NAME else settings.get('decision_mode', 'traditional'),
                                            'entry_price': current_price if 'current_price' in locals() else 0,
                                            'indicators': ai_indicators if 'ai_indicators' in locals() else {}
                                        })

                                    if trade_journal:
                                        journal_data = {
                                            'result': 'loss',
                                            'action': action.lower(),
                                            'market_regime': market_regime if 'market_regime' in locals() else 'unknown',
                                            'indicators': ai_indicators if 'ai_indicators' in locals() else {}
                                        }
                                        analysis = trade_journal.analyze_trade(journal_data)
                                        trade_journal.add_entry(journal_data, analysis)
                                except Exception as e:
                                    print(f"⚠️ ULTRA systems recording error: {e}")

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
        'trades': bot_state['trades'],
        'pattern_data': bot_state.get('pattern_data', {
            'pattern_type': None,
            'pattern_strength': 0,
            'pattern_quality': 0,
            'pattern_timeframe': '1m'
        })
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
    global settings, AI_ENABLED, ai_brain, optimizer
    try:
        new_settings = request.json
        settings.update(new_settings)

        # Update AI status if changed
        if 'ai_enabled' in new_settings:
            should_enable = new_settings['ai_enabled']
            settings['ai_enabled'] = should_enable

            if should_enable:
                # Try to initialize AI if not already initialized
                if not ai_brain:
                    print(f"🔄 AI not initialized, attempting to initialize...")
                    success = initialize_ai_system()
                    if success:
                        AI_ENABLED = True
                        add_log("🤖 AI System ENABLED - ULTRA SUPER POWERFUL MODE ACTIVATED!")
                        add_log("🚀 GPT-4 TRADING GOD ONLINE - 99% WIN RATE TARGET!")
                        print(f"✅ AI initialization successful, AI_ENABLED={AI_ENABLED}")
                    else:
                        AI_ENABLED = False
                        settings['ai_enabled'] = False  # Revert if initialization failed
                        add_log("❌ AI System failed to initialize - check console for details")
                        print(f"❌ AI initialization failed, returning error")
                        return jsonify({
                            'success': False,
                            'error': 'AI initialization failed. Check if ai_config.py exists in parent directory and OpenAI API key is valid.',
                            'details': 'Check server console for detailed error logs'
                        })
                else:
                    AI_ENABLED = True
                    add_log("🤖 AI System ENABLED - ULTRA SUPER POWERFUL MODE!")
                    if ai_brain:
                        ai_brain.load_patterns()
            else:
                AI_ENABLED = False
                add_log("🤖 AI System DISABLED - Using traditional indicators only")

        add_log(f"⚙️ Settings updated successfully")
        return jsonify({'success': True, 'message': 'Settings updated'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/ai-status', methods=['GET'])
def get_ai_status():
    """Get AI system status"""
    global AI_ENABLED, ai_brain

    # The actual current state
    ai_is_enabled = AI_ENABLED and ai_brain is not None

    # Get the active strategy
    current_strat = settings.get('active_strategy', 'AI_ENHANCED')
    if current_strat == 'AI_ENHANCED' and settings.get('ai_strategy'):
        current_strat = settings.get('ai_strategy', 'ULTRA_SCALPING')

    return jsonify({
        'ai_enabled': ai_is_enabled,
        'ai_available': ai_brain is not None,
        'patterns_learned': len(ai_brain.pattern_database) if ai_brain and hasattr(ai_brain, 'pattern_database') else 0,
        'current_strategy': current_strat,
        'ai_module_loaded': ai_brain is not None,
        'settings_enabled': settings.get('ai_enabled', False),
        'global_enabled': AI_ENABLED
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


@app.route('/api/chart-data', methods=['GET'])
def get_chart_data():
    """Get historical chart data for persistence"""
    return jsonify({
        'times': [t.isoformat() if hasattr(t, 'isoformat') else str(t) for t in bot_state['chart_data']['times']],
        'balances': bot_state['chart_data']['balances'],
        'trades': bot_state['chart_data']['trades'],
        'initial_balance': bot_state['initial_balance']
    })


# ========================================================================
# ULTRA SYSTEMS API ENDPOINTS
# ========================================================================

@app.route('/strategies')
def strategies_page():
    """Strategy Builder UI"""
    return render_template('strategies.html')


@app.route('/api/strategies/list', methods=['GET'])
def get_strategies_list():
    """Get all strategies"""
    if strategy_builder:
        return jsonify(strategy_builder.get_all_strategies())
    return jsonify({})


@app.route('/api/strategies/create', methods=['POST'])
def create_strategy():
    """Create a new strategy"""
    if not strategy_builder:
        return jsonify({'success': False, 'message': 'Strategy builder not available'})

    try:
        strategy_data = request.json
        success, message = strategy_builder.create_strategy(strategy_data)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/strategies/toggle/<strategy_id>', methods=['POST'])
def toggle_strategy(strategy_id):
    """Toggle strategy active state"""
    if not strategy_builder:
        return jsonify({'success': False})

    try:
        data = request.json
        active = data.get('active', False)
        success, message = strategy_builder.update_strategy(strategy_id, {'active': active})
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/strategies/delete/<strategy_id>', methods=['DELETE'])
def delete_strategy(strategy_id):
    """Delete a strategy"""
    if not strategy_builder:
        return jsonify({'success': False})

    try:
        success, message = strategy_builder.delete_strategy(strategy_id)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Run backtest on a strategy"""
    if not backtest_engine:
        return jsonify({'error': 'Backtest engine not available'})

    try:
        strategy_config = request.json

        # Load historical data
        historical_candles = backtest_engine.load_historical_data(limit=1000)

        if not historical_candles:
            return jsonify({'error': 'No historical data available. Need data in data_1m/ folder'})

        # Run backtest
        results = backtest_engine.backtest_strategy(
            strategy_config,
            historical_candles,
            initial_balance=100.0,
            payout_percent=85.0
        )

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/performance/stats', methods=['GET'])
def get_performance_stats():
    """Get performance statistics"""
    if not performance_tracker:
        return jsonify({'error': 'Performance tracker not available'})

    try:
        stats = performance_tracker.get_all_stats_summary()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/journal/recent', methods=['GET'])
def get_recent_journal():
    """Get recent trade journal entries"""
    if not trade_journal:
        return jsonify([])

    try:
        count = request.args.get('count', 20, type=int)
        entries = trade_journal.get_recent_entries(count)
        return jsonify(entries)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/journal/report', methods=['GET'])
def get_monthly_report():
    """Get monthly performance report"""
    if not trade_journal:
        return jsonify({'error': 'Trade journal not available'})

    try:
        report = trade_journal.generate_monthly_report()
        return jsonify({'report': report})
    except Exception as e:
        return jsonify({'error': str(e)})


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

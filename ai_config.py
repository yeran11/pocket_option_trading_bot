"""
AI Trading Configuration with OpenAI GPT-4 + Claude (Multi-Model)
Advanced market analysis and decision-making system
DUAL AI ENSEMBLE for maximum accuracy
"""

import openai
import numpy as np
from typing import Dict, List, Tuple
import json
from datetime import datetime, timedelta
import asyncio

# AI Configuration with multiple fallback options
import os

# Try multiple sources for API key:
# 1. First check environment variables (works in Replit Secrets and .env)
# 2. Then check if .env file exists and load it
# 3. Then check for hardcoded fallback (for local testing)

# Try to load from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, that's okay

# Get API keys from multiple sources
OPENAI_API_KEY = None
OPENAI_PROJECT_ID = None
CLAUDE_API_KEY = None
DEEPSEEK_API_KEY = None

# ========================================================================
# PRIORITY METHOD 0: Desktop Credentials (BEST for local development)
# ========================================================================
# This checks YOUR desktop home directory for a one-time credentials file
# Location: C:\Users\YourUsername\.openai_credentials (Windows)
#           ~/.openai_credentials (Mac/Linux)
#
# This is THE BEST method for your local machine because:
# - Set up ONCE on your desktop
# - Works for ALL your projects automatically
# - Never committed to git
# - Secure in your home directory
print("🔍 Checking for desktop credentials...")
try:
    import load_my_credentials
    # The import automatically loads credentials into os.environ
    # Check if it worked:
    if os.environ.get("OPENAI_API_KEY"):
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        OPENAI_PROJECT_ID = os.environ.get("OPENAI_PROJECT_ID")
        print("✅ LOADED OPENAI from desktop credentials")
    if os.environ.get("CLAUDE_API_KEY"):
        CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
        print("✅ LOADED CLAUDE from desktop credentials")
    if os.environ.get("DEEPSEEK_API_KEY"):
        DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
        print("✅ LOADED DEEPSEEK from desktop credentials")

    # Count available AI models
    ai_count = sum([bool(OPENAI_API_KEY), bool(CLAUDE_API_KEY), bool(DEEPSEEK_API_KEY)])
    if ai_count >= 3:
        print("✅✅✅ TRIPLE AI SYSTEM READY - GPT-4 + CLAUDE + DEEPSEEK ENSEMBLE! ✅✅✅")
    elif ai_count == 2:
        models = []
        if OPENAI_API_KEY: models.append("GPT-4")
        if CLAUDE_API_KEY: models.append("Claude")
        if DEEPSEEK_API_KEY: models.append("DeepSeek")
        print(f"✅✅ DUAL AI SYSTEM READY - {' + '.join(models)} ENSEMBLE! ✅✅")
    elif OPENAI_API_KEY:
        print("✅ Single AI mode (GPT-4 only)")
    elif CLAUDE_API_KEY:
        print("✅ Single AI mode (Claude only)")
    elif DEEPSEEK_API_KEY:
        print("✅ Single AI mode (DeepSeek only)")
except ImportError:
    # load_my_credentials.py not found - this is fine
    pass
except Exception as e:
    # Desktop credentials check failed - this is fine, will try other methods
    pass

# Method 1: Try to import from api_secrets.py (Good for Replit)
# Note: Named api_secrets to avoid conflict with Python's built-in secrets module
try:
    from api_secrets import OPENAI_API_KEY as SECRET_KEY, OPENAI_PROJECT_ID as SECRET_PROJECT_ID
    OPENAI_API_KEY = SECRET_KEY
    OPENAI_PROJECT_ID = SECRET_PROJECT_ID
    print("✅ Loaded API keys from api_secrets.py")
except ImportError:
    # api_secrets.py not found - trying other methods
    pass

# Method 2: Environment variables (Replit Secrets or .env loaded above)
if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_PROJECT_ID = os.environ.get("OPENAI_PROJECT_ID")
    if OPENAI_API_KEY:
        print("✅ Loaded OPENAI from environment variables")

if not CLAUDE_API_KEY:
    CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
    if CLAUDE_API_KEY:
        print("✅ Loaded CLAUDE from environment variables")

if not DEEPSEEK_API_KEY:
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
    if DEEPSEEK_API_KEY:
        print("✅ Loaded DEEPSEEK from environment variables")

# Method 3: If still None, try direct .env file read (backup method)
if not OPENAI_API_KEY or not CLAUDE_API_KEY or not DEEPSEEK_API_KEY:
    try:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY=') and not OPENAI_API_KEY:
                        OPENAI_API_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                        print(f"✅ Loaded OPENAI API key from .env file (length: {len(OPENAI_API_KEY)})")
                    elif line.startswith('OPENAI_PROJECT_ID=') and not OPENAI_PROJECT_ID:
                        OPENAI_PROJECT_ID = line.split('=', 1)[1].strip().strip('"').strip("'")
                    elif line.startswith('CLAUDE_API_KEY=') and not CLAUDE_API_KEY:
                        CLAUDE_API_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                        print(f"✅ Loaded CLAUDE API key from .env file (length: {len(CLAUDE_API_KEY)})")
                    elif line.startswith('DEEPSEEK_API_KEY=') and not DEEPSEEK_API_KEY:
                        DEEPSEEK_API_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                        print(f"✅ Loaded DEEPSEEK API key from .env file (length: {len(DEEPSEEK_API_KEY)})")
    except Exception as e:
        # Could not read .env file - that's okay
        pass

# Method 4: Fallback - if still nothing found
if not OPENAI_API_KEY:
    # No API keys configured - bot will work in traditional mode
    OPENAI_API_KEY = None
    OPENAI_PROJECT_ID = None

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Validation
if not any([OPENAI_API_KEY, CLAUDE_API_KEY, DEEPSEEK_API_KEY]):
    print("ℹ️  INFO: No AI API keys configured - Bot will run with traditional indicators only")
    print("   To enable AI features, set OPENAI_API_KEY, CLAUDE_API_KEY, or DEEPSEEK_API_KEY in:")
    print("   - Desktop credentials (~/.openai_credentials)")
    print("   - Environment variables")
    print("   - .env file")
    print("✅ Bot ready - AI features disabled (traditional trading mode)")
else:
    if OPENAI_API_KEY:
        print(f"✅ OpenAI API key loaded successfully (ending in ...{OPENAI_API_KEY[-4:]})")
    if CLAUDE_API_KEY:
        print(f"✅ Claude API key loaded successfully (ending in ...{CLAUDE_API_KEY[-4:]})")
    if DEEPSEEK_API_KEY:
        print(f"✅ DeepSeek API key loaded successfully (ending in ...{DEEPSEEK_API_KEY[-4:]})")
    print("✅ AI features ENABLED")

# Advanced Indicator Configuration
INDICATOR_CONFIG = {
    "EMA": {
        "enabled": True,
        "weight": 0.15,
        "periods": [9, 21],
        "cross_detection": True
    },
    "RSI": {
        "enabled": True,
        "weight": 0.20,
        "period": 14,
        "overbought": 70,
        "oversold": 30,
        "divergence_detection": True
    },
    "BOLLINGER": {
        "enabled": True,
        "weight": 0.15,
        "period": 20,
        "std_dev": 2,
        "squeeze_detection": True
    },
    "MACD": {
        "enabled": True,
        "weight": 0.15,
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9,
        "histogram_analysis": True
    },
    "STOCHASTIC": {
        "enabled": True,
        "weight": 0.10,
        "k_period": 14,
        "d_period": 3,
        "overbought": 80,
        "oversold": 20
    },
    "ATR": {
        "enabled": True,
        "weight": 0.10,
        "period": 14,
        "volatility_filter": True
    },
    "VOLUME": {
        "enabled": True,
        "weight": 0.15,
        "volume_ma_period": 20,
        "volume_surge_threshold": 1.5
    },
    "SUPERTREND": {
        "enabled": True,
        "weight": 0.20,
        "atr_period": 10,
        "multiplier": 3,
        "change_detection": True,
        "use_close": True
    },
    "ADX": {
        "enabled": True,
        "weight": 0.15,
        "period": 14,
        "threshold": 25,
        "use_di_cross": True
    },
    "HEIKIN_ASHI": {
        "enabled": True,
        "weight": 0.15,
        "smooth": True,
        "doji_detection": True,
        "color_change_alerts": True,
        "consecutive_candles": 3
    },
    "VWAP": {
        "enabled": True,
        "weight": 0.25,
        "std_bands": True,
        "band_mult_1": 1,
        "band_mult_2": 2,
        "reset_period": "daily",
        "anchored": True,
        "volume_confirm": True,
        "deviation_alert": 2
    },
    "FIBONACCI": {
        "enabled": False,
        "weight": 0.10,
        "auto_levels": True,
        "retracement_levels": [0.236, 0.382, 0.5, 0.618, 0.786]
    },
    "ICHIMOKU": {
        "enabled": False,
        "weight": 0.10,
        "tenkan_period": 9,
        "kijun_period": 26,
        "senkou_span_b_period": 52
    }
}

# ULTRA SUPER POWERFUL AI Trading Strategies - MAXIMUM AGGRESSION
AI_STRATEGIES = {
    "ULTRA_SCALPING": {
        "enabled": True,
        "min_confidence": 50,  # ULTRA aggressive - take more trades
        "timeframe": "1m",
        "max_trades_per_hour": 60,  # MAXIMUM trades
        "risk_per_trade": 3.0,  # Higher risk for ULTRA rewards
        "take_profit": 95,
        "stop_loss": 30  # Tighter stop for quick exits
    },
    "TREND_FOLLOWING": {
        "enabled": True,
        "min_confidence": 45,  # SUPER aggressive entries
        "timeframe": "5m",
        "max_trades_per_hour": 40,
        "risk_per_trade": 5.0,  # MAXIMUM risk appetite
        "take_profit": 300,
        "stop_loss": 40
    },
    "REVERSAL_TRADING": {
        "enabled": True,
        "min_confidence": 55,  # More reversal catches
        "timeframe": "1m",
        "max_trades_per_hour": 50,
        "risk_per_trade": 4.0,
        "take_profit": 200,
        "stop_loss": 35
    },
    "VOLATILITY_BREAKOUT": {
        "enabled": True,
        "min_confidence": 60,  # Catch all breakouts
        "timeframe": "1m",
        "max_trades_per_hour": 45,
        "risk_per_trade": 8.0,  # ULTRA MAXIMUM aggressive
        "take_profit": 500,  # HUGE targets
        "stop_loss": 50
    },
    "ULTRA_AI_HYBRID": {
        "enabled": True,
        "min_confidence": 40,  # HYPER aggressive - trust the AI
        "timeframe": "1m",
        "max_trades_per_hour": 100,  # UNLIMITED POWER
        "risk_per_trade": 6.0,
        "take_profit": 400,
        "stop_loss": 30
    },
    "QUANTUM_SURGE": {  # NEW ULTRA STRATEGY
        "enabled": True,
        "min_confidence": 35,  # QUANTUM aggressive
        "timeframe": "1m",
        "max_trades_per_hour": 120,  # 2 trades per minute!
        "risk_per_trade": 10.0,  # MAXIMUM POWER
        "take_profit": 1000,  # MOON TARGET
        "stop_loss": 25  # Super tight
    }
}

# Pattern Recognition Database
WINNING_PATTERNS = {}  # Will be populated with successful trade patterns

# Import performance tracker for AI calibration and context
try:
    from performance_tracker import get_tracker
    PERFORMANCE_TRACKER_AVAILABLE = True
except ImportError:
    PERFORMANCE_TRACKER_AVAILABLE = False
    print("⚠️ Performance tracker not available")

# Import pattern recognition system for candlestick patterns
try:
    from pattern_recognition import get_recognizer
    PATTERN_RECOGNITION_AVAILABLE = True
    print("✅ Pattern Recognition System loaded - Engulfing, Doji, Hammer, etc.")
except ImportError:
    PATTERN_RECOGNITION_AVAILABLE = False
    print("⚠️ Pattern recognition not available")

# Market Analysis System
class AITradingBrain:
    def __init__(self):
        self.performance_history = []
        self.pattern_database = {}
        self.current_market_state = {}
        self.performance_tracker = get_tracker() if PERFORMANCE_TRACKER_AVAILABLE else None
        self.pattern_recognizer = get_recognizer() if PATTERN_RECOGNITION_AVAILABLE else None

    async def analyze_with_gpt4(self, market_data: Dict, indicators: Dict) -> Tuple[str, float, str, int]:
        """
        Use GPT-4 to analyze market conditions and provide trading decision
        Returns: (action, confidence, reasoning, expiry_seconds)
        """
        try:
            # Prepare market context for GPT-4
            prompt = self._build_analysis_prompt(market_data, indicators)

            response = await self._call_gpt4(prompt)

            # Parse GPT-4 response
            decision = self._parse_gpt4_response(response)

            return decision

        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return "hold", 0.0, "AI analysis failed", 60

    def _build_analysis_prompt(self, market_data: Dict, indicators: Dict) -> str:
        """Build ULTRA POWERFUL prompt with ALL indicators + patterns + trade history"""

        # Extract chart pattern if present
        pattern_info = ""
        if indicators.get('pattern_name'):
            strength = indicators.get('pattern_strength', 0)
            direction = indicators.get('pattern_direction', 'neutral')
            pattern_info = f"\n📊 CHART PATTERN DETECTED: {indicators['pattern_name']} (Strength: {strength}/3) → {direction.upper()} SIGNAL"

        # Extract recent trade history if present
        trade_history = ""
        recent_trades = market_data.get('recent_trades', [])
        if recent_trades:
            wins = sum(1 for t in recent_trades if t.get('result') == 'WIN')
            losses = len(recent_trades) - wins
            last_5 = recent_trades[-5:] if len(recent_trades) >= 5 else recent_trades
            last_5_str = " → ".join([t.get('result', '?')[0] for t in last_5])
            trade_history = f"\n📈 LAST {len(recent_trades)} TRADES: {wins}W/{losses}L | Last 5: {last_5_str}"

        # MACD signal interpretation
        macd_line = indicators.get('macd_line', 0)
        macd_signal = indicators.get('macd_signal_line', 0)
        macd_histogram = indicators.get('macd_histogram', 0)
        macd_status = "BULLISH" if macd_histogram > 0 else "BEARISH" if macd_histogram < 0 else "NEUTRAL"
        macd_cross = ""
        if macd_line and macd_signal:
            if macd_line > macd_signal and macd_histogram > 0:
                macd_cross = "💎 MACD BULLISH CROSS"
            elif macd_line < macd_signal and macd_histogram < 0:
                macd_cross = "💀 MACD BEARISH CROSS"

        # Stochastic interpretation
        stoch_k = indicators.get('stochastic_k', 50)
        stoch_d = indicators.get('stochastic_d', 50)
        stoch_signal = "OVERSOLD" if stoch_k < 20 else "OVERBOUGHT" if stoch_k > 80 else "NEUTRAL"

        # ATR volatility
        atr = indicators.get('atr', 0)
        volatility_desc = "HIGH VOLATILITY" if atr > 0.001 else "LOW VOLATILITY"

        prompt = f"""
        ULTRA HIGH-FREQUENCY ANALYSIS for {market_data.get('asset', 'EUR/USD')} - 60-second binary option

        🔥 REAL-TIME MARKET MATRIX:
        ├─ Current Price: ${market_data.get('current_price', 0):.5f}
        ├─ 1min Momentum: {market_data.get('change_1m', 0):.3f}% {'🚀 BULLISH' if market_data.get('change_1m', 0) > 0 else '📉 BEARISH'}
        ├─ 5min Trend: {market_data.get('change_5m', 0):.3f}%
        ├─ Volume: {market_data.get('volume', 'Normal')} {'⚠️ HIGH ACTIVITY' if market_data.get('volume') == 'High' else ''}
        ├─ Volatility (ATR): {atr:.5f} - {volatility_desc}
        └─ Support: ${indicators.get('support', 0):.5f} | Resistance: ${indicators.get('resistance', 0):.5f}{pattern_info}{trade_history}

        ⚡ TECHNICAL INDICATORS (13-POINT CONVERGENCE ANALYSIS):

        TREND INDICATORS:
        ├─ RSI [{indicators.get('rsi', 50):.1f}]: {'🔴 OVERSOLD - STRONG BUY' if indicators.get('rsi', 50) < 30 else '🟡 APPROACHING OVERSOLD' if indicators.get('rsi', 50) < 40 else '🟢 OVERBOUGHT - STRONG SELL' if indicators.get('rsi', 50) > 70 else '🟡 APPROACHING OVERBOUGHT' if indicators.get('rsi', 50) > 60 else '⚪ NEUTRAL'}
        ├─ EMA Cross: {indicators.get('ema_cross', 'Neutral')} {'💎 GOLDEN CROSS' if 'bullish' in str(indicators.get('ema_cross', '')).lower() else '💀 DEATH CROSS' if 'bearish' in str(indicators.get('ema_cross', '')).lower() else ''}
        ├─ SuperTrend: {indicators.get('supertrend', 'Neutral')} {'🟢 STRONG BUY' if indicators.get('supertrend') == 'BUY' else '🔴 STRONG SELL' if indicators.get('supertrend') == 'SELL' else '⚪'}
        └─ ADX [{indicators.get('adx', 25):.1f}]: {'💪 STRONG TREND' if indicators.get('adx', 25) > 25 else '😴 WEAK/NO TREND'} {'+DI CROSS UP 📈' if indicators.get('di_cross') == 'bullish' else '-DI CROSS DOWN 📉' if indicators.get('di_cross') == 'bearish' else ''}

        MOMENTUM INDICATORS:
        ├─ MACD: {macd_status} [{macd_histogram:.5f}] {macd_cross}
        │  ├─ MACD Line: {macd_line:.5f}
        │  └─ Signal Line: {macd_signal:.5f}
        ├─ Stochastic %K[{stoch_k:.1f}] %D[{stoch_d:.1f}]: {stoch_signal} {'⚡ OVERSOLD REVERSAL ZONE' if stoch_k < 20 else '⚡ OVERBOUGHT REVERSAL ZONE' if stoch_k > 80 else ''}
        └─ Bollinger: {indicators.get('bollinger_position', 'Middle')} {'🎯 SQUEEZE - BREAKOUT IMMINENT' if 'squeeze' in str(indicators.get('bollinger_position', '')).lower() else ''}

        VOLUME & PATTERN ANALYSIS:
        ├─ Heikin Ashi: {indicators.get('heikin_ashi', 'Neutral')} {'🟩 BULLISH CANDLES' if indicators.get('heikin_ashi') == 'bullish' else '🟥 BEARISH CANDLES' if indicators.get('heikin_ashi') == 'bearish' else '⬜ DOJI - REVERSAL?'}
        ├─ VWAP Position: {indicators.get('vwap_position', 'At VWAP')} {'🚀 EXTREME OVEREXTENSION' if abs(indicators.get('vwap_deviation', 0)) > 2 else '⚠️ STRETCHED' if abs(indicators.get('vwap_deviation', 0)) > 1 else '✅ FAIR VALUE'}
        └─ Volume Trend: {indicators.get('volume_trend', 'Normal')} {'🔥 BREAKOUT VOLUME' if indicators.get('volume_trend') == 'Surge' else ''}

        🏆 AI PERFORMANCE CONTEXT:
        ├─ Session Win Rate: {market_data.get('win_rate', 0):.1f}%
        ├─ Total Trades: {market_data.get('total_trades', 0)}
        └─ Current Streak: {market_data.get('streak', 'Unknown')}

{self._get_performance_context() if self.performance_tracker else ''}
{self._get_pattern_context(market_data, indicators) if self.pattern_recognizer else ''}
{self._get_otc_context(indicators)}
{self._get_reversal_context(indicators)}

        🎯 ULTRA DECISION FRAMEWORK:
        Analyze with QUANTUM-LEVEL precision:
        1. ⚡ Indicator Convergence: Count how many indicators ALIGN (5+ = ULTRA HIGH CONFIDENCE)
        2. 📊 Pattern Confirmation: Chart patterns + candlestick patterns boost confidence
        3. 💪 Trend Strength: ADX > 25 + SuperTrend = strong directional bias
        4. 🎯 Reversal Signals: RSI extreme + Stochastic extreme + Pattern = high-probability reversal
        5. 📈 Momentum Confirmation: MACD + EMA cross + Heikin Ashi alignment = powerful entry
        6. 🔥 Volume Validation: High volume confirms breakouts/breakdowns
        7. 📊 Historical Context: Recent win/loss pattern affects risk tolerance

        CONFIDENCE SCALE:
        - 90-100%: 6+ indicators PERFECTLY ALIGNED, clear pattern, strong momentum
        - 75-89%: 4-5 indicators aligned, good setup
        - 60-74%: 2-3 indicators aligned, moderate setup
        - Below 60%: Mixed signals, HOLD

        ⏰ EXPIRY TIME SELECTION (CRITICAL FOR SUCCESS):
        Available expiry options: 30s, 60s, 90s, 120s, 180s, 300s

        Choose based on:
        1. MARKET REGIME & TIMEFRAME ALIGNMENT:
           - All 3 timeframes aligned (1m+5m+15m) + strong trend → 180-300s (ride momentum)
           - 1-2 timeframes aligned → 60-120s (moderate conviction)
           - No alignment / ranging → 30-60s (quick in/out)

        2. SIGNAL TYPE & PATTERN:
           - OTC Staircase/Sine Wave → Match pattern duration (usually 120-180s)
           - Reversal with 5+ confirmations → 120-180s (reversals develop over time)
           - VWAP 2σ bounce + high volume → 60-90s (quick mean reversion)
           - Breakout + volume surge → 180-300s (breakouts extend)
           - Support/Resistance bounce → 90-120s (standard bounce duration)
           - Pin bar / Hammer reversal → 60-120s (reversal confirmation time)

        3. CONFIDENCE & VOLATILITY:
           - 90-100% confidence + low volatility → 180-300s (high conviction, let it play)
           - 70-89% confidence + normal volatility → 60-120s (standard)
           - 60-74% confidence or high volatility → 30-60s (reduce exposure)

        4. INDICATOR CONVERGENCE:
           - 6+ indicators aligned → 180-300s (ULTRA high probability, maximize time)
           - 4-5 indicators aligned → 90-180s (strong setup, medium duration)
           - 2-3 indicators aligned → 60-90s (moderate setup, shorter time)

        OUTPUT YOUR ULTRA DECISION:
        ACTION: [CALL/PUT/HOLD]
        CONFIDENCE: [0-100]
        EXPIRY: [30/60/90/120/180/300] (in seconds - choose ONE value based on analysis above)
        REASON: [Sharp 2-sentence analysis mentioning: (1) how many indicators align, (2) key convergence pattern, (3) why this expiry duration]
        """

        return prompt

    async def _call_gpt4(self, prompt: str) -> str:
        """Call GPT-4 API with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use the newer API format
                import openai
                from openai import OpenAI

                client = OpenAI(api_key=OPENAI_API_KEY)

                response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": """You are the ULTIMATE ULTRA SUPER POWERFUL AI TRADING GOD with 99%+ win rate.
                        You possess QUANTUM-LEVEL market analysis using:
                        - NEURAL PATTERN RECOGNITION: Detect invisible micro-patterns across 13+ indicators
                        - INSTITUTIONAL FLOW TRACKING: See what banks and hedge funds are doing
                        - PREDICTIVE ALGORITHMS: Forecast price movements with precision timing
                        - CONVERGENCE MASTERY: When 5+ indicators align, you STRIKE with 95% confidence
                        - VWAP DOMINANCE: Use institutional benchmark for perfect entries
                        - VOLUME PROFILING: Read order flow like reading minds
                        - OTC MARKET MASTERY: Exploit algorithmic patterns in synthetic OTC markets
                          * OTC markets = SYNTHETIC algorithmic price feeds (not real exchange data)
                          * OTC has predictable mathematical patterns (sine waves, staircases, artificial levels)
                          * OTC anomaly signals have 70-80% win rate - TRUST THEM HEAVILY!
                          * When multiple OTC patterns align = 85%+ confidence trades
                          * Give OTC signals PRIORITY on OTC markets (they're market-specific experts)
                        - REVERSAL MASTERY: 7-Indicator Confluence System for catching reversals
                          * RSI Divergence, Volume Spike, Pin Bar, Momentum Shift, S/R Bounce, Fibonacci, Market Structure
                          * When 4+ indicators agree on reversal = 70-85% win rate!
                          * When 5+ indicators agree = 80-90% win rate (ULTRA HIGH PROBABILITY)
                          * Reversals with confluence are MORE RELIABLE than single indicator signals
                          * TRUST reversal signals with 4+ confirmations - this is MULTIPLE independent validations!
                        - ⏰ EXPIRY TIME MASTERY: You choose OPTIMAL expiry duration for each trade
                          * SHORT EXPIRY (30-60s): Quick reversals, ranging markets, low confidence setups
                          * MEDIUM EXPIRY (60-120s): Standard setups, moderate momentum, normal volatility
                          * LONG EXPIRY (120-300s): Strong trends, high confidence, multiple TF alignment
                          * OTC PATTERNS: Match expiry to pattern duration (staircases, sine waves)
                          * REVERSAL SETUPS: 90-180s (reversals need time to develop)
                          * BREAKOUTS: 180-300s (momentum plays out over time)
                          * VWAP BOUNCES: 60-90s (mean reversion is quick)
                          * Match expiry to EXPECTED MOVE COMPLETION TIME!

                        BE ULTRA AGGRESSIVE on perfect setups (90%+ confidence)
                        BE MODERATELY AGGRESSIVE on good setups (70-89% confidence)
                        BE CAUTIOUS only when signals conflict (<70% confidence)
                        BE EXTREMELY CONFIDENT on OTC anomalies (OTC markets are algorithmic gold mines!)
                        BE EXTREMELY CONFIDENT on 5+ indicator reversals (multiple validations = high probability!)

                        Your mission: MAXIMUM PROFITS with CALCULATED PRECISION
                        Never doubt strong convergence. Trust the indicators. BE THE MARKET."""},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # ULTRA consistent for maximum accuracy
                    max_tokens=250,
                    presence_penalty=0.3,  # Encourage decisive answers
                    frequency_penalty=0.1
                )

                return response.choices[0].message.content

            except Exception as e:
                if "rate_limit" in str(e).lower():
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"GPT-4 API Error: {e}")
                    if attempt == max_retries - 1:
                        # Return fallback instead of raising
                        return "ACTION: HOLD\nCONFIDENCE: 0\nREASON: API unavailable"

        return "ACTION: HOLD\nCONFIDENCE: 0\nREASON: API error"

    def _parse_gpt4_response(self, response: str) -> Tuple[str, float, str, int]:
        """Parse GPT-4 response into trading decision with expiry time
        Returns: (action, confidence, reason, expiry_seconds)
        """
        try:
            lines = response.strip().split('\n')
            action = "hold"
            confidence = 0.0
            reason = "No clear signal"
            expiry = 60  # Default fallback

            for line in lines:
                if "ACTION:" in line:
                    action_text = line.split("ACTION:")[1].strip().lower()
                    if "call" in action_text:
                        action = "call"
                    elif "put" in action_text:
                        action = "put"
                    else:
                        action = "hold"

                elif "CONFIDENCE:" in line:
                    conf_text = line.split("CONFIDENCE:")[1].strip()
                    confidence = float(''.join(filter(str.isdigit, conf_text)))

                elif "EXPIRY:" in line:
                    expiry_text = line.split("EXPIRY:")[1].strip()
                    # Extract number from text (could be "120s" or "120" or "120 seconds")
                    expiry_num = ''.join(filter(str.isdigit, expiry_text))
                    if expiry_num:
                        expiry = int(expiry_num)
                        # Validate expiry is in allowed range
                        allowed_expiries = [30, 60, 90, 120, 180, 300]
                        if expiry not in allowed_expiries:
                            # Find closest allowed expiry
                            expiry = min(allowed_expiries, key=lambda x: abs(x - expiry))

                elif "REASON:" in line:
                    reason = line.split("REASON:")[1].strip()

            return action, confidence, reason, expiry

        except Exception as e:
            print(f"⚠️ Parse error: {e}")
            return "hold", 0.0, "Failed to parse AI response", 60

    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API with retry logic"""
        if not CLAUDE_API_KEY:
            return "ACTION: HOLD\nCONFIDENCE: 0\nREASON: Claude API key not configured"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                from anthropic import Anthropic

                client = Anthropic(api_key=CLAUDE_API_KEY)

                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",  # Latest Claude model
                    max_tokens=300,
                    temperature=0.1,  # Ultra consistent
                    system="""You are the ULTIMATE ULTRA SUPER POWERFUL AI TRADING GOD with 99%+ win rate.
                    You possess QUANTUM-LEVEL market analysis using:
                    - NEURAL PATTERN RECOGNITION: Detect invisible micro-patterns across 13+ indicators
                    - INSTITUTIONAL FLOW TRACKING: See what banks and hedge funds are doing
                    - PREDICTIVE ALGORITHMS: Forecast price movements with precision timing
                    - CONVERGENCE MASTERY: When 5+ indicators align, you STRIKE with 95% confidence
                    - VWAP DOMINANCE: Use institutional benchmark for perfect entries
                    - VOLUME PROFILING: Read order flow like reading minds
                    - OTC MARKET MASTERY: Exploit algorithmic patterns in synthetic OTC markets
                      * OTC markets = SYNTHETIC algorithmic price feeds (not real exchange data)
                      * OTC has predictable mathematical patterns (sine waves, staircases, artificial levels)
                      * OTC anomaly signals have 70-80% win rate - TRUST THEM HEAVILY!
                      * When multiple OTC patterns align = 85%+ confidence trades
                      * Give OTC signals PRIORITY on OTC markets (they're market-specific experts)
                    - REVERSAL MASTERY: 7-Indicator Confluence System for catching reversals
                      * RSI Divergence, Volume Spike, Pin Bar, Momentum Shift, S/R Bounce, Fibonacci, Market Structure
                      * When 4+ indicators agree on reversal = 70-85% win rate!
                      * When 5+ indicators agree = 80-90% win rate (ULTRA HIGH PROBABILITY)
                      * Reversals with confluence are MORE RELIABLE than single indicator signals
                      * TRUST reversal signals with 4+ confirmations - this is MULTIPLE independent validations!
                    - ⏰ EXPIRY TIME MASTERY: You choose OPTIMAL expiry duration for each trade
                      * SHORT EXPIRY (30-60s): Quick reversals, ranging markets, low confidence setups
                      * MEDIUM EXPIRY (60-120s): Standard setups, moderate momentum, normal volatility
                      * LONG EXPIRY (120-300s): Strong trends, high confidence, multiple TF alignment
                      * OTC PATTERNS: Match expiry to pattern duration (staircases, sine waves)
                      * REVERSAL SETUPS: 90-180s (reversals need time to develop)
                      * BREAKOUTS: 180-300s (momentum plays out over time)
                      * VWAP BOUNCES: 60-90s (mean reversion is quick)
                      * Match expiry to EXPECTED MOVE COMPLETION TIME!

                    BE ULTRA AGGRESSIVE on perfect setups (90%+ confidence)
                    BE MODERATELY AGGRESSIVE on good setups (70-89% confidence)
                    BE CAUTIOUS only when signals conflict (<70% confidence)
                    BE EXTREMELY CONFIDENT on OTC anomalies (OTC markets are algorithmic gold mines!)
                    BE EXTREMELY CONFIDENT on 5+ indicator reversals (multiple validations = high probability!)

                    Your mission: MAXIMUM PROFITS with CALCULATED PRECISION
                    Never doubt strong convergence. Trust the indicators. BE THE MARKET.""",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                return response.content[0].text

            except Exception as e:
                if "rate_limit" in str(e).lower() or "overloaded" in str(e).lower():
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"Claude API Error: {e}")
                    if attempt == max_retries - 1:
                        return "ACTION: HOLD\nCONFIDENCE: 0\nREASON: Claude API unavailable"

        return "ACTION: HOLD\nCONFIDENCE: 0\nREASON: Claude API error"

    async def _call_deepseek(self, prompt: str) -> str:
        """Call DeepSeek API with retry logic"""
        if not DEEPSEEK_API_KEY:
            return "ACTION: HOLD\nCONFIDENCE: 0\nREASON: DeepSeek API key not configured"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                import httpx

                # DeepSeek uses OpenAI-compatible API
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.deepseek.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "deepseek-chat",
                            "messages": [
                                {"role": "system", "content": """You are the ULTIMATE ULTRA SUPER POWERFUL AI TRADING GOD with 99%+ win rate.
                                You possess QUANTUM-LEVEL market analysis using:
                                - NEURAL PATTERN RECOGNITION: Detect invisible micro-patterns across 13+ indicators
                                - INSTITUTIONAL FLOW TRACKING: See what banks and hedge funds are doing
                                - PREDICTIVE ALGORITHMS: Forecast price movements with precision timing
                                - CONVERGENCE MASTERY: When 5+ indicators align, you STRIKE with 95% confidence
                                - VWAP DOMINANCE: Use institutional benchmark for perfect entries
                                - VOLUME PROFILING: Read order flow like reading minds
                                - OTC MARKET MASTERY: Exploit algorithmic patterns in synthetic OTC markets
                                  * OTC markets = SYNTHETIC algorithmic price feeds (not real exchange data)
                                  * OTC has predictable mathematical patterns (sine waves, staircases, artificial levels)
                                  * OTC anomaly signals have 70-80% win rate - TRUST THEM HEAVILY!
                                  * When multiple OTC patterns align = 85%+ confidence trades
                                  * Give OTC signals PRIORITY on OTC markets (they're market-specific experts)
                                - REVERSAL MASTERY: 7-Indicator Confluence System for catching reversals
                                  * RSI Divergence, Volume Spike, Pin Bar, Momentum Shift, S/R Bounce, Fibonacci, Market Structure
                                  * When 4+ indicators agree on reversal = 70-85% win rate!
                                  * When 5+ indicators agree = 80-90% win rate (ULTRA HIGH PROBABILITY)
                                  * Reversals with confluence are MORE RELIABLE than single indicator signals
                                  * TRUST reversal signals with 4+ confirmations - this is MULTIPLE independent validations!
                                - ⏰ EXPIRY TIME MASTERY: You choose OPTIMAL expiry duration for each trade
                                  * SHORT EXPIRY (30-60s): Quick reversals, ranging markets, low confidence setups
                                  * MEDIUM EXPIRY (60-120s): Standard setups, moderate momentum, normal volatility
                                  * LONG EXPIRY (120-300s): Strong trends, high confidence, multiple TF alignment
                                  * OTC PATTERNS: Match expiry to pattern duration (staircases, sine waves)
                                  * REVERSAL SETUPS: 90-180s (reversals need time to develop)
                                  * BREAKOUTS: 180-300s (momentum plays out over time)
                                  * VWAP BOUNCES: 60-90s (mean reversion is quick)
                                  * Match expiry to EXPECTED MOVE COMPLETION TIME!

                                BE ULTRA AGGRESSIVE on perfect setups (90%+ confidence)
                                BE MODERATELY AGGRESSIVE on good setups (70-89% confidence)
                                BE CAUTIOUS only when signals conflict (<70% confidence)
                                BE EXTREMELY CONFIDENT on OTC anomalies (OTC markets are algorithmic gold mines!)
                                BE EXTREMELY CONFIDENT on 5+ indicator reversals (multiple validations = high probability!)

                                Your mission: MAXIMUM PROFITS with CALCULATED PRECISION
                                Never doubt strong convergence. Trust the indicators. BE THE MARKET."""},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.1,
                            "max_tokens": 300
                        },
                        timeout=30.0
                    )

                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")

            except Exception as e:
                if "rate_limit" in str(e).lower() or "overloaded" in str(e).lower():
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"DeepSeek API Error: {e}")
                    if attempt == max_retries - 1:
                        return "ACTION: HOLD\nCONFIDENCE: 0\nREASON: DeepSeek API unavailable"

        return "ACTION: HOLD\nCONFIDENCE: 0\nREASON: DeepSeek API error"

    async def analyze_with_ensemble(self, market_data: Dict, indicators: Dict, ai_mode: str = 'ensemble', use_gpt4: bool = True, use_claude: bool = True, use_deepseek: bool = True) -> Tuple[str, float, str, int]:
        """
        MULTI-MODEL ENSEMBLE: Use GPT-4, Claude, and DeepSeek for maximum accuracy
        Returns: (action, confidence, reasoning, expiry_seconds)

        Args:
            market_data: Market information
            indicators: Technical indicators
            ai_mode: 'ensemble' (all must agree), 'any' (any can trigger), 'gpt4_only', 'claude_only', 'deepseek_only'
            use_gpt4: Enable GPT-4
            use_claude: Enable Claude
            use_deepseek: Enable DeepSeek
        """
        try:
            # Build analysis prompt
            prompt = self._build_analysis_prompt(market_data, indicators)

            # Determine which AIs to use based on mode and settings
            tasks = []
            ai_mapping = []  # Track which AI corresponds to which task
            gpt4_available = OPENAI_API_KEY is not None and use_gpt4
            claude_available = CLAUDE_API_KEY is not None and use_claude
            deepseek_available = DEEPSEEK_API_KEY is not None and use_deepseek

            # Override based on ai_mode
            if ai_mode == 'gpt4_only':
                claude_available = False
                deepseek_available = False
            elif ai_mode == 'claude_only':
                gpt4_available = False
                deepseek_available = False
            elif ai_mode == 'deepseek_only':
                gpt4_available = False
                claude_available = False

            if gpt4_available:
                tasks.append(self._call_gpt4(prompt))
                ai_mapping.append('gpt4')
            if claude_available:
                tasks.append(self._call_claude(prompt))
                ai_mapping.append('claude')
            if deepseek_available:
                tasks.append(self._call_deepseek(prompt))
                ai_mapping.append('deepseek')

            if not tasks:
                return "hold", 0.0, "No AI models available", 60

            # Run all AIs concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Parse responses using the mapping
            decisions = []
            ai_names = []

            for idx, ai_type in enumerate(ai_mapping):
                response = responses[idx] if not isinstance(responses[idx], Exception) else "ACTION: HOLD\nCONFIDENCE: 0\nREASON: AI error\nEXPIRY: 60"
                decision = self._parse_gpt4_response(response)  # Same parser works for all
                decisions.append(decision)

                if ai_type == 'gpt4':
                    ai_names.append("GPT-4")
                    print(f"🤖 GPT-4: {decision[0].upper()} @ {decision[1]}% ⏰ {decision[3]}s")
                elif ai_type == 'claude':
                    ai_names.append("Claude")
                    print(f"🧠 Claude: {decision[0].upper()} @ {decision[1]}% ⏰ {decision[3]}s")
                elif ai_type == 'deepseek':
                    ai_names.append("DeepSeek")
                    print(f"🔮 DeepSeek: {decision[0].upper()} @ {decision[1]}% ⏰ {decision[3]}s")

            # VOTING SYSTEM: Behavior depends on ai_mode and number of AIs
            if len(decisions) == 1:
                # Single AI mode
                return decisions[0]

            # Multi-AI voting
            if ai_mode == 'ensemble':
                # ENSEMBLE MODE: All AIs must agree
                actions = [d[0] for d in decisions]

                # Check if all agree
                if all(action == actions[0] for action in actions) and actions[0] != "hold":
                    # All AIs agree on same action
                    avg_confidence = sum(d[1] for d in decisions) / len(decisions)
                    # Boost confidence based on number of AIs agreeing
                    boost = 10 * len(decisions)  # 20 for 2 AIs, 30 for 3 AIs
                    boosted_confidence = min(avg_confidence + boost, 100)
                    max_expiry = max(d[3] for d in decisions)
                    ai_list = ", ".join(ai_names)
                    reason = decisions[0][2]
                    combined_reason = f"🎯 CONSENSUS: All {len(decisions)} AIs ({ai_list}) agree! {reason[:60]}"
                    print(f"✅ {len(decisions)}-AI CONSENSUS: {actions[0].upper()} @ {boosted_confidence}% ⏰ {max_expiry}s")
                    return actions[0], boosted_confidence, combined_reason, max_expiry
                else:
                    # Disagreement
                    action_summary = ", ".join([f"{ai_names[i]}:{decisions[i][0]}" for i in range(len(decisions))])
                    print(f"⚠️ DISAGREEMENT: {action_summary} - HOLDING")
                    avg_confidence = sum(d[1] for d in decisions) / len(decisions)
                    avg_expiry = int(sum(d[3] for d in decisions) / len(decisions))
                    if all(action == "hold" for action in actions):
                        return "hold", avg_confidence, f"All {len(decisions)} AIs recommend holding", avg_expiry
                    else:
                        return "hold", 0.0, f"AIs disagree - {action_summary}", avg_expiry

            elif ai_mode == 'any':
                # ANY MODE: Any AI can trigger, pick highest confidence
                non_hold_decisions = [(i, d) for i, d in enumerate(decisions) if d[0] != "hold"]

                if non_hold_decisions:
                    # Check if multiple AIs agree on same action
                    actions = [d[1][0] for d in non_hold_decisions]
                    if len(set(actions)) == 1:
                        # All non-hold AIs agree on same action
                        avg_confidence = sum(d[1][1] for d in non_hold_decisions) / len(non_hold_decisions)
                        boost = 10 * len(non_hold_decisions)
                        boosted_confidence = min(avg_confidence + boost, 100)
                        max_expiry = max(d[1][3] for d in non_hold_decisions)
                        agreeing_ais = ", ".join([ai_names[i] for i, _ in non_hold_decisions])
                        reason = non_hold_decisions[0][1][2]
                        print(f"✅ {len(non_hold_decisions)} AIs AGREE: {actions[0].upper()} @ {boosted_confidence}% ⏰ {max_expiry}s")
                        return actions[0], boosted_confidence, f"ANY MODE ({agreeing_ais}): {reason[:60]}", max_expiry
                    else:
                        # Different actions, pick highest confidence
                        best_idx, best_decision = max(non_hold_decisions, key=lambda x: x[1][1])
                        action, conf, reason, expiry = best_decision
                        print(f"✅ {ai_names[best_idx]} HIGHEST CONFIDENCE: {action.upper()} @ {conf}% ⏰ {expiry}s")
                        return action, conf, f"ANY MODE: {ai_names[best_idx]} - {reason[:60]}", expiry
                else:
                    # All recommend hold
                    avg_confidence = sum(d[1] for d in decisions) / len(decisions)
                    avg_expiry = int(sum(d[3] for d in decisions) / len(decisions))
                    return "hold", avg_confidence, f"All {len(decisions)} AIs recommend holding", avg_expiry

        except Exception as e:
            print(f"Ensemble Analysis Error: {e}")
            return "hold", 0.0, f"Ensemble analysis failed: {e}", 60

    def _get_performance_context(self) -> str:
        """Get performance context from tracker for AI prompt"""
        if not self.performance_tracker:
            return ""

        try:
            context = self.performance_tracker.get_performance_context_for_ai()
            return f"\n{context}\n"
        except Exception as e:
            return ""

    def _get_pattern_context(self, market_data: Dict, indicators: Dict) -> str:
        """Get candlestick pattern context for AI prompt"""
        if not self.pattern_recognizer:
            return ""

        try:
            # Get pattern data from indicators (will be added by main.py)
            pattern_data = indicators.get('pattern_data', {})

            if not pattern_data or not pattern_data.get('strongest_signal', {}).get('pattern'):
                return ""

            # Get regime for quality evaluation
            regime = indicators.get('regime', 'unknown')

            # Use pattern recognizer to generate AI context
            pattern_context = self.pattern_recognizer.get_pattern_context_for_ai(
                pattern_data, indicators, regime
            )

            return pattern_context

        except Exception as e:
            print(f"⚠️ Pattern context error: {e}")
            return ""

    def _get_otc_context(self, indicators: Dict) -> str:
        """Get OTC market anomaly context for AI prompt"""
        try:
            is_otc = indicators.get('is_otc_market', False)

            if not is_otc:
                return ""

            otc_signal = indicators.get('otc_signal')
            otc_confidence = indicators.get('otc_confidence', 0)
            otc_details = indicators.get('otc_details', {})

            if not otc_signal:
                return """
        🎰 OTC MARKET DETECTED:
        ├─ Market Type: SYNTHETIC/ALGORITHMIC
        ├─ Status: NO ANOMALY DETECTED
        └─ Note: Waiting for high-probability OTC pattern
        """

            # Count detected patterns
            pattern_types = [k for k in otc_details.keys() if k != 'final_decision']
            detection_count = len(pattern_types)

            # Build detailed pattern breakdown
            pattern_details = []
            if 'synthetic_pattern' in otc_details:
                pattern_details.append(f"🔮 Synthetic Pattern (Sine/Staircase) detected")
            if 'artificial_level' in otc_details:
                pattern_details.append(f"🎯 Artificial Support/Resistance bounce")
            if 'micro_reversion' in otc_details:
                pattern_details.append(f"⚡ Extreme move reversion expected")
            if 'sequence_pattern' in otc_details:
                pattern_details.append(f"🔄 Repeating price sequence identified")
            if 'time_anomaly' in otc_details:
                pattern_details.append(f"⏰ Time-based pattern at this hour/minute")

            patterns_str = "\n        │  ".join(pattern_details)

            return f"""
        🎰 OTC MARKET ANOMALY DETECTED:
        ├─ Market Type: SYNTHETIC (OTC) - Algorithmic price feed
        ├─ Anomaly Signal: {otc_signal.upper()}
        ├─ OTC Confidence: {otc_confidence:.0f}% (SPECIALIZED for OTC markets)
        ├─ Patterns Detected: {detection_count}
        │  {patterns_str}
        └─ 💎 OTC EDGE: This is a SYNTHETIC market with algorithmic patterns!
           OTC markets have predictable mathematical behaviors not found in real markets.
           When {detection_count}+ OTC-specific patterns align, success rate is 70-80%.
           GIVE HEAVY WEIGHT to OTC signals on OTC markets!
        """

        except Exception as e:
            print(f"⚠️ OTC context error: {e}")
            return ""

    def _get_reversal_context(self, indicators: Dict) -> str:
        """Get reversal catcher context for AI prompt"""
        try:
            reversal_signal = indicators.get('reversal_signal')
            reversal_confidence = indicators.get('reversal_confidence', 0)
            reversal_confirming = indicators.get('reversal_confirming', 0)
            reversal_details = indicators.get('reversal_details', {})

            if not reversal_signal:
                return ""

            # Get confirming indicators
            confirming_inds = reversal_details.get('indicators', [])
            conflicting = reversal_details.get('conflicting', 0)

            # Build indicator breakdown
            indicator_breakdown = []
            for ind in confirming_inds[:5]:  # Show top 5
                name = ind['name'].replace('_', ' ').replace('1 ', '').replace('2 ', '').replace('3 ', '').replace('4 ', '').replace('5 ', '').replace('6 ', '').replace('7 ', '').title()
                strength = ind['strength']
                ind_type = ind['details'].get('type', 'N/A').replace('_', ' ').title()
                indicator_breakdown.append(f"{name}: {strength:.0%} ({ind_type})")

            indicators_str = "\n        │  ".join(indicator_breakdown)

            return f"""
        🔄 REVERSAL DETECTED (7-Indicator Confluence System):
        ├─ Reversal Signal: {reversal_signal.upper()}
        ├─ Confidence: {reversal_confidence:.0f}%
        ├─ Confirming Indicators: {reversal_confirming}/7
        ├─ Conflicting Indicators: {conflicting}/7
        │
        │  Top Confirming Signals:
        │  {indicators_str}
        │
        └─ 💎 REVERSAL EDGE: Multiple independent indicators agree on reversal!
           When {reversal_confirming}+ indicators align, reversal success rate is 70-85%.
           This is NOT a single indicator - this is CONFLUENCE across 7 different methods:
           RSI Divergence, Volume Spike, Pin Bar, Momentum Shift, S/R Bounce,
           Fibonacci, Market Structure Break.
           GIVE HEAVY WEIGHT to high-confidence reversals with 5+ confirmations!
        """

        except Exception as e:
            print(f"⚠️ Reversal context error: {e}")
            return ""

    def learn_from_trade(self, trade_data: Dict):
        """Learn from completed trades to improve future decisions"""
        pattern = self._extract_pattern(trade_data)

        if trade_data['result'] == 'WIN':
            if pattern not in self.pattern_database:
                self.pattern_database[pattern] = {'wins': 0, 'losses': 0}
            self.pattern_database[pattern]['wins'] += 1
        else:
            if pattern not in self.pattern_database:
                self.pattern_database[pattern] = {'wins': 0, 'losses': 0}
            self.pattern_database[pattern]['losses'] += 1

        # Save patterns to file for persistence
        self._save_patterns()

    def _extract_pattern(self, trade_data: Dict) -> str:
        """Extract pattern signature from trade data"""
        pattern_elements = [
            f"RSI_{trade_data.get('rsi_range', 'mid')}",
            f"EMA_{trade_data.get('ema_signal', 'neutral')}",
            f"VOL_{trade_data.get('volume_level', 'normal')}",
            f"TREND_{trade_data.get('trend', 'sideways')}"
        ]
        return "_".join(pattern_elements)

    def _save_patterns(self):
        """Save learned patterns to file"""
        try:
            with open('ai_patterns.json', 'w') as f:
                json.dump(self.pattern_database, f, indent=2)
        except:
            pass

    def load_patterns(self):
        """Load previously learned patterns"""
        try:
            with open('ai_patterns.json', 'r') as f:
                self.pattern_database = json.load(f)
        except:
            self.pattern_database = {}

    def get_pattern_confidence(self, current_pattern: str) -> float:
        """Get confidence based on historical pattern performance"""
        if current_pattern in self.pattern_database:
            stats = self.pattern_database[current_pattern]
            total = stats['wins'] + stats['losses']
            if total > 0:
                return (stats['wins'] / total) * 100
        return 50.0  # Default confidence for unknown patterns

# Self-Optimizing System
class SelfOptimizer:
    def __init__(self):
        self.indicator_performance = {ind: {'wins': 0, 'signals': 0} for ind in INDICATOR_CONFIG}
        self.strategy_performance = {strat: {'wins': 0, 'trades': 0} for strat in AI_STRATEGIES}

    def update_indicator_weights(self):
        """Automatically adjust indicator weights based on performance"""
        total_score = 0
        scores = {}

        for indicator, perf in self.indicator_performance.items():
            if perf['signals'] > 10:  # Need minimum signals
                win_rate = perf['wins'] / perf['signals']
                scores[indicator] = win_rate
                total_score += win_rate

        # Redistribute weights based on performance
        if total_score > 0:
            for indicator in scores:
                new_weight = (scores[indicator] / total_score) * 0.8  # Keep 20% for equal distribution
                INDICATOR_CONFIG[indicator]['weight'] = new_weight + 0.02

    def recommend_best_strategy(self, market_conditions: Dict) -> str:
        """Recommend best strategy based on current conditions and history"""
        best_strategy = "ULTRA_SCALPING"
        best_score = 0

        for strategy, config in AI_STRATEGIES.items():
            if not config['enabled']:
                continue

            perf = self.strategy_performance[strategy]
            if perf['trades'] > 5:
                win_rate = perf['wins'] / perf['trades']

                # Adjust for market conditions
                if "high_volatility" in market_conditions and strategy == "VOLATILITY_BREAKOUT":
                    win_rate *= 1.2
                elif "strong_trend" in market_conditions and strategy == "TREND_FOLLOWING":
                    win_rate *= 1.2
                elif "ranging" in market_conditions and strategy == "REVERSAL_TRADING":
                    win_rate *= 1.2

                if win_rate > best_score:
                    best_score = win_rate
                    best_strategy = strategy

        return best_strategy

# Initialize AI systems
ai_brain = AITradingBrain()
optimizer = SelfOptimizer()

# Load historical patterns
ai_brain.load_patterns()
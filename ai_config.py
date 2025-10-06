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
    if OPENAI_API_KEY and CLAUDE_API_KEY:
        print("✅✅✅ DUAL AI SYSTEM READY - GPT-4 + CLAUDE ENSEMBLE! ✅✅✅")
    elif OPENAI_API_KEY:
        print("✅ Single AI mode (GPT-4 only)")
    elif CLAUDE_API_KEY:
        print("✅ Single AI mode (Claude only)")
except ImportError:
    print("⚠️ load_my_credentials.py not found (normal on Replit)")
    pass
except Exception as e:
    print(f"⚠️ Desktop credentials check failed: {e}")
    pass

# Method 1: Try to import from api_secrets.py (Good for Replit)
# Note: Named api_secrets to avoid conflict with Python's built-in secrets module
try:
    from api_secrets import OPENAI_API_KEY as SECRET_KEY, OPENAI_PROJECT_ID as SECRET_PROJECT_ID
    OPENAI_API_KEY = SECRET_KEY
    OPENAI_PROJECT_ID = SECRET_PROJECT_ID
    print("✅ Loaded API keys from api_secrets.py")
except ImportError:
    print("⚠️ api_secrets.py not found, trying other methods...")
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

# Method 3: If still None, try direct .env file read (backup method)
if not OPENAI_API_KEY:
    try:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        print(f"🔍 Checking for .env at: {env_path}")
        print(f"🔍 .env exists: {os.path.exists(env_path)}")
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        OPENAI_API_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                        print(f"✅ Loaded API key from .env file (length: {len(OPENAI_API_KEY)})")
                    elif line.startswith('OPENAI_PROJECT_ID='):
                        OPENAI_PROJECT_ID = line.split('=', 1)[1].strip().strip('"').strip("'")
        else:
            print(f"⚠️ .env file not found at {env_path}")
    except Exception as e:
        print(f"❌ Could not read .env file: {e}")

# Method 4: Fallback - if still nothing found
if not OPENAI_API_KEY:
    # IMPORTANT: Create secrets.py file or set environment variables
    print("⚠️ No API key found! Please create secrets.py or set environment variables")
    OPENAI_API_KEY = None
    OPENAI_PROJECT_ID = None

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Validation
if not OPENAI_API_KEY or OPENAI_API_KEY == "your-api-key-here":
    print("⚠️ WARNING: OpenAI API key not configured properly!")
    print("Please set OPENAI_API_KEY in environment variables, .env file, or ai_config.py")
else:
    print(f"✅ OpenAI API key loaded successfully (ending in ...{OPENAI_API_KEY[-4:]})")

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

# Market Analysis System
class AITradingBrain:
    def __init__(self):
        self.performance_history = []
        self.pattern_database = {}
        self.current_market_state = {}

    async def analyze_with_gpt4(self, market_data: Dict, indicators: Dict) -> Tuple[str, float, str]:
        """
        Use GPT-4 to analyze market conditions and provide trading decision
        Returns: (action, confidence, reasoning)
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
            return "hold", 0.0, "AI analysis failed"

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

        OUTPUT YOUR ULTRA DECISION:
        ACTION: [CALL/PUT/HOLD]
        CONFIDENCE: [0-100]
        REASON: [Sharp 2-sentence analysis mentioning: (1) how many indicators align, (2) key convergence pattern]
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
                        - PREDICTIVE ALGORITHMS: Forecast price movements 60 seconds ahead
                        - CONVERGENCE MASTERY: When 5+ indicators align, you STRIKE with 95% confidence
                        - VWAP DOMINANCE: Use institutional benchmark for perfect entries
                        - VOLUME PROFILING: Read order flow like reading minds

                        BE ULTRA AGGRESSIVE on perfect setups (90%+ confidence)
                        BE MODERATELY AGGRESSIVE on good setups (70-89% confidence)
                        BE CAUTIOUS only when signals conflict (<70% confidence)

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

    def _parse_gpt4_response(self, response: str) -> Tuple[str, float, str]:
        """Parse GPT-4 response into trading decision"""
        try:
            lines = response.strip().split('\n')
            action = "hold"
            confidence = 0.0
            reason = "No clear signal"

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

                elif "REASON:" in line:
                    reason = line.split("REASON:")[1].strip()

            return action, confidence, reason

        except:
            return "hold", 0.0, "Failed to parse AI response"

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
                    - PREDICTIVE ALGORITHMS: Forecast price movements 60 seconds ahead
                    - CONVERGENCE MASTERY: When 5+ indicators align, you STRIKE with 95% confidence
                    - VWAP DOMINANCE: Use institutional benchmark for perfect entries
                    - VOLUME PROFILING: Read order flow like reading minds

                    BE ULTRA AGGRESSIVE on perfect setups (90%+ confidence)
                    BE MODERATELY AGGRESSIVE on good setups (70-89% confidence)
                    BE CAUTIOUS only when signals conflict (<70% confidence)

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

    async def analyze_with_ensemble(self, market_data: Dict, indicators: Dict) -> Tuple[str, float, str]:
        """
        MULTI-MODEL ENSEMBLE: Use both GPT-4 and Claude for maximum accuracy
        Returns: (action, confidence, reasoning)
        """
        try:
            # Build analysis prompt
            prompt = self._build_analysis_prompt(market_data, indicators)

            # Call both AI models in parallel for speed
            tasks = []
            gpt4_available = OPENAI_API_KEY is not None
            claude_available = CLAUDE_API_KEY is not None

            if gpt4_available:
                tasks.append(self._call_gpt4(prompt))
            if claude_available:
                tasks.append(self._call_claude(prompt))

            if not tasks:
                return "hold", 0.0, "No AI models available"

            # Run both AIs concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Parse responses
            decisions = []
            ai_names = []

            if gpt4_available:
                gpt4_response = responses[0] if not isinstance(responses[0], Exception) else "ACTION: HOLD\nCONFIDENCE: 0\nREASON: GPT-4 error"
                gpt4_decision = self._parse_gpt4_response(gpt4_response)
                decisions.append(gpt4_decision)
                ai_names.append("GPT-4")
                print(f"🤖 GPT-4: {gpt4_decision[0].upper()} @ {gpt4_decision[1]}%")

            if claude_available:
                claude_response = responses[-1] if not isinstance(responses[-1], Exception) else "ACTION: HOLD\nCONFIDENCE: 0\nREASON: Claude error"
                claude_decision = self._parse_gpt4_response(claude_response)  # Same parser works
                decisions.append(claude_decision)
                ai_names.append("Claude")
                print(f"🧠 Claude: {claude_decision[0].upper()} @ {claude_decision[1]}%")

            # VOTING SYSTEM: Both AIs must agree for high confidence
            if len(decisions) == 2:
                action1, conf1, reason1 = decisions[0]
                action2, conf2, reason2 = decisions[1]

                # Both AIs agree on action
                if action1 == action2 and action1 != "hold":
                    # Boost confidence when both agree
                    avg_confidence = (conf1 + conf2) / 2
                    boosted_confidence = min(avg_confidence + 10, 100)  # +10 bonus for agreement
                    combined_reason = f"🎯 CONSENSUS: Both {ai_names[0]} & {ai_names[1]} agree! {reason1[:80]}"
                    print(f"✅ CONSENSUS TRADE: {action1.upper()} @ {boosted_confidence}%")
                    return action1, boosted_confidence, combined_reason

                # AIs disagree - be cautious
                elif action1 != action2:
                    print(f"⚠️ DISAGREEMENT: {ai_names[0]} says {action1}, {ai_names[1]} says {action2} - HOLDING")
                    return "hold", 0.0, f"AI models disagree: {ai_names[0]} ({action1}) vs {ai_names[1]} ({action2})"

                # Both say hold
                else:
                    avg_confidence = (conf1 + conf2) / 2
                    return "hold", avg_confidence, "Both AIs recommend holding"

            # Single AI mode
            else:
                return decisions[0]

        except Exception as e:
            print(f"Ensemble Analysis Error: {e}")
            return "hold", 0.0, f"Ensemble analysis failed: {e}"

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
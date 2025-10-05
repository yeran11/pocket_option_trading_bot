"""
AI Trading Configuration with OpenAI GPT-4
Advanced market analysis and decision-making system
"""

import openai
import numpy as np
from typing import Dict, List, Tuple
import json
from datetime import datetime, timedelta
import asyncio

# OpenAI Configuration with multiple fallback options
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

# Get API key from multiple sources
OPENAI_API_KEY = None
OPENAI_PROJECT_ID = None

# Method 1: Try to import from api_secrets.py (MOST RELIABLE - Direct Python import)
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
        print("✅ Loaded API keys from environment variables")

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
        """Build ULTRA POWERFUL prompt for GPT-4 analysis"""
        prompt = f"""
        ULTRA HIGH-FREQUENCY ANALYSIS for {market_data.get('asset', 'EUR/USD')} - 60-second binary option

        🔥 REAL-TIME MARKET MATRIX:
        ├─ Current Price: ${market_data.get('current_price', 0)}
        ├─ 1min Momentum: {market_data.get('change_1m', 0):.3f}% {'🚀 BULLISH' if market_data.get('change_1m', 0) > 0 else '📉 BEARISH'}
        ├─ 5min Trend: {market_data.get('change_5m', 0):.3f}%
        ├─ Volume Surge: {market_data.get('volume', 'Normal')} {'⚠️ HIGH ACTIVITY' if market_data.get('volume') == 'High' else ''}
        └─ Volatility Index: {market_data.get('volatility', 'Medium')}

        ⚡ POWER INDICATORS CONVERGENCE:
        ├─ RSI [{indicators.get('rsi', 50)}]: {'🔴 OVERSOLD - BUY SIGNAL' if indicators.get('rsi', 50) < 30 else '🟢 OVERBOUGHT - SELL SIGNAL' if indicators.get('rsi', 50) > 70 else '⚪ NEUTRAL'}
        ├─ EMA Cross: {indicators.get('ema_cross', 'Neutral')} {'💎 GOLDEN CROSS' if 'bullish' in str(indicators.get('ema_cross', '')).lower() else '💀 DEATH CROSS' if 'bearish' in str(indicators.get('ema_cross', '')).lower() else ''}
        ├─ Bollinger: {indicators.get('bollinger_position', 'Middle')} {'🎯 SQUEEZE DETECTED' if 'squeeze' in str(indicators.get('bollinger_position', '')).lower() else ''}
        ├─ MACD: {indicators.get('macd_signal', 'Neutral')} {'📈 BULLISH DIVERGENCE' if 'bullish' in str(indicators.get('macd_signal', '')).lower() else '📉 BEARISH DIVERGENCE' if 'bearish' in str(indicators.get('macd_signal', '')).lower() else ''}
        ├─ Stochastic [{indicators.get('stochastic', 50)}]: {'⚡ OVERSOLD' if indicators.get('stochastic', 50) < 20 else '⚡ OVERBOUGHT' if indicators.get('stochastic', 50) > 80 else 'NEUTRAL'}
        ├─ SuperTrend: {indicators.get('supertrend', 'Neutral')} {'🟢 STRONG BUY' if indicators.get('supertrend') == 'BUY' else '🔴 STRONG SELL' if indicators.get('supertrend') == 'SELL' else '⚪'}
        ├─ ADX [{indicators.get('adx', 25)}]: {'💪 STRONG TREND' if indicators.get('adx', 25) > 25 else '😴 WEAK/NO TREND'} {'+DI CROSS UP 📈' if indicators.get('di_cross') == 'bullish' else '-DI CROSS DOWN 📉' if indicators.get('di_cross') == 'bearish' else ''}
        ├─ Heikin Ashi: {indicators.get('heikin_ashi', 'Neutral')} {'🟩 BULLISH CANDLES' if indicators.get('heikin_ashi') == 'bullish' else '🟥 BEARISH CANDLES' if indicators.get('heikin_ashi') == 'bearish' else '⬜ DOJI - REVERSAL?' if indicators.get('heikin_ashi') == 'doji' else ''}
        ├─ VWAP: Price vs VWAP: {indicators.get('vwap_position', 'At VWAP')} {'🚀 ABOVE +2σ EXTREME BUY' if indicators.get('vwap_deviation', 0) > 2 else '⚠️ ABOVE +1σ OVERBOUGHT' if indicators.get('vwap_deviation', 0) > 1 else '💀 BELOW -2σ EXTREME SELL' if indicators.get('vwap_deviation', 0) < -2 else '⚠️ BELOW -1σ OVERSOLD' if indicators.get('vwap_deviation', 0) < -1 else '✅ FAIR VALUE'} | Volume: {'🔥 INSTITUTIONAL' if indicators.get('vwap_volume') == 'high' else '📊 NORMAL'}
        └─ Volume Profile: {indicators.get('volume_trend', 'Normal')} {'🔥 BREAKOUT IMMINENT' if indicators.get('volume_trend') == 'Surge' else ''}

        🏆 AI PERFORMANCE METRICS:
        ├─ Session Win Rate: {market_data.get('win_rate', 0)}%
        ├─ Pattern Recognition: {market_data.get('pattern_confidence', 85)}% confidence
        └─ Risk Level: {market_data.get('risk_level', 'MEDIUM')}

        ULTRA POWERFUL DECISION REQUIRED:
        Analyze ALL signals with EXTREME precision. Look for:
        1. Multiple indicator convergence (3+ signals aligned)
        2. Volume confirmation of price movement
        3. Momentum acceleration patterns
        4. Support/Resistance proximity
        5. Hidden divergences and micro-patterns

        BE AGGRESSIVE on high-confidence setups (80%+)
        BE CAUTIOUS on mixed signals (<70%)

        OUTPUT YOUR ULTRA DECISION:
        ACTION: [CALL/PUT/HOLD]
        CONFIDENCE: [0-100]
        REASON: [Sharp, decisive reasoning - mention specific convergence]
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
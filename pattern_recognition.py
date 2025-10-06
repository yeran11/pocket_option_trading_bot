"""
🕯️ CANDLESTICK PATTERN RECOGNITION SYSTEM
Advanced pattern detection for trading bot - engulfing, doji, hammer, shooting star, etc.
Provides quality scoring based on context (support/resistance, RSI, volume, regime)
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class PatternRecognizer:
    """
    Detects and analyzes candlestick patterns across multiple timeframes
    """

    def __init__(self):
        self.patterns_detected = []
        self.pattern_history_file = "pattern_history.json"
        self.load_pattern_history()

    def load_pattern_history(self):
        """Load historical pattern performance data"""
        if os.path.exists(self.pattern_history_file):
            try:
                with open(self.pattern_history_file, 'r') as f:
                    self.pattern_history = json.load(f)
            except:
                self.pattern_history = {}
        else:
            self.pattern_history = {}

    def save_pattern_history(self):
        """Save pattern performance data"""
        try:
            with open(self.pattern_history_file, 'w') as f:
                json.dump(self.pattern_history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save pattern history: {e}")

    # ==================== ENGULFING PATTERNS ====================

    def detect_engulfing_pattern(self, candles: List, min_body_ratio: float = 1.5) -> Dict:
        """
        Detect bullish and bearish engulfing patterns

        Args:
            candles: List of candles [timestamp, open, close, high, low, volume]
            min_body_ratio: Minimum ratio of engulfing body to engulfed body (default 1.5x)

        Returns:
            {
                'pattern': 'bullish_engulfing' | 'bearish_engulfing' | None,
                'strength': 0-100,
                'candle_index': index of engulfing candle,
                'body_ratio': how much larger the engulfing candle is,
                'volume_confirmation': True/False
            }
        """
        if len(candles) < 2:
            return {'pattern': None, 'strength': 0}

        # Get last two candles
        prev_candle = candles[-2]
        curr_candle = candles[-1]

        prev_open = float(prev_candle[1])
        prev_close = float(prev_candle[2])
        prev_high = float(prev_candle[3])
        prev_low = float(prev_candle[4])
        prev_volume = float(prev_candle[5]) if len(prev_candle) > 5 else 0

        curr_open = float(curr_candle[1])
        curr_close = float(curr_candle[2])
        curr_high = float(curr_candle[3])
        curr_low = float(curr_candle[4])
        curr_volume = float(curr_candle[5]) if len(curr_candle) > 5 else 0

        # Calculate body sizes
        prev_body = abs(prev_close - prev_open)
        curr_body = abs(curr_close - curr_open)

        # Avoid division by zero
        if prev_body == 0:
            return {'pattern': None, 'strength': 0}

        body_ratio = curr_body / prev_body

        # Volume confirmation (current candle has higher volume)
        volume_confirmation = curr_volume > prev_volume if prev_volume > 0 else False

        # BULLISH ENGULFING
        # Previous candle is bearish (red), current is bullish (green)
        # Current candle's body completely engulfs previous candle's body
        if prev_close < prev_open and curr_close > curr_open:
            # Check if current candle engulfs previous
            if curr_open <= prev_close and curr_close >= prev_open:
                # Calculate strength (0-100)
                strength = min(100, int(body_ratio * 40))  # Base strength from body ratio

                # Bonus points
                if body_ratio >= min_body_ratio:
                    strength += 20
                if volume_confirmation:
                    strength += 15
                if curr_close > prev_high:  # Closes above previous high
                    strength += 10
                if body_ratio >= 2.0:  # Very strong engulfing
                    strength += 15

                strength = min(100, strength)

                return {
                    'pattern': 'bullish_engulfing',
                    'strength': strength,
                    'candle_index': len(candles) - 1,
                    'body_ratio': round(body_ratio, 2),
                    'volume_confirmation': volume_confirmation,
                    'prev_candle': {'open': prev_open, 'close': prev_close, 'high': prev_high, 'low': prev_low},
                    'curr_candle': {'open': curr_open, 'close': curr_close, 'high': curr_high, 'low': curr_low}
                }

        # BEARISH ENGULFING
        # Previous candle is bullish (green), current is bearish (red)
        # Current candle's body completely engulfs previous candle's body
        elif prev_close > prev_open and curr_close < curr_open:
            # Check if current candle engulfs previous
            if curr_open >= prev_close and curr_close <= prev_open:
                # Calculate strength (0-100)
                strength = min(100, int(body_ratio * 40))

                # Bonus points
                if body_ratio >= min_body_ratio:
                    strength += 20
                if volume_confirmation:
                    strength += 15
                if curr_close < prev_low:  # Closes below previous low
                    strength += 10
                if body_ratio >= 2.0:
                    strength += 15

                strength = min(100, strength)

                return {
                    'pattern': 'bearish_engulfing',
                    'strength': strength,
                    'candle_index': len(candles) - 1,
                    'body_ratio': round(body_ratio, 2),
                    'volume_confirmation': volume_confirmation,
                    'prev_candle': {'open': prev_open, 'close': prev_close, 'high': prev_high, 'low': prev_low},
                    'curr_candle': {'open': curr_open, 'close': curr_close, 'high': curr_high, 'low': curr_low}
                }

        return {'pattern': None, 'strength': 0}

    # ==================== DOJI PATTERNS ====================

    def detect_doji(self, candles: List, doji_threshold: float = 0.1) -> Dict:
        """
        Detect doji candles (open ≈ close, indicates indecision)

        Args:
            candles: List of candles
            doji_threshold: Max body size as % of total range (default 10%)

        Returns:
            {
                'pattern': 'doji' | None,
                'type': 'standard' | 'dragonfly' | 'gravestone',
                'strength': 0-100,
                'indecision_score': 0-100
            }
        """
        if len(candles) < 1:
            return {'pattern': None, 'strength': 0}

        candle = candles[-1]
        open_price = float(candle[1])
        close_price = float(candle[2])
        high_price = float(candle[3])
        low_price = float(candle[4])

        # Calculate ranges
        body = abs(close_price - open_price)
        total_range = high_price - low_price

        if total_range == 0:
            return {'pattern': None, 'strength': 0}

        body_percentage = (body / total_range) * 100

        # Doji if body is less than threshold % of total range
        if body_percentage <= doji_threshold * 100:
            # Determine doji type
            upper_shadow = high_price - max(open_price, close_price)
            lower_shadow = min(open_price, close_price) - low_price

            if lower_shadow > upper_shadow * 2:
                doji_type = 'dragonfly'  # Long lower shadow (bullish reversal)
                strength = 75
            elif upper_shadow > lower_shadow * 2:
                doji_type = 'gravestone'  # Long upper shadow (bearish reversal)
                strength = 75
            else:
                doji_type = 'standard'  # Equal shadows (high indecision)
                strength = 60

            return {
                'pattern': 'doji',
                'type': doji_type,
                'strength': strength,
                'indecision_score': int((1 - body_percentage / 10) * 100),
                'body_percentage': round(body_percentage, 2)
            }

        return {'pattern': None, 'strength': 0}

    # ==================== HAMMER & SHOOTING STAR ====================

    def detect_hammer_shooting_star(self, candles: List) -> Dict:
        """
        Detect hammer (bullish reversal) and shooting star (bearish reversal) patterns

        Returns:
            {
                'pattern': 'hammer' | 'shooting_star' | None,
                'strength': 0-100
            }
        """
        if len(candles) < 1:
            return {'pattern': None, 'strength': 0}

        candle = candles[-1]
        open_price = float(candle[1])
        close_price = float(candle[2])
        high_price = float(candle[3])
        low_price = float(candle[4])

        body = abs(close_price - open_price)
        total_range = high_price - low_price

        if total_range == 0:
            return {'pattern': None, 'strength': 0}

        upper_shadow = high_price - max(open_price, close_price)
        lower_shadow = min(open_price, close_price) - low_price

        # HAMMER: Small body at top, long lower shadow (2x+ body size)
        if lower_shadow >= body * 2 and upper_shadow < body * 0.5:
            strength = min(100, int((lower_shadow / body) * 30))
            return {
                'pattern': 'hammer',
                'strength': strength,
                'lower_shadow_ratio': round(lower_shadow / body, 2)
            }

        # SHOOTING STAR: Small body at bottom, long upper shadow (2x+ body size)
        if upper_shadow >= body * 2 and lower_shadow < body * 0.5:
            strength = min(100, int((upper_shadow / body) * 30))
            return {
                'pattern': 'shooting_star',
                'strength': strength,
                'upper_shadow_ratio': round(upper_shadow / body, 2)
            }

        return {'pattern': None, 'strength': 0}

    # ==================== CONTEXT QUALITY SCORING ====================

    def evaluate_pattern_quality(self, pattern: Dict, indicators: Dict, regime: str,
                                  support_resistance: Optional[Dict] = None) -> Dict:
        """
        Evaluate pattern quality based on context (RSI, regime, support/resistance, etc.)

        Args:
            pattern: Pattern detection result
            indicators: Current market indicators (RSI, MACD, etc.)
            regime: Current market regime
            support_resistance: Support/resistance levels if available

        Returns:
            {
                'quality_score': 0-100,
                'trade_recommendation': 'strong_buy' | 'buy' | 'neutral' | 'sell' | 'strong_sell' | 'no_trade',
                'confidence': 0-100,
                'reasons': [list of why this pattern is good/bad]
            }
        """
        if not pattern or pattern.get('pattern') is None:
            return {'quality_score': 0, 'trade_recommendation': 'no_trade', 'confidence': 0, 'reasons': []}

        quality_score = pattern.get('strength', 50)
        reasons = []

        pattern_type = pattern['pattern']

        # BULLISH ENGULFING QUALITY
        if pattern_type == 'bullish_engulfing':
            # Check RSI (oversold is better)
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                quality_score += 20
                reasons.append("✅ RSI oversold (high reversal probability)")
            elif rsi < 40:
                quality_score += 10
                reasons.append("✅ RSI below 40")

            # Check regime (best in downtrend reversal)
            if regime in ['trending_down', 'high_volatility']:
                quality_score += 15
                reasons.append("✅ Potential downtrend reversal")

            # Check MACD (bullish cross is confirmation)
            macd_histogram = indicators.get('macd_histogram', 0)
            if macd_histogram > 0:
                quality_score += 10
                reasons.append("✅ MACD bullish")

            # Volume confirmation
            if pattern.get('volume_confirmation'):
                quality_score += 15
                reasons.append("✅ High volume confirmation")

            # Strong body ratio
            if pattern.get('body_ratio', 1) >= 2.0:
                quality_score += 10
                reasons.append("✅ Very strong engulfing (2x+ body)")

        # BEARISH ENGULFING QUALITY
        elif pattern_type == 'bearish_engulfing':
            # Check RSI (overbought is better)
            rsi = indicators.get('rsi', 50)
            if rsi > 70:
                quality_score += 20
                reasons.append("✅ RSI overbought (high reversal probability)")
            elif rsi > 60:
                quality_score += 10
                reasons.append("✅ RSI above 60")

            # Check regime (best in uptrend reversal)
            if regime in ['trending_up', 'high_volatility']:
                quality_score += 15
                reasons.append("✅ Potential uptrend reversal")

            # Check MACD (bearish cross is confirmation)
            macd_histogram = indicators.get('macd_histogram', 0)
            if macd_histogram < 0:
                quality_score += 10
                reasons.append("✅ MACD bearish")

            # Volume confirmation
            if pattern.get('volume_confirmation'):
                quality_score += 15
                reasons.append("✅ High volume confirmation")

            # Strong body ratio
            if pattern.get('body_ratio', 1) >= 2.0:
                quality_score += 10
                reasons.append("✅ Very strong engulfing (2x+ body)")

        # HAMMER QUALITY (bullish at support)
        elif pattern_type == 'hammer':
            rsi = indicators.get('rsi', 50)
            if rsi < 35:
                quality_score += 25
                reasons.append("✅ Hammer at oversold levels")

            if regime == 'trending_down':
                quality_score += 20
                reasons.append("✅ Hammer in downtrend (reversal signal)")

        # SHOOTING STAR QUALITY (bearish at resistance)
        elif pattern_type == 'shooting_star':
            rsi = indicators.get('rsi', 50)
            if rsi > 65:
                quality_score += 25
                reasons.append("✅ Shooting star at overbought levels")

            if regime == 'trending_up':
                quality_score += 20
                reasons.append("✅ Shooting star in uptrend (reversal signal)")

        # DOJI QUALITY (context-dependent)
        elif pattern_type == 'doji':
            doji_type = pattern.get('type', 'standard')

            if doji_type == 'dragonfly' and regime == 'trending_down':
                quality_score += 20
                reasons.append("✅ Dragonfly doji in downtrend (bullish reversal)")
            elif doji_type == 'gravestone' and regime == 'trending_up':
                quality_score += 20
                reasons.append("✅ Gravestone doji in uptrend (bearish reversal)")
            else:
                quality_score -= 10
                reasons.append("⚠️ Doji shows indecision (wait for confirmation)")

        # Cap quality score at 100
        quality_score = min(100, quality_score)

        # Determine trade recommendation
        if quality_score >= 85:
            recommendation = 'strong_buy' if pattern_type in ['bullish_engulfing', 'hammer', 'dragonfly'] else 'strong_sell'
            confidence = quality_score
        elif quality_score >= 70:
            recommendation = 'buy' if pattern_type in ['bullish_engulfing', 'hammer', 'dragonfly'] else 'sell'
            confidence = quality_score
        elif quality_score >= 50:
            recommendation = 'neutral'
            confidence = 50
        else:
            recommendation = 'no_trade'
            confidence = 30
            reasons.append("❌ Low quality pattern - skip trade")

        return {
            'quality_score': quality_score,
            'trade_recommendation': recommendation,
            'confidence': confidence,
            'reasons': reasons
        }

    # ==================== MULTI-TIMEFRAME PATTERN DETECTION ====================

    def detect_all_patterns_mtf(self, candles_1m: List, candles_5m: List = None,
                                 candles_15m: List = None) -> Dict:
        """
        Detect all patterns across multiple timeframes

        Returns:
            {
                '1m': {'engulfing': {...}, 'doji': {...}, 'hammer': {...}},
                '5m': {...},
                '15m': {...},
                'strongest_signal': {'timeframe': '5m', 'pattern': 'bullish_engulfing', 'strength': 85}
            }
        """
        results = {}

        # Detect on 1m
        results['1m'] = self._detect_all_patterns_single_tf(candles_1m)

        # Detect on 5m if available
        if candles_5m and len(candles_5m) >= 2:
            results['5m'] = self._detect_all_patterns_single_tf(candles_5m)

        # Detect on 15m if available
        if candles_15m and len(candles_15m) >= 2:
            results['15m'] = self._detect_all_patterns_single_tf(candles_15m)

        # Find strongest signal across all timeframes
        strongest_signal = {'timeframe': None, 'pattern': None, 'strength': 0}

        for tf, patterns in results.items():
            for pattern_name, pattern_data in patterns.items():
                if pattern_data.get('pattern') and pattern_data.get('strength', 0) > strongest_signal['strength']:
                    strongest_signal = {
                        'timeframe': tf,
                        'pattern': pattern_data['pattern'],
                        'strength': pattern_data['strength'],
                        'data': pattern_data
                    }

        results['strongest_signal'] = strongest_signal

        return results

    def _detect_all_patterns_single_tf(self, candles: List) -> Dict:
        """Detect all pattern types on a single timeframe"""
        return {
            'engulfing': self.detect_engulfing_pattern(candles),
            'doji': self.detect_doji(candles),
            'hammer_star': self.detect_hammer_shooting_star(candles)
        }

    # ==================== PATTERN PERFORMANCE TRACKING ====================

    def record_pattern_trade(self, pattern_type: str, result: str, profit: float,
                             quality_score: int, indicators: Dict):
        """
        Record trade result for a pattern to build performance history

        Args:
            pattern_type: 'bullish_engulfing', 'bearish_engulfing', etc.
            result: 'win' or 'loss'
            profit: Profit/loss amount
            quality_score: The quality score given to the pattern
            indicators: Market indicators at time of trade
        """
        if pattern_type not in self.pattern_history:
            self.pattern_history[pattern_type] = {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'total_profit': 0.0,
                'avg_quality_score': 0,
                'trades': []
            }

        self.pattern_history[pattern_type]['total_trades'] += 1

        if result == 'win':
            self.pattern_history[pattern_type]['wins'] += 1
        else:
            self.pattern_history[pattern_type]['losses'] += 1

        self.pattern_history[pattern_type]['total_profit'] += profit

        # Update avg quality score
        trades = self.pattern_history[pattern_type]['total_trades']
        current_avg = self.pattern_history[pattern_type]['avg_quality_score']
        new_avg = ((current_avg * (trades - 1)) + quality_score) / trades
        self.pattern_history[pattern_type]['avg_quality_score'] = new_avg

        # Store trade details (keep last 100 trades)
        trade_data = {
            'timestamp': datetime.now().isoformat(),
            'result': result,
            'profit': profit,
            'quality_score': quality_score,
            'rsi': indicators.get('rsi', 0),
            'regime': indicators.get('regime', 'unknown')
        }

        self.pattern_history[pattern_type]['trades'].append(trade_data)

        # Keep only last 100 trades
        if len(self.pattern_history[pattern_type]['trades']) > 100:
            self.pattern_history[pattern_type]['trades'] = self.pattern_history[pattern_type]['trades'][-100:]

        self.save_pattern_history()

    def get_pattern_performance(self, pattern_type: str = None) -> Dict:
        """
        Get performance statistics for a specific pattern or all patterns

        Args:
            pattern_type: Specific pattern to query, or None for all patterns

        Returns:
            Performance data with win rates, profitability, etc.
        """
        if pattern_type:
            if pattern_type in self.pattern_history:
                data = self.pattern_history[pattern_type]
                win_rate = (data['wins'] / data['total_trades'] * 100) if data['total_trades'] > 0 else 0
                return {
                    'pattern': pattern_type,
                    'win_rate': round(win_rate, 1),
                    'total_trades': data['total_trades'],
                    'wins': data['wins'],
                    'losses': data['losses'],
                    'total_profit': round(data['total_profit'], 2),
                    'avg_quality_score': round(data['avg_quality_score'], 1)
                }
            else:
                return {'pattern': pattern_type, 'win_rate': 0, 'total_trades': 0}
        else:
            # Return all patterns
            performance = {}
            for pattern, data in self.pattern_history.items():
                win_rate = (data['wins'] / data['total_trades'] * 100) if data['total_trades'] > 0 else 0
                performance[pattern] = {
                    'win_rate': round(win_rate, 1),
                    'total_trades': data['total_trades'],
                    'total_profit': round(data['total_profit'], 2)
                }
            return performance

    # ==================== AI CONTEXT GENERATION ====================

    def get_pattern_context_for_ai(self, mtf_patterns: Dict, indicators: Dict, regime: str) -> str:
        """
        Generate formatted context string for AI prompt with pattern analysis

        Args:
            mtf_patterns: Multi-timeframe pattern detection results
            indicators: Current market indicators
            regime: Current market regime

        Returns:
            Formatted string for AI prompt
        """
        context_lines = []
        context_lines.append("\n🕯️ ==================== CANDLESTICK PATTERN ANALYSIS ====================")

        strongest = mtf_patterns.get('strongest_signal', {})

        if strongest.get('pattern'):
            pattern_name = strongest['pattern'].replace('_', ' ').upper()
            timeframe = strongest['timeframe'].upper()
            strength = strongest['strength']

            context_lines.append(f"\n🎯 STRONGEST PATTERN: {pattern_name} on {timeframe} (Strength: {strength}%)")

            # Get quality evaluation
            quality = self.evaluate_pattern_quality(
                strongest.get('data', {}),
                indicators,
                regime
            )

            context_lines.append(f"├─ Quality Score: {quality['quality_score']}/100")
            context_lines.append(f"├─ Recommendation: {quality['trade_recommendation'].upper()}")
            context_lines.append(f"└─ AI Confidence: {quality['confidence']}%")

            if quality['reasons']:
                context_lines.append("\n📋 PATTERN QUALITY FACTORS:")
                for reason in quality['reasons']:
                    context_lines.append(f"   {reason}")

            # Historical performance
            pattern_perf = self.get_pattern_performance(strongest['pattern'])
            if pattern_perf.get('total_trades', 0) > 0:
                context_lines.append(f"\n📊 HISTORICAL PERFORMANCE ({strongest['pattern']}):")
                context_lines.append(f"├─ Win Rate: {pattern_perf['win_rate']}%")
                context_lines.append(f"├─ Total Trades: {pattern_perf['total_trades']}")
                context_lines.append(f"└─ Total Profit: ${pattern_perf['total_profit']}")

        # Show all detected patterns by timeframe
        context_lines.append("\n🔍 ALL DETECTED PATTERNS:")

        for tf in ['1m', '5m', '15m']:
            if tf in mtf_patterns:
                tf_patterns = mtf_patterns[tf]
                detected = []

                for pattern_type, pattern_data in tf_patterns.items():
                    if pattern_data.get('pattern'):
                        pattern_name = pattern_data['pattern'].replace('_', ' ').title()
                        strength = pattern_data.get('strength', 0)
                        detected.append(f"{pattern_name} ({strength}%)")

                if detected:
                    context_lines.append(f"├─ {tf.upper()}: {', '.join(detected)}")

        context_lines.append("=" * 75)

        return '\n'.join(context_lines)


# ==================== GLOBAL INSTANCE ====================

_pattern_recognizer_instance = None

def get_recognizer() -> PatternRecognizer:
    """Get global pattern recognizer instance"""
    global _pattern_recognizer_instance
    if _pattern_recognizer_instance is None:
        _pattern_recognizer_instance = PatternRecognizer()
    return _pattern_recognizer_instance


# ==================== UTILITY FUNCTIONS ====================

def detect_engulfing_simple(candles: List) -> Tuple[Optional[str], int]:
    """
    Simple helper function to detect engulfing patterns
    Returns: (pattern_type, strength) or (None, 0)
    """
    recognizer = get_recognizer()
    result = recognizer.detect_engulfing_pattern(candles)
    return (result.get('pattern'), result.get('strength', 0))


def get_best_pattern(candles_1m: List, candles_5m: List = None, candles_15m: List = None) -> Dict:
    """
    Simple helper to get the best pattern across all timeframes
    Returns: {'pattern': 'bullish_engulfing', 'timeframe': '5m', 'strength': 85, ...}
    """
    recognizer = get_recognizer()
    mtf_patterns = recognizer.detect_all_patterns_mtf(candles_1m, candles_5m, candles_15m)
    return mtf_patterns.get('strongest_signal', {})


if __name__ == "__main__":
    print("🕯️ Pattern Recognition System - Test Mode")
    print("=" * 75)

    # Test with sample candles
    sample_candles = [
        [1704067200000, 1.1050, 1.1045, 1.1055, 1.1040, 1000],  # Red candle
        [1704067260000, 1.1045, 1.1065, 1.1070, 1.1042, 1500],  # Strong green engulfing
    ]

    recognizer = get_recognizer()

    # Test engulfing detection
    engulfing = recognizer.detect_engulfing_pattern(sample_candles)
    print(f"\n✅ Engulfing Pattern Test:")
    print(f"   Pattern: {engulfing.get('pattern', 'None')}")
    print(f"   Strength: {engulfing.get('strength', 0)}%")
    print(f"   Body Ratio: {engulfing.get('body_ratio', 0)}x")

    # Test quality evaluation
    test_indicators = {'rsi': 28.5, 'macd_histogram': 0.5}
    quality = recognizer.evaluate_pattern_quality(engulfing, test_indicators, 'trending_down')

    print(f"\n✅ Quality Evaluation:")
    print(f"   Quality Score: {quality['quality_score']}/100")
    print(f"   Recommendation: {quality['trade_recommendation']}")
    print(f"   Reasons:")
    for reason in quality['reasons']:
        print(f"      {reason}")

    print("\n" + "=" * 75)
    print("✅ Pattern Recognition System Ready!")

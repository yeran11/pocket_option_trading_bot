"""
Market Regime Detection - Identify current market state
Detects: Trending Up, Trending Down, Ranging, High Volatility, Low Volatility
"""

from typing import Dict, List, Tuple, Optional
import statistics


class MarketRegimeDetector:
    """
    Detect market regime to apply appropriate trading strategies

    Regimes:
    1. TRENDING_UP - Strong uptrend (trade CALLs primarily)
    2. TRENDING_DOWN - Strong downtrend (trade PUTs primarily)
    3. RANGING - Sideways/choppy (mean reversion strategies)
    4. HIGH_VOLATILITY - Large price swings (reduce position size)
    5. LOW_VOLATILITY - Tight range (wait for breakout or skip)
    """

    def __init__(self):
        self.regime_history = []

    async def detect_regime(
        self,
        candles_1m: List,
        candles_5m: Optional[List] = None,
        candles_15m: Optional[List] = None,
        indicators: Optional[Dict] = None
    ) -> Tuple[str, float, str]:
        """
        Detect current market regime using multiple timeframes and indicators

        Returns: (regime, confidence, description)

        regime: 'trending_up', 'trending_down', 'ranging', 'high_volatility', 'low_volatility'
        confidence: 0-100 score
        description: Human-readable explanation
        """
        if not candles_1m or len(candles_1m) < 20:
            return ('unknown', 0.0, 'Insufficient data')

        # Extract prices for analysis
        prices_1m = [c[2] for c in candles_1m[-50:]]  # Last 50 candles
        highs_1m = [c[3] for c in candles_1m[-20:]]
        lows_1m = [c[4] for c in candles_1m[-20:]]

        # Calculate key metrics
        current_price = prices_1m[-1]

        # Trend strength (slope of prices)
        trend_slope = self._calculate_trend_slope(prices_1m)

        # Volatility (ATR-like measure)
        volatility = self._calculate_volatility(highs_1m, lows_1m, prices_1m)

        # Range detection (price confined to narrow band)
        is_ranging = self._detect_ranging(prices_1m, volatility)

        # Higher timeframe alignment (if available)
        htf_trend = self._detect_higher_timeframe_trend(candles_5m, candles_15m)

        # Use indicators if provided
        indicator_signals = self._analyze_indicators(indicators) if indicators else {}

        # Decision logic
        regime, confidence, description = self._determine_regime(
            trend_slope=trend_slope,
            volatility=volatility,
            is_ranging=is_ranging,
            htf_trend=htf_trend,
            indicator_signals=indicator_signals,
            current_price=current_price
        )

        # Record in history
        self.regime_history.append({
            'regime': regime,
            'confidence': confidence,
            'trend_slope': trend_slope,
            'volatility': volatility
        })

        # Keep only last 100 records
        if len(self.regime_history) > 100:
            self.regime_history.pop(0)

        return (regime, confidence, description)

    def _calculate_trend_slope(self, prices: List[float]) -> float:
        """
        Calculate trend slope using linear regression
        Positive = uptrend, Negative = downtrend, Near zero = ranging
        """
        if len(prices) < 10:
            return 0.0

        n = len(prices)
        x_values = list(range(n))
        y_values = prices

        # Simple linear regression
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)

        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Normalize slope to -1 to +1 range (approximately)
        # Scale by price to get percentage slope
        avg_price = y_mean if y_mean > 0 else 1
        normalized_slope = (slope / avg_price) * 1000  # Scale up for visibility

        return max(-1.0, min(1.0, normalized_slope))

    def _calculate_volatility(self, highs: List[float], lows: List[float], closes: List[float]) -> float:
        """
        Calculate volatility (similar to ATR)
        Returns normalized volatility score (0-1)
        """
        if not highs or not lows or len(highs) < 2:
            return 0.0

        # True Range calculation
        true_ranges = []
        for i in range(1, len(highs)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            true_ranges.append(tr)

        if not true_ranges:
            return 0.0

        # Average True Range
        atr = statistics.mean(true_ranges)

        # Normalize by current price
        current_price = closes[-1] if closes else 1
        normalized_volatility = (atr / current_price) * 100 if current_price > 0 else 0

        # Clamp to 0-1 range (volatility over 5% is considered very high)
        return min(1.0, normalized_volatility / 5.0)

    def _detect_ranging(self, prices: List[float], volatility: float) -> bool:
        """
        Detect if market is ranging (sideways movement)
        """
        if len(prices) < 20:
            return False

        # Check if price is mostly within a narrow band
        recent_high = max(prices[-20:])
        recent_low = min(prices[-20:])
        price_range = recent_high - recent_low

        avg_price = statistics.mean(prices[-20:])
        range_percent = (price_range / avg_price) * 100 if avg_price > 0 else 0

        # If price stays within 1% range and volatility is low, it's ranging
        is_narrow_range = range_percent < 1.0
        is_low_volatility = volatility < 0.3

        return is_narrow_range and is_low_volatility

    def _detect_higher_timeframe_trend(
        self,
        candles_5m: Optional[List],
        candles_15m: Optional[List]
    ) -> str:
        """
        Detect trend from higher timeframes
        Returns: 'up', 'down', 'neutral'
        """
        trends = []

        # 5-minute trend
        if candles_5m and len(candles_5m) >= 20:
            prices_5m = [c[2] for c in candles_5m[-20:]]
            slope_5m = self._calculate_trend_slope(prices_5m)

            if slope_5m > 0.2:
                trends.append('up')
            elif slope_5m < -0.2:
                trends.append('down')
            else:
                trends.append('neutral')

        # 15-minute trend
        if candles_15m and len(candles_15m) >= 20:
            prices_15m = [c[2] for c in candles_15m[-20:]]
            slope_15m = self._calculate_trend_slope(prices_15m)

            if slope_15m > 0.2:
                trends.append('up')
            elif slope_15m < -0.2:
                trends.append('down')
            else:
                trends.append('neutral')

        # Consensus from higher timeframes
        if not trends:
            return 'neutral'

        up_count = trends.count('up')
        down_count = trends.count('down')

        if up_count > down_count:
            return 'up'
        elif down_count > up_count:
            return 'down'
        else:
            return 'neutral'

    def _analyze_indicators(self, indicators: Dict) -> Dict:
        """
        Extract trend signals from indicators
        """
        signals = {
            'trend': 'neutral',
            'strength': 0.5
        }

        # EMA cross
        if 'ema_cross' in indicators:
            if indicators['ema_cross'] == 'Bullish':
                signals['trend'] = 'up'
                signals['strength'] = 0.7
            elif indicators['ema_cross'] == 'Bearish':
                signals['trend'] = 'down'
                signals['strength'] = 0.7

        # SuperTrend
        if 'supertrend' in indicators:
            if indicators['supertrend'] == 'BUY':
                signals['trend'] = 'up' if signals['trend'] != 'down' else 'neutral'
                signals['strength'] = min(1.0, signals['strength'] + 0.2)
            elif indicators['supertrend'] == 'SELL':
                signals['trend'] = 'down' if signals['trend'] != 'up' else 'neutral'
                signals['strength'] = min(1.0, signals['strength'] + 0.2)

        # ADX (trend strength)
        if 'adx' in indicators:
            adx = indicators['adx']
            if adx > 25:
                signals['strength'] = min(1.0, signals['strength'] + 0.2)

        return signals

    def _determine_regime(
        self,
        trend_slope: float,
        volatility: float,
        is_ranging: bool,
        htf_trend: str,
        indicator_signals: Dict,
        current_price: float
    ) -> Tuple[str, float, str]:
        """
        Determine market regime from all signals
        Returns: (regime, confidence, description)
        """
        # High volatility check first
        if volatility > 0.7:
            return (
                'high_volatility',
                85.0,
                f"⚡ High volatility detected ({volatility*100:.1f}%). Reduce position sizes!"
            )

        # Low volatility / ranging check
        if is_ranging or volatility < 0.2:
            return (
                'low_volatility',
                80.0,
                f"😴 Low volatility / ranging market ({volatility*100:.1f}%). Wait for breakout or use mean reversion."
            )

        # Trending up check
        bullish_signals = 0
        bearish_signals = 0

        if trend_slope > 0.3:
            bullish_signals += 2
        elif trend_slope > 0.1:
            bullish_signals += 1

        if trend_slope < -0.3:
            bearish_signals += 2
        elif trend_slope < -0.1:
            bearish_signals += 1

        if htf_trend == 'up':
            bullish_signals += 2
        elif htf_trend == 'down':
            bearish_signals += 2

        if indicator_signals.get('trend') == 'up':
            bullish_signals += 1
        elif indicator_signals.get('trend') == 'down':
            bearish_signals += 1

        # Determine regime
        total_signals = bullish_signals + bearish_signals

        if bullish_signals >= 3 and bullish_signals > bearish_signals:
            confidence = min(95.0, 60 + (bullish_signals * 10))
            return (
                'trending_up',
                confidence,
                f"📈 UPTREND detected (slope: {trend_slope:.2f}). Favor CALL trades. Higher timeframe: {htf_trend.upper()}"
            )

        elif bearish_signals >= 3 and bearish_signals > bullish_signals:
            confidence = min(95.0, 60 + (bearish_signals * 10))
            return (
                'trending_down',
                confidence,
                f"📉 DOWNTREND detected (slope: {trend_slope:.2f}). Favor PUT trades. Higher timeframe: {htf_trend.upper()}"
            )

        else:
            # Not enough signals for clear trend
            return (
                'ranging',
                70.0,
                f"↔️ RANGING / MIXED signals. Use mean reversion strategies. Trend slope: {trend_slope:.2f}"
            )

    def get_trading_recommendation(self, regime: str, action: str) -> Tuple[bool, str]:
        """
        Get recommendation whether to take a trade based on regime alignment

        Args:
            regime: Current market regime
            action: Proposed trade action ('call' or 'put')

        Returns: (should_trade, reason)
        """
        if regime == 'low_volatility':
            return (False, "🛑 Low volatility - wait for clearer setup")

        if regime == 'high_volatility':
            return (True, "⚠️ High volatility - REDUCE position size by 50%")

        if regime == 'trending_up':
            if action == 'call':
                return (True, "✅ CALL aligns with UPTREND - EXCELLENT setup!")
            else:
                return (False, "⚠️ PUT against UPTREND - risky, skip unless very high confidence")

        if regime == 'trending_down':
            if action == 'put':
                return (True, "✅ PUT aligns with DOWNTREND - EXCELLENT setup!")
            else:
                return (False, "⚠️ CALL against DOWNTREND - risky, skip unless very high confidence")

        if regime == 'ranging':
            return (True, "⚙️ RANGING market - use mean reversion, expect quick reversals")

        return (True, "Regime unknown - proceed with caution")


# Global instance
_detector_instance = None

def get_detector() -> MarketRegimeDetector:
    """Get or create global market regime detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = MarketRegimeDetector()
    return _detector_instance

"""
Multi-Timeframe Analysis - Aggregate and analyze multiple timeframes
Converts 1-minute candles to 5-minute and 15-minute for bigger picture analysis
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta


class MultiTimeframeAnalyzer:
    """
    Aggregate 1-minute candles into higher timeframes
    Analyze trend alignment across timeframes
    """

    def __init__(self):
        self.candle_cache = {
            '1m': [],
            '5m': [],
            '15m': []
        }

    def aggregate_candles(self, candles_1m: List, timeframe_minutes: int) -> List:
        """
        Aggregate 1-minute candles into higher timeframe

        Args:
            candles_1m: List of 1-minute candles [[timestamp, open, close, high, low, volume], ...]
            timeframe_minutes: Target timeframe (5, 15, 30, 60, etc.)

        Returns:
            List of aggregated candles in same format
        """
        if not candles_1m or timeframe_minutes < 1:
            return []

        aggregated = []
        current_group = []
        group_start_time = None

        for candle in candles_1m:
            timestamp = candle[0]

            # Convert timestamp to datetime
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    dt = datetime.fromtimestamp(timestamp / 1000)  # Milliseconds
            elif isinstance(timestamp, (int, float)):
                dt = datetime.fromtimestamp(timestamp / 1000)  # Assume milliseconds
            else:
                dt = timestamp

            # Determine which group this candle belongs to
            minute_of_hour = dt.minute
            group_number = minute_of_hour // timeframe_minutes

            if group_start_time is None:
                group_start_time = group_number
                current_group = [candle]
            elif group_number == group_start_time:
                current_group.append(candle)
            else:
                # New group started, aggregate previous group
                if current_group:
                    agg_candle = self._aggregate_group(current_group)
                    aggregated.append(agg_candle)

                # Start new group
                current_group = [candle]
                group_start_time = group_number

        # Don't forget the last group
        if current_group:
            agg_candle = self._aggregate_group(current_group)
            aggregated.append(agg_candle)

        return aggregated

    def _aggregate_group(self, candle_group: List) -> List:
        """
        Aggregate a group of candles into one

        Args:
            candle_group: List of candles to aggregate

        Returns:
            Single aggregated candle [timestamp, open, close, high, low, volume]
        """
        if not candle_group:
            return None

        # Use first candle's timestamp
        timestamp = candle_group[0][0]

        # Open = first candle's open
        open_price = candle_group[0][1]

        # Close = last candle's close
        close_price = candle_group[-1][2]

        # High = highest of all highs
        high_price = max(c[3] for c in candle_group)

        # Low = lowest of all lows
        low_price = min(c[4] for c in candle_group)

        # Volume = sum of all volumes (if available)
        total_volume = sum(c[5] if len(c) > 5 else 0 for c in candle_group)

        return [timestamp, open_price, close_price, high_price, low_price, total_volume]

    def get_multi_timeframe_data(self, candles_1m: List) -> Dict:
        """
        Get 1m, 5m, and 15m candles from 1m source

        Returns:
            {
                '1m': [...],
                '5m': [...],
                '15m': [...]
            }
        """
        if not candles_1m:
            return {'1m': [], '5m': [], '15m': []}

        candles_5m = self.aggregate_candles(candles_1m, 5)
        candles_15m = self.aggregate_candles(candles_1m, 15)

        return {
            '1m': candles_1m,
            '5m': candles_5m,
            '15m': candles_15m
        }

    def analyze_trend_alignment(
        self,
        candles_1m: List,
        candles_5m: List,
        candles_15m: List
    ) -> Dict:
        """
        Analyze if trends are aligned across timeframes

        Returns:
            {
                'aligned': True/False,
                '1m_trend': 'up'/'down'/'neutral',
                '5m_trend': 'up'/'down'/'neutral',
                '15m_trend': 'up'/'down'/'neutral',
                'strength': 0-100 (confidence in trend),
                'recommendation': 'STRONG BUY' / 'BUY' / 'NEUTRAL' / 'SELL' / 'STRONG SELL'
            }
        """
        trends = {}

        # Analyze each timeframe
        for tf_name, candles in [('1m', candles_1m), ('5m', candles_5m), ('15m', candles_15m)]:
            if not candles or len(candles) < 3:
                trends[f'{tf_name}_trend'] = 'neutral'
                continue

            # Simple trend detection: compare current price to moving average
            recent_candles = candles[-20:] if len(candles) >= 20 else candles
            closes = [c[2] for c in recent_candles]

            current_price = closes[-1]
            avg_price = sum(closes) / len(closes)

            # Check slope (price momentum)
            if len(closes) >= 3:
                recent_slope = closes[-1] - closes[-3]
            else:
                recent_slope = 0

            # Determine trend
            if current_price > avg_price * 1.001 and recent_slope > 0:
                trends[f'{tf_name}_trend'] = 'up'
            elif current_price < avg_price * 0.999 and recent_slope < 0:
                trends[f'{tf_name}_trend'] = 'down'
            else:
                trends[f'{tf_name}_trend'] = 'neutral'

        # Check alignment
        trend_values = [trends.get(f'{tf}_trend') for tf in ['1m', '5m', '15m']]

        # Count trends
        up_count = trend_values.count('up')
        down_count = trend_values.count('down')
        neutral_count = trend_values.count('neutral')

        # Determine alignment
        aligned = False
        strength = 50
        recommendation = 'NEUTRAL'

        if up_count >= 2:
            aligned = up_count == 3
            strength = 60 + (up_count * 10)
            recommendation = 'STRONG BUY' if up_count == 3 else 'BUY'

        elif down_count >= 2:
            aligned = down_count == 3
            strength = 60 + (down_count * 10)
            recommendation = 'STRONG SELL' if down_count == 3 else 'SELL'

        return {
            'aligned': aligned,
            '1m_trend': trends.get('1m_trend', 'neutral'),
            '5m_trend': trends.get('5m_trend', 'neutral'),
            '15m_trend': trends.get('15m_trend', 'neutral'),
            'strength': strength,
            'recommendation': recommendation,
            'up_count': up_count,
            'down_count': down_count,
            'neutral_count': neutral_count
        }

    def get_higher_timeframe_context(
        self,
        candles_5m: List,
        candles_15m: List
    ) -> str:
        """
        Generate human-readable context about higher timeframes

        Returns:
            String description for AI or logging
        """
        if not candles_5m and not candles_15m:
            return "⚠️ Higher timeframe data not available"

        context_parts = []

        # 5-minute analysis
        if candles_5m and len(candles_5m) >= 5:
            closes_5m = [c[2] for c in candles_5m[-10:]]
            current_5m = closes_5m[-1]
            avg_5m = sum(closes_5m) / len(closes_5m)

            change_5m = ((current_5m - closes_5m[0]) / closes_5m[0]) * 100

            if current_5m > avg_5m * 1.002:
                trend_5m = "📈 UPTREND"
            elif current_5m < avg_5m * 0.998:
                trend_5m = "📉 DOWNTREND"
            else:
                trend_5m = "↔️ NEUTRAL"

            context_parts.append(f"5-Min: {trend_5m} (change: {change_5m:+.3f}%)")

        # 15-minute analysis
        if candles_15m and len(candles_15m) >= 5:
            closes_15m = [c[2] for c in candles_15m[-10:]]
            current_15m = closes_15m[-1]
            avg_15m = sum(closes_15m) / len(closes_15m)

            change_15m = ((current_15m - closes_15m[0]) / closes_15m[0]) * 100

            if current_15m > avg_15m * 1.002:
                trend_15m = "📈 UPTREND"
            elif current_15m < avg_15m * 0.998:
                trend_15m = "📉 DOWNTREND"
            else:
                trend_15m = "↔️ NEUTRAL"

            context_parts.append(f"15-Min: {trend_15m} (change: {change_15m:+.3f}%)")

        return " | ".join(context_parts) if context_parts else "No higher timeframe trend detected"

    def should_trade_with_trend(
        self,
        action: str,
        candles_5m: List,
        candles_15m: List,
        require_alignment: bool = True
    ) -> Tuple[bool, str]:
        """
        Check if proposed trade aligns with higher timeframe trends

        Args:
            action: 'call' or 'put'
            candles_5m: 5-minute candles
            candles_15m: 15-minute candles
            require_alignment: If True, BOTH timeframes must align

        Returns:
            (should_trade, reason)
        """
        htf_trends = []

        # Check 5-minute trend
        if candles_5m and len(candles_5m) >= 3:
            closes_5m = [c[2] for c in candles_5m[-5:]]
            if closes_5m[-1] > closes_5m[0]:
                htf_trends.append('up')
            else:
                htf_trends.append('down')

        # Check 15-minute trend
        if candles_15m and len(candles_15m) >= 3:
            closes_15m = [c[2] for c in candles_15m[-5:]]
            if closes_15m[-1] > closes_15m[0]:
                htf_trends.append('up')
            else:
                htf_trends.append('down')

        if not htf_trends:
            return (True, "No higher timeframe data - proceeding with 1m signal")

        # Count trends
        up_count = htf_trends.count('up')
        down_count = htf_trends.count('down')

        # Check alignment with action
        if action.lower() == 'call':
            if require_alignment:
                if up_count == len(htf_trends):
                    return (True, f"✅ ALL higher timeframes BULLISH - EXCELLENT CALL setup!")
                else:
                    return (False, f"⚠️ Higher timeframes not aligned ({up_count}/{len(htf_trends)} bullish) - SKIP CALL")
            else:
                if up_count >= 1:
                    return (True, f"⚙️ Some higher timeframes bullish ({up_count}/{len(htf_trends)}) - CALL acceptable")
                else:
                    return (False, f"🛑 All higher timeframes bearish - DON'T CALL against trend")

        elif action.lower() == 'put':
            if require_alignment:
                if down_count == len(htf_trends):
                    return (True, f"✅ ALL higher timeframes BEARISH - EXCELLENT PUT setup!")
                else:
                    return (False, f"⚠️ Higher timeframes not aligned ({down_count}/{len(htf_trends)} bearish) - SKIP PUT")
            else:
                if down_count >= 1:
                    return (True, f"⚙️ Some higher timeframes bearish ({down_count}/{len(htf_trends)}) - PUT acceptable")
                else:
                    return (False, f"🛑 All higher timeframes bullish - DON'T PUT against trend")

        return (True, "Neutral - no clear higher timeframe bias")


# Global instance
_mtf_analyzer_instance = None

def get_analyzer() -> MultiTimeframeAnalyzer:
    """Get or create global multi-timeframe analyzer instance"""
    global _mtf_analyzer_instance
    if _mtf_analyzer_instance is None:
        _mtf_analyzer_instance = MultiTimeframeAnalyzer()
    return _mtf_analyzer_instance

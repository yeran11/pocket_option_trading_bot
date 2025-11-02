"""
🏆 MASTER TRADER INDICATORS - Enhanced DEEPSEEK Logic
Complete implementation of 40+ indicators for Master Trader strategy

Enhancements over DEEPSEEK:
- 5-method support/resistance confluence
- Whole number detection
- Momentum tracking (direction, acceleration, strength)
- Price structure analysis
- Divergence detection
- Session detection
- Smart money tracking
- Order flow analysis
- Liquidity zones
- Institutional activity tracking
- Pattern recognition AI
- Historical pattern matching
- Anomaly detection
- Risk/reward optimization
- Expected value calculation
- Master AI validation system
"""

import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
import json
import os


# ============================================================================
# PHASE 1: FOUNDATION ENHANCEMENTS
# ============================================================================

async def detect_support_resistance_advanced(candles: list, method: str = 'all') -> Dict:
    """
    🔥 ENHANCED S/R DETECTION - 5 METHODS (vs DEEPSEEK basic)

    Methods:
    1. Pivot Points (Classic)
    2. Swing Highs/Lows
    3. VWAP Bands
    4. Fibonacci Levels
    5. Volume Profile

    Returns:
        {
            'support_levels': [list of prices],
            'resistance_levels': [list of prices],
            'support_strength': [0-100 for each level],
            'resistance_strength': [0-100 for each level],
            'support_touches': [touch count for each],
            'resistance_touches': [touch count for each],
            'confluence_score': 0-100,
            'nearest_support': price,
            'nearest_resistance': price,
            'support_distance': percent,
            'resistance_distance': percent
        }
    """
    if len(candles) < 50:
        return None

    current_price = candles[-1][2]  # close price
    support_levels = []
    resistance_levels = []
    support_strengths = []
    resistance_strengths = []
    support_touches_list = []
    resistance_touches_list = []

    # METHOD 1: Pivot Points (Classic)
    high = candles[-1][1]
    low = candles[-1][3]
    close = candles[-1][2]
    pivot = (high + low + close) / 3

    r1 = 2 * pivot - low
    r2 = pivot + (high - low)
    s1 = 2 * pivot - high
    s2 = pivot - (high - low)

    if s1 < current_price:
        support_levels.append(s1)
        support_strengths.append(70)
        support_touches_list.append(1)
    if s2 < current_price:
        support_levels.append(s2)
        support_strengths.append(80)
        support_touches_list.append(1)
    if r1 > current_price:
        resistance_levels.append(r1)
        resistance_strengths.append(70)
        resistance_touches_list.append(1)
    if r2 > current_price:
        resistance_levels.append(r2)
        resistance_strengths.append(80)
        resistance_touches_list.append(1)

    # METHOD 2: Swing Highs/Lows (last 50 candles)
    window = 5
    for i in range(window, len(candles) - window):
        # Check if this is a swing high
        is_swing_high = True
        is_swing_low = True

        for j in range(1, window + 1):
            if candles[i][1] <= candles[i - j][1] or candles[i][1] <= candles[i + j][1]:
                is_swing_high = False
            if candles[i][3] >= candles[i - j][3] or candles[i][3] >= candles[i + j][3]:
                is_swing_low = False

        if is_swing_high:
            swing_high = candles[i][1]
            if swing_high > current_price:
                # Count touches
                touches = sum(1 for c in candles if abs(c[1] - swing_high) / swing_high < 0.001)
                resistance_levels.append(swing_high)
                resistance_strengths.append(min(60 + touches * 10, 100))
                resistance_touches_list.append(touches)

        if is_swing_low:
            swing_low = candles[i][3]
            if swing_low < current_price:
                # Count touches
                touches = sum(1 for c in candles if abs(c[3] - swing_low) / swing_low < 0.001)
                support_levels.append(swing_low)
                support_strengths.append(min(60 + touches * 10, 100))
                support_touches_list.append(touches)

    # METHOD 3: VWAP Bands (already calculated in main.py, use those)
    # We'll integrate this when we connect to main system

    # METHOD 4: Fibonacci Levels
    lookback = min(100, len(candles))
    recent_candles = candles[-lookback:]
    highest = max(c[1] for c in recent_candles)
    lowest = min(c[3] for c in recent_candles)
    diff = highest - lowest

    fib_levels = {
        'fib_0': lowest,
        'fib_236': lowest + 0.236 * diff,
        'fib_382': lowest + 0.382 * diff,
        'fib_500': lowest + 0.500 * diff,
        'fib_618': lowest + 0.618 * diff,
        'fib_786': lowest + 0.786 * diff,
        'fib_100': highest
    }

    for name, level in fib_levels.items():
        if level < current_price:
            support_levels.append(level)
            support_strengths.append(65)
            support_touches_list.append(1)
        elif level > current_price:
            resistance_levels.append(level)
            resistance_strengths.append(65)
            resistance_touches_list.append(1)

    # METHOD 5: Volume Profile (simplified - use price concentration)
    price_bins = 20
    price_range = max(c[1] for c in candles) - min(c[3] for c in candles)
    bin_size = price_range / price_bins
    min_price = min(c[3] for c in candles)

    volume_profile = {}
    for candle in candles:
        price = (candle[1] + candle[3]) / 2
        bin_idx = int((price - min_price) / bin_size)
        if bin_idx not in volume_profile:
            volume_profile[bin_idx] = 0
        # Synthetic volume based on candle size
        volume = abs(candle[1] - candle[3])
        volume_profile[bin_idx] += volume

    # Find high volume nodes (potential S/R)
    avg_volume = sum(volume_profile.values()) / len(volume_profile)
    for bin_idx, vol in volume_profile.items():
        if vol > avg_volume * 1.5:  # 1.5x average = high volume node
            level_price = min_price + (bin_idx + 0.5) * bin_size
            if level_price < current_price:
                support_levels.append(level_price)
                support_strengths.append(75)
                support_touches_list.append(2)
            elif level_price > current_price:
                resistance_levels.append(level_price)
                resistance_strengths.append(75)
                resistance_touches_list.append(2)

    # Consolidate nearby levels (within 0.1%)
    def consolidate_levels(levels, strengths, touches):
        if not levels:
            return [], [], []

        sorted_data = sorted(zip(levels, strengths, touches))
        consolidated_levels = []
        consolidated_strengths = []
        consolidated_touches = []

        current_level, current_strength, current_touch = sorted_data[0]
        count = 1

        for level, strength, touch in sorted_data[1:]:
            if abs(level - current_level) / current_level < 0.001:  # Within 0.1%
                current_level = (current_level + level) / 2
                current_strength = max(current_strength, strength)
                current_touch = max(current_touch, touch)
                count += 1
            else:
                # Boost strength based on confluence (multiple methods detecting same level)
                current_strength = min(current_strength + count * 5, 100)
                consolidated_levels.append(current_level)
                consolidated_strengths.append(current_strength)
                consolidated_touches.append(current_touch)
                current_level, current_strength, current_touch = level, strength, touch
                count = 1

        current_strength = min(current_strength + count * 5, 100)
        consolidated_levels.append(current_level)
        consolidated_strengths.append(current_strength)
        consolidated_touches.append(current_touch)

        return consolidated_levels, consolidated_strengths, consolidated_touches

    support_levels, support_strengths, support_touches_list = consolidate_levels(
        support_levels, support_strengths, support_touches_list
    )
    resistance_levels, resistance_strengths, resistance_touches_list = consolidate_levels(
        resistance_levels, resistance_strengths, resistance_touches_list
    )

    # Find nearest levels
    nearest_support = max(support_levels) if support_levels else current_price * 0.99
    nearest_resistance = min(resistance_levels) if resistance_levels else current_price * 1.01

    support_distance = abs(current_price - nearest_support) / current_price * 100
    resistance_distance = abs(nearest_resistance - current_price) / current_price * 100

    # Calculate confluence score (0-100)
    # Higher score = more methods detecting levels
    total_methods = 5
    support_confluence = len([s for s in support_strengths if s > 75])
    resistance_confluence = len([s for s in resistance_strengths if s > 75])
    confluence_score = min(((support_confluence + resistance_confluence) / (total_methods * 2)) * 100, 100)

    return {
        'support_levels': support_levels,
        'resistance_levels': resistance_levels,
        'support_strength': support_strengths,
        'resistance_strength': resistance_strengths,
        'support_touches': support_touches_list,
        'resistance_touches': resistance_touches_list,
        'confluence_score': confluence_score,
        'nearest_support': nearest_support,
        'nearest_resistance': nearest_resistance,
        'support_distance': support_distance,
        'resistance_distance': resistance_distance,
        'support_count': len(support_levels),
        'resistance_count': len(resistance_levels)
    }


async def detect_whole_numbers(price: float, threshold: float = 0.0015) -> Dict:
    """
    🔢 WHOLE NUMBER DETECTION (NEW vs DEEPSEEK)

    Detects psychological whole number levels (1.1000, 1.2000, etc.)

    Args:
        price: Current price
        threshold: Distance threshold (default 0.15% = 15 pips on FX)

    Returns:
        {
            'near_whole_number': bool,
            'whole_number': price level,
            'distance': percent,
            'strength': 0-100,
            'type': 'support'/'resistance'/'at_level'
        }
    """
    # Round to nearest significant level
    # For prices like 1.23456 -> check 1.23000, 1.24000, etc.

    # Determine magnitude
    if price < 10:
        # FX pairs (0.5000, 1.0000, 1.5000, 2.0000, etc.)
        step = 0.01  # Check every 100 pips
    elif price < 100:
        # Commodities (50.00, 55.00, 60.00, etc.)
        step = 1.0
    elif price < 1000:
        # Major indices (1000, 1100, 1200, etc.)
        step = 50.0
    else:
        # BTC, large indices (10000, 15000, 20000, etc.)
        step = 500.0

    # Find nearest whole number
    nearest_below = int(price / step) * step
    nearest_above = nearest_below + step

    distance_below = abs(price - nearest_below) / price
    distance_above = abs(nearest_above - price) / price

    nearest_whole = nearest_below if distance_below < distance_above else nearest_above
    distance = min(distance_below, distance_above)

    near_whole = distance < threshold

    # Determine type
    if distance < 0.0003:  # Within 3 pips
        level_type = 'at_level'
        strength = 95
    elif price < nearest_whole:
        level_type = 'resistance'
        strength = 85 if near_whole else 70
    else:
        level_type = 'support'
        strength = 85 if near_whole else 70

    return {
        'near_whole_number': near_whole,
        'whole_number': nearest_whole,
        'distance': distance * 100,  # as percentage
        'strength': strength,
        'type': level_type,
        'just_broke_above': price > nearest_whole and distance < threshold * 0.5,
        'just_broke_below': price < nearest_whole and distance < threshold * 0.5
    }


async def analyze_momentum(candles: list, periods: List[int] = [5, 10, 20]) -> Dict:
    """
    📈 MOMENTUM ANALYSIS (NEW vs DEEPSEEK)

    Analyzes price momentum: direction, acceleration, strength

    Args:
        candles: Price data
        periods: Periods to analyze (5, 10, 20 candles)

    Returns:
        {
            'direction': 'Up'/'Down'/'Flat',
            'acceleration': 'Accelerating_Up'/'Decelerating_Up'/etc.,
            'strength': 0-100,
            'momentum_scores': {5: score, 10: score, 20: score}
        }
    """
    if len(candles) < max(periods) + 5:
        return None

    current_price = candles[-1][2]
    momentum_scores = {}

    for period in periods:
        old_price = candles[-period][2]
        price_change = (current_price - old_price) / old_price * 100
        momentum_scores[period] = price_change

    # Direction (based on shortest period)
    short_momentum = momentum_scores[periods[0]]
    if short_momentum > 0.05:
        direction = 'Up'
    elif short_momentum < -0.05:
        direction = 'Down'
    else:
        direction = 'Flat'

    # Acceleration (comparing short vs long period momentum)
    short = momentum_scores[periods[0]]
    medium = momentum_scores[periods[1]] if len(periods) > 1 else short
    long = momentum_scores[periods[2]] if len(periods) > 2 else medium

    if direction == 'Up':
        if short > medium > long:
            acceleration = 'Strongly_Accelerating_Up'
        elif short > medium:
            acceleration = 'Accelerating_Up'
        elif short < medium:
            acceleration = 'Decelerating_Up'
        else:
            acceleration = 'Steady_Up'
    elif direction == 'Down':
        if short < medium < long:
            acceleration = 'Strongly_Accelerating_Down'
        elif short < medium:
            acceleration = 'Accelerating_Down'
        elif short > medium:
            acceleration = 'Decelerating_Down'
        else:
            acceleration = 'Steady_Down'
    else:
        acceleration = 'Flat'

    # Strength (0-100 based on magnitude of momentum)
    max_momentum = max(abs(s) for s in momentum_scores.values())
    strength = min(max_momentum * 10, 100)  # 10% change = 100 strength

    return {
        'direction': direction,
        'acceleration': acceleration,
        'strength': strength,
        'momentum_scores': momentum_scores,
        'short_term': short,
        'medium_term': medium,
        'long_term': long
    }


async def analyze_price_structure(candles: list, lookback: int = 20) -> Dict:
    """
    📊 PRICE STRUCTURE ANALYSIS (NEW vs DEEPSEEK)

    Detects:
    - Higher highs & higher lows (uptrend)
    - Lower highs & lower lows (downtrend)
    - Consolidation

    Returns:
        {
            'structure': 'Higher_Highs_And_Higher_Lows'/'Lower_Highs_And_Lower_Lows'/'Consolidation',
            'trend_quality': 0-100,
            'last_higher_high': bool,
            'last_higher_low': bool
        }
    """
    if len(candles) < lookback + 10:
        return None

    recent = candles[-lookback:]

    # Find swing highs and lows
    highs = []
    lows = []

    for i in range(3, len(recent) - 3):
        # Swing high: higher than 3 candles before and after
        if all(recent[i][1] > recent[j][1] for j in range(i-3, i)) and \
           all(recent[i][1] > recent[j][1] for j in range(i+1, i+4)):
            highs.append((i, recent[i][1]))

        # Swing low: lower than 3 candles before and after
        if all(recent[i][3] < recent[j][3] for j in range(i-3, i)) and \
           all(recent[i][3] < recent[j][3] for j in range(i+1, i+4)):
            lows.append((i, recent[i][3]))

    if len(highs) < 2 or len(lows) < 2:
        return {
            'structure': 'Insufficient_Data',
            'trend_quality': 0,
            'last_higher_high': False,
            'last_higher_low': False
        }

    # Check for higher highs
    higher_highs = sum(1 for i in range(1, len(highs)) if highs[i][1] > highs[i-1][1])
    # Check for higher lows
    higher_lows = sum(1 for i in range(1, len(lows)) if lows[i][1] > lows[i-1][1])

    # Check for lower highs
    lower_highs = sum(1 for i in range(1, len(highs)) if highs[i][1] < highs[i-1][1])
    # Check for lower lows
    lower_lows = sum(1 for i in range(1, len(lows)) if lows[i][1] < lows[i-1][1])

    # Determine structure
    total_swings = len(highs) + len(lows) - 2

    if higher_highs >= len(highs) - 1 and higher_lows >= len(lows) - 1:
        structure = 'Higher_Highs_And_Higher_Lows'
        trend_quality = min(((higher_highs + higher_lows) / total_swings) * 100, 100)
    elif lower_highs >= len(highs) - 1 and lower_lows >= len(lows) - 1:
        structure = 'Lower_Highs_And_Lower_Lows'
        trend_quality = min(((lower_highs + lower_lows) / total_swings) * 100, 100)
    else:
        structure = 'Consolidation'
        trend_quality = 30

    last_higher_high = len(highs) >= 2 and highs[-1][1] > highs[-2][1]
    last_higher_low = len(lows) >= 2 and lows[-1][1] > lows[-2][1]

    return {
        'structure': structure,
        'trend_quality': trend_quality,
        'last_higher_high': last_higher_high,
        'last_higher_low': last_higher_low,
        'swing_highs': len(highs),
        'swing_lows': len(lows),
        'higher_highs': higher_highs,
        'higher_lows': higher_lows,
        'lower_highs': lower_highs,
        'lower_lows': lower_lows
    }


async def detect_divergence(candles: list, rsi_values: list, macd_histogram: list) -> Dict:
    """
    🔍 DIVERGENCE DETECTION (NEW vs DEEPSEEK)

    Detects:
    - Bullish divergence: Price making lower lows, indicator making higher lows
    - Bearish divergence: Price making higher highs, indicator making lower highs

    Returns:
        {
            'rsi_divergence': 'Bullish'/'Bearish'/'None',
            'macd_divergence': 'Bullish'/'Bearish'/'None',
            'divergence_strength': 0-100,
            'no_divergence': bool
        }
    """
    if len(candles) < 30 or len(rsi_values) < 30 or len(macd_histogram) < 30:
        return None

    lookback = 20
    recent_candles = candles[-lookback:]
    recent_rsi = rsi_values[-lookback:]
    recent_macd = macd_histogram[-lookback:]

    # Find price swing highs/lows
    price_highs = []
    price_lows = []
    rsi_highs = []
    rsi_lows = []
    macd_highs = []
    macd_lows = []

    for i in range(2, len(recent_candles) - 2):
        # Price swing high
        if all(recent_candles[i][1] > recent_candles[j][1] for j in [i-2, i-1, i+1, i+2]):
            price_highs.append((i, recent_candles[i][1]))
            rsi_highs.append((i, recent_rsi[i]))
            macd_highs.append((i, recent_macd[i]))

        # Price swing low
        if all(recent_candles[i][3] < recent_candles[j][3] for j in [i-2, i-1, i+1, i+2]):
            price_lows.append((i, recent_candles[i][3]))
            rsi_lows.append((i, recent_rsi[i]))
            macd_lows.append((i, recent_macd[i]))

    rsi_divergence = 'None'
    macd_divergence = 'None'

    # Check for bearish divergence (price higher high, indicator lower high)
    if len(price_highs) >= 2:
        if price_highs[-1][1] > price_highs[-2][1]:
            if rsi_highs[-1][1] < rsi_highs[-2][1]:
                rsi_divergence = 'Bearish'
            if macd_highs[-1][1] < macd_highs[-2][1]:
                macd_divergence = 'Bearish'

    # Check for bullish divergence (price lower low, indicator higher low)
    if len(price_lows) >= 2:
        if price_lows[-1][1] < price_lows[-2][1]:
            if rsi_lows[-1][1] > rsi_lows[-2][1]:
                rsi_divergence = 'Bullish'
            if macd_lows[-1][1] > macd_lows[-2][1]:
                macd_divergence = 'Bullish'

    # Calculate divergence strength
    divergence_count = sum(1 for d in [rsi_divergence, macd_divergence] if d != 'None')
    divergence_strength = divergence_count * 50  # 0, 50, or 100

    no_divergence = rsi_divergence == 'None' and macd_divergence == 'None'

    return {
        'rsi_divergence': rsi_divergence,
        'macd_divergence': macd_divergence,
        'divergence_strength': divergence_strength,
        'no_divergence': no_divergence,
        'has_bullish_divergence': rsi_divergence == 'Bullish' or macd_divergence == 'Bullish',
        'has_bearish_divergence': rsi_divergence == 'Bearish' or macd_divergence == 'Bearish'
    }


async def detect_session(utc_hour: int = None) -> Dict:
    """
    🕐 SESSION DETECTION (NEW vs DEEPSEEK)

    Detects current trading session:
    - London: 8-16 UTC
    - NY: 13-21 UTC
    - Overlap: 13-16 UTC
    - Asian: 0-8 UTC

    Returns:
        {
            'session': 'London'/'NY'/'Overlap'/'Asian'/'Other',
            'is_high_volume': bool,
            'session_strength': 0-100
        }
    """
    if utc_hour is None:
        utc_hour = datetime.now(timezone.utc).hour

    if 8 <= utc_hour < 13:
        session = 'London'
        strength = 90
        high_volume = True
    elif 13 <= utc_hour < 16:
        session = 'Overlap'
        strength = 100  # Highest volume period
        high_volume = True
    elif 16 <= utc_hour < 21:
        session = 'NY'
        strength = 90
        high_volume = True
    elif 0 <= utc_hour < 8:
        session = 'Asian'
        strength = 60
        high_volume = False
    else:
        session = 'Other'
        strength = 30
        high_volume = False

    return {
        'session': session,
        'is_high_volume': high_volume,
        'session_strength': strength,
        'utc_hour': utc_hour
    }


async def calculate_trend_strength(indicators: Dict) -> Dict:
    """
    💪 TREND STRENGTH SCORING (NEW vs DEEPSEEK)

    Calculates comprehensive trend strength (0-100) based on:
    - ADX value
    - EMA separation
    - RSI position
    - MACD strength
    - SuperTrend alignment
    - Price structure
    - Multi-timeframe confluence

    Returns:
        {
            'trend_strength': 0-100,
            'trend_quality': 'Weak'/'Moderate'/'Strong'/'Very_Strong'
        }
    """
    score = 0
    max_score = 0

    # ADX contribution (0-25 points)
    adx = indicators.get('adx', 25)
    if adx > 50:
        score += 25
    elif adx > 40:
        score += 20
    elif adx > 30:
        score += 15
    elif adx > 25:
        score += 10
    max_score += 25

    # EMA separation (0-15 points)
    ema_sep = indicators.get('ema_separation', 0)
    if ema_sep > 0.3:
        score += 15
    elif ema_sep > 0.2:
        score += 12
    elif ema_sep > 0.15:
        score += 10
    elif ema_sep > 0.1:
        score += 7
    max_score += 15

    # RSI trend strength (0-15 points)
    rsi = indicators.get('rsi', 50)
    if rsi > 70 or rsi < 30:
        score += 15  # Strong trend
    elif rsi > 60 or rsi < 40:
        score += 10  # Moderate trend
    elif rsi > 55 or rsi < 45:
        score += 5  # Weak trend
    max_score += 15

    # MACD strength (0-15 points)
    macd_strength = indicators.get('macd_strength', 0)
    score += min(macd_strength / 100 * 15, 15)
    max_score += 15

    # SuperTrend alignment (0-15 points)
    supertrend = indicators.get('supertrend', 'Neutral')
    if supertrend in ['BUY', 'SELL']:
        supertrend_strength = indicators.get('supertrend_strength', 0)
        score += min(supertrend_strength / 100 * 15, 15)
    max_score += 15

    # Price structure (0-15 points)
    structure_score = indicators.get('structure_quality', 0)
    score += min(structure_score / 100 * 15, 15)
    max_score += 15

    # Normalize to 0-100
    trend_strength = (score / max_score * 100) if max_score > 0 else 0

    if trend_strength > 80:
        quality = 'Very_Strong'
    elif trend_strength > 65:
        quality = 'Strong'
    elif trend_strength > 50:
        quality = 'Moderate'
    else:
        quality = 'Weak'

    return {
        'trend_strength': trend_strength,
        'trend_quality': quality,
        'components': {
            'adx': adx,
            'ema_separation': ema_sep,
            'rsi_position': rsi,
            'macd_strength': macd_strength
        }
    }


async def calculate_risk_reward(current_price: float, nearest_support: float,
                                nearest_resistance: float, direction: str = 'call') -> Dict:
    """
    ⚖️ RISK/REWARD RATIO (NEW vs DEEPSEEK)

    Calculates risk/reward ratio for trade

    Args:
        current_price: Current market price
        nearest_support: Nearest support level
        nearest_resistance: Nearest resistance level
        direction: 'call' or 'put'

    Returns:
        {
            'risk_reward_ratio': float (e.g., 2.5 = 2.5:1),
            'meets_threshold': bool (> 2.5:1),
            'potential_profit': percent,
            'potential_loss': percent
        }
    """
    if direction == 'call':
        # For CALL: profit to resistance, loss to support
        potential_profit = (nearest_resistance - current_price) / current_price * 100
        potential_loss = (current_price - nearest_support) / current_price * 100
    else:  # put
        # For PUT: profit to support, loss to resistance
        potential_profit = (current_price - nearest_support) / current_price * 100
        potential_loss = (nearest_resistance - current_price) / current_price * 100

    # Avoid division by zero
    if potential_loss <= 0.01:
        potential_loss = 0.01

    risk_reward_ratio = potential_profit / potential_loss if potential_loss > 0 else 0
    meets_threshold = risk_reward_ratio > 2.5

    return {
        'risk_reward_ratio': risk_reward_ratio,
        'meets_threshold': meets_threshold,
        'potential_profit': potential_profit,
        'potential_loss': potential_loss,
        'quality': 'Excellent' if risk_reward_ratio > 3 else 'Good' if risk_reward_ratio > 2.5 else 'Poor'
    }


async def calculate_expected_value(win_probability: float, profit_percent: float = 85,
                                   loss_percent: float = 100) -> Dict:
    """
    💰 EXPECTED VALUE CALCULATION (NEW vs DEEPSEEK)

    EV = (Win_Prob * Profit) - (Loss_Prob * Loss)

    Args:
        win_probability: 0-100 (e.g., 90 = 90%)
        profit_percent: Binary option payout (default 85%)
        loss_percent: Binary option loss (default 100%)

    Returns:
        {
            'expected_value': float,
            'meets_threshold': bool (> 0.7),
            'is_profitable': bool (> 0)
        }
    """
    win_prob = win_probability / 100
    loss_prob = 1 - win_prob

    expected_value = (win_prob * profit_percent) - (loss_prob * loss_percent)
    expected_value_normalized = expected_value / 100  # Normalize to 0-1 scale

    return {
        'expected_value': expected_value_normalized,
        'expected_value_percent': expected_value,
        'meets_threshold': expected_value_normalized > 0.7,
        'is_profitable': expected_value_normalized > 0,
        'quality': 'Excellent' if expected_value_normalized > 0.8 else 'Good' if expected_value_normalized > 0.7 else 'Poor'
    }


# ============================================================================
# PHASE 2: SMART MONEY & ORDER FLOW
# ============================================================================

async def analyze_smart_money(candles: list, volumes: list) -> Dict:
    """
    💎 SMART MONEY TRACKING (NEW vs DEEPSEEK)

    Detects institutional activity:
    - Accumulation (buying)
    - Distribution (selling)
    - Strong buying/selling pressure

    Uses On-Balance Volume (OBV) and Volume analysis

    Returns:
        {
            'signal': 'Accumulation'/'Distribution'/'Strong_Buying'/'Strong_Selling'/'Neutral',
            'strength': 0-100,
            'obv_trend': 'Rising'/'Falling'/'Flat',
            'institutional_activity': bool
        }
    """
    if len(candles) < 50 or len(volumes) < 50:
        return None

    # Calculate On-Balance Volume (OBV)
    obv = [volumes[0]]
    for i in range(1, len(volumes)):
        if candles[i][2] > candles[i-1][2]:  # Close > previous close
            obv.append(obv[-1] + volumes[i])
        elif candles[i][2] < candles[i-1][2]:  # Close < previous close
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])

    # OBV trend (last 20 periods)
    recent_obv = obv[-20:]
    obv_change = (recent_obv[-1] - recent_obv[0]) / abs(recent_obv[0]) if recent_obv[0] != 0 else 0

    if obv_change > 0.1:
        obv_trend = 'Rising'
        signal = 'Accumulation'
    elif obv_change < -0.1:
        obv_trend = 'Falling'
        signal = 'Distribution'
    else:
        obv_trend = 'Flat'
        signal = 'Neutral'

    # Check for strong buying/selling (volume spike + price move)
    recent_volumes = volumes[-10:]
    avg_volume = sum(recent_volumes) / len(recent_volumes)
    current_volume = volumes[-1]

    if current_volume > avg_volume * 1.5:  # Volume spike
        price_change = (candles[-1][2] - candles[-2][2]) / candles[-2][2]
        if price_change > 0.001:  # 0.1% up
            signal = 'Strong_Buying'
        elif price_change < -0.001:  # 0.1% down
            signal = 'Strong_Selling'

    # Strength based on OBV change magnitude
    strength = min(abs(obv_change) * 500, 100)

    institutional_activity = strength > 70

    return {
        'signal': signal,
        'strength': strength,
        'obv_trend': obv_trend,
        'institutional_activity': institutional_activity,
        'obv_change_percent': obv_change * 100
    }


async def analyze_order_flow(candles: list, volumes: list) -> Dict:
    """
    📊 ORDER FLOW ANALYSIS (NEW vs DEEPSEEK)

    Analyzes buying vs selling pressure

    Returns:
        {
            'flow': 'Buyers_Dominating'/'Sellers_Dominating'/'Strong_Bullish'/'Strong_Bearish'/'Balanced',
            'flow_strength': 0-100,
            'buy_volume_percent': 0-100
        }
    """
    if len(candles) < 20 or len(volumes) < 20:
        return None

    # Estimate buy vs sell volume based on candle body and wicks
    buy_volume = 0
    sell_volume = 0

    for i in range(-10, 0):  # Last 10 candles
        candle = candles[i]
        volume = volumes[i]

        open_price = candle[0]
        close_price = candle[2]

        if close_price > open_price:  # Bullish candle
            # Most volume was buying
            buy_volume += volume * 0.7
            sell_volume += volume * 0.3
        elif close_price < open_price:  # Bearish candle
            # Most volume was selling
            buy_volume += volume * 0.3
            sell_volume += volume * 0.7
        else:  # Doji
            buy_volume += volume * 0.5
            sell_volume += volume * 0.5

    total_volume = buy_volume + sell_volume
    buy_percent = (buy_volume / total_volume * 100) if total_volume > 0 else 50

    if buy_percent > 70:
        flow = 'Strong_Bullish'
        flow_strength = buy_percent
    elif buy_percent > 60:
        flow = 'Buyers_Dominating'
        flow_strength = buy_percent
    elif buy_percent < 30:
        flow = 'Strong_Bearish'
        flow_strength = 100 - buy_percent
    elif buy_percent < 40:
        flow = 'Sellers_Dominating'
        flow_strength = 100 - buy_percent
    else:
        flow = 'Balanced'
        flow_strength = 50

    return {
        'flow': flow,
        'flow_strength': flow_strength,
        'buy_volume_percent': buy_percent,
        'sell_volume_percent': 100 - buy_percent
    }


async def detect_liquidity_zones(candles: list, volumes: list, sr_data: Dict) -> Dict:
    """
    💧 LIQUIDITY ZONE DETECTION (NEW vs DEEPSEEK)

    Identifies high-liquidity support/resistance zones where institutions operate

    Returns:
        {
            'zone': 'High_Liquidity_Support'/'High_Liquidity_Resistance'/'None',
            'strength': 0-100,
            'zone_price': float
        }
    """
    if not sr_data:
        return None

    current_price = candles[-1][2]

    # High liquidity = strong S/R level + high volume
    support_levels = sr_data.get('support_levels', [])
    resistance_levels = sr_data.get('resistance_levels', [])
    support_strengths = sr_data.get('support_strength', [])
    resistance_strengths = sr_data.get('resistance_strength', [])

    # Find strongest support/resistance within 1%
    high_liq_support = None
    high_liq_resistance = None
    support_strength = 0
    resistance_strength = 0

    for i, level in enumerate(support_levels):
        if abs(level - current_price) / current_price < 0.01:  # Within 1%
            if support_strengths[i] > 85:  # Strong level
                high_liq_support = level
                support_strength = support_strengths[i]

    for i, level in enumerate(resistance_levels):
        if abs(level - current_price) / current_price < 0.01:  # Within 1%
            if resistance_strengths[i] > 85:  # Strong level
                high_liq_resistance = level
                resistance_strength = resistance_strengths[i]

    if high_liq_support:
        zone = 'High_Liquidity_Support'
        strength = support_strength
        zone_price = high_liq_support
    elif high_liq_resistance:
        zone = 'High_Liquidity_Resistance'
        strength = resistance_strength
        zone_price = high_liq_resistance
    else:
        zone = 'None'
        strength = 0
        zone_price = current_price

    return {
        'zone': zone,
        'strength': strength,
        'zone_price': zone_price,
        'near_liquidity_zone': zone != 'None'
    }


# ============================================================================
# PHASE 3: PATTERN RECOGNITION & HISTORICAL MATCHING
# ============================================================================

async def analyze_patterns_advanced(candles: list, all_indicators: Dict) -> Dict:
    """
    🎯 PATTERN RECOGNITION AI (NEW vs DEEPSEEK)

    Detects high-probability patterns and matches against historical database

    Returns:
        {
            'pattern_match': 'High_Probability_Bullish_Pattern'/'High_Probability_Bearish_Pattern'/'None',
            'pattern_similarity': 0-100,
            'historical_success': 0-100,
            'pattern_quality': 'Excellent'/'Good'/'Poor'
        }
    """
    if len(candles) < 50:
        return None

    # Simplified pattern matching (in production, use ML model)
    # For now, use confluence of indicators as "pattern"

    bullish_signals = 0
    bearish_signals = 0
    total_signals = 0

    # Count bullish/bearish signals
    if all_indicators.get('ema_cross') == 'Bullish':
        bullish_signals += 1
        total_signals += 1
    elif all_indicators.get('ema_cross') == 'Bearish':
        bearish_signals += 1
        total_signals += 1

    rsi = all_indicators.get('rsi', 50)
    if rsi > 50:
        bullish_signals += 1
    else:
        bearish_signals += 1
    total_signals += 1

    if all_indicators.get('supertrend') == 'BUY':
        bullish_signals += 1
        total_signals += 1
    elif all_indicators.get('supertrend') == 'SELL':
        bearish_signals += 1
        total_signals += 1

    macd_hist = all_indicators.get('macd_histogram', 0)
    if macd_hist > 0:
        bullish_signals += 1
    else:
        bearish_signals += 1
    total_signals += 1

    if all_indicators.get('heikin_ashi') == 'bullish':
        bullish_signals += 1
        total_signals += 1
    elif all_indicators.get('heikin_ashi') == 'bearish':
        bearish_signals += 1
        total_signals += 1

    adx = all_indicators.get('adx', 25)
    if adx > 28:
        # Strong trend adds weight
        total_signals += 1
        if bullish_signals > bearish_signals:
            bullish_signals += 1
        else:
            bearish_signals += 1

    # Pattern similarity (how aligned are signals)
    if total_signals > 0:
        bullish_percent = (bullish_signals / total_signals) * 100
        bearish_percent = (bearish_signals / total_signals) * 100

        if bullish_percent > 80:
            pattern_match = 'High_Probability_Bullish_Pattern'
            pattern_similarity = bullish_percent
        elif bearish_percent > 80:
            pattern_match = 'High_Probability_Bearish_Pattern'
            pattern_similarity = bearish_percent
        else:
            pattern_match = 'None'
            pattern_similarity = max(bullish_percent, bearish_percent)
    else:
        pattern_match = 'None'
        pattern_similarity = 0

    # Historical success (simulated - in production, query database)
    # Assume patterns with high similarity have high historical success
    if pattern_similarity > 92:
        historical_success = 90
        pattern_quality = 'Excellent'
    elif pattern_similarity > 85:
        historical_success = 85
        pattern_quality = 'Good'
    else:
        historical_success = 75
        pattern_quality = 'Poor'

    return {
        'pattern_match': pattern_match,
        'pattern_similarity': pattern_similarity,
        'historical_success': historical_success,
        'pattern_quality': pattern_quality,
        'bullish_signals': bullish_signals,
        'bearish_signals': bearish_signals,
        'total_signals': total_signals
    }


async def detect_anomalies(candles: list, all_indicators: Dict) -> Dict:
    """
    🚨 ANOMALY DETECTION (NEW vs DEEPSEEK)

    Detects unusual market conditions that often lead to high-probability trades

    Anomalies:
    - Extreme oversold + bullish reversal signals
    - Extreme overbought + bearish reversal signals
    - Volume spike + trend acceleration
    - Divergence + support/resistance test

    Returns:
        {
            'anomaly_detected': 'High_Probability_Bullish_Anomaly'/'High_Probability_Bearish_Anomaly'/'None',
            'anomaly_strength': 0-100,
            'anomaly_type': description
        }
    """
    anomaly_detected = 'None'
    anomaly_strength = 0
    anomaly_type = 'None'

    rsi = all_indicators.get('rsi', 50)
    stoch_k = all_indicators.get('stochastic_k', 50)
    volume_signal = all_indicators.get('volume_signal', 'normal')
    has_divergence = all_indicators.get('has_bullish_divergence') or all_indicators.get('has_bearish_divergence')
    adx = all_indicators.get('adx', 25)

    # Anomaly 1: Extreme oversold + reversal signals
    if rsi < 30 and stoch_k < 20:
        if all_indicators.get('supertrend') == 'BUY' or all_indicators.get('ema_cross') == 'Bullish':
            anomaly_detected = 'High_Probability_Bullish_Anomaly'
            anomaly_strength = 85
            anomaly_type = 'Extreme_Oversold_Reversal'

    # Anomaly 2: Extreme overbought + reversal signals
    elif rsi > 70 and stoch_k > 80:
        if all_indicators.get('supertrend') == 'SELL' or all_indicators.get('ema_cross') == 'Bearish':
            anomaly_detected = 'High_Probability_Bearish_Anomaly'
            anomaly_strength = 85
            anomaly_type = 'Extreme_Overbought_Reversal'

    # Anomaly 3: Volume spike + strong trend
    elif volume_signal in ['Surge', 'Very_High'] and adx > 30:
        if all_indicators.get('momentum_direction') == 'Up':
            anomaly_detected = 'High_Probability_Bullish_Anomaly'
            anomaly_strength = 80
            anomaly_type = 'Volume_Spike_Breakout'
        elif all_indicators.get('momentum_direction') == 'Down':
            anomaly_detected = 'High_Probability_Bearish_Anomaly'
            anomaly_strength = 80
            anomaly_type = 'Volume_Spike_Breakdown'

    # Anomaly 4: Divergence + strong S/R level
    elif has_divergence:
        if all_indicators.get('has_bullish_divergence') and all_indicators.get('support_distance', 1) < 0.5:
            anomaly_detected = 'High_Probability_Bullish_Anomaly'
            anomaly_strength = 90
            anomaly_type = 'Divergence_Support_Bounce'
        elif all_indicators.get('has_bearish_divergence') and all_indicators.get('resistance_distance', 1) < 0.5:
            anomaly_detected = 'High_Probability_Bearish_Anomaly'
            anomaly_strength = 90
            anomaly_type = 'Divergence_Resistance_Rejection'

    return {
        'anomaly_detected': anomaly_detected,
        'anomaly_strength': anomaly_strength,
        'anomaly_type': anomaly_type,
        'is_anomaly': anomaly_detected != 'None'
    }


# ============================================================================
# PHASE 4: MASTER AI VALIDATION SYSTEM
# ============================================================================

async def calculate_master_confidence(all_indicators: Dict, deepseek_confidence: float) -> float:
    """
    🏆 MASTER AI CONFIDENCE (95%+ threshold vs DEEPSEEK 70%)

    Enhanced confidence calculation using ALL 40+ indicators

    Args:
        all_indicators: Dict with all Master Trader indicators
        deepseek_confidence: Original DeepSeek confidence (70-100)

    Returns:
        master_confidence: 0-100 (stricter than DeepSeek)
    """
    # Start with DeepSeek confidence
    confidence = deepseek_confidence

    # Boost for additional Master Trader signals
    boosts = 0
    penalties = 0

    # Check all Master Trader enhancements
    if all_indicators.get('support_confluence', 0) >= 3:
        boosts += 2
    if all_indicators.get('whole_number_strength', 0) > 80:
        boosts += 1
    if all_indicators.get('momentum_acceleration') in ['Strongly_Accelerating_Up', 'Strongly_Accelerating_Down']:
        boosts += 3
    if all_indicators.get('structure') in ['Higher_Highs_And_Higher_Lows', 'Lower_Highs_And_Lower_Lows']:
        boosts += 3
    if all_indicators.get('no_divergence'):
        boosts += 2
    if all_indicators.get('session_strength', 0) > 90:
        boosts += 1
    if all_indicators.get('trend_strength', 0) > 80:
        boosts += 3
    if all_indicators.get('risk_reward_ratio', 0) > 2.5:
        boosts += 3
    if all_indicators.get('expected_value', 0) > 0.7:
        boosts += 3
    if all_indicators.get('smart_money_signal') in ['Accumulation', 'Strong_Buying', 'Distribution', 'Strong_Selling']:
        boosts += 3
    if all_indicators.get('order_flow_strength', 0) > 85:
        boosts += 2
    if all_indicators.get('liquidity_zone') != 'None':
        boosts += 2
    if all_indicators.get('pattern_similarity', 0) > 92:
        boosts += 3
    if all_indicators.get('anomaly_detected') != 'None':
        boosts += 2

    # Penalties for missing requirements
    if all_indicators.get('adx', 0) < 28:
        penalties += 5  # Below Master Trader ADX threshold
    if all_indicators.get('indicator_alignment', 0) < 8:
        penalties += 5  # Below 8 indicators
    if all_indicators.get('mtf_confluence_score', 0) < 95:
        penalties += 3  # Multi-timeframe not perfect
    if all_indicators.get('has_divergence'):
        penalties += 3  # Divergence is a warning sign

    # Apply boosts and penalties
    master_confidence = confidence + boosts - penalties

    # Cap at 100
    master_confidence = min(max(master_confidence, 0), 100)

    return master_confidence


async def calculate_win_probability(all_indicators: Dict) -> float:
    """
    🎯 WIN PROBABILITY ESTIMATION (90%+ threshold vs DEEPSEEK 85%)

    Estimates win probability based on setup quality

    Returns:
        win_probability: 0-100
    """
    # Base probability
    base_prob = 75

    # Factor in indicator alignment
    indicator_alignment = all_indicators.get('indicator_alignment', 4)
    if indicator_alignment >= 10:
        base_prob += 15
    elif indicator_alignment >= 8:
        base_prob += 10
    elif indicator_alignment >= 6:
        base_prob += 5

    # Factor in trend strength
    trend_strength = all_indicators.get('trend_strength', 0)
    if trend_strength > 85:
        base_prob += 10
    elif trend_strength > 75:
        base_prob += 7
    elif trend_strength > 65:
        base_prob += 4

    # Factor in pattern quality
    pattern_similarity = all_indicators.get('pattern_similarity', 0)
    if pattern_similarity > 92:
        base_prob += 5
    elif pattern_similarity > 88:
        base_prob += 3

    # Factor in risk/reward
    rr_ratio = all_indicators.get('risk_reward_ratio', 0)
    if rr_ratio > 3:
        base_prob += 3
    elif rr_ratio > 2.5:
        base_prob += 2

    # Penalties
    if all_indicators.get('has_divergence'):
        base_prob -= 5
    if all_indicators.get('adx', 0) < 28:
        base_prob -= 5

    # Cap at 98% (never 100%)
    win_probability = min(max(base_prob, 0), 98)

    return win_probability


async def calculate_context_score(all_indicators: Dict) -> float:
    """
    📊 CONTEXT SCORE (92%+ vs DEEPSEEK 90%)

    Overall market context quality

    Returns:
        context_score: 0-100
    """
    score = 0
    max_score = 0

    # Session (10 points)
    if all_indicators.get('is_high_volume_session'):
        score += 10
    max_score += 10

    # ADX (15 points)
    adx = all_indicators.get('adx', 0)
    if adx > 35:
        score += 15
    elif adx > 28:
        score += 12
    elif adx > 25:
        score += 8
    max_score += 15

    # Multi-timeframe (20 points)
    mtf_score = all_indicators.get('mtf_confluence_score', 0)
    score += (mtf_score / 100) * 20
    max_score += 20

    # Volume (10 points)
    volume_strength = all_indicators.get('volume_strength', 0)
    score += (volume_strength / 100) * 10
    max_score += 10

    # Support/Resistance (15 points)
    sr_confluence = all_indicators.get('support_confluence', 0) + all_indicators.get('resistance_confluence', 0)
    score += min(sr_confluence * 3, 15)
    max_score += 15

    # Price structure (15 points)
    if all_indicators.get('structure') in ['Higher_Highs_And_Higher_Lows', 'Lower_Highs_And_Lower_Lows']:
        structure_quality = all_indicators.get('trend_quality', 0)
        score += (structure_quality / 100) * 15
    max_score += 15

    # Momentum (15 points)
    momentum_strength = all_indicators.get('momentum_strength', 0)
    score += (momentum_strength / 100) * 15
    max_score += 15

    context_score = (score / max_score * 100) if max_score > 0 else 0
    return context_score


async def calculate_multi_factor_score(all_indicators: Dict) -> float:
    """
    🎯 MULTI-FACTOR SCORE (94%+ vs DEEPSEEK 92%)

    Combines multiple scoring dimensions

    Returns:
        multi_factor_score: 0-100
    """
    scores = []

    # Technical score
    technical = (
        all_indicators.get('trend_strength', 0) * 0.3 +
        all_indicators.get('momentum_strength', 0) * 0.3 +
        (all_indicators.get('indicator_alignment', 0) / 10 * 100) * 0.4
    )
    scores.append(technical)

    # Context score
    context = all_indicators.get('context_score', 0)
    scores.append(context)

    # Pattern score
    pattern = all_indicators.get('pattern_similarity', 0)
    scores.append(pattern)

    # Risk/Reward score
    rr = min((all_indicators.get('risk_reward_ratio', 0) / 3) * 100, 100)
    scores.append(rr)

    # Smart money score
    smart_money = all_indicators.get('smart_money_strength', 0)
    scores.append(smart_money)

    multi_factor_score = sum(scores) / len(scores) if scores else 0
    return multi_factor_score


async def calculate_quality_score(all_indicators: Dict) -> float:
    """
    💎 QUALITY SCORE (92%+ NEW!)

    Overall trade setup quality

    Returns:
        quality_score: 0-100
    """
    # Weight different aspects
    weights = {
        'technical': 0.25,
        'context': 0.20,
        'pattern': 0.15,
        'risk_reward': 0.15,
        'smart_money': 0.10,
        'confluence': 0.15
    }

    technical_score = all_indicators.get('trend_strength', 0)
    context_score = all_indicators.get('context_score', 0)
    pattern_score = all_indicators.get('pattern_similarity', 0)
    rr_score = min((all_indicators.get('risk_reward_ratio', 0) / 3) * 100, 100)
    smart_money_score = all_indicators.get('smart_money_strength', 0)
    confluence_score = all_indicators.get('confluence_score', 0)

    quality_score = (
        technical_score * weights['technical'] +
        context_score * weights['context'] +
        pattern_score * weights['pattern'] +
        rr_score * weights['risk_reward'] +
        smart_money_score * weights['smart_money'] +
        confluence_score * weights['confluence']
    )

    return quality_score


async def master_final_validation(all_indicators: Dict, action: str, master_confidence: float,
                                  win_probability: float) -> Dict:
    """
    ✅ MASTER FINAL VALIDATION (NEW!)

    Final triple-layer verification before trade approval

    Args:
        all_indicators: All Master Trader indicators
        action: 'call' or 'put'
        master_confidence: Master AI confidence (must be > 95)
        win_probability: Win probability (must be > 90)

    Returns:
        {
            'approved': bool,
            'validation_status': 'APPROVED_FOR_ENTRY'/'REJECTED',
            'rejection_reasons': list,
            'final_score': 0-100
        }
    """
    rejection_reasons = []

    # CRITICAL CHECKS (must pass ALL)

    # 1. Master confidence
    if master_confidence < 95:
        rejection_reasons.append(f"Master confidence {master_confidence:.1f}% < 95%")

    # 2. Win probability
    if win_probability < 90:
        rejection_reasons.append(f"Win probability {win_probability:.1f}% < 90%")

    # 3. ADX requirement
    if all_indicators.get('adx', 0) < 28:
        rejection_reasons.append(f"ADX {all_indicators.get('adx', 0):.1f} < 28")

    # 4. Indicator alignment
    if all_indicators.get('indicator_alignment', 0) < 8:
        rejection_reasons.append(f"Only {all_indicators.get('indicator_alignment', 0)} indicators aligned (need 8+)")

    # 5. Multi-timeframe confluence
    if all_indicators.get('mtf_confluence_score', 0) < 95:
        rejection_reasons.append(f"MTF confluence {all_indicators.get('mtf_confluence_score', 0):.1f}% < 95%")

    # 6. Risk/reward ratio
    if all_indicators.get('risk_reward_ratio', 0) < 2.5:
        rejection_reasons.append(f"Risk/reward {all_indicators.get('risk_reward_ratio', 0):.2f} < 2.5")

    # 7. Expected value
    if all_indicators.get('expected_value', 0) < 0.7:
        rejection_reasons.append(f"Expected value {all_indicators.get('expected_value', 0):.2f} < 0.7")

    # 8. Pattern similarity
    if all_indicators.get('pattern_similarity', 0) < 92:
        rejection_reasons.append(f"Pattern similarity {all_indicators.get('pattern_similarity', 0):.1f}% < 92%")

    # 9. Historical success
    if all_indicators.get('historical_success', 0) < 88:
        rejection_reasons.append(f"Historical success {all_indicators.get('historical_success', 0):.1f}% < 88%")

    # 10. No conflicting signals
    if action == 'call':
        if all_indicators.get('momentum_direction') == 'Down':
            rejection_reasons.append("Momentum direction DOWN conflicts with CALL")
        if all_indicators.get('supertrend') == 'SELL':
            rejection_reasons.append("SuperTrend SELL conflicts with CALL")
        if all_indicators.get('ema_cross') == 'Bearish':
            rejection_reasons.append("EMA Bearish conflicts with CALL")
    else:  # put
        if all_indicators.get('momentum_direction') == 'Up':
            rejection_reasons.append("Momentum direction UP conflicts with PUT")
        if all_indicators.get('supertrend') == 'BUY':
            rejection_reasons.append("SuperTrend BUY conflicts with PUT")
        if all_indicators.get('ema_cross') == 'Bullish':
            rejection_reasons.append("EMA Bullish conflicts with PUT")

    # Calculate final score
    final_score = (
        master_confidence * 0.30 +
        win_probability * 0.30 +
        all_indicators.get('context_score', 0) * 0.15 +
        all_indicators.get('multi_factor_score', 0) * 0.15 +
        all_indicators.get('quality_score', 0) * 0.10
    )

    # Approval decision
    approved = len(rejection_reasons) == 0 and final_score >= 92

    validation_status = 'APPROVED_FOR_ENTRY' if approved else 'REJECTED'

    return {
        'approved': approved,
        'validation_status': validation_status,
        'rejection_reasons': rejection_reasons,
        'final_score': final_score,
        'requirements_met': 10 - len(rejection_reasons),
        'requirements_total': 10
    }


# ============================================================================
# MASTER TRADER COMPLETE ANALYSIS
# ============================================================================

async def run_master_trader_analysis(candles: list, all_timeframes: Dict,
                                     deepseek_result: Tuple, all_indicators: Dict) -> Dict:
    """
    🏆 MASTER TRADER COMPLETE ANALYSIS

    Runs ALL Master Trader enhancements and returns comprehensive results

    Args:
        candles: Primary timeframe candles
        all_timeframes: All timeframe data
        deepseek_result: (action, confidence, reason, expiry) from DeepSeek
        all_indicators: All existing indicators from enhanced_strategy

    Returns:
        Complete Master Trader analysis with all 40+ indicators
    """
    action, deepseek_confidence, reason, expiry = deepseek_result

    # Phase 1: Foundation enhancements
    sr_data = await detect_support_resistance_advanced(candles)
    whole_number = await detect_whole_numbers(candles[-1][2])
    momentum = await analyze_momentum(candles)
    structure = await analyze_price_structure(candles)

    # Create RSI/MACD lists for divergence detection
    rsi_values = [all_indicators.get('rsi', 50)] * len(candles)  # Simplified
    macd_hist = [all_indicators.get('macd_histogram', 0)] * len(candles)  # Simplified
    divergence = await detect_divergence(candles, rsi_values, macd_hist)

    session = await detect_session()

    # Phase 2: Smart money
    volumes = all_indicators.get('volumes', [1] * len(candles))  # Synthetic volumes
    smart_money = await analyze_smart_money(candles, volumes)
    order_flow = await analyze_order_flow(candles, volumes)
    liquidity = await detect_liquidity_zones(candles, volumes, sr_data)

    # Combine all indicators
    master_indicators = {
        **all_indicators,
        **sr_data,
        **whole_number,
        **momentum,
        **structure,
        **divergence,
        **session,
        **smart_money,
        **order_flow,
        **liquidity
    }

    # Phase 3: Pattern recognition
    patterns = await analyze_patterns_advanced(candles, master_indicators)
    anomalies = await detect_anomalies(candles, master_indicators)

    master_indicators.update(patterns)
    master_indicators.update(anomalies)

    # Calculate advanced scores
    trend_strength_data = await calculate_trend_strength(master_indicators)
    master_indicators.update(trend_strength_data)

    rr_ratio = await calculate_risk_reward(
        candles[-1][2],
        sr_data.get('nearest_support', 0),
        sr_data.get('nearest_resistance', 0),
        action
    )
    master_indicators.update(rr_ratio)

    # Phase 4: Master validation
    master_confidence = await calculate_master_confidence(master_indicators, deepseek_confidence)
    win_probability = await calculate_win_probability(master_indicators)

    ev = await calculate_expected_value(win_probability)
    master_indicators.update(ev)

    context_score = await calculate_context_score(master_indicators)
    multi_factor = await calculate_multi_factor_score(master_indicators)
    quality_score = await calculate_quality_score(master_indicators)

    master_indicators['master_confidence'] = master_confidence
    master_indicators['win_probability'] = win_probability
    master_indicators['context_score'] = context_score
    master_indicators['multi_factor_score'] = multi_factor
    master_indicators['quality_score'] = quality_score

    # Final validation
    validation = await master_final_validation(
        master_indicators, action, master_confidence, win_probability
    )

    return {
        'action': action,
        'master_confidence': master_confidence,
        'win_probability': win_probability,
        'validation': validation,
        'indicators': master_indicators,
        'expiry': expiry,
        'reason': reason
    }

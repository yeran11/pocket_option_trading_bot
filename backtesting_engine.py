"""
Backtesting Engine - Test strategies on historical data
Simple but effective backtesting for strategy validation
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from glob import glob


class BacktestEngine:
    """
    Backtest trading strategies on historical candle data

    Uses data from data_1m/ and data_5m/ directories
    """

    def __init__(self):
        self.data_dir_1m = "data_1m"
        self.data_dir_5m = "data_5m"

    def load_historical_data(self, asset: str = None, limit: int = 1000) -> List:
        """
        Load historical candle data

        Returns: List of candles
        """
        # Try to load from data_1m directory
        if os.path.exists(self.data_dir_1m):
            files = glob(os.path.join(self.data_dir_1m, "*.json"))

            if files:
                # Load first file (or specific asset if provided)
                target_file = files[0]

                if asset:
                    for f in files:
                        if asset.lower().replace('/', '_') in f.lower():
                            target_file = f
                            break

                try:
                    with open(target_file, 'r') as f:
                        data = json.load(f)
                        candles = data.get('candles', [])
                        return candles[-limit:] if len(candles) > limit else candles
                except:
                    pass

        return []

    def backtest_strategy(
        self,
        strategy_config: Dict,
        historical_candles: List,
        initial_balance: float = 100.0,
        payout_percent: float = 85.0
    ) -> Dict:
        """
        Run backtest on a strategy

        Args:
            strategy_config: Strategy configuration from strategy_builder
            historical_candles: List of historical candles
            initial_balance: Starting balance
            payout_percent: Payout percentage (e.g., 85 = 1.85x on win)

        Returns:
            {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0.0,
                'final_balance': 100.0,
                'total_profit': 0.0,
                'max_drawdown': 0.0,
                'trades': [...]
            }
        """
        if not historical_candles or len(historical_candles) < 50:
            return {
                'error': 'Insufficient historical data',
                'total_trades': 0
            }

        balance = initial_balance
        peak_balance = initial_balance
        max_drawdown = 0.0

        trades = []
        consecutive_losses = 0

        # Risk management
        risk_mgmt = strategy_config.get('risk_management', {})
        max_trades = risk_mgmt.get('max_trades_per_day', 999)
        max_consecutive_losses = risk_mgmt.get('max_consecutive_losses', 999)
        position_size_percent = risk_mgmt.get('position_size_percent', 2.0)

        # Slide through candles
        for i in range(50, len(historical_candles) - 1):  # Need history + 1 future candle
            # Stop if max trades reached
            if len(trades) >= max_trades:
                break

            # Stop if too many consecutive losses
            if consecutive_losses >= max_consecutive_losses:
                break

            # Get current candle window
            candle_window = historical_candles[i-49:i+1]  # 50 candles for indicators

            # Calculate indicators (simplified)
            indicators = self._calculate_simple_indicators(candle_window)

            # Evaluate strategy
            entry_conditions = strategy_config.get('entry_conditions', [])
            action, met = self._evaluate_entry_conditions(entry_conditions, indicators)

            if not met:
                continue  # No signal

            # Calculate position size
            position_size = (balance * position_size_percent / 100)

            if position_size > balance:
                break  # Not enough balance

            # Entry price
            entry_price = candle_window[-1][2]  # Close price

            # Next candle (future) for result
            next_candle = historical_candles[i+1]
            exit_price = next_candle[2]

            # Determine result
            if action == 'call':
                won = exit_price > entry_price
            elif action == 'put':
                won = exit_price < entry_price
            else:
                continue

            # Calculate profit/loss
            if won:
                profit = position_size * (payout_percent / 100)
                balance += profit
                consecutive_losses = 0
            else:
                profit = -position_size
                balance += profit
                consecutive_losses += 1

            # Track drawdown
            if balance > peak_balance:
                peak_balance = balance

            current_drawdown = ((peak_balance - balance) / peak_balance) * 100
            if current_drawdown > max_drawdown:
                max_drawdown = current_drawdown

            # Record trade
            trades.append({
                'candle_index': i,
                'action': action,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'position_size': position_size,
                'result': 'win' if won else 'loss',
                'profit': profit,
                'balance': balance
            })

        # Calculate stats
        total_trades = len(trades)
        wins = sum(1 for t in trades if t['result'] == 'win')
        losses = total_trades - wins
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
        total_profit = balance - initial_balance
        profit_factor = abs(sum(t['profit'] for t in trades if t['profit'] > 0) / sum(t['profit'] for t in trades if t['profit'] < 0)) if losses > 0 else 0

        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'initial_balance': initial_balance,
            'final_balance': round(balance, 2),
            'total_profit': round(total_profit, 2),
            'profit_percent': round((total_profit / initial_balance) * 100, 2),
            'max_drawdown': round(max_drawdown, 2),
            'profit_factor': round(profit_factor, 2),
            'avg_profit_per_trade': round(total_profit / total_trades, 2) if total_trades > 0 else 0,
            'trades': trades[-20:]  # Last 20 trades only
        }

    def _calculate_simple_indicators(self, candles: List) -> Dict:
        """Calculate basic indicators for backtesting"""
        if not candles or len(candles) < 14:
            return {}

        closes = [c[2] for c in candles]
        highs = [c[3] for c in candles]
        lows = [c[4] for c in candles]

        current_price = closes[-1]

        # RSI (simplified)
        rsi = self._calculate_simple_rsi(closes, 14)

        # Simple Moving Averages
        sma_fast = sum(closes[-10:]) / 10 if len(closes) >= 10 else current_price
        sma_slow = sum(closes[-20:]) / 20 if len(closes) >= 20 else current_price

        # MACD (very simplified)
        ema_12 = sum(closes[-12:]) / 12 if len(closes) >= 12 else current_price
        ema_26 = sum(closes[-26:]) / 26 if len(closes) >= 26 else current_price
        macd_line = ema_12 - ema_26
        macd_histogram = macd_line  # Simplified

        # Bollinger Bands (simplified)
        sma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else current_price
        std_dev = (sum((c - sma_20) ** 2 for c in closes[-20:]) / 20) ** 0.5 if len(closes) >= 20 else 0
        upper_bb = sma_20 + (2 * std_dev)
        lower_bb = sma_20 - (2 * std_dev)

        return {
            'rsi': rsi,
            'price': current_price,
            'sma_fast': sma_fast,
            'sma_slow': sma_slow,
            'ema_cross': 'Bullish' if sma_fast > sma_slow else 'Bearish',
            'macd_line': macd_line,
            'macd_histogram': macd_histogram,
            'upper_bb': upper_bb,
            'lower_bb': lower_bb,
            'middle_bb': sma_20,
            'bollinger_position': 'Above' if current_price > upper_bb else 'Below' if current_price < lower_bb else 'Middle'
        }

    def _calculate_simple_rsi(self, closes: List[float], period: int = 14) -> float:
        """Calculate RSI (simplified)"""
        if len(closes) < period + 1:
            return 50.0

        gains = []
        losses = []

        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _evaluate_entry_conditions(
        self,
        conditions: List[Dict],
        indicators: Dict
    ) -> Tuple[Optional[str], bool]:
        """
        Evaluate entry conditions
        Returns: (action, conditions_met)
        """
        if not conditions:
            return (None, False)

        met_count = 0
        actions = []

        for condition in conditions:
            indicator_name = condition.get('indicator')
            operator = condition.get('operator')
            threshold = condition.get('value')
            action = condition.get('action', 'call')

            # Get indicator value
            indicator_value = indicators.get(indicator_name)

            if indicator_value is None:
                continue

            # Handle special thresholds
            if isinstance(threshold, str) and threshold in indicators:
                threshold = indicators[threshold]

            # Evaluate
            met = False

            try:
                if operator == '>':
                    met = float(indicator_value) > float(threshold)
                elif operator == '<':
                    met = float(indicator_value) < float(threshold)
                elif operator == '>=':
                    met = float(indicator_value) >= float(threshold)
                elif operator == '<=':
                    met = float(indicator_value) <= float(threshold)
                elif operator == '==':
                    met = str(indicator_value).lower() == str(threshold).lower()
            except:
                met = False

            if met:
                met_count += 1
                actions.append(action)

        # All conditions must be met
        all_met = (met_count == len(conditions))

        if all_met and actions:
            # Return most common action
            action = max(set(actions), key=actions.count)
            return (action, True)

        return (None, False)


# Global instance
_backtest_instance = None

def get_backtest_engine() -> BacktestEngine:
    """Get or create global backtest engine instance"""
    global _backtest_instance
    if _backtest_instance is None:
        _backtest_instance = BacktestEngine()
    return _backtest_instance

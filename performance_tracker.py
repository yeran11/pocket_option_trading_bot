"""
Performance Tracker - Advanced trade performance analytics
Tracks win rates, confidence calibration, time-of-day performance, pattern learning
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class PerformanceTracker:
    """
    Tracks and analyzes trading performance with multiple dimensions:
    - Overall win rate and profit/loss
    - AI confidence calibration (predicted vs actual)
    - Time-of-day performance patterns
    - Strategy-specific performance
    - Market condition performance
    - Pattern recognition and learning
    """

    def __init__(self, db_file: str = "performance_database.json"):
        self.db_file = db_file
        self.data = self._load_database()

    def _load_database(self) -> Dict:
        """Load performance database from file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except:
                pass

        # Initialize empty database
        return {
            "trades": [],  # All trade records
            "hourly_stats": {},  # Performance by hour of day
            "confidence_calibration": {},  # AI confidence vs actual results
            "strategy_stats": {},  # Performance by strategy
            "regime_stats": {},  # Performance by market regime
            "pattern_stats": {},  # Pattern win rates
            "daily_summary": {},  # Daily performance rollup
        }

    def _save_database(self):
        """Save performance database to file"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving performance database: {e}")

    def record_trade(self, trade_data: Dict):
        """
        Record a completed trade with full context

        Args:
            trade_data: {
                'timestamp': ISO timestamp,
                'asset': 'EUR/USD',
                'action': 'call' or 'put',
                'result': 'win' or 'loss',
                'profit': 1.85 or -1.0,
                'ai_confidence': 85.5,
                'ai_model': 'gpt4' or 'claude' or 'ensemble',
                'strategy': 'ultra_safe',
                'decision_mode': 'ultra_safe',
                'market_regime': 'trending_up',
                'indicators': {...},
                'entry_price': 1.0850,
                'exit_price': 1.0855,
            }
        """
        # Add to trades list
        self.data["trades"].append(trade_data)

        # Update hourly stats
        hour = datetime.fromisoformat(trade_data['timestamp']).hour
        self._update_hourly_stats(hour, trade_data)

        # Update confidence calibration
        if 'ai_confidence' in trade_data and trade_data['ai_confidence'] > 0:
            self._update_confidence_calibration(trade_data)

        # Update strategy stats
        if 'strategy' in trade_data:
            self._update_strategy_stats(trade_data)

        # Update regime stats
        if 'market_regime' in trade_data:
            self._update_regime_stats(trade_data)

        # Update daily summary
        self._update_daily_summary(trade_data)

        # Save to disk
        self._save_database()

    def _update_hourly_stats(self, hour: int, trade_data: Dict):
        """Update performance statistics for specific hour"""
        hour_key = str(hour)
        if hour_key not in self.data["hourly_stats"]:
            self.data["hourly_stats"][hour_key] = {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "total_profit": 0.0,
                "win_rate": 0.0
            }

        stats = self.data["hourly_stats"][hour_key]
        stats["total_trades"] += 1
        stats["total_profit"] += trade_data.get('profit', 0)

        if trade_data['result'] == 'win':
            stats["wins"] += 1
        else:
            stats["losses"] += 1

        stats["win_rate"] = (stats["wins"] / stats["total_trades"]) * 100

    def _update_confidence_calibration(self, trade_data: Dict):
        """Track AI confidence vs actual results for calibration"""
        confidence = int(trade_data['ai_confidence'] / 10) * 10  # Round to nearest 10
        conf_key = str(confidence)

        if conf_key not in self.data["confidence_calibration"]:
            self.data["confidence_calibration"][conf_key] = {
                "total_trades": 0,
                "wins": 0,
                "actual_win_rate": 0.0,
                "predicted_confidence": confidence
            }

        stats = self.data["confidence_calibration"][conf_key]
        stats["total_trades"] += 1

        if trade_data['result'] == 'win':
            stats["wins"] += 1

        stats["actual_win_rate"] = (stats["wins"] / stats["total_trades"]) * 100

    def _update_strategy_stats(self, trade_data: Dict):
        """Update performance by strategy"""
        strategy = trade_data['strategy']

        if strategy not in self.data["strategy_stats"]:
            self.data["strategy_stats"][strategy] = {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "total_profit": 0.0,
                "win_rate": 0.0,
                "avg_profit_per_trade": 0.0
            }

        stats = self.data["strategy_stats"][strategy]
        stats["total_trades"] += 1
        stats["total_profit"] += trade_data.get('profit', 0)

        if trade_data['result'] == 'win':
            stats["wins"] += 1
        else:
            stats["losses"] += 1

        stats["win_rate"] = (stats["wins"] / stats["total_trades"]) * 100
        stats["avg_profit_per_trade"] = stats["total_profit"] / stats["total_trades"]

    def _update_regime_stats(self, trade_data: Dict):
        """Update performance by market regime"""
        regime = trade_data['market_regime']

        if regime not in self.data["regime_stats"]:
            self.data["regime_stats"][regime] = {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0
            }

        stats = self.data["regime_stats"][regime]
        stats["total_trades"] += 1

        if trade_data['result'] == 'win':
            stats["wins"] += 1
        else:
            stats["losses"] += 1

        stats["win_rate"] = (stats["wins"] / stats["total_trades"]) * 100

    def _update_daily_summary(self, trade_data: Dict):
        """Update daily performance summary"""
        date = datetime.fromisoformat(trade_data['timestamp']).date().isoformat()

        if date not in self.data["daily_summary"]:
            self.data["daily_summary"][date] = {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "total_profit": 0.0,
                "win_rate": 0.0,
                "best_hour": None,
                "worst_hour": None
            }

        stats = self.data["daily_summary"][date]
        stats["total_trades"] += 1
        stats["total_profit"] += trade_data.get('profit', 0)

        if trade_data['result'] == 'win':
            stats["wins"] += 1
        else:
            stats["losses"] += 1

        stats["win_rate"] = (stats["wins"] / stats["total_trades"]) * 100

    def get_calibrated_confidence(self, ai_confidence: float) -> float:
        """
        Get calibrated confidence based on historical performance

        If AI says 80% but historically wins only 60% at that level,
        return 60% as the calibrated confidence.
        """
        confidence_bucket = int(ai_confidence / 10) * 10
        conf_key = str(confidence_bucket)

        if conf_key in self.data["confidence_calibration"]:
            stats = self.data["confidence_calibration"][conf_key]
            if stats["total_trades"] >= 5:  # Need minimum sample size
                return stats["actual_win_rate"]

        # No data yet, return original confidence with slight pessimism
        return ai_confidence * 0.9  # 10% discount for uncertainty

    def get_hourly_performance(self, hour: int) -> Dict:
        """Get performance statistics for a specific hour"""
        hour_key = str(hour)
        if hour_key in self.data["hourly_stats"]:
            return self.data["hourly_stats"][hour_key]

        return {
            "total_trades": 0,
            "win_rate": 50.0,  # Default neutral
            "total_profit": 0.0
        }

    def get_best_trading_hours(self, min_trades: int = 10) -> List[Tuple[int, float]]:
        """
        Get hours ranked by win rate
        Returns: [(hour, win_rate), ...]
        """
        hours_with_stats = []

        for hour_str, stats in self.data["hourly_stats"].items():
            if stats["total_trades"] >= min_trades:
                hours_with_stats.append((int(hour_str), stats["win_rate"]))

        # Sort by win rate descending
        hours_with_stats.sort(key=lambda x: x[1], reverse=True)
        return hours_with_stats

    def get_strategy_performance(self, strategy: str) -> Dict:
        """Get performance stats for a specific strategy"""
        if strategy in self.data["strategy_stats"]:
            return self.data["strategy_stats"][strategy]

        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "total_profit": 0.0,
            "avg_profit_per_trade": 0.0
        }

    def get_regime_performance(self, regime: str) -> Dict:
        """Get performance for a specific market regime"""
        if regime in self.data["regime_stats"]:
            return self.data["regime_stats"][regime]

        return {
            "total_trades": 0,
            "win_rate": 0.0
        }

    def get_recent_trades(self, count: int = 50) -> List[Dict]:
        """Get most recent N trades"""
        return self.data["trades"][-count:] if self.data["trades"] else []

    def get_win_streak(self) -> Tuple[int, str]:
        """
        Get current win/loss streak
        Returns: (count, 'win' or 'loss')
        """
        if not self.data["trades"]:
            return (0, 'none')

        streak_count = 0
        streak_type = None

        for trade in reversed(self.data["trades"]):
            result = trade['result']

            if streak_type is None:
                streak_type = result
                streak_count = 1
            elif result == streak_type:
                streak_count += 1
            else:
                break

        return (streak_count, streak_type)

    def get_performance_context_for_ai(self) -> str:
        """
        Generate performance context summary for AI prompts
        """
        recent_trades = self.get_recent_trades(50)

        if not recent_trades:
            return "No trading history available yet. Start building your track record!"

        # Calculate recent win rate
        wins = sum(1 for t in recent_trades if t['result'] == 'win')
        total = len(recent_trades)
        win_rate = (wins / total) * 100

        # Get streak
        streak_count, streak_type = self.get_win_streak()

        # Get current hour performance
        current_hour = datetime.now().hour
        hour_stats = self.get_hourly_performance(current_hour)

        context = f"""
📊 YOUR RECENT PERFORMANCE (Last {total} trades):
   - Win Rate: {win_rate:.1f}%
   - Current Streak: {streak_count} {streak_type.upper()}{'S' if streak_count != 1 else ''}

⏰ HOUR {current_hour}:00 PERFORMANCE:
   - Historical Win Rate: {hour_stats.get('win_rate', 50):.1f}%
   - Trades at this hour: {hour_stats.get('total_trades', 0)}

⚠️ TRADING WISDOM:
   - {"✅ You're on a hot streak - stay disciplined!" if streak_type == 'win' and streak_count >= 3 else ""}
   - {"⚠️ You're in a losing streak - BE EXTRA CONSERVATIVE" if streak_type == 'loss' and streak_count >= 3 else ""}
   - {"✅ This hour is historically profitable for you" if hour_stats.get('win_rate', 0) >= 60 else ""}
   - {"⚠️ This hour has lower win rate historically - trade carefully" if hour_stats.get('win_rate', 100) < 55 else ""}
"""
        return context.strip()

    def should_trade_now(self, min_hour_winrate: float = 55.0, max_loss_streak: int = 5) -> Tuple[bool, str]:
        """
        Determine if trading should be allowed based on performance

        Returns: (should_trade, reason)
        """
        # Check loss streak
        streak_count, streak_type = self.get_win_streak()
        if streak_type == 'loss' and streak_count >= max_loss_streak:
            return (False, f"🛑 STOPPED: {streak_count} consecutive losses. Take a break and reset.")

        # Check hour performance
        current_hour = datetime.now().hour
        hour_stats = self.get_hourly_performance(current_hour)

        if hour_stats['total_trades'] >= 20:  # Enough data
            if hour_stats['win_rate'] < min_hour_winrate:
                return (False, f"⚠️ Hour {current_hour}:00 has {hour_stats['win_rate']:.1f}% win rate (below {min_hour_winrate}%). Consider waiting.")

        return (True, "✅ Clear to trade")

    def get_all_stats_summary(self) -> Dict:
        """Get complete performance summary for dashboard"""
        total_trades = len(self.data["trades"])

        if total_trades == 0:
            return {"total_trades": 0, "message": "No trades yet"}

        wins = sum(1 for t in self.data["trades"] if t['result'] == 'win')
        total_profit = sum(t.get('profit', 0) for t in self.data["trades"])

        return {
            "total_trades": total_trades,
            "total_wins": wins,
            "total_losses": total_trades - wins,
            "overall_win_rate": (wins / total_trades) * 100,
            "total_profit": total_profit,
            "avg_profit_per_trade": total_profit / total_trades,
            "hourly_stats": self.data["hourly_stats"],
            "strategy_stats": self.data["strategy_stats"],
            "regime_stats": self.data["regime_stats"],
            "confidence_calibration": self.data["confidence_calibration"],
            "best_hours": self.get_best_trading_hours(),
            "current_streak": self.get_win_streak(),
        }


# Global instance
_tracker_instance = None

def get_tracker() -> PerformanceTracker:
    """Get or create global performance tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = PerformanceTracker()
    return _tracker_instance

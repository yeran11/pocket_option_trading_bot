"""
Trade Journal - AI-powered trade analysis and learning
Analyzes why trades won/lost and provides insights
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class TradeJournal:
    """
    Record and analyze individual trades with AI insights
    """

    def __init__(self, journal_file: str = "trade_journal.json"):
        self.journal_file = journal_file
        self.entries = self._load_journal()

    def _load_journal(self) -> List[Dict]:
        """Load journal from file"""
        if os.path.exists(self.journal_file):
            try:
                with open(self.journal_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save_journal(self):
        """Save journal to file"""
        try:
            # Keep only last 500 entries
            if len(self.entries) > 500:
                self.entries = self.entries[-500:]

            with open(self.journal_file, 'w') as f:
                json.dump(self.entries, f, indent=2)
        except Exception as e:
            print(f"Error saving journal: {e}")

    def add_entry(
        self,
        trade_data: Dict,
        ai_analysis: Optional[str] = None
    ):
        """
        Add a trade journal entry

        Args:
            trade_data: Full trade information
            ai_analysis: Optional AI-generated analysis of the trade
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'trade': trade_data,
            'ai_analysis': ai_analysis or "Analysis pending"
        }

        self.entries.append(entry)
        self._save_journal()

    def analyze_trade(self, trade_data: Dict) -> str:
        """
        Generate AI analysis of why a trade won or lost

        Returns:
            Analysis string
        """
        result = trade_data.get('result', 'unknown')
        action = trade_data.get('action', 'unknown')
        indicators = trade_data.get('indicators', {})
        regime = trade_data.get('market_regime', 'unknown')

        if result == 'win':
            analysis = f"✅ WIN ANALYSIS:\n"
            analysis += f"   Action: {action.upper()}\n"
            analysis += f"   Market Regime: {regime}\n"
            analysis += f"   Key Factors:\n"

            # Identify what likely caused the win
            if indicators.get('rsi'):
                rsi = indicators['rsi']
                if action == 'call' and rsi < 35:
                    analysis += f"     - RSI oversold ({rsi:.1f}) signaled bounce\n"
                elif action == 'put' and rsi > 65:
                    analysis += f"     - RSI overbought ({rsi:.1f}) signaled drop\n"

            if indicators.get('ema_cross') == 'Bullish' and action == 'call':
                analysis += f"     - EMA bullish cross confirmed uptrend\n"
            elif indicators.get('ema_cross') == 'Bearish' and action == 'put':
                analysis += f"     - EMA bearish cross confirmed downtrend\n"

            if regime in ['trending_up', 'trending_down']:
                analysis += f"     - Trade aligned with {regime.replace('_', ' ')}\n"

            analysis += f"   ✨ Replicate this setup for more wins!\n"

        else:  # loss
            analysis = f"❌ LOSS ANALYSIS:\n"
            analysis += f"   Action: {action.upper()}\n"
            analysis += f"   Market Regime: {regime}\n"
            analysis += f"   Likely Issues:\n"

            # Identify what likely caused the loss
            if regime == 'trending_up' and action == 'put':
                analysis += f"     - MISTAKE: Traded PUT against uptrend\n"
            elif regime == 'trending_down' and action == 'call':
                analysis += f"     - MISTAKE: Traded CALL against downtrend\n"
            elif regime == 'ranging':
                analysis += f"     - Choppy ranging market - hard to predict\n"
            elif regime == 'high_volatility':
                analysis += f"     - High volatility caused unexpected reversal\n"

            if indicators.get('rsi'):
                rsi = indicators['rsi']
                if action == 'call' and rsi > 60:
                    analysis += f"     - RSI already elevated ({rsi:.1f}) - late entry\n"
                elif action == 'put' and rsi < 40:
                    analysis += f"     - RSI already low ({rsi:.1f}) - late entry\n"

            analysis += f"   📚 Lesson: Avoid this setup in future\n"

        return analysis

    def get_recent_entries(self, count: int = 20) -> List[Dict]:
        """Get most recent journal entries"""
        return self.entries[-count:] if self.entries else []

    def get_winning_patterns(self, min_occurrences: int = 3) -> Dict[str, int]:
        """
        Identify patterns that frequently lead to wins

        Returns:
            Dict of pattern descriptions and their win counts
        """
        patterns = {}

        for entry in self.entries:
            trade = entry.get('trade', {})
            if trade.get('result') != 'win':
                continue

            # Create pattern signature
            action = trade.get('action', '')
            regime = trade.get('market_regime', '')
            indicators = trade.get('indicators', {})

            rsi = indicators.get('rsi', 0)
            rsi_zone = 'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'neutral'

            ema_cross = indicators.get('ema_cross', 'neutral')

            pattern = f"{action.upper()} in {regime} with RSI {rsi_zone}, EMA {ema_cross}"

            patterns[pattern] = patterns.get(pattern, 0) + 1

        # Filter to patterns with minimum occurrences
        return {k: v for k, v in patterns.items() if v >= min_occurrences}

    def get_losing_patterns(self, min_occurrences: int = 3) -> Dict[str, int]:
        """Identify patterns that frequently lead to losses"""
        patterns = {}

        for entry in self.entries:
            trade = entry.get('trade', {})
            if trade.get('result') != 'loss':
                continue

            # Create pattern signature
            action = trade.get('action', '')
            regime = trade.get('market_regime', '')

            pattern = f"{action.upper()} in {regime}"

            patterns[pattern] = patterns.get(pattern, 0) + 1

        return {k: v for k, v in patterns.items() if v >= min_occurrences}

    def generate_monthly_report(self) -> str:
        """Generate monthly performance report with insights"""
        # Get trades from last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)

        recent_entries = [
            entry for entry in self.entries
            if datetime.fromisoformat(entry['timestamp']) > cutoff_date
        ]

        if not recent_entries:
            return "No trades in the last 30 days"

        total_trades = len(recent_entries)
        wins = sum(1 for e in recent_entries if e.get('trade', {}).get('result') == 'win')
        losses = total_trades - wins
        win_rate = (wins / total_trades) * 100

        report = f"""
📊 30-DAY PERFORMANCE REPORT
{"="*50}

📈 Overview:
   Total Trades: {total_trades}
   Wins: {wins}
   Losses: {losses}
   Win Rate: {win_rate:.1f}%

✅ TOP WINNING PATTERNS:
"""
        winning_patterns = self.get_winning_patterns(min_occurrences=2)
        if winning_patterns:
            for pattern, count in sorted(winning_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
                report += f"   • {pattern} ({count} wins)\n"
        else:
            report += "   • Not enough data yet\n"

        report += f"""
❌ PATTERNS TO AVOID:
"""
        losing_patterns = self.get_losing_patterns(min_occurrences=2)
        if losing_patterns:
            for pattern, count in sorted(losing_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
                report += f"   • {pattern} ({count} losses)\n"
        else:
            report += "   • No consistent losing patterns identified\n"

        report += f"""
💡 RECOMMENDATIONS:
   • {"Focus on your winning patterns above" if winning_patterns else "Build more trading history to identify patterns"}
   • {"Avoid the losing patterns identified" if losing_patterns else "Keep learning from each trade"}
   • {"Your win rate is strong! Keep up the discipline." if win_rate >= 60 else "Focus on quality over quantity"}
"""

        return report


# Global instance
_journal_instance = None

def get_journal() -> TradeJournal:
    """Get or create global trade journal instance"""
    global _journal_instance
    if _journal_instance is None:
        _journal_instance = TradeJournal()
    return _journal_instance

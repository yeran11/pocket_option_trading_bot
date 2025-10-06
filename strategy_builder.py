"""
Strategy Builder - Create and manage custom trading strategies
Allows users to build strategies using conditions, indicators, and risk management
"""

import json
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


class StrategyBuilder:
    """
    Build, save, and execute custom trading strategies

    Strategy Structure:
    {
        'name': 'My Scalping Strategy',
        'description': 'Quick scalps on oversold RSI',
        'entry_conditions': [
            {'indicator': 'rsi', 'operator': '<', 'value': 30},
            {'indicator': 'macd_histogram', 'operator': '>', 'value': 0},
        ],
        'exit_conditions': {...},
        'risk_management': {
            'max_trades_per_day': 50,
            'max_consecutive_losses': 3,
            'position_size_percent': 2.0
        },
        'ai_integration': {
            'mode': 'validator',  # 'none', 'validator', 'override'
            'min_ai_confidence': 70
        },
        'regime_filter': ['trending_up', 'ranging'],
        'timeframe_alignment': True,
        'active': True,
        'performance': {
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0,
            'total_profit': 0.0
        }
    }
    """

    def __init__(self, strategies_file: str = "custom_strategies.json"):
        self.strategies_file = strategies_file
        self.strategies = self._load_strategies()

    def _load_strategies(self) -> Dict[str, Dict]:
        """Load strategies from file"""
        if os.path.exists(self.strategies_file):
            try:
                with open(self.strategies_file, 'r') as f:
                    return json.load(f)
            except:
                pass

        # Return default strategies
        return self._get_default_strategies()

    def _get_default_strategies(self) -> Dict[str, Dict]:
        """Create default starter strategies"""
        return {
            "rsi_oversold_scalp": {
                "name": "RSI Oversold Scalp",
                "description": "Buy when RSI oversold + MACD bullish",
                "entry_conditions": [
                    {"indicator": "rsi", "operator": "<", "value": 30, "action": "call"},
                    {"indicator": "macd_histogram", "operator": ">", "value": 0, "action": "call"}
                ],
                "ai_integration": {
                    "mode": "validator",
                    "min_ai_confidence": 70
                },
                "risk_management": {
                    "max_trades_per_day": 50,
                    "max_consecutive_losses": 3,
                    "position_size_percent": 2.0
                },
                "regime_filter": ["trending_up", "ranging"],
                "timeframe_alignment": False,
                "active": True,
                "performance": {
                    "total_trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "win_rate": 0.0,
                    "total_profit": 0.0
                }
            },
            "bollinger_breakout": {
                "name": "Bollinger Band Breakout",
                "description": "Trade breakouts from Bollinger Bands",
                "entry_conditions": [
                    {"indicator": "price", "operator": ">", "value": "upper_bb", "action": "call"},
                    {"indicator": "volume_trend", "operator": "==", "value": "increasing", "action": "call"}
                ],
                "ai_integration": {
                    "mode": "validator",
                    "min_ai_confidence": 75
                },
                "risk_management": {
                    "max_trades_per_day": 30,
                    "max_consecutive_losses": 4,
                    "position_size_percent": 1.5
                },
                "regime_filter": ["trending_up", "trending_down", "high_volatility"],
                "timeframe_alignment": True,
                "active": False,
                "performance": {
                    "total_trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "win_rate": 0.0,
                    "total_profit": 0.0
                }
            }
        }

    def _save_strategies(self):
        """Save strategies to file"""
        try:
            with open(self.strategies_file, 'w') as f:
                json.dump(self.strategies, f, indent=2)
        except Exception as e:
            print(f"Error saving strategies: {e}")

    def create_strategy(self, strategy_data: Dict) -> Tuple[bool, str]:
        """
        Create a new strategy

        Args:
            strategy_data: Strategy configuration dict

        Returns:
            (success, message)
        """
        # Validate required fields
        required_fields = ['name', 'entry_conditions']
        for field in required_fields:
            if field not in strategy_data:
                return (False, f"Missing required field: {field}")

        # Generate strategy ID from name
        strategy_id = strategy_data['name'].lower().replace(' ', '_')

        # Check if exists
        if strategy_id in self.strategies:
            return (False, f"Strategy '{strategy_data['name']}' already exists")

        # Set defaults
        if 'description' not in strategy_data:
            strategy_data['description'] = ''

        if 'ai_integration' not in strategy_data:
            strategy_data['ai_integration'] = {
                'mode': 'none',
                'min_ai_confidence': 70
            }

        if 'risk_management' not in strategy_data:
            strategy_data['risk_management'] = {
                'max_trades_per_day': 50,
                'max_consecutive_losses': 3,
                'position_size_percent': 2.0
            }

        if 'regime_filter' not in strategy_data:
            strategy_data['regime_filter'] = []

        if 'timeframe_alignment' not in strategy_data:
            strategy_data['timeframe_alignment'] = False

        if 'active' not in strategy_data:
            strategy_data['active'] = True

        if 'performance' not in strategy_data:
            strategy_data['performance'] = {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0.0,
                'total_profit': 0.0,
                'created_at': datetime.now().isoformat()
            }

        # Save strategy
        self.strategies[strategy_id] = strategy_data
        self._save_strategies()

        return (True, f"Strategy '{strategy_data['name']}' created successfully!")

    def update_strategy(self, strategy_id: str, updates: Dict) -> Tuple[bool, str]:
        """Update an existing strategy"""
        if strategy_id not in self.strategies:
            return (False, f"Strategy '{strategy_id}' not found")

        # Update fields
        self.strategies[strategy_id].update(updates)
        self._save_strategies()

        return (True, f"Strategy '{strategy_id}' updated successfully!")

    def delete_strategy(self, strategy_id: str) -> Tuple[bool, str]:
        """Delete a strategy"""
        if strategy_id not in self.strategies:
            return (False, f"Strategy '{strategy_id}' not found")

        del self.strategies[strategy_id]
        self._save_strategies()

        return (True, f"Strategy '{strategy_id}' deleted successfully!")

    def get_strategy(self, strategy_id: str) -> Optional[Dict]:
        """Get a specific strategy"""
        return self.strategies.get(strategy_id)

    def get_all_strategies(self) -> Dict[str, Dict]:
        """Get all strategies"""
        return self.strategies

    def get_active_strategies(self) -> Dict[str, Dict]:
        """Get only active strategies"""
        return {
            sid: strat for sid, strat in self.strategies.items()
            if strat.get('active', False)
        }

    def evaluate_strategy(
        self,
        strategy_id: str,
        market_data: Dict,
        indicators: Dict,
        regime: str,
        mtf_aligned: bool,
        ai_decision: Optional[Tuple[str, float, str]] = None
    ) -> Tuple[Optional[str], float, str]:
        """
        Evaluate if strategy conditions are met

        Returns:
            (action, confidence, reason) or (None, 0, reason) if no signal
        """
        strategy = self.get_strategy(strategy_id)

        if not strategy or not strategy.get('active'):
            return (None, 0.0, f"Strategy '{strategy_id}' not active")

        # Check regime filter
        if strategy.get('regime_filter'):
            if regime not in strategy['regime_filter']:
                return (None, 0.0, f"Regime '{regime}' not in allowed regimes: {strategy['regime_filter']}")

        # Check timeframe alignment
        if strategy.get('timeframe_alignment', False):
            if not mtf_aligned:
                return (None, 0.0, "Higher timeframes not aligned - skipping")

        # Evaluate entry conditions
        conditions_met, action, confidence, reasons = self._evaluate_conditions(
            strategy['entry_conditions'],
            indicators
        )

        if not conditions_met:
            return (None, 0.0, "Entry conditions not met")

        # Check AI integration
        ai_mode = strategy.get('ai_integration', {}).get('mode', 'none')
        min_ai_conf = strategy.get('ai_integration', {}).get('min_ai_confidence', 70)

        if ai_mode != 'none' and ai_decision:
            ai_action, ai_confidence, ai_reason = ai_decision

            if ai_mode == 'validator':
                # AI must agree
                if ai_action.lower() != action.lower():
                    return (None, 0.0, f"AI disagrees: AI says {ai_action}, strategy says {action}")

                if ai_confidence < min_ai_conf:
                    return (None, 0.0, f"AI confidence {ai_confidence}% below minimum {min_ai_conf}%")

                # AI agrees, boost confidence
                combined_confidence = (confidence + ai_confidence) / 2
                return (action, combined_confidence, f"✅ Strategy + AI aligned: {', '.join(reasons)}")

            elif ai_mode == 'override':
                # AI can override if very confident
                if ai_confidence >= 85:
                    return (ai_action, ai_confidence, f"🤖 AI OVERRIDE (conf {ai_confidence}%): {ai_reason}")
                else:
                    # Use strategy decision
                    return (action, confidence, f"Strategy decision: {', '.join(reasons)}")

        # No AI integration or AI mode is 'none'
        return (action, confidence, f"Strategy conditions met: {', '.join(reasons)}")

    def _evaluate_conditions(
        self,
        conditions: List[Dict],
        indicators: Dict
    ) -> Tuple[bool, Optional[str], float, List[str]]:
        """
        Evaluate a list of conditions

        Returns:
            (all_met, action, confidence, reasons)
        """
        if not conditions:
            return (False, None, 0.0, ["No conditions defined"])

        met_count = 0
        total_count = len(conditions)
        reasons = []
        actions = []

        for condition in conditions:
            indicator_name = condition.get('indicator')
            operator = condition.get('operator')
            threshold = condition.get('value')
            action = condition.get('action', 'call')  # Default to call

            # Get indicator value
            indicator_value = indicators.get(indicator_name)

            if indicator_value is None:
                continue  # Skip if indicator not available

            # Handle special values (like 'upper_bb', 'lower_bb')
            if isinstance(threshold, str) and threshold in indicators:
                threshold = indicators[threshold]

            # Evaluate condition
            met = self._evaluate_single_condition(indicator_value, operator, threshold)

            if met:
                met_count += 1
                reasons.append(f"{indicator_name} {operator} {threshold}")
                actions.append(action)

        # All conditions must be met
        all_met = (met_count == total_count)

        # Determine action (majority vote if multiple actions)
        if actions:
            action = max(set(actions), key=actions.count)  # Most common action
        else:
            action = None

        # Confidence based on how many conditions met
        confidence = (met_count / total_count) * 100 if total_count > 0 else 0

        return (all_met, action, confidence, reasons)

    def _evaluate_single_condition(
        self,
        indicator_value: Any,
        operator: str,
        threshold: Any
    ) -> bool:
        """Evaluate a single condition"""
        try:
            if operator == '>':
                return float(indicator_value) > float(threshold)
            elif operator == '<':
                return float(indicator_value) < float(threshold)
            elif operator == '>=':
                return float(indicator_value) >= float(threshold)
            elif operator == '<=':
                return float(indicator_value) <= float(threshold)
            elif operator == '==':
                return str(indicator_value).lower() == str(threshold).lower()
            elif operator == '!=':
                return str(indicator_value).lower() != str(threshold).lower()
            else:
                return False
        except:
            return False

    def record_strategy_result(
        self,
        strategy_id: str,
        result: str,
        profit: float
    ):
        """Record the result of a strategy trade"""
        if strategy_id not in self.strategies:
            return

        perf = self.strategies[strategy_id].get('performance', {})

        perf['total_trades'] = perf.get('total_trades', 0) + 1

        if result == 'win':
            perf['wins'] = perf.get('wins', 0) + 1
        else:
            perf['losses'] = perf.get('losses', 0) + 1

        perf['total_profit'] = perf.get('total_profit', 0.0) + profit

        if perf['total_trades'] > 0:
            perf['win_rate'] = (perf['wins'] / perf['total_trades']) * 100

        perf['last_updated'] = datetime.now().isoformat()

        self.strategies[strategy_id]['performance'] = perf
        self._save_strategies()

    def clone_strategy(self, source_id: str, new_name: str) -> Tuple[bool, str]:
        """Clone an existing strategy with a new name"""
        if source_id not in self.strategies:
            return (False, f"Source strategy '{source_id}' not found")

        # Create copy
        new_strategy = dict(self.strategies[source_id])
        new_strategy['name'] = new_name
        new_strategy['performance'] = {
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'created_at': datetime.now().isoformat(),
            'cloned_from': source_id
        }

        # Create with new name
        return self.create_strategy(new_strategy)

    def get_performance_leaderboard(self) -> List[Tuple[str, Dict]]:
        """
        Get strategies ranked by performance

        Returns:
            List of (strategy_id, strategy_data) sorted by win rate
        """
        strategies_with_perf = [
            (sid, strat) for sid, strat in self.strategies.items()
            if strat.get('performance', {}).get('total_trades', 0) >= 10  # Min 10 trades
        ]

        # Sort by win rate descending
        strategies_with_perf.sort(
            key=lambda x: x[1].get('performance', {}).get('win_rate', 0),
            reverse=True
        )

        return strategies_with_perf


# Global instance
_builder_instance = None

def get_builder() -> StrategyBuilder:
    """Get or create global strategy builder instance"""
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = StrategyBuilder()
    return _builder_instance

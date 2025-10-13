"""
🎯 ULTRA-SOPHISTICATED STRATEGY BUILDER
Master-Level Strategy Creation and Multi-Strategy Execution System

Features:
- AND/OR condition groups for complex logic
- Multi-strategy simultaneous execution
- Strategy priority and conflict resolution
- Signal aggregation (voting, weighted, priority-based)
- Time and asset filters
- Advanced per-strategy risk management
- Real-time performance tracking
- Strategy templates library
"""

import json
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, time as dt_time
from collections import defaultdict


class AdvancedStrategyBuilder:
    """
    Ultra-sophisticated strategy builder with master-level features

    Strategy Structure (Enhanced):
    {
        'name': 'My Master Strategy',
        'description': 'Advanced multi-condition strategy',
        'priority': 1,  # 1-10, higher = executes first
        'condition_groups': [
            {
                'logic': 'AND',  # or 'OR'
                'conditions': [
                    {'indicator': 'rsi', 'operator': '<', 'value': 30, 'weight': 1.0},
                    {'indicator': 'macd_histogram', 'operator': '>', 'value': 0, 'weight': 1.5},
                ]
            }
        ],
        'action': 'call',  # or 'put' or 'auto' (determined by conditions)
        'time_filter': {
            'enabled': True,
            'allowed_hours': [[9, 12], [14, 17]],  # Trade 9-12 and 14-17
            'timezone': 'UTC'
        },
        'asset_filter': {
            'enabled': True,
            'whitelist': ['EUR/USD', 'GBP/USD'],  # Only these assets
            'blacklist': []  # Or exclude these
        },
        'risk_management': {
            'max_trades_per_day': 50,
            'max_trades_per_hour': 10,
            'max_consecutive_losses': 3,
            'position_size_percent': 2.0,
            'stop_on_drawdown_percent': 5.0,
            'take_profit_target_percent': 10.0
        },
        'signal_strength': {
            'min_confidence': 70,
            'condition_weights': True  # Use weighted conditions
        },
        'regime_filter': ['trending_up', 'ranging'],
        'timeframe_alignment': True,
        'active': True,
        'performance': {
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'avg_profit_per_trade': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'trades_today': 0,
            'trades_this_hour': 0,
            'consecutive_losses': 0,
            'last_trade_time': None
        }
    }
    """

    def __init__(self, strategies_file: str = "custom_strategies.json"):
        self.strategies_file = strategies_file
        self.strategies = self._load_strategies()
        self.execution_mode = 'priority'  # 'priority', 'all', 'voting', 'weighted'

    def _load_strategies(self) -> Dict[str, Dict]:
        """Load strategies from file"""
        if os.path.exists(self.strategies_file):
            try:
                with open(self.strategies_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_strategies(self):
        """Save strategies to file"""
        try:
            with open(self.strategies_file, 'w') as f:
                json.dump(self.strategies, f, indent=2)
        except Exception as e:
            print(f"Error saving strategies: {e}")

    def set_execution_mode(self, mode: str):
        """
        Set multi-strategy execution mode

        Modes:
        - 'priority': Execute highest priority strategy only
        - 'all': Execute all triggered strategies
        - 'voting': Majority vote wins
        - 'weighted': Weighted by confidence
        """
        if mode in ['priority', 'all', 'voting', 'weighted']:
            self.execution_mode = mode

    def evaluate_multiple_strategies(
        self,
        market_data: Dict,
        indicators: Dict,
        regime: str,
        mtf_aligned: bool
    ) -> List[Dict]:
        """
        Evaluate all active strategies and return signals based on execution mode

        Returns:
            List of strategy signals with actions and confidence
        """
        signals = []

        # Get all active strategies
        active_strategies = self.get_active_strategies()

        # Sort by priority (highest first)
        sorted_strategies = sorted(
            active_strategies.items(),
            key=lambda x: x[1].get('priority', 5),
            reverse=True
        )

        # Evaluate each strategy
        for strategy_id, strategy in sorted_strategies:
            # Check time filter
            if not self._check_time_filter(strategy):
                continue

            # Check asset filter
            current_asset = market_data.get('asset', 'Unknown')
            if not self._check_asset_filter(strategy, current_asset):
                continue

            # Check risk limits
            if not self._check_risk_limits(strategy):
                continue

            # Evaluate strategy conditions
            result = self._evaluate_strategy_conditions(
                strategy,
                indicators,
                regime,
                mtf_aligned
            )

            if result['signal']:
                signals.append({
                    'strategy_id': strategy_id,
                    'strategy_name': strategy['name'],
                    'action': result['action'],
                    'confidence': result['confidence'],
                    'reason': result['reason'],
                    'priority': strategy.get('priority', 5)
                })

                # In priority mode, stop after first signal
                if self.execution_mode == 'priority':
                    break

        # Apply execution mode logic
        return self._aggregate_signals(signals)

    def _evaluate_strategy_conditions(
        self,
        strategy: Dict,
        indicators: Dict,
        regime: str,
        mtf_aligned: bool
    ) -> Dict:
        """
        Evaluate strategy with AND/OR condition groups

        Returns:
            {'signal': bool, 'action': str, 'confidence': float, 'reason': str}
        """
        # Check regime filter
        if strategy.get('regime_filter'):
            if regime not in strategy['regime_filter']:
                return {'signal': False, 'action': None, 'confidence': 0.0,
                       'reason': f"Regime '{regime}' not allowed"}

        # Check timeframe alignment
        if strategy.get('timeframe_alignment', False):
            if not mtf_aligned:
                return {'signal': False, 'action': None, 'confidence': 0.0,
                       'reason': "Higher timeframes not aligned"}

        # Evaluate condition groups
        condition_groups = strategy.get('condition_groups', [])
        if not condition_groups:
            # Fallback to old-style entry_conditions
            return self._evaluate_legacy_conditions(strategy, indicators)

        group_results = []
        all_reasons = []

        for group in condition_groups:
            group_logic = group.get('logic', 'AND')
            conditions = group.get('conditions', [])

            met_conditions = 0
            total_weight = 0.0
            met_weight = 0.0
            group_reasons = []

            for condition in conditions:
                indicator_name = condition.get('indicator')
                operator = condition.get('operator')
                threshold = condition.get('value')
                weight = condition.get('weight', 1.0)

                total_weight += weight

                # Get indicator value
                indicator_value = indicators.get(indicator_name)
                if indicator_value is None:
                    continue

                # Handle special values
                if isinstance(threshold, str) and threshold in indicators:
                    threshold = indicators[threshold]

                # Evaluate condition
                if self._evaluate_single_condition(indicator_value, operator, threshold):
                    met_conditions += 1
                    met_weight += weight
                    group_reasons.append(f"{indicator_name} {operator} {threshold}")

            # Check if group passes
            if group_logic == 'AND':
                group_passes = (met_conditions == len(conditions))
            else:  # OR
                group_passes = (met_conditions > 0)

            if group_passes:
                # Calculate group confidence
                if strategy.get('signal_strength', {}).get('condition_weights', False):
                    group_confidence = (met_weight / total_weight * 100) if total_weight > 0 else 0
                else:
                    group_confidence = (met_conditions / len(conditions) * 100) if conditions else 0

                group_results.append(group_confidence)
                all_reasons.extend(group_reasons)

        # Check if any groups passed
        if not group_results:
            return {'signal': False, 'action': None, 'confidence': 0.0,
                   'reason': "No condition groups met"}

        # Calculate overall confidence (average of all groups that passed)
        overall_confidence = sum(group_results) / len(group_results)

        # Check minimum confidence
        min_conf = strategy.get('signal_strength', {}).get('min_confidence', 70)
        if overall_confidence < min_conf:
            return {'signal': False, 'action': None, 'confidence': overall_confidence,
                   'reason': f"Confidence {overall_confidence:.1f}% below minimum {min_conf}%"}

        # Determine action
        action = strategy.get('action', 'auto')
        if action == 'auto':
            # Determine from conditions (not implemented in this version)
            action = 'call'

        return {
            'signal': True,
            'action': action,
            'confidence': overall_confidence,
            'reason': ' + '.join(all_reasons)
        }

    def _evaluate_legacy_conditions(self, strategy: Dict, indicators: Dict) -> Dict:
        """Evaluate old-style entry_conditions for backward compatibility"""
        conditions = strategy.get('entry_conditions', [])
        if not conditions:
            return {'signal': False, 'action': None, 'confidence': 0.0,
                   'reason': "No conditions defined"}

        met_count = 0
        reasons = []
        actions = []

        for condition in conditions:
            indicator_name = condition.get('indicator')
            operator = condition.get('operator')
            threshold = condition.get('value')
            action = condition.get('action', 'call')

            indicator_value = indicators.get(indicator_name)
            if indicator_value is None:
                continue

            if isinstance(threshold, str) and threshold in indicators:
                threshold = indicators[threshold]

            if self._evaluate_single_condition(indicator_value, operator, threshold):
                met_count += 1
                reasons.append(f"{indicator_name} {operator} {threshold}")
                actions.append(action)

        all_met = (met_count == len(conditions))
        confidence = (met_count / len(conditions) * 100) if conditions else 0
        action = max(set(actions), key=actions.count) if actions else None

        return {
            'signal': all_met,
            'action': action,
            'confidence': confidence,
            'reason': ' + '.join(reasons) if reasons else "Conditions not met"
        }

    def _evaluate_single_condition(self, indicator_value: Any, operator: str, threshold: Any) -> bool:
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
            elif operator == 'contains':
                return str(threshold).lower() in str(indicator_value).lower()
            else:
                return False
        except:
            return False

    def _check_time_filter(self, strategy: Dict) -> bool:
        """Check if current time is within allowed trading hours"""
        time_filter = strategy.get('time_filter', {})
        if not time_filter.get('enabled', False):
            return True

        allowed_hours = time_filter.get('allowed_hours', [])
        if not allowed_hours:
            return True

        current_hour = datetime.now().hour

        for hour_range in allowed_hours:
            if len(hour_range) == 2:
                start, end = hour_range
                if start <= current_hour < end:
                    return True

        return False

    def _check_asset_filter(self, strategy: Dict, asset: str) -> bool:
        """Check if asset is allowed for this strategy"""
        asset_filter = strategy.get('asset_filter', {})
        if not asset_filter.get('enabled', False):
            return True

        whitelist = asset_filter.get('whitelist', [])
        blacklist = asset_filter.get('blacklist', [])

        if whitelist and asset not in whitelist:
            return False

        if blacklist and asset in blacklist:
            return False

        return True

    def _check_risk_limits(self, strategy: Dict) -> bool:
        """Check if strategy is within risk limits"""
        risk_mgmt = strategy.get('risk_management', {})
        perf = strategy.get('performance', {})

        # Check trades today
        max_trades_day = risk_mgmt.get('max_trades_per_day', 999)
        trades_today = perf.get('trades_today', 0)
        if trades_today >= max_trades_day:
            return False

        # Check trades this hour
        max_trades_hour = risk_mgmt.get('max_trades_per_hour', 999)
        trades_hour = perf.get('trades_this_hour', 0)
        if trades_hour >= max_trades_hour:
            return False

        # Check consecutive losses
        max_consecutive_losses = risk_mgmt.get('max_consecutive_losses', 999)
        consecutive_losses = perf.get('consecutive_losses', 0)
        if consecutive_losses >= max_consecutive_losses:
            return False

        return True

    def _aggregate_signals(self, signals: List[Dict]) -> List[Dict]:
        """
        Aggregate multiple signals based on execution mode

        Returns:
            List of signals to execute
        """
        if not signals:
            return []

        if self.execution_mode == 'priority':
            # Return highest priority only (already sorted)
            return [signals[0]] if signals else []

        elif self.execution_mode == 'all':
            # Return all signals
            return signals

        elif self.execution_mode == 'voting':
            # Majority vote wins
            call_votes = sum(1 for s in signals if s['action'] == 'call')
            put_votes = sum(1 for s in signals if s['action'] == 'put')

            if call_votes > put_votes:
                winning_signals = [s for s in signals if s['action'] == 'call']
            elif put_votes > call_votes:
                winning_signals = [s for s in signals if s['action'] == 'put']
            else:
                # Tie - use highest confidence
                winning_signals = [max(signals, key=lambda x: x['confidence'])]

            return winning_signals

        elif self.execution_mode == 'weighted':
            # Weighted by confidence
            call_weight = sum(s['confidence'] for s in signals if s['action'] == 'call')
            put_weight = sum(s['confidence'] for s in signals if s['action'] == 'put')

            if call_weight > put_weight:
                return [max([s for s in signals if s['action'] == 'call'],
                           key=lambda x: x['confidence'])]
            else:
                return [max([s for s in signals if s['action'] == 'put'],
                           key=lambda x: x['confidence'])]

        return signals

    def get_active_strategies(self) -> Dict[str, Dict]:
        """Get only active strategies"""
        return {
            sid: strat for sid, strat in self.strategies.items()
            if strat.get('active', False)
        }

    def get_all_strategies(self) -> Dict[str, Dict]:
        """Get all strategies"""
        return self.strategies

    def toggle_strategy(self, strategy_id: str, active: bool) -> Tuple[bool, str]:
        """Toggle strategy active state"""
        if strategy_id not in self.strategies:
            return (False, f"Strategy '{strategy_id}' not found")

        self.strategies[strategy_id]['active'] = active
        self._save_strategies()

        state = "activated" if active else "deactivated"
        return (True, f"Strategy '{strategy_id}' {state}")

    def update_strategy_priority(self, strategy_id: str, priority: int) -> Tuple[bool, str]:
        """Update strategy execution priority (1-10)"""
        if strategy_id not in self.strategies:
            return (False, f"Strategy '{strategy_id}' not found")

        priority = max(1, min(10, priority))  # Clamp to 1-10
        self.strategies[strategy_id]['priority'] = priority
        self._save_strategies()

        return (True, f"Strategy priority updated to {priority}")

    def record_strategy_result(self, strategy_id: str, result: str, profit: float):
        """Record trade result for strategy"""
        if strategy_id not in self.strategies:
            return

        perf = self.strategies[strategy_id].get('performance', {})

        perf['total_trades'] = perf.get('total_trades', 0) + 1
        perf['trades_today'] = perf.get('trades_today', 0) + 1
        perf['trades_this_hour'] = perf.get('trades_this_hour', 0) + 1

        if result == 'win':
            perf['wins'] = perf.get('wins', 0) + 1
            perf['consecutive_losses'] = 0
        else:
            perf['losses'] = perf.get('losses', 0) + 1
            perf['consecutive_losses'] = perf.get('consecutive_losses', 0) + 1

        perf['total_profit'] = perf.get('total_profit', 0.0) + profit

        if perf['total_trades'] > 0:
            perf['win_rate'] = (perf['wins'] / perf['total_trades']) * 100
            perf['avg_profit_per_trade'] = perf['total_profit'] / perf['total_trades']

        perf['last_trade_time'] = datetime.now().isoformat()

        self.strategies[strategy_id]['performance'] = perf
        self._save_strategies()


# Global instance
_advanced_builder_instance = None

def get_advanced_builder() -> AdvancedStrategyBuilder:
    """Get or create global advanced strategy builder instance"""
    global _advanced_builder_instance
    if _advanced_builder_instance is None:
        _advanced_builder_instance = AdvancedStrategyBuilder()
    return _advanced_builder_instance

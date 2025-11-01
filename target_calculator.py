"""Calculate target buy/sell prices based on technical analysis."""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class TargetPriceCalculator:
    """Calculate target prices for buy/sell based on technical indicators."""
    
    def __init__(self, price_data: pd.DataFrame, indicators: Dict):
        """Initialize target price calculator.
        
        Args:
            price_data: DataFrame with price and indicator data
            indicators: Dictionary of current indicator values
        """
        self.df = price_data
        self.indicators = indicators
        self.current_price = indicators['price']
    
    def calculate_targets(self, signal: str) -> Dict[str, Optional[float]]:
        """Calculate buy/sell targets and stop loss based on signal.
        
        Args:
            signal: Trading signal (strong_buy, buy, hold, sell, strong_sell)
            
        Returns:
            Dictionary with buy_target, sell_target, stop_loss, risk_reward_ratio
        """
        if signal in ['strong_buy', 'buy']:
            return self._calculate_bullish_targets()
        elif signal in ['strong_sell', 'sell']:
            return self._calculate_bearish_targets()
        else:  # hold
            return self._calculate_neutral_targets()
    
    def _calculate_bullish_targets(self) -> Dict:
        """Calculate targets for bullish scenario."""
        targets = {}
        
        # Buy target: Lower Bollinger Band or recent support
        support_level = self._find_support_level()
        bb_lower = self.indicators.get('bb_lower')
        
        if bb_lower and support_level:
            targets['buy_target'] = min(bb_lower, support_level)
        elif bb_lower:
            targets['buy_target'] = bb_lower
        elif support_level:
            targets['buy_target'] = support_level
        else:
            # Fallback: 2-3% below current price
            targets['buy_target'] = self.current_price * 0.97
        
        # Sell target: Upper Bollinger Band or resistance
        resistance_level = self._find_resistance_level()
        bb_upper = self.indicators.get('bb_upper')
        
        if bb_upper and resistance_level:
            targets['sell_target'] = max(bb_upper, resistance_level)
        elif bb_upper:
            targets['sell_target'] = bb_upper
        elif resistance_level:
            targets['sell_target'] = resistance_level
        else:
            # Fallback: 5-10% above current price
            targets['sell_target'] = self.current_price * 1.08
        
        # Stop loss: Below support with ATR buffer
        atr = self.indicators.get('atr', self.current_price * 0.02)
        if targets.get('buy_target'):
            targets['stop_loss'] = targets['buy_target'] - (1.5 * atr)
        else:
            targets['stop_loss'] = self.current_price * 0.95
        
        # Calculate risk/reward ratio
        if targets.get('buy_target') and targets.get('sell_target') and targets.get('stop_loss'):
            risk = targets['buy_target'] - targets['stop_loss']
            reward = targets['sell_target'] - targets['buy_target']
            if risk > 0:
                targets['risk_reward_ratio'] = reward / risk
            else:
                targets['risk_reward_ratio'] = 0
        
        return targets
    
    def _calculate_bearish_targets(self) -> Dict:
        """Calculate targets for bearish scenario."""
        targets = {}
        
        # Sell target: Current price or upper resistance
        resistance_level = self._find_resistance_level()
        bb_upper = self.indicators.get('bb_upper')
        
        if resistance_level and resistance_level > self.current_price:
            targets['sell_target'] = resistance_level
        elif bb_upper and bb_upper > self.current_price:
            targets['sell_target'] = bb_upper
        else:
            # Sell near current price or slight bounce
            targets['sell_target'] = self.current_price * 1.02
        
        # Buy target: Lower support level
        support_level = self._find_support_level()
        bb_lower = self.indicators.get('bb_lower')
        
        if bb_lower and support_level:
            targets['buy_target'] = min(bb_lower, support_level)
        elif bb_lower:
            targets['buy_target'] = bb_lower
        elif support_level:
            targets['buy_target'] = support_level
        else:
            # Fallback: 8-12% below current price
            targets['buy_target'] = self.current_price * 0.90
        
        # Stop loss: Above current price (for short positions) or below buy target
        atr = self.indicators.get('atr', self.current_price * 0.02)
        if targets.get('sell_target'):
            targets['stop_loss'] = targets['sell_target'] + (1.5 * atr)
        else:
            targets['stop_loss'] = self.current_price * 1.05
        
        # Calculate risk/reward ratio (for re-buying)
        if targets.get('sell_target') and targets.get('buy_target'):
            profit = targets['sell_target'] - targets['buy_target']
            risk = targets['buy_target'] * 0.05  # Assume 5% risk on re-buy
            if risk > 0:
                targets['risk_reward_ratio'] = profit / risk
            else:
                targets['risk_reward_ratio'] = 0
        
        return targets
    
    def _calculate_neutral_targets(self) -> Dict:
        """Calculate targets for neutral/hold scenario."""
        targets = {}
        
        # Set wide ranges for hold scenario
        bb_lower = self.indicators.get('bb_lower')
        bb_upper = self.indicators.get('bb_upper')
        
        if bb_lower:
            targets['buy_target'] = bb_lower
        else:
            targets['buy_target'] = self.current_price * 0.95
        
        if bb_upper:
            targets['sell_target'] = bb_upper
        else:
            targets['sell_target'] = self.current_price * 1.05
        
        # Stop loss: Below BB lower or 8% below
        if bb_lower:
            atr = self.indicators.get('atr', self.current_price * 0.02)
            targets['stop_loss'] = bb_lower - (1.5 * atr)
        else:
            targets['stop_loss'] = self.current_price * 0.92
        
        targets['risk_reward_ratio'] = 1.0  # Neutral
        
        return targets
    
    def _find_support_level(self) -> Optional[float]:
        """Find nearest support level from recent lows."""
        if len(self.df) < 20:
            return None
        
        # Look at recent 30 days
        recent_data = self.df.tail(30)
        
        # Find local minima (support levels)
        lows = recent_data['price'].rolling(window=5, center=True).min()
        support_levels = recent_data[recent_data['price'] == lows]['price'].values
        
        # Get support levels below current price
        support_below = [s for s in support_levels if s < self.current_price]
        
        if support_below:
            # Return the nearest support below current price
            return max(support_below)
        
        return None
    
    def _find_resistance_level(self) -> Optional[float]:
        """Find nearest resistance level from recent highs."""
        if len(self.df) < 20:
            return None
        
        # Look at recent 30 days
        recent_data = self.df.tail(30)
        
        # Find local maxima (resistance levels)
        highs = recent_data['price'].rolling(window=5, center=True).max()
        resistance_levels = recent_data[recent_data['price'] == highs]['price'].values
        
        # Get resistance levels above current price
        resistance_above = [r for r in resistance_levels if r > self.current_price]
        
        if resistance_above:
            # Return the nearest resistance above current price
            return min(resistance_above)
        
        return None


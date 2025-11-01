"""Technical analysis indicators and calculations."""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange


class TechnicalAnalyzer:
    """Performs technical analysis on price data."""
    
    def __init__(self, price_data: pd.DataFrame):
        """Initialize the technical analyzer.
        
        Args:
            price_data: DataFrame with 'price' column and datetime index
        """
        self.df = price_data.copy()
        self._calculate_indicators()
    
    def _calculate_indicators(self):
        """Calculate all technical indicators."""
        if len(self.df) < 2:
            return
        
        # Momentum Indicators
        self._calculate_rsi()
        self._calculate_stochastic()
        
        # Trend Indicators
        self._calculate_moving_averages()
        self._calculate_macd()
        
        # Volatility Indicators
        self._calculate_bollinger_bands()
        self._calculate_atr()
    
    def _calculate_rsi(self, period: int = 14):
        """Calculate Relative Strength Index."""
        try:
            rsi = RSIIndicator(close=self.df['price'], window=period)
            self.df['rsi'] = rsi.rsi()
        except Exception as e:
            print(f"Error calculating RSI: {e}")
            self.df['rsi'] = np.nan
    
    def _calculate_stochastic(self, period: int = 14):
        """Calculate Stochastic Oscillator."""
        try:
            # Create high, low, close from price (simplified)
            self.df['high'] = self.df['price']
            self.df['low'] = self.df['price']
            
            stoch = StochasticOscillator(
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['price'],
                window=period
            )
            self.df['stoch_k'] = stoch.stoch()
            self.df['stoch_d'] = stoch.stoch_signal()
        except Exception as e:
            print(f"Error calculating Stochastic: {e}")
            self.df['stoch_k'] = np.nan
            self.df['stoch_d'] = np.nan
    
    def _calculate_moving_averages(self):
        """Calculate various moving averages."""
        try:
            # Simple Moving Averages
            sma_20 = SMAIndicator(close=self.df['price'], window=20)
            sma_50 = SMAIndicator(close=self.df['price'], window=50)
            
            self.df['sma_20'] = sma_20.sma_indicator()
            self.df['sma_50'] = sma_50.sma_indicator()
            
            # Exponential Moving Averages
            ema_12 = EMAIndicator(close=self.df['price'], window=12)
            ema_26 = EMAIndicator(close=self.df['price'], window=26)
            
            self.df['ema_12'] = ema_12.ema_indicator()
            self.df['ema_26'] = ema_26.ema_indicator()
        except Exception as e:
            print(f"Error calculating moving averages: {e}")
            self.df['sma_20'] = np.nan
            self.df['sma_50'] = np.nan
            self.df['ema_12'] = np.nan
            self.df['ema_26'] = np.nan
    
    def _calculate_macd(self):
        """Calculate MACD indicator."""
        try:
            macd = MACD(close=self.df['price'])
            self.df['macd'] = macd.macd()
            self.df['macd_signal'] = macd.macd_signal()
            self.df['macd_diff'] = macd.macd_diff()
        except Exception as e:
            print(f"Error calculating MACD: {e}")
            self.df['macd'] = np.nan
            self.df['macd_signal'] = np.nan
            self.df['macd_diff'] = np.nan
    
    def _calculate_bollinger_bands(self, period: int = 20, std_dev: int = 2):
        """Calculate Bollinger Bands."""
        try:
            bb = BollingerBands(
                close=self.df['price'],
                window=period,
                window_dev=std_dev
            )
            self.df['bb_upper'] = bb.bollinger_hband()
            self.df['bb_middle'] = bb.bollinger_mavg()
            self.df['bb_lower'] = bb.bollinger_lband()
            self.df['bb_width'] = bb.bollinger_wband()
        except Exception as e:
            print(f"Error calculating Bollinger Bands: {e}")
            self.df['bb_upper'] = np.nan
            self.df['bb_middle'] = np.nan
            self.df['bb_lower'] = np.nan
            self.df['bb_width'] = np.nan
    
    def _calculate_atr(self, period: int = 14):
        """Calculate Average True Range."""
        try:
            # Use price as high/low/close for simplified ATR
            atr = AverageTrueRange(
                high=self.df['price'],
                low=self.df['price'],
                close=self.df['price'],
                window=period
            )
            self.df['atr'] = atr.average_true_range()
        except Exception as e:
            print(f"Error calculating ATR: {e}")
            self.df['atr'] = np.nan
    
    def get_latest_indicators(self) -> Dict:
        """Get the most recent values of all indicators.
        
        Returns:
            Dictionary with current indicator values
        """
        if len(self.df) == 0:
            return {}
        
        latest = self.df.iloc[-1]
        current_price = latest['price']
        
        return {
            'price': current_price,
            'rsi': latest.get('rsi'),
            'stoch_k': latest.get('stoch_k'),
            'stoch_d': latest.get('stoch_d'),
            'sma_20': latest.get('sma_20'),
            'sma_50': latest.get('sma_50'),
            'ema_12': latest.get('ema_12'),
            'ema_26': latest.get('ema_26'),
            'macd': latest.get('macd'),
            'macd_signal': latest.get('macd_signal'),
            'macd_diff': latest.get('macd_diff'),
            'bb_upper': latest.get('bb_upper'),
            'bb_middle': latest.get('bb_middle'),
            'bb_lower': latest.get('bb_lower'),
            'bb_width': latest.get('bb_width'),
            'atr': latest.get('atr'),
        }
    
    def get_trend_analysis(self) -> Dict:
        """Analyze current price trends.
        
        Returns:
            Dictionary with trend information
        """
        indicators = self.get_latest_indicators()
        price = indicators['price']
        
        trends = {
            'short_term': 'neutral',
            'medium_term': 'neutral',
            'long_term': 'neutral'
        }
        
        # Short-term trend (EMA 12 vs EMA 26)
        if indicators.get('ema_12') and indicators.get('ema_26'):
            if indicators['ema_12'] > indicators['ema_26']:
                trends['short_term'] = 'bullish'
            elif indicators['ema_12'] < indicators['ema_26']:
                trends['short_term'] = 'bearish'
        
        # Medium-term trend (price vs SMA 20)
        if indicators.get('sma_20'):
            if price > indicators['sma_20']:
                trends['medium_term'] = 'bullish'
            elif price < indicators['sma_20']:
                trends['medium_term'] = 'bearish'
        
        # Long-term trend (SMA 20 vs SMA 50)
        if indicators.get('sma_20') and indicators.get('sma_50'):
            if indicators['sma_20'] > indicators['sma_50']:
                trends['long_term'] = 'bullish'
            elif indicators['sma_20'] < indicators['sma_50']:
                trends['long_term'] = 'bearish'
        
        return trends
    
    def get_momentum_signals(self) -> Dict:
        """Get momentum-based signals.
        
        Returns:
            Dictionary with momentum signals and conditions
        """
        indicators = self.get_latest_indicators()
        signals = {
            'rsi_signal': 'neutral',
            'macd_signal': 'neutral',
            'stoch_signal': 'neutral',
            'conditions': []
        }
        
        # RSI signals
        rsi = indicators.get('rsi')
        if rsi:
            if rsi < 30:
                signals['rsi_signal'] = 'oversold'
                signals['conditions'].append(f"RSI is oversold ({rsi:.1f})")
            elif rsi > 70:
                signals['rsi_signal'] = 'overbought'
                signals['conditions'].append(f"RSI is overbought ({rsi:.1f})")
        
        # MACD signals
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        if macd and macd_signal:
            if macd > macd_signal:
                signals['macd_signal'] = 'bullish'
            elif macd < macd_signal:
                signals['macd_signal'] = 'bearish'
            
            # Check for crossovers (if we have previous data)
            if len(self.df) >= 2:
                prev = self.df.iloc[-2]
                prev_macd = prev.get('macd')
                prev_signal = prev.get('macd_signal')
                
                if prev_macd and prev_signal:
                    # Bullish crossover
                    if prev_macd <= prev_signal and macd > macd_signal:
                        signals['conditions'].append("MACD bullish crossover detected")
                    # Bearish crossover
                    elif prev_macd >= prev_signal and macd < macd_signal:
                        signals['conditions'].append("MACD bearish crossover detected")
        
        # Stochastic signals
        stoch_k = indicators.get('stoch_k')
        if stoch_k:
            if stoch_k < 20:
                signals['stoch_signal'] = 'oversold'
            elif stoch_k > 80:
                signals['stoch_signal'] = 'overbought'
        
        return signals
    
    def get_volatility_analysis(self) -> Dict:
        """Analyze current volatility conditions.
        
        Returns:
            Dictionary with volatility information
        """
        indicators = self.get_latest_indicators()
        price = indicators['price']
        
        analysis = {
            'bb_position': 'middle',
            'volatility_level': 'normal',
            'conditions': []
        }
        
        # Bollinger Bands position
        bb_upper = indicators.get('bb_upper')
        bb_lower = indicators.get('bb_lower')
        bb_width = indicators.get('bb_width')
        
        if bb_upper and bb_lower:
            if price >= bb_upper:
                analysis['bb_position'] = 'upper'
                analysis['conditions'].append("Price at upper Bollinger Band")
            elif price <= bb_lower:
                analysis['bb_position'] = 'lower'
                analysis['conditions'].append("Price at lower Bollinger Band")
        
        if bb_width:
            # Determine volatility level based on historical bb_width
            median_width = self.df['bb_width'].median()
            if bb_width > median_width * 1.5:
                analysis['volatility_level'] = 'high'
            elif bb_width < median_width * 0.5:
                analysis['volatility_level'] = 'low'
                analysis['conditions'].append("Low volatility - potential breakout ahead")
        
        return analysis


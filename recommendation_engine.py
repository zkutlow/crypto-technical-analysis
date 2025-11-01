"""Recommendation engine for generating trading signals and advice."""

from typing import Dict, List, Tuple
from technical_analysis import TechnicalAnalyzer
from target_calculator import TargetPriceCalculator
from config import Config


class RecommendationEngine:
    """Generates recommendations based on technical analysis."""
    
    def __init__(self, analyzer: TechnicalAnalyzer, symbol: str, holding_value: float):
        """Initialize the recommendation engine.
        
        Args:
            analyzer: TechnicalAnalyzer instance with calculated indicators
            symbol: Cryptocurrency symbol
            holding_value: Current USD value of holdings
        """
        self.analyzer = analyzer
        self.symbol = symbol
        self.holding_value = holding_value
    
    def generate_recommendation(self) -> Dict:
        """Generate a comprehensive recommendation.
        
        Returns:
            Dictionary containing:
                - signal: 'strong_buy', 'buy', 'hold', 'sell', 'strong_sell'
                - score: Numerical score (-100 to +100)
                - confidence: 'low', 'medium', 'high'
                - reasons: List of reasons for the recommendation
                - alerts: List of important alerts
                - summary: Human-readable summary
        """
        indicators = self.analyzer.get_latest_indicators()
        trends = self.analyzer.get_trend_analysis()
        momentum = self.analyzer.get_momentum_signals()
        volatility = self.analyzer.get_volatility_analysis()
        
        score = 0
        reasons = []
        alerts = []
        
        # Trend analysis scoring
        trend_score, trend_reasons = self._analyze_trends(trends)
        score += trend_score
        reasons.extend(trend_reasons)
        
        # Momentum analysis scoring
        momentum_score, momentum_reasons, momentum_alerts = self._analyze_momentum(
            momentum, indicators
        )
        score += momentum_score
        reasons.extend(momentum_reasons)
        alerts.extend(momentum_alerts)
        
        # Volatility analysis scoring
        volatility_score, volatility_reasons, volatility_alerts = self._analyze_volatility(
            volatility, indicators
        )
        score += volatility_score
        reasons.extend(volatility_reasons)
        alerts.extend(volatility_alerts)
        
        # Determine signal based on score
        signal, confidence = self._score_to_signal(score, len(reasons))
        
        # Calculate target prices
        target_calc = TargetPriceCalculator(self.analyzer.df, indicators)
        targets = target_calc.calculate_targets(signal)
        
        # Generate summary
        summary = self._generate_summary(signal, score, trends, momentum, volatility)
        
        return {
            'symbol': self.symbol,
            'signal': signal,
            'score': score,
            'confidence': confidence,
            'reasons': reasons,
            'alerts': alerts,
            'summary': summary,
            'holding_value': self.holding_value,
            'current_price': indicators.get('price'),
            'targets': targets,
            'price_data': self.analyzer.df,  # For charting
            'indicators': indicators,  # For charting
        }
    
    def _analyze_trends(self, trends: Dict) -> Tuple[int, List[str]]:
        """Analyze trends and return score and reasons."""
        score = 0
        reasons = []
        
        # Short-term trend (weight: 10 points)
        if trends['short_term'] == 'bullish':
            score += 10
            reasons.append("✓ Short-term trend is bullish (EMA crossover)")
        elif trends['short_term'] == 'bearish':
            score -= 10
            reasons.append("✗ Short-term trend is bearish (EMA crossover)")
        
        # Medium-term trend (weight: 15 points)
        if trends['medium_term'] == 'bullish':
            score += 15
            reasons.append("✓ Price is above 20-day SMA (medium-term uptrend)")
        elif trends['medium_term'] == 'bearish':
            score -= 15
            reasons.append("✗ Price is below 20-day SMA (medium-term downtrend)")
        
        # Long-term trend (weight: 20 points)
        if trends['long_term'] == 'bullish':
            score += 20
            reasons.append("✓ Long-term trend is bullish (SMA 20 > SMA 50)")
        elif trends['long_term'] == 'bearish':
            score -= 20
            reasons.append("✗ Long-term trend is bearish (SMA 20 < SMA 50)")
        
        return score, reasons
    
    def _analyze_momentum(
        self, 
        momentum: Dict, 
        indicators: Dict
    ) -> Tuple[int, List[str], List[str]]:
        """Analyze momentum and return score, reasons, and alerts."""
        score = 0
        reasons = []
        alerts = []
        
        # RSI analysis (weight: 25 points)
        rsi = indicators.get('rsi')
        if rsi:
            if momentum['rsi_signal'] == 'oversold':
                score += 25
                reasons.append(f"✓ RSI indicates oversold conditions ({rsi:.1f})")
                alerts.append(f"🔔 {self.symbol}: RSI oversold - potential buying opportunity")
            elif momentum['rsi_signal'] == 'overbought':
                score -= 25
                reasons.append(f"✗ RSI indicates overbought conditions ({rsi:.1f})")
                alerts.append(f"⚠️  {self.symbol}: RSI overbought - consider taking profits")
        
        # MACD analysis (weight: 15 points)
        if momentum['macd_signal'] == 'bullish':
            score += 15
            reasons.append("✓ MACD is bullish")
        elif momentum['macd_signal'] == 'bearish':
            score -= 15
            reasons.append("✗ MACD is bearish")
        
        # Add momentum condition alerts
        for condition in momentum['conditions']:
            if 'bullish crossover' in condition.lower():
                alerts.append(f"🚀 {self.symbol}: {condition}")
                score += 10
            elif 'bearish crossover' in condition.lower():
                alerts.append(f"📉 {self.symbol}: {condition}")
                score -= 10
        
        # Stochastic analysis (weight: 10 points)
        if momentum['stoch_signal'] == 'oversold':
            score += 10
        elif momentum['stoch_signal'] == 'overbought':
            score -= 10
        
        return score, reasons, alerts
    
    def _analyze_volatility(
        self, 
        volatility: Dict, 
        indicators: Dict
    ) -> Tuple[int, List[str], List[str]]:
        """Analyze volatility and return score, reasons, and alerts."""
        score = 0
        reasons = []
        alerts = []
        
        # Bollinger Bands position (weight: 15 points)
        if volatility['bb_position'] == 'lower':
            score += 15
            reasons.append("✓ Price at lower Bollinger Band (potential reversal)")
            alerts.append(f"💡 {self.symbol}: Price touching lower Bollinger Band")
        elif volatility['bb_position'] == 'upper':
            score -= 15
            reasons.append("✗ Price at upper Bollinger Band (potential pullback)")
            alerts.append(f"⚠️  {self.symbol}: Price touching upper Bollinger Band")
        
        # Volatility conditions
        for condition in volatility['conditions']:
            if 'low volatility' in condition.lower():
                alerts.append(f"⚡ {self.symbol}: {condition}")
                reasons.append("⚡ Low volatility detected - watch for breakout")
        
        return score, reasons, alerts
    
    def _score_to_signal(self, score: int, reason_count: int) -> Tuple[str, str]:
        """Convert numerical score to trading signal and confidence level.
        
        Args:
            score: Numerical score from -100 to +100
            reason_count: Number of reasons contributing to the score
            
        Returns:
            Tuple of (signal, confidence)
        """
        # Determine confidence based on number of indicators
        if reason_count >= 6:
            confidence = 'high'
        elif reason_count >= 4:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        # Determine signal based on score
        if score >= 50:
            signal = 'strong_buy'
        elif score >= 20:
            signal = 'buy'
        elif score <= -50:
            signal = 'strong_sell'
        elif score <= -20:
            signal = 'sell'
        else:
            signal = 'hold'
        
        return signal, confidence
    
    def _generate_summary(
        self, 
        signal: str, 
        score: int, 
        trends: Dict, 
        momentum: Dict,
        volatility: Dict
    ) -> str:
        """Generate a human-readable summary of the recommendation."""
        signal_text = {
            'strong_buy': '🟢 STRONG BUY',
            'buy': '🟢 BUY',
            'hold': '🟡 HOLD',
            'sell': '🔴 SELL',
            'strong_sell': '🔴 STRONG SELL',
        }
        
        trend_summary = []
        if trends['short_term'] == 'bullish':
            trend_summary.append('short-term uptrend')
        elif trends['short_term'] == 'bearish':
            trend_summary.append('short-term downtrend')
        
        if trends['long_term'] == 'bullish':
            trend_summary.append('long-term uptrend')
        elif trends['long_term'] == 'bearish':
            trend_summary.append('long-term downtrend')
        
        trend_text = ', '.join(trend_summary) if trend_summary else 'neutral trend'
        
        summary = (
            f"{signal_text[signal]} (Score: {score:+d}) - "
            f"{self.symbol} is showing {trend_text}"
        )
        
        if momentum['rsi_signal'] in ['oversold', 'overbought']:
            summary += f" with {momentum['rsi_signal']} RSI"
        
        if volatility['volatility_level'] == 'high':
            summary += ". High volatility - trade with caution"
        elif volatility['volatility_level'] == 'low':
            summary += ". Low volatility - potential breakout coming"
        
        return summary


def prioritize_recommendations(recommendations: List[Dict]) -> List[Dict]:
    """Sort recommendations by priority for user attention.
    
    Args:
        recommendations: List of recommendation dictionaries
        
    Returns:
        Sorted list with highest priority recommendations first
    """
    # Priority scoring
    signal_priority = {
        'strong_buy': 100,
        'strong_sell': 90,
        'buy': 70,
        'sell': 60,
        'hold': 10,
    }
    
    def priority_score(rec):
        score = signal_priority.get(rec['signal'], 0)
        
        # Boost priority based on holding value
        if rec['holding_value'] > 10000:
            score += 20
        elif rec['holding_value'] > 1000:
            score += 10
        
        # Boost priority if there are alerts
        score += len(rec.get('alerts', [])) * 5
        
        # Boost based on confidence
        if rec.get('confidence') == 'high':
            score += 15
        elif rec.get('confidence') == 'medium':
            score += 5
        
        return score
    
    return sorted(recommendations, key=priority_score, reverse=True)


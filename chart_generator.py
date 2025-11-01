"""Chart generation for technical analysis visualization."""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


class ChartGenerator:
    """Generates technical analysis charts."""
    
    def __init__(self, output_dir: str = 'charts'):
        """Initialize chart generator.
        
        Args:
            output_dir: Directory to save charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def generate_technical_chart(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        indicators: dict,
        target_prices: Optional[dict] = None
    ) -> str:
        """Generate comprehensive technical analysis chart.
        
        Args:
            symbol: Cryptocurrency symbol
            price_data: DataFrame with price and indicator data
            indicators: Dictionary of current indicator values
            target_prices: Dictionary with buy_target, sell_target, stop_loss
            
        Returns:
            Path to saved chart file
        """
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.3)
        
        # Main price chart with moving averages and Bollinger Bands
        ax1 = fig.add_subplot(gs[0])
        self._plot_price_and_mas(ax1, symbol, price_data, indicators, target_prices)
        
        # RSI
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        self._plot_rsi(ax2, price_data)
        
        # MACD
        ax3 = fig.add_subplot(gs[2], sharex=ax1)
        self._plot_macd(ax3, price_data)
        
        # Volume
        ax4 = fig.add_subplot(gs[3], sharex=ax1)
        self._plot_volume(ax4, price_data)
        
        # Hide x-axis labels for all but bottom chart
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax3.get_xticklabels(), visible=False)
        
        # Format x-axis
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax4.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save chart
        filename = f"{symbol}_technical_analysis.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def _plot_price_and_mas(self, ax, symbol, df, indicators, target_prices):
        """Plot price with moving averages and Bollinger Bands."""
        # Price line
        ax.plot(df.index, df['price'], label='Price', color='#2962FF', linewidth=2)
        
        # Moving averages
        if 'sma_20' in df.columns:
            ax.plot(df.index, df['sma_20'], label='SMA 20', color='#FF6D00', 
                   linewidth=1.5, alpha=0.8)
        if 'sma_50' in df.columns:
            ax.plot(df.index, df['sma_50'], label='SMA 50', color='#D500F9', 
                   linewidth=1.5, alpha=0.8)
        
        # Bollinger Bands
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            ax.plot(df.index, df['bb_upper'], label='BB Upper', color='gray', 
                   linewidth=1, linestyle='--', alpha=0.5)
            ax.plot(df.index, df['bb_lower'], label='BB Lower', color='gray', 
                   linewidth=1, linestyle='--', alpha=0.5)
            ax.fill_between(df.index, df['bb_upper'], df['bb_lower'], 
                           alpha=0.1, color='gray')
        
        # Target prices
        if target_prices:
            current_price = df['price'].iloc[-1]
            
            if 'buy_target' in target_prices and target_prices['buy_target']:
                ax.axhline(y=target_prices['buy_target'], color='green', 
                          linestyle='--', linewidth=2, label=f"Buy Target: ${target_prices['buy_target']:,.2f}")
            
            if 'sell_target' in target_prices and target_prices['sell_target']:
                ax.axhline(y=target_prices['sell_target'], color='red', 
                          linestyle='--', linewidth=2, label=f"Sell Target: ${target_prices['sell_target']:,.2f}")
            
            if 'stop_loss' in target_prices and target_prices['stop_loss']:
                ax.axhline(y=target_prices['stop_loss'], color='darkred', 
                          linestyle=':', linewidth=2, label=f"Stop Loss: ${target_prices['stop_loss']:,.2f}")
        
        ax.set_title(f'{symbol} Technical Analysis', fontsize=16, fontweight='bold')
        ax.set_ylabel('Price (USD)', fontsize=12)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add current price annotation
        current_price = df['price'].iloc[-1]
        ax.annotate(f'${current_price:,.2f}',
                   xy=(df.index[-1], current_price),
                   xytext=(10, 0), textcoords='offset points',
                   fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
    
    def _plot_rsi(self, ax, df):
        """Plot RSI indicator."""
        if 'rsi' in df.columns:
            ax.plot(df.index, df['rsi'], label='RSI', color='#2962FF', linewidth=2)
            
            # Overbought/oversold lines
            ax.axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.5)
            ax.axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.5)
            ax.fill_between(df.index, 70, 100, alpha=0.1, color='red')
            ax.fill_between(df.index, 0, 30, alpha=0.1, color='green')
            
            ax.set_ylabel('RSI', fontsize=12)
            ax.set_ylim(0, 100)
            ax.legend(loc='upper left', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Add current RSI value
            current_rsi = df['rsi'].iloc[-1]
            if not pd.isna(current_rsi):
                color = 'red' if current_rsi > 70 else 'green' if current_rsi < 30 else 'orange'
                ax.annotate(f'{current_rsi:.1f}',
                           xy=(df.index[-1], current_rsi),
                           xytext=(10, 0), textcoords='offset points',
                           fontsize=10, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.7))
    
    def _plot_macd(self, ax, df):
        """Plot MACD indicator."""
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            ax.plot(df.index, df['macd'], label='MACD', color='#2962FF', linewidth=1.5)
            ax.plot(df.index, df['macd_signal'], label='Signal', color='#FF6D00', linewidth=1.5)
            
            # Histogram
            if 'macd_diff' in df.columns:
                colors = ['green' if x > 0 else 'red' for x in df['macd_diff']]
                ax.bar(df.index, df['macd_diff'], label='Histogram', color=colors, alpha=0.3)
            
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax.set_ylabel('MACD', fontsize=12)
            ax.legend(loc='upper left', fontsize=10)
            ax.grid(True, alpha=0.3)
    
    def _plot_volume(self, ax, df):
        """Plot volume."""
        if 'volume' in df.columns:
            colors = ['green' if df['price'].iloc[i] >= df['price'].iloc[i-1] 
                     else 'red' for i in range(1, len(df))]
            colors.insert(0, 'gray')  # First bar
            
            ax.bar(df.index, df['volume'], color=colors, alpha=0.5)
            ax.set_ylabel('Volume', fontsize=12)
            ax.set_xlabel('Date', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Format y-axis to show abbreviated numbers
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.0f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))


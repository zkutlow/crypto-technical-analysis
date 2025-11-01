"""Market data fetching for cryptocurrency price history."""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from config import Config


class MarketDataProvider:
    """Fetches historical and current market data for cryptocurrencies."""
    
    def __init__(self):
        """Initialize the market data provider."""
        self.coingecko_base = 'https://api.coingecko.com/api/v3'
        self.cache = {}  # Simple cache to avoid repeated API calls
        
    def _symbol_to_coingecko_id(self, symbol: str) -> str:
        """Convert common crypto symbols to CoinGecko IDs.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            
        Returns:
            CoinGecko ID for the cryptocurrency
        """
        # Common mappings
        mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'XRP': 'ripple',
            'USDC': 'usd-coin',
            'ADA': 'cardano',
            'DOGE': 'dogecoin',
            'TRX': 'tron',
            'TON': 'the-open-network',
            'LINK': 'chainlink',
            'MATIC': 'matic-network',
            'DOT': 'polkadot',
            'AVAX': 'avalanche-2',
            'UNI': 'uniswap',
            'ATOM': 'cosmos',
            'XLM': 'stellar',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'ALGO': 'algorand',
        }
        
        symbol_upper = symbol.upper()
        if symbol_upper in mapping:
            return mapping[symbol_upper]
        
        # Try to search for the coin if not in mapping
        return self._search_coin_id(symbol)
    
    def _search_coin_id(self, symbol: str) -> str:
        """Search for a coin ID on CoinGecko.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            CoinGecko ID or the symbol lowercased as fallback
        """
        try:
            url = f"{self.coingecko_base}/search"
            response = requests.get(url, params={'query': symbol}, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('coins'):
                # Return the first match
                return data['coins'][0]['id']
        except Exception as e:
            print(f"Warning: Could not search for {symbol}: {e}")
        
        # Fallback to lowercase symbol
        return symbol.lower()
    
    def get_historical_prices(
        self, 
        symbol: str, 
        days: int = None
    ) -> Optional[pd.DataFrame]:
        """Get historical price data for a cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            days: Number of days of historical data (default from Config)
            
        Returns:
            DataFrame with columns: timestamp, price, volume
            Returns None if data fetch fails
        """
        if days is None:
            days = Config.LOOKBACK_DAYS
        
        cache_key = f"{symbol}_{days}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        coin_id = self._symbol_to_coingecko_id(symbol)
        
        try:
            url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'prices' not in data:
                print(f"Warning: No price data found for {symbol}")
                return None
            
            # Convert to DataFrame
            prices = data['prices']
            volumes = data.get('total_volumes', [[p[0], 0] for p in prices])
            
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['volume'] = [v[1] for v in volumes]
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('timestamp')
            
            # Cache the result
            self.cache[cache_key] = df
            
            time.sleep(Config.REQUEST_DELAY)  # Rate limiting
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get the current price for a cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            Current price in USD or None if fetch fails
        """
        coin_id = self._symbol_to_coingecko_id(symbol)
        
        try:
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get(coin_id, {}).get('usd')
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return None


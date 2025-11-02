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
        self.coincap_base = 'https://api.coincap.io/v2'
        self.binance_base = 'https://api.binance.com/api/v3'
        self.cache = {}  # Simple cache to avoid repeated API calls
        self.failed_providers = set()  # Track which providers are rate limited
        
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
        
        # Try multiple data sources in order
        providers = [
            ('coincap', self._get_historical_from_coincap),
            ('binance', self._get_historical_from_binance),
            ('coingecko', self._get_historical_from_coingecko),
        ]
        
        for provider_name, provider_func in providers:
            if provider_name in self.failed_providers:
                continue
                
            try:
                df = provider_func(symbol, days)
                if df is not None and len(df) > 0:
                    self.cache[cache_key] = df
                    return df
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(f"  Rate limit hit on {provider_name}, trying next provider...")
                    self.failed_providers.add(provider_name)
                    continue
            except Exception as e:
                # Try next provider
                continue
        
        print(f"Error: Could not fetch data for {symbol} from any provider")
        return None
    
    def _get_historical_from_coincap(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """Get historical data from CoinCap API."""
        # CoinCap uses lowercase ids
        coin_id = symbol.lower()
        
        # Special mappings for CoinCap
        coincap_mapping = {
            'xrp': 'ripple',
        }
        coin_id = coincap_mapping.get(coin_id, coin_id)
        
        end_time = int(time.time() * 1000)
        start_time = end_time - (days * 24 * 60 * 60 * 1000)
        
        url = f"{self.coincap_base}/assets/{coin_id}/history"
        params = {
            'interval': 'd1',
            'start': start_time,
            'end': end_time
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'data' not in data or not data['data']:
            return None
        
        # Convert to DataFrame
        records = []
        for point in data['data']:
            records.append({
                'timestamp': pd.to_datetime(point['time'], unit='ms'),
                'price': float(point['priceUsd']),
                'volume': 0  # CoinCap doesn't provide volume in this endpoint
            })
        
        df = pd.DataFrame(records)
        df = df.set_index('timestamp')
        
        time.sleep(0.5)  # Rate limiting
        return df
    
    def _get_historical_from_binance(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """Get historical data from Binance API."""
        # Binance uses USDT pairs
        pair = f"{symbol}USDT"
        
        # Binance klines (candlestick) endpoint
        url = f"{self.binance_base}/klines"
        params = {
            'symbol': pair,
            'interval': '1d',
            'limit': days
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return None
        
        # Convert to DataFrame
        # Binance kline format: [timestamp, open, high, low, close, volume, ...]
        records = []
        for kline in data:
            records.append({
                'timestamp': pd.to_datetime(kline[0], unit='ms'),
                'price': float(kline[4]),  # Close price
                'volume': float(kline[5])
            })
        
        df = pd.DataFrame(records)
        df = df.set_index('timestamp')
        
        time.sleep(0.5)  # Rate limiting
        return df
    
    def _get_historical_from_coingecko(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """Get historical data from CoinGecko API."""
        coin_id = self._symbol_to_coingecko_id(symbol)
        
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
            return None
        
        # Convert to DataFrame
        prices = data['prices']
        volumes = data.get('total_volumes', [[p[0], 0] for p in prices])
        
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['volume'] = [v[1] for v in volumes]
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('timestamp')
        
        time.sleep(2.0)  # Rate limiting - increased delay for CoinGecko free tier
        return df
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get the current price for a cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            Current price in USD or None if fetch fails
        """
        # Try CoinCap first (better rate limits)
        try:
            coin_id = symbol.lower()
            coincap_mapping = {'xrp': 'ripple'}
            coin_id = coincap_mapping.get(coin_id, coin_id)
            
            url = f"{self.coincap_base}/assets/{coin_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and 'priceUsd' in data['data']:
                time.sleep(0.3)
                return float(data['data']['priceUsd'])
        except:
            pass
        
        # Try Binance
        try:
            pair = f"{symbol}USDT"
            url = f"{self.binance_base}/ticker/price"
            params = {'symbol': pair}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'price' in data:
                time.sleep(0.3)
                return float(data['price'])
        except:
            pass
        
        # Fallback to CoinGecko
        try:
            coin_id = self._symbol_to_coingecko_id(symbol)
            
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            time.sleep(1.0)  # Rate limiting
            return data.get(coin_id, {}).get('usd')
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return None


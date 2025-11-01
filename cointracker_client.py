"""CoinTracker API client for fetching portfolio data."""

import requests
import time
from typing import Dict, List, Optional
from config import Config


class CoinTrackerClient:
    """Client for interacting with CoinTracker API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the CoinTracker client.
        
        Args:
            api_key: CoinTracker API key. If not provided, uses Config.
        """
        self.api_key = api_key or Config.COINTRACKER_API_KEY
        self.base_url = Config.COINTRACKER_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, endpoint: str, method: str = 'GET', **kwargs) -> Dict:
        """Make a request to the CoinTracker API.
        
        Args:
            endpoint: API endpoint (e.g., '/portfolio')
            method: HTTP method
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            time.sleep(Config.REQUEST_DELAY)  # Rate limiting
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError(
                    "Invalid CoinTracker API key. Please check your .env file."
                ) from e
            elif response.status_code == 403:
                raise ValueError(
                    "Access forbidden. Please check your API key permissions."
                ) from e
            raise
    
    def get_portfolio(self) -> Dict:
        """Get the current portfolio holdings.
        
        Returns:
            Dictionary containing portfolio data with holdings
        """
        return self._make_request('/portfolio')
    
    def get_holdings(self) -> List[Dict]:
        """Get list of current holdings with amounts and values.
        
        Returns:
            List of holdings, each containing:
                - symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
                - name: Full name of the cryptocurrency
                - amount: Amount held
                - value_usd: Current USD value
                - price_usd: Current price per unit
        """
        portfolio = self.get_portfolio()
        
        # CoinTracker API structure may vary, adapting to common format
        holdings = []
        
        # Try to extract holdings from various possible API response structures
        if 'holdings' in portfolio:
            raw_holdings = portfolio['holdings']
        elif 'data' in portfolio and 'holdings' in portfolio['data']:
            raw_holdings = portfolio['data']['holdings']
        elif 'positions' in portfolio:
            raw_holdings = portfolio['positions']
        else:
            # Fallback: assume the portfolio dict itself contains holdings
            raw_holdings = portfolio.get('currencies', [])
        
        for holding in raw_holdings:
            # Extract data with fallbacks for different API structures
            symbol = holding.get('currency_code') or holding.get('symbol', '')
            amount = float(holding.get('amount', 0) or 0)
            value = float(holding.get('value_usd', 0) or holding.get('value', 0) or 0)
            
            # Skip holdings below minimum threshold or with zero amount
            if amount <= 0 or value < Config.MIN_PORTFOLIO_VALUE:
                continue
            
            holdings.append({
                'symbol': symbol.upper(),
                'name': holding.get('name', symbol),
                'amount': amount,
                'value_usd': value,
                'price_usd': value / amount if amount > 0 else 0
            })
        
        return holdings
    
    def get_account_info(self) -> Dict:
        """Get account information.
        
        Returns:
            Dictionary containing account details
        """
        return self._make_request('/account')


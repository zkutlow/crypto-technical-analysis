"""Coinbase API client for fetching portfolio data."""

import requests
import time
import hmac
import hashlib
import base64
from typing import Dict, List, Optional
from config import Config


class CoinbaseClient:
    """Client for interacting with Coinbase API."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize the Coinbase client.
        
        Args:
            api_key: Coinbase API key. If not provided, uses Config.
            api_secret: Coinbase API secret. If not provided, uses Config.
        """
        self.api_key = api_key or Config.COINBASE_API_KEY
        self.api_secret = api_secret or Config.COINBASE_API_SECRET
        self.base_url = Config.COINBASE_BASE_URL
        self.session = requests.Session()
    
    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = '') -> str:
        """Generate CB-ACCESS-SIGN header for authentication.
        
        Args:
            timestamp: Unix timestamp as string
            method: HTTP method (GET, POST, etc.)
            path: Request path
            body: Request body (empty for GET)
            
        Returns:
            Base64-encoded signature
        """
        message = timestamp + method + path + body
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        return base64.b64encode(signature.digest()).decode()
    
    def _make_request(self, endpoint: str, method: str = 'GET', **kwargs) -> Dict:
        """Make a request to the Coinbase API.
        
        Args:
            endpoint: API endpoint (e.g., '/accounts')
            method: HTTP method
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(time.time()))
        
        # Generate signature for authentication
        signature = self._generate_signature(timestamp, method, endpoint)
        
        headers = {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            time.sleep(Config.REQUEST_DELAY)  # Rate limiting
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError(
                    "Invalid Coinbase API credentials. Please check your .env file."
                ) from e
            elif response.status_code == 403:
                raise ValueError(
                    "Access forbidden. Please check your API key permissions."
                ) from e
            raise
    
    def get_accounts(self) -> List[Dict]:
        """Get all Coinbase accounts.
        
        Returns:
            List of account dictionaries
        """
        response = self._make_request('/v2/accounts')
        return response.get('data', [])
    
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
        accounts = self.get_accounts()
        holdings = []
        
        for account in accounts:
            # Extract balance information
            balance = account.get('balance', {})
            amount = float(balance.get('amount', 0))
            currency = account.get('currency', {})
            
            if isinstance(currency, dict):
                symbol = currency.get('code', '')
                name = currency.get('name', symbol)
            else:
                symbol = currency
                name = symbol
            
            # Skip zero balances and USD/fiat currencies
            if amount <= 0 or symbol in ['USD', 'EUR', 'GBP', 'CAD']:
                continue
            
            # Get native balance (value in user's native currency, usually USD)
            native_balance = account.get('native_balance', {})
            value_usd = float(native_balance.get('amount', 0))
            
            # Skip holdings below minimum threshold
            if value_usd < Config.MIN_PORTFOLIO_VALUE:
                continue
            
            holdings.append({
                'symbol': symbol.upper(),
                'name': name,
                'amount': amount,
                'value_usd': value_usd,
                'price_usd': value_usd / amount if amount > 0 else 0
            })
        
        return holdings
    
    def get_account_info(self) -> Dict:
        """Get user account information.
        
        Returns:
            Dictionary containing account details
        """
        return self._make_request('/v2/user')


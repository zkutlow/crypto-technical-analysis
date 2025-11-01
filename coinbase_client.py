"""Coinbase API client for fetching portfolio data."""

import requests
import time
import jwt
import json
from typing import Dict, List, Optional
from pathlib import Path
from config import Config


class CoinbaseClient:
    """Client for interacting with Coinbase CDP API."""
    
    def __init__(self, api_key_name: Optional[str] = None, private_key: Optional[str] = None):
        """Initialize the Coinbase client.
        
        Args:
            api_key_name: Coinbase CDP API key name. If not provided, uses Config.
            private_key: Coinbase CDP private key. If not provided, uses Config.
        """
        self.api_key_name = api_key_name or Config.COINBASE_API_KEY_NAME
        self.private_key = private_key or Config.COINBASE_PRIVATE_KEY
        self.base_url = 'https://api.coinbase.com'
        self.session = requests.Session()
    
    def _generate_jwt_token(self, request_method: str, request_path: str) -> str:
        """Generate JWT token for CDP API authentication.
        
        Args:
            request_method: HTTP method (GET, POST, etc.)
            request_path: Request path
            
        Returns:
            JWT token string
        """
        # Extract key name from the full path
        key_name = self.api_key_name.split('/')[-1]
        
        uri = f"{request_method} {request_path}"
        
        claims = {
            "sub": self.api_key_name,
            "iss": "coinbase-cloud",
            "nbf": int(time.time()),
            "exp": int(time.time()) + 120,  # Token expires in 2 minutes
            "uri": uri,
        }
        
        token = jwt.encode(claims, self.private_key, algorithm="ES256", headers={"kid": key_name, "nonce": str(int(time.time()))})
        return token
    
    def _make_request(self, endpoint: str, method: str = 'GET', **kwargs) -> Dict:
        """Make a request to the Coinbase CDP API.
        
        Args:
            endpoint: API endpoint (e.g., '/api/v3/brokerage/accounts')
            method: HTTP method
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        # Generate JWT token for authentication
        jwt_token = self._generate_jwt_token(method, endpoint)
        
        headers = {
            'Authorization': f'Bearer {jwt_token}',
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
                    "Invalid Coinbase API credentials. Please check your API key file."
                ) from e
            elif response.status_code == 403:
                raise ValueError(
                    "Access forbidden. Please check your API key permissions."
                ) from e
            raise
    
    def get_accounts(self) -> List[Dict]:
        """Get all Coinbase brokerage accounts.
        
        Returns:
            List of account dictionaries
        """
        response = self._make_request('/api/v3/brokerage/accounts')
        return response.get('accounts', [])
    
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
            # Extract balance information from CDP API v3 format
            symbol = account.get('currency', '')
            name = account.get('name', symbol)
            
            # Get available balance
            available_balance = account.get('available_balance', {})
            amount = float(available_balance.get('value', 0))
            
            # Skip zero balances and USD/fiat currencies
            if amount <= 0 or symbol in ['USD', 'EUR', 'GBP', 'CAD', 'USDC', 'USDT']:
                continue
            
            # Get current price for the asset to calculate USD value
            try:
                spot_price = self.get_spot_price(symbol)
                value_usd = amount * spot_price
            except Exception as e:
                print(f"Warning: Could not get price for {symbol}: {e}")
                # Try to use available balance if it exists
                value_usd = 0
            
            # Skip holdings below minimum threshold
            if value_usd < Config.MIN_PORTFOLIO_VALUE:
                continue
            
            holdings.append({
                'symbol': symbol.upper(),
                'name': name,
                'amount': amount,
                'value_usd': value_usd,
                'price_usd': spot_price if value_usd > 0 else 0
            })
        
        return holdings
    
    def get_spot_price(self, currency: str, base_currency: str = 'USD') -> float:
        """Get the current spot price for a currency pair.
        
        Args:
            currency: The cryptocurrency (e.g., 'BTC')
            base_currency: The base currency (default: 'USD')
            
        Returns:
            Current spot price as float
        """
        product_id = f"{currency}-{base_currency}"
        endpoint = f"/api/v3/brokerage/products/{product_id}"
        
        try:
            response = self._make_request(endpoint)
            price = response.get('price', 0)
            return float(price) if price else 0
        except Exception:
            # Fallback: try without authentication (public endpoint)
            url = f"{self.base_url}{endpoint}"
            try:
                resp = requests.get(url, timeout=10)
                data = resp.json()
                price = data.get('price', 0)
                return float(price) if price else 0
            except Exception:
                return 0
    
    def get_account_info(self) -> Dict:
        """Get user account information.
        
        Returns:
            Dictionary containing account details
        """
        return self._make_request('/api/v3/brokerage/accounts')


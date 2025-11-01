"""Configuration management for the crypto technical analysis app."""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # Coinbase CDP API - Load from JSON file
    COINBASE_API_KEY_FILE = os.getenv('COINBASE_API_KEY_FILE', '')
    COINBASE_API_KEY_NAME = ''
    COINBASE_PRIVATE_KEY = ''
    
    # Load API credentials from JSON file if specified
    if COINBASE_API_KEY_FILE and Path(COINBASE_API_KEY_FILE).exists():
        try:
            with open(COINBASE_API_KEY_FILE, 'r') as f:
                api_data = json.load(f)
                COINBASE_API_KEY_NAME = api_data.get('name', '')
                COINBASE_PRIVATE_KEY = api_data.get('privateKey', '')
        except Exception as e:
            print(f"Warning: Could not load API key file: {e}")
    
    COINBASE_BASE_URL = 'https://api.coinbase.com'
    
    # Technical Analysis Thresholds
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
    
    # Portfolio filters
    MIN_PORTFOLIO_VALUE = float(os.getenv('MIN_PORTFOLIO_VALUE', '100'))
    
    # Data settings
    LOOKBACK_DAYS = 90  # Days of historical data for technical analysis
    
    # API rate limiting
    REQUEST_DELAY = 0.5  # Seconds between API requests
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.COINBASE_API_KEY_FILE:
            raise ValueError(
                "COINBASE_API_KEY_FILE not set. Please create a .env file "
                "and specify the path to your Coinbase CDP API key JSON file. "
                "See env.template for reference."
            )
        if not cls.COINBASE_API_KEY_NAME:
            raise ValueError(
                "Could not load API key name from JSON file. "
                "Please check that your COINBASE_API_KEY_FILE path is correct "
                "and the JSON file contains a 'name' field."
            )
        if not cls.COINBASE_PRIVATE_KEY:
            raise ValueError(
                "Could not load private key from JSON file. "
                "Please check that your COINBASE_API_KEY_FILE path is correct "
                "and the JSON file contains a 'privateKey' field."
            )
        return True


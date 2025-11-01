"""Configuration management for the crypto technical analysis app."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # Coinbase API
    COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', '')
    COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET', '')
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
        if not cls.COINBASE_API_KEY:
            raise ValueError(
                "COINBASE_API_KEY not set. Please create a .env file "
                "with your API key and secret. See env.template for reference."
            )
        if not cls.COINBASE_API_SECRET:
            raise ValueError(
                "COINBASE_API_SECRET not set. Please create a .env file "
                "with your API key and secret. See env.template for reference."
            )
        return True


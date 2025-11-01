"""Configuration management for the crypto technical analysis app."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # CoinTracker API
    COINTRACKER_API_KEY = os.getenv('COINTRACKER_API_KEY', '')
    COINTRACKER_BASE_URL = 'https://api.cointracker.io/api/v2'
    
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
        if not cls.COINTRACKER_API_KEY:
            raise ValueError(
                "COINTRACKER_API_KEY not set. Please create a .env file "
                "with your API key. See .env.example for reference."
            )
        return True


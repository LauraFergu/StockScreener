"""
Configuration settings for Stock Screener
"""

import os
from typing import Optional

class Config:
    # API Configuration
    ALPHA_VANTAGE_API_KEY: str = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
    API_BASE_URL: str = "https://www.alphavantage.co/query"
    
    # Request Configuration
    REQUEST_TIMEOUT: int = 30
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: float = 1.0
    
    # Default Stock Symbols
    DEFAULT_SYMBOLS: list = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
    
    # Output Configuration
    MAX_NAME_LENGTH: int = 19
    
    @classmethod
    def get_api_key(cls) -> str:
        """Get API key with fallback to demo"""
        return cls.ALPHA_VANTAGE_API_KEY
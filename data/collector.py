import os
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()

class MarketDataCollector:
    def __init__(self):
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.base_url = os.getenv('ALPACA_BASE_URL')
        
        self.api = tradeapi.REST(
            self.api_key, 
            self.secret_key, 
            self.base_url, 
            api_version='v2'
        )

    def get_price_data(self, symbol, timeframe='1Day', limit=100):
        """
        Fetches historical price data for a given symbol.
        """
        start = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')
        try:
            bars = self.api.get_bars(symbol, timeframe, start=start, limit=limit).df
            return bars
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def get_crypto_data(self, symbol, timeframe='1Day', limit=100):
        """
        Fetches historical crypto data for a given symbol.
        """
        # Ensure symbol is in BTC/USD format if passed as BTCUSD
        if "/" not in symbol and symbol.upper().endswith("USD"):
             symbol = f"{symbol[:-3]}/{symbol[-3:]}"
        
        start = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')
        try:
            bars = self.api.get_crypto_bars(symbol, timeframe, start=start, limit=limit).df
            return bars
        except Exception as e:
            print(f"Error fetching crypto data for {symbol}: {e}")
            return None


from .collector import MarketDataCollector
from .technicals import TechnicalAnalyzer

class DataOrchestrator:
    def __init__(self):
        self.collector = MarketDataCollector()
        self.analyzer = TechnicalAnalyzer()

    def get_enriched_data(self, symbol, asset_type='stock', timeframe='1Day', limit=100):
        """
        Fetches data, calculates technicals, and returns a combined dataframe.
        """
        if asset_type == 'crypto':
            df = self.collector.get_crypto_data(symbol, timeframe, limit)
        else:
            df = self.collector.get_price_data(symbol, timeframe, limit)
            
        if df is not None and not df.empty:
            df = self.analyzer.add_sma(df, period=20)
            df = self.analyzer.add_rsi(df, period=14)
            df = self.analyzer.add_macd(df)
            return df
        return None


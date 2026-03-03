import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from utils.logger import logger
from agents.orchestrator import AgentOrchestrator

load_dotenv()

class NewsListener:
    def __init__(self):
        self.fmp_key = os.getenv('FMP_API_KEY')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        self.agents = AgentOrchestrator()
        self.seen_news = set()

    def fetch_finnhub_news(self, symbol: str):
        """Fetches latest news for a symbol from Finnhub (FREE)."""
        if not self.finnhub_key:
            return []
        
        # Finnhub uses date ranges
        end = datetime.now().strftime('%Y-%m-%d')
        start = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={start}&to={end}&token={self.finnhub_key}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Error fetching Finnhub news for {symbol}: {e}")
            return []

    def fetch_cryptopanic_news(self, symbol: str):
        """Fetches news from CryptoPanic (FREE/Public)."""
        # CryptoPanic often uses currency codes like BTC, ETH
        clean_symbol = symbol.split("/")[0] if "/" in symbol else symbol
        url = f"https://cryptopanic.com/api/v1/posts/?auth_token=PUBLIC&currencies={clean_symbol}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get('results', [])
            return []
        except:
            return []

    def fetch_latest_news(self, symbol: str, asset_type: str = 'stock'):
        """Aggregates news from available free sources."""
        all_news = []
        
        if asset_type == 'crypto':
            all_news.extend(self.fetch_cryptopanic_news(symbol))
        else:
            # Try Finnhub for stocks
            all_news.extend(self.fetch_finnhub_news(symbol))
            
        return all_news

    def analyze_and_trigger(self, symbol: str, asset_type: str = 'stock'):
        """Polls news and triggers a debate if 'interesting' news is found."""
        news_items = self.fetch_latest_news(symbol, asset_type)
        
        for item in news_items:
            # Unique ID varies by source
            news_id = item.get('url') or item.get('id')
            if news_id in self.seen_news:
                continue
            
            self.seen_news.add(news_id)
            title = item.get('headline') or item.get('title')
            
            logger.info(f"Breaking News [{asset_type}] for {symbol}: {title}")
            return True # Trigger debate
        
        return False


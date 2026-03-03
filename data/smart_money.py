import os
import requests
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

class SmartMoneyTracker:
    """
    Tracks movements of professional and institutional traders using Financial Modeling Prep (FMP).
    Focuses on free/accessible endpoints for deep integration.
    """

    def __init__(self):
        self.fmp_api_key = os.getenv('FMP_API_KEY')
        self.fmp_base = "https://financialmodelingprep.com/api/v3"

    def get_key_metrics(self, symbol: str) -> dict:
        """
        Fetches key financial metrics which can give 'Smart Money' confidence.
        """
        if not self.fmp_api_key:
            return {"confidence_boost": 0.0}

        url = f"{self.fmp_base}/key-metrics-ttm/{symbol}?apikey={self.fmp_api_key}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if not data: return {"confidence_boost": 0.0}

            metrics = data[0]
            # Example: High ROIC often indicates quality institutional-grade asset
            roic = metrics.get('roicTTM', 0)
            boost = min(0.10, max(0, roic * 0.1))
            return {"confidence_boost": boost}
        except:
            return {"confidence_boost": 0.0}

    def get_analyst_ratings(self, symbol: str) -> dict:
        """
        Fetches analyst stock recommendations (consensus).
        """
        if not self.fmp_api_key:
            return {"confidence_boost": 0.0, "consensus": "Neutral"}

        url = f"{self.fmp_base}/analyst-stock-recommendations/{symbol}?limit=1&apikey={self.fmp_api_key}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if not data:
                return {"confidence_boost": 0.0, "consensus": "Neutral"}

            rec = data[0]
            buy_score = rec.get("analystRatingsbuy", 0) + rec.get("analystRatingsstrongBuy", 0)
            sell_score = rec.get("analystRatingssell", 0) + rec.get("analystRatingsstrongSell", 0)
            
            boost = 0.0
            consensus = "Neutral"
            if buy_score > sell_score:
                boost = 0.10
                consensus = "Buy"
            elif sell_score > buy_score:
                boost = -0.05
                consensus = "Sell"

            logger.info(f"[FMP-Analyst] {symbol}: Consensus {consensus}")
            return {"confidence_boost": boost, "consensus": consensus}
        except Exception as e:
            logger.error(f"FMP analyst error for {symbol}: {e}")
            return {"confidence_boost": 0.0, "consensus": "Neutral"}

    def get_institutional_holdings_free_check(self, symbol: str) -> dict:
        """
        Checks if institutional holdings data is accessible (often 403 on free).
        If 403, falls back to metrics.
        """
        url = f"{self.fmp_base}/institutional-holder/{symbol}?apikey={self.fmp_api_key}"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 403:
                return None
            resp.raise_for_status()
            data = resp.json()
            return data
        except:
            return None

    def get_fear_greed(self) -> float:
        """
        Fetches the Fear & Greed Index (Crypto focus but applicable to general sentiment).
        Returns a confidence boost based on extreme fear (buying opportunity) or greed (risk).
        """
        try:
            url = "https://api.alternative.me/fng/"
            resp = requests.get(url, timeout=5).json()
            val = int(resp['data'][0]['value'])
            
            # Counter-cyclical logic: Extreme Fear (+ boost), Extreme Greed (- boost)
            if val < 20: return 0.15 # Extreme Fear
            if val < 40: return 0.05 # Fear
            if val > 80: return -0.10 # Extreme Greed
            if val > 60: return -0.05 # Greed
            return 0.0
        except:
            return 0.0

    def get_pro_trader_sentiment(self, symbol: str, asset_type: str = "stock") -> float:
        """
        Aggregated confidence boost from deep FMP signals and global sentiment.
        """
        total = 0.0
        clean_symbol = symbol.split("/")[0] if "/" in symbol else symbol

        # 1. Global Sentiment Boost (Fear & Greed)
        total += self.get_fear_greed()

        # 2. Fundamental Quality (Regular stocks)
        analysts = self.get_analyst_ratings(clean_symbol)
        total += analysts.get("confidence_boost", 0)

        metrics = self.get_key_metrics(clean_symbol)
        total += metrics.get("confidence_boost", 0)

        # 3. Institutional Proxy (Handle 403 gracefully)
        holdings = self.get_institutional_holdings_free_check(clean_symbol)
        if holdings:
            num_holders = len(holdings)
            total += min(0.10, num_holders * 0.002)

        logger.info(f"Final Smart Money aggregation for {symbol}: {total:+.3f}")
        return total

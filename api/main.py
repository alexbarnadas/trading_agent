from fastapi import FastAPI, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
import requests
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from data.news_listener import NewsListener
from data.smart_money import SmartMoneyTracker
from utils.logger import logger
from agents.state import state_manager
from agents.orchestrator import AgentOrchestrator

load_dotenv()

app = FastAPI(title="Trading Bot Dashboard API")
listener = NewsListener()
smart_money = SmartMoneyTracker()

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Alpaca API
api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_SECRET_KEY'),
    os.getenv('ALPACA_BASE_URL'),
    api_version='v2'
)

async def news_monitor_loop():
    """Background loop to check news periodically for target symbols."""
    logger.info("News monitor loop started.")
    while True:
        settings = state_manager.settings
        autonomous = settings.get("autonomous_trading", False)
        symbols = settings.get("watchlist", [])
        for symbol in symbols:
            asset_type = 'crypto' if '/' in symbol else 'stock'
            if listener.analyze_and_trigger(symbol, asset_type):
                logger.info(f"News signal for {symbol}. Triggering AI debate...")
                
                # Enrich summary for the Strategist
                latest_price = 150.0 # Default mock
                try:
                    latest_price = api.get_latest_trade(symbol).price if asset_type == 'stock' else api.get_latest_crypto_trade(symbol).price
                except Exception as e:
                    logger.warning(f"Could not get latest price for {symbol}: {e}")

                summary = {
                    "symbol": symbol,
                    "event": "Breaking News", 
                    "type": asset_type,
                    "latest_price": latest_price,
                    "sentiment": 0.82
                }
                
                orchestrator = AgentOrchestrator()
                proposal = orchestrator.run_debate(symbol, summary)
                
                # If autonomous and approved, execute!
                if autonomous and proposal['signal'] != 'HOLD':
                    logger.info(f"AUTONOMOUS MODE: Executing {proposal['signal']} for {symbol}")
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(news_monitor_loop())

@app.get("/")
async def root():
    return {"status": "online", "message": "Trading Bot API is running"}

@app.get("/status")
async def get_status():
    try:
        account = api.get_account()
        return {
            "alpaca_connected": True,
            "equity": account.equity,
            "buying_power": account.buying_power,
            "market_status": "open" if api.get_clock().is_open else "closed"
        }
    except Exception as e:
        return {"alpaca_connected": False, "error": str(e)}

@app.get("/candidates")
async def get_candidates():
    """Returns tickers currently under evaluation."""
    return state_manager.get_all_candidates()

@app.get("/news")
async def get_news():
    """Aggregates news headlines from all watchlist symbols."""
    settings = state_manager.settings
    symbols = settings.get("watchlist", [])
    all_news = []

    for symbol in symbols:
        asset_type = 'crypto' if '/' in symbol else 'stock'
        try:
            items = listener.fetch_latest_news(symbol, asset_type)
            for item in items[:5]:  # Limit per symbol
                headline = item.get('headline') or item.get('title') or ''
                source = item.get('source') or item.get('domain') or 'Unknown'
                url = item.get('url') or ''
                timestamp = item.get('datetime') or item.get('published_at') or item.get('created_at') or ''
                summary = item.get('summary') or item.get('body') or ''

                all_news.append({
                    "symbol": symbol,
                    "headline": headline,
                    "source": source,
                    "url": url,
                    "timestamp": timestamp,
                    "summary": summary[:200] if summary else ''
                })
        except Exception as e:
            logger.warning(f"Error fetching news for {symbol}: {e}")

    # Sort by timestamp descending (newest first), handle mixed types
    all_news.sort(key=lambda x: str(x.get('timestamp', '')), reverse=True)
    return all_news[:30]  # Cap at 30 items total

@app.get("/market-sentiment")
async def get_market_sentiment():
    """Returns Fear & Greed Index and analyst sentiment data."""
    try:
        fng_url = "https://api.alternative.me/fng/?limit=1"
        resp = requests.get(fng_url, timeout=5)
        fng_data = resp.json()
        value = int(fng_data['data'][0]['value'])
        classification = fng_data['data'][0]['value_classification']
    except Exception:
        value = 50
        classification = "Neutral"

    return {
        "fear_greed_value": value,
        "fear_greed_label": classification,
    }

@app.get("/settings")
async def get_settings():
    return state_manager.settings

@app.patch("/settings")
async def update_settings(settings: dict = Body(...)):
    state_manager.save_settings(settings)
    return {"status": "success", "settings": state_manager.settings}

@app.get("/positions")
async def get_positions():
    """Returns current paper positions."""
    try:
        positions = api.list_positions()
        return [
            {
                "symbol": p.symbol,
                "qty": p.qty,
                "market_value": p.market_value,
                "unrealized_pl": p.unrealized_pl
            } for p in positions
        ]
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

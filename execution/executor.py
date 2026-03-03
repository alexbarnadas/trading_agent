import os
import alpaca_trade_api as tradeapi
from utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

class ExecutionAgent:
    def __init__(self):
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY'),
            os.getenv('ALPACA_SECRET_KEY'),
            os.getenv('ALPACA_BASE_URL'),
            api_version='v2'
        )

    def execute_trade(self, symbol, side, qty, type='market'):
        """
        Executes a trade on Alpaca.
        """
        try:
            logger.info(f"EXECUTING ORDER: {side} {qty} shares of {symbol}")
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                time_in_force='gtc'
            )
            logger.info(f"Order submitted successfully. ID: {order.id}")
            return order
        except Exception as e:
            logger.error(f"Execution Failed: {e}")
            return None

    def get_account_info(self):
        return self.api.get_account()

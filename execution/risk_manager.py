from utils.logger import logger

class RiskManager:
    def __init__(self, max_portfolio_risk=0.02, max_position_size=0.10):
        """
        :param max_portfolio_risk: Max % of portfolio to risk on a single day (Drawdown limit).
        :param max_position_size: Max % of total equity for any single position.
        """
        self.max_portfolio_risk = max_portfolio_risk
        self.max_position_size = max_position_size

    def validate_trade(self, proposal, account_info):
        """
        Strict deterministic checks. AI cannot override these.
        """
        equity = float(account_info.equity)
        buying_power = float(account_info.buying_power)
        
        logger.info(f"Risk Check: Evaluating proposal for {proposal['symbol']}...")

        # 1. Position Size Check
        suggested_size = equity * self.max_position_size
        if suggested_size > buying_power:
            logger.warning("Risk Check: Insufficient buying power for standard position size.")
            suggested_size = buying_power * 0.95 # Use 95% of BP as last resort

        # 2. Daily Drawdown Check (Dummy check for now, needs PnL tracking)
        # if Todays_Loss > equity * self.max_portfolio_risk:
        #    return False, "Daily Max Drawdown reached."

        # 3. Stop Loss sanity check
        entry_price = proposal['latest_price']
        stop_loss = proposal['stop_loss']
        risk_per_share = abs(entry_price - stop_loss)
        risk_percent = risk_per_share / entry_price
        
        if risk_percent > 0.05: # Reject if stop loss is more than 5% away (too volatile)
            return False, f"Risk Check: Stop loss too wide ({risk_percent*100:.2f}%)"

        proposal['risk_validated_size'] = suggested_size
        return True, "Trade approved by Risk Manager"

    def calculate_shares(self, entry_price, allocated_funds, is_crypto=False):
        """
        Calculates number of shares based on allocated budget.
        Supports fractional shares for crypto.
        """
        if is_crypto:
            return round(allocated_funds / entry_price, 6)
        return int(allocated_funds / entry_price)

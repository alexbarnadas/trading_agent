import sys
from data.orchestrator import DataOrchestrator
from data.smart_money import SmartMoneyTracker
from agents.orchestrator import AgentOrchestrator
from execution.risk_manager import RiskManager
from execution.executor import ExecutionAgent
from utils.logger import logger

def run_daily_pipeline(symbol, asset_type='stock'):
    logger.info(f"--- Starting Daily Pipeline for {symbol} ---")
    
    # 1. DATA INGESTION
    orchestrator = DataOrchestrator()
    market_data = orchestrator.get_enriched_data(symbol, asset_type=asset_type, limit=50)
    
    if market_data is None or market_data.empty:
        logger.error(f"Failed to fetch market data for {symbol}")
        return

    latest_close = market_data['close'].iloc[-1]
    logger.info(f"Latest Close Price: {latest_close}")
    
    sm_tracker = SmartMoneyTracker()
    sm_bias = sm_tracker.get_pro_trader_sentiment(symbol, asset_type=asset_type)
    logger.info(f"Smart Money Confidence Boost: +{sm_bias:.2f}")
    
    # 2. META-STRATEGY (LLM DEBATE)
    market_summary = {
        'symbol': symbol,
        'latest_price': latest_close,
        'sm_bias': sm_bias,
        'technicals': market_data.iloc[-1].to_dict()
    }
    
    agents = AgentOrchestrator()
    decision = agents.run_debate(symbol, market_summary)
    
    if decision['signal'] == 'HOLD':
        logger.info("Decision is HOLD. No further action.")
        return

    # 3. RISK MANAGEMENT
    executor = ExecutionAgent()
    account = executor.get_account_info()
    
    risker = RiskManager()
    # Add latest price and stop loss to decision for risk validation
    decision['latest_price'] = latest_close
    
    approved, message = risker.validate_trade(decision, account)
    logger.info(f"Risk Evaluation: {message}")

    if not approved:
        logger.warning("Trade rejected by Risk Manager. Aborting.")
        return

    # 4. EXECUTION
    is_crypto = (asset_type == 'crypto')
    qty = risker.calculate_shares(latest_close, decision['risk_validated_size'], is_crypto=is_crypto)
    if qty > 0:
        logger.info(f"Safety checks passed. Proceeding with {decision['signal']} of {qty} shares.")
        # executor.execute_trade(symbol, decision['signal'].lower(), qty) # UNCOMMENT TO GO LIVE (PAPER)
        logger.info("[SIMULATION] Order would be placed here.")
    else:
        logger.warning("Calculated quantity is 0. Check funds/price.")

    logger.info(f"--- Pipeline Finished for {symbol} ---")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_symbol = sys.argv[1]
        target_type = sys.argv[2] if len(sys.argv) > 2 else 'stock'
    else:
        target_symbol = "BTC/USD"
        target_type = "crypto"
        
    run_daily_pipeline(target_symbol, target_type)

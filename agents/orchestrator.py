from .strategist import MasterStrategist
from .critic import ExecutionCritic
from utils.logger import logger
from .state import state_manager

class AgentOrchestrator:
    def __init__(self):
        self.strategist = MasterStrategist()
        self.critic = ExecutionCritic()

    def run_debate(self, symbol, market_summary):
        """
        Coordinates the debate and updates the global state for the frontend.
        """
        logger.info(f"Starting Meta-Strategy debate for {symbol}...")
        
        # Update state to 'debating'
        state_manager.update_candidate(symbol, {
            "status": "debating",
            "reason": "Technical/Fundamental shift detected",
            "market_summary": market_summary,
            "insights": "AI Agents are debating the entry point..."
        })

        # 1. Get initial proposal
        proposal = self.strategist.generate_proposal(market_summary)
        logger.info(f"Strategist Proposal: {proposal['signal']} at confidence {proposal['confidence']}")
        
        if proposal['signal'] == 'HOLD':
            logger.info("Strategist recommends HOLD. Ending debate.")
            state_manager.update_candidate(symbol, {
                "status": "rejected",
                "reason": "Strategist recommends HOLD",
                "insights": "No clear trend or opportunity identified by the strategist."
            })
            return proposal
            
        # 2. Critic challenges
        critique = self.critic.challenge_proposal(proposal, market_summary)
        logger.info(f"Critic valid check: {critique['is_valid']}")
        
        # 3. Finalize
        if not critique['is_valid']:
            logger.warning(f"Critic REJECTED proposal: {critique['objections']}")
            proposal['signal'] = 'HOLD'
            state_manager.update_candidate(symbol, {
                "status": "rejected",
                "reason": critique['objections'],
                "insights": "Critic found insufficient momentum or high risk."
            })
        else:
            proposal['confidence'] = critique['revised_confidence']
            proposal['critic_feedback'] = critique['objections']
            state_manager.update_candidate(symbol, {
                "status": "approved",
                "reason": f"Strategist and Critic agree on {proposal['signal']}",
                "confidence": proposal['confidence'],
                "insights": f"Ready to invest. Rationale: {proposal['rationale']}. Critic note: {critique['objections']}"
            })
            logger.info(f"Debate finalized. Consenus Signal: {proposal['signal']} ({proposal['confidence']})")

        return proposal

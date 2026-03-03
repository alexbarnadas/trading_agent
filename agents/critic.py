class ExecutionCritic:
    def __init__(self, model="gpt-4o"):
        self.model = model
        self.system_prompt = """
        You are a Professional Execution Critic. Your goal is to find reasons NOT to take a proposed trade.
        Your skepticism protects the portfolio from high-risk or hallucinated strategies.
        
        Identify:
        - Overbought/Oversold traps.
        - Lack of volume confirmation.
        - Contradictory macro-economic signals.
        - Unrealistic target/stop-loss distances.
        """

    def challenge_proposal(self, proposal, market_summary):
        """
        Skeleton for challenging a trade proposal.
        """
        # In a real implementation, this would call the LLM API.
        # For the prototype, we mimic the logic.
        return {
            "is_valid": True,
            "objections": ["Volume is slightly decreasing on 1h, but macro trend supports the move."],
            "revised_confidence": 0.80
        }

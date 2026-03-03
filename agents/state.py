import json
import os

class StateManager:
    def __init__(self):
        self.candidates = {} # symbol -> {indicators, news, rationale, score}
        self.settings_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.json")
        self.settings = self._load_settings()

    def _load_settings(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r') as f:
                return json.load(f)
        return {
            "risk_aggression": 1.0,
            "sentiment_threshold": 0.7,
            "watchlist": ["AAPL", "BTC/USD", "TSLA", "SOL/USD"],
            "autonomous_mode": False,
            "live_trading": False
        }

    def save_settings(self, new_settings):
        self.settings.update(new_settings)
        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
        with open(self.settings_path, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def update_candidate(self, symbol, data):
        self.candidates[symbol] = data

    def get_candidate(self, symbol):
        return self.candidates.get(symbol)

    def get_all_candidates(self):
        return self.candidates

state_manager = StateManager()

class ChemicalOptimizer:
    def __init__(self, trend_rate=0.0005, error_threshold=0.5):
        self.trend_rate = trend_rate
        self.error_threshold = error_threshold
        self.reward_history = []

    def compute_prediction_error(self, expected_reward, actual_reward):
        return actual_reward - expected_reward

    def update_trend(self, actual_reward):
        self.reward_history.append(actual_reward)
        if len(self.reward_history) > 100:
            self.reward_history.pop(0)

    def get_reward_trend(self):
        if not self.reward_history:
            return 0
        return sum(self.reward_history) / len(self.reward_history)

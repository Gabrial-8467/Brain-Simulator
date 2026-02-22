class DecisionEngine:
    def __init__(self, decision_config: dict, deterministic=False):
        self.model = ProbabilityModel(decision_config)
        self.deterministic = deterministic
        self.action_feedback = decision_config.get("action_feedback", {})
        self.feedback_mode = decision_config.get("feedback_mode", "immediate")

    def decide(self, chemical_state: dict):
        probabilities = self.model.compute(chemical_state)

        if self.deterministic:
            action = max(probabilities, key=probabilities.get)
        else:
            action = self._weighted_random_choice(probabilities)

        return {
            "action": action,
            "probabilities": probabilities,
            "feedback": self.action_feedback.get(action, {})
        }

    def _weighted_random_choice(self, probabilities: dict):
        import random
        actions = list(probabilities.keys())
        weights = list(probabilities.values())
        return random.choices(actions, weights=weights, k=1)[0]

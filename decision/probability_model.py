class ProbabilityModel:
    def __init__(self, config: dict):
        self.actions = config["actions"]
        self.base_probabilities = config["base_probabilities"]
        self.chemical_influence = config.get("chemical_influence", {})
        self.normalize = config.get("normalization", True)

        self.min_prob = config.get("safety_rules", {}).get("min_probability", 0.0)
        self.max_prob = config.get("safety_rules", {}).get("max_probability", 1.0)

    def compute(self, chemical_state: dict):
        # Start with base probabilities
        probabilities = self.base_probabilities.copy()

        # Apply chemical influence
        for chem_name, action_map in self.chemical_influence.items():
            chem_value = chemical_state.get(chem_name, 0)

            for action, weight in action_map.items():
                if action in probabilities:
                    probabilities[action] += chem_value * weight

        # Apply safety clamping
        for action in probabilities:
            probabilities[action] = max(
                self.min_prob,
                min(probabilities[action], self.max_prob)
            )

        # Normalize if required
        if self.normalize:
            total = sum(probabilities.values())
            if total > 0:
                for action in probabilities:
                    probabilities[action] /= total

        return probabilities

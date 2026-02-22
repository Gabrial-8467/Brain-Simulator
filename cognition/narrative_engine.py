import random

class NarrativeEngine:

    def __init__(self):

        self.current_narrative = "I am forming."
        self.identity_bias = {}

        # Stability & decay
        self.bias_decay = 0.98
        self.stability = 0.9  # higher = harder to change narrative

    # -------------------------------------------------
    # UPDATE NARRATIVE
    # -------------------------------------------------

    def update_narrative(self, recent_events):

        if not recent_events:
            return

        successes = 0
        failures = 0
        stress_events = 0

        for event in recent_events:

            identity = event.get("identity", {})
            chemicals = event.get("chemicals", {})

            competence = identity.get("competence", 0)

            cortisol_data = chemicals.get("cortisol", 0)

            if isinstance(cortisol_data, dict):
                cortisol = cortisol_data.get("value", 0)
            else:
                cortisol = cortisol_data

            if competence > 0.6:
                successes += 1

            if competence < 0.4:
                failures += 1

            if cortisol > 55:
                stress_events += 1

        total = len(recent_events)
        if total == 0:
            return

        success_ratio = successes / total
        failure_ratio = failures / total
        stress_ratio = stress_events / total

        growth_score = success_ratio - failure_ratio

        # --------------------------------
        # Narrative Decision
        # --------------------------------

        if growth_score > 0.2:
            new_narrative = "I am capable and improving."
            target_bias = {
                "competence": 0.04,
                "resilience": 0.02
            }

        elif growth_score < -0.2:
            new_narrative = "I struggle but I endure."
            target_bias = {
                "resilience": 0.05,
                "competence": -0.02
            }

        else:
            new_narrative = "I am adapting."
            target_bias = {
                "resilience": 0.02
            }

        if stress_ratio > 0.5:
            new_narrative += " The world feels stressful."
            target_bias["resilience"] = target_bias.get("resilience", 0) + 0.02

        # Stability filter
        if new_narrative != self.current_narrative:
            if random.random() > self.stability:
                self.current_narrative = new_narrative

        # Smooth bias blending
        for trait, value in target_bias.items():
            old = self.identity_bias.get(trait, 0)
            blended = (old * 0.7) + (value * 0.3)
            self.identity_bias[trait] = blended

        # Bias decay
        for trait in list(self.identity_bias.keys()):
            self.identity_bias[trait] *= self.bias_decay

    # -------------------------------------------------
    # GETTERS
    # -------------------------------------------------

    def get_identity_bias(self):
        return self.identity_bias

    def get_current_narrative(self):
        return self.current_narrative

    # 🔥 Compatibility method (brain expects this)
    def get_narrative(self):
        return self.current_narrative

import math


class EmotionalIndex:
    def __init__(self, influence_scale=0.005, max_influence=0.2):
        # Smaller scale for stability
        self.influence_scale = influence_scale

        # Hard cap to prevent runaway emotional amplification
        self.max_influence = max_influence

    # -------------------------------------------------
    # Emotional reaction modifier (chemistry influence)
    # -------------------------------------------------
    def compute_modifier(self, association):

        if not association:
            return {}

        modifier = {}
        frequency = association["frequency"]

        # Confidence grows slowly with repetition (log curve)
        confidence = math.log1p(frequency) / 5

        for chem, total_delta in association["emotional_signature"].items():

            avg_delta = total_delta / max(frequency, 1)

            value = avg_delta * self.influence_scale * confidence

            # Clamp to prevent explosion
            value = max(-self.max_influence, min(value, self.max_influence))

            modifier[chem] = value

        return modifier

    # -------------------------------------------------
    # Decision bias influence (reward conditioning)
    # -------------------------------------------------
    def compute_decision_bias(self, association):

        if not association:
            return 0.0

        frequency = association["frequency"]

        confidence = math.log1p(frequency) / 5

        value = association["reward_score"] * self.influence_scale * confidence

        # Clamp for stability
        return max(-self.max_influence, min(value, self.max_influence))

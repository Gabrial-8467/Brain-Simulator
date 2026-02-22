from collections import defaultdict
import math


class AppraisalEngine:

    def __init__(self, similarity_engine=None):

        # event_type → learned emotional profile
        self.emotional_memory = defaultdict(self._empty_profile)

        self.similarity_engine = similarity_engine

        # learning controls
        self.learning_rate = 0.06
        self.negative_amplifier = 1.3
        self.decay_rate = 0.995
        self.max_intensity = 8.0

        # advanced controls
        self.surprise_sensitivity = 0.08
        self.volatility_decay = 0.99

    # -------------------------------------------------
    # Internal Template
    # -------------------------------------------------

    def _empty_profile(self):
        return {
            "dopamine": 0.0,
            "cortisol": 0.0,
            "oxytocin": 0.0,
            "serotonin": 0.0,
            "confidence": 0.0,
            "volatility": 0.0
        }

    # -------------------------------------------------
    # Predict Emotional Fit (Anticipation)
    # -------------------------------------------------

    def predict_emotion(self, event_type, current_state=None):

        profile = self.emotional_memory[event_type]

        # Base learned prediction
        scale = min(1.0, profile["confidence"])

        predicted = {
            chem: profile[chem] * scale
            for chem in ["dopamine", "cortisol", "oxytocin", "serotonin"]
        }

        # -------------------------------------------------
        # Similarity Generalization
        # -------------------------------------------------

        if self.similarity_engine and current_state:

            similar_profiles = self.similarity_engine.find_similar_profiles(
                event_type,
                current_state
            )

            if similar_profiles:

                for chem in predicted:

                    values = []

                    for sp in similar_profiles:

                        if not isinstance(sp, dict):
                            continue

                        # flat format
                        if chem in sp:
                            values.append(sp.get(chem, 0))

                        # nested format
                        elif "chemical_delta" in sp:
                            values.append(
                                sp["chemical_delta"].get(chem, 0)
                            )

                    if values:
                        avg = sum(values) / len(values)

                        # blend softly (does NOT overwrite memory)
                        predicted[chem] += avg * 0.2

        return predicted

    # -------------------------------------------------
    # Learning Update
    # -------------------------------------------------

    def update_emotional_learning(
        self,
        event_type,
        chemical_delta,
        outcome_value
    ):

        profile = self.emotional_memory[event_type]

        modifier = (
            self.negative_amplifier
            if outcome_value < 0
            else 1.0
        )

        total_surprise = 0

        for chem in ["dopamine", "cortisol", "oxytocin", "serotonin"]:

            delta = chemical_delta.get(chem, 0.0)

            predicted = profile[chem]
            prediction_error = delta - predicted

            total_surprise += abs(prediction_error)

            adjustment = (
                prediction_error
                * outcome_value
                * self.learning_rate
                * modifier
            )

            profile[chem] += adjustment

            profile[chem] = max(
                -self.max_intensity,
                min(self.max_intensity, profile[chem])
            )

        # Surprise drives volatility
        profile["volatility"] += total_surprise * self.surprise_sensitivity
        profile["volatility"] *= self.volatility_decay

        # Stability increases confidence
        stability_factor = 1 - min(1.0, profile["volatility"])
        profile["confidence"] += 0.02 * stability_factor
        profile["confidence"] = min(1.0, profile["confidence"])

        # Plasticity decay
        for chem in ["dopamine", "cortisol", "oxytocin", "serotonin"]:
            profile[chem] *= self.decay_rate

    # -------------------------------------------------

    def get_emotional_memory(self):
        return dict(self.emotional_memory)

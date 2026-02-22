import math
import random


class BrainHelpers:

    @staticmethod
    def normalize(probabilities: dict):
        total = sum(probabilities.values())
        if total == 0:
            return probabilities

        return {k: v / total for k, v in probabilities.items()}

    @staticmethod
    def weighted_choice(probabilities: dict):
        actions = list(probabilities.keys())
        weights = list(probabilities.values())
        return random.choices(actions, weights=weights, k=1)[0]

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + math.exp(-x))

    @staticmethod
    def clamp(value, min_val, max_val):
        return max(min_val, min(value, max_val))

    @staticmethod
    def scale_feedback(delta, multiplier):
        return delta * multiplier

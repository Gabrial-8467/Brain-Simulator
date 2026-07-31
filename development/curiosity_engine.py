# development/curiosity_engine.py

class CuriosityEngine:

    def __init__(self):
        self.novelty_tracker = {}

    # -----------------------------------------
    # NOVELTY OBSERVATION
    # -----------------------------------------

    def observe(self, key: str) -> None:
        """Increment frequency counts for observed concepts, categories, or modalities."""
        if not key:
            return
        self.novelty_tracker[key] = self.novelty_tracker.get(key, 0) + 1

    # -----------------------------------------
    # CURIOSITY EVALUATION
    # -----------------------------------------

    def get_curiosity_bonus(self, key: str) -> float:
        """
        Calculate curiosity bonus based on the inverse frequency of observations.
        
        Formula:
            Curiosity Bonus = 1.0 / (1.0 + Frequency)
        """
        if not key:
            return 0.0
        freq = self.novelty_tracker.get(key, 0)
        return 1.0 / (1.0 + freq)

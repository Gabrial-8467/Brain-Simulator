import copy

class CuriosityEngine:
    def __init__(self):
        self.novelty_tracker = {}

    def observe(self, key: str) -> None:
        """Increment count for an observed category or modality."""
        if not key:
            return
        self.novelty_tracker[key] = self.novelty_tracker.get(key, 0) + 1

    def get_curiosity_bonus(self, key: str) -> float:
        """Calculate curiosity bonus based on inverse frequency of observation."""
        if not key:
            return 0.0
        freq = self.novelty_tracker.get(key, 0)
        return 1.0 / (1.0 + freq)

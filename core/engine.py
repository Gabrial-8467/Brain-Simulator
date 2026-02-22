from core.homeostasis import Homeostasis
from core.noise import Noise


class BrainEngine:
    def __init__(self, state, interactions, deterministic=False):
        self.state = state
        self.interactions = interactions
        self.deterministic = deterministic

    def tick(self):
        # Apply chemical interactions
        self.interactions.apply(self.state)

        # Apply homeostasis
        Homeostasis.apply(self.state)

        # Apply stochastic noise
        Noise.apply(self.state, deterministic=self.deterministic)

        # Clamp values
        self._clamp()

    def _clamp(self):
        for name, data in self.state.chemicals.items():
            value = data["value"]
            min_val = data["min"]
            max_val = data["max"]

            data["value"] = max(min_val, min(value, max_val))

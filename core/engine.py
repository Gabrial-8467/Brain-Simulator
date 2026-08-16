from core.homeostasis import Homeostasis
from core.noise import Noise
from core.interactions import Interactions
from core.state import BrainState


class BrainEngine:
    """Chemical micro-engine orchestrating the per-tick chemical mechanics.

    Applies cross-chemical interactions, homeostasis, stochastic noise and
    clamping against any state container exposing ``.chemicals`` (dict-like,
    ``data["value"]`` protocol). When no ``state`` is supplied it builds a
    reference ``BrainState`` from ``chemical_configs``; the live simulation
    passes its richer ``ChemicalRegistry`` instead.

    When constructed with a ``brain``, the enhanced config-driven homeostasis
    is used; standalone usage falls back to the naive baseline decay.
    """

    def __init__(self, state=None, interactions=None, deterministic=False, brain=None, chemical_configs=None):
        if state is None:
            state = BrainState(chemical_configs or {})
        self.state = state
        self.interactions = interactions or Interactions({})
        self.deterministic = deterministic
        self.brain = brain

    def apply_interactions(self):
        self.interactions.apply(self.state)

    def apply_homeostasis(self):
        Homeostasis.apply(self.state, brain=self.brain)

    def apply_noise(self):
        Noise.apply(self.state, deterministic=self.deterministic)

    def clamp(self):
        for name, data in self.state.chemicals.items():
            value = data["value"]
            min_val = data["min"]
            max_val = data["max"]

            data["value"] = max(min_val, min(value, max_val))

    def tick(self):
        # Apply chemical interactions
        self.apply_interactions()

        # Apply homeostasis
        self.apply_homeostasis()

        # Apply stochastic noise
        self.apply_noise()

        # Clamp values
        self.clamp()

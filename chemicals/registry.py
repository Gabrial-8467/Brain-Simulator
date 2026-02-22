from chemicals.models import Chemical


class ChemicalRegistry:
    def __init__(self, chemical_configs: dict):
        self.chemicals = {}

        for name, config in chemical_configs.items():
            self.chemicals[name] = Chemical(name, config)

    def get(self, name: str):
        return self.chemicals.get(name)

    def all(self):
        return self.chemicals

    def values(self):
        return {name: chem.value for name, chem in self.chemicals.items()}

    def apply_homeostasis(self):
        for chem in self.chemicals.values():
            chem.apply_homeostasis()

    def apply_noise(self, deterministic=False):
        for chem in self.chemicals.values():
            chem.apply_noise(deterministic=deterministic)

    def clamp_all(self):
        for chem in self.chemicals.values():
            chem.clamp()

    def inject_event(self, effects: dict):
        for name, delta in effects.items():
            if name in self.chemicals:
                self.chemicals[name].inject(delta)

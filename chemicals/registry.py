from chemicals.models import Chemical


class ChemicalRegistry:
    def __init__(self, chemical_configs: dict):
        self.chemicals = {}

        for name, config in chemical_configs.items():
            self.chemicals[name] = Chemical(name, config)

    def get(self, name: str, default=None):
        return self.chemicals.get(name, default)

    def all(self):
        return self.chemicals

    def values(self):
        return self.chemicals.values()

    def items(self):
        return self.chemicals.items()

    def keys(self):
        return self.chemicals.keys()

    def __getitem__(self, key):
        chem = self.get(key)
        if chem is None:
            raise KeyError(key)
        return chem

    def __setitem__(self, key, value):
        chem = self.get(key)
        if chem is not None:
            if isinstance(value, (int, float)):
                chem.value = float(value)
            elif isinstance(value, dict) and "value" in value:
                chem.value = float(value["value"])
            elif hasattr(value, "value"):
                chem.value = float(value.value)

    def __contains__(self, key):
        return key in self.chemicals

    def __iter__(self):
        return iter(self.chemicals)

    def apply_homeostasis(self):
        for chem in self.chemicals.values():
            chem.apply_homeostasis()

    def apply_noise(self, deterministic=False):
        for chem in self.chemicals.values():
            chem.apply_noise(deterministic=deterministic)

    def clamp_all(self):
        for chem in self.chemicals.values():
            chem.clamp()

    def update_receptor_dynamics(self):
        for chem in self.chemicals.values():
            chem.update_receptor_dynamics()

    def inject_event(self, effects: dict):
        for name, delta in effects.items():
            if name in self.chemicals:
                self.chemicals[name].inject(delta)

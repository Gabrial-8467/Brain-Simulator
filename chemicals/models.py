from typing import Any

class Chemical:
    def __init__(self, name: str, config: dict):
        self.name = name
        self.value = float(config["baseline"])
        self.baseline = float(config["baseline"])
        self.min = float(config["min"])
        self.max = float(config["max"])
        self.decay = float(config["decay"])
        self.noise = float(config["noise"])
        
        # Dynamic Receptor Sensitivity Configuration
        self.sensitivity = 1.0
        self.baseline_sensitivity = 1.0
        self.chronic_high_ticks = 0
        self.chronic_low_ticks = 0

    @property
    def effective_value(self) -> float:
        return self.value * self.sensitivity

    def update_receptor_dynamics(self):
        # Downregulation if chronically elevated
        if self.value >= 1.5 * self.baseline:
            self.chronic_high_ticks += 1
            if self.chronic_high_ticks >= 5:
                self.sensitivity = max(0.2, self.sensitivity - 0.02)
        else:
            self.chronic_high_ticks = 0

        # Upregulation if chronically depressed
        if self.value <= 0.5 * self.baseline:
            self.chronic_low_ticks += 1
            if self.chronic_low_ticks >= 5:
                self.sensitivity = min(2.0, self.sensitivity + 0.01)
        else:
            self.chronic_low_ticks = 0

        # Gentle drift back to baseline sensitivity if chemical is near baseline
        if 0.8 * self.baseline <= self.value <= 1.2 * self.baseline:
            self.sensitivity += (self.baseline_sensitivity - self.sensitivity) * 0.005

    def apply_homeostasis(self):
        self.value += (self.baseline - self.value) * self.decay

    def apply_noise(self, deterministic=False, random_fn=None):
        if deterministic:
            return

        if random_fn is None:
            import random
            random_fn = random.uniform

        variation = random_fn(-self.noise, self.noise)
        self.value += variation

    def clamp(self):
        self.value = max(self.min, min(self.value, self.max))

    def inject(self, delta: float):
        self.value += delta

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
            "baseline": self.baseline,
            "min": self.min,
            "max": self.max,
            "decay": self.decay,
            "noise": self.noise,
            "sensitivity": self.sensitivity,
            "effective_value": self.effective_value,
        }

    def __getitem__(self, key: str) -> float | str:
        if key == "value":
            return self.value
        elif key == "baseline":
            return self.baseline
        elif key == "min":
            return self.min
        elif key == "max":
            return self.max
        elif key == "decay":
            return self.decay
        elif key == "noise":
            return self.noise
        elif key == "name":
            return self.name
        elif key == "sensitivity":
            return self.sensitivity
        elif key == "effective_value":
            return self.effective_value
        raise KeyError(key)

    def __setitem__(self, key: str, value: float | str) -> None:
        if key == "value":
            self.value = float(value)
        elif key == "baseline":
            self.baseline = float(value)
        elif key == "min":
            self.min = float(value)
        elif key == "max":
            self.max = float(value)
        elif key == "decay":
            self.decay = float(value)
        elif key == "noise":
            self.noise = float(value)
        elif key == "name":
            self.name = str(value)
        elif key == "sensitivity":
            self.sensitivity = float(value)
        else:
            raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

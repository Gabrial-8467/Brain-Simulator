from typing import Any

class Chemical:
    def __init__(self, name: str, config: dict):
        self.name = name
        self.value = config["baseline"]
        self.baseline = config["baseline"]
        self.min = config["min"]
        self.max = config["max"]
        self.decay = config["decay"]
        self.noise = config["noise"]

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
        else:
            raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

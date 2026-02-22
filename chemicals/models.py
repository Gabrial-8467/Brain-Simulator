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

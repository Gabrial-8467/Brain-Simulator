import random


class Bias:
    def __init__(self, name, config):

        self.name = name

        # 🔹 Small randomized core temperament
        core_range = config.get("core_range", 0.2)
        self.value = random.uniform(-core_range, core_range)

        # Symmetric bounded personality space
        self.min = config.get("min", -1.0)
        self.max = config.get("max", 1.0)

        # 🔹 Very slow personality decay (human-like stability)
        self.decay = config.get("decay", 0.0003)

        # 🔹 Small threshold for significant learning
        self.delta_threshold = config.get("delta_threshold", 8.0)

        # 🔹 Very small imprint factor (slow growth)
        self.imprint_factor = config.get("imprint_factor", 0.0005)

    def apply_decay(self):
        self.value *= (1 - self.decay)

    def clamp(self):
        self.value = max(self.min, min(self.value, self.max))

    def imprint(self, delta_value):
        if abs(delta_value) >= self.delta_threshold:
            direction = 1 if delta_value > 0 else -1
            self.value += direction * self.imprint_factor

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value
        }

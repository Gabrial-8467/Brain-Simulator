import random


class Noise:
    @staticmethod
    def apply(state, deterministic=False):
        if deterministic:
            return

        for name, data in state.chemicals.items():
            noise_range = data["noise"]
            variation = random.uniform(-noise_range, noise_range)
            data["value"] += variation

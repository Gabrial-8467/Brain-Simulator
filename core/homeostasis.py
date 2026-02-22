class Homeostasis:
    @staticmethod
    def apply(state):
        for name, data in state.chemicals.items():
            current = data["value"]
            baseline = data["baseline"]
            decay = data["decay"]

            updated = current + (baseline - current) * decay
            data["value"] = updated

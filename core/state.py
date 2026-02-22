class BrainState:
    def __init__(self, chemical_configs: dict):
        self.chemicals = {}

        for name, config in chemical_configs.items():
            self.chemicals[name] = {
                "value": config["baseline"],
                "baseline": config["baseline"],
                "min": config["min"],
                "max": config["max"],
                "decay": config["decay"],
                "noise": config["noise"]
            }

    def get(self, name):
        return self.chemicals[name]["value"]

    def set(self, name, value):
        self.chemicals[name]["value"] = value

    def all(self):
        return {k: v["value"] for k, v in self.chemicals.items()}

    def metadata(self, name):
        return self.chemicals[name]

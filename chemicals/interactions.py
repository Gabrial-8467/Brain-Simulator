class ChemicalInteractions:
    def __init__(self, interaction_matrix: dict):
        """
        interaction_matrix format:

        {
            "cortisol": {
                "dopamine": -0.001
            },
            "serotonin": {
                "cortisol": -0.0005
            }
        }
        """
        self.matrix = interaction_matrix or {}

    def apply(self, registry):
        deltas = {}

        for source_name, targets in self.matrix.items():
            source = registry.get(source_name)
            if not source:
                continue

            for target_name, weight in targets.items():
                target = registry.get(target_name)
                if not target:
                    continue

                influence = source.value * weight

                if target_name not in deltas:
                    deltas[target_name] = 0

                deltas[target_name] += influence

        # Apply after calculating all influences
        for target_name, delta in deltas.items():
            registry.get(target_name).inject(delta)

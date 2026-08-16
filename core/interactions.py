class Interactions:
    def __init__(self, interaction_matrix: dict):
        self.matrix = interaction_matrix or {}

    def apply(self, state):
        """Apply cross-chemical influences through the interaction matrix.

        Operates on any container exposing ``.chemicals.items()`` where each
        chemical supports the mapping protocol (``data["value"]``), e.g.
        ``BrainState`` or ``ChemicalRegistry``.
        """
        chemicals = state.chemicals

        deltas = {}

        for source, targets in self.matrix.items():
            if source not in chemicals:
                continue

            source_value = chemicals[source]["value"]

            for target, weight in targets.items():
                if target not in chemicals:
                    continue

                influence = source_value * weight

                if target not in deltas:
                    deltas[target] = 0

                deltas[target] += influence

        # Apply after calculating all influences
        for target, delta in deltas.items():
            chemicals[target]["value"] += delta

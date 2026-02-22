class Interactions:
    def __init__(self, interaction_matrix: dict):
        self.matrix = interaction_matrix

    def apply(self, state):
        deltas = {}

        for source, targets in self.matrix.items():
            source_value = state.get(source)

            for target, weight in targets.items():
                influence = source_value * weight

                if target not in deltas:
                    deltas[target] = 0

                deltas[target] += influence

        # Apply after calculating all influences
        for target, delta in deltas.items():
            current = state.get(target)
            state.set(target, current + delta)

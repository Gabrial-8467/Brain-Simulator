import math


class AssociativeMemory:
    def __init__(self, base_decay=0.0005, min_strength=0.0001):
        self.memory = {}

        # Very slow decay (human-like forgetting)
        self.base_decay = base_decay

        # Remove memory if it becomes extremely weak
        self.min_strength = min_strength

    # -------------------------------------------------
    # Update / Reinforce Memory
    # -------------------------------------------------
    def update(self, context_key, chemical_deltas, reward_score=0):

        if context_key not in self.memory:
            self.memory[context_key] = {
                "frequency": 0,
                "emotional_signature": {},
                "reward_score": 0.0,
                "strength": 1.0
            }

        entry = self.memory[context_key]

        entry["frequency"] += 1

        # Reinforce memory strength logarithmically
        entry["strength"] += math.log1p(entry["frequency"]) * 0.01

        entry["reward_score"] += reward_score

        for chem, delta in chemical_deltas.items():
            if chem not in entry["emotional_signature"]:
                entry["emotional_signature"][chem] = 0.0

            entry["emotional_signature"][chem] += delta

    # -------------------------------------------------
    # Retrieve Association
    # -------------------------------------------------
    def get_association(self, context_key):
        return self.memory.get(context_key, None)

    # -------------------------------------------------
    # Human-like Decay
    # -------------------------------------------------
    def decay(self):

        keys_to_delete = []

        for key, entry in self.memory.items():

            # Stronger memories decay slower
            adaptive_decay = self.base_decay / max(entry["strength"], 1)

            entry["reward_score"] *= (1 - adaptive_decay)

            for chem in entry["emotional_signature"]:
                entry["emotional_signature"][chem] *= (1 - adaptive_decay)

            entry["strength"] *= (1 - adaptive_decay)

            # Remove extremely weak memories
            if entry["strength"] < self.min_strength:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self.memory[key]

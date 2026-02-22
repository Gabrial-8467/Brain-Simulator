class DynamicIdentity:
    def __init__(self):
        self.traits = {
            "competence": 0.5,
            "social_value": 0.5,
            "resilience": 0.5,
            "intelligence": 0.5,
        }

        self.evidence = {trait: 0 for trait in self.traits}
        self.learning_rate = 0.02

    def add_evidence(self, trait, amount):
        if trait in self.evidence:
            self.evidence[trait] += amount

    def update(self):
        for trait in self.traits:
            delta = self.evidence[trait] * self.learning_rate
            self.traits[trait] += delta
            self.traits[trait] = max(0.0, min(1.0, self.traits[trait]))
            self.evidence[trait] = 0

    def get(self, trait):
        return self.traits.get(trait, 0)

    def get_snapshot(self):
        return self.traits.copy()

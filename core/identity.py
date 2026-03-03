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

    def _sanitize_trait(self, value):
        return round(max(0.0, min(1.0, float(value))), 4)

    def add_evidence(self, trait, amount):
        if trait in self.evidence:
            self.evidence[trait] = round(self.evidence[trait] + float(amount), 6)

    def update(self):
        for trait in self.traits:
            delta = self.evidence[trait] * self.learning_rate
            self.traits[trait] = self._sanitize_trait(self.traits[trait] + delta)
            self.evidence[trait] = 0.0

    def get(self, trait):
        return self.traits.get(trait, 0)

    def get_snapshot(self):
        return self.traits.copy()

class AbstractionEngine:
    def __init__(self):
        self.categories = {}  # category_name → set(context_keys)
        self.category_profiles = {}  # category → chemical weights

    def assign_to_category(self, category_name, context_key):
        if category_name not in self.categories:
            self.categories[category_name] = set()
            self.category_profiles[category_name] = {}

        self.categories[category_name].add(context_key)

    def update_category_profile(self, category_name, chemical_deltas, learning_rate=0.001):
        if category_name not in self.category_profiles:
            return

        for chem, delta in chemical_deltas.items():
            if chem not in self.category_profiles[category_name]:
                self.category_profiles[category_name][chem] = 0

            self.category_profiles[category_name][chem] += delta * learning_rate

    def get_category_profile(self, context_key):
        for category, members in self.categories.items():
            if context_key in members:
                return self.category_profiles.get(category, {})

        return {}

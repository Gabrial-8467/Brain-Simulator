from bias.bias_models import Bias


class BiasEngine:
    def __init__(self, bias_configs, mapping_matrix):
        self.biases = {
            name: Bias(name, config)
            for name, config in bias_configs.items()
        }

        self.mapping_matrix = mapping_matrix

    # -----------------------------------
    # 1️⃣ Imprint based on deviation (slow drift)
    # -----------------------------------
    def update_from_conscious(self, conscious_state, baseline_state):

        for bias_name, bias in self.biases.items():

            mapping = self.mapping_matrix.get(bias_name, {})

            for chem_name in mapping.get("imprint_from", []):
                if chem_name in conscious_state:

                    delta = conscious_state[chem_name] - baseline_state[chem_name]

                    # Imprint only on significant deviation
                    bias.imprint(delta)

            # Very slow stabilization
            bias.apply_decay()
            bias.clamp()

    # -----------------------------------
    # 2️⃣ Apply baseline shift (NON-ACCUMULATIVE)
    # -----------------------------------
    def apply_baseline_shift(self, chemicals):

        for bias_name, bias in self.biases.items():

            mapping = self.mapping_matrix.get(bias_name, {})

            for chem_name, weight in mapping.get("baseline_shift", {}).items():

                if chem_name in chemicals:

                    # Reset to original baseline first (important!)
                    original = chemicals[chem_name].get("baseline")

                    # Apply bias influence temporarily
                    chemicals[chem_name]["baseline"] = (
                        original + bias.value * weight
                    )

    # -----------------------------------
    # 3️⃣ Scale reaction strength (subtle amplification)
    # -----------------------------------
    def scale_reaction(self, chemical_name, delta):

        for bias_name, bias in self.biases.items():

            mapping = self.mapping_matrix.get(bias_name, {})

            if chemical_name in mapping.get("reaction_scale", {}):

                weight = mapping["reaction_scale"][chemical_name]

                # Soft scaling to prevent explosion
                delta *= (1 + bias.value * weight)

        return delta

    # -----------------------------------
    # 4️⃣ Modify decision probabilities (small nudging)
    # -----------------------------------
    def modify_decision(self, probabilities):

        for bias_name, bias in self.biases.items():

            mapping = self.mapping_matrix.get(bias_name, {})

            for action, weight in mapping.get("decision_bias", {}).items():

                if action in probabilities:

                    probabilities[action] += bias.value * weight

        return probabilities

    # -----------------------------------
    # 5️⃣ Get bias state
    # -----------------------------------
    def get_bias_state(self):
        return {name: bias.value for name, bias in self.biases.items()}

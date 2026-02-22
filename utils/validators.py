class ConfigValidator:

    @staticmethod
    def validate_chemicals(config: dict, logger=None):
        required_keys = ["min", "max", "baseline", "decay", "noise"]

        for chem_name, chem_config in config.items():
            for key in required_keys:
                if key not in chem_config:
                    if logger:
                        logger.warning(
                            f"[Validator] '{chem_name}' missing '{key}'. Applying default."
                        )
                    chem_config[key] = 0

            # Fix invalid min/max
            if chem_config["min"] >= chem_config["max"]:
                if logger:
                    logger.warning(
                        f"[Validator] '{chem_name}' min >= max. Swapping values."
                    )
                chem_config["min"], chem_config["max"] = (
                    chem_config["max"],
                    chem_config["min"],
                )

            # Clamp baseline inside range
            if not (chem_config["min"] <= chem_config["baseline"] <= chem_config["max"]):
                if logger:
                    logger.warning(
                        f"[Validator] '{chem_name}' baseline outside range. Clamping."
                    )
                chem_config["baseline"] = max(
                    chem_config["min"],
                    min(chem_config["baseline"], chem_config["max"]),
                )

        return config

    @staticmethod
    def validate_decision_config(config: dict, logger=None):
        if "actions" not in config:
            if logger:
                logger.warning("[Validator] Missing 'actions'. Creating empty list.")
            config["actions"] = []

        if "base_probabilities" not in config:
            if logger:
                logger.warning("[Validator] Missing base probabilities. Initializing uniform.")
            config["base_probabilities"] = {
                action: 1.0 for action in config["actions"]
            }

        total = sum(config["base_probabilities"].values())

        if total <= 0:
            if logger:
                logger.warning("[Validator] Invalid probability sum. Resetting to uniform.")
            uniform = 1.0 / max(len(config["actions"]), 1)
            config["base_probabilities"] = {
                action: uniform for action in config["actions"]
            }

        return config

    @staticmethod
    def validate_interactions(interaction_matrix: dict, chemical_names: list, logger=None):
        cleaned_matrix = {}

        for source, targets in interaction_matrix.items():
            if source not in chemical_names:
                if logger:
                    logger.warning(f"[Validator] Invalid interaction source: {source}")
                continue

            cleaned_matrix[source] = {}

            for target, weight in targets.items():
                if target not in chemical_names:
                    if logger:
                        logger.warning(f"[Validator] Invalid interaction target: {target}")
                    continue

                cleaned_matrix[source][target] = weight

        return cleaned_matrix

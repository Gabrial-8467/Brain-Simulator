class Homeostasis:
    @staticmethod
    def apply(state, brain=None):
        """Drive chemical values toward their baselines.

        Two modes:

        - ``brain=None`` (standalone): the legacy naive decay toward each
          chemical's own baseline using its per-chemical ``decay`` rate.
        - ``brain=<VirtualBrain>``: the full config-driven homeostasis used by
          the live simulation, including gentle dopamine recovery, oxytocin
          floor protection, cortisol decay and serotonin regulation.
        """
        if brain is None:
            for name, data in state.chemicals.items():
                current = data["value"]
                baseline = data["baseline"]
                decay = data["decay"]

                updated = current + (baseline - current) * decay
                data["value"] = updated
            return

        has_positive_perception = any(v > 0 for v in brain._step_perception_valences)
        homeo = brain.brain_config["homeostasis"]
        oxy_mults = homeo["oxytocin_decay_multipliers"]
        for chem_name, data in state.chemicals.items():
            current = data["value"]
            target = float(
                brain.homeostasis_baselines.get(chem_name, data.get("baseline", brain.homeostasis_target))
            )
            delta = (target - current) * brain.homeostasis_rate
            delta = max(-brain.homeostasis_max_delta, min(brain.homeostasis_max_delta, delta))

            if chem_name == "dopamine" and delta > 0 and not has_positive_perception:
                delta = min(delta, brain.homeostasis_gentle_upward_max)

            if chem_name == "oxytocin" and delta < 0:
                social_value = float(brain.identity.get("social_value"))
                if social_value > float(oxy_mults["high_social_value"]):
                    oxytocin_decay_multiplier = float(oxy_mults["high_multiplier"])
                elif social_value > float(oxy_mults["mid_social_value"]):
                    oxytocin_decay_multiplier = float(oxy_mults["mid_multiplier"])
                else:
                    oxytocin_decay_multiplier = 1.0
                delta *= oxytocin_decay_multiplier

            if chem_name == "cortisol":
                excess = max(0.0, current - brain.cortisol_decay_baseline)
                cortisol_decay = float(homeo["cortisol_decay_rate"]) * excess
                delta -= cortisol_decay
                delta = max(-brain.homeostasis_max_delta, min(brain.homeostasis_max_delta, delta))

            updated = current + delta
            if chem_name == "oxytocin" and updated < float(homeo["oxytocin_floor"]):
                updated += (float(homeo["oxytocin_floor"]) - updated) * float(homeo["oxytocin_floor_pull"])
            if chem_name == "serotonin":
                serotonin_pull = (brain.serotonin_regulation_baseline - updated) * float(homeo["serotonin_pull_rate"])
                updated += serotonin_pull
            data["value"] = updated

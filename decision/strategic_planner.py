import copy


class StrategicPlanner:

    def __init__(
        self,
        appraisal_engine,
        similarity_engine,
        identity
    ):
        self.appraisal_engine = appraisal_engine
        self.similarity_engine = similarity_engine
        self.identity = identity

        # Planning depth (multi-step lookahead)
        self.max_depth = 2

        # Dynamic risk aversion (can evolve later)
        self.risk_aversion = 0.2

    # -------------------------------------------------
    # ACTION SELECTION
    # -------------------------------------------------

    def choose_action(self, brain, probabilities):

        best_action = None
        best_score = float("-inf")

        # Get a lightweight copy of the current state
        current_state = brain.get_state()

        for action, base_prob in probabilities.items():

            simulated_score = self._simulate_future(
                brain,
                current_state,
                action,
                depth=self.max_depth
            )

            # Personality influence
            competence = self.identity.get("competence")
            resilience = self.identity.get("resilience")

            personality_modifier = (
                competence * 0.3 +
                resilience * 0.2
            )

            final_score = (
                simulated_score +
                personality_modifier -
                self.risk_aversion * (1 - base_prob)
            )

            if final_score > best_score:
                best_score = final_score
                best_action = action

        return best_action

    # -------------------------------------------------
    # FUTURE SIMULATION
    # -------------------------------------------------

    def _simulate_future(self, brain, current_state, action, depth):

        if depth == 0:
            return 0.0

        # Execute hypothetical action
        decision_output = brain.decision_engine.execute_action(
            action,
            current_state
        ) if brain.decision_engine else {}

        feedback = decision_output.get("feedback", {})
        reward_score = sum(feedback.values())

        # Transition chemical state based on feedback
        next_chemicals = current_state.get("neurochemicals", {}).copy()
        feedback_multiplier = getattr(brain, "feedback_multiplier", 1.0)
        decision_feedback_scale = getattr(brain, "decision_feedback_scale", 0.45)

        for chem, delta in feedback.items():
            if chem in next_chemicals and chem in brain.chemicals:
                chem_def = brain.chemicals[chem]
                val = next_chemicals[chem]
                span = max(1e-6, chem_def["max"] - chem_def["min"])

                bounded = max(-3.0, min(3.0, delta * feedback_multiplier * decision_feedback_scale))
                if chem == "cortisol":
                    bounded = max(-0.6, min(0.6, bounded))

                # Saturation scaling
                if bounded >= 0:
                    headroom = (chem_def["max"] - val) / span
                else:
                    headroom = (val - chem_def["min"]) / span
                scale = max(0.15, min(1.0, headroom * 1.8))

                new_val = val + bounded * scale
                # Clamp
                new_val = max(chem_def["min"], min(new_val, chem_def["max"]))
                if chem == "cortisol":
                    new_val = min(100.0, new_val)

                next_chemicals[chem] = new_val

        # Create transitioned state dictionary for next lookahead steps
        temp_state = current_state.copy()
        temp_state["neurochemicals"] = next_chemicals
        for chem, val in next_chemicals.items():
            temp_state[chem] = val  # update flattened values

        # Next state probabilities
        if brain.decision_engine and brain.decision_engine.model:
            next_probabilities = brain.decision_engine.model.compute(next_chemicals)
            action_bias = temp_state.get("decision_action_bias", {})
            if isinstance(action_bias, dict):
                for act, delta in action_bias.items():
                    if act in next_probabilities:
                        next_probabilities[act] += float(delta)
            # Clamp and normalize
            min_prob = getattr(brain.decision_engine.model, "min_prob", 0.0)
            max_prob = getattr(brain.decision_engine.model, "max_prob", 1.0)
            for act in next_probabilities:
                next_probabilities[act] = max(min_prob, min(max_prob, next_probabilities[act]))
            total = sum(next_probabilities.values())
            if total > 0:
                for act in next_probabilities:
                    next_probabilities[act] /= total
        else:
            actions = ["support", "challenge", "suggest", "refuse", "neutral"]
            next_probabilities = {act: 1.0 / len(actions) for act in actions}

        future_score = 0.0

        for next_action, prob in next_probabilities.items():
            future_score += (
                prob *
                self._simulate_future(
                    brain,
                    temp_state,
                    next_action,
                    depth - 1
                )
            )

        return reward_score + 0.5 * future_score

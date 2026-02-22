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

        for action, base_prob in probabilities.items():

            simulated_score = self._simulate_future(
                brain,
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

    def _simulate_future(self, brain, action, depth):

        if depth == 0:
            return 0

        simulated_brain = copy.deepcopy(brain)

        # Execute hypothetical action
        decision_output = simulated_brain.decision_engine.execute_action(
            action,
            simulated_brain.get_state()
        )

        feedback = decision_output.get("feedback", {})
        reward_score = sum(feedback.values())

        # Next state probabilities
        next_probabilities = simulated_brain.decision_engine.model.compute(
            simulated_brain.get_state()
        )

        future_score = 0

        for next_action, prob in next_probabilities.items():
            future_score += (
                prob *
                self._simulate_future(
                    simulated_brain,
                    next_action,
                    depth - 1
                )
            )

        return reward_score + 0.5 * future_score

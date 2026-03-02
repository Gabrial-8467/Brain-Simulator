from __future__ import annotations

from core.attention import GlobalWorkspace, Thought


class SelfReflection:
    def __init__(self, appraisal_engine, similarity_engine, identity):
        self.appraisal_engine = appraisal_engine
        self.similarity_engine = similarity_engine
        self.identity = identity

        self.wisdom = 0.0
        self.regret_memory = []
        self.confidence_shift = 0.0

        self.max_regret_memory = 200
        self.regret_sensitivity = 0.8
        self.wisdom_growth_rate = 0.002

    def reflect_on_decision(self, chosen_action, available_actions, current_state):
        actual_value = self._estimate_action_value(chosen_action, current_state)
        best_alternative_value = actual_value

        for action in available_actions:
            if action == chosen_action:
                continue
            value = self._estimate_action_value(action, current_state)
            if value > best_alternative_value:
                best_alternative_value = value

        regret = best_alternative_value - actual_value
        self._update_regret(regret)
        self._update_confidence(regret)
        self._update_wisdom(regret)
        return regret

    def _estimate_action_value(self, action, state):
        predicted = self.appraisal_engine.predict_emotion(event_type=action, current_state=state)
        return (
            predicted.get("dopamine", 0)
            + predicted.get("serotonin", 0)
            - predicted.get("cortisol", 0)
        )

    def _update_regret(self, regret):
        self.regret_memory.append(regret)
        if len(self.regret_memory) > self.max_regret_memory:
            self.regret_memory.pop(0)

    def _update_confidence(self, regret):
        if regret > 0:
            self.identity.add_evidence("competence", -regret * 0.02)
            self.confidence_shift -= regret * 0.01
        else:
            self.identity.add_evidence("competence", 0.01)
            self.confidence_shift += 0.005

    def _update_wisdom(self, regret):
        if regret > 0:
            self.wisdom += regret * self.wisdom_growth_rate
        self.wisdom = max(0.0, min(1.0, self.wisdom))

    def propose_reflection_thought(self, brain, chosen_action, regret) -> None:
        th = Thought(
            content=f"Reflection on {chosen_action}: regret={regret:.2f}",
            source="internal",
            emotional_weight=max(0.0, min(1.0, abs(regret) * 0.3)),
            novelty=0.3,
            relevance_to_goals=0.3,
        )
        GlobalWorkspace.post(th)

    def get_wisdom(self):
        return self.wisdom

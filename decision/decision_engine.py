from __future__ import annotations

from core.attention import Thought

from .probability_model import ProbabilityModel


class DecisionEngine:
    def __init__(self, decision_config: dict, deterministic: bool = False):
        self.model = ProbabilityModel(decision_config)
        self.deterministic = deterministic
        self.action_feedback = decision_config.get("action_feedback", {})
        self.feedback_mode = decision_config.get("feedback_mode", "immediate")

    def decide(self, focus: Thought) -> dict:
        base = self.model.compute({})

        bias = (focus.emotional_weight * 0.3) + (focus.relevance_to_goals * 0.2)
        for act in base:
            base[act] += bias

        total = sum(base.values())
        if total:
            for k in base:
                base[k] /= total

        if self.deterministic:
            action = max(base, key=base.get)
        else:
            import random

            actions = list(base.keys())
            probs = list(base.values())
            action = random.choices(actions, weights=probs, k=1)[0]

        return {
            "action": action,
            "probabilities": base,
            "feedback": self.action_feedback.get(action, {}),
        }

    def execute_action(self, action: str, state: dict | None = None) -> dict:
        return {
            "action": action,
            "probabilities": {},
            "feedback": self.action_feedback.get(action, {}),
        }

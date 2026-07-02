from __future__ import annotations

from core.attention import Thought

from .probability_model import ProbabilityModel


class DecisionEngine:
    def __init__(self, decision_config: dict, deterministic: bool = False):
        self.model = ProbabilityModel(decision_config)
        self.deterministic = deterministic
        self.action_feedback = decision_config.get("action_feedback", {})
        self.feedback_mode = decision_config.get("feedback_mode", "immediate")

    def decide(self, focus: Thought, state: dict | None = None, recent_valence_avg: float = 0.0) -> dict:
        state = state or {}

        neuro = state.get("neurochemicals", {}) if isinstance(state.get("neurochemicals", {}), dict) else {}
        chemical_state = {
            "dopamine": float(neuro.get("dopamine", state.get("dopamine", 0.0))),
            "cortisol": float(neuro.get("cortisol", state.get("cortisol", 0.0))),
            "oxytocin": float(neuro.get("oxytocin", state.get("oxytocin", 0.0))),
            "serotonin": float(neuro.get("serotonin", state.get("serotonin", 0.0))),
        }
        identity = state.get("identity_traits", {}) if isinstance(state.get("identity_traits", {}), dict) else {}

        base = self.model.compute(chemical_state)
        action_bias = state.get("decision_action_bias", {})
        if isinstance(action_bias, dict):
            for action, delta in action_bias.items():
                if action in base:
                    base[action] += float(delta)

        stress_level = max(0.0, min(1.0, chemical_state.get("cortisol", 0.0) / 100.0))
        reward_level = max(0.0, min(1.0, chemical_state.get("dopamine", 0.0) / 100.0))
        bond_level = max(0.0, min(1.0, chemical_state.get("oxytocin", 0.0) / 100.0))
        serotonin_level = max(0.0, min(1.0, chemical_state.get("serotonin", 0.0) / 100.0))
        emotional_salience = max(0.0, min(1.0, float(focus.emotional_weight)))
        competence = max(0.0, min(1.0, float(identity.get("competence", state.get("identity_competence", 0.5)))))
        social_value = max(-0.3, min(1.0, float(identity.get("social_value", state.get("identity_social_value", 0.5)))))
        social_norm = (social_value + 0.3) / 1.3
        mood_state = state.get("mood_state", {}) if isinstance(state.get("mood_state", {}), dict) else {}
        mood_valence = max(-1.0, min(1.0, float(mood_state.get("valence", 0.0))))
        mood_arousal = max(0.0, min(1.0, float(mood_state.get("arousal", 0.0))))

        active_beliefs = state.get("beliefs", [])
        if not isinstance(active_beliefs, list):
            active_beliefs = []
        belief_map = {}
        for belief in active_beliefs:
            if not isinstance(belief, dict):
                continue
            statement = str(belief.get("statement", "")).lower()
            confidence = float(belief.get("confidence", 0.0) or 0.0)
            if statement:
                belief_map[statement] = max(belief_map.get(statement, 0.0), confidence)

        action_modifiers = {
            "refuse": 0.9 * stress_level,
            "neutral": 0.55 * stress_level,
            "support": (0.85 * bond_level) - (0.5 * stress_level),
            "suggest": (0.55 * reward_level) - (0.25 * stress_level),
            "challenge": (0.35 * stress_level) + (0.4 * max(0.0, -recent_valence_avg)),
        }

        for action in list(base.keys()):
            base[action] += action_modifiers.get(action, 0.0)

        base["support"] = base.get("support", 0.0) + (0.35 * emotional_salience * max(0.0, recent_valence_avg)) + (0.28 * social_norm) + (0.16 * serotonin_level)
        base["challenge"] = base.get("challenge", 0.0) + (0.35 * emotional_salience * max(0.0, -recent_valence_avg))
        base["suggest"] = base.get("suggest", 0.0) + (0.22 * competence) + (0.14 * reward_level) - (0.2 * stress_level)
        base["neutral"] = base.get("neutral", 0.0) + (0.3 * stress_level) + (0.1 * (1.0 - emotional_salience))
        base["refuse"] = base.get("refuse", 0.0) + (0.4 * stress_level * (1.0 - social_norm)) + (0.22 * max(0.0, -recent_valence_avg))

        if stress_level > 0.6:
            pressure = (stress_level - 0.6) / 0.4
            base["refuse"] = base.get("refuse", 0.0) + (0.55 * pressure)
            base["neutral"] = base.get("neutral", 0.0) + (0.35 * pressure)
            base["support"] = base.get("support", 0.0) - (0.25 * pressure)
        elif stress_level < 0.5:
            calm = (0.5 - stress_level) / 0.5
            base["support"] = base.get("support", 0.0) + (0.3 * calm)
            base["suggest"] = base.get("suggest", 0.0) + (0.15 * calm)
            base["refuse"] = base.get("refuse", 0.0) - (0.18 * calm)

        if mood_valence < -0.2:
            stress_push = abs(mood_valence) * (0.2 + 0.1 * mood_arousal)
            base["refuse"] = base.get("refuse", 0.0) + stress_push
            base["neutral"] = base.get("neutral", 0.0) + (0.75 * stress_push)
            base["support"] = base.get("support", 0.0) - (0.45 * stress_push)
        elif mood_valence > 0.2:
            prosocial = mood_valence * (0.18 + 0.08 * (1.0 - mood_arousal))
            base["support"] = base.get("support", 0.0) + prosocial
            base["suggest"] = base.get("suggest", 0.0) + (0.8 * prosocial)

        rejection_conf = max(
            confidence
            for statement, confidence in belief_map.items()
            if "reaching out often leads to rejection" in statement
        ) if any("reaching out often leads to rejection" in statement for statement in belief_map) else 0.0
        support_conf = max(
            confidence
            for statement, confidence in belief_map.items()
            if "supportive connections are available" in statement
        ) if any("supportive connections are available" in statement for statement in belief_map) else 0.0
        mastery_conf = max(
            confidence
            for statement, confidence in belief_map.items()
            if "persistent effort helps me solve challenges" in statement
        ) if any("persistent effort helps me solve challenges" in statement for statement in belief_map) else 0.0
        unsafe_conf = max(
            confidence
            for statement, confidence in belief_map.items()
            if "environment often feels unsafe" in statement
        ) if any("environment often feels unsafe" in statement for statement in belief_map) else 0.0

        if rejection_conf > 0.4:
            base["support"] = base.get("support", 0.0) - (0.22 * rejection_conf)
            base["neutral"] = base.get("neutral", 0.0) + (0.12 * rejection_conf)
        if support_conf > 0.4:
            base["support"] = base.get("support", 0.0) + (0.24 * support_conf)
            base["refuse"] = base.get("refuse", 0.0) - (0.1 * support_conf)
        if mastery_conf > 0.45:
            base["suggest"] = base.get("suggest", 0.0) + (0.16 * mastery_conf)
            base["challenge"] = base.get("challenge", 0.0) + (0.1 * mastery_conf)
        if unsafe_conf > 0.45:
            base["neutral"] = base.get("neutral", 0.0) + (0.18 * unsafe_conf)
            base["refuse"] = base.get("refuse", 0.0) + (0.12 * unsafe_conf)

        for action in list(base.keys()):
            base[action] = max(self.model.min_prob, min(self.model.max_prob, base[action]))

        total = sum(base.values())
        if total > 0:
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

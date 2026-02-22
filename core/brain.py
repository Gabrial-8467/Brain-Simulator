import random
from collections import deque
import re

from core.identity import DynamicIdentity
from core.development import DynamicDevelopment
from core.self_reflection import SelfReflection

from cognition.autobiographical_memory import AutobiographicalMemory
from cognition.narrative_engine import NarrativeEngine

from learning.appraisal_engine import AppraisalEngine
from learning.similarity_engine import SimilarityEngine

from decision.strategic_planner import StrategicPlanner


class VirtualBrain:

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        chemical_configs: dict,
        interaction_matrix: dict = None,
        decision_engine=None,
        feedback_multiplier: float = 1.0,
        deterministic=False
    ):

        self.deterministic = deterministic
        self.feedback_multiplier = feedback_multiplier
        self.decision_engine = decision_engine

        # Core Self
        self.identity = DynamicIdentity()
        self.development = DynamicDevelopment()

        # Memory
        self.autobiography = AutobiographicalMemory()
        self.narrative_engine = NarrativeEngine()

        # Learning
        self.similarity_engine = SimilarityEngine()
        self.appraisal_engine = AppraisalEngine(
            similarity_engine=self.similarity_engine
        )

        # Planning
        self.strategic_planner = StrategicPlanner(
            appraisal_engine=self.appraisal_engine,
            similarity_engine=self.similarity_engine,
            identity=self.identity
        )

        # Counterfactual reflection
        self.self_reflection = SelfReflection(
            appraisal_engine=self.appraisal_engine,
            similarity_engine=self.similarity_engine,
            identity=self.identity
        )

        # Cognitive Development
        self.experience = 0.0
        self.intelligence = 0.5
        self.wisdom = 0.0

        self.last_prediction_error = 1.0
        self.previous_chem_snapshot = {}

        # Cognitive Profile
        self.risk_tolerance = 0.5
        self.risk_adapt_rate = 0.01

        self.fatigue = 0
        self.fatigue_recovery_rate = 0.98
        self.reflection_decay_rate = 0.995
        self.max_reflection_influence = 0.05

        # Stress / Resilience
        self.stress_accumulator = 0
        self.recovery_counter = 0
        self.stress_threshold = 50
        self.burnout_threshold = 75
        self.resilience_growth_rate = 0.01
        self.resilience_damage_rate = 0.02

        self.interaction_matrix = interaction_matrix or {}
        self.step_counter = 0
        self.recent_perceptions = deque(maxlen=50)
        self.concept_memory = {}
        self.concept_aliases = {
            "finger": "fingers",
            "fingers": "fingers",
            "hand": "hand",
            "cat": "cat",
            "cats": "cat",
            "dog": "dog",
            "dogs": "dog",
            "face": "face",
            "eyes": "eyes",
            "eye": "eyes",
            "camera": "camera",
            "light": "light",
            "dark": "darkness",
            "bright": "brightness",
            "person": "person",
            "people": "person",
        }
        self.development_stage = "baby"
        self.stage_learning_multipliers = {
            "baby": 0.7,
            "child": 1.0,
            "teen": 1.25,
            "adult": 1.5,
        }

        # Chemicals
        self.chemicals = {}
        for name, config in chemical_configs.items():
            self.chemicals[name] = {
                "value": config["baseline"],
                "baseline": config["baseline"],
                "min": config["min"],
                "max": config["max"],
                "decay": config["decay"],
                "noise": config["noise"]
            }

    # ==========================================================
    # MAIN TICK LOOP
    # ==========================================================

    def tick(self):

        self._apply_interactions()
        self._apply_homeostasis()
        self._apply_noise()
        self._clamp()

        regret = 0
        decision_output = None

        if self.decision_engine:

            probabilities = self.decision_engine.model.compute(self.get_state())

            competence = self.identity.get("competence")
            social_value = self.identity.get("social_value")
            resilience = self.identity.get("resilience")
            maturity = self.development.maturity

            maturity_influence = min(
                maturity * 0.02,
                self.max_reflection_influence
            )

            for action in probabilities:

                probabilities[action] += competence * 0.02
                probabilities[action] += social_value * 0.01
                probabilities[action] += resilience * 0.01
                probabilities[action] += maturity_influence

                probabilities[action] *= (0.8 + self.risk_tolerance * 0.4)
                probabilities[action] *= (1 - self.fatigue * 0.25)

            total = sum(probabilities.values())
            if total > 0:
                for k in probabilities:
                    probabilities[k] /= total

            chosen_action = self.strategic_planner.choose_action(
                brain=self,
                probabilities=probabilities
            )

            decision_output = self.decision_engine.execute_action(
                chosen_action,
                self.get_state()
            )

            feedback = decision_output.get("feedback", {})
            self._apply_decision_feedback(feedback)
            self._clamp()

            regret = self.self_reflection.reflect_on_decision(
                chosen_action=chosen_action,
                available_actions=list(probabilities.keys()),
                current_state=self.get_state()
            )

            self._adapt_risk(regret)

        # Core updates
        self._update_resilience()
        self._update_reflection_balance()

        self.development.reflect(self.identity.get("intelligence"))
        self.development.update()

        if self.fatigue < 0.6:
            self.identity.update()

        self._update_cognitive_growth(regret)
        self._encode_autobiography()

        self.step_counter += 1
        return decision_output

    # ==========================================================
    # EVENT INJECTION
    # ==========================================================

    def inject_event(self, effects: dict, event_type=None, source=None, tags=None):

        resilience = self.identity.get("resilience")
        maturity = self.development.maturity

        predicted = self.appraisal_engine.predict_emotion(
            event_type,
            current_state=self.get_state()
        )

        anticipation_strength = 0.5 + (maturity * 0.5)

        for chem, delta in predicted.items():
            if chem in self.chemicals:
                self.chemicals[chem]["value"] += delta * anticipation_strength

        previous_state = {
            name: self.chemicals[name]["value"]
            for name in self.chemicals
        }

        identity_before = self.identity.get_snapshot()

        if event_type == "praise":
            self.identity.add_evidence("competence", 1)
            self.identity.add_evidence("social_value", 1)

        elif event_type == "criticism":
            self.identity.add_evidence("competence", -1)
            self.identity.add_evidence("social_value", -1)

        elif event_type == "failure":
            self.identity.add_evidence("competence", -1)

        elif event_type == "success":
            self.identity.add_evidence("competence", 1)
            self.identity.add_evidence("intelligence", 1)

        for chem, delta in effects.items():
            if chem in self.chemicals:
                if chem in ["dopamine", "serotonin"] and delta < 0:
                    delta *= (1 - resilience * 0.5)
                if chem == "cortisol" and resilience > 0:
                    delta *= (1 - resilience * 0.4)

                self.chemicals[chem]["value"] += delta

        self._clamp()

        chemical_delta = {
            name: self.chemicals[name]["value"] - previous_state[name]
            for name in self.chemicals
        }

        identity_after = self.identity.get_snapshot()
        identity_change = sum(
            identity_after[k] - identity_before.get(k, 0)
            for k in identity_after
        )

        outcome_value = 1 if identity_change >= 0 else -1

        self.appraisal_engine.update_emotional_learning(
            event_type,
            chemical_delta,
            outcome_value
        )

        self.similarity_engine.record_event_profile(
            event_type,
            chemical_delta,
            identity_after
        )

    # ==========================================================
    # DEVELOPMENT MODEL
    # ==========================================================

    def _update_cognitive_growth(self, regret):
        growth_multiplier = self.stage_learning_multipliers.get(self.development_stage, 1.0)

        volatility = sum(
            abs(self.chemicals[k]["value"] - self.previous_chem_snapshot.get(k, 0))
            for k in self.chemicals
        )

        novelty_factor = 1 / (1 + self.experience * 0.1)

        stress_recovered = (
            self.stress_accumulator > 0 and
            self.recovery_counter > 3
        )

        # EXPERIENCE
        experience_gain = (
            volatility * 0.0008 +
            abs(regret) * 0.008 +
            (0.02 if stress_recovered else 0)
        ) * novelty_factor * growth_multiplier

        self.experience += experience_gain

        # INTELLIGENCE
        prediction_error = abs(regret)
        stability = max(0, self.last_prediction_error - prediction_error)

        intelligence_gain = (
            stability * 0.01 +
            self.development.reflection_depth * 0.0003
        ) * growth_multiplier

        self.intelligence += intelligence_gain
        self.intelligence = max(0.3, min(1.0, self.intelligence))

        self.last_prediction_error = prediction_error

        # WISDOM
        wisdom_gain = 0

        if regret > 0 and stability > 0:
            wisdom_gain += regret * 0.003 * growth_multiplier

        if stress_recovered:
            wisdom_gain += 0.01 * growth_multiplier

        if self.identity.get("resilience") > 0.6 and regret > 0:
            wisdom_gain += 0.002 * growth_multiplier

        self.wisdom = min(1.0, self.wisdom + wisdom_gain)

        # MATURITY (smooth transition)
        maturity_target = (
            self.experience * 0.15 +
            self.intelligence * 0.35 +
            self.wisdom * 0.35 +
            self.development.reflection_depth * 0.0004
        )

        self.development.maturity += (
            (maturity_target - self.development.maturity) * 0.05
        )

        self.development.maturity = max(
            0, min(1.0, self.development.maturity)
        )

        self.previous_chem_snapshot = {
            k: self.chemicals[k]["value"]
            for k in self.chemicals
        }

    # ==========================================================
    # PERCEPTION INTAKE
    # ==========================================================

    def get_stt_languages(self):
        # Brain-controlled listening languages.
        return ("en-US", "en-IN")

    def get_language_instruction(self):
        return "Reply in English."

    def describe_visual_scene(self, brightness):
        if brightness < 45:
            return "camera observation: dark scene"
        if brightness > 170:
            return "camera observation: bright scene"
        return "camera observation: normal lighting"

    def observe_perception(self, modality: str, content: str, source="system"):

        modality = (modality or "").strip().lower()
        content = (content or "").strip()

        if not modality or not content:
            return

        effects = {}
        event_type = "observation"

        # Basic interpretation layer from raw perception to emotional effect.
        if modality == "hearing":
            event_type = "social_contact"
            effects = {"oxytocin": 0.4, "dopamine": 0.2}
        elif modality == "speaking":
            event_type = "expression"
            effects = {"oxytocin": 0.3, "cortisol": -0.2}
        elif modality == "vision":
            event_type = "novel_stimulus"
            effects = {"dopamine": 0.25}
        else:
            effects = {"dopamine": 0.1}

        if "thank" in content.lower():
            effects["oxytocin"] = effects.get("oxytocin", 0) + 0.5
            event_type = "social_reward"

        self.recent_perceptions.append({
            "modality": modality,
            "content": content,
            "source": source
        })
        self._learn_from_perception(modality=modality, content=content, source=source)

        self.inject_event(
            effects=effects,
            event_type=event_type,
            source=source,
            tags=[modality, "perception"]
        )

        # Persist interpreted perception into autobiographical memory.
        self.autobiography.record_event(
            description=f"perception:{modality}:{event_type}",
            chemicals={k: v["value"] for k, v in self.chemicals.items()},
            identity_snapshot=self.identity.get_snapshot(),
            metadata={
                "source": source,
                "content": content[:220],
                "effects": effects,
            }
        )

    def _extract_concepts(self, text):
        tokens = re.findall(r"[a-zA-Z]+", (text or "").lower())
        concepts = []
        for tok in tokens:
            if len(tok) < 3:
                continue
            mapped = self.concept_aliases.get(tok)
            if mapped:
                concepts.append(mapped)
        return concepts

    def _learn_from_perception(self, modality, content, source):
        concepts = self._extract_concepts(content)
        if not concepts:
            return

        now_step = self.step_counter
        # Baby learns slowly; adult consolidates faster.
        stage_rate = {
            "baby": 0.05,
            "child": 0.07,
            "teen": 0.09,
            "adult": 0.11,
        }.get(self.development_stage, 0.07)

        for concept in concepts:
            entry = self.concept_memory.get(concept, {
                "count": 0,
                "strength": 0.0,
                "first_seen_step": now_step,
                "last_seen_step": now_step,
                "modalities": {}
            })

            entry["count"] += 1
            # Incremental concept learning that scales with maturity stage.
            entry["strength"] = min(1.0, entry["strength"] + stage_rate)
            entry["last_seen_step"] = now_step
            entry["modalities"][modality] = entry["modalities"].get(modality, 0) + 1

            self.concept_memory[concept] = entry

    def _compute_development_stage(self):
        m = self.development.maturity
        e = self.experience

        if m < 0.25 and e < 0.8:
            return "baby"
        if m < 0.5 and e < 2.5:
            return "child"
        if m < 0.75 and e < 5.0:
            return "teen"
        return "adult"

    def get_top_concepts(self, n=10):
        if not self.concept_memory:
            return []
        ranked = sorted(
            self.concept_memory.items(),
            key=lambda kv: (kv[1]["strength"], kv[1]["count"]),
            reverse=True
        )
        return [
            {
                "concept": concept,
                "count": data["count"],
                "strength": round(data["strength"], 3),
                "modalities": data["modalities"],
            }
            for concept, data in ranked[:n]
        ]

    def regulate_speech(self, text: str):
        """
        Final speech-control layer owned by the brain.
        Shapes response style using current internal state.
        """
        if not text:
            return text

        controlled = text.strip()
        state = self.get_state()
        fatigue = state.get("fatigue", 0.0)
        cortisol = state.get("cortisol", 50.0)
        oxytocin = state.get("oxytocin", 50.0)
        stage = state.get("development_stage", "baby")

        # Tired/stressed: keep speech concise and simple.
        if fatigue > 0.7 or cortisol > 70:
            parts = controlled.split(".")
            controlled = parts[0].strip()
            if not controlled.endswith((".", "!", "?")):
                controlled += "."

        # Developmental language shaping from simple to mature.
        if stage == "baby":
            words = controlled.split()
            controlled = " ".join(words[:18]).strip()
            if controlled and not controlled.endswith((".", "!", "?")):
                controlled += "."
        elif stage == "child":
            words = controlled.split()
            controlled = " ".join(words[:28]).strip()
            if controlled and not controlled.endswith((".", "!", "?")):
                controlled += "."

        # Avoid trailing conjunctions from truncation.
        trailing_bad = {"and", "or", "but", "so", "because"}
        tokens = controlled.rstrip(".!? ").split()
        if tokens and tokens[-1].lower() in trailing_bad:
            tokens = tokens[:-1]
            if tokens:
                controlled = " ".join(tokens).strip()
                if not controlled.endswith((".", "!", "?")):
                    controlled += "."

        # Warm social state: keep tone connected.
        if oxytocin > 70 and not any(
            controlled.lower().startswith(prefix)
            for prefix in ("i ", "we ", "let", "you're", "you are")
        ):
            controlled = "I hear you. " + controlled

        return controlled

    # ==========================================================
    # INTERNAL SYSTEMS
    # ==========================================================

    def _adapt_risk(self, regret):

        if regret > 0:
            self.risk_tolerance -= self.risk_adapt_rate
        else:
            self.risk_tolerance += self.risk_adapt_rate * 0.5

        self.risk_tolerance += self.wisdom * 0.003
        self.risk_tolerance = max(0.1, min(0.9, self.risk_tolerance))

    def _update_reflection_balance(self):

        self.development.reflection_depth *= self.reflection_decay_rate

        if self.development.reflection_depth > 50:
            self.fatigue += 0.01

        cortisol = self.chemicals.get("cortisol", {}).get("value", 0)

        if cortisol < self.stress_threshold:
            self.fatigue *= self.fatigue_recovery_rate

        self.fatigue = max(0, min(self.fatigue, 1))

    def _update_resilience(self):

        cortisol = self.chemicals.get("cortisol", {}).get("value", 0)

        if cortisol > self.stress_threshold:
            self.stress_accumulator += 1
            self.recovery_counter = 0
        else:
            self.recovery_counter += 1

        if 1 <= self.stress_accumulator <= 4 and self.recovery_counter > 3:
            self.identity.add_evidence(
                "resilience",
                self.resilience_growth_rate
            )
            self.stress_accumulator = 0

        if cortisol > self.burnout_threshold:
            self.identity.add_evidence(
                "resilience",
                -self.resilience_damage_rate
            )

    def _apply_homeostasis(self):

        for data in self.chemicals.values():
            current = data["value"]
            baseline = data["baseline"]
            decay = data["decay"]
            data["value"] = current + (baseline - current) * decay

    def _apply_noise(self):

        if self.deterministic:
            return

        for data in self.chemicals.values():
            variation = random.uniform(-data["noise"], data["noise"])
            data["value"] += variation

    def _apply_interactions(self):

        deltas = {}

        for source, targets in self.interaction_matrix.items():

            if source not in self.chemicals:
                continue

            source_value = self.chemicals[source]["value"]

            for target, weight in targets.items():

                if target not in self.chemicals:
                    continue

                deltas[target] = deltas.get(target, 0) + source_value * weight

        for target, delta in deltas.items():
            self.chemicals[target]["value"] += delta

    def _apply_decision_feedback(self, feedback: dict):

        for chem, delta in feedback.items():
            if chem in self.chemicals:
                self.chemicals[chem]["value"] += (
                    delta * self.feedback_multiplier
                )

    def _clamp(self):

        for data in self.chemicals.values():
            data["value"] = max(data["min"], min(data["value"], data["max"]))

    def _encode_autobiography(self):

        self.autobiography.record_event(
            description="cycle_step",
            chemicals={k: v["value"] for k, v in self.chemicals.items()},
            identity_snapshot=self.identity.get_snapshot()
        )

        if self.step_counter % 25 == 0:

            recent = self.autobiography.get_recent_events(100)
            self.narrative_engine.update_narrative(recent)

            narrative_bias = self.narrative_engine.get_identity_bias()

            for trait, delta in narrative_bias.items():
                self.identity.add_evidence(trait, delta * 0.1)

    # ==========================================================
    # HUMAN RESPONSE LATENCY
    # ==========================================================

    def get_response_latency(self):

        cortisol = self.chemicals["cortisol"]["value"]
        dopamine = self.chemicals["dopamine"]["value"]

        emotional_weight = (
            cortisol * 0.0025 -
            dopamine * 0.0008
        )

        cognitive_load = (
            self.fatigue * 0.5 +
            emotional_weight
        )

        maturity_effect = (1 - self.development.maturity) * 0.15

        base_time = 0.25  # faster base thinking

        latency = base_time + (cognitive_load * 1.2) + maturity_effect

        return max(0.15, min(2.2, latency))


    # ==========================================================
    # STATE EXPORT
    # ==========================================================

    def get_state(self):
        self.development_stage = self._compute_development_stage()

        state = {name: data["value"] for name, data in self.chemicals.items()}

        state.update({
            f"identity_{k}": v
            for k, v in self.identity.get_snapshot().items()
        })

        state.update({
            f"development_{k}": v
            for k, v in self.development.get_snapshot().items()
        })

        state.update({
            "fatigue": self.fatigue,
            "self_narrative": self.narrative_engine.get_current_narrative(),
            "wisdom": self.self_reflection.get_wisdom()
        })

        state["intelligence"] = self.intelligence
        state["experience"] = self.experience
        state["development_stage"] = self.development_stage
        state["recent_perceptions"] = list(self.recent_perceptions)[-5:]
        state["learned_concepts"] = self.get_top_concepts(8)

        return state

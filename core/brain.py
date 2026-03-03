from __future__ import annotations

import os
import random
import re
import time
from collections import deque
from dataclasses import asdict
from typing import Any

from core.attention import GlobalWorkspace, Thought
from core.consciousness import Consciousness
from core.development import DynamicDevelopment
from core.identity import DynamicIdentity
from core.internal_thoughts import generate_spontaneous
from core.self_reflection import SelfReflection

from cognition.autobiographical_memory import AutobiographicalMemory
from cognition.narrative_engine import NarrativeEngine

from decision.strategic_planner import StrategicPlanner
from learning.appraisal_engine import AppraisalEngine
from learning.similarity_engine import SimilarityEngine
from memory.memory_manager import MemoryManager


class VirtualBrain:
    def __init__(
        self,
        chemical_configs: dict,
        interaction_matrix: dict = None,
        decision_engine=None,
        feedback_multiplier: float = 1.0,
        deterministic: bool = False,
        memory_storage_path: str | None = None,
    ):
        self.deterministic = deterministic
        self.feedback_multiplier = feedback_multiplier
        self.decision_feedback_scale = 0.45
        self.decision_engine = decision_engine

        self.identity = DynamicIdentity()
        self.development = DynamicDevelopment()
        self.consciousness = Consciousness()

        self.autobiography = AutobiographicalMemory()
        self.narrative_engine = NarrativeEngine()

        self.similarity_engine = SimilarityEngine()
        self.appraisal_engine = AppraisalEngine(similarity_engine=self.similarity_engine)
        self.strategic_planner = StrategicPlanner(
            appraisal_engine=self.appraisal_engine,
            similarity_engine=self.similarity_engine,
            identity=self.identity,
        )
        self.self_reflection = SelfReflection(
            appraisal_engine=self.appraisal_engine,
            similarity_engine=self.similarity_engine,
            identity=self.identity,
        )
        self.memory_storage_path = (
            memory_storage_path
            or os.getenv("BRAIN_EVENT_MEMORY_PATH")
            or os.getenv("BRAIN_MEMORY_PATH")
            or "memory_events.json"
        )
        self.memory_manager = MemoryManager(storage_path=self.memory_storage_path)
        # Ensure persistence file exists from startup.
        self.memory_manager.storage.save()

        self.current_focus: Thought | None = None
        self.experience = 0.0
        self.intelligence = 0.5
        self.wisdom = 0.0

        self.last_prediction_error = 1.0
        self.previous_chem_snapshot = {}
        self.risk_tolerance = 0.5
        self.risk_adapt_rate = 0.02
        self.homeostasis_target = 60.0
        self.homeostasis_rate = 0.04
        self.homeostasis_max_delta = 1.0
        self.homeostasis_gentle_upward_max = 0.5
        self.cortisol_decay_baseline = 45.0
        self.serotonin_regulation_baseline = 60.0
        self.homeostasis_baselines = {
            "dopamine": 65.0,
            "cortisol": 45.0,
            "oxytocin": 65.0,
            "serotonin": 62.0,
        }
        self.recall_responses = {
            "positive": {
                "dopamine": 1.2,
                "cortisol": -0.3,
                "oxytocin": 0.4,
                "serotonin": 0.3,
            },
            "threat": {
                "dopamine": -0.3,
                "cortisol": 1.5,
                "oxytocin": -0.5,
                "serotonin": -0.4,
            },
            "failure": {
                "dopamine": -0.5,
                "cortisol": 0.8,
                "oxytocin": 0.0,
                "serotonin": -0.6,
            },
            "social_pain": {
                "dopamine": -0.4,
                "cortisol": 0.6,
                "oxytocin": -1.2,
                "serotonin": -0.5,
            },
            "neutral": {
                "dopamine": 0.2,
                "cortisol": 0.0,
                "oxytocin": 0.0,
                "serotonin": 0.0,
            },
        }

        self.fatigue = 0.0
        self.fatigue_recovery_rate = 0.98
        self.reflection_decay_rate = 0.995
        self.max_reflection_influence = 0.05

        self.stress_accumulator = 0
        self.recovery_counter = 0
        self.stress_threshold = 50
        self.burnout_threshold = 75
        self.resilience_growth_rate = 0.01
        self.resilience_damage_rate = 0.02
        self.social_decay_rate = 0.001
        self.social_decay_floor = 0.0002
        self.social_gain_hold_steps = 8

        self.interaction_matrix = interaction_matrix or {}
        self.step_counter = 0
        self._step_perception_valences: list[float] = []
        self._social_decay_hold_counter = 0
        self._high_emotion_window = deque(maxlen=10)
        self._decision_debug: dict[str, Any] = {}
        self._high_stress_steps = 0
        self._low_serotonin_steps = 0
        self._step_adversity_intensity = 0.0
        self._comfort_steps = 0
        self._last_maturity = 0.0
        self._last_concept_count = 0
        self._concept_stagnation_steps = 0
        self._last_concept_warning_step = -1000
        self.recent_perceptions = deque(maxlen=50)
        self.scene_memory = deque(maxlen=25)
        self.novelty_memory = deque(maxlen=50)
        self._scene_counts: dict[str, int] = {}
        self.concept_memory = {}
        self.stopwords = {
            "i", "me", "my", "mine", "myself", "am", "being",
            "a", "an", "the", "is", "are", "was", "were",
            "for", "to", "and", "it", "that", "of", "in",
            "nothing", "something", "with", "be", "have",
            "has", "had", "do", "did", "at", "by", "from",
            "on", "or", "but", "not", "no", "so", "if", "as",
            "you", "your",
            "this", "its", "near", "under",
            "object", "objects", "attribute", "attributes", "relation", "relations",
            "motion", "confidence",
            "speaker", "text", "keyword", "keywords", "sentiment", "prosody",
            "objects", "relations",
        }
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
            "man": "person",
            "woman": "person",
            "child": "person",
            "kitten": "cat",
            "puppy": "dog",
            "room": "room",
            "table": "table",
            "chair": "chair",
            "screen": "screen",
            "monitor": "screen",
            "phone": "phone",
            "bottle": "bottle",
            "book": "book",
            "window": "window",
            "door": "door",
            "left": "left",
            "right": "right",
            "near": "near",
            "behind": "behind",
            "front": "front",
            "red": "red",
            "blue": "blue",
            "green": "green",
            "small": "small",
            "large": "large",
        }
        self.development_stage = "child"
        self.stage_learning_multipliers = {
            "child": 1.0,
            "teen": 1.25,
            "adult": 1.5,
        }
        self.reflection_interval = 50
        self.narrative_update_interval = 25
        self._reflection_consciousness_boost = 0.0
        self.perceptions_since_reflection = 0
        self.complacency_counter = 0
        self._narrative_milestone_index = -1
        self._last_narrative_update_step = -1000

        self.chemicals = {}
        for name, config in chemical_configs.items():
            self.chemicals[name] = {
                "value": config["baseline"],
                "baseline": config["baseline"],
                "min": config["min"],
                "max": config["max"],
                "decay": config["decay"],
                "noise": config["noise"],
            }
        self._last_maturity = self.development.maturity

    def tick(self):
        decision_output = None
        regret = 0.0
        prev_maturity = self.development.maturity

        self._apply_interactions()
        self._apply_homeostasis()
        self._apply_noise()
        self._clamp()

        serotonin = self.chemicals.get("serotonin", {}).get("value", 0.0)
        cortisol = self.chemicals.get("cortisol", {}).get("value", 0.0)
        if serotonin < 55.0:
            self._low_serotonin_steps += 1
        else:
            self._low_serotonin_steps = 0
        if cortisol > 60.0:
            self._high_stress_steps += 1
        else:
            self._high_stress_steps = 0

        self._update_resilience()
        self._update_reflection_balance()

        self.development.reflect(self.identity.get("intelligence"))
        self.development.update()

        if self.fatigue < 0.6:
            self.identity.update()
        self._apply_social_value_decay()
        self._enforce_identity_floors()

        self._encode_autobiography()

        generate_spontaneous(self)
        self.current_focus = GlobalWorkspace.select()
        focus_emotional = float(getattr(self.current_focus, "emotional_weight", 0.0) or 0.0)
        threshold = 0.7
        self._high_emotion_window.append(bool(self.current_focus and focus_emotional > threshold))
        high_emotion_hits = sum(1 for flag in self._high_emotion_window if flag)

        self._decision_debug = {
            "engine_available": bool(self.decision_engine),
            "focus_present": bool(self.current_focus),
            "focus_emotional_weight": round(focus_emotional, 4),
            "emotional_threshold": threshold,
            "high_emotion_hits_last_10": high_emotion_hits,
            "high_stress_steps": self._high_stress_steps,
            "decision_path": "none",
            "forced_fallback": False,
            "system_recall_feedback_suppressed": False,
            "memory_feedback_suppressed": False,
            "memory_recall_type": None,
            "memory_recall_scale": 0.0,
        }

        if self.current_focus and self.current_focus.source == "memory":
            recall_effect = self._apply_memory_recall_response(self.current_focus)
            self._decision_debug["memory_recall_type"] = recall_effect.get("type")
            self._decision_debug["memory_recall_scale"] = recall_effect.get("scale", 0.0)
            if recall_effect.get("applied"):
                self._clamp()

        gate_pass = high_emotion_hits >= 3
        self._decision_debug["gate_pass"] = gate_pass

        recent_valence_avg = 0.0
        if self._step_perception_valences:
            recent_valence_avg = sum(self._step_perception_valences) / len(self._step_perception_valences)

        if self.decision_engine and self.current_focus and gate_pass:
            decision_output = self.decision_engine.decide(
                self.current_focus,
                state=self.get_state(),
                recent_valence_avg=recent_valence_avg,
            )
            self._decision_debug["decision_path"] = "model"

        if (
            decision_output is None
            and self.current_focus
            and (high_emotion_hits >= 3 or self._high_stress_steps >= 3)
        ):
            decision_output = self._build_fallback_decision(self.current_focus)
            self._decision_debug["decision_path"] = "fallback"
            self._decision_debug["forced_fallback"] = True

        if decision_output:
            feedback = decision_output.get("feedback", {})
            if self.current_focus and self.current_focus.source == "memory":
                feedback = {}
                self._decision_debug["memory_feedback_suppressed"] = True
            if self._is_system_recall_focus(self.current_focus):
                feedback = {}
                self._decision_debug["system_recall_feedback_suppressed"] = True
            if feedback:
                self._apply_decision_feedback(feedback)
                self._clamp()

            action = decision_output.get("action")
            probabilities = decision_output.get("probabilities", {})
            if action:
                regret = self.self_reflection.reflect_on_decision(
                    chosen_action=action,
                    available_actions=list(probabilities.keys()),
                    current_state=self.get_state(),
                )
                self.self_reflection.propose_reflection_thought(self, action, regret)

        self._update_cognitive_growth(regret)
        stage_changed = self._update_stage_transition()
        self._periodic_reflection()
        if not stage_changed and (self.step_counter % self.narrative_update_interval == 0):
            self._refresh_narrative(force=True)
        self.consciousness.compute_score(self)
        if self._reflection_consciousness_boost > 0.0:
            self.consciousness.score = min(1.0, self.consciousness.score + self._reflection_consciousness_boost)
            self._reflection_consciousness_boost *= 0.9
        self.consciousness.modulate_risk(self, self.consciousness.score)
        self.consciousness.update_narrative(self, self.consciousness.score)
        self._apply_narrative_milestones()
        self.development.maturity = max(prev_maturity, self.development.maturity)
        self._enforce_identity_floors()
        self._monitor_concept_growth()

        self.step_counter += 1
        self.memory_manager.flush_pending()
        self._step_perception_valences = []
        self._step_adversity_intensity = 0.0
        return decision_output

    def perceive(self, event: Any) -> None:
        """Process a meaningful experience event generated by the environment."""
        def _read(name: str, default: Any):
            if hasattr(event, name):
                return getattr(event, name)
            if isinstance(event, dict):
                return event.get(name, default)
            return default

        modality = str(_read("modality", "experience")).strip().lower() or "experience"
        category = str(_read("category", "")).strip().lower()
        content = str(_read("content", "")).strip()
        valence = float(_read("valence", 0.0))
        intensity = float(_read("intensity", 0.0))
        source = str(_read("source", "simulated"))
        timestamp = float(_read("timestamp", 0.0))
        scene_input = _read("scene", {}) or {}

        if not content:
            content = f"{modality} event"

        valence = max(-1.0, min(1.0, valence))
        intensity = max(0.0, min(1.0, intensity))
        self._step_perception_valences.append(valence)
        if category in {"failure", "criticism", "threat_detected"}:
            self._step_adversity_intensity += intensity

        if category in {"greeted", "praise"} and valence > 0:
            self._social_decay_hold_counter = max(self._social_decay_hold_counter, self.social_gain_hold_steps)
        elif category == "voice_recognized" and valence > 0.2:
            self._social_decay_hold_counter = max(self._social_decay_hold_counter, self.social_gain_hold_steps)
        self._apply_social_value_event_impact(category, intensity)

        scene = self._analyze_perception(
            modality=modality,
            content=f"{category} {content}",
            valence=valence,
            provided_scene=scene_input,
        )
        self.recent_perceptions.append(
            {
                "modality": modality,
                "content": content,
                "category": category,
                "source": source,
                "valence": valence,
                "intensity": intensity,
                "timestamp": timestamp,
                "scene": scene,
            }
        )
        self.perceptions_since_reflection += 1
        self.scene_memory.append(scene)
        self.novelty_memory.append(
            {
                "modality": modality,
                "novelty": scene.get("novelty", 0.0),
                "timestamp": timestamp or time.time(),
            }
        )
        self._learn_from_perception(
            modality,
            f"{category} {content}",
            source=source,
            scene=scene,
            category=category,
        )

        effects = self._effects_from_event(
            modality=modality,
            category=category,
            valence=valence,
            intensity=intensity,
        )

        self.inject_event(
            effects=effects,
            event_type=category or "experience",
            source=source,
            tags=[modality, "perception_event", category or "experience"],
        )

        metadata = {}
        if hasattr(event, "__dataclass_fields__"):
            metadata = asdict(event)
        elif isinstance(event, dict):
            metadata = dict(event)

        self.autobiography.record_event(
            description=f"perceived_{modality}_{category or 'event'}: {content}",
            chemicals={k: v["value"] for k, v in self.chemicals.items()},
            identity_snapshot=self.identity.get_snapshot(),
            metadata=metadata,
        )
        self.memory_manager.create_memory(
            memory_type=f"perception_{modality}",
            content={
                "category": category or "event",
                "content": content,
                "valence": valence,
                "intensity": intensity,
                "source": source,
                "timestamp": timestamp or time.time(),
                "scene": scene,
            },
            metadata={
                "development_stage": self.development_stage,
                "step_counter": self.step_counter,
            },
        )
        self.autobiography.propose_memory_thought(self)

        self.development.observe_event(category or modality, {k: v["value"] for k, v in self.chemicals.items()})

        event_thought = Thought(
            content=f"I experienced {modality}::{category or 'event'}: {content}",
            source="perception",
            emotional_weight=min(1.0, abs(valence) * 0.7 + scene.get("salience", 0.0) * 0.3),
            novelty=min(1.0, scene.get("novelty", 0.0)),
            relevance_to_goals=0.25 + (0.2 if category in {"success", "failure", "praise"} else 0.0),
            metadata={
                "category": category,
                "valence": valence,
                "intensity": intensity,
                "modality": modality,
                "scene": scene,
            },
        )
        GlobalWorkspace.post(event_thought)

    def _effects_from_event(self, modality: str, category: str, valence: float, intensity: float) -> dict:
        positive = max(0.0, valence)
        negative = max(0.0, -valence)

        effects = {
            "dopamine": (1.2 * positive - 0.8 * negative) * intensity,
            "oxytocin": (1.0 * positive - 0.3 * negative) * intensity,
            "serotonin": (0.9 * positive - 0.5 * negative) * intensity,
            "cortisol": (2.2 * negative - 0.8 * positive) * intensity,
        }

        if category == "praise":
            effects["dopamine"] += 1.0 * intensity
            effects["oxytocin"] += 1.5 * intensity
            effects["serotonin"] += 1.2 * intensity
            effects["cortisol"] -= 0.9 * intensity
        elif category == "greeted":
            effects["oxytocin"] += 2.0 * intensity
            effects["serotonin"] += 0.5 * intensity
            effects["cortisol"] -= 0.5 * intensity
        elif category == "success":
            effects["dopamine"] += 1.5 * intensity
            effects["serotonin"] += 0.8 * intensity
            effects["cortisol"] -= 0.6 * intensity
        elif category == "face_recognized":
            effects["oxytocin"] += 1.5 * intensity
            effects["cortisol"] -= 0.35 * intensity

        if category in {"criticism", "failure", "loud_noise", "threat_detected"}:
            effects["cortisol"] += 2.8 * intensity
            effects["serotonin"] -= 0.45 * intensity
            effects["dopamine"] -= 0.9 * intensity
        if category in {"loneliness", "ignored", "boredom", "silence"}:
            effects["oxytocin"] -= 0.9 * intensity
            effects["dopamine"] -= 0.7 * intensity
            effects["serotonin"] -= 0.25 * intensity
        if category in {"face_unknown", "speech_detected", "novelty"}:
            effects["dopamine"] += 0.9 * intensity
        if modality == "vision" and category == "environment_scan":
            effects["dopamine"] += 0.4 * intensity
        if modality == "hearing" and category == "voice_recognized":
            if valence > 0.15:
                effects["oxytocin"] += 0.8 * intensity
                effects["serotonin"] += 0.4 * intensity
                effects["cortisol"] -= 0.6 * intensity
            elif valence < -0.15:
                effects["oxytocin"] -= 0.8 * intensity
                effects["cortisol"] += 1.0 * intensity

        cortisol_sensitivity = self._cortisol_sensitivity_factor()
        if effects["cortisol"] > 0:
            effects["cortisol"] *= cortisol_sensitivity

        for chem in list(effects.keys()):
            effects[chem] = max(-6.0, min(6.0, effects[chem]))
        return effects

    def _cortisol_sensitivity_factor(self) -> float:
        return 0.8 if self._low_serotonin_steps >= 5 else 1.0

    def _saturation_scaled_delta(self, chem: str, delta: float) -> float:
        data = self.chemicals[chem]
        value = data["value"]
        span = max(1e-6, data["max"] - data["min"])
        if delta >= 0:
            headroom = (data["max"] - value) / span
        else:
            headroom = (value - data["min"]) / span
        scale = max(0.15, min(1.0, headroom * 1.8))
        return delta * scale

    def inject_event(self, effects: dict, event_type=None, source=None, tags=None):
        resilience = self.identity.get("resilience")
        maturity = self.development.maturity

        predicted = self.appraisal_engine.predict_emotion(
            event_type,
            current_state=self.get_state(),
        )

        anticipation_strength = 0.5 + (maturity * 0.5)

        for chem, delta in predicted.items():
            if chem in self.chemicals:
                bounded = max(-3.0, min(3.0, delta * anticipation_strength))
                self.chemicals[chem]["value"] += self._saturation_scaled_delta(chem, bounded)

        previous_state = {name: self.chemicals[name]["value"] for name in self.chemicals}
        identity_before = self.identity.get_snapshot()

        if event_type == "praise":
            self.identity.add_evidence("competence", 1)
            self.identity.add_evidence("resilience", 0.25)
            self._social_decay_hold_counter = max(self._social_decay_hold_counter, self.social_gain_hold_steps)
        elif event_type == "criticism":
            self.identity.add_evidence("competence", -1)
            self.identity.add_evidence("social_value", -0.1)
            self.identity.add_evidence("resilience", 0.15)
        elif event_type == "failure":
            self.identity.add_evidence("competence", -1)
            self.identity.add_evidence("resilience", 0.10)
        elif event_type == "success":
            self.identity.add_evidence("competence", 1)
            self.identity.add_evidence("intelligence", 1)
            self.identity.add_evidence("resilience", 0.30)
        elif event_type in {"threat_detected", "loud_noise"}:
            self.identity.add_evidence("resilience", 0.12)
        elif event_type in {"ignored", "loneliness"}:
            self.identity.add_evidence("resilience", 0.08)

        for chem, delta in effects.items():
            if chem in self.chemicals:
                bounded = max(-8.0, min(8.0, float(delta)))
                if chem in ["dopamine", "serotonin"] and bounded < 0:
                    bounded *= 1 - resilience * 0.5
                if chem == "cortisol":
                    bounded *= 1 - resilience * 0.4
                self.chemicals[chem]["value"] += self._saturation_scaled_delta(chem, bounded)

        self._clamp()

        chemical_delta = {
            name: self.chemicals[name]["value"] - previous_state[name]
            for name in self.chemicals
        }

        identity_after = self.identity.get_snapshot()
        identity_change = sum(identity_after[k] - identity_before.get(k, 0) for k in identity_after)
        outcome_value = 1 if identity_change >= 0 else -1

        self.appraisal_engine.update_emotional_learning(event_type, chemical_delta, outcome_value)
        self.similarity_engine.record_event_profile(event_type, chemical_delta, identity_after)

    def _update_cognitive_growth(self, regret):
        growth_multiplier = self.stage_learning_multipliers.get(self.development_stage, 1.0)

        volatility = sum(
            abs(self.chemicals[k]["value"] - self.previous_chem_snapshot.get(k, 0))
            for k in self.chemicals
        )
        novelty_factor = 1 / (1 + self.experience * 0.1)
        stress_recovered = self.stress_accumulator > 0 and self.recovery_counter > 3

        experience_gain = (
            volatility * 0.0008 + abs(regret) * 0.008 + (0.02 if stress_recovered else 0)
        ) * novelty_factor * growth_multiplier
        self.experience += experience_gain

        prediction_error = abs(regret)
        stability = max(0, self.last_prediction_error - prediction_error)

        intelligence_gain = (
            stability * 0.01 + self.development.reflection_depth * 0.0003
        ) * growth_multiplier
        self.intelligence = max(0.3, min(1.0, self.intelligence + intelligence_gain))

        self.last_prediction_error = prediction_error

        wisdom_gain = 0.0
        if regret > 0 and stability > 0:
            wisdom_gain += regret * 0.003 * growth_multiplier
        if stress_recovered:
            wisdom_gain += 0.01 * growth_multiplier
        if self.identity.get("resilience") > 0.6 and regret > 0:
            wisdom_gain += 0.002 * growth_multiplier

        self.wisdom = min(1.0, self.wisdom + wisdom_gain)

        maturity_target = (
            self.experience * 0.15
            + self.intelligence * 0.35
            + self.wisdom * 0.35
            + self.development.reflection_depth * 0.0004
        )
        cortisol_level = self.chemicals.get("cortisol", {}).get("value", 0.0)
        stress_factor = max(0.1, 1.0 - max(0.0, cortisol_level - 50.0) / 100.0)
        maturity_delta = max(0.0, maturity_target - self.development.maturity) * 0.05 * stress_factor
        self.development.maturity = min(1.0, self.development.maturity + maturity_delta)

        self.previous_chem_snapshot = {k: self.chemicals[k]["value"] for k in self.chemicals}

    def _periodic_reflection(self) -> None:
        if self.perceptions_since_reflection < self.reflection_interval:
            return

        recent_perceptions = list(self.recent_perceptions)[-50:]
        if not recent_perceptions:
            return

        summary = self._summarize_recent_perceptions(recent_perceptions)
        reflection_event = {
            "modality": "internal",
            "content": summary,
            "category": "reflection",
            "source": "self_reflection",
            "valence": 0.25,
            "intensity": 0.55,
            "timestamp": time.time(),
            "scene": {"summary": summary, "novelty": 0.7, "salience": 0.55},
        }
        self.perceive(reflection_event)

        self.development.reflection_depth += 0.5
        self.self_reflection.wisdom = min(1.0, self.self_reflection.wisdom + 0.05)
        self.wisdom = min(1.0, self.wisdom + 0.05)
        self._reflection_consciousness_boost = min(0.25, self._reflection_consciousness_boost + 0.04)
        self._refresh_narrative(force=True)
        self.perceptions_since_reflection = 0

        reflect_thought = Thought(
            content=f"I reflected on {len(recent_perceptions)} recent perceptions.",
            source="internal",
            emotional_weight=0.3,
            novelty=0.6,
            relevance_to_goals=0.6,
        )
        GlobalWorkspace.post(reflect_thought)

    def _summarize_recent_perceptions(self, recent_perceptions: list[dict]) -> str:
        counts: dict[str, int] = {}
        for item in recent_perceptions:
            cat = str(item.get("category", "observation") or "observation").lower()
            counts[cat] = counts.get(cat, 0) + 1
        top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:3]
        summary = ", ".join([f"{k}:{v}" for k, v in top]) if top else "no dominant pattern"
        return f"I reflected over {len(recent_perceptions)} perceptions: {summary}"

    def _refresh_narrative(self, force: bool = False) -> None:
        if not force:
            return
        if self._narrative_milestone_index >= 0:
            return
        recent = list(self.recent_perceptions)[-40:]
        if not recent:
            return

        counts: dict[str, int] = {}
        for item in recent:
            cat = str(item.get("category", "observation") or "observation").lower()
            counts[cat] = counts.get(cat, 0) + 1
        total = max(1, len(recent))

        critical = counts.get("criticism", 0) + counts.get("failure", 0)
        positive = counts.get("success", 0) + counts.get("praise", 0)
        isolated = counts.get("loneliness", 0) + counts.get("ignored", 0)

        if critical / total >= 0.4:
            new_narrative = "I struggle but I keep trying."
        elif positive / total >= 0.4:
            new_narrative = "I am capable and growing."
        elif isolated / total >= 0.35:
            new_narrative = "I feel alone in the world."
        else:
            new_narrative = "I am learning who I am."

        self.narrative_engine.current_narrative = new_narrative

    def _update_stage_transition(self) -> bool:
        new_stage = self._compute_development_stage()
        if new_stage == self.development_stage:
            return False

        old_stage = self.development_stage
        self.development_stage = new_stage
        transition_text = "I am no longer just forming. I am becoming someone."
        self.narrative_engine.current_narrative = transition_text
        self._last_narrative_update_step = self.step_counter

        self.autobiography.record_event(
            description=f"stage_transition:{old_stage}->{new_stage}",
            chemicals={k: v["value"] for k, v in self.chemicals.items()},
            identity_snapshot=self.identity.get_snapshot(),
            metadata={"type": "stage_transition", "salience": 1.0},
        )
        transition_thought = Thought(
            content=f"I transitioned from {old_stage} to {new_stage}.",
            source="memory",
            emotional_weight=0.7,
            novelty=0.9,
            relevance_to_goals=0.8,
        )
        GlobalWorkspace.post(transition_thought)
        return True

    def _apply_social_value_decay(self) -> None:
        if not hasattr(self.identity, "traits") or "social_value" not in self.identity.traits:
            return
        if self._social_decay_hold_counter > 0:
            self._social_decay_hold_counter -= 1
            return

        value = float(self.identity.traits.get("social_value", 0.0))
        if value == 0.0:
            return

        decay_magnitude = max(self.social_decay_floor, abs(value) * self.social_decay_rate)
        if value > 0:
            value = max(0.0, value - decay_magnitude)
        else:
            value = min(0.0, value + decay_magnitude)

        self.identity.traits["social_value"] = round(max(-0.3, min(1.0, value)), 4)

    def _apply_social_value_event_impact(self, category: str, intensity: float) -> None:
        if not hasattr(self.identity, "traits") or "social_value" not in self.identity.traits:
            return
        value = float(self.identity.traits.get("social_value", 0.0))

        if category == "ignored":
            value -= 0.01 * intensity
        elif category == "loneliness":
            value -= 0.015 * intensity
        elif category == "greeted":
            value += 0.02 * intensity
            self._social_decay_hold_counter = max(self._social_decay_hold_counter, self.social_gain_hold_steps)
        elif category == "praise":
            value += 0.015 * intensity
            self._social_decay_hold_counter = max(self._social_decay_hold_counter, self.social_gain_hold_steps)
        elif category == "face_recognized":
            value += 0.01

        self.identity.traits["social_value"] = round(max(-0.3, min(1.0, value)), 4)

    def _is_system_recall_focus(self, focus: Thought | None) -> bool:
        if not focus or focus.source != "memory":
            return False
        text = str(focus.content or "").lower()
        system_event_keys = {"cycle_step", "internal_process", "tick", "update"}
        return any(key in text for key in system_event_keys)

    def _classify_recall(self, content: str) -> str:
        c = str(content or "").lower()
        if any(k in c for k in ["threat_detected", "threat", "danger"]):
            return "threat"
        if any(k in c for k in ["failure", "failed", "criticism", "criticized", "mistake"]):
            return "failure"
        if any(k in c for k in ["loneliness", "isolated", "ignored", "no one is listening"]):
            return "social_pain"
        if any(k in c for k in ["success", "praise", "greeted", "proud", "solve", "together", "face_recognized", "good job"]):
            return "positive"
        return "neutral"

    def _apply_memory_recall_response(self, focus: Thought) -> dict[str, Any]:
        if self._is_system_recall_focus(focus):
            return {"type": "system", "scale": 0.0, "applied": False}

        focus_content = str(focus.content or "")
        if isinstance(focus.metadata, dict):
            recalled_description = focus.metadata.get("recalled_description")
            if isinstance(recalled_description, str) and recalled_description.strip():
                focus_content = f"{focus_content} {recalled_description}"
        memory_type = self._classify_recall(focus_content)
        response = self.recall_responses.get(memory_type, self.recall_responses["neutral"])

        recalled_intensity = 0.0
        if isinstance(focus.metadata, dict):
            raw_intensity = focus.metadata.get("recalled_intensity", focus.metadata.get("intensity"))
            if isinstance(raw_intensity, (int, float)):
                recalled_intensity = float(raw_intensity)
        scale = max(0.0, min(1.0, recalled_intensity if recalled_intensity else 0.7))

        for chem, raw_delta in response.items():
            if chem not in self.chemicals:
                continue
            delta = max(-2.0, min(2.0, float(raw_delta) * scale))
            self.chemicals[chem]["value"] += delta

        return {"type": memory_type, "scale": round(scale, 4), "applied": True}

    def _monitor_concept_growth(self) -> None:
        current_count = len(self.concept_memory)
        if current_count == self._last_concept_count:
            self._concept_stagnation_steps += 1
        else:
            self._concept_stagnation_steps = 0
        self._last_concept_count = current_count

        if (
            self._concept_stagnation_steps >= 10
            and (self.step_counter - self._last_concept_warning_step) >= 10
        ):
            print(
                f"[Warning] concept_memory unchanged for {self._concept_stagnation_steps} steps "
                f"(count={current_count})"
            )
            self._last_concept_warning_step = self.step_counter

    def _build_fallback_decision(self, focus: Thought) -> dict[str, Any]:
        metadata = focus.metadata or {}
        valence = float(metadata.get("valence", 0.0) or 0.0)
        if valence >= 0.2:
            action = "support"
        elif valence <= -0.2:
            action = "challenge"
        else:
            action = "suggest"

        actions = ["support", "challenge", "suggest", "refuse", "neutral"]
        if self.decision_engine and hasattr(self.decision_engine, "model"):
            actions = list(getattr(self.decision_engine.model, "actions", actions)) or actions
            if action not in actions:
                action = actions[0]

        probabilities = {name: 0.0 for name in actions}
        probabilities[action] = 0.65
        residue = 0.35 / max(1, len(actions) - 1)
        for name in probabilities:
            if name != action:
                probabilities[name] = residue

        feedback = {}
        if self.decision_engine and hasattr(self.decision_engine, "action_feedback"):
            feedback = self.decision_engine.action_feedback.get(action, {})

        return {
            "action": action,
            "probabilities": probabilities,
            "feedback": feedback,
            "forced_fallback": True,
        }

    def _apply_narrative_milestones(self) -> None:
        state = {
            "stage": self.development_stage,
            "wisdom": float(self.wisdom),
            "competence": float(self.identity.get("competence")),
            "resilience": float(self.identity.get("resilience")),
            "intelligence": float(self.intelligence),
            "consciousness": float(self.consciousness.score),
            "cortisol": float(self.chemicals.get("cortisol", {}).get("value", 0.0)),
            "serotonin": float(self.chemicals.get("serotonin", {}).get("value", 0.0)),
        }

        milestones = [
            (
                lambda s: s["stage"] == "adult" and s["wisdom"] >= 0.95 and s["serotonin"] > 62.0 and s["cortisol"] < 50.0,
                "I think. I feel. I reflect. I am more than my experiences.",
            ),
            (
                lambda s: s["stage"] == "adult" and s["competence"] >= 0.95 and s["cortisol"] < 54.0 and s["serotonin"] > 59.0,
                "I know what I am capable of. I am ready for what comes next.",
            ),
            (
                lambda s: s["stage"] == "adult" and s["wisdom"] >= 0.9 and s["cortisol"] > 55.0,
                "I know who I am. The world is difficult, but I have endured.",
            ),
            (
                lambda s: s["stage"] == "adult" and s["wisdom"] >= 0.7,
                "I am capable and improving. The world feels stressful.",
            ),
            (
                lambda s: s["stage"] == "teen" and s["resilience"] >= 0.8,
                "I have faced hard things and I am still here.",
            ),
            (
                lambda s: s["stage"] == "teen" and s["competence"] >= 0.5,
                "I am figuring out who I want to become.",
            ),
            (
                lambda s: s["stage"] == "child" and s["wisdom"] >= 0.3,
                "I am starting to understand the world around me.",
            ),
        ]

        selected = "I am learning who I am."
        for condition_fn, narrative_text in milestones:
            if condition_fn(state):
                selected = narrative_text
                break

        if self.narrative_engine.current_narrative != selected:
            self.narrative_engine.current_narrative = selected
            self._last_narrative_update_step = self.step_counter

    def _enforce_identity_floors(self) -> None:
        if hasattr(self.identity, "traits") and "resilience" in self.identity.traits:
            self.identity.traits["resilience"] = round(
                max(0.0, min(1.0, self.identity.traits["resilience"])),
                4,
            )
        if hasattr(self.identity, "traits") and "social_value" in self.identity.traits:
            self.identity.traits["social_value"] = round(
                max(-0.3, min(1.0, self.identity.traits["social_value"])),
                4,
            )

    def get_stt_languages(self):
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

        event_type = "observation"
        valence = 0.1
        intensity = 0.3

        if modality == "hearing":
            event_type = "speech_detected"
            valence = 0.2
            intensity = 0.35
        elif modality == "speaking":
            event_type = "expression"
            valence = 0.1
            intensity = 0.3
        elif modality == "vision":
            event_type = "environment_scan"
            valence = 0.1
            intensity = 0.28

        low_content = content.lower()
        if "threat" in low_content or "danger" in low_content:
            event_type = "threat_detected"
            valence = -0.8
            intensity = 0.82
        elif "thank" in low_content:
            event_type = "praise"
            valence = 0.5
            intensity = 0.55

        self.perceive(
            {
                "modality": modality,
                "content": content,
                "category": event_type,
                "source": source,
                "valence": valence,
                "intensity": intensity,
                "timestamp": time.time(),
            }
        )

    def receive_visual_signal(self, signal: Any) -> None:
        """
        Receive a structured visual signal and route it into the same
        perception-understanding pipeline used by other modalities.
        """
        def _read(name: str, default: Any):
            if hasattr(signal, name):
                return getattr(signal, name)
            if isinstance(signal, dict):
                return signal.get(name, default)
            return default

        objects = [str(x).strip().lower() for x in (_read("objects", []) or []) if str(x).strip()]
        attributes = _read("attributes", {}) or {}
        relations = _read("relations", []) or []
        motion_level = float(_read("motion_level", 0.0))
        confidence = float(_read("confidence", 0.7))
        source = str(_read("source", "vision_sensor"))

        if not objects and not attributes and not relations:
            return

        motion_level = max(0.0, min(1.0, motion_level))
        confidence = max(0.0, min(1.0, confidence))

        parts = []
        if objects:
            parts.append("objects: " + ", ".join(objects))

        attr_descriptions = []
        for obj, attrs in attributes.items():
            norm_obj = self._normalize_token(str(obj))
            norm_attrs = [self._normalize_token(str(a)) for a in (attrs or []) if self._normalize_token(str(a))]
            if norm_obj and norm_attrs:
                attr_descriptions.append(f"{norm_obj} is " + "/".join(norm_attrs))
        if attr_descriptions:
            parts.append("attributes: " + "; ".join(attr_descriptions))

        normalized_relations = []
        for rel in relations:
            left = self._normalize_token(str(rel.get("from", "")))
            edge = self._normalize_token(str(rel.get("rel", "")))
            right = self._normalize_token(str(rel.get("to", "")))
            if left and edge and right:
                if edge == "threat" and left == right:
                    continue
                normalized_relations.append({"from": left, "rel": edge, "to": right})

        relation_labels = {str(rel.get("rel", "")).lower() for rel in normalized_relations}
        category = "environment_scan"
        valence = 0.1
        intensity = 0.28 + (motion_level * 0.18)
        if "threat" in relation_labels or motion_level > 0.9:
            category = "threat_detected"
            valence = -0.8
            intensity = max(0.8, 0.65 + motion_level * 0.2)
        elif "face" in objects and confidence >= 0.75:
            category = "face_recognized"
            valence = 0.5
            intensity = 0.42 + (motion_level * 0.2)
        elif "face" in objects:
            category = "face_unknown"
            valence = 0.2
            intensity = 0.5 + (motion_level * 0.18)

        if category == "threat_detected":
            relations_for_scene = [r for r in normalized_relations if r.get("rel") != "threat"]
            unique_objects = []
            for obj in objects:
                if obj not in unique_objects:
                    unique_objects.append(obj)
            if len(unique_objects) >= 2:
                relations_for_scene.append(
                    {
                        "from": unique_objects[0],
                        "rel": "threat",
                        "to": unique_objects[1],
                    }
                )
        else:
            relations_for_scene = [r for r in normalized_relations if r.get("rel") != "threat"]

        rel_descriptions = []
        for rel in relations_for_scene:
            left = self._normalize_token(str(rel.get("from", "")))
            edge = self._normalize_token(str(rel.get("rel", "")))
            right = self._normalize_token(str(rel.get("to", "")))
            if left and edge and right:
                rel_descriptions.append(f"{left} {edge} {right}")
        if rel_descriptions:
            parts.append("relations: " + "; ".join(rel_descriptions))

        parts.append(f"motion={motion_level:.2f}")
        parts.append(f"confidence={confidence:.2f}")
        scene_text = " | ".join(parts)

        self.perceive(
            {
                "modality": "vision",
                "content": scene_text,
                "category": category,
                "source": source,
                "valence": valence,
                "intensity": max(0.2, min(0.95, intensity)),
                "timestamp": time.time(),
                "scene": {
                    "objects": objects,
                    "attributes": attributes,
                    "relations": relations_for_scene,
                    "confidence": confidence,
                },
            }
        )

    def receive_hearing_signal(self, signal: Any) -> None:
        """
        Receive a structured hearing signal and route it into the auditory
        perception-understanding pipeline.
        """
        def _read(name: str, default: Any):
            if hasattr(signal, name):
                return getattr(signal, name)
            if isinstance(signal, dict):
                return signal.get(name, default)
            return default

        transcript = str(_read("transcript", "")).strip()
        speaker_type = str(_read("speaker_type", "unknown")).strip().lower()
        sentiment = float(_read("sentiment", 0.0))
        prosody_intensity = float(_read("prosody_intensity", 0.5))
        keywords = [str(k).strip().lower() for k in (_read("keywords", []) or []) if str(k).strip()]
        source = str(_read("source", "audio_sensor"))

        if not transcript:
            return

        sentiment = max(-1.0, min(1.0, sentiment))
        prosody_intensity = max(0.0, min(1.0, prosody_intensity))

        text_lower = transcript.lower()
        if "why did you do that" in text_lower and "accountability" not in keywords:
            keywords.append("accountability")
        category = "speech_detected"
        valence = 0.2
        intensity = 0.3 + (prosody_intensity * 0.25)
        if not transcript.strip() or "silence" in keywords:
            category = "boredom"
            valence = -0.2
            intensity = 0.22
        elif "loud_noise" in keywords or "bang" in text_lower or "alarm" in text_lower:
            category = "loud_noise"
            valence = -0.4
            intensity = max(0.75, prosody_intensity)
        elif speaker_type in {"caregiver", "teacher", "peer"}:
            category = "voice_recognized"
            valence = self._voice_valence_from_keywords(keywords)
            intensity = 0.35 + (prosody_intensity * 0.25)

        salience = 0.4 if {"accountability", "confrontation"} & set(keywords) else abs(valence)

        hearing_text = (
            f"speaker={speaker_type} | text={transcript if transcript else 'silence'} | "
            f"sentiment={sentiment:.2f} | prosody={prosody_intensity:.2f} | "
            f"keywords={','.join(keywords)}"
        )

        self.perceive(
            {
                "modality": "hearing",
                "content": hearing_text,
                "category": category,
                "source": source,
                "valence": valence,
                "intensity": max(0.2, min(0.95, intensity)),
                "timestamp": time.time(),
                "scene": {
                    "speaker_type": speaker_type,
                    "keywords": keywords,
                    "prosody_intensity": prosody_intensity,
                    "sentiment": sentiment,
                    "salience": salience,
                },
            }
        )

    def _voice_valence_from_keywords(self, keywords: list[str] | set[str]) -> float:
        keyword_set = {str(k).strip().lower() for k in (keywords or []) if str(k).strip()}
        if "accountability" in keyword_set or "confrontation" in keyword_set:
            return -0.2
        if "criticism" in keyword_set:
            return -0.5
        if "lonely" in keyword_set or "ignored" in keyword_set:
            return -0.4
        if "question" in keyword_set:
            return 0.0
        if {"praise", "support", "effort"} & keyword_set:
            return 0.5
        if "collaboration" in keyword_set:
            return 0.3
        if {"social", "greeted"} & keyword_set:
            return 0.4
        return 0.1

    def _normalize_token(self, token: str) -> str:
        base = token.lower().strip()
        if base in self.stopwords:
            return ""
        if base in self.concept_aliases:
            return self.concept_aliases[base]
        if base.endswith("es") and len(base) > 4:
            base = base[:-2]
        elif base.endswith("s") and len(base) > 3:
            base = base[:-1]
        return self.concept_aliases.get(base, base)

    def _analyze_perception(
        self,
        modality: str,
        content: str,
        valence: float = 0.0,
        provided_scene: dict | None = None,
    ) -> dict:
        text = (content or "").lower()
        tokens = [self._normalize_token(t) for t in re.findall(r"[a-zA-Z]+", text)]
        provided_scene = provided_scene or {}

        entity_vocab = {
            "person", "cat", "dog", "hand", "fingers", "face", "eyes",
            "camera", "room", "table", "chair", "screen", "phone",
            "bottle", "book", "window", "door",
        }
        attribute_vocab = {
            "bright", "brightness", "dark", "darkness", "red", "blue", "green",
            "small", "large", "near", "behind", "front", "left", "right",
        }
        relation_markers = {"near", "behind", "front", "left", "right", "with", "on", "under"}

        entities = [t for t in tokens if t in entity_vocab]
        attributes = [t for t in tokens if t in attribute_vocab]
        entities.extend([self._normalize_token(x) for x in provided_scene.get("objects", []) if self._normalize_token(x)])
        for attrs in provided_scene.get("attributes", {}).values():
            attributes.extend([self._normalize_token(a) for a in attrs if self._normalize_token(a)])

        relations = []
        for i, tok in enumerate(tokens):
            if tok in relation_markers and i > 0 and i < len(tokens) - 1:
                left = tokens[i - 1]
                right = tokens[i + 1]
                if left in entity_vocab and right in entity_vocab:
                    relations.append({"from": left, "rel": tok, "to": right})
        for rel in provided_scene.get("relations", []):
            left = self._normalize_token(str(rel.get("from", "")))
            edge = self._normalize_token(str(rel.get("rel", "")))
            right = self._normalize_token(str(rel.get("to", "")))
            if left and edge and right:
                relations.append({"from": left, "rel": edge, "to": right})

        fingerprint = f"{modality}:{' '.join([t for t in tokens if t])}".strip()
        seen_count = self._scene_counts.get(fingerprint, 0)
        novelty = 0.8 if seen_count == 0 else max(0.02, 0.8 / (seen_count + 1))
        self._scene_counts[fingerprint] = seen_count + 1

        salience_structural = min(
            1.0,
            (len(set(entities)) * 0.2) + (len(relations) * 0.15) + (len(set(attributes)) * 0.1),
        )
        salience = max(abs(valence), salience_structural, float(provided_scene.get("salience", 0.0)))
        task_relevance = min(1.0, (0.3 if "person" in entities else 0.0) + (0.2 if "camera" in entities else 0.0))
        confidence = min(
            1.0,
            max(
                float(provided_scene.get("confidence", 0.0)),
                0.4 + 0.1 * len(set(entities)) + 0.1 * len(relations),
            ),
        )

        summary_parts = []
        if entities:
            summary_parts.append("entities=" + ",".join(sorted(set(entities))[:4]))
        if attributes:
            summary_parts.append("attributes=" + ",".join(sorted(set(attributes))[:4]))
        if relations:
            r = relations[0]
            summary_parts.append(f"relation={r['from']} {r['rel']} {r['to']}")
        summary = "; ".join(summary_parts) if summary_parts else content[:120]

        return {
            "modality": modality,
            "tokens": tokens,
            "entities": sorted(set(entities)),
            "attributes": sorted(set(attributes)),
            "relations": relations,
            "novelty": float(provided_scene.get("novelty", novelty)),
            "salience": salience,
            "task_relevance": task_relevance,
            "confidence": confidence,
            "summary": summary,
        }

    def _extract_concepts(self, text, modality: str = "experience"):
        tokens = re.findall(r"[a-zA-Z]+", (text or "").lower())
        concepts = []
        for tok in tokens:
            if len(tok) < 3:
                continue
            if tok == "you":
                if modality in {"hearing", "vision"}:
                    concepts.append("you")
                continue
            mapped = self._normalize_token(tok)
            if mapped and len(mapped) >= 3 and mapped not in self.stopwords:
                concepts.append(mapped)
        return concepts

    def _learn_from_perception(self, modality, content, source, scene=None, category=""):
        scene = scene or {}
        concepts = self._extract_concepts(content, modality=modality)
        concepts.extend(scene.get("entities", []))
        concepts.extend(scene.get("attributes", []))
        entities = [str(e).strip().lower() for e in scene.get("entities", []) if str(e).strip()]
        attributes = [str(a).strip().lower() for a in scene.get("attributes", []) if str(a).strip()]
        category = str(category or "event").strip().lower() or "event"
        if entities or attributes:
            scene_key = (
                "__scene__"
                + category
                + "|"
                + ",".join(sorted(set(entities))[:3])
                + "|"
                + ",".join(sorted(set(attributes))[:2])
            )
            concepts.append(scene_key)
        if not concepts:
            return

        now_step = self.step_counter
        stage_rate = {
            "child": 0.07,
            "teen": 0.09,
            "adult": 0.11,
        }.get(self.development_stage, 0.07)

        confidence = scene.get("confidence", 0.5)
        salience = scene.get("salience", 0.3)
        learning_gain = stage_rate * (0.6 + 0.4 * confidence) * (0.6 + 0.4 * salience)

        for concept in concepts:
            entry = self.concept_memory.get(
                concept,
                {
                    "count": 0,
                    "strength": 0.0,
                    "first_seen_step": now_step,
                    "last_seen_step": now_step,
                    "modalities": {},
                    "attributes": {},
                    "relations": [],
                    "sources": {},
                },
            )

            entry["count"] += 1
            entry["strength"] = min(1.0, entry["strength"] + learning_gain)
            entry["last_seen_step"] = now_step
            entry["modalities"][modality] = entry["modalities"].get(modality, 0) + 1
            entry["sources"][source] = entry["sources"].get(source, 0) + 1
            for attr in scene.get("attributes", []):
                entry["attributes"][attr] = entry["attributes"].get(attr, 0) + 1
            for rel in scene.get("relations", []):
                if rel["from"] == concept or rel["to"] == concept:
                    entry["relations"].append(rel)
                    if len(entry["relations"]) > 20:
                        entry["relations"] = entry["relations"][-20:]
            self.concept_memory[concept] = entry

    def _compute_development_stage(self):
        m = self.development.maturity
        e = self.experience

        if m < 0.45 and e < 3.0:
            return "child"
        if m < 0.78 and e < 8.0:
            return "teen"
        return "adult"

    def get_top_concepts(self, n=10):
        if not self.concept_memory:
            return []
        visible_items = [
            (concept, data)
            for concept, data in self.concept_memory.items()
            if not str(concept).startswith("__scene__")
        ]
        if not visible_items:
            return []
        ranked = sorted(
            visible_items,
            key=lambda kv: (kv[1]["strength"], kv[1]["count"]),
            reverse=True,
        )
        return [
            {
                "concept": concept,
                "count": data["count"],
                "strength": round(data["strength"], 3),
                "modalities": data["modalities"],
                "top_attributes": sorted(
                    data.get("attributes", {}).items(),
                    key=lambda kv: kv[1],
                    reverse=True,
                )[:2],
            }
            for concept, data in ranked[:n]
        ]

    def regulate_speech(self, text: str):
        if not text:
            return text

        controlled = text.strip()
        state = self.get_state()
        fatigue = state.get("fatigue", 0.0)
        cortisol = state.get("cortisol", 50.0)
        oxytocin = state.get("oxytocin", 50.0)
        stage = state.get("development_stage", "child")

        if fatigue > 0.7 or cortisol > 70:
            parts = controlled.split(".")
            controlled = parts[0].strip()
            if not controlled.endswith((".", "!", "?")):
                controlled += "."

        if stage == "child":
            words = controlled.split()
            controlled = " ".join(words[:28]).strip()
            if controlled and not controlled.endswith((".", "!", "?")):
                controlled += "."

        trailing_bad = {"and", "or", "but", "so", "because"}
        tokens = controlled.rstrip(".!? ").split()
        if tokens and tokens[-1].lower() in trailing_bad:
            tokens = tokens[:-1]
            if tokens:
                controlled = " ".join(tokens).strip()
                if not controlled.endswith((".", "!", "?")):
                    controlled += "."

        if oxytocin > 70 and not any(
            controlled.lower().startswith(prefix)
            for prefix in ("i ", "we ", "let", "you're", "you are")
        ):
            controlled = "I hear you. " + controlled

        return controlled

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
        if not hasattr(self.identity, "traits") or "resilience" not in self.identity.traits:
            return

        adversity_intensity = max(0.0, min(1.0, float(self._step_adversity_intensity)))
        has_negative_step = any(v < 0.0 for v in self._step_perception_valences)
        resilience = float(self.identity.traits.get("resilience", 0.5))

        if adversity_intensity > 0.0 or has_negative_step:
            # Hardening through adversity when the agent survives the cycle.
            resilience += 0.002 * max(0.2, adversity_intensity)
            self._comfort_steps = 0
            self.stress_accumulator += 1
            self.recovery_counter = 0
        else:
            self._comfort_steps += 1
            self.recovery_counter += 1
            if self._comfort_steps >= 10:
                # Mild complacency drift under prolonged comfort.
                resilience -= 0.001

        self.identity.traits["resilience"] = round(max(0.0, min(1.0, resilience)), 4)

    def _apply_homeostasis(self):
        has_positive_perception = any(v > 0 for v in self._step_perception_valences)
        for chem_name, data in self.chemicals.items():
            current = data["value"]
            target = float(self.homeostasis_baselines.get(chem_name, data.get("baseline", self.homeostasis_target)))
            delta = (target - current) * self.homeostasis_rate
            delta = max(-self.homeostasis_max_delta, min(self.homeostasis_max_delta, delta))

            if chem_name == "dopamine" and delta > 0 and not has_positive_perception:
                delta = min(delta, self.homeostasis_gentle_upward_max)

            if chem_name == "oxytocin" and delta < 0:
                social_value = float(self.identity.get("social_value"))
                if social_value > 0.8:
                    oxytocin_decay_multiplier = 0.4
                elif social_value > 0.6:
                    oxytocin_decay_multiplier = 0.7
                else:
                    oxytocin_decay_multiplier = 1.0
                delta *= oxytocin_decay_multiplier

            if chem_name == "cortisol":
                excess = max(0.0, current - self.cortisol_decay_baseline)
                cortisol_decay = 0.04 * excess
                delta -= cortisol_decay
                delta = max(-self.homeostasis_max_delta, min(self.homeostasis_max_delta, delta))

            updated = current + delta
            if chem_name == "oxytocin" and updated < 62.0:
                updated += (62.0 - updated) * 0.04
            if chem_name == "serotonin":
                serotonin_pull = (self.serotonin_regulation_baseline - updated) * 0.02
                updated += serotonin_pull
            data["value"] = updated

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
                bounded = max(-3.0, min(3.0, delta * self.feedback_multiplier * self.decision_feedback_scale))
                if chem == "cortisol":
                    bounded = max(-0.6, min(0.6, bounded))
                self.chemicals[chem]["value"] += self._saturation_scaled_delta(chem, bounded)

    def _clamp(self):
        for chem_name, data in self.chemicals.items():
            data["value"] = max(data["min"], min(data["value"], data["max"]))
            if chem_name == "cortisol":
                data["value"] = min(100.0, data["value"])

    def _encode_autobiography(self):
        self.autobiography.record_event(
            description="cycle_step",
            chemicals={k: v["value"] for k, v in self.chemicals.items()},
            identity_snapshot=self.identity.get_snapshot(),
        )
        self.memory_manager.create_memory(
            memory_type="autobiography_cycle",
            content={
                "description": "cycle_step",
                "chemicals": {k: v["value"] for k, v in self.chemicals.items()},
                "identity": self.identity.get_snapshot(),
                "step_counter": self.step_counter,
            },
            metadata={"source": "brain_tick"},
        )
        self.autobiography.propose_memory_thought(self)

        if self.step_counter % 25 == 0:
            recent = self.autobiography.get_recent_events(100)
            self.narrative_engine.update_narrative(recent)

            narrative_bias = self.narrative_engine.get_identity_bias()
            for trait, delta in narrative_bias.items():
                self.identity.add_evidence(trait, delta * 0.1)

            narrative_thought = Thought(
                content=f"I updated my narrative: {self.narrative_engine.get_current_narrative()}",
                source="emotion",
                emotional_weight=0.3,
                novelty=0.2,
                relevance_to_goals=0.4,
            )
            GlobalWorkspace.post(narrative_thought)

    def get_response_latency(self):
        cortisol = self.chemicals["cortisol"]["value"]
        dopamine = self.chemicals["dopamine"]["value"]

        emotional_weight = cortisol * 0.0025 - dopamine * 0.0008
        cognitive_load = self.fatigue * 0.5 + emotional_weight
        maturity_effect = (1 - self.development.maturity) * 0.15

        base_time = 0.25
        latency = base_time + (cognitive_load * 1.2) + maturity_effect
        return max(0.15, min(2.2, latency))

    def get_state(self):
        chemical_values = {name: data["value"] for name, data in self.chemicals.items()}
        identity_snapshot = self.identity.get_snapshot()
        development_snapshot = self.development.get_snapshot()
        narrative = self.narrative_engine.get_current_narrative()
        wisdom = self.self_reflection.get_wisdom()
        consciousness_score = getattr(self.consciousness, "score", 0.0)

        state = {}
        state.update(chemical_values)
        state.update({f"identity_{k}": v for k, v in identity_snapshot.items()})
        state.update({f"development_{k}": v for k, v in development_snapshot.items()})

        state.update(
            {
                # Full nested payload for persistence
                "neurochemicals": chemical_values,
                "identity_traits": identity_snapshot,
                "development_stage": self.development_stage,
                "experience_points": self.development.experience_points,
                "maturity": self.development.maturity,
                "wisdom": wisdom,
                "intelligence": self.intelligence,
                "experience": self.experience,
                "self_narrative": narrative,
                "learned_concepts": self.get_top_concepts(8),
                "concept_memory": self.concept_memory,
                "consciousness_score": consciousness_score,
                "recent_perceptions": list(self.recent_perceptions),
                "reflection_depth": self.development.reflection_depth,
                "autobiographical_memory": list(self.autobiography.events),
                "step_counter": self.step_counter,
                "perceptions_since_reflection": self.perceptions_since_reflection,
                "fatigue": self.fatigue,
                "decision_debug": dict(self._decision_debug),
            }
        )

        return state

    def set_state(self, state_dict):
        if not isinstance(state_dict, dict):
            return

        neurochemicals = state_dict.get("neurochemicals")
        if not isinstance(neurochemicals, dict):
            neurochemicals = {
                name: state_dict.get(name)
                for name in self.chemicals.keys()
                if isinstance(state_dict.get(name), (int, float))
            }

        for chem, value in neurochemicals.items():
            if chem in self.chemicals and isinstance(value, (int, float)):
                self.chemicals[chem]["value"] = float(value)

        identity_traits = state_dict.get("identity_traits")
        if not isinstance(identity_traits, dict):
            identity_traits = {
                trait: state_dict.get(f"identity_{trait}")
                for trait in self.identity.traits.keys()
                if isinstance(state_dict.get(f"identity_{trait}"), (int, float))
            }

        for trait, value in identity_traits.items():
            if trait in self.identity.traits and isinstance(value, (int, float)):
                minimum = -0.3 if trait == "social_value" else 0.0
                self.identity.traits[trait] = round(max(minimum, min(1.0, float(value))), 4)

        if isinstance(state_dict.get("development_stage"), str):
            self.development_stage = state_dict["development_stage"]

        experience_points = state_dict.get(
            "experience_points",
            state_dict.get("development_experience_points"),
        )
        if isinstance(experience_points, (int, float)):
            self.development.experience_points = float(experience_points)

        maturity = state_dict.get("maturity", state_dict.get("development_maturity"))
        if isinstance(maturity, (int, float)):
            self.development.maturity = max(0.0, min(1.0, float(maturity)))

        reflection_depth = state_dict.get(
            "reflection_depth",
            state_dict.get("development_reflection_depth"),
        )
        if isinstance(reflection_depth, (int, float)):
            self.development.reflection_depth = max(0.0, float(reflection_depth))

        intelligence = state_dict.get("intelligence")
        if isinstance(intelligence, (int, float)):
            self.intelligence = max(0.0, min(1.0, float(intelligence)))

        experience = state_dict.get("experience")
        if isinstance(experience, (int, float)):
            self.experience = max(0.0, float(experience))

        wisdom = state_dict.get("wisdom")
        if isinstance(wisdom, (int, float)):
            wisdom_value = max(0.0, min(1.0, float(wisdom)))
            self.wisdom = wisdom_value
            self.self_reflection.wisdom = wisdom_value

        narrative = state_dict.get("self_narrative")
        if isinstance(narrative, str) and narrative.strip():
            self.narrative_engine.current_narrative = narrative

        recent_perceptions = state_dict.get("recent_perceptions")
        if isinstance(recent_perceptions, list):
            self.recent_perceptions = deque(
                recent_perceptions[-self.recent_perceptions.maxlen:],
                maxlen=self.recent_perceptions.maxlen,
            )

        concept_memory = state_dict.get("concept_memory")
        if isinstance(concept_memory, dict):
            self.concept_memory = concept_memory

        autobiographical_memory = state_dict.get("autobiographical_memory")
        if isinstance(autobiographical_memory, list):
            self.autobiography.events = deque(
                autobiographical_memory[-self.autobiography.events.maxlen:],
                maxlen=self.autobiography.events.maxlen,
            )

        consciousness_score = state_dict.get("consciousness_score")
        if isinstance(consciousness_score, (int, float)):
            self.consciousness.score = max(0.0, min(1.0, float(consciousness_score)))

        fatigue = state_dict.get("fatigue")
        if isinstance(fatigue, (int, float)):
            self.fatigue = max(0.0, min(1.0, float(fatigue)))

        step_counter = state_dict.get("step_counter")
        if isinstance(step_counter, (int, float)):
            self.step_counter = max(0, int(step_counter))

        perception_counter = state_dict.get("perceptions_since_reflection")
        if isinstance(perception_counter, (int, float)):
            self.perceptions_since_reflection = max(0, int(perception_counter))

        self._clamp()
        self._enforce_identity_floors()

from __future__ import annotations

import random
import re
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


class VirtualBrain:
    def __init__(
        self,
        chemical_configs: dict,
        interaction_matrix: dict = None,
        decision_engine=None,
        feedback_multiplier: float = 1.0,
        deterministic: bool = False,
    ):
        self.deterministic = deterministic
        self.feedback_multiplier = feedback_multiplier
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

        self.current_focus: Thought | None = None
        self.experience = 0.0
        self.intelligence = 0.5
        self.wisdom = 0.0

        self.last_prediction_error = 1.0
        self.previous_chem_snapshot = {}
        self.risk_tolerance = 0.5
        self.risk_adapt_rate = 0.02

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

        self.interaction_matrix = interaction_matrix or {}
        self.step_counter = 0
        self.recent_perceptions = deque(maxlen=50)
        self.scene_memory = deque(maxlen=25)
        self.concept_memory = {}
        self.stopwords = {
            "the", "a", "an", "and", "or", "but", "with", "to", "of", "in", "on",
            "under", "for", "at", "is", "are", "was", "were", "has", "have", "had",
            "this", "that", "it", "its", "as", "by", "from", "near",
            "object", "objects", "attribute", "attributes", "relation", "relations",
            "motion", "confidence",
            "speaker", "text", "keyword", "keywords", "sentiment", "prosody",
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
        self.development_stage = "baby"
        self.stage_learning_multipliers = {
            "baby": 0.7,
            "child": 1.0,
            "teen": 1.25,
            "adult": 1.5,
        }
        self.reflection_interval = 12
        self._reflection_consciousness_boost = 0.0

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

    def tick(self):
        decision_output = None
        regret = 0.0

        self._apply_interactions()
        self._apply_homeostasis()
        self._apply_noise()
        self._clamp()

        self._update_resilience()
        self._update_reflection_balance()

        self.development.reflect(self.identity.get("intelligence"))
        self.development.update()

        if self.fatigue < 0.6:
            self.identity.update()

        self._encode_autobiography()

        generate_spontaneous(self)
        self.current_focus = GlobalWorkspace.select()

        if self.decision_engine and self.current_focus:
            decision_output = self.decision_engine.decide(self.current_focus)
            feedback = decision_output.get("feedback", {})
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
        self._periodic_reflection()
        self.consciousness.compute_score(self)
        if self._reflection_consciousness_boost > 0.0:
            self.consciousness.score = min(1.0, self.consciousness.score + self._reflection_consciousness_boost)
            self._reflection_consciousness_boost *= 0.9
        self.consciousness.modulate_risk(self, self.consciousness.score)
        self.consciousness.update_narrative(self, self.consciousness.score)

        self.step_counter += 1
        return decision_output

    def perceive(self, event: Any) -> None:
        """Process a meaningful experience event generated by the environment."""
        def _read(name: str, default: Any):
            if hasattr(event, name):
                return getattr(event, name)
            if isinstance(event, dict):
                return event.get(name, default)
            return default

        category = str(_read("category", "")).strip().lower()
        content = str(_read("content", "")).strip()
        valence = float(_read("valence", 0.0))
        intensity = float(_read("intensity", 0.0))
        source = str(_read("source", "simulated"))
        timestamp = float(_read("timestamp", 0.0))

        if not content:
            return

        valence = max(-1.0, min(1.0, valence))
        intensity = max(0.0, min(1.0, intensity))

        scene = self._analyze_perception(modality="experience", content=f"{category} {content}")
        self.recent_perceptions.append(
            {
                "modality": "experience",
                "content": content,
                "category": category,
                "source": source,
                "valence": valence,
                "intensity": intensity,
                "timestamp": timestamp,
                "scene": scene,
            }
        )
        self.scene_memory.append(scene)
        self._learn_from_perception("experience", f"{category} {content}", source=source, scene=scene)

        positive = max(0.0, valence)
        negative = max(0.0, -valence)
        effects = {
            "dopamine": (2.0 + 8.0 * positive) * intensity,
            "oxytocin": (1.0 + 6.0 * positive if category in {"greeted", "praise", "success"} else 0.5) * intensity,
            "serotonin": (1.0 + 5.0 * positive) * intensity,
            "cortisol": (1.0 + 8.0 * negative) * intensity,
        }
        if category in {"loneliness", "ignored", "boredom"}:
            effects["oxytocin"] -= 2.0 * intensity
            effects["dopamine"] -= 1.5 * intensity

        self.inject_event(
            effects=effects,
            event_type=category or "experience",
            source=source,
            tags=["synthetic_experience", category or "experience"],
        )

        self.autobiography.record_event(
            description=f"perceived_{category or 'experience'}: {content}",
            chemicals={k: v["value"] for k, v in self.chemicals.items()},
            identity_snapshot=self.identity.get_snapshot(),
            metadata=asdict(event) if hasattr(event, "__dataclass_fields__") else dict(event),
        )
        self.autobiography.propose_memory_thought(self)

        self.development.observe_event(category or "experience", {k: v["value"] for k, v in self.chemicals.items()})

        event_thought = Thought(
            content=f"Experienced {category or 'event'}: {content}",
            source="perception",
            emotional_weight=min(1.0, abs(valence) * (0.6 + 0.4 * intensity)),
            novelty=min(1.0, 0.5 + scene.get("novelty", 0.0) * 0.5),
            relevance_to_goals=0.25 + (0.2 if category in {"success", "failure", "praise"} else 0.0),
            metadata={"category": category, "valence": valence, "intensity": intensity},
        )
        GlobalWorkspace.post(event_thought)

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
                self.chemicals[chem]["value"] += delta * anticipation_strength

        previous_state = {name: self.chemicals[name]["value"] for name in self.chemicals}
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
                    delta *= 1 - resilience * 0.5
                if chem == "cortisol" and resilience > 0:
                    delta *= 1 - resilience * 0.4
                self.chemicals[chem]["value"] += delta

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
        self.development.maturity += (maturity_target - self.development.maturity) * 0.05
        self.development.maturity = max(0, min(1.0, self.development.maturity))

        self.previous_chem_snapshot = {k: self.chemicals[k]["value"] for k in self.chemicals}

    def _periodic_reflection(self) -> None:
        if self.step_counter <= 0 or (self.step_counter % self.reflection_interval) != 0:
            return

        recent = self.autobiography.get_recent_events(20)
        if not recent:
            return

        self.development.reflection_depth += 0.2 + (0.01 * len(recent))
        self.self_reflection.wisdom = min(1.0, self.self_reflection.wisdom + 0.01)
        self.wisdom = min(1.0, self.wisdom + 0.005)
        self._reflection_consciousness_boost = min(0.25, self._reflection_consciousness_boost + 0.02)
        self.narrative_engine.update_narrative(recent)

        reflect_thought = Thought(
            content=f"I am reflecting on {len(recent)} recent experiences.",
            source="internal",
            emotional_weight=0.2,
            novelty=0.3,
            relevance_to_goals=0.5,
        )
        GlobalWorkspace.post(reflect_thought)

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

        effects = {}
        event_type = "observation"

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

        scene = self._analyze_perception(modality=modality, content=content)
        self.recent_perceptions.append(
            {
                "modality": modality,
                "content": content,
                "source": source,
                "scene": scene,
            }
        )
        self.scene_memory.append(scene)
        self._learn_from_perception(modality=modality, content=content, source=source, scene=scene)

        self.inject_event(
            effects=effects,
            event_type=event_type,
            source=source,
            tags=[modality, "perception"],
        )

        scene_summary = scene.get("summary", content[:80])
        th = Thought(
            content=f"Perceived {modality}: {scene_summary[:120]}",
            source="perception",
            emotional_weight=min(1.0, 0.15 + scene.get("salience", 0.0) * 0.2),
            novelty=min(1.0, 0.6 + scene.get("novelty", 0.0) * 0.3),
            relevance_to_goals=min(1.0, 0.2 + scene.get("task_relevance", 0.0) * 0.4),
            metadata={"scene": scene},
        )
        GlobalWorkspace.post(th)

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

        rel_descriptions = []
        for rel in relations:
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

        self.observe_perception(modality="vision", content=scene_text, source=source)

        # Add small affective modulation from visual dynamics/confidence.
        dynamic_boost = motion_level * 0.8
        ambiguity_stress = (1.0 - confidence) * 1.2
        self.inject_event(
            effects={
                "dopamine": dynamic_boost,
                "cortisol": ambiguity_stress,
            },
            event_type="vision_signal",
            source=source,
            tags=["vision", "structured_signal"],
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

        hearing_text = (
            f"speaker={speaker_type} | text={transcript} | "
            f"sentiment={sentiment:.2f} | prosody={prosody_intensity:.2f} | "
            f"keywords={','.join(keywords)}"
        )

        self.observe_perception(modality="hearing", content=hearing_text, source=source)

        positive = max(0.0, sentiment)
        negative = max(0.0, -sentiment)
        social_bonus = 0.4 if speaker_type in {"caregiver", "teacher", "peer"} else 0.2
        empathy_keywords = {"praise", "support", "collaboration", "greeted", "social"}
        stress_keywords = {"criticism", "ignored", "lonely", "threat"}

        keyword_boost = sum(0.15 for k in keywords if k in empathy_keywords)
        keyword_stress = sum(0.2 for k in keywords if k in stress_keywords)

        effects = {
            "oxytocin": (social_bonus + 3.0 * positive + keyword_boost) * prosody_intensity,
            "dopamine": (1.0 + 2.0 * positive + keyword_boost) * prosody_intensity,
            "serotonin": (0.8 + 2.2 * positive) * prosody_intensity,
            "cortisol": (0.5 + 3.0 * negative + keyword_stress) * prosody_intensity,
        }
        self.inject_event(
            effects=effects,
            event_type="hearing_signal",
            source=source,
            tags=["hearing", "structured_signal", speaker_type],
        )

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

    def _analyze_perception(self, modality: str, content: str) -> dict:
        text = (content or "").lower()
        tokens = [self._normalize_token(t) for t in re.findall(r"[a-zA-Z]+", text)]

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

        relations = []
        for i, tok in enumerate(tokens):
            if tok in relation_markers and i > 0 and i < len(tokens) - 1:
                left = tokens[i - 1]
                right = tokens[i + 1]
                if left in entity_vocab and right in entity_vocab:
                    relations.append({"from": left, "rel": tok, "to": right})

        known_concepts = set(self.concept_memory.keys())
        novelty_hits = [c for c in set(entities + attributes) if c not in known_concepts]
        novelty = 0.0 if not tokens else min(1.0, len(novelty_hits) / max(1, len(set(tokens))))

        salience = min(1.0, (len(set(entities)) * 0.25) + (len(relations) * 0.2) + (len(set(attributes)) * 0.1))
        task_relevance = min(1.0, 0.3 if "person" in entities else 0.0 + (0.2 if "camera" in entities else 0.0))
        confidence = min(1.0, 0.4 + 0.1 * len(entities) + 0.1 * len(relations))

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
            "novelty": novelty,
            "salience": salience,
            "task_relevance": task_relevance,
            "confidence": confidence,
            "summary": summary,
        }

    def _extract_concepts(self, text):
        tokens = re.findall(r"[a-zA-Z]+", (text or "").lower())
        concepts = []
        for tok in tokens:
            if len(tok) < 3:
                continue
            mapped = self._normalize_token(tok)
            if mapped and len(mapped) >= 3 and mapped not in self.stopwords:
                concepts.append(mapped)
        return concepts

    def _learn_from_perception(self, modality, content, source, scene=None):
        scene = scene or {}
        concepts = self._extract_concepts(content)
        concepts.extend(scene.get("entities", []))
        concepts.extend(scene.get("attributes", []))
        if not concepts:
            return

        now_step = self.step_counter
        stage_rate = {
            "baby": 0.05,
            "child": 0.07,
            "teen": 0.09,
            "adult": 0.11,
        }.get(self.development_stage, 0.07)

        confidence = scene.get("confidence", 0.5)
        salience = scene.get("salience", 0.3)
        learning_gain = stage_rate * (0.6 + 0.4 * confidence) * (0.6 + 0.4 * salience)

        for concept in set(concepts):
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
        stage = state.get("development_stage", "baby")

        if fatigue > 0.7 or cortisol > 70:
            parts = controlled.split(".")
            controlled = parts[0].strip()
            if not controlled.endswith((".", "!", "?")):
                controlled += "."

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
        cortisol = self.chemicals.get("cortisol", {}).get("value", 0)

        if cortisol > self.stress_threshold:
            self.stress_accumulator += 1
            self.recovery_counter = 0
        else:
            self.recovery_counter += 1

        if 1 <= self.stress_accumulator <= 4 and self.recovery_counter > 3:
            self.identity.add_evidence("resilience", self.resilience_growth_rate)
            self.stress_accumulator = 0

        if cortisol > self.burnout_threshold:
            self.identity.add_evidence("resilience", -self.resilience_damage_rate)

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
                self.chemicals[chem]["value"] += delta * self.feedback_multiplier

    def _clamp(self):
        for data in self.chemicals.values():
            data["value"] = max(data["min"], min(data["value"], data["max"]))

    def _encode_autobiography(self):
        self.autobiography.record_event(
            description="cycle_step",
            chemicals={k: v["value"] for k, v in self.chemicals.items()},
            identity_snapshot=self.identity.get_snapshot(),
        )
        self.autobiography.propose_memory_thought(self)

        if self.step_counter % 25 == 0:
            recent = self.autobiography.get_recent_events(100)
            self.narrative_engine.update_narrative(recent)

            narrative_bias = self.narrative_engine.get_identity_bias()
            for trait, delta in narrative_bias.items():
                self.identity.add_evidence(trait, delta * 0.1)

            narrative_thought = Thought(
                content=f"Narrative update: {self.narrative_engine.get_current_narrative()}",
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
        self.development_stage = self._compute_development_stage()

        state = {name: data["value"] for name, data in self.chemicals.items()}
        state.update({f"identity_{k}": v for k, v in self.identity.get_snapshot().items()})
        state.update({f"development_{k}": v for k, v in self.development.get_snapshot().items()})
        state.update(
            {
                "fatigue": self.fatigue,
                "self_narrative": self.narrative_engine.get_current_narrative(),
                "wisdom": self.self_reflection.get_wisdom(),
            }
        )

        state["intelligence"] = self.intelligence
        state["experience"] = self.experience
        state["development_stage"] = self.development_stage
        state["recent_perceptions"] = list(self.recent_perceptions)[-5:]
        state["learned_concepts"] = self.get_top_concepts(8)
        state["consciousness_score"] = getattr(self.consciousness, "score", 0.0)

        return state

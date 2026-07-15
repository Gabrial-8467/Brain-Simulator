from __future__ import annotations

import os
import random
import re
import time
import copy
from collections import deque
from dataclasses import asdict
from typing import Any

from core.attention import GlobalWorkspace, Thought
from core.consciousness import Consciousness
from core.development import DynamicDevelopment
from core.identity import DynamicIdentity
from core.internal_thoughts import generate_spontaneous
from core.self_reflection import SelfReflection
from chemicals.registry import ChemicalRegistry
from bias.bias_engine import BiasEngine
from development.attachment_system import AttachmentSystem
from development.curiosity_engine import CuriosityEngine
from development.goal_system import GoalSystem

from utils.text_processor import TextProcessor
from utils.speech_regulator import SpeechRegulator
from core.sensory_parser import SensoryParser
from core.sleep_manager import SleepManager

DEFAULT_BIAS_CONFIGS = {
    "negativity_bias": {
        "core_range": 0.1,
        "min": -1.0,
        "max": 1.0,
        "decay": 0.0003,
        "delta_threshold": 5.0,
        "imprint_factor": 0.001,
    },
    "optimism_bias": {
        "core_range": 0.1,
        "min": -1.0,
        "max": 1.0,
        "decay": 0.0003,
        "delta_threshold": 5.0,
        "imprint_factor": 0.001,
    }
}

DEFAULT_BIAS_MAPPING = {
    "negativity_bias": {
        "imprint_from": ["cortisol"],
        "baseline_shift": {
            "cortisol": 5.0
        },
        "reaction_scale": {
            "cortisol": 0.15
        },
        "decision_bias": {
            "refuse": 0.05,
            "neutral": 0.03,
            "support": -0.05
        }
    },
    "optimism_bias": {
        "imprint_from": ["dopamine"],
        "baseline_shift": {
            "dopamine": 3.0,
            "serotonin": 2.0
        },
        "reaction_scale": {
            "dopamine": 0.1
        },
        "decision_bias": {
            "support": 0.05,
            "suggest": 0.04
        }
    }
}

from cognition.autobiographical_memory import AutobiographicalMemory
from cognition.belief_engine import BeliefEngine
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
        worldview_config: dict | None = None,
        global_workspace: Any = None,
    ):
        self.deterministic = deterministic
        self.feedback_multiplier = feedback_multiplier
        self.decision_feedback_scale = 0.45
        self.love_score = 0.0
        self.loved_source = None
        self.decision_engine = decision_engine
        self.global_workspace = global_workspace or GlobalWorkspace.get_default()

        self.identity = DynamicIdentity()
        self.development = DynamicDevelopment()
        self.consciousness = Consciousness()

        self.autobiography = AutobiographicalMemory()
        self.narrative_engine = NarrativeEngine()
        self.worldview = BeliefEngine(worldview_config)

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
        self._step_perception_signals: list[dict[str, Any]] = []
        self._step_perception_novelty = 0.0
        self.sleeping = False
        self.sleep_ticks_left = 0
        self.network_mode = "TPN"
        self.hopfield_weights = [[0.0 for _ in range(9)] for _ in range(9)]
        self.attachment_system = AttachmentSystem()
        self.curiosity_engine = CuriosityEngine()
        self.goal_system = GoalSystem()
        self._social_decay_hold_counter = 0
        self._high_emotion_window = deque(maxlen=10)
        self._decision_debug: dict[str, Any] = {}
        self._high_stress_steps = 0
        self._low_serotonin_steps = 0
        self._step_adversity_intensity = 0.0
        self._chronic_stress_steps = 0
        self._emotional_dip_active = False
        self._comfort_steps = 0
        self._last_maturity = 0.0
        self._last_concept_count = 0
        self._concept_stagnation_steps = 0
        self._last_concept_warning_step = -1000
        self.recent_perceptions = deque(maxlen=50)
        self.scene_memory = deque(maxlen=25)
        self.novelty_memory = deque(maxlen=50)
        self.text_processor = TextProcessor()
        self.speech_regulator = SpeechRegulator()
        self.sensory_parser = SensoryParser(self.text_processor)
        self.sleep_manager = SleepManager(cycle_period=100)

        self._scene_counts = self.sensory_parser.scene_counts
        self.stopwords = self.text_processor.stopwords
        self.concept_aliases = self.text_processor.concept_aliases
        self.concept_memory = {}
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

        self.chemicals = ChemicalRegistry(chemical_configs)
        self._original_baselines = {name: float(config["baseline"]) for name, config in chemical_configs.items()}
        self.bias_engine = BiasEngine(DEFAULT_BIAS_CONFIGS, DEFAULT_BIAS_MAPPING)
        self._last_maturity = self.development.maturity

    def _run_sleep_cycle(self) -> dict[str, Any]:
        return self.sleep_manager.run_sleep_cycle(self)

    def tick(self):
        if self.sleeping:
            return self._run_sleep_cycle()

        # 1. Update sleep drives and Process S/Process C dynamics
        self.sleep_manager.update_sleep_drives(self)

        # 2. Check sleep triggers
        if self.sleep_manager.should_sleep(self):
            self.sleeping = True
            self.sleep_ticks_left = 5
            return self._run_sleep_cycle()

        # 3. Dynamic Acetylcholine (ACh) attention focus tracking
        if "acetylcholine" in self.chemicals:
            streak = getattr(self.global_workspace, "_streak", 0) or getattr(self.global_workspace, "streak", 0)
            self.chemicals["acetylcholine"]["value"] = min(100.0, self.chemicals["acetylcholine"]["value"] + streak * 3.5)
            self._clamp()
            ach_val = self.chemicals["acetylcholine"]["value"] / 100.0
            if self.decision_engine:
                self.decision_engine.learning_rate = 0.05 + 0.15 * ach_val

        decision_output = None
        regret = 0.0
        prev_maturity = self.development.maturity

        for name in self.chemicals.keys():
            self.chemicals[name]["baseline"] = self._original_baselines[name]

        conscious_values = {k: v["value"] for k, v in self.chemicals.items()}
        baseline_values = {k: self._original_baselines[k] for k in self.chemicals.keys()}
        self.bias_engine.update_from_conscious(conscious_values, baseline_values)
        self.bias_engine.apply_baseline_shift(self.chemicals)

        self._apply_interactions()
        self._apply_homeostasis()
        self._apply_noise()
        self._clamp()

        if "norepinephrine" in self.chemicals:
            ne_val = self.chemicals["norepinephrine"]["value"]
            ne_baseline = self.chemicals["norepinephrine"]["baseline"]
            ne_decay = self.chemicals["norepinephrine"]["decay"]
            ne_val += (ne_baseline - ne_val) * ne_decay
            ne_val += self._step_perception_novelty * 15.0
            cort_delta = max(0.0, self.chemicals["cortisol"]["value"] - self.previous_chem_snapshot.get("cortisol", 40.0))
            ne_val += cort_delta * 0.25
            self.chemicals["norepinephrine"]["value"] = max(0.0, min(100.0, ne_val))
            self._clamp()

        self.chemicals.update_receptor_dynamics()

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
        if cortisol > 58.0:
            self._chronic_stress_steps += 1
        else:
            self._chronic_stress_steps = max(0, self._chronic_stress_steps - 1)

        self.worldview.update_mood(self._step_perception_signals)

        self._update_resilience()
        self._update_reflection_balance()

        self.development.reflect(self.identity.get("intelligence"))
        self.development.update()

        if self.fatigue < 0.6:
            self.identity.update()
        self._apply_social_value_decay()
        self._enforce_identity_floors()

        self._encode_autobiography()
        belief_update = self._update_worldview()

        # Salience Network updates cognitive mode (TPN vs. DMN)
        ne_val = self.chemicals.get("norepinephrine", {}).get("value", 50.0)
        if ne_val > 65.0 or self._step_perception_signals:
            self.network_mode = "TPN"
        else:
            self.network_mode = "DMN"

        generate_spontaneous(self)
        self.current_focus = self.global_workspace.select(
            norepinephrine=ne_val,
            network_mode=self.network_mode,
            love_score=self.love_score,
            loved_source=self.loved_source,
        )

        # Calculate active Love Score based on current focus and chemical levels
        self.love_score = 0.0
        self.loved_source = None
        if self.current_focus and hasattr(self, "attachment_system") and self.attachment_system:
            c_source = self.current_focus.source or ""
            attach = self.attachment_system.get_attachment(c_source)
            if attach > 0.6:
                oxt = self.chemicals["oxytocin"]["value"] if "oxytocin" in self.chemicals else 0.0
                da = self.chemicals["dopamine"]["value"] if "dopamine" in self.chemicals else 0.0
                if oxt > 60.0 and da > 60.0:
                    self.love_score = attach * (oxt / 100.0) * (da / 100.0)
                    self.loved_source = c_source
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
            "belief_count": int(belief_update.get("belief_count", 0)),
            "belief_shift": float(belief_update.get("max_conf_shift", 0.0)),
            "mood_valence": float(self.worldview.mood_state.get("valence", 0.0)),
            "mood_tone": str(self.worldview.mood_state.get("tone", "neutral")),
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
            decision_state = self.get_state()
            decision_state["decision_action_bias"] = self.worldview.decision_bias()
            decision_output = self.decision_engine.decide(
                self.current_focus,
                state=decision_state,
                recent_valence_avg=recent_valence_avg,
                bias_engine=self.bias_engine,
            )
            if decision_output and "probabilities" in decision_output:
                best_action = self.strategic_planner.choose_action(self, decision_output["probabilities"])
                decision_output["action"] = best_action
                decision_output["feedback"] = self.decision_engine.action_feedback.get(best_action, {})
                self._decision_debug["decision_path"] = "strategic_planner"
            else:
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
                self.worldview.record_decision_outcome(
                    action=action,
                    success=bool(regret <= 0.05),
                    intensity=float(getattr(self.current_focus, "emotional_weight", 0.5) or 0.5),
                )

                if self.decision_engine and hasattr(self.decision_engine, "update_q_value"):
                    reward = 1.0 - (regret * 2.0)
                    mood_tone = str(self.worldview.mood_state.get("tone", "neutral")).lower()
                    rpe = self.decision_engine.update_q_value(mood_tone, action, reward)
                    dopamine_change = rpe * 5.0
                    dopamine_change = max(-10.0, min(10.0, dopamine_change))
                    self.chemicals["dopamine"]["value"] = max(0.0, min(100.0, self.chemicals["dopamine"]["value"] + dopamine_change))
                    self._clamp()

        self._update_cognitive_growth(regret)

        # Spike Endorphins on regret resolution and apply physiological buffering
        if regret > 0.0 and "endorphins" in self.chemicals:
            self.chemicals["endorphins"]["value"] = min(100.0, self.chemicals["endorphins"]["value"] + regret * 25.0)
            self._clamp()

        if "endorphins" in self.chemicals:
            endorphin_val = self.chemicals["endorphins"]["value"]
            if "cortisol" in self.chemicals:
                self.chemicals["cortisol"]["value"] = max(0.0, self.chemicals["cortisol"]["value"] - endorphin_val * 0.15)
            if "serotonin" in self.chemicals:
                self.chemicals["serotonin"]["value"] = min(100.0, self.chemicals["serotonin"]["value"] + endorphin_val * 0.10)
            self._clamp()

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

        # Decay social attachment and goals
        if hasattr(self, "attachment_system") and self.attachment_system:
            self.attachment_system.decay()
        if hasattr(self, "goal_system") and self.goal_system:
            self.goal_system.decay()

        # Dopaminergic reward for exploring curious thoughts
        if self.current_focus and hasattr(self, "curiosity_engine") and self.curiosity_engine:
            c_topic = self.current_focus.topic or self.current_focus.metadata.get("category") or self.current_focus.source
            c_bonus = self.curiosity_engine.get_curiosity_bonus(c_topic)
            if c_bonus > 0.6:
                if "dopamine" in self.chemicals:
                    self.chemicals["dopamine"]["value"] += c_bonus * 12.0
                    self._clamp()

        # Update active goal strength based on chosen action outcome
        if decision_output and hasattr(self, "goal_system") and self.goal_system:
            action = decision_output.get("action")
            if action:
                reward = 1.0 - regret
                if action in {"support", "suggest"}:
                    self.goal_system.create_or_update_goal("social_bond", reward)
                if action in {"challenge", "suggest"}:
                    self.goal_system.create_or_update_goal("task_mastery", reward)
                if action in {"refuse", "neutral"}:
                    self.goal_system.create_or_update_goal("safety", reward)

        self.step_counter += 1
        self.memory_manager.flush_pending()
        self._step_perception_valences = []
        self._step_perception_signals = []
        self._step_perception_novelty = 0.0
        self._step_adversity_intensity = 0.0
        return decision_output

    def perceive(self, event: Any) -> None:
        """Process a meaningful experience event generated by the environment."""
        def _read(name, default):
            if hasattr(event, "get"):
                return event.get(name, default)
            if hasattr(event, name):
                return getattr(event, name)
            if isinstance(event, dict):
                return event.get(name, default)
            return default

        if self.sleeping:
            category = str(_read("category", "")).strip().lower()
            intensity = float(_read("intensity", 0.0))
            if category == "threat_detected" and intensity >= 0.8:
                self.sleeping = False
                self.sleep_ticks_left = 0
            else:
                return

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

        # 1. Observe event in Curiosity Engine
        self.curiosity_engine.observe(category or modality)

        # 2. Process Social Attachment updates and appraisals
        reward_signal = max(0.0, valence)
        stress_signal = max(0.0, -valence)
        if source:
            self.attachment_system.update(source, reward_signal, stress_signal)
            attach_val = self.attachment_system.get_attachment(source)
            if attach_val > 0.0:
                # Buffer stress impact
                if valence < 0.0:
                    valence = valence * (1.0 - attach_val * 0.5)
                    intensity = intensity * (1.0 - attach_val * 0.4)
                # Boost oxytocin responses
                if "oxytocin" in self.chemicals:
                    self.chemicals["oxytocin"]["value"] += attach_val * 10.0
                    self._clamp()

        # 3. Process Adrenaline (Epinephrine) acute threat spikes
        if category == "threat_detected" and "adrenaline" in self.chemicals:
            self.chemicals["adrenaline"]["value"] = min(100.0, self.chemicals["adrenaline"]["value"] + intensity * 45.0)
            self._clamp()

        # 4. Apply Love Emotion additional cortisol stress buffering
        if self.love_score > 0.5:
            if valence < 0.0:
                valence = valence * (1.0 - self.love_score * 0.7)
                intensity = intensity * (1.0 - self.love_score * 0.6)

        expected_valence = self.worldview.expected_valence(category or modality)
        valence, intensity = self.worldview.adjust_appraisal(
            category=category or modality,
            content=content,
            valence=valence,
            intensity=intensity,
            modality=modality,
        )
        self.worldview.record_prediction(expected_valence=expected_valence, actual_valence=valence)
        self._step_perception_valences.append(valence)
        self._step_perception_signals.append(
            {
                "category": category or modality,
                "modality": modality,
                "valence": valence,
                "intensity": intensity,
            }
        )
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
        self._step_perception_novelty = max(self._step_perception_novelty, float(scene.get("novelty", 0.0)))
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

        self._record_memory_event(
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
        self.global_workspace.post(event_thought)

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
        resilience = max(0.0, float(self.identity.get("resilience")))
        effective_resilience = resilience / (1.0 + resilience)
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
                scaled_delta = self.bias_engine.scale_reaction(chem, float(delta))
                bounded = max(-8.0, min(8.0, scaled_delta))
                if chem in ["dopamine", "serotonin"] and bounded < 0:
                    bounded *= 1 - effective_resilience * 0.5
                if chem == "cortisol":
                    bounded *= 1 - effective_resilience * 0.4
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
        self.global_workspace.post(reflect_thought)

    def _summarize_recent_perceptions(self, recent_perceptions: list[dict]) -> str:
        counts: dict[str, int] = {}
        for item in recent_perceptions:
            cat = str(item.get("category", "observation") or "observation").lower()
            counts[cat] = counts.get(cat, 0) + 1
        top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:3]
        summary = ", ".join([f"{k}:{v}" for k, v in top]) if top else "no dominant pattern"
        return f"I reflected over {len(recent_perceptions)} perceptions: {summary}"

    def _update_worldview(self) -> dict[str, Any]:
        recent_events = self.autobiography.get_recent_events(self.worldview.event_window)
        belief_update = self.worldview.extract_beliefs(
            events=recent_events,
            step_counter=self.step_counter,
            reflection_depth=self.development.reflection_depth,
        )
        if belief_update.get("updated"):
            self.memory_manager.create_memory(
                memory_type="belief_update",
                content={
                    "beliefs": self.worldview.get_active_beliefs(limit=8, min_confidence=0.2),
                    "max_conf_shift": belief_update.get("max_conf_shift", 0.0),
                    "step_counter": self.step_counter,
                },
                metadata={"source": "worldview_engine"},
            )

        drift = self.worldview.identity_drift(
            cortisol=float(self.chemicals.get("cortisol", {}).get("value", 0.0)),
            identity_snapshot=self.identity.get_snapshot(),
        )
        for trait, delta in drift.items():
            self.identity.add_evidence(trait, delta)

        if self.worldview.should_rewrite_narrative(
            step_counter=self.step_counter,
            max_conf_shift=float(belief_update.get("max_conf_shift", 0.0)),
        ):
            narrative = self.worldview.compose_narrative(
                identity_snapshot=self.identity.get_snapshot(),
                stage=self.development_stage,
                existing_narrative=self.narrative_engine.get_current_narrative(),
            )
            if narrative and narrative != self.narrative_engine.get_current_narrative():
                self.narrative_engine.current_narrative = narrative
                self.worldview.mark_narrative_rewrite(self.step_counter)
                self._record_memory_event(
                    description=f"worldview_narrative_rewrite: {narrative}",
                    chemicals={k: v["value"] for k, v in self.chemicals.items()},
                    identity_snapshot=self.identity.get_snapshot(),
                    metadata={
                        "type": "worldview_narrative_rewrite",
                        "belief_shift": belief_update.get("max_conf_shift", 0.0),
                    },
                )
                self.global_workspace.post(
                    Thought(
                        content=f"I revised my worldview narrative: {narrative}",
                        source="internal",
                        emotional_weight=0.35,
                        novelty=0.4,
                        relevance_to_goals=0.6,
                    )
                )

        return belief_update

    def _refresh_narrative(self, force: bool = False) -> None:
        if not force:
            return
        if self.worldview.get_active_beliefs(limit=1, min_confidence=0.3):
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

        self._record_memory_event(
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
        self.global_workspace.post(transition_thought)
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
        if self.worldview.get_active_beliefs(limit=1, min_confidence=0.35):
            return

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
                max(0.0, float(self.identity.traits["resilience"])),
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
        parsed = self.sensory_parser.parse_visual_signal(signal)
        if parsed:
            self.perceive(parsed)

    def receive_hearing_signal(self, signal: Any) -> None:
        parsed = self.sensory_parser.parse_hearing_signal(signal)
        if parsed:
            self.perceive(parsed)

    def _normalize_token(self, token: str) -> str:
        return self.text_processor.normalize_token(token)

    def _analyze_perception(
        self,
        modality: str,
        content: str,
        valence: float = 0.0,
        provided_scene: dict | None = None,
    ) -> dict:
        return self.sensory_parser.analyze_perception(modality, content, valence, provided_scene)

    def _extract_concepts(self, text, modality: str = "experience"):
        return self.text_processor.extract_concepts(text, modality)

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
        state = self.get_state()
        return self.speech_regulator.regulate(
            text=text,
            fatigue=self.fatigue,
            cortisol=state.get("cortisol", 50.0),
            oxytocin=state.get("oxytocin", 50.0),
            stage=self.development_stage
        )

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
        resilience = max(0.0, float(self.identity.traits.get("resilience", 0.5)))

        cortisol = float(self.chemicals.get("cortisol", {}).get("value", 0.0))
        dopamine = float(self.chemicals.get("dopamine", {}).get("value", 0.0))
        serotonin = float(self.chemicals.get("serotonin", {}).get("value", 0.0))

        in_emotional_dip = has_negative_step or dopamine < 56.0 or serotonin < 56.0
        if in_emotional_dip:
            self._emotional_dip_active = True

        if self._chronic_stress_steps >= 5:
            stress_load = max(0.0, (cortisol - 55.0) / 25.0)
            stress_loss = 0.003 * (1.0 + min(1.5, stress_load))
            resilience -= stress_loss * (1.0 + min(1.0, resilience / 2.5))

        recovered = (
            self._emotional_dip_active
            and cortisol < 54.0
            and dopamine > 57.0
            and serotonin > 58.0
        )
        if recovered:
            recovery_strength = 0.004 + (0.004 * max(0.0, (serotonin - 58.0) / 20.0))
            soft_headroom = max(0.1, 2.5 - resilience)
            resilience += recovery_strength * (soft_headroom / 2.5)
            self._emotional_dip_active = False

        if adversity_intensity > 0.0 or has_negative_step:
            hardening = 0.0015 * max(0.2, adversity_intensity)
            survival_factor = max(0.2, 1.0 - max(0.0, cortisol - 45.0) / 70.0)
            resilience += hardening * survival_factor
            self._comfort_steps = 0
            self.stress_accumulator += 1
            self.recovery_counter = 0
        else:
            self._comfort_steps += 1
            self.recovery_counter += 1
            if self._comfort_steps >= 12 and cortisol < 50.0:
                complacency = 0.0008 * max(0.2, resilience / 2.5)
                resilience -= complacency

        self.identity.traits["resilience"] = round(max(0.0, resilience), 4)

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

    def _binarize_state(self, chemicals: dict, identity: dict) -> list[int]:
        chems = ["dopamine", "cortisol", "oxytocin", "serotonin", "norepinephrine"]
        traits = ["competence", "social_value", "resilience", "intelligence"]
        vec = []
        for c in chems:
            val = chemicals.get(c, 50.0)
            if isinstance(val, dict):
                val = val.get("value", 50.0)
            vec.append(1 if float(val) >= 50.0 else -1)
        for t in traits:
            val = identity.get(t, 0.5)
            vec.append(1 if float(val) >= 0.5 else -1)
        return vec

    def _project_hebbian_learning(self, chemicals: dict, identity: dict):
        p = self._binarize_state(chemicals, identity)
        ach_val = 50.0
        ach = chemicals.get("acetylcholine")
        if ach:
            ach_val = ach.get("value", 50.0) if isinstance(ach, dict) else float(ach)
        ach_scale = ach_val / 100.0
        update_multiplier = 0.3 + 1.2 * ach_scale

        for i in range(9):
            for j in range(9):
                if i != j:
                    self.hopfield_weights[i][j] += float(p[i] * p[j]) * update_multiplier

    def _record_memory_event(self, description: str, chemicals: dict, identity_snapshot: dict, metadata: dict = None):
        self.autobiography.record_event(
            description=description,
            chemicals=chemicals,
            identity_snapshot=identity_snapshot,
            metadata=metadata,
        )
        if description != "cycle_step":
            self._project_hebbian_learning(chemicals, identity_snapshot)

    def _encode_autobiography(self):
        self._record_memory_event(
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

        if self.step_counter % 25 == 0 and not self.worldview.get_active_beliefs(limit=1, min_confidence=0.3):
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
            self.global_workspace.post(narrative_thought)

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
        effective_chemical_values = {name: data.effective_value for name, data in self.chemicals.items()}
        receptor_sensitivities = {name: data.sensitivity for name, data in self.chemicals.items()}
        identity_snapshot = self.identity.get_snapshot()
        development_snapshot = self.development.get_snapshot()
        narrative = self.narrative_engine.get_current_narrative()
        wisdom = self.self_reflection.get_wisdom()
        consciousness_score = getattr(self.consciousness, "score", 0.0)
        worldview_state = self.worldview.to_state()
        consciousness_components = self.worldview.get_consciousness_factors(
            reflection_depth=self.development.reflection_depth,
            narrative=narrative,
        )

        # Fetch attachment value of the active focus source
        focus_source = "simulated"
        if self.current_focus:
            focus_source = self.current_focus.metadata.get("original_event", {}).get("source") or self.current_focus.source
            if not focus_source or focus_source in {"memory", "internal", "emotion", "goal", "perception"}:
                if self.recent_perceptions:
                    focus_source = self.recent_perceptions[-1].get("source") or "simulated"
        attach_val = 0.0
        if hasattr(self, "attachment_system") and self.attachment_system:
            attach_val = self.attachment_system.get_attachment(focus_source)

        state = {}
        state.update(chemical_values)
        state.update({f"identity_{k}": v for k, v in identity_snapshot.items()})
        state.update({f"development_{k}": v for k, v in development_snapshot.items()})
        state["attachment_value"] = attach_val

        state.update(
            {
                # Full nested payload for persistence
                "neurochemicals": chemical_values,
                "effective_neurochemicals": effective_chemical_values,
                "receptor_sensitivities": receptor_sensitivities,
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
                "beliefs": worldview_state.get("beliefs", []),
                "mood_state": worldview_state.get("mood_state", {}),
                "worldview": worldview_state,
                "consciousness_components": consciousness_components,
                "bias_state": self.bias_engine.get_bias_state(),
                "q_table": copy.deepcopy(self.decision_engine.q_table) if self.decision_engine and hasattr(self.decision_engine, "q_table") else {},
                "hopfield_weights": copy.deepcopy(self.hopfield_weights),
                "love_score": self.love_score,
                "loved_source": self.loved_source,
                "attachments": dict(self.attachment_system.attachments) if hasattr(self, "attachment_system") and self.attachment_system else {},
                "curiosity_tracker": dict(self.curiosity_engine.novelty_tracker) if hasattr(self, "curiosity_engine") and self.curiosity_engine else {},
                "goals": dict(self.goal_system.goals) if hasattr(self, "goal_system") and self.goal_system else {},
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

        receptor_sensitivities = state_dict.get("receptor_sensitivities")
        if isinstance(receptor_sensitivities, dict):
            for chem, value in receptor_sensitivities.items():
                if chem in self.chemicals and isinstance(value, (int, float)):
                    self.chemicals[chem].sensitivity = float(value)

        identity_traits = state_dict.get("identity_traits")
        if not isinstance(identity_traits, dict):
            identity_traits = {
                trait: state_dict.get(f"identity_{trait}")
                for trait in self.identity.traits.keys()
                if isinstance(state_dict.get(f"identity_{trait}"), (int, float))
            }

        for trait, value in identity_traits.items():
            if trait in self.identity.traits and isinstance(value, (int, float)):
                numeric = float(value)
                if trait == "social_value":
                    self.identity.traits[trait] = round(max(-0.3, min(1.0, numeric)), 4)
                elif trait == "resilience":
                    self.identity.traits[trait] = round(max(0.0, numeric), 4)
                else:
                    self.identity.traits[trait] = round(max(0.0, min(1.0, numeric)), 4)

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
            self.sleep_manager.process_s = self.fatigue

        step_counter = state_dict.get("step_counter")
        if isinstance(step_counter, (int, float)):
            self.step_counter = max(0, int(step_counter))

        perception_counter = state_dict.get("perceptions_since_reflection")
        if isinstance(perception_counter, (int, float)):
            self.perceptions_since_reflection = max(0, int(perception_counter))

        worldview_payload = state_dict.get("worldview")
        if not isinstance(worldview_payload, dict):
            worldview_payload = {
                "beliefs": state_dict.get("beliefs", []),
                "mood_state": state_dict.get("mood_state", {}),
            }
        self.worldview.load_state(worldview_payload)

        bias_state = state_dict.get("bias_state")
        if bias_state and hasattr(self, "bias_engine"):
            for bias_name, val in bias_state.items():
                if bias_name in self.bias_engine.biases:
                    self.bias_engine.biases[bias_name].value = float(val)

        q_table = state_dict.get("q_table")
        if q_table and self.decision_engine and hasattr(self.decision_engine, "q_table"):
            self.decision_engine.q_table = copy.deepcopy(q_table)

        self.love_score = float(state_dict.get("love_score", 0.0))
        self.loved_source = state_dict.get("loved_source")

        hopfield = state_dict.get("hopfield_weights")
        if isinstance(hopfield, list):
            self.hopfield_weights = copy.deepcopy(hopfield)

        attachments = state_dict.get("attachments")
        if isinstance(attachments, dict) and hasattr(self, "attachment_system") and self.attachment_system:
            self.attachment_system.attachments = copy.deepcopy(attachments)

        curiosity_tracker = state_dict.get("curiosity_tracker")
        if isinstance(curiosity_tracker, dict) and hasattr(self, "curiosity_engine") and self.curiosity_engine:
            self.curiosity_engine.novelty_tracker = copy.deepcopy(curiosity_tracker)

        goals = state_dict.get("goals")
        if isinstance(goals, dict) and hasattr(self, "goal_system") and self.goal_system:
            self.goal_system.goals = copy.deepcopy(goals)

        self._clamp()
        self._enforce_identity_floors()

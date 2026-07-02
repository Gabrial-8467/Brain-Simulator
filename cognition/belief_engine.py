from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


class BeliefEngine:
    """Extracts compact beliefs from lived events and applies worldview effects."""

    def __init__(self, config: dict | None = None) -> None:
        cfg = config or {}
        self.extraction_interval = max(1, int(cfg.get("extraction_interval", 12)))
        self.event_window = max(20, int(cfg.get("event_window", 80)))
        self.min_evidence = max(2, int(cfg.get("min_evidence", 3)))
        self.confidence_smoothing = _clamp(cfg.get("confidence_smoothing", 0.25), 0.05, 0.8)
        self.shift_threshold = _clamp(cfg.get("narrative_shift_threshold", 0.12), 0.02, 0.5)
        self.rewrite_cooldown_steps = max(1, int(cfg.get("narrative_rewrite_cooldown_steps", 20)))

        self.beliefs: dict[str, dict[str, Any]] = {}
        self.mood_state: dict[str, Any] = {
            "valence": 0.0,
            "arousal": 0.0,
            "tone": "neutral",
            "updated_at": time.time(),
        }

        self.action_stats: dict[str, dict[str, int]] = defaultdict(
            lambda: {"attempts": 0, "successes": 0, "failures": 0}
        )
        self.recent_action_outcomes: deque[dict[str, Any]] = deque(maxlen=120)
        self.prediction_hits = 0
        self.prediction_total = 0

        self._last_extract_step = -10_000
        self._last_max_shift = 0.0
        self._last_narrative_rewrite_step = -10_000
        self._last_narrative_mood_valence = 0.0

    @staticmethod
    def _extract_fields(event: dict) -> dict[str, Any]:
        metadata = event.get("metadata", {}) if isinstance(event, dict) else {}
        if not isinstance(metadata, dict):
            metadata = {}
        description = str(event.get("description", "") if isinstance(event, dict) else "")
        category = str(metadata.get("category", "")).strip().lower()
        valence = float(metadata.get("valence", 0.0) or 0.0)
        intensity = float(metadata.get("intensity", 0.0) or 0.0)
        text = f"{description} {metadata.get('content', '')}".lower()
        return {
            "category": category,
            "description": description,
            "text": text,
            "valence": valence,
            "intensity": intensity,
        }

    @staticmethod
    def _belief_payload(
        statement: str,
        confidence: float,
        category: str,
        evidence_count: int,
        now_ts: float,
    ) -> dict[str, Any]:
        return {
            "statement": statement,
            "confidence": _clamp(confidence, 0.0, 1.0),
            "category": category,
            "evidence_count": int(max(0, evidence_count)),
            "last_updated": now_ts,
        }

    def get_active_beliefs(self, limit: int = 5, min_confidence: float = 0.25) -> list[dict[str, Any]]:
        active = [
            b
            for b in self.beliefs.values()
            if float(b.get("confidence", 0.0)) >= float(min_confidence)
        ]
        active.sort(
            key=lambda b: (
                float(b.get("confidence", 0.0)),
                int(b.get("evidence_count", 0)),
            ),
            reverse=True,
        )
        return active[:limit]

    def _belief_confidence(self, contains_text: str) -> float:
        needle = str(contains_text or "").lower()
        best = 0.0
        for belief in self.beliefs.values():
            if needle in str(belief.get("statement", "")).lower():
                best = max(best, float(belief.get("confidence", 0.0)))
        return best

    def extract_beliefs(
        self,
        events: list[dict],
        step_counter: int,
        reflection_depth: float = 0.0,
    ) -> dict[str, Any]:
        if (step_counter - self._last_extract_step) < self.extraction_interval:
            return {
                "updated": False,
                "max_conf_shift": 0.0,
                "belief_count": len(self.beliefs),
            }

        self._last_extract_step = step_counter
        if not events:
            return {
                "updated": False,
                "max_conf_shift": 0.0,
                "belief_count": len(self.beliefs),
            }

        window = list(events)[-self.event_window :]
        total = max(1, len(window))
        counts = defaultdict(int)

        for event in window:
            f = self._extract_fields(event)
            text = f["text"]
            cat = f["category"]
            if cat:
                counts[cat] += 1

            if "criticism" in text or "criticized" in text or "mistake" in text:
                counts["criticism_like"] += 1
            if "failure" in text or "failed" in text:
                counts["failure_like"] += 1
            if "success" in text or "solved" in text:
                counts["success_like"] += 1
            if "ignored" in text or "isolated" in text or "loneliness" in text:
                counts["social_rejection_like"] += 1
            if "threat_detected" in text or "threat" in text or "danger" in text:
                counts["threat_like"] += 1
            if "greeted" in text or "praise" in text or "proud of you" in text:
                counts["support_like"] += 1
            if "novelty" in text or "new and unfamiliar" in text:
                counts["novelty_like"] += 1

        task_successes = counts["success"] + counts["success_like"]
        task_failures = counts["failure"] + counts["failure_like"] + counts["criticism_like"]
        social_rejection = counts["ignored"] + counts["loneliness"] + counts["social_rejection_like"]
        social_support = counts["greeted"] + counts["praise"] + counts["support_like"]
        social_attempts = max(1, social_rejection + social_support)
        threat_load = counts["threat_detected"] + counts["threat_like"] + counts["loud_noise"]
        novelty_exposure = counts["novelty"] + counts["novelty_like"] + counts["face_unknown"]

        candidate_beliefs: list[dict[str, Any]] = []
        now_ts = time.time()

        criticism_ratio = counts["criticism_like"] / total
        if counts["criticism_like"] >= self.min_evidence and criticism_ratio >= 0.12:
            confidence = 0.2 + (criticism_ratio * 1.9) + min(0.2, counts["criticism_like"] / 25.0)
            candidate_beliefs.append(
                self._belief_payload(
                    "Criticism often follows my attempts.",
                    confidence,
                    "social",
                    counts["criticism_like"],
                    now_ts,
                )
            )

        task_total = max(1, task_successes + task_failures)
        failure_ratio = task_failures / task_total
        if task_total >= self.min_evidence + 1 and failure_ratio > 0.55:
            confidence = 0.25 + (failure_ratio - 0.5) * 1.3
            candidate_beliefs.append(
                self._belief_payload(
                    "I often fail before I succeed.",
                    confidence,
                    "self",
                    task_failures,
                    now_ts,
                )
            )
        elif task_total >= self.min_evidence + 1 and (task_successes / task_total) > 0.55:
            confidence = 0.25 + ((task_successes / task_total) - 0.5) * 1.3
            candidate_beliefs.append(
                self._belief_payload(
                    "Persistent effort helps me solve challenges.",
                    confidence,
                    "task",
                    task_successes,
                    now_ts,
                )
            )

        rejection_ratio = social_rejection / social_attempts
        if social_attempts >= self.min_evidence + 1 and rejection_ratio > 0.52:
            confidence = 0.2 + (rejection_ratio * 0.9)
            candidate_beliefs.append(
                self._belief_payload(
                    "Reaching out often leads to rejection.",
                    confidence,
                    "social",
                    social_rejection,
                    now_ts,
                )
            )
        elif social_attempts >= self.min_evidence + 1 and (social_support / social_attempts) > 0.5:
            confidence = 0.2 + ((social_support / social_attempts) * 0.8)
            candidate_beliefs.append(
                self._belief_payload(
                    "Supportive connections are available to me.",
                    confidence,
                    "social",
                    social_support,
                    now_ts,
                )
            )

        threat_ratio = threat_load / total
        if threat_load >= self.min_evidence and threat_ratio >= 0.1:
            confidence = 0.2 + (threat_ratio * 1.6)
            candidate_beliefs.append(
                self._belief_payload(
                    "The environment often feels unsafe.",
                    confidence,
                    "self",
                    threat_load,
                    now_ts,
                )
            )

        if novelty_exposure >= self.min_evidence and task_successes >= max(1, task_failures * 0.7):
            confidence = 0.2 + min(0.55, novelty_exposure / max(12.0, total))
            candidate_beliefs.append(
                self._belief_payload(
                    "New experiences help me adapt.",
                    confidence,
                    "task",
                    novelty_exposure,
                    now_ts,
                )
            )

        smooth = self.confidence_smoothing * (1.0 + min(0.3, max(0.0, reflection_depth) / 25.0))
        smooth = _clamp(smooth, 0.08, 0.8)
        max_shift = 0.0
        active_statements = set()

        for candidate in candidate_beliefs:
            statement = candidate["statement"]
            active_statements.add(statement)
            old = self.beliefs.get(statement)
            old_conf = float(old.get("confidence", 0.0)) if isinstance(old, dict) else 0.0
            new_conf = old_conf + ((candidate["confidence"] - old_conf) * smooth)
            candidate["confidence"] = _clamp(new_conf, 0.0, 1.0)
            max_shift = max(max_shift, abs(candidate["confidence"] - old_conf))
            self.beliefs[statement] = candidate

        for statement in list(self.beliefs.keys()):
            if statement in active_statements:
                continue
            old_conf = float(self.beliefs[statement].get("confidence", 0.0))
            decayed = old_conf * 0.985
            self.beliefs[statement]["confidence"] = decayed
            max_shift = max(max_shift, abs(old_conf - decayed))
            if decayed < 0.08:
                self.beliefs.pop(statement, None)

        self._last_max_shift = max_shift
        return {
            "updated": True,
            "max_conf_shift": round(max_shift, 6),
            "belief_count": len(self.beliefs),
            "active_beliefs": self.get_active_beliefs(limit=5),
        }

    def update_mood(self, step_signals: list[dict[str, Any]]) -> dict[str, Any]:
        prev_valence = float(self.mood_state.get("valence", 0.0))
        prev_arousal = float(self.mood_state.get("arousal", 0.0))

        if not step_signals:
            mood_valence = prev_valence * 0.98
            mood_arousal = prev_arousal * 0.95
        else:
            weighted_valence = 0.0
            total_weight = 0.0
            weighted_arousal = 0.0
            for signal in step_signals:
                valence = float(signal.get("valence", 0.0) or 0.0)
                intensity = _clamp(float(signal.get("intensity", 0.0) or 0.0), 0.0, 1.0)
                weight = max(0.05, intensity)
                weighted_valence += valence * weight
                weighted_arousal += abs(valence) * weight
                total_weight += weight
            step_valence = weighted_valence / max(0.001, total_weight)
            step_arousal = _clamp(weighted_arousal / max(0.001, total_weight), 0.0, 1.0)

            mood_valence = (0.94 * prev_valence) + (0.06 * step_valence)
            mood_arousal = (0.9 * prev_arousal) + (0.1 * step_arousal)

        tone = "neutral"
        if mood_valence <= -0.4:
            tone = "distressed"
        elif mood_valence <= -0.15 and mood_arousal >= 0.4:
            tone = "tense"
        elif mood_valence >= 0.35:
            tone = "confident"
        elif mood_valence >= 0.15:
            tone = "hopeful"
        elif mood_arousal < 0.2:
            tone = "calm"

        self.mood_state = {
            "valence": round(_clamp(mood_valence, -1.0, 1.0), 4),
            "arousal": round(_clamp(mood_arousal, 0.0, 1.0), 4),
            "tone": tone,
            "updated_at": time.time(),
        }
        return dict(self.mood_state)

    def adjust_appraisal(
        self,
        category: str,
        content: str,
        valence: float,
        intensity: float,
        modality: str = "experience",
    ) -> tuple[float, float]:
        valence = _clamp(valence, -1.0, 1.0)
        intensity = _clamp(intensity, 0.0, 1.0)
        mood_valence = float(self.mood_state.get("valence", 0.0))
        mood_arousal = float(self.mood_state.get("arousal", 0.0))

        intensity_scale = 1.0 + (mood_arousal * 0.08)
        valence_shift = 0.0
        category = str(category or "").lower()
        text = f"{category} {content}".lower()

        if valence < 0 and mood_valence < 0:
            intensity_scale += abs(mood_valence) * 0.2
        elif valence > 0 and mood_valence < -0.35:
            intensity_scale *= 0.92

        if self._belief_confidence("Criticism often follows my attempts.") > 0.5:
            conf = self._belief_confidence("Criticism often follows my attempts.")
            if category in {"criticism", "ignored", "loneliness"} or "mistake" in text:
                intensity_scale += 0.16 * conf
                valence_shift -= 0.05 * conf

        unsafe_conf = self._belief_confidence("environment often feels unsafe")
        if unsafe_conf > 0.45 and (
            category in {"threat_detected", "loud_noise"} or "threat" in text
        ):
            intensity_scale += 0.2 * unsafe_conf
            valence_shift -= 0.04 * unsafe_conf

        mastery_conf = self._belief_confidence("Persistent effort helps me solve challenges.")
        if mastery_conf > 0.4 and category in {"success", "novelty", "face_recognized"}:
            intensity_scale += 0.1 * mastery_conf
            if valence >= 0:
                valence_shift += 0.04 * mastery_conf

        if modality == "internal":
            intensity_scale *= 0.88

        adjusted_valence = _clamp(valence + valence_shift, -1.0, 1.0)
        adjusted_intensity = _clamp(intensity * _clamp(intensity_scale, 0.7, 1.35), 0.0, 1.0)
        return adjusted_valence, adjusted_intensity

    def expected_valence(self, category: str) -> float:
        cat = str(category or "").lower()
        if cat in {"criticism", "failure", "threat_detected", "loud_noise"}:
            if self._belief_confidence("Persistent effort helps me solve challenges.") > 0.55:
                return -0.2
            return -0.6
        if cat in {"success", "praise", "greeted", "face_recognized"}:
            if self._belief_confidence("Reaching out often leads to rejection.") > 0.55:
                return 0.1
            return 0.5
        if cat in {"ignored", "loneliness"}:
            return -0.5
        return 0.0

    def record_prediction(self, expected_valence: float, actual_valence: float) -> None:
        expected_sign = 0
        if expected_valence > 0.05:
            expected_sign = 1
        elif expected_valence < -0.05:
            expected_sign = -1

        actual_sign = 0
        if actual_valence > 0.05:
            actual_sign = 1
        elif actual_valence < -0.05:
            actual_sign = -1

        self.prediction_total += 1
        if expected_sign == actual_sign:
            self.prediction_hits += 1

    def record_decision_outcome(self, action: str, success: bool, intensity: float = 0.5) -> None:
        if not action:
            return
        stats = self.action_stats[action]
        stats["attempts"] += 1
        if success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1
        self.recent_action_outcomes.append(
            {
                "action": action,
                "success": bool(success),
                "intensity": _clamp(intensity, 0.0, 1.0),
                "timestamp": time.time(),
            }
        )

    def strategy_action_bias(self) -> dict[str, float]:
        bias: dict[str, float] = {}
        for action, stats in self.action_stats.items():
            attempts = max(1, int(stats.get("attempts", 0)))
            if attempts < 4:
                continue
            successes = int(stats.get("successes", 0))
            failures = int(stats.get("failures", 0))
            success_rate = successes / attempts
            fail_rate = failures / attempts
            bias[action] = (success_rate - 0.5) * 0.18
            if fail_rate > 0.6 and failures >= 3:
                bias[action] -= (fail_rate - 0.6) * 0.5

        novelty_conf = self._belief_confidence("New experiences help me adapt.")
        if novelty_conf > 0.55:
            boost = 0.12 * novelty_conf
            bias["challenge"] = bias.get("challenge", 0.0) + boost
            bias["suggest"] = bias.get("suggest", 0.0) + (boost * 0.8)

        for action in list(bias.keys()):
            bias[action] = _clamp(bias[action], -0.35, 0.35)
        return bias

    def decision_bias(self) -> dict[str, float]:
        bias = self.strategy_action_bias()
        mood_valence = float(self.mood_state.get("valence", 0.0))
        mood_arousal = float(self.mood_state.get("arousal", 0.0))

        if mood_valence < -0.2:
            stress_push = abs(mood_valence) * (0.22 + 0.1 * mood_arousal)
            bias["refuse"] = bias.get("refuse", 0.0) + stress_push
            bias["neutral"] = bias.get("neutral", 0.0) + (stress_push * 0.8)
            bias["support"] = bias.get("support", 0.0) - (stress_push * 0.5)
        elif mood_valence > 0.2:
            lift = mood_valence * 0.2
            bias["support"] = bias.get("support", 0.0) + lift
            bias["suggest"] = bias.get("suggest", 0.0) + (lift * 0.8)

        reject_conf = self._belief_confidence("Reaching out often leads to rejection.")
        support_conf = self._belief_confidence("Supportive connections are available to me.")
        unsafe_conf = self._belief_confidence("environment often feels unsafe")
        mastery_conf = self._belief_confidence("Persistent effort helps me solve challenges.")

        if reject_conf > 0.4:
            bias["support"] = bias.get("support", 0.0) - (0.25 * reject_conf)
            bias["neutral"] = bias.get("neutral", 0.0) + (0.12 * reject_conf)
        if support_conf > 0.4:
            bias["support"] = bias.get("support", 0.0) + (0.25 * support_conf)
            bias["refuse"] = bias.get("refuse", 0.0) - (0.12 * support_conf)
        if unsafe_conf > 0.45:
            bias["neutral"] = bias.get("neutral", 0.0) + (0.18 * unsafe_conf)
            bias["refuse"] = bias.get("refuse", 0.0) + (0.12 * unsafe_conf)
        if mastery_conf > 0.5:
            bias["suggest"] = bias.get("suggest", 0.0) + (0.14 * mastery_conf)
            bias["challenge"] = bias.get("challenge", 0.0) + (0.1 * mastery_conf)

        for action in list(bias.keys()):
            bias[action] = _clamp(bias[action], -0.4, 0.4)
        return bias

    def identity_drift(self, cortisol: float, identity_snapshot: dict[str, float]) -> dict[str, float]:
        drift: dict[str, float] = {}
        mood_valence = float(self.mood_state.get("valence", 0.0))
        reject_conf = self._belief_confidence("Reaching out often leads to rejection.")
        support_conf = self._belief_confidence("Supportive connections are available to me.")
        mastery_conf = self._belief_confidence("Persistent effort helps me solve challenges.")
        unsafe_conf = self._belief_confidence("environment often feels unsafe")

        if reject_conf > 0.4:
            drift["social_value"] = drift.get("social_value", 0.0) - (0.02 * reject_conf)
        if support_conf > 0.4:
            drift["social_value"] = drift.get("social_value", 0.0) + (0.02 * support_conf)
        if mastery_conf > 0.45:
            drift["competence"] = drift.get("competence", 0.0) + (0.015 * mastery_conf)
        if unsafe_conf > 0.5 and cortisol > 58.0:
            drift["competence"] = drift.get("competence", 0.0) - (0.008 * unsafe_conf)

        if mood_valence > 0.2:
            drift["intelligence"] = drift.get("intelligence", 0.0) + (0.005 * mood_valence)
        elif mood_valence < -0.3:
            drift["intelligence"] = drift.get("intelligence", 0.0) - (0.003 * abs(mood_valence))

        competence = float(identity_snapshot.get("competence", 0.5) or 0.5)
        if competence > 0.7 and mastery_conf > 0.5:
            drift["resilience"] = drift.get("resilience", 0.0) + (0.01 * mastery_conf)

        for trait in list(drift.keys()):
            drift[trait] = round(_clamp(drift[trait], -0.08, 0.08), 6)
        return drift

    def _belief_coherence(self) -> float:
        reject_conf = self._belief_confidence("Reaching out often leads to rejection.")
        support_conf = self._belief_confidence("Supportive connections are available to me.")
        failure_conf = self._belief_confidence("I often fail before I succeed.")
        mastery_conf = self._belief_confidence("Persistent effort helps me solve challenges.")
        contradiction_penalty = min(reject_conf, support_conf) * 0.5 + min(failure_conf, mastery_conf) * 0.5
        return _clamp(1.0 - contradiction_penalty, 0.0, 1.0)

    @staticmethod
    def _narrative_tone(narrative: str) -> float:
        text = str(narrative or "").lower()
        positive_words = ("capable", "ready", "endured", "adapt", "support", "improving")
        negative_words = ("struggle", "unsafe", "difficult", "alone", "rejection")
        score = 0.0
        for token in positive_words:
            if token in text:
                score += 0.2
        for token in negative_words:
            if token in text:
                score -= 0.2
        return _clamp(score, -1.0, 1.0)

    @staticmethod
    def _narrative_complexity(narrative: str) -> float:
        words = [w for w in str(narrative or "").lower().split() if w.strip()]
        if not words:
            return 0.0
        unique_ratio = len(set(words)) / len(words)
        length_factor = min(1.0, len(words) / 24.0)
        return _clamp((0.55 * unique_ratio) + (0.45 * length_factor), 0.0, 1.0)

    def get_consciousness_factors(self, reflection_depth: float, narrative: str) -> dict[str, float]:
        coherence = self._belief_coherence()
        prediction_accuracy = (
            float(self.prediction_hits) / float(self.prediction_total)
            if self.prediction_total > 0
            else 0.5
        )
        narrative_tone = self._narrative_tone(narrative)
        mood_valence = float(self.mood_state.get("valence", 0.0))
        internal_consistency = 1.0 - abs(narrative_tone - mood_valence) / 2.0
        internal_consistency = _clamp(internal_consistency, 0.0, 1.0)
        reflection_frequency = _clamp(float(reflection_depth) / 12.0, 0.0, 1.0)
        narrative_complexity = self._narrative_complexity(narrative)
        return {
            "belief_coherence": round(coherence, 4),
            "prediction_accuracy": round(_clamp(prediction_accuracy, 0.0, 1.0), 4),
            "internal_consistency": round(internal_consistency, 4),
            "reflection_frequency": round(reflection_frequency, 4),
            "narrative_complexity": round(narrative_complexity, 4),
        }

    def compose_narrative(
        self,
        identity_snapshot: dict[str, float],
        stage: str,
        existing_narrative: str = "",
    ) -> str:
        beliefs = self.get_active_beliefs(limit=2, min_confidence=0.3)
        mood_tone = str(self.mood_state.get("tone", "neutral"))
        competence = float(identity_snapshot.get("competence", 0.5) or 0.5)
        resilience = float(identity_snapshot.get("resilience", 0.5) or 0.5)

        if stage == "child":
            lead = "I am learning from each experience."
        elif stage == "teen":
            lead = "I am shaping who I am through what I face."
        else:
            if competence > 0.75 and resilience > 0.8:
                lead = "I know what I can carry and what I can change."
            else:
                lead = "I am still building my way through this world."

        belief_part = ""
        if beliefs:
            fragments = []
            for belief in beliefs:
                confidence = float(belief.get("confidence", 0.0))
                qualifier = "strongly" if confidence >= 0.7 else "increasingly"
                statement = str(belief.get("statement", "")).strip().rstrip(".")
                if statement:
                    fragments.append(f"I {qualifier} believe {statement.lower()}.")
            belief_part = " ".join(fragments)

        mood_line = {
            "distressed": "I feel pressure lingering, but I am trying to stay grounded.",
            "tense": "I feel tense and alert as I interpret what happens around me.",
            "hopeful": "I feel cautiously hopeful about what I can improve.",
            "confident": "I feel confident in my ability to adapt.",
            "calm": "I feel calm and able to think clearly.",
            "neutral": "I am balancing what I feel with what I learn.",
        }.get(mood_tone, "I am balancing what I feel with what I learn.")

        narrative = " ".join(part for part in [lead, belief_part, mood_line] if part).strip()
        if not narrative:
            narrative = existing_narrative or "I am learning who I am."
        return narrative

    def should_rewrite_narrative(self, step_counter: int, max_conf_shift: float) -> bool:
        if (step_counter - self._last_narrative_rewrite_step) < self.rewrite_cooldown_steps:
            return False
        mood_shift = abs(float(self.mood_state.get("valence", 0.0)) - self._last_narrative_mood_valence)
        return bool(max_conf_shift >= self.shift_threshold or mood_shift >= 0.35)

    def mark_narrative_rewrite(self, step_counter: int) -> None:
        self._last_narrative_rewrite_step = int(step_counter)
        self._last_narrative_mood_valence = float(self.mood_state.get("valence", 0.0))

    def to_state(self) -> dict[str, Any]:
        return {
            "beliefs": list(self.beliefs.values()),
            "mood_state": dict(self.mood_state),
            "action_stats": {k: dict(v) for k, v in self.action_stats.items()},
            "prediction_hits": int(self.prediction_hits),
            "prediction_total": int(self.prediction_total),
            "last_max_shift": float(self._last_max_shift),
            "last_extract_step": int(self._last_extract_step),
        }

    def load_state(self, payload: dict | None) -> None:
        if not isinstance(payload, dict):
            return

        loaded_beliefs = payload.get("beliefs")
        if isinstance(loaded_beliefs, list):
            self.beliefs = {}
            for belief in loaded_beliefs:
                if not isinstance(belief, dict):
                    continue
                statement = str(belief.get("statement", "")).strip()
                if not statement:
                    continue
                self.beliefs[statement] = {
                    "statement": statement,
                    "confidence": _clamp(belief.get("confidence", 0.0), 0.0, 1.0),
                    "category": str(belief.get("category", "self")),
                    "evidence_count": int(max(0, belief.get("evidence_count", 0))),
                    "last_updated": float(belief.get("last_updated", time.time())),
                }

        mood_state = payload.get("mood_state")
        if isinstance(mood_state, dict):
            self.mood_state = {
                "valence": round(_clamp(mood_state.get("valence", 0.0), -1.0, 1.0), 4),
                "arousal": round(_clamp(mood_state.get("arousal", 0.0), 0.0, 1.0), 4),
                "tone": str(mood_state.get("tone", "neutral")),
                "updated_at": float(mood_state.get("updated_at", time.time())),
            }

        action_stats = payload.get("action_stats")
        if isinstance(action_stats, dict):
            self.action_stats = defaultdict(lambda: {"attempts": 0, "successes": 0, "failures": 0})
            for action, stats in action_stats.items():
                if not isinstance(stats, dict):
                    continue
                self.action_stats[str(action)] = {
                    "attempts": int(max(0, stats.get("attempts", 0))),
                    "successes": int(max(0, stats.get("successes", 0))),
                    "failures": int(max(0, stats.get("failures", 0))),
                }

        self.prediction_hits = int(max(0, payload.get("prediction_hits", self.prediction_hits)))
        self.prediction_total = int(max(0, payload.get("prediction_total", self.prediction_total)))
        self._last_max_shift = float(payload.get("last_max_shift", self._last_max_shift))
        self._last_extract_step = int(payload.get("last_extract_step", self._last_extract_step))

"""Recurring-experience pattern detectors for the enhanced belief engine.

Each detector scans a window of lived events and reports whether a recurring
pattern is present, how strongly, and how much evidence supports it. Detectors
are deterministic and side-effect free so they can be unit-tested in isolation.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

CRITICISM_CATEGORIES = {"criticism", "negative_feedback", "correction", "reprimand"}
FAILURE_CATEGORIES = {"failure", "mistake", "task_failed", "setback"}
SUCCESS_CATEGORIES = {"success", "task_completed", "achievement", "accomplishment"}
REJECTION_CATEGORIES = {"ignored", "loneliness", "rejection", "excluded", "social_pain"}
SUPPORT_CATEGORIES = {"greeted", "praise", "affection", "appreciation", "welcome"}
THREAT_CATEGORIES = {"threat_detected", "loud_noise", "danger", "alarm"}
NOVELTY_CATEGORIES = {"novelty", "face_unknown", "speech_detected", "new_environment", "unknown_sound"}

TASK_CATEGORIES = FAILURE_CATEGORIES | SUCCESS_CATEGORIES | CRITICISM_CATEGORIES


def _category(event: dict) -> str:
    if not isinstance(event, dict):
        return ""
    metadata = event.get("metadata")
    if isinstance(metadata, dict):
        return str(metadata.get("category", "") or "").strip().lower()
    return str(event.get("category", "") or "").strip().lower()


def _is_criticism(event: dict) -> bool:
    return _category(event) in CRITICISM_CATEGORIES


def _is_success(event: dict) -> bool:
    return _category(event) in SUCCESS_CATEGORIES


def _is_failure(event: dict) -> bool:
    return _category(event) in FAILURE_CATEGORIES


def _is_task(event: dict) -> bool:
    return _category(event) in TASK_CATEGORIES


def _is_rejection(event: dict) -> bool:
    return _category(event) in REJECTION_CATEGORIES


def _is_support(event: dict) -> bool:
    return _category(event) in SUPPORT_CATEGORIES


def _is_threat(event: dict) -> bool:
    return _category(event) in THREAT_CATEGORIES


def _is_novelty(event: dict) -> bool:
    return _category(event) in NOVELTY_CATEGORIES


def _temporal_density(indices: list[int]) -> float:
    """Density of clustering among matching event indices (0..1)."""
    if len(indices) < 2:
        return 1.0
    ordered = sorted(indices)
    adjacent = sum(1 for a, b in zip(ordered, ordered[1:]) if b - a == 1)
    return min(1.0, (adjacent + 1) / len(ordered))


def _preceding_categories(events: list[dict], match_indices: set[int]) -> dict[str, float]:
    """Fraction of matching events that had each category within the 3 prior events."""
    preceded: Counter[str] = Counter()
    count = 0
    for idx in sorted(match_indices):
        window = events[max(0, idx - 3): idx]
        if not window:
            continue
        count += 1
        for event in window:
            cat = _category(event)
            if cat:
                preceded[cat] += 1
    if count == 0:
        return {}
    total = sum(preceded.values()) or 1
    return {cat: round(times / total, 4) for cat, times in preceded.items()}


class PatternDetector:
    """Base class for detecting recurring patterns in lived events."""

    min_evidence: int = 1

    def detect_pattern(self, events: list[dict]) -> dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    def calculate_confidence(pattern_strength: float, evidence_count: int) -> float:
        base_confidence = min(0.9, max(0.0, float(pattern_strength)) * 2.0)
        evidence_bonus = min(0.3, max(0, int(evidence_count)) / 50.0)
        return min(1.0, base_confidence + evidence_bonus)

    def _undetected(self, evidence_count: int = 0) -> dict[str, Any]:
        return {"detected": False, "strength": 0.0, "evidence_count": int(evidence_count)}


class CriticismPatternDetector(PatternDetector):
    """Detects clusters of criticism following attempted action."""

    min_evidence = 3

    def detect_pattern(self, events: list[dict]) -> dict[str, Any]:
        events = list(events or [])
        total = len(events)
        criticism_indices = [i for i, e in enumerate(events) if _is_criticism(e)]
        if len(criticism_indices) < self.min_evidence or total == 0:
            return self._undetected(len(criticism_indices))

        temporal_density = _temporal_density(criticism_indices)
        context = _preceding_categories(events, set(criticism_indices))
        attempt_preceded = sum(
            1
            for idx in criticism_indices
            if any(_is_task(e) for e in events[max(0, idx - 3): idx])
        )
        context_bonus = attempt_preceded / max(1, len(criticism_indices))

        pattern_strength = (len(criticism_indices) / total) * temporal_density * (0.6 + 0.4 * context_bonus)
        return {
            "detected": pattern_strength > 0.15,
            "strength": round(pattern_strength, 4),
            "evidence_count": len(criticism_indices),
            "temporal_density": round(temporal_density, 4),
            "context_patterns": context,
            "belief_statement": "Criticism often follows my attempts.",
            "belief_category": "social",
        }


class SuccessFailurePatternDetector(PatternDetector):
    """Detects dominant success/failure trajectories in task events."""

    min_evidence = 5

    def detect_pattern(self, events: list[dict]) -> dict[str, Any]:
        events = list(events or [])
        task_events = [(i, e) for i, e in enumerate(events) if _is_task(e)]
        if len(task_events) < self.min_evidence:
            return self._undetected(len(task_events))

        successes = sum(1 for _, e in task_events if _is_success(e))
        failures = sum(1 for _, e in task_events if _is_failure(e))
        success_rate = successes / len(task_events)
        failure_rate = failures / len(task_events)

        midpoint = len(task_events) // 2
        first_half = task_events[:max(1, midpoint)]
        second_half = task_events[midpoint:]
        first_rate = sum(1 for _, e in first_half if _is_success(e)) / len(first_half)
        second_rate = sum(1 for _, e in second_half if _is_success(e)) / len(second_half)
        learning_trajectory = second_rate - first_rate

        pattern_strength = abs(success_rate - failure_rate)
        if failure_rate > 0.6:
            statement = "I often fail before I succeed."
            category = "self"
        elif success_rate > 0.6 and learning_trajectory > 0.1:
            statement = "Persistent effort helps me solve challenges."
            category = "task"
        else:
            return self._undetected(len(task_events))

        return {
            "detected": pattern_strength > 0.2,
            "strength": round(pattern_strength, 4),
            "evidence_count": len(task_events),
            "success_rate": round(success_rate, 4),
            "failure_rate": round(failure_rate, 4),
            "learning_trajectory": round(learning_trajectory, 4),
            "belief_statement": statement,
            "belief_category": category,
        }


class SocialRejectionPatternDetector(PatternDetector):
    """Detects whether outreach is predominantly met with rejection or support."""

    min_evidence = 3

    def detect_pattern(self, events: list[dict]) -> dict[str, Any]:
        events = list(events or [])
        rejections = [i for i, e in enumerate(events) if _is_rejection(e)]
        supports = [i for i, e in enumerate(events) if _is_support(e)]
        attempts = len(rejections) + len(supports)
        if attempts < self.min_evidence:
            return self._undetected(attempts)

        rejection_ratio = len(rejections) / attempts
        pattern_strength = abs(rejection_ratio - 0.5) * 2.0
        if rejection_ratio > 0.52:
            statement = "Reaching out often leads to rejection."
            category = "social"
        elif (len(supports) / attempts) > 0.5:
            statement = "Supportive connections are available to me."
            category = "social"
        else:
            return self._undetected(attempts)

        return {
            "detected": pattern_strength > 0.2,
            "strength": round(pattern_strength, 4),
            "evidence_count": attempts,
            "rejection_ratio": round(rejection_ratio, 4),
            "belief_statement": statement,
            "belief_category": category,
        }


class ThreatPatternDetector(PatternDetector):
    """Detects recurring environmental threats."""

    min_evidence = 3

    def detect_pattern(self, events: list[dict]) -> dict[str, Any]:
        events = list(events or [])
        total = len(events)
        threat_indices = [i for i, e in enumerate(events) if _is_threat(e)]
        if len(threat_indices) < self.min_evidence or total == 0:
            return self._undetected(len(threat_indices))

        temporal_density = _temporal_density(threat_indices)
        pattern_strength = (len(threat_indices) / total) * temporal_density
        return {
            "detected": pattern_strength > 0.12,
            "strength": round(pattern_strength, 4),
            "evidence_count": len(threat_indices),
            "temporal_density": round(temporal_density, 4),
            "belief_statement": "The environment often feels unsafe.",
            "belief_category": "self",
        }


class NoveltyAdaptationPatternDetector(PatternDetector):
    """Detects whether novel experiences are followed by successful adaptation."""

    min_evidence = 3

    def detect_pattern(self, events: list[dict]) -> dict[str, Any]:
        events = list(events or [])
        novelty_count = sum(1 for e in events if _is_novelty(e))
        task_events = [e for e in events if _is_task(e)]
        if novelty_count < self.min_evidence or len(task_events) < 3:
            return self._undetected(novelty_count)

        successes = sum(1 for e in task_events if _is_success(e))
        failures = sum(1 for e in task_events if _is_failure(e))
        success_rate = successes / max(1, successes + failures)
        if success_rate < 0.55:
            return self._undetected(novelty_count)

        pattern_strength = (novelty_count / max(1, len(events))) * success_rate
        return {
            "detected": pattern_strength > 0.08,
            "strength": round(pattern_strength, 4),
            "evidence_count": novelty_count,
            "success_rate": round(success_rate, 4),
            "belief_statement": "New experiences help me adapt.",
            "belief_category": "task",
        }


def build_default_detectors() -> dict[str, PatternDetector]:
    return {
        "criticism_pattern": CriticismPatternDetector(),
        "success_failure_pattern": SuccessFailurePatternDetector(),
        "social_rejection_pattern": SocialRejectionPatternDetector(),
        "threat_pattern": ThreatPatternDetector(),
        "novelty_adaptation_pattern": NoveltyAdaptationPatternDetector(),
    }

"""Enhanced belief extraction engine with pattern detection.

Opt-in: construct with `config={"engine": "enhanced"}`. Runs the standard
BeliefEngine pipeline and augments it with recurring-pattern detection over
the event window. Fully backward compatible with the base engine's interface.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any

from cognition.belief_engine import BeliefEngine, _clamp
from cognition.pattern_detectors import PatternDetector, build_default_detectors


class EnhancedBeliefEngine(BeliefEngine):
    """BeliefEngine augmented with pattern detection and pattern awareness."""

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        detector_config = (config or {}).get("pattern_detectors", {}) or {}
        detectors = build_default_detectors()
        self.pattern_detectors: dict[str, PatternDetector] = {}
        for name, detector in detectors.items():
            enabled = detector_config.get(name, True)
            if enabled:
                self.pattern_detectors[name] = detector
        self.pattern_log: deque[dict[str, Any]] = deque(maxlen=200)
        self.last_pattern_summary: list[dict[str, Any]] = []

    def extract_beliefs(
        self,
        events: list[dict],
        step_counter: int,
        reflection_depth: float = 0.0,
    ) -> dict[str, Any]:
        result = super().extract_beliefs(events, step_counter, reflection_depth)
        if not result.get("updated"):
            result["patterns"] = list(self.last_pattern_summary)
            return result

        pattern_shift = self._extract_pattern_beliefs(events, reflection_depth)
        result["max_conf_shift"] = round(max(float(result.get("max_conf_shift", 0.0)), pattern_shift), 6)
        result["patterns"] = list(self.last_pattern_summary)
        return result

    def _extract_pattern_beliefs(self, events: list[dict], reflection_depth: float) -> float:
        window = list(events or [])[-self.event_window:]
        max_shift = 0.0
        detections: list[dict[str, Any]] = []
        now_ts = time.time()

        smooth = self.confidence_smoothing * (1.0 + min(0.3, max(0.0, reflection_depth) / 25.0))
        smooth = _clamp(smooth, 0.08, 0.8)

        for name, detector in self.pattern_detectors.items():
            pattern = detector.detect_pattern(window)
            if not pattern.get("detected"):
                continue

            statement = str(pattern.get("belief_statement", "")).strip()
            category = str(pattern.get("belief_category", "self"))
            evidence_count = int(pattern.get("evidence_count", 0))
            strength = float(pattern.get("strength", 0.0))
            confidence = detector.calculate_confidence(strength, evidence_count)

            old = self.beliefs.get(statement)
            old_conf = float(old.get("confidence", 0.0)) if isinstance(old, dict) else 0.0
            new_conf = _clamp(old_conf + ((confidence - old_conf) * smooth), 0.0, 1.0)
            self.beliefs[statement] = self._belief_payload(
                statement,
                new_conf,
                category,
                evidence_count,
                now_ts,
            )
            max_shift = max(max_shift, abs(new_conf - old_conf))

            detail = {k: v for k, v in pattern.items() if k not in {"detected", "belief_statement", "belief_category"}}
            detections.append(
                {
                    "detector": name,
                    "statement": statement,
                    "confidence": round(new_conf, 4),
                    "strength": round(strength, 4),
                    "evidence_count": evidence_count,
                    "detected_at": now_ts,
                    **detail,
                }
            )

        if detections:
            self.pattern_log.append(detections)
        self.last_pattern_summary = detections
        return max_shift

    def get_pattern_report(self, limit: int = 5) -> list[list[dict[str, Any]]]:
        return [list(detection) for detection in list(self.pattern_log)[-limit:]]

    def to_state(self) -> dict[str, Any]:
        state = super().to_state()
        state["patterns"] = [list(detection) for detection in self.pattern_log]
        return state

    def load_state(self, payload: dict | None) -> None:
        super().load_state(payload)
        if not isinstance(payload, dict):
            return
        patterns = payload.get("patterns")
        if isinstance(patterns, list):
            self.pattern_log.clear()
            for detection in patterns:
                if isinstance(detection, list):
                    self.pattern_log.append(detection)

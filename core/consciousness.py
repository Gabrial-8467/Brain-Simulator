from __future__ import annotations

from typing import Any

from core.attention import GlobalWorkspace


class Consciousness:
    def __init__(self) -> None:
        self.score = 0.0

    def compute_score(self, brain: Any) -> float:
        stability = GlobalWorkspace.focus_stability()
        streak_bonus = min(0.5, (GlobalWorkspace._streak // 5) * 0.1)
        development_bonus = min(
            0.3,
            getattr(getattr(brain, "development", None), "experience_points", 0) / 500.0,
        )
        reflection_bonus = min(
            0.2,
            getattr(getattr(brain, "development", None), "reflection_depth", 0.0) / 100.0,
        )

        source_bonus = 0.0
        focus = GlobalWorkspace.current_focus()
        if focus and focus.source in ("memory", "goal"):
            source_bonus = 0.1

        raw = stability + streak_bonus + source_bonus + development_bonus + reflection_bonus
        self.score = max(0.0, min(1.0, raw))
        return self.score

    def modulate_risk(self, brain: Any, score: float) -> None:
        if not hasattr(brain, "risk_tolerance"):
            return

        adapt_rate = getattr(brain, "risk_adapt_rate", 0.02)
        if score < 0.4:
            brain.risk_tolerance += adapt_rate
        elif score > 0.6:
            brain.risk_tolerance -= adapt_rate
        else:
            brain.risk_tolerance += (0.5 - brain.risk_tolerance) * 0.1

        brain.risk_tolerance = max(0.1, min(0.9, brain.risk_tolerance))

    def update_narrative(self, brain: Any, score: float) -> None:
        return

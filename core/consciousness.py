from __future__ import annotations

from typing import Any

from core.attention import GlobalWorkspace


class Consciousness:
    def __init__(self) -> None:
        self.score = 0.0

    def compute_score(self, brain: Any) -> float:
        stability = GlobalWorkspace.focus_stability()
        streak_bonus = min(0.5, (GlobalWorkspace._streak // 5) * 0.1)
        experience_points = getattr(getattr(brain, "development", None), "experience_points", 0)
        development_bonus = min(0.35, experience_points / 1000.0)
        reflection_bonus = min(
            0.2,
            getattr(getattr(brain, "development", None), "reflection_depth", 0.0) / 100.0,
        )

        recent = list(getattr(brain, "recent_perceptions", []))[-20:]
        vision_bonus = 0.02 if any(p.get("modality") == "vision" for p in recent) else 0.0
        hearing_bonus = 0.02 if any(p.get("modality") == "hearing" for p in recent) else 0.0
        novelty_weighted = 0.0
        if recent:
            for idx, p in enumerate(recent):
                recency_weight = (idx + 1) / len(recent)
                novelty = float((p.get("scene") or {}).get("novelty", 0.0))
                if p.get("modality") in ("vision", "hearing"):
                    novelty *= 1.2
                novelty_weighted += novelty * recency_weight
        novelty_bonus = min(0.2, novelty_weighted * 0.05)

        source_bonus = 0.0
        focus = GlobalWorkspace.current_focus()
        if focus and focus.source in ("memory", "goal"):
            source_bonus = 0.1

        raw = (
            stability
            + streak_bonus
            + source_bonus
            + development_bonus
            + reflection_bonus
            + vision_bonus
            + hearing_bonus
            + novelty_bonus
        )
        target = max(0.0, min(1.0, raw))
        # Smooth step-to-step noise while still integrating new evidence.
        self.score = (0.95 * self.score) + (0.05 * target)
        self.score = max(0.0, min(1.0, self.score))
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

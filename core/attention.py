from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Literal

SourceType = Literal[
    "memory",
    "emotion",
    "goal",
    "perception",
    "internal",
]


@dataclass
class Thought:
    content: str
    source: SourceType
    emotional_weight: float = 0.0
    novelty: float = 0.0
    relevance_to_goals: float = 0.0
    recency: float = field(default_factory=lambda: time.time())
    metadata: Dict[str, Any] = field(default_factory=dict)


class GlobalWorkspace:
    _candidates: list[Thought] = []
    _last_winner: Thought | None = None
    _streak: int = 0

    WEIGHTS = {
        "emotional": 0.35,
        "novelty": 0.20,
        "relevance": 0.25,
        "recency": 0.20,
    }

    @classmethod
    def post(cls, thought: Thought) -> None:
        cls._candidates.append(thought)

    @classmethod
    def _recency_factor(cls, thought: Thought, now: float) -> float:
        age = now - thought.recency
        return max(0.0, 1.0 - (age / 30.0))

    @classmethod
    def select(cls) -> Thought | None:
        if not cls._candidates:
            winner = cls._last_winner
        else:
            now = time.time()
            activations: list[tuple[float, Thought]] = []
            for th in cls._candidates:
                recency_factor = cls._recency_factor(th, now)
                activation = (
                    cls.WEIGHTS["emotional"] * th.emotional_weight
                    + cls.WEIGHTS["novelty"] * th.novelty
                    + cls.WEIGHTS["relevance"] * th.relevance_to_goals
                    + cls.WEIGHTS["recency"] * recency_factor
                )
                activations.append((activation, th))
            winner = max(activations, key=lambda a: a[0])[1]

        if winner is cls._last_winner and winner is not None:
            cls._streak += 1
        elif winner is None:
            cls._streak = 0
        else:
            cls._streak = 1

        cls._last_winner = winner
        cls._candidates = []
        return winner

    @classmethod
    def current_focus(cls) -> Thought | None:
        return cls._last_winner

    @classmethod
    def focus_stability(cls) -> float:
        return min(1.0, cls._streak / 20.0)

    @classmethod
    def reset(cls) -> None:
        cls._candidates = []
        cls._last_winner = None
        cls._streak = 0

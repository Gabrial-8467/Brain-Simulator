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
    topic: str = ""


class WorkspaceMethod:
    def __init__(self, name: str):
        self.name = name

    def __get__(self, instance: Any, owner: Any) -> Any:
        if instance is not None:
            return getattr(instance, "_" + self.name)
        else:
            def proxy(*args: Any, **kwargs: Any) -> Any:
                default = owner.get_default()
                return getattr(default, "_" + self.name)(*args, **kwargs)
            return proxy


class WorkspaceProperty:
    def __init__(self, name: str):
        self.name = name

    def __get__(self, instance: Any, owner: Any) -> Any:
        inst_attr = "_" + self.name + "_inst"
        if instance is not None:
            if not hasattr(instance, inst_attr):
                setattr(instance, inst_attr, [] if self.name == "candidates" else (None if self.name == "last_winner" else 0))
            return getattr(instance, inst_attr)
        else:
            default = owner.get_default()
            if not hasattr(default, inst_attr):
                setattr(default, inst_attr, [] if self.name == "candidates" else (None if self.name == "last_winner" else 0))
            return getattr(default, inst_attr)

    def __set__(self, instance: Any, value: Any) -> None:
        inst_attr = "_" + self.name + "_inst"
        if instance is not None:
            setattr(instance, inst_attr, value)
        else:
            setattr(GlobalWorkspace.get_default(), inst_attr, value)


class GlobalWorkspace:
    _default_instance: GlobalWorkspace | None = None

    @classmethod
    def get_default(cls) -> GlobalWorkspace:
        if cls._default_instance is None:
            cls._default_instance = cls()
        return cls._default_instance

    def __init__(self) -> None:
        self._candidates: list[Thought] = []
        self._last_winner: Thought | None = None
        self._streak: int = 0

    WEIGHTS = {
        "emotional": 0.35,
        "novelty": 0.20,
        "relevance": 0.25,
        "recency": 0.20,
    }

    def _post(self, thought: Thought) -> None:
        self._candidates.append(thought)

    def _recency_factor(self, thought: Thought, now: float) -> float:
        age = now - thought.recency
        return max(0.0, 1.0 - (age / 30.0))

    def _select(self, norepinephrine: float = 50.0, network_mode: str = "TPN", curiosity_engine: Any = None, active_goal: str | None = None, love_score: float = 0.0, loved_source: str | None = None) -> Thought | None:
        if not self._candidates:
            winner = self._last_winner
        else:
            now = time.time()
            activations: list[tuple[float, Thought]] = []
            for th in self._candidates:
                recency_factor = self._recency_factor(th, now)
                
                # Apply boost to memory and internal thoughts under Default Mode Network (DMN)
                dmn_boost = 1.3 if network_mode == "DMN" and th.source in {"memory", "internal"} else 1.0
                
                # Dynamic Curiosity modulation on novelty weight
                c_topic = th.topic or th.metadata.get("category") or th.source
                if curiosity_engine and hasattr(curiosity_engine, "get_curiosity_bonus"):
                    c_bonus = curiosity_engine.get_curiosity_bonus(c_topic)
                    th_novelty = 0.5 * th.novelty + 0.5 * c_bonus
                else:
                    th_novelty = th.novelty

                # Dynamic Goal modulation on relevance weight
                th_relevance = th.relevance_to_goals
                if active_goal:
                    goal_keywords = {
                        "safety": ["threat", "unsafe", "danger", "protect", "hide", "refuse", "neutral"],
                        "task_mastery": ["task", "solve", "attempt", "success", "challenge", "suggest", "wisdom"],
                        "social_bond": ["caregiver", "user", "social", "attachment", "support", "friend", "bond", "talk"],
                    }
                    keywords = goal_keywords.get(active_goal, [])
                    content_lower = th.content.lower()
                    if any(kw in content_lower for kw in keywords) or th.source == "goal" or th.topic == active_goal:
                        th_relevance = max(th_relevance, 0.9)

                # Love infatuation boost
                if love_score > 0.0 and loved_source:
                    if th.source == loved_source or loved_source.lower() in th.content.lower():
                        th_relevance = min(1.0, th_relevance + 0.4 * love_score)

                activation = (
                    self.WEIGHTS["emotional"] * th.emotional_weight
                    + self.WEIGHTS["novelty"] * th_novelty
                    + self.WEIGHTS["relevance"] * th_relevance
                    + self.WEIGHTS["recency"] * recency_factor
                ) * dmn_boost
                activations.append((activation, th))
            winner = max(activations, key=lambda a: a[0])[1]

        if winner is self._last_winner and winner is not None:
            import random
            # High norepinephrine causes distractibility (reset/decay streak)
            distraction_chance = max(0.0, (norepinephrine - 70.0) / 60.0)
            if random.random() < distraction_chance:
                self._streak = max(0, self._streak - 2)
            else:
                self._streak += 1
        elif winner is None:
            self._streak = 0
        else:
            self._streak = 1

        self._last_winner = winner
        self._candidates = []
        return winner

    def _current_focus(self) -> Thought | None:
        return self._last_winner

    def _focus_stability(self, norepinephrine: float = 50.0) -> float:
        base_stability = min(1.0, self._streak / 20.0)
        if norepinephrine > 75.0:
            # Hyper-arousal penalty
            penalty = ((norepinephrine - 75.0) / 25.0) * 0.4
            return max(0.0, base_stability - penalty)
        return base_stability

    def _reset(self) -> None:
        self._candidates = []
        self._last_winner = None
        self._streak = 0

    # Descriptors mapping public names to instance/singleton targets
    post = WorkspaceMethod("post")
    select = WorkspaceMethod("select")
    current_focus = WorkspaceMethod("current_focus")
    focus_stability = WorkspaceMethod("focus_stability")
    reset = WorkspaceMethod("reset")

    _candidates = WorkspaceProperty("candidates")
    _last_winner = WorkspaceProperty("last_winner")
    _streak = WorkspaceProperty("streak")

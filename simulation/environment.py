from __future__ import annotations

from dataclasses import dataclass
import random
import time


@dataclass
class VisionSignal:
    """Structured visual observation that an external vision system can emit."""

    objects: list[str]
    attributes: dict[str, list[str]]
    relations: list[dict[str, str]]
    motion_level: float
    confidence: float
    source: str
    timestamp: float


@dataclass
class HearingSignal:
    """Structured auditory observation for external audio systems."""

    transcript: str
    speaker_type: str
    sentiment: float
    prosody_intensity: float
    keywords: list[str]
    source: str
    timestamp: float


@dataclass
class PerceptionEvent:
    content: str
    category: str
    valence: float
    intensity: float
    source: str
    timestamp: float


class SyntheticEnvironment:
    """Generate one meaningful developmental life event per cycle."""

    EVENT_LIBRARY = [
        ("greeted", "A caregiver greets you warmly.", 0.6),
        ("ignored", "Your attempt to connect is ignored.", -0.5),
        ("praise", "You are praised for trying.", 0.8),
        ("criticism", "You are criticized for a mistake.", -0.8),
        ("success", "You solved a small challenge successfully.", 0.9),
        ("failure", "You failed to solve a challenge.", -0.9),
        ("novelty", "You encounter something new and unfamiliar.", 0.3),
        ("boredom", "Nothing changes and stimulation is low.", -0.2),
        ("loneliness", "You feel socially isolated.", -0.7),
    ]

    def __init__(self, deterministic: bool = False):
        self._rng = random.Random(42) if deterministic else random.Random()
        self._vision_object_pool = [
            "person", "cat", "dog", "table", "chair", "book", "bottle", "window", "door"
        ]
        self._vision_attr_pool = ["red", "blue", "green", "small", "large", "bright", "dark"]
        self._vision_rel_pool = ["near", "behind", "left", "right", "on"]
        self._hearing_samples = [
            ("I am proud of you", "caregiver", 0.8, ["praise", "support"]),
            ("Why did you do that?", "caregiver", -0.4, ["question"]),
            ("Good job, keep trying", "teacher", 0.7, ["praise", "effort"]),
            ("No one is listening", "peer", -0.6, ["ignored", "lonely"]),
            ("Let us solve it together", "caregiver", 0.6, ["collaboration"]),
            ("That was a mistake", "teacher", -0.7, ["criticism"]),
            ("Hello, I am here with you", "caregiver", 0.7, ["greeted", "social"]),
        ]

    def generate_event(self) -> PerceptionEvent:
        category, description, valence = self._rng.choice(self.EVENT_LIBRARY)
        intensity = self._rng.uniform(0.35, 0.95)
        return PerceptionEvent(
            content=description,
            category=category,
            valence=max(-1.0, min(1.0, valence)),
            intensity=max(0.0, min(1.0, intensity)),
            source="simulated",
            timestamp=time.time(),
        )

    def generate_vision_signal(self) -> VisionSignal:
        """Create one synthetic visual signal for development/testing."""
        object_count = self._rng.randint(1, 3)
        objects = self._rng.sample(self._vision_object_pool, k=object_count)

        attributes: dict[str, list[str]] = {}
        for obj in objects:
            attr_count = self._rng.randint(0, 2)
            if attr_count:
                attributes[obj] = self._rng.sample(self._vision_attr_pool, k=attr_count)

        relations: list[dict[str, str]] = []
        if len(objects) >= 2 and self._rng.random() < 0.7:
            relations.append(
                {
                    "from": objects[0],
                    "rel": self._rng.choice(self._vision_rel_pool),
                    "to": objects[1],
                }
            )

        return VisionSignal(
            objects=objects,
            attributes=attributes,
            relations=relations,
            motion_level=self._rng.uniform(0.0, 1.0),
            confidence=self._rng.uniform(0.55, 0.95),
            source="simulated_vision",
            timestamp=time.time(),
        )

    def generate_hearing_signal(self) -> HearingSignal:
        """Create one synthetic structured hearing signal for development/testing."""
        transcript, speaker_type, sentiment, keywords = self._rng.choice(self._hearing_samples)
        return HearingSignal(
            transcript=transcript,
            speaker_type=speaker_type,
            sentiment=max(-1.0, min(1.0, sentiment)),
            prosody_intensity=self._rng.uniform(0.3, 0.95),
            keywords=list(keywords),
            source="simulated_audio",
            timestamp=time.time(),
        )

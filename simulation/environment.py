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
    modality: str
    content: str
    category: str
    valence: float
    intensity: float
    source: str
    timestamp: float
    scene: dict | None = None


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
    LANDMARK_EVENTS = {"praise", "criticism", "success", "failure", "threat_detected"}

    def __init__(self, deterministic: bool = False):
        self._rng = random.Random(42) if deterministic else random.Random()
        self._vision_object_pool = [
            "person", "face", "cat", "dog", "table", "chair", "book", "bottle", "window", "door"
        ]
        self._vision_attr_pool = ["red", "blue", "green", "small", "large", "bright", "dark"]
        self._vision_rel_pool = ["near", "behind", "left", "right", "on"]
        self._hearing_samples = [
            ("I am proud of you", "caregiver", 0.8, ["praise", "support"]),
            ("Why did you do that?", "caregiver", -0.4, ["question", "accountability"]),
            ("Good job, keep trying", "teacher", 0.7, ["praise", "effort"]),
            ("No one is listening", "peer", -0.6, ["ignored", "lonely"]),
            ("Let us solve it together", "caregiver", 0.6, ["collaboration"]),
            ("That was a mistake", "teacher", -0.7, ["criticism"]),
            ("Hello, I am here with you", "caregiver", 0.7, ["greeted", "social"]),
            ("", "ambient", -0.2, ["silence"]),
            ("Loud bang from the corridor", "ambient", -0.4, ["loud_noise"]),
        ]

    @staticmethod
    def _voice_valence_from_keywords(keywords: set[str]) -> float:
        """Infer social valence for recognized voice content from semantic keywords."""
        if "accountability" in keywords or "confrontation" in keywords:
            return -0.2
        if "criticism" in keywords:
            return -0.5
        if "lonely" in keywords or "ignored" in keywords:
            return -0.4
        if "question" in keywords:
            return 0.0
        if {"praise", "support", "effort"} & keywords:
            return 0.5
        if "collaboration" in keywords:
            return 0.3
        if {"social", "greeted"} & keywords:
            return 0.4
        return 0.1

    def generate_event(self) -> PerceptionEvent:
        category, description, valence = self._rng.choice(self.EVENT_LIBRARY)
        intensity = self._rng.uniform(0.2, 0.65)
        if category in self.LANDMARK_EVENTS and self._rng.random() < 0.30:
            intensity = self._rng.uniform(0.8, 0.92)
        return PerceptionEvent(
            modality="experience",
            content=description,
            category=category,
            valence=max(-1.0, min(1.0, valence)),
            intensity=max(0.0, min(1.0, intensity)),
            source="simulated",
            timestamp=time.time(),
            scene={"novelty": 0.8, "salience": abs(valence)},
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

    def generate_vision_event(self) -> PerceptionEvent:
        signal = self.generate_vision_signal()
        objects = [o.lower() for o in signal.objects]
        relations = []
        for rel in signal.relations:
            left = str(rel.get("from", "")).lower()
            edge = str(rel.get("rel", "")).lower()
            right = str(rel.get("to", "")).lower()
            if left and edge and right:
                if edge == "threat" and left == right:
                    continue
                relations.append({"from": left, "rel": edge, "to": right})

        category = "environment_scan"
        valence = 0.1
        intensity = self._rng.uniform(0.2, 0.4)
        threat_cue = signal.motion_level > 0.9 or self._rng.random() < 0.15
        if threat_cue:
            category = "threat_detected"
            valence = -0.8
            intensity = self._rng.uniform(0.8, 0.92)
        elif "face" in objects and signal.confidence >= 0.75:
            category = "face_recognized"
            valence = 0.5
            intensity = self._rng.uniform(0.35, 0.65)
        elif "face" in objects:
            category = "face_unknown"
            valence = 0.2
            intensity = self._rng.uniform(0.45, 0.75)

        if category == "threat_detected":
            unique_objects = []
            for obj in objects:
                if obj not in unique_objects:
                    unique_objects.append(obj)
            relations = [r for r in relations if r.get("rel") != "threat"]
            if len(unique_objects) >= 2:
                relations.append(
                    {
                        "from": unique_objects[0],
                        "rel": "threat",
                        "to": unique_objects[1],
                    }
                )
        else:
            relations = [r for r in relations if r.get("rel") != "threat"]

        content = (
            f"objects={','.join(objects)}; motion={signal.motion_level:.2f}; "
            f"confidence={signal.confidence:.2f}"
        )
        return PerceptionEvent(
            modality="vision",
            content=content,
            category=category,
            valence=valence,
            intensity=intensity,
            source=signal.source,
            timestamp=signal.timestamp,
            scene={
                "objects": objects,
                "attributes": signal.attributes,
                "relations": relations,
                "confidence": signal.confidence,
                "novelty": 0.8 if category in {"face_unknown", "threat_detected"} else 0.4,
                "salience": abs(valence),
            },
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

    def generate_hearing_event(self) -> PerceptionEvent:
        signal = self.generate_hearing_signal()
        text = signal.transcript.strip().lower()
        keywords = {k.lower() for k in signal.keywords}

        category = "speech_detected"
        valence = 0.2
        intensity = self._rng.uniform(0.3, 0.55)
        if not text or "silence" in keywords:
            category = "boredom"
            valence = -0.2
            intensity = self._rng.uniform(0.2, 0.35)
        elif "loud_noise" in keywords or "bang" in text or "alarm" in text:
            category = "loud_noise"
            valence = -0.4
            intensity = self._rng.uniform(0.75, 0.9)
        elif signal.speaker_type in {"caregiver", "teacher", "peer"}:
            category = "voice_recognized"
            valence = self._voice_valence_from_keywords(keywords)
            intensity = self._rng.uniform(0.35, 0.65)

        salience = 0.4 if {"accountability", "confrontation"} & keywords else abs(valence)

        return PerceptionEvent(
            modality="hearing",
            content=signal.transcript if signal.transcript else "silence",
            category=category,
            valence=valence,
            intensity=intensity,
            source=signal.source,
            timestamp=signal.timestamp,
            scene={
                "speaker_type": signal.speaker_type,
                "keywords": list(keywords),
                "prosody_intensity": signal.prosody_intensity,
                "novelty": 0.8 if category in {"loud_noise", "speech_detected"} else 0.35,
                "salience": salience,
            },
        )

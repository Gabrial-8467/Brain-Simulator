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
        ("greeted", "A caregiver is greeting me warmly.", 0.6),
        ("ignored", "My attempt to connect is being ignored.", -0.5),
        ("praise", "I am being praised for trying.", 0.8),
        ("criticism", "I am being criticized for a mistake.", -0.8),
        ("success", "I solved a small challenge successfully.", 0.9),
        ("failure", "I failed to solve a challenge.", -0.9),
        ("novelty", "I encountered something new and unfamiliar.", 0.3),
        ("boredom", "I feel bored. Nothing is stimulating me.", -0.2),
        ("loneliness", "I feel socially isolated.", -0.7),
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
            {
                "transcript": "I am proud of you",
                "speaker_type": "caregiver",
                "sentiment": 0.8,
                "keywords": ["praise", "support"],
                "weight": 0.13,
            },
            {
                "transcript": "Why did you do that?",
                "speaker_type": "caregiver",
                "sentiment": -0.4,
                "keywords": ["question", "accountability"],
                "weight": 0.12,
            },
            {
                "transcript": "Good job, keep trying",
                "speaker_type": "teacher",
                "sentiment": 0.7,
                "keywords": ["praise", "effort"],
                "weight": 0.13,
            },
            {
                "transcript": "No one is listening",
                "speaker_type": "peer",
                "sentiment": -0.6,
                "keywords": ["ignored", "lonely"],
                "weight": 0.12,
            },
            {
                "transcript": "Let us solve it together",
                "speaker_type": "caregiver",
                "sentiment": 0.6,
                "keywords": ["collaboration"],
                "weight": 0.12,
            },
            {
                "transcript": "That was a mistake",
                "speaker_type": "teacher",
                "sentiment": -0.7,
                "keywords": ["criticism"],
                "weight": 0.12,
            },
            {
                "transcript": "Hello, I am here with you",
                "speaker_type": "caregiver",
                "sentiment": 0.7,
                "keywords": ["greeted", "social"],
                "weight": 0.11,
            },
            {
                "transcript": "",
                "speaker_type": "ambient",
                "sentiment": -0.2,
                "keywords": ["silence"],
                "weight": 0.12,
            },
            {
                "transcript": "Loud bang from the corridor",
                "speaker_type": "ambient",
                "sentiment": -0.4,
                "keywords": ["loud_noise"],
                "weight": 0.08,
            },
        ]
        self.category_default_novelty = {
            "greeted": 0.8,
            "ignored": 0.8,
            "praise": 0.8,
            "criticism": 0.8,
            "success": 0.8,
            "failure": 0.8,
            "novelty": 0.8,
            "boredom": 0.8,
            "loneliness": 0.8,
            "voice_recognized": 0.35,
            "speech_detected": 0.35,
            "loud_noise": 0.8,
            "environment_scan": 0.4,
            "threat_detected": 0.8,
            "face_recognized": 0.4,
            "face_unknown": 0.8,
        }
        self.event_exposure_counts: dict[str, int] = {}
        self._step_counter = -1
        self._last_loud_noise_step = -999

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

    def _compute_novelty(self, category: str, content: str, base_novelty: float | None = None) -> float:
        base = (
            float(base_novelty)
            if base_novelty is not None
            else float(self.category_default_novelty.get(category, 0.4))
        )
        event_key = f"{category}|{(content or '').strip().lower()}"
        exposure = self.event_exposure_counts.get(event_key, 0)
        novelty = base * (0.5 ** (exposure / 10.0))
        novelty = max(0.05, novelty)
        self.event_exposure_counts[event_key] = exposure + 1
        return novelty

    def generate_event(self) -> PerceptionEvent:
        self._step_counter += 1
        category, description, valence = self._rng.choice(self.EVENT_LIBRARY)
        intensity = self._rng.uniform(0.2, 0.65)
        if category in self.LANDMARK_EVENTS and self._rng.random() < 0.30:
            intensity = self._rng.uniform(0.8, 0.92)
        novelty = self._compute_novelty(category=category, content=description, base_novelty=0.8)
        return PerceptionEvent(
            modality="experience",
            content=description,
            category=category,
            valence=max(-1.0, min(1.0, valence)),
            intensity=max(0.0, min(1.0, intensity)),
            source="simulated",
            timestamp=time.time(),
            scene={"novelty": novelty, "salience": abs(valence)},
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
        novelty = self._compute_novelty(
            category=category,
            content=content,
            base_novelty=self.category_default_novelty.get(category, 0.4),
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
                "novelty": novelty,
                "salience": abs(valence),
            },
        )

    def generate_hearing_signal(self) -> HearingSignal:
        """Create one synthetic structured hearing signal for development/testing."""
        candidates = list(self._hearing_samples)
        if self._step_counter - self._last_loud_noise_step < 5:
            candidates = [
                sample
                for sample in candidates
                if "loud_noise" not in {k.lower() for k in sample.get("keywords", [])}
            ]
        weights = [float(sample.get("weight", 0.1)) for sample in candidates]
        sample = self._rng.choices(candidates, weights=weights, k=1)[0]
        transcript = sample["transcript"]
        speaker_type = sample["speaker_type"]
        sentiment = sample["sentiment"]
        keywords = list(sample["keywords"])
        if "loud_noise" in {k.lower() for k in keywords}:
            self._last_loud_noise_step = self._step_counter
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
        content = signal.transcript if signal.transcript else "silence"
        novelty = self._compute_novelty(
            category=category,
            content=content,
            base_novelty=self.category_default_novelty.get(category, 0.35),
        )

        return PerceptionEvent(
            modality="hearing",
            content=content,
            category=category,
            valence=valence,
            intensity=intensity,
            source=signal.source,
            timestamp=signal.timestamp,
            scene={
                "speaker_type": signal.speaker_type,
                "keywords": list(keywords),
                "prosody_intensity": signal.prosody_intensity,
                "novelty": novelty,
                "salience": salience,
            },
        )

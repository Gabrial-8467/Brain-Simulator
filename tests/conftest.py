import os
import random
import sys

import pytest
import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.brain import VirtualBrain
from decision.decision_engine import DecisionEngine

TIME_BASED_KEYS = {"timestamp", "created_at", "updated_at", "last_updated", "recency", "detected_at"}


def _load_chemicals():
    with open(os.path.join(PROJECT_ROOT, "config", "chemicals.yaml")) as f:
        return yaml.safe_load(f)


def _load_decision():
    with open(os.path.join(PROJECT_ROOT, "config", "decision.yaml")) as f:
        payload = yaml.safe_load(f) or {}
    return payload.get("decision", payload)


def _load_brain_config():
    path = os.path.join(PROJECT_ROOT, "config", "brain.yaml")
    with open(path) as f:
        return yaml.safe_load(f) or {}


def build_brain(tmp_path, name="mem", brain_config=None, deterministic=True, seed=None):
    """Construct a fresh brain isolated from any real persisted data."""
    storage_path = str(tmp_path / f"{name}.json")
    if seed is not None:
        random.seed(seed)
    chemical_cfg = _load_chemicals()
    engine = DecisionEngine(decision_config=_load_decision(), deterministic=deterministic)
    return VirtualBrain(
        chemical_configs=chemical_cfg["chemicals"],
        interaction_matrix=chemical_cfg.get("interactions"),
        decision_engine=engine,
        deterministic=deterministic,
        memory_storage_path=storage_path,
        brain_config=brain_config,
    )


def strip_time_fields(payload):
    """Recursively remove wall-clock fields that legitimately differ across runs."""
    if isinstance(payload, dict):
        return {
            key: strip_time_fields(value)
            for key, value in payload.items()
            if key not in TIME_BASED_KEYS
        }
    if isinstance(payload, list):
        return [strip_time_fields(item) for item in payload]
    return payload


@pytest.fixture
def brain(tmp_path):
    return build_brain(tmp_path, seed=42)


@pytest.fixture
def brain_config():
    return _load_brain_config()


# A fixed, reproducible stream of lived events used across tests.
EVENT_STREAM = [
    {"modality": "hearing", "category": "greeted", "content": "Hello, welcome", "valence": 0.6, "intensity": 0.5, "source": "simulated"},
    {"modality": "hearing", "category": "praise", "content": "Good job trying", "valence": 0.8, "intensity": 0.6, "source": "simulated"},
    {"modality": "hearing", "category": "criticism", "content": "That was wrong", "valence": -0.7, "intensity": 0.7, "source": "simulated"},
    {"modality": "hearing", "category": "failure", "content": "You failed the task", "valence": -0.6, "intensity": 0.6, "source": "simulated"},
    {"modality": "hearing", "category": "success", "content": "Task completed", "valence": 0.8, "intensity": 0.6, "source": "simulated"},
    {"modality": "vision", "category": "threat_detected", "content": "Loud noise detected", "valence": -0.8, "intensity": 0.8, "source": "simulated"},
    {"modality": "hearing", "category": "loneliness", "content": "Nobody responded", "valence": -0.5, "intensity": 0.5, "source": "simulated"},
    {"modality": "hearing", "category": "greeted", "content": "Hello again friend", "valence": 0.7, "intensity": 0.5, "source": "simulated"},
    {"modality": "vision", "category": "environment_scan", "content": "Objects scanned", "valence": 0.2, "intensity": 0.3, "source": "simulated"},
    {"modality": "hearing", "category": "praise", "content": "Well done today", "valence": 0.9, "intensity": 0.6, "source": "simulated"},
    {"modality": "hearing", "category": "criticism", "content": "You should not have", "valence": -0.6, "intensity": 0.6, "source": "simulated"},
    {"modality": "hearing", "category": "praise", "content": "Great recovery", "valence": 0.8, "intensity": 0.5, "source": "simulated"},
    {"modality": "hearing", "category": "ignored", "content": "Silence again", "valence": -0.4, "intensity": 0.4, "source": "simulated"},
    {"modality": "hearing", "category": "success", "content": "Another win", "valence": 0.7, "intensity": 0.6, "source": "simulated"},
    {"modality": "hearing", "category": "novelty", "content": "Something new", "valence": 0.4, "intensity": 0.5, "source": "simulated"},
]


def run_stream(brain, n, stream=None):
    """Feed n events from the stream, ticking after each perception."""
    stream = stream or EVENT_STREAM
    for i in range(n):
        brain.perceive(stream[i % len(stream)])
        brain.tick()
    return brain

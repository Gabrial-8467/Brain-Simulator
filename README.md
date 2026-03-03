# Brain Simulator

Brain Simulator is a developmental cognitive agent prototype.
It is designed to accumulate experiences over time and update internal state through:

- neurochemical dynamics
- autobiographical memory
- identity/development updates
- attention-based thought selection
- reflection and narrative updates

## What Is Implemented

- Core chemistry model with four chemicals: dopamine, cortisol, oxytocin, serotonin
- Chemical interactions, decay, noise, and clamping
- Dynamic identity traits: competence, social_value, resilience, intelligence
- Development tracking: experience points, reflection depth, maturity
- Global Workspace attention model (`Thought` + `GlobalWorkspace`)
- Consciousness score based on focus stability + development/reflection
- Autobiographical memory with event recording and memory-thought proposals
- Narrative engine that updates a short self-narrative from recent events
- Self-reflection with regret and wisdom tracking
- Synthetic environment that generates one life event per simulation cycle
- Perception pipelines:
  - `brain.perceive(event)` for structured life events
  - `brain.observe_perception(modality, content, source)` for text modality input
  - `brain.receive_visual_signal(signal)` for structured visual signals
  - `brain.receive_hearing_signal(signal)` for structured hearing signals

## Current CLI

`main.py` supports:

- `--mode simulate` (default)
- `--mode live`
- `--cycles <int>`
- `--deterministic`

Examples:

```bash
python main.py --mode simulate --cycles 100
python main.py --mode live
python main.py --mode simulate --cycles 500 --deterministic
```

## How Simulation Runs

In simulate mode:

1. `Simulator` generates one synthetic developmental event each cycle.
2. The event is sent to `brain.perceive(...)`.
3. Optional scenario events (from `simulation/scenarios.py`) are injected.
4. Brain runs `tick()` and outputs updated state (and optional decision if engine is attached).

## Programmatic Perception APIs

You can feed external sensors later without changing the core loop.

### Event-style input

```python
brain.perceive({
    "content": "You are praised for trying.",
    "category": "praise",
    "valence": 0.8,
    "intensity": 0.7,
    "source": "simulated",
    "timestamp": 0.0,
})
```

### Structured vision input

```python
brain.receive_visual_signal({
    "objects": ["person", "bottle"],
    "attributes": {"person": ["red"]},
    "relations": [{"from": "person", "rel": "near", "to": "bottle"}],
    "motion_level": 0.4,
    "confidence": 0.9,
    "source": "camera_pipeline",
    "timestamp": 0.0,
})
```

### Structured hearing input

```python
brain.receive_hearing_signal({
    "transcript": "Good job, keep trying",
    "speaker_type": "caregiver",
    "sentiment": 0.7,
    "prosody_intensity": 0.6,
    "keywords": ["praise", "support"],
    "source": "audio_pipeline",
    "timestamp": 0.0,
})
```

## Output State Includes

`brain.get_state()` returns, among others:

- chemical values
- identity snapshot (`identity_*`)
- development snapshot (`development_*`)
- recent perceptions
- learned concepts
- wisdom
- self narrative
- consciousness score

## Project Notes

- Decision engine exists (`decision/decision_engine.py`) and is attention-driven, but `main.py` currently initializes `VirtualBrain` without attaching a decision engine.
- This repository is a research/development prototype, not a production chatbot stack.

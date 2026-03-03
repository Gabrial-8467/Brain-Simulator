# Virtual Brain Engine - Implemented Feature List

This file lists features that are currently present in the codebase.

## 1. Core Brain State

- Four modeled chemicals: dopamine, cortisol, oxytocin, serotonin
- Per-chemical baseline, decay, noise, min/max clamping
- Chemical interaction matrix support (`config/chemicals.yaml`)
- Risk tolerance, fatigue, stress accumulator, recovery counters

## 2. Identity and Development

- Dynamic identity traits:
  - competence
  - social_value
  - resilience
  - intelligence
- Evidence-based trait updates with learning rate
- Development metrics:
  - experience_points
  - emotional_weight
  - stress_exposure
  - success_exposure
  - reflection_depth
  - maturity
- Development stage labels: baby, child, teen, adult

## 3. Attention and Consciousness

- `Thought` model with:
  - content, source, emotional_weight, novelty, relevance_to_goals, recency, metadata
- Global Workspace competition:
  - weighted activation (emotional/novelty/relevance/recency)
  - current focus and streak tracking
  - focus stability score
- Internal spontaneous thought generator (`core/internal_thoughts.py`)
- Consciousness score from:
  - focus stability/streak
  - memory/goal focus bonus
  - development and reflection bonuses

## 4. Memory and Narrative

- Autobiographical memory:
  - event recording with chemicals, identity snapshot, metadata
  - recent event retrieval
  - memory-thought proposal to workspace
- Narrative engine:
  - computes narrative from recent event trends
  - maintains identity bias values with decay
  - exposes current narrative string

## 5. Learning and Reflection

- Appraisal engine:
  - emotional prediction per event type
  - confidence/volatility tracking
  - emotional learning updates from outcomes
- Similarity engine:
  - stores event profiles
  - finds similar profiles by chemical/identity distance
  - blended emotional prediction
- Self reflection:
  - regret estimation from chosen vs alternative actions
  - confidence and wisdom updates
  - reflection thought proposals
- Periodic reflection step in brain tick:
  - reviews recent memory
  - increases reflection depth
  - increases wisdom

## 6. Perception Interfaces

- Generic modality perception:
  - `observe_perception(modality, content, source)`
- Experience event perception:
  - `perceive(event)` with content/category/valence/intensity/source/timestamp
- Structured vision interface:
  - `receive_visual_signal(signal)` with objects/attributes/relations/motion/confidence
- Structured hearing interface:
  - `receive_hearing_signal(signal)` with transcript/speaker/sentiment/prosody/keywords
- Perception analysis includes:
  - token normalization
  - entities/attributes/relations extraction
  - novelty/salience/confidence estimates
  - concept learning with strength and modality/source tracking

## 7. Simulation Layer

- Synthetic environment (`simulation/environment.py`) provides:
  - lifecycle events (`PerceptionEvent`)
  - synthetic vision signals (`VisionSignal`)
  - synthetic hearing signals (`HearingSignal`)
- Simulator loop:
  - generates one synthetic event each cycle and calls `brain.perceive(...)`
  - injects optional scenario events
  - runs `brain.tick()`
  - prints state and optional decision output
- Structured scenario builder (`simulation/scenarios.py`)

## 8. Decision Module

- `DecisionEngine` exists and is attention-driven:
  - input is current focus `Thought`
  - base probabilities from `ProbabilityModel`
  - bias from emotional_weight and relevance_to_goals
  - deterministic or stochastic action selection
- Action feedback mapping is supported
- Strategic planner module exists (`decision/strategic_planner.py`)

## 9. CLI and Configuration

- CLI options in `main.py`:
  - `--mode` (`simulate`, `live`)
  - `--cycles`
  - `--deterministic`
- Config files:
  - `config/chemicals.yaml`
  - `config/decision.yaml`
  - `config/engine.yaml`

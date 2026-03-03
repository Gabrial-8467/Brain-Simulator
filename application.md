# Virtual Brain Engine - Practical Applications (Current Scope)

This document lists realistic applications based on features that are currently implemented.

## 1. Cognitive Architecture Prototyping

- Test attention-based cognitive loops using `Thought` + Global Workspace.
- Evaluate how memory, perception, and reflection interact over many cycles.
- Experiment with consciousness scoring tied to focus stability and development state.

## 2. Developmental Simulation Experiments

- Run repeatable synthetic lifecycles with `SyntheticEnvironment`.
- Measure effects of event patterns (`praise`, `criticism`, `failure`, `success`, etc.) on:
  - chemical state
  - identity traits
  - development metrics
  - narrative shifts
- Compare deterministic vs stochastic runs.

## 3. Perception-to-Memory Pipeline Testing

- Feed event signals via `brain.perceive(...)`.
- Feed text modality input via `brain.observe_perception(...)`.
- Feed structured sensor-like inputs:
  - `brain.receive_visual_signal(...)`
  - `brain.receive_hearing_signal(...)`
- Inspect concept growth and recent perception history in exported state.

## 4. Reflection and Wisdom Dynamics

- Observe regret-based reflection using self-reflection module.
- Track periodic reflection effects on:
  - `development_reflection_depth`
  - `wisdom`
  - `consciousness_score`
- Study how reflective updates influence long-run maturity and risk tolerance.

## 5. Narrative and Identity Studies

- Analyze how autobiographical event accumulation updates narrative text.
- Track identity trait drift (`competence`, `social_value`, `resilience`, `intelligence`) under different event schedules.
- Examine coupling between stress exposure, recovery, and resilience changes.

## 6. Educational and Research Demos

- Demonstrate multi-cycle stateful cognition to students or research teams.
- Use CLI simulation mode to show full state evolution per step.
- Use live mode as an interactive debug surface for manual event/perception experiments.

## 7. Integration Baseline for External Sensors

- Use current structured interfaces as integration points for external pipelines:
  - vision system -> `receive_visual_signal`
  - hearing/audio system -> `receive_hearing_signal`
- Keep external sensor logic separate from brain internals while reusing the same learning and memory path.

## Non-goals in Current Repository

The current project does not implement:

- web API service layer
- production persistence/database layer
- camera CLI mode in `main.py`
- LLM chatbot orchestration

The codebase is best used as a research/development cognitive simulation core.

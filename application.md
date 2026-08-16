# Virtual Brain Engine - Practical Applications (Current Scope)

This document lists realistic applications based on features that are currently implemented in the simulator.

## 1. Cognitive Architecture Prototyping

- **Attention Gating & Workspace Competition**: Test attention-based cognitive loops using the `Thought` + `GlobalWorkspace` competitive selection mechanism.
- **Salience Network Gating**: Study transition conditions between Task Positive Network (TPN) and Default Mode Network (DMN) modes modulated by Norepinephrine.
- **Dream & Memory Replays**: Evaluate offline memory consolidation, Hopfield CA3 attractor recall, and sleep cycle recovery (SWS and REM).

## 2. Developmental Simulation Experiments

- **Stress-Slowed Growth**: Measure the impact of stress exposure and chemical volatility on maturity progression and stage transitions (Baby -> Child -> Teen -> Adult).
- **Homeostatic Stability**: Test chemical homeostasis, receptor sensitivity scaling, and matrix interactions under various external event frequencies.
- **Deterministic vs Stochastic Runs**: Compare deterministic runs (greedy selection, no noise) against stochastic runs for reproducibility research.

## 3. Perception-to-Memory Pipeline Testing

- **Perceptual Gating & Appraisal**: Study how the `BeliefEngine` schemas (criticism, failure, support, etc.) appraisal-modulate incoming perceptions.
- **Curiosity-Driven GWT Gating**: Observe how the `CuriosityEngine` logs event frequencies to boost novelty weights in the Global Workspace.
- **Multimodal Sensor Simulation**: Feed text, structured vision, and structured hearing signals, observing semantic concepts and scene parser updates.

## 4. Reinforcement Learning & Planning

- **Striatal RL Action Policies**: Analyze how the `DecisionEngine` maps active mood states to action Q-values, and updates them via Reward Prediction Errors (RPE).
- **Look-Ahead Strategic Planning**: Test recursive tree search planning over lightweight state dictionaries to determine optimal prosocial or survival actions.
- **Goal System Gating**: Track how Goal System values (Safety, Mastery, Social Connection) influence workspace selection relevance and action reinforcement.

## 5. Narrative, Identity, and Speech Studies

- **Evidence-Based Identity**: Trace trait values (`competence`, `social_value`, `resilience`, `intelligence`) as they accumulate evidence over developmental cycles.
- **Self-Narrative Synthesis**: Study how the `NarrativeEngine` updates internal monologues and records milestones.
- **Linguistic Speech Regulation**: Investigate how the `SpeechRegulator` truncates, limits, and prefixes responses based on cortisol levels, oxytocin levels, and maturity stages.

## 6. Metacognition & Self-Reflection

- **Regret-to-Wisdom Dynamics**: Track how counterfactual comparisons between chosen and best-alternative actions generate regret, reducing competence but increasing Wisdom.
- **Reflective GWT Intrusion**: Study how high regret posts reflection thoughts back to the workspace to redirect attention to mistakes.

## 7. Educational and Research Demos

- Demonstrate multi-cycle stateful, biologically inspired cognition to students or research teams.
- Use the CLI simulation mode to inspect full state logs at each step or live mode for manual interactive debug scenarios.

## 8. Automated Application Scaffolding

The brain generates complete, runnable vertical applications (deterministically, no LLM):

- **Eight full-stack kinds**: `food_delivery`, `ecommerce`, `booking`, `task_tracker`, `chat`, `blog`, `notes`, `fitness` — each producing a Flask REST backend, SQLite schema, single-page frontend, Docker deployment files, and per-app README.
- **Learned-language gating**: generation is blocked until the brain has learned the required language from perceptions, so capabilities are tied to demonstrated knowledge rather than assumed.
- **Out-of-the-box vertical features**: pbkdf2-hashed session auth, SQLite persistence (WAL mode, `DATABASE_PATH` override), search + pagination, simulated payments, and real-time chat via Server-Sent Events.
- **Kind aliases**: natural phrasing such as "zomato", "cms", "todo", or "workout" is normalized to the matching kind.

## 9. Deterministic Self-Debugging & Auto-Repair

- **Static bug detection**: scan a generated project for leftover template tokens, Python syntax errors, backend-referenced tables missing from the schema, seed inserts into unknown tables, frontend route calls with no matching backend route, and missing SQLite bootstrap.
- **Structured reports**: every bug carries a severity, file location, and human-readable message; report-only mode never modifies the project.
- **Safe in-place repair**: with `fix=True` the brain renames an unused declared table to the missing referenced table, inserts a missing `_init_db()` call, or deterministically rebuilds the app from its template when consistency errors remain.
- **Verification loop**: after a repair the debugger is re-run and must report zero bugs; live test-client flows (register → authenticate → CRUD → authorization boundaries) confirm the app still works.

## Non-goals in Current Repository

The current project does not implement:

- Production-grade external database layer (the brain's own state is a local JSON storage file; generated apps persist to local SQLite, with the generated README documenting a PostgreSQL migration path).
- Multi-agent networked environment.
- Live camera feed or audio capture CLI tools.
- Direct LLM conversational wrapper (Aashu uses a local Ollama instance purely for speech synthesis, never for code generation, planning, or debugging).

The codebase is best used as a research/development cognitive simulation core.

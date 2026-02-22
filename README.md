# Virtual Brain Engine

A sophisticated cognitive simulation framework that models the complex interactions between neurochemical dynamics, memory systems, decision-making processes, and developmental psychology. This project creates a virtual brain that can learn, adapt, and respond to stimuli in a biologically-inspired manner.

## Overview

The Virtual Brain Engine simulates the intricate balance of neurochemicals that influence behavior, emotion, and cognition. It models systems including:

- **Neurochemical Dynamics**: Dopamine, cortisol, oxytocin, and serotonin interactions with realistic decay and noise
- **Cognitive Systems**: Autobiographical memory, narrative generation, and self-reflection
- **Learning Mechanisms**: Appraisal engine, similarity-based learning, and pattern recognition
- **Developmental Psychology**: Dynamic identity formation, attachment systems, and goal-setting
- **Resilience Modeling**: Stress accumulation, burnout prevention, and recovery mechanisms

## Features

- **Real-time Neurochemical Simulation**: Models the interaction and decay of four key brain chemicals with stochastic noise
- **Autobiographical Memory**: Event-based memory system with emotional and chemical context tracking
- **Narrative Engine**: Generates coherent narratives from life events and experiences
- **Appraisal Learning**: Similarity-based emotional learning with surprise detection and volatility tracking
- **Strategic Planning**: Multi-step future simulation with counterfactual reasoning for optimal decision-making
- **Counterfactual Reflection**: Regret-based learning from alternative outcomes and wisdom accumulation
- **Dynamic Identity**: Evolving self-concept based on experiences and chemical states
- **Developmental Systems**: Attachment modeling, goal formation, and curiosity drives
- **Resilience Modeling**: Stress accumulation, burnout thresholds, and recovery mechanisms
- **Sensory Perception System**: Camera-based visual scene analysis and multi-modal sensory integration
- **Configurable Parameters**: YAML-based configuration for all system parameters
- **Scenario Testing**: Built-in structured learning scenarios and stress testing capabilities
- **Live Mode**: Interactive mode for real-time brain state exploration and manual stimulation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd BRAIN
```

2. Create and activate virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Simulation

Run a default simulation with 1000 cycles:
```bash
python main.py
```

### Custom Simulation

Run with specific parameters:
```bash
python main.py --cycles 5000 --deterministic
```

### Live Mode

Interactive mode for exploring brain states:
```bash
python main.py --mode live
```

### Scenario-based Simulation

The system runs structured learning scenarios by default, simulating events like praise and criticism at regular intervals to model learning and development.

## Usage

### Command Line Options

- `--mode`: Choose between `simulate` (default) or `live`
- `--cycles`: Number of simulation cycles (default: 100)
- `--deterministic`: Run without stochastic noise for reproducible results

### Configuration

The system is configured through YAML files in the `config/` directory:

- `chemicals.yaml`: Defines neurochemical properties, interactions, and global settings
- `decision.yaml`: Decision engine configuration with actions and feedback mappings
- `engine.yaml`: Core simulation engine settings and update orders

## Architecture

```
BRAIN/
│
├── main.py                 # Entry point and CLI interface
│
├── core/                   # Core brain systems
│   ├── brain.py           # Main VirtualBrain class
│   ├── identity.py        # Dynamic identity formation
│   ├── development.py     # Developmental processes
│   ├── engine.py          # Core simulation engine
│   ├── homeostasis.py     # Self-regulation systems
│   ├── noise.py           # Stochastic noise generation
│   ├── interactions.py    # Chemical interaction logic
│   ├── state.py           # State management
│   └── self_reflection.py # Metacognitive processes
│
├── chemicals/             # Neurochemical systems
│   ├── registry.py        # Chemical registration and management
│   ├── models.py          # Chemical behavior models
│   └── interactions.py    # Chemical interaction calculations
│
├── config/                # Configuration files
│   ├── chemicals.yaml     # Chemical definitions and interactions
│   ├── decision.yaml      # Decision engine configuration
│   └── engine.yaml        # Engine settings and parameters
│
├── cognition/             # Cognitive systems
│   ├── autobiographical_memory.py  # Life event memory
│   └── narrative_engine.py         # Story generation
│
├── learning/              # Learning mechanisms
│   ├── appraisal_engine.py         # Emotional learning
│   ├── similarity_engine.py       # Pattern similarity
│   ├── abstraction_engine.py      # Concept formation
│   └── chemical_optimizer.py       # Chemical regulation
│
├── memory/                # Memory systems
│   ├── memory_manager.py  # Main memory management
│   ├── schemas.py         # Memory data structures
│   ├── storage.py         # Persistent storage
│   ├── associative_memory.py  # Associative memory patterns
│   ├── context_tracker.py     # Context tracking
│   ├── emotional_index.py     # Emotional memory indexing
│   └── pattern_engine.py      # Pattern recognition
│
├── decision/              # Decision-making systems
│   ├── decision_engine.py # Core decision logic
│   ├── probability_model.py # Probabilistic modeling
│   └── strategic_planner.py # Multi-step strategic planning
│
├── bias/                  # Cognitive bias systems
│   ├── bias_engine.py     # Bias modeling
│   └── bias_models.py     # Specific bias implementations
│
├── development/           # Developmental psychology systems
│   ├── attachment_system.py   # Attachment modeling
│   ├── curiosity_engine.py    # Curiosity simulation
│   └── goal_system.py         # Goal formation and pursuit
│
├── simulation/            # Simulation tools
│   ├── simulator.py       # Main simulation controller
│   ├── scenarios.py       # Predefined scenarios
│   └── stress_tests.py    # System stress testing
│
├── utils/                 # Utility functions
│   ├── logger.py          # Logging configuration
│   ├── validators.py      # Data validation
│   └── helpers.py         # Helper functions
│
└── myenv/                 # Virtual environment
```

## Core Components

### VirtualBrain Class

The main orchestrator that coordinates all subsystems:

```python
from core.brain import VirtualBrain

brain = VirtualBrain(
    chemical_configs=chemical_configs["chemicals"],
    interaction_matrix=chemical_configs.get("interactions"),
    deterministic=False
)
```

### Chemical System

Models four key neurochemicals with realistic interactions:

- **Dopamine**: Reward and motivation (baseline: 50, decay: 0.02)
- **Cortisol**: Stress response (baseline: 40, decay: 0.02)
- **Oxytocin**: Social bonding (baseline: 60, decay: 0.015)
- **Serotonin**: Mood regulation (baseline: 55, decay: 0.02)

### Cognitive Systems

- **Autobiographical Memory**: Event-based memory with chemical and emotional context
- **Narrative Engine**: Generates coherent life narratives from stored events
- **Self-Reflection**: Metacognitive processes for self-awareness

### Learning Mechanisms

- **Appraisal Engine**: Emotional learning with similarity-based pattern recognition
- **Similarity Engine**: Pattern matching and experience comparison
- **Abstraction Engine**: Concept formation and generalization
- **Strategic Planner**: Multi-step future simulation for optimal action selection
- **Counterfactual Reflection**: Regret-based learning and wisdom accumulation

### Developmental Systems

- **Dynamic Identity**: Evolving self-concept based on experiences
- **Attachment System**: Social bonding and relationship modeling
- **Goal System**: Goal formation, pursuit, and achievement tracking
- **Curiosity Engine**: Exploration and learning drives

### Sensory Perception System

- **Visual Scene Analysis**: Camera-based brightness detection and scene classification
- **Multi-modal Integration**: Combines vision, speaking, and other sensory inputs
- **Concept Learning**: Visual concept memory with strength tracking and timestamps
- **Perceptual Events**: Chemical responses to visual and sensory stimuli
- **Scene Classification**: Dark, normal, and bright scene categorization

### Strategic Planning System

- **Multi-step Simulation**: Recursive future state prediction with configurable depth
- **Counterfactual Reasoning**: Evaluation of alternative actions and outcomes
- **Goal Alignment**: Decision scoring based on active goals and identity growth
- **Emotional Forecasting**: Predicts emotional responses to potential actions

### Self-Reflection System

- **Regret Calculation**: Computes regret from unchosen alternatives
- **Wisdom Accumulation**: Long-term learning from counterfactual thinking
- **Profile Blending**: Combines predicted outcomes with similar historical patterns
- **Maturity Development**: Gradual growth from reflective experiences

## Configuration


### Chemical Configuration

```yaml
chemicals:
  dopamine:
    min: 0
    max: 100
    baseline: 50
    decay: 0.02
    noise: 0.5
  
  cortisol:
    min: 0
    max: 100
    baseline: 40
    decay: 0.02
    noise: 0.4

interactions:
  cortisol:
    dopamine: -0.0008  # Cortisol reduces dopamine
  serotonin:
    cortisol: -0.0005  # Serotonin reduces cortisol
  
global_settings:
  clamp_after_interaction: true
  clamp_after_noise: true
```

### Decision Engine Configuration

```yaml
decision:
  actions:
    - support
    - challenge  
    - suggest
    - refuse
    - neutral
  
  base_probabilities:
    support: 0.35
    challenge: 0.25
    suggest: 0.20
    refuse: 0.10
    neutral: 0.10
  
  chemical_influence:
    dopamine:
      support: 0.002
    cortisol:
      challenge: 0.003
  
  action_feedback:
    support:
      dopamine: 2
      oxytocin: 1
    challenge:
      cortisol: 1
      serotonin: -0.5
```

### Engine Configuration

```yaml
engine:
  deterministic_mode: false
  
  update_order:
    - interactions
    - homeostasis
    - noise
    - clamp
  
  simulation_defaults:
    cycles: 1000
    log_interval: 100
  
  stability:
    enable_homeostasis: true
    enable_noise: true
    enable_interactions: true
```

### Scenario Configuration

The system includes predefined scenarios that simulate learning experiences:

- **Praise Events**: Occur every 10 steps, increase dopamine, oxytocin, serotonin
- **Criticism Events**: Occur every 25 steps, increase cortisol, decrease dopamine/serotonin
- **Challenge Events**: Occur every 40 steps, moderate stress with potential growth

### Strategic Planning Configuration

The strategic planner uses configurable parameters for future simulation:

- **Planning Depth**: Number of future steps to simulate (default: 2)
- **Risk Aversion**: Dynamic risk tolerance affecting decisions (default: 0.2)
- **Personality Influence**: How competence and resilience affect action selection
- **Future Discount Factor**: Weight given to future outcomes (default: 0.7)
- **Regret Memory Size**: Maximum stored regret experiences (default: 200)
- **Wisdom Growth Rate**: Learning rate from counterfactual reflection (default: 0.02)

## API Reference

### Main Classes

- `VirtualBrain`: Core brain simulation class with cognitive and developmental systems
- `Simulator`: Simulation controller for running scenarios and managing time steps
- `AutobiographicalMemory`: Event-based memory storage and retrieval
- `AppraisalEngine`: Emotional learning and experience evaluation
- `NarrativeEngine`: Story generation from life events
- `DynamicIdentity`: Evolving self-concept and personality traits (competence, social_value, resilience, intelligence)
- `DynamicDevelopment`: Maturity and experience tracking system
- `StrategicPlanner`: Multi-step future simulation and optimal action selection
- `SelfReflection`: Counterfactual thinking and wisdom accumulation
- `SimilarityEngine`: Pattern matching and experience comparison
- `DecisionEngine`: Configurable decision-making with probability modeling
- `GoalSystem`: Goal formation, pursuit, and achievement tracking
- `AssociativeMemory`: Long-term memory with human-like decay patterns

### Key Methods

```python
# Brain tick - advance simulation by one cycle
brain.tick()

# Get current brain state (includes chemicals, identity, development)
state = brain.get_state()

# Visual scene analysis
scene_description = brain.describe_visual_scene(brightness=100)
print(f"Scene: {scene_description}")

# Process sensory perceptions
brain.observe_perception(
    modality="vision",
    content="I see a bright light",
    source="camera"
)

brain.observe_perception(
    modality="hearing", 
    content="I hear music playing",
    source="microphone"
)

# Get recent perceptions
recent_perceptions = state.get("recent_perceptions", [])
print(f"Recent perceptions: {recent_perceptions}")

# Get learned concepts from perception
learned_concepts = state.get("learned_concepts", [])
print(f"Learned concepts: {learned_concepts}")

# Inject external event
brain.inject_event(
    effects={"dopamine": 10, "cortisol": -5},
    event_type="reward",
    source="environment",
    tags=["positive", "achievement"]
)

# Get recent memories
recent_events = brain.autobiography.get_recent_events(n=50)

# Generate life narrative
narrative = brain.narrative_engine.get_current_narrative()

# Check stress levels
stress_level = brain.stress_accumulator
is_burnout_risk = stress_level > brain.burnout_threshold

# Strategic planning
best_action = brain.strategic_planner.choose_action(
    brain=brain,
    probabilities={"support": 0.3, "challenge": 0.2, "suggest": 0.5}
)

# Self-reflection insights
wisdom_score = brain.self_reflection.get_wisdom()
last_regret = brain.self_reflection.get_last_regret()

# Identity and development
competence = brain.identity.get("competence")
maturity = brain.development.maturity
experience = brain.development.experience_points

# Decision making
if brain.decision_engine:
    decision = brain.decision_engine.decide(state)
    action = decision["action"]
    feedback = decision["feedback"]
```

## Examples

### Manual Event Injection

```python
# Inject a positive event
brain.inject_event(
    effects={
        "dopamine": 15,
        "oxytocin": 8,
        "serotonin": 5
    },
    event_type="achievement",
    source="personal_goal",
    tags=["success", "milestone"]
)

# Advance simulation
result = brain.tick()
print(f"Decision: {result}")
print(f"State: {brain.get_state()}")

### Decision Engine Example

```python
# Load decision configuration
with open("config/decision.yaml", "r") as f:
    decision_config = yaml.safe_load(f)

# Create decision engine
decision_engine = DecisionEngine(decision_config["decision"])

# Make decision based on current chemical state
result = decision_engine.decide(brain.get_state())
chosen_action = result["action"]
probabilities = result["probabilities"]
feedback = result["feedback"]

print(f"Chosen action: {chosen_action}")
print(f"Action probabilities: {probabilities}")
print(f"Chemical feedback: {feedback}")

# Apply feedback to brain
brain._apply_decision_feedback(feedback)
```

### Strategic Planning Example

```python
# Configure strategic planner with custom depth
brain.strategic_planner.max_depth = 3
brain.strategic_planner.risk_aversion = 0.1  # More risk-taking

# Define action probabilities (from decision engine)
probabilities = {
    "support": 0.35,
    "challenge": 0.25,
    "suggest": 0.20,
    "refuse": 0.10,
    "neutral": 0.10
}

# Get optimal action based on future simulation
optimal_action = brain.strategic_planner.choose_action(
    brain=brain,
    probabilities=probabilities
)

print(f"Strategic recommendation: {optimal_action}")

# Execute the action and observe outcomes
result = brain.tick()
print(f"Decision outcome: {result}")
```

### Self-Reflection Analysis

### Self-Reflection Analysis

```python
# After making decisions, analyze regret and wisdom
regret = brain.self_reflection.reflect_on_decision(
    chosen_action="support",
    available_actions=["support", "challenge", "suggest", "refuse", "neutral"],
    current_state=brain.get_state()
)

print(f"Regret from alternative actions: {regret:.2f}")
print(f"Accumulated wisdom: {brain.self_reflection.get_wisdom():.2f}")

# Wisdom influences future decision quality
if brain.self_reflection.get_wisdom() > 0.5:
    print("High wisdom achieved - better strategic decisions expected")

# Track identity development
identity_snapshot = brain.identity.get_snapshot()
print(f"Current identity: {identity_snapshot}")

# Monitor developmental progress
print(f"Maturity level: {brain.development.maturity:.2f}")
print(f"Experience points: {brain.development.experience_points}")
print(f"Reflection depth: {brain.development.reflection_depth:.2f}")
```

### Memory and Learning Example

```python
# Record an associative memory
brain.associative_memory.update(
    context_key="social_success",
    chemical_deltas={"dopamine": 5, "oxytocin": 3, "serotonin": 2},
    reward_score=8.0
)

# Retrieve associated memory
memory = brain.associative_memory.get_association("social_success")
if memory:
    print(f"Memory strength: {memory['strength']:.2f}")
    print(f"Emotional signature: {memory['emotional_signature']}")
    print(f"Frequency: {memory['frequency']}")

# Update narrative based on recent events
recent_events = brain.autobiography.get_recent_events(50)
brain.narrative_engine.update_narrative(recent_events)
print(f"Current narrative: {brain.narrative_engine.get_current_narrative()}")
```

## Testing

### Running Simulations

The system includes built-in testing scenarios:

```bash
# Run default structured learning simulation
python main.py

# Run deterministic simulation for reproducible results
python main.py --deterministic --cycles 1000

# Run interactive live mode
python main.py --mode live
```

### Stress Testing

```bash
# Run extended stress test
python main.py --cycles 5000
```

### Custom Testing

Create custom scenarios by modifying `simulation/scenarios.py` or inject events programmatically:

```python
# Custom event injection for testing
brain.inject_event(
    effects={"cortisol": 30},  # High stress
    event_type="emergency",
    source="test_scenario"
)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]

## Acknowledgments

This project draws inspiration from neuroscience research, cognitive psychology, and computational modeling of brain function.

## Future Development

- [ ] GUI interface for real-time visualization
- [ ] Extended chemical system (more neurotransmitters)
- [ ] Machine learning integration for pattern recognition
- [ ] Networked multi-brain simulations
- [ ] Integration with external data sources

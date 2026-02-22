## Virtual Brain Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 500MB free space
- **Camera**: Optional, for visual perception features
- **Microphone**: Optional, for audio perception features

## Installation

### Prerequisites

Ensure you have Python 3.8+ installed. Check with:
```bash
python --version
```

### Quick Install

1. Clone the repository:
```bash
git clone https://github.com/Gabrial-8467/Brain-Simulator.git
cd Brain-Simulator
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

### Troubleshooting

#### Common Issues

1. **Camera Access Issues** (Windows):
   ```bash
   # Install OpenCV with additional dependencies
   pip install opencv-python --upgrade
   pip install opencv-contrib-python
   ```

2. **Audio Issues** (macOS/Linux):
   ```bash
   # Install additional audio dependencies
   pip install pyaudio
   ```

3. **Virtual Environment Issues**:
   ```bash
   # Remove and recreate venv
   rm -rf myenv
   python -m venv myenv
   source myenv/bin/activate  # Windows: myenv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Permission Issues** (Linux/macOS):
   ```bash
   # Fix camera/microphone permissions
   sudo usermod -a -G video $USER
   sudo usermod -a -G audio $USER
   ```

#### Getting Help

- 📖 Check the [Issues](https://github.com/Gabrial-8467/Brain-Simulator/issues) page
- 🐛 Report bugs with detailed error messages
- 💡 Feature requests are welcome!

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

<!-- ## Architecture

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
``` -->

<!-- ## Core Components

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
- **Maturity Development**: Gradual growth from reflective experiences -->

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

<!-- ### Key Methods

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
``` -->

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

We welcome contributions to the Virtual Brain Engine! Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
## 📄 License

This project is licensed under the **Gabrial Deora Source Code License (GDSCL) v1.0** - see the [LICENSE](LICENSE) file for the full text.

### 🎯 License Overview

```python
GABRIAL DEORA SOURCE CODE LICENSE (GDSCL) v1.0
Copyright (c) 2026 Gabrial Deora. All rights reserved.

1. Ownership
   All source code, files, assets, and documentation contained in this repository (the "Software") are the exclusive intellectual property of the Author.

2. Viewing Permission
   Permission is granted to any person to view and read the Software for educational and reference purposes only.

3. Use by Permission Only
   No individual or organization is allowed to use the Software, in whole or in part, in any project, product, assignment, service, research, or commercial activity without obtaining prior written permission from the Author.

4. Prohibited Actions (Without Permission)
   The following actions are strictly prohibited unless the Author has granted written consent:

• Copying or reusing the code
• Modifying or creating derivative works
• Uploading to another repository
• Redistributing the Software
• Deploying the project publicly or privately
• Using the architecture, logic, database schema, or API design in another project
• Commercial use or monetization

5. Requesting Permission
   Anyone wishing to use the Software must first obtain explicit written approval from the Author.

6. No Implied License
   Access to this repository does not grant any ownership or usage rights.

7. Violation
   Unauthorized use of the Software constitutes copyright infringement and may result in legal action, including takedown requests and account reporting.

8. Disclaimer
   The Software is provided "as is", without warranty of any kind, express or implied.
```

### ✅ What You Can Do

- **👁️ View & Read**: View and read the source code for educational and reference purposes
- **📚 Learn**: Study the architecture and implementation for learning purposes
- **🔍 Reference**: Use as a reference for understanding similar concepts

### 🚫 What Requires Permission

- **📋 Copying**: Copying or reusing any part of the code
- **🔧 Modification**: Modifying or creating derivative works
- **📤 Redistribution**: Uploading to another repository or redistributing
- **🚀 Deployment**: Deploying the project publicly or privately
- **🏗️ Architecture Use**: Using the architecture, logic, database schema, or API design
- **💰 Commercial Use**: Any commercial use or monetization
- **🔬 Research**: Using in research projects without permission
- **📦 Integration**: Using in any project, product, or service

### 📧 Requesting Permission

To request permission to use this software, please:
- 📧 Contact the Author directly for written approval
- 📋 Provide detailed information about intended use
- 🎯 Specify the scope and nature of your project
- ⏳ Allow reasonable time for permission review

### ⚠️ Important Notes

- **No Implied Rights**: Repository access does not grant usage rights
- **Legal Protection**: Unauthorized use constitutes copyright infringement
- **Enforcement**: Violations may result in legal action and takedown requests
- **All Rights Reserved**: Author maintains exclusive intellectual property rights

### 📦 Third-Party Dependencies

This project incorporates open-source packages with their respective licenses:

| Package | Version | License | Type |
|---------|---------|---------|------|
| **PyYAML** | ≥6.0 | MIT License | Core Dependencies |
| **NumPy** | ≥1.21.0 | BSD License | Core Dependencies |
| **SciPy** | ≥1.7.0 | BSD License | Core Dependencies |
| **OpenCV** | ≥4.9.0 | Apache License 2.0 | Computer Vision |
| **Pillow** | ≥8.0.0 | HPND License | Image Processing |
| **pyttsx3** | ≥2.90 | GPL v3 | Audio Processing |
| **sounddevice** | ≥0.4.0 | MIT License | Audio Processing |
| **soundfile** | ≥0.10.0 | BSD License | Audio Processing |
| **ollama** | ≥0.1.0 | Apache License 2.0 | AI & ML |
| **pandas** | ≥1.3.0 | BSD License | Data Processing |
| **matplotlib** | ≥3.5.0 | PSF License | Data Visualization |
| **pytest** | ≥6.0.0 | MIT License | Development & Testing |

**Note**: Third-party dependencies are subject to their respective licenses as listed above. The GDSCL license applies only to the Virtual Brain Engine codebase.

### 🔍 License Type

The **Gabrial Deora Source Code License (GDSCL) v1.0** is a **proprietary, source-available license** that:

- 🔒 **Restricts usage** without explicit permission
- 👁️ **Allows viewing** for educational purposes
- 📋 **Requires written consent** for any use
- 🛡️ **Protects intellectual property** rights
- ⚖️ **Enforces copyright** protection

---

**⚠️ Important**: This is a proprietary license. Do not use this software in any project without first obtaining written permission from the Author.

## Future Development

### Roadmap

- [ ] **GUI Interface**: Real-time visualization dashboard with brain state monitoring
- [ ] **Extended Chemical System**: Additional neurotransmitters (GABA, norepinephrine, endorphins)
- [ ] **Machine Learning Integration**: Deep learning for pattern recognition and prediction
- [ ] **Advanced Analytics**: Statistical analysis tools for brain behavior patterns
- [ ] **Export/Import**: Save and load brain states for continuity
- [ ] **Plugin System**: Extensible architecture for custom modules

### Contributing to Roadmap

We prioritize features based on community feedback. Vote for existing issues or create new ones to help shape the project's future!

---

## 🧠 Acknowledgments

This project draws inspiration from:
- **Neuroscience Research**: Latest findings in brain chemistry and cognitive function
- **Cognitive Psychology**: Theories of memory, learning, and decision-making
- **Computational Modeling**: Advances in brain simulation and artificial intelligence
- **Open Source Community**: The countless developers who make these tools possible

**Special thanks** to the researchers and developers who have contributed to our understanding of the human brain.

---

<div align="center">

**⭐ Star this repository if you find it interesting!**

Made with ❤️ by [Gabrial Deora](https://github.com/Gabrial-8467)

</div>

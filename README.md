# Brain Simulator

*A biologically-inspired cognitive simulation that learns, adapts, and evolves through experience*

[![License: GDSCL](https://img.shields.io/badge/License-GDSCL%20v1.0-red.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🧠 See It In Action

```
Step 1: Brain receives praise → Dopamine: 58→66, Oxytocin: 60→65
Step 2: Forms positive memory "I am valued" with emotional signature
Step 3: Identity trait "competence" increases: 0.45→0.48
Step 4: Strategic planner learns "seek positive social interactions"
Step 25: Brain receives criticism → Cortisol: 40→50, Dopamine: 66→62
Step 26: Stress accumulates, resilience systems activate
Step 27: Memory links criticism to previous praise events
Step 28: Self-reflection calculates regret, wisdom increases: 0.0→0.02
```

---

## What This Project Is

Brain Simulator creates a **virtual cognitive system** that models how the brain processes experiences, forms memories, and makes decisions. Unlike chatbots that simply respond to prompts, this system:

- **Lives through time** - experiences events sequentially and builds a life story
- **Has internal chemistry** - dopamine, cortisol, oxytocin, and serotonin interact realistically
- **Forms memories** - stores events with emotional context and retrieves them associatively  
- **Develops personality** - identity traits evolve based on experiences
- **Learns from mistakes** - uses counterfactual thinking to gain wisdom
- **Plans strategically** - simulates future outcomes before acting

The system demonstrates **emergent behavior** - complex psychological patterns arise from simple neurochemical rules.

---

## Key Features

- **Real-time Neurochemical Simulation** - Four key brain chemicals with realistic decay and interactions
- **Autobiographical Memory** - Event-based memory with emotional and chemical context
- **Dynamic Identity Formation** - Personality traits (competence, resilience, intelligence) evolve over time
- **Strategic Planning** - Multi-step future simulation with counterfactual reasoning
- **Self-Reflection & Wisdom** - Learns from alternative outcomes and accumulates wisdom
- **Stress & Resilience Modeling** - Burnout prevention and recovery mechanisms
- **Narrative Generation** - Creates coherent life stories from accumulated experiences
- **Sensory Perception** - Camera-based visual analysis and multi-modal integration
- **Configurable Psychology** - YAML-based configuration of all cognitive parameters

---

## How It Works (High Level)

1. **Neurochemical Core**: Four brain chemicals (dopamine, cortisol, oxytocin, serotonin) form the foundation of all behavior
2. **Event Processing**: External events trigger chemical responses that create emotional states
3. **Memory Formation**: Events are stored with chemical signatures and retrieved through similarity matching
4. **Identity Evolution**: Repeated patterns shape personality traits and self-concept
5. **Strategic Planning**: System simulates multiple future paths before choosing actions
6. **Learning & Adaptation**: Both positive reinforcement and regret-based learning modify future behavior

The system runs in discrete time steps, with each "tick" representing a moment of cognitive processing.

---

## Installation

### Prerequisites
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/Gabrial-8467/Brain-Simulator.git
cd Brain-Simulator

# Create virtual environment
python -m venv brain_env
source brain_env/bin/activate  # Windows: brain_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Quick Start

### Run Your First Simulation
```bash
python main.py --cycles 100
```

### Interactive Mode
```bash
python main.py --mode live
```

### Deterministic Testing
```bash
python main.py --cycles 500 --deterministic
```

---

## Example Behavior Log

```
[START] Virtual Brain initialized - dopamine:50, cortisol:40, oxytocin:60, serotonin:55
[STEP 10] Praise received - dopamine:58→66, oxytocin:60→65, serotonin:55→58
[STEP 10] Memory formed: "Received positive feedback" with emotional signature [0.8, 0.2, 0.7, 0.6]
[STEP 10] Identity updated: competence 0.45→0.48, social_value 0.50→0.52
[STEP 25] Criticism received - cortisol:40→50, dopamine:66→62, serotonin:58→56
[STEP 25] Stress accumulator: 0→15, resilience systems activated
[STEP 25] Memory linked: Associated criticism with previous praise events
[STEP 26] Self-reflection: Regret calculated from alternative responses, wisdom: 0.0→0.02
[STEP 26] Strategic learning: Future simulations weight positive outcomes more heavily
[STEP 50] Burnout risk detected - implementing recovery protocols
[STEP 75] Resilience trait increased: 0.5→0.53 from stress recovery
[END] Final identity: competence:0.62, resilience:0.53, intelligence:0.58, wisdom:0.15
```

---

## Use Cases

### Research & Academia
- **Cognitive Psychology**: Study emotion, memory, and decision-making
- **Neuroscience**: Model neurochemical interactions and behavioral outcomes
- **AI Development**: Test biologically-inspired learning algorithms

### Game Development  
- **NPC Intelligence**: Create characters with personality development
- **Dynamic Storytelling**: Generate evolving character narratives
- **Emotional AI**: Build agents with realistic emotional responses

### Education & Training
- **Psychology Education**: Demonstrate cognitive processes interactively
- **Decision Training**: Model consequences of different strategies
- **Stress Management**: Teach resilience and coping mechanisms

### Creative Applications
- **Character Development**: Generate backstories and personality arcs
- **Interactive Fiction**: Create responsive narrative systems
- **Artificial Companions**: Build agents with emotional depth

---

## License

This project is licensed under the **Gabrial Deora Source Code License (GDSCL) v1.0**. See the [LICENSE](LICENSE) file for complete terms.

**Summary**: Viewing and educational use permitted. All other uses require explicit written permission from the author.

---

## Missing Sections & Improvements

**Currently Missing:**
- Real-time visualization dashboard
- Web interface for parameter tuning
- Pre-built use case examples
- Performance benchmarks
- Integration examples with other AI systems

**Could Be More Impressive With:**
- Interactive 3D brain visualization
- Real-time chemical level graphs
- Memory network visualization
- Comparative analysis with human psychology data
- Export/import brain states for sharing
- Multi-brain interaction scenarios

---

<div align="center">

**⭐ Star this repository if you find it interesting!**

Made with ❤️ by [Gabrial Deora](https://github.com/Gabrial-8467)

</div>


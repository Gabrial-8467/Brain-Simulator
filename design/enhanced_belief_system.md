# Enhanced Belief Extraction Layer and Worldview Engine

## Architecture Overview

The enhanced system builds upon the existing BeliefEngine with these key improvements:

### 1. Enhanced Belief Extraction Layer

```python
class EnhancedBeliefEngine(BeliefEngine):
    """Advanced belief extraction with pattern detection and worldview modeling."""
    
    def __init__(self, config: dict | None = None):
        super().__init__(config)
        
        # Enhanced pattern detection
        self.pattern_detectors = {
            'criticism_pattern': CriticismPatternDetector(),
            'success_failure_pattern': SuccessFailurePatternDetector(),
            'social_rejection_pattern': SocialRejectionPatternDetector(),
            'threat_pattern': ThreatPatternDetector(),
            'novelty_adaptation_pattern': NoveltyAdaptationPatternDetector(),
        }
        
        # Belief coherence tracking
        self.belief_network = BeliefNetwork()
        
        # Enhanced mood model
        self.mood_engine = MoodEngine(config.get('mood_config', {}))
        
        # Strategy adaptation
        self.strategy_adaptation = StrategyAdaptationEngine()
        
        # Consciousness factors
        self.consciousness_calculator = ConsciousnessCalculator()
```

### 2. Pattern Detection System

```python
class PatternDetector:
    """Base class for detecting recurring patterns in events."""
    
    def detect_pattern(self, events: list[dict]) -> dict:
        raise NotImplementedError
    
    def calculate_confidence(self, pattern_strength: float, evidence_count: int) -> float:
        base_confidence = min(0.9, pattern_strength * 2.0)
        evidence_bonus = min(0.3, evidence_count / 50.0)
        return base_confidence + evidence_bonus

class CriticismPatternDetector(PatternDetector):
    def detect_pattern(self, events: list[dict]) -> dict:
        criticism_events = [e for e in events if self._is_criticism(e)]
        total_events = len(events)
        
        if len(criticism_events) < 3:
            return {'detected': False}
        
        # Temporal clustering - are criticisms clustered?
        temporal_density = self._calculate_temporal_density(criticism_events)
        
        # Context patterns - what precedes criticism?
        context_analysis = self._analyze_context_patterns(criticism_events, events)
        
        pattern_strength = (len(criticism_events) / total_events) * temporal_density
        
        return {
            'detected': pattern_strength > 0.15,
            'strength': pattern_strength,
            'evidence_count': len(criticism_events),
            'temporal_density': temporal_density,
            'context_patterns': context_analysis,
            'belief_statement': "Criticism often follows my attempts."
        }

class SuccessFailurePatternDetector(PatternDetector):
    def detect_pattern(self, events: list[dict]) -> dict:
        task_events = [e for e in events if self._is_task_related(e)]
        successes = [e for e in task_events if self._is_success(e)]
        failures = [e for e in task_events if self._is_failure(e)]
        
        if len(task_events) < 5:
            return {'detected': False}
        
        success_rate = len(successes) / len(task_events)
        failure_rate = len(failures) / len(task_events)
        
        # Learning trajectory - improving over time?
        learning_trajectory = self._calculate_learning_trajectory(task_events)
        
        pattern_strength = abs(success_rate - failure_rate)
        
        if failure_rate > 0.6:
            belief_statement = "I often fail before I succeed."
        elif success_rate > 0.6 and learning_trajectory > 0.1:
            belief_statement = "Persistent effort helps me solve challenges."
        else:
            return {'detected': False}
        
        return {
            'detected': pattern_strength > 0.2,
            'strength': pattern_strength,
            'evidence_count': len(task_events),
            'success_rate': success_rate,
            'failure_rate': failure_rate,
            'learning_trajectory': learning_trajectory,
            'belief_statement': belief_statement
        }
```

### 3. Dynamic Resilience System

```python
class DynamicResilienceEngine:
    """Resilience as recovery speed, not capped at 1.0."""
    
    def __init__(self, config: dict | None = None):
        self.base_recovery_rate = config.get('base_recovery_rate', 0.02)
        self.chronic_stress_threshold = config.get('chronic_stress_threshold', 58.0)
        self.resilience_decay_rate = config.get('resilience_decay_rate', 0.001)
        self.recovery_bonus_rate = config.get('recovery_bonus_rate', 0.005)
        
        # Track resilience dynamics
        self.resilience_velocity = 0.0  # Rate of change
        self.stress_exposure_history = deque(maxlen=100)
        self.recovery_events = deque(maxlen=50)
        
    def update_resilience(self, cortisol: float, emotional_dip_active: bool, 
                          recovery_counter: int, chronic_stress_steps: int) -> float:
        """Update resilience based on stress exposure and recovery."""
        
        # Track stress exposure
        self.stress_exposure_history.append(cortisol)
        
        # Calculate stress load
        recent_avg_cortisol = sum(self.stress_exposure_history) / len(self.stress_exposure_history)
        stress_load = max(0, (recent_avg_cortisol - self.chronic_stress_threshold) / 20.0)
        
        # Resilience damage from chronic stress
        if chronic_stress_steps > 10:
            damage_rate = self.resilience_decay_rate * (1 + stress_load * 2)
            self.resilience_velocity -= damage_rate
        
        # Resilience growth from recovery
        if emotional_dip_active and recovery_counter > 3:
            recovery_bonus = self.recovery_bonus_rate * (1 + recovery_counter * 0.1)
            self.resilience_velocity += recovery_bonus
            self.recovery_events.append(time.time())
        
        # Natural resilience decay (asymptotic limit)
        current_resilience = self._get_current_resilience()
        if current_resilience > 2.0:  # Soft asymptotic limit
            self.resilience_velocity -= (current_resilience - 2.0) * 0.01
        
        # Apply velocity with damping
        self.resilience_velocity *= 0.95  # Damping factor
        resilience_change = self.resilience_velocity
        
        return resilience_change
    
    def get_recovery_speed_multiplier(self) -> float:
        """Get how quickly resilience recovers from stress."""
        current_resilience = self._get_current_resilience()
        return 1.0 + (current_resilience * 0.2)  # Higher resilience = faster recovery
    
    def _get_current_resilience(self) -> float:
        # This would interface with the identity system
        return 1.0  # Placeholder
```

### 4. Lingering Mood Model

```python
class MoodEngine:
    """Enhanced mood system with slow decay and belief influence."""
    
    def __init__(self, config: dict | None = None):
        self.mood_decay_rate = config.get('mood_decay_rate', 0.02)  # Very slow decay
        self.mood_inertia = config.get('mood_inertia', 0.95)  # High inertia
        self.belief_influence_weight = config.get('belief_influence_weight', 0.15)
        
        # Multi-dimensional mood
        self.mood_state = {
            'valence': 0.0,      # -1 to 1 (positive/negative)
            'arousal': 0.0,      # 0 to 1 (calm/excited)
            'dominance': 0.0,    # -1 to 1 (submissive/dominant)
            'certainty': 0.5,    # 0 to 1 (uncertain/certain)
        }
        
        self.mood_history = deque(maxlen=200)
        self.emotional_imprints = []  # Strong emotional events that leave lasting marks
        
    def update_mood(self, emotional_signals: list[dict], beliefs: list[dict]) -> dict:
        """Update mood with slow decay and belief influence."""
        
        # Calculate immediate emotional response
        immediate_response = self._calculate_immediate_response(emotional_signals)
        
        # Apply belief-based mood bias
        belief_bias = self._calculate_belief_mood_bias(beliefs)
        
        # Update mood with high inertia
        for dimension in self.mood_state:
            current = self.mood_state[dimension]
            
            # Combine immediate response, belief bias, and decay
            target = (
                immediate_response.get(dimension, 0.0) * 0.1 +
                belief_bias.get(dimension, 0.0) * self.belief_influence_weight +
                current * self.mood_inertia
            )
            
            # Very slow decay toward neutral
            if dimension == 'valence':
                target += -current * self.mood_decay_rate
            elif dimension == 'arousal':
                target += -current * (self.mood_decay_rate * 1.5)
            
            self.mood_state[dimension] = max(-1.0, min(1.0, target))
        
        # Check for emotional imprints
        self._update_emotional_imprints(emotional_signals)
        
        # Store mood history
        self.mood_history.append(dict(self.mood_state))
        
        return dict(self.mood_state)
    
    def _calculate_belief_mood_bias(self, beliefs: list[dict]) -> dict:
        """Calculate mood bias based on active beliefs."""
        bias = {'valence': 0.0, 'arousal': 0.0, 'dominance': 0.0, 'certainty': 0.0}
        
        for belief in beliefs:
            confidence = belief.get('confidence', 0.0)
            statement = belief.get('statement', '').lower()
            
            if 'criticism' in statement:
                bias['valence'] -= 0.2 * confidence
                bias['certainty'] -= 0.1 * confidence
            elif 'support' in statement:
                bias['valence'] += 0.3 * confidence
                bias['dominance'] += 0.1 * confidence
            elif 'unsafe' in statement:
                bias['arousal'] += 0.4 * confidence
                bias['certainty'] -= 0.2 * confidence
            elif 'persistent effort' in statement:
                bias['certainty'] += 0.2 * confidence
                bias['dominance'] += 0.15 * confidence
        
        return bias
    
    def get_mood_tone(self) -> str:
        """Get descriptive mood tone."""
        v, a, d, c = (self.mood_state['valence'], 
                      self.mood_state['arousal'],
                      self.mood_state['dominance'],
                      self.mood_state['certainty'])
        
        if v < -0.4 and a > 0.6:
            return "distressed"
        elif v < -0.3 and a < 0.3:
            return "depressed"
        elif v > 0.4 and a > 0.5:
            return "confident"
        elif v > 0.2 and a < 0.4:
            return "content"
        elif c < 0.3:
            return "uncertain"
        elif a > 0.7:
            return "tense"
        else:
            return "neutral"
```

### 5. Enhanced Narrative System

```python
class NarrativeRewriteEngine:
    """Dynamic narrative generation based on beliefs and mood."""
    
    def __init__(self, config: dict | None = None):
        self.novelty_threshold = config.get('novelty_threshold', 0.3)
        self.coherence_threshold = config.get('coherence_threshold', 0.4)
        self.belief_weight = config.get('belief_weight', 0.4)
        self.mood_weight = config.get('mood_weight', 0.3)
        self.identity_weight = config.get('identity_weight', 0.3)
        
    def generate_narrative(self, beliefs: list[dict], mood_state: dict, 
                          identity_snapshot: dict, stage: str) -> str:
        """Generate narrative from current cognitive state."""
        
        # Extract themes
        belief_themes = self._extract_belief_themes(beliefs)
        mood_theme = self._extract_mood_theme(mood_state)
        identity_theme = self._extract_identity_theme(identity_snapshot)
        
        # Calculate narrative coherence
        coherence = self._calculate_narrative_coherence(beliefs, mood_state, identity_snapshot)
        
        # Generate narrative structure
        narrative_structure = self._select_narrative_structure(stage, coherence)
        
        # Compose narrative
        narrative = self._compose_narrative(
            structure=narrative_structure,
            belief_themes=belief_themes,
            mood_theme=mood_theme,
            identity_theme=identity_theme,
            stage=stage
        )
        
        return narrative
    
    def should_rewrite_narrative(self, belief_shift: float, mood_shift: float, 
                                coherence_change: float) -> bool:
        """Determine if narrative should be rewritten."""
        return (
            belief_shift > self.novelty_threshold or
            mood_shift > 0.25 or
            coherence_change > self.coherence_threshold
        )
    
    def _extract_belief_themes(self, beliefs: list[dict]) -> list[str]:
        """Extract dominant themes from beliefs."""
        themes = []
        for belief in beliefs[:3]:  # Top 3 beliefs
            statement = belief['statement']
            confidence = belief['confidence']
            
            if confidence > 0.6:
                themes.append(statement.lower())
        
        return themes
    
    def _compose_narrative(self, structure: str, belief_themes: list[str], 
                          mood_theme: str, identity_theme: str, stage: str) -> str:
        """Compose narrative from components."""
        
        # Stage-appropriate opening
        openings = {
            'child': "I am learning that",
            'teen': "I'm discovering that",
            'adult': "I understand that"
        }
        
        narrative = openings.get(stage, "I experience that")
        
        # Add belief themes
        if belief_themes:
            if len(belief_themes) == 1:
                narrative += f" {belief_themes[0]}"
            else:
                narrative += f" {belief_themes[0]}, and also {belief_themes[1]}"
        
        # Add mood context
        if mood_theme != "neutral":
            mood_phrases = {
                "confident": "which makes me feel capable",
                "distressed": "which weighs on me",
                "uncertain": "which leaves me unsure",
                "content": "which brings me peace"
            }
            narrative += f", {mood_phrases.get(mood_theme, 'which affects me')}"
        
        # Add identity reflection
        if identity_theme:
            narrative += f". {identity_theme}"
        
        return narrative
```

### 6. Strategy Adaptation Engine

```python
class StrategyAdaptationEngine:
    """Adaptive strategy selection based on success/failure patterns."""
    
    def __init__(self, config: dict | None = None):
        self.failure_threshold = config.get('failure_threshold', 0.6)
        self.min_attempts = config.get('min_attempts', 5)
        self.exploration_bonus = config.get('exploration_bonus', 0.2)
        self.decay_rate = config.get('decay_rate', 0.98)
        
        self.action_performance = defaultdict(lambda: {
            'attempts': 0,
            'successes': 0,
            'failures': 0,
            'recent_success_rate': 0.0,
            'confidence': 0.5
        })
        
        self.strategy_history = deque(maxlen=100)
        
    def record_outcome(self, action: str, success: bool, intensity: float = 0.5):
        """Record action outcome for strategy adaptation."""
        perf = self.action_performance[action]
        perf['attempts'] += 1
        
        if success:
            perf['successes'] += 1
        else:
            perf['failures'] += 1
        
        # Update recent success rate (exponential moving average)
        new_rate = 1.0 if success else 0.0
        perf['recent_success_rate'] = (
            perf['recent_success_rate'] * 0.8 + new_rate * 0.2
        )
        
        # Update confidence
        if perf['attempts'] >= self.min_attempts:
            success_rate = perf['successes'] / perf['attempts']
            perf['confidence'] = success_rate
        
        self.strategy_history.append({
            'action': action,
            'success': success,
            'timestamp': time.time(),
            'intensity': intensity
        })
    
    def get_strategy_bias(self, beliefs: list[dict]) -> dict[str, float]:
        """Get strategy bias based on performance and beliefs."""
        bias = {}
        
        for action, perf in self.action_performance.items():
            if perf['attempts'] < self.min_attempts:
                continue
            
            success_rate = perf['successes'] / perf['attempts']
            
            # Base bias from performance
            if success_rate < self.failure_threshold and perf['failures'] >= 3:
                # Penalize failed strategies
                bias[action] = -(self.failure_threshold - success_rate) * 0.5
            else:
                # Reward successful strategies
                bias[action] = (success_rate - 0.5) * 0.3
            
            # Exploration bonus for novelty beliefs
            novelty_confidence = self._get_belief_confidence(
                "New experiences help me adapt.", beliefs
            )
            if novelty_confidence > 0.5 and action in ['challenge', 'suggest']:
                bias[action] += self.exploration_bonus * novelty_confidence
        
        # Decay biases over time
        for action in bias:
            bias[action] *= self.decay_rate
        
        return bias
    
    def _get_belief_confidence(self, statement: str, beliefs: list[dict]) -> float:
        """Get confidence for a specific belief statement."""
        for belief in beliefs:
            if belief['statement'] == statement:
                return belief['confidence']
        return 0.0
```

### 7. Enhanced Consciousness Calculator

```python
class ConsciousnessCalculator:
    """Consciousness score based on coherence, prediction, and integration."""
    
    def __init__(self, config: dict | None = None):
        self.coherence_weight = config.get('coherence_weight', 0.3)
        self.prediction_weight = config.get('prediction_weight', 0.25)
        self.integration_weight = config.get('integration_weight', 0.25)
        self.complexity_weight = config.get('complexity_weight', 0.2)
        
    def calculate_consciousness(self, beliefs: list[dict], prediction_accuracy: float,
                             mood_state: dict, narrative_complexity: float,
                             reflection_depth: float) -> dict:
        """Calculate consciousness factors and overall score."""
        
        # Belief coherence
        coherence = self._calculate_belief_coherence(beliefs)
        
        # Prediction accuracy (already provided)
        prediction_accuracy = max(0.0, min(1.0, prediction_accuracy))
        
        # Internal integration (mood-narrative consistency)
        integration = self._calculate_internal_integration(mood_state, narrative_complexity)
        
        # Cognitive complexity
        complexity = self._calculate_cognitive_complexity(
            len(beliefs), reflection_depth, narrative_complexity
        )
        
        # Overall consciousness score
        consciousness_score = (
            coherence * self.coherence_weight +
            prediction_accuracy * self.prediction_weight +
            integration * self.integration_weight +
            complexity * self.complexity_weight
        )
        
        return {
            'consciousness_score': max(0.0, min(1.0, consciousness_score)),
            'belief_coherence': coherence,
            'prediction_accuracy': prediction_accuracy,
            'internal_integration': integration,
            'cognitive_complexity': complexity,
            'factors': {
                'coherence_contribution': coherence * self.coherence_weight,
                'prediction_contribution': prediction_accuracy * self.prediction_weight,
                'integration_contribution': integration * self.integration_weight,
                'complexity_contribution': complexity * self.complexity_weight
            }
        }
    
    def _calculate_belief_coherence(self, beliefs: list[dict]) -> float:
        """Calculate how coherent beliefs are with each other."""
        if len(beliefs) < 2:
            return 0.5
        
        # Check for contradictions
        contradictions = 0
        total_pairs = 0
        
        belief_pairs = [
            ("Reaching out often leads to rejection.", "Supportive connections are available to me."),
            ("I often fail before I succeed.", "Persistent effort helps me solve challenges."),
            ("The environment often feels unsafe.", "New experiences help me adapt.")
        ]
        
        belief_dict = {b['statement']: b['confidence'] for b in beliefs}
        
        for stmt1, stmt2 in belief_pairs:
            conf1 = belief_dict.get(stmt1, 0.0)
            conf2 = belief_dict.get(stmt2, 0.0)
            
            if conf1 > 0.3 and conf2 > 0.3:
                contradictions += min(conf1, conf2)
            total_pairs += 1
        
        coherence_penalty = contradictions / max(1, total_pairs)
        return max(0.0, 1.0 - coherence_penalty)
    
    def _calculate_internal_integration(self, mood_state: dict, narrative_complexity: float) -> float:
        """Calculate integration between mood and narrative."""
        mood_valence = mood_state.get('valence', 0.0)
        mood_certainty = mood_state.get('certainty', 0.5)
        
        # Higher integration when mood is stable and narrative is complex
        stability = 1.0 - abs(mood_valence) * 0.3  # Less extreme moods = more stable
        return (stability * 0.6 + mood_certainty * 0.4) * narrative_complexity
```

## Integration Points

### 1. Brain Class Integration

```python
# In VirtualBrain.__init__
self.worldview = EnhancedBeliefEngine(worldview_config)
self.resilience_engine = DynamicResilienceEngine(config.get('resilience_config', {}))
self.mood_engine = MoodEngine(config.get('mood_config', {}))
self.narrative_engine = NarrativeRewriteEngine(config.get('narrative_config', {}))
self.strategy_adaptation = StrategyAdaptationEngine(config.get('strategy_config', {}))
self.consciousness_calc = ConsciousnessCalculator(config.get('consciousness_config', {}))
```

### 2. Tick Method Integration

```python
# In VirtualBrain.tick()
def tick(self):
    # ... existing code ...
    
    # Enhanced mood update
    mood_update = self.mood_engine.update_mood(
        emotional_signals=self._step_perception_signals,
        beliefs=self.worldview.get_active_beliefs()
    )
    
    # Dynamic resilience update
    resilience_change = self.resilience_engine.update_resilience(
        cortisol=self.chemicals['cortisol']['value'],
        emotional_dip_active=self._emotional_dip_active,
        recovery_counter=self.recovery_counter,
        chronic_stress_steps=self._chronic_stress_steps
    )
    self.identity.add_evidence('resilience', resilience_change)
    
    # Enhanced belief extraction
    belief_update = self._update_worldview()
    
    # Strategy adaptation
    if hasattr(self, 'last_action') and hasattr(self, 'last_action_success'):
        self.strategy_adaptation.record_outcome(
            action=self.last_action,
            success=self.last_action_success,
            intensity=getattr(self.current_focus, 'emotional_weight', 0.5)
        )
    
    # Enhanced consciousness calculation
    consciousness_factors = self.consciousness_calc.calculate_consciousness(
        beliefs=self.worldview.get_active_beliefs(),
        prediction_accuracy=self.worldview.prediction_hits / max(1, self.worldview.prediction_total),
        mood_state=mood_update,
        narrative_complexity=self._calculate_narrative_complexity(),
        reflection_depth=self.development.reflection_depth
    )
    
    self.consciousness.score = consciousness_factors['consciousness_score']
    
    # ... rest of tick method ...
```

### 3. Decision Bias Integration

```python
# Enhanced decision bias calculation
def get_enhanced_decision_bias(self) -> dict:
    belief_bias = self.worldview.decision_bias()
    strategy_bias = self.strategy_adaptation.get_strategy_bias(
        self.worldview.get_active_beliefs()
    )
    mood_bias = self._calculate_mood_bias()
    
    # Combine biases
    combined_bias = {}
    all_actions = set(belief_bias.keys()) | set(strategy_bias.keys())
    
    for action in all_actions:
        combined_bias[action] = (
            belief_bias.get(action, 0.0) * 0.4 +
            strategy_bias.get(action, 0.0) * 0.4 +
            mood_bias.get(action, 0.0) * 0.2
        )
    
    return combined_bias
```

## Minimal Refactoring Strategy

### Phase 1: Core Enhancement
1. Extend existing `BeliefEngine` with pattern detectors
2. Add `DynamicResilienceEngine` alongside current resilience system
3. Enhance mood system in place

### Phase 2: Integration
1. Update `VirtualBrain.tick()` to use new components
2. Modify decision bias calculation
3. Update consciousness calculation

### Phase 3: Cleanup
1. Remove old resilience caps
2. Consolidate duplicate code
3. Add configuration options

This design maintains modularity while addressing all architectural problems identified.

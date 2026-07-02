# Implementation Blueprint

## Step-by-Step Implementation Plan

### Phase 1: Foundation Enhancement (Week 1-2)

#### 1.1 Enhanced Belief Engine
```python
# File: cognition/enhanced_belief_engine.py
class EnhancedBeliefEngine(BeliefEngine):
    """Extend existing BeliefEngine with pattern detection."""
    
    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.pattern_detectors = self._init_pattern_detectors()
        self.belief_network = BeliefNetwork()
        
    def _init_pattern_detectors(self):
        return {
            'criticism': CriticismPatternDetector(),
            'success_failure': SuccessFailurePatternDetector(),
            'social_rejection': SocialRejectionPatternDetector(),
            'threat': ThreatPatternDetector(),
            'novelty_adaptation': NoveltyAdaptationPatternDetector(),
        }
    
    def extract_beliefs(self, events: list[dict], step_counter: int, 
                       reflection_depth: float = 0.0) -> dict:
        """Enhanced belief extraction with pattern detection."""
        
        # Call parent method for basic belief extraction
        base_result = super().extract_beliefs(events, step_counter, reflection_depth)
        
        # Add pattern-based belief extraction
        pattern_beliefs = self._extract_pattern_beliefs(events)
        
        # Integrate pattern beliefs
        for belief in pattern_beliefs:
            self._integrate_pattern_belief(belief)
        
        return {
            **base_result,
            'pattern_beliefs': len(pattern_beliefs),
            'total_beliefs': len(self.beliefs)
        }
```

#### 1.2 Pattern Detectors
```python
# File: cognition/pattern_detectors.py
class CriticismPatternDetector:
    def detect_pattern(self, events: list[dict]) -> dict:
        criticism_events = [e for e in events if self._is_criticism(e)]
        
        if len(criticism_events) < 3:
            return {'detected': False}
        
        # Calculate temporal density
        timestamps = [e.get('timestamp', 0) for e in criticism_events]
        timestamps.sort()
        
        if len(timestamps) > 1:
            time_spans = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            avg_span = sum(time_spans) / len(time_spans)
            temporal_density = 1.0 / (1.0 + avg_span / 1000.0)  # Normalize
        else:
            temporal_density = 0.5
        
        # Context analysis
        context_patterns = self._analyze_context_patterns(criticism_events, events)
        
        pattern_strength = (len(criticism_events) / len(events)) * temporal_density
        
        return {
            'detected': pattern_strength > 0.15,
            'strength': pattern_strength,
            'evidence_count': len(criticism_events),
            'temporal_density': temporal_density,
            'context_patterns': context_patterns,
            'belief_statement': "Criticism often follows my attempts."
        }
    
    def _is_criticism(self, event: dict) -> bool:
        text = str(event.get('description', '') + ' ' + 
                  event.get('metadata', {}).get('content', '')).lower()
        return any(keyword in text for keyword in [
            'criticism', 'criticized', 'mistake', 'error', 'wrong', 'failure'
        ])
```

#### 1.3 Dynamic Resilience Engine
```python
# File: core/dynamic_resilience.py
class DynamicResilienceEngine:
    def __init__(self, config: dict | None = None):
        self.base_recovery_rate = config.get('base_recovery_rate', 0.02)
        self.chronic_stress_threshold = config.get('chronic_stress_threshold', 58.0)
        self.resilience_decay_rate = config.get('resilience_decay_rate', 0.001)
        self.recovery_bonus_rate = config.get('recovery_bonus_rate', 0.005)
        
        self.resilience_velocity = 0.0
        self.stress_exposure_history = deque(maxlen=100)
        self.recovery_events = deque(maxlen=50)
        
    def update_resilience(self, cortisol: float, emotional_dip_active: bool, 
                          recovery_counter: int, chronic_stress_steps: int) -> float:
        """Update resilience - returns change to apply."""
        
        self.stress_exposure_history.append(cortisol)
        
        # Calculate stress load
        if len(self.stress_exposure_history) > 0:
            recent_avg = sum(self.stress_exposure_history) / len(self.stress_exposure_history)
            stress_load = max(0, (recent_avg - self.chronic_stress_threshold) / 20.0)
        else:
            stress_load = 0
        
        # Damage from chronic stress
        if chronic_stress_steps > 10:
            damage = self.resilience_decay_rate * (1 + stress_load * 2)
            self.resilience_velocity -= damage
        
        # Growth from recovery
        if emotional_dip_active and recovery_counter > 3:
            recovery_bonus = self.recovery_bonus_rate * (1 + recovery_counter * 0.1)
            self.resilience_velocity += recovery_bonus
            self.recovery_events.append(time.time())
        
        # Soft asymptotic limit (no hard cap)
        current_resilience = self._get_current_resilience()
        if current_resilience > 3.0:  # Soft limit at 3.0
            self.resilience_velocity -= (current_resilience - 3.0) * 0.01
        
        # Apply damping
        self.resilience_velocity *= 0.95
        
        return self.resilience_velocity
    
    def get_recovery_speed_multiplier(self) -> float:
        """Higher resilience = faster recovery."""
        current = self._get_current_resilience()
        return 1.0 + (current * 0.2)
    
    def _get_current_resilience(self) -> float:
        """Interface with identity system."""
        # This will be connected to the identity system
        return 1.0  # Placeholder
```

### Phase 2: Integration (Week 3-4)

#### 2.1 Enhanced Mood Engine
```python
# File: cognition/mood_engine.py
class MoodEngine:
    def __init__(self, config: dict | None = None):
        self.mood_decay_rate = config.get('mood_decay_rate', 0.02)
        self.mood_inertia = config.get('mood_inertia', 0.95)
        self.belief_influence_weight = config.get('belief_influence_weight', 0.15)
        
        self.mood_state = {
            'valence': 0.0,      # -1 to 1
            'arousal': 0.0,      # 0 to 1
            'dominance': 0.0,    # -1 to 1
            'certainty': 0.5,    # 0 to 1
        }
        
        self.mood_history = deque(maxlen=200)
        self.emotional_imprints = []
    
    def update_mood(self, emotional_signals: list[dict], beliefs: list[dict]) -> dict:
        """Update mood with slow decay and belief influence."""
        
        # Calculate immediate response
        immediate = self._calculate_immediate_response(emotional_signals)
        
        # Calculate belief bias
        belief_bias = self._calculate_belief_mood_bias(beliefs)
        
        # Update each dimension
        for dimension in self.mood_state:
            current = self.mood_state[dimension]
            
            # Weighted combination
            target = (
                immediate.get(dimension, 0.0) * 0.1 +
                belief_bias.get(dimension, 0.0) * self.belief_influence_weight +
                current * self.mood_inertia
            )
            
            # Slow decay
            if dimension == 'valence':
                target += -current * self.mood_decay_rate
            elif dimension == 'arousal':
                target += -current * (self.mood_decay_rate * 1.5)
            
            self.mood_state[dimension] = max(-1.0, min(1.0, target))
        
        self.mood_history.append(dict(self.mood_state))
        return dict(self.mood_state)
```

#### 2.2 Strategy Adaptation
```python
# File: decision/strategy_adaptation.py
class StrategyAdaptationEngine:
    def __init__(self, config: dict | None = None):
        self.failure_threshold = config.get('failure_threshold', 0.6)
        self.min_attempts = config.get('min_attempts', 5)
        self.exploration_bonus = config.get('exploration_bonus', 0.2)
        self.decay_rate = config.get('decay_rate', 0.98)
        
        self.action_performance = defaultdict(lambda: {
            'attempts': 0, 'successes': 0, 'failures': 0,
            'recent_success_rate': 0.0, 'confidence': 0.5
        })
        
        self.strategy_history = deque(maxlen=100)
    
    def record_outcome(self, action: str, success: bool, intensity: float = 0.5):
        perf = self.action_performance[action]
        perf['attempts'] += 1
        
        if success:
            perf['successes'] += 1
            new_rate = 1.0
        else:
            perf['failures'] += 1
            new_rate = 0.0
        
        # Update recent success rate
        perf['recent_success_rate'] = (
            perf['recent_success_rate'] * 0.8 + new_rate * 0.2
        )
        
        # Update confidence
        if perf['attempts'] >= self.min_attempts:
            success_rate = perf['successes'] / perf['attempts']
            perf['confidence'] = success_rate
    
    def get_strategy_bias(self, beliefs: list[dict]) -> dict[str, float]:
        bias = {}
        
        for action, perf in self.action_performance.items():
            if perf['attempts'] < self.min_attempts:
                continue
            
            success_rate = perf['successes'] / perf['attempts']
            
            # Base bias from performance
            if success_rate < self.failure_threshold and perf['failures'] >= 3:
                bias[action] = -(self.failure_threshold - success_rate) * 0.5
            else:
                bias[action] = (success_rate - 0.5) * 0.3
            
            # Exploration bonus
            novelty_confidence = self._get_belief_confidence(
                "New experiences help me adapt.", beliefs
            )
            if novelty_confidence > 0.5 and action in ['challenge', 'suggest']:
                bias[action] += self.exploration_bonus * novelty_confidence
        
        # Apply decay
        for action in bias:
            bias[action] *= self.decay_rate
        
        return bias
```

#### 2.3 Enhanced Consciousness Calculator
```python
# File: core/enhanced_consciousness.py
class EnhancedConsciousnessCalculator:
    def __init__(self, config: dict | None = None):
        self.coherence_weight = config.get('coherence_weight', 0.3)
        self.prediction_weight = config.get('prediction_weight', 0.25)
        self.integration_weight = config.get('integration_weight', 0.25)
        self.complexity_weight = config.get('complexity_weight', 0.2)
    
    def calculate_consciousness(self, beliefs: list[dict], prediction_accuracy: float,
                             mood_state: dict, narrative_complexity: float,
                             reflection_depth: float) -> dict:
        
        coherence = self._calculate_belief_coherence(beliefs)
        prediction_accuracy = max(0.0, min(1.0, prediction_accuracy))
        integration = self._calculate_internal_integration(mood_state, narrative_complexity)
        complexity = self._calculate_cognitive_complexity(
            len(beliefs), reflection_depth, narrative_complexity
        )
        
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
            'cognitive_complexity': complexity
        }
    
    def _calculate_belief_coherence(self, beliefs: list[dict]) -> float:
        if len(beliefs) < 2:
            return 0.5
        
        contradictions = 0
        belief_dict = {b['statement']: b['confidence'] for b in beliefs}
        
        # Check contradictory pairs
        contradictory_pairs = [
            ("Reaching out often leads to rejection.", "Supportive connections are available to me."),
            ("I often fail before I succeed.", "Persistent effort helps me solve challenges."),
        ]
        
        for stmt1, stmt2 in contradictory_pairs:
            conf1 = belief_dict.get(stmt1, 0.0)
            conf2 = belief_dict.get(stmt2, 0.0)
            
            if conf1 > 0.3 and conf2 > 0.3:
                contradictions += min(conf1, conf2)
        
        coherence_penalty = contradictions / len(contradictory_pairs)
        return max(0.0, 1.0 - coherence_penalty)
```

### Phase 3: Brain Integration (Week 5-6)

#### 3.1 Updated VirtualBrain Class
```python
# In core/brain.py - modify __init__ method
def __init__(self, chemical_configs: dict, interaction_matrix: dict = None, 
             decision_engine=None, feedback_multiplier: float = 1.0,
             deterministic: bool = False, memory_storage_path: str | None = None,
             worldview_config: dict | None = None):
    
    # ... existing initialization ...
    
    # Enhanced systems
    self.worldview = EnhancedBeliefEngine(worldview_config)
    self.resilience_engine = DynamicResilienceEngine(
        config=worldview_config.get('resilience_config', {})
    )
    self.mood_engine = MoodEngine(
        config=worldview_config.get('mood_config', {})
    )
    self.strategy_adaptation = StrategyAdaptationEngine(
        config=worldview_config.get('strategy_config', {})
    )
    self.consciousness_calc = EnhancedConsciousnessCalculator(
        config=worldview_config.get('consciousness_config', {})
    )
```

#### 3.2 Updated Tick Method
```python
# In core/brain.py - modify tick method
def tick(self):
    # ... existing code until mood update ...
    
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
    
    # Remove old resilience cap enforcement
    # OLD: self.identity.set('resilience', min(1.0, self.identity.get('resilience')))
    
    # Enhanced belief extraction
    belief_update = self._update_worldview()
    
    # Strategy adaptation
    if hasattr(self, '_last_action') and hasattr(self, '_last_action_success'):
        self.strategy_adaptation.record_outcome(
            action=self._last_action,
            success=self._last_action_success,
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
    
    # ... continue with existing tick logic ...
```

#### 3.3 Enhanced Decision Bias
```python
# In core/brain.py - add new method
def get_enhanced_decision_bias(self) -> dict[str, float]:
    """Combine multiple bias sources for decision making."""
    
    belief_bias = self.worldview.decision_bias()
    strategy_bias = self.strategy_adaptation.get_strategy_bias(
        self.worldview.get_active_beliefs()
    )
    mood_bias = self._calculate_mood_bias()
    
    # Combine biases with weights
    combined_bias = {}
    all_actions = set(belief_bias.keys()) | set(strategy_bias.keys()) | set(mood_bias.keys())
    
    for action in all_actions:
        combined_bias[action] = (
            belief_bias.get(action, 0.0) * 0.4 +
            strategy_bias.get(action, 0.0) * 0.4 +
            mood_bias.get(action, 0.0) * 0.2
        )
    
    return combined_bias

def _calculate_mood_bias(self) -> dict[str, float]:
    """Calculate mood-based decision bias."""
    mood = self.mood_engine.mood_state
    bias = {}
    
    valence = mood.get('valence', 0.0)
    arousal = mood.get('arousal', 0.0)
    
    if valence < -0.2:
        bias['refuse'] = abs(valence) * 0.3
        bias['neutral'] = abs(valence) * 0.2
    elif valence > 0.2:
        bias['support'] = valence * 0.3
        bias['suggest'] = valence * 0.2
    
    if arousal > 0.7:
        bias['challenge'] = arousal * 0.15
    
    return bias
```

### Phase 4: Testing & Validation (Week 7-8)

#### 4.1 Test Cases
```python
# File: tests/test_enhanced_belief_system.py
class TestEnhancedBeliefSystem:
    def test_pattern_detection(self):
        """Test pattern detection in belief extraction."""
        events = [
            {'description': 'I was criticized for my mistake', 'metadata': {'category': 'criticism'}},
            {'description': 'I made another error', 'metadata': {'category': 'failure'}},
            # ... more test events
        ]
        
        engine = EnhancedBeliefEngine()
        result = engine.extract_beliefs(events, step_counter=100)
        
        assert result['pattern_beliefs'] > 0
        assert len(engine.beliefs) > 0
    
    def test_dynamic_resilience(self):
        """Test resilience without hard caps."""
        engine = DynamicResilienceEngine()
        
        # Simulate chronic stress
        for i in range(20):
            change = engine.update_resilience(
                cortisol=65.0,  # High stress
                emotional_dip_active=False,
                recovery_counter=0,
                chronic_stress_steps=i+1
            )
            # Resilience should decrease
            assert change < 0
        
        # Simulate recovery
        for i in range(10):
            change = engine.update_resilience(
                cortisol=45.0,  # Low stress
                emotional_dip_active=True,
                recovery_counter=i+1,
                chronic_stress_steps=0
            )
            # Resilience should increase
            assert change > 0
    
    def test_mood_persistence(self):
        """Test mood persistence over time."""
        engine = MoodEngine()
        
        # Apply strong emotional stimulus
        signals = [{'valence': 0.8, 'intensity': 0.9}]
        engine.update_mood(signals, [])
        
        initial_valence = engine.mood_state['valence']
        
        # Apply decay over multiple steps
        for i in range(50):
            engine.update_mood([], [])
        
        # Mood should still be elevated (slow decay)
        assert engine.mood_state['valence'] > initial_valence * 0.5
```

#### 4.2 Integration Tests
```python
# File: tests/test_brain_integration.py
class TestBrainIntegration:
    def test_enhanced_brain_tick(self):
        """Test enhanced brain functionality."""
        brain = VirtualBrain(chemical_configs, worldview_config={
            'resilience_config': {'base_recovery_rate': 0.03},
            'mood_config': {'mood_decay_rate': 0.01}
        })
        
        # Apply repeated stress
        for i in range(30):
            brain.perceive({
                'category': 'criticism',
                'content': 'You made a mistake',
                'valence': -0.7,
                'intensity': 0.8
            })
            brain.tick()
        
        # Check belief formation
        beliefs = brain.worldview.get_active_beliefs()
        assert any('criticism' in b['statement'].lower() for b in beliefs)
        
        # Check resilience impact
        resilience = brain.identity.get('resilience')
        assert resilience < 1.0  # Should be reduced by chronic stress
        
        # Check mood impact
        mood_valence = brain.mood_engine.mood_state['valence']
        assert mood_valence < -0.2  # Should be negative
```

## Configuration Structure

```yaml
# config/enhanced_worldview.yaml
belief_engine:
  extraction_interval: 12
  event_window: 80
  min_evidence: 3
  confidence_smoothing: 0.25
  narrative_shift_threshold: 0.12

resilience_engine:
  base_recovery_rate: 0.02
  chronic_stress_threshold: 58.0
  resilience_decay_rate: 0.001
  recovery_bonus_rate: 0.005

mood_engine:
  mood_decay_rate: 0.02
  mood_inertia: 0.95
  belief_influence_weight: 0.15

strategy_adaptation:
  failure_threshold: 0.6
  min_attempts: 5
  exploration_bonus: 0.2
  decay_rate: 0.98

consciousness_calculator:
  coherence_weight: 0.3
  prediction_weight: 0.25
  integration_weight: 0.25
  complexity_weight: 0.2
```

## Migration Strategy

### Step 1: Backup Current System
```bash
cp cognition/belief_engine.py cognition/belief_engine.py.backup
cp core/brain.py core/brain.py.backup
```

### Step 2: Install New Components
1. Add new files to appropriate directories
2. Update imports in existing files
3. Add configuration options

### Step 3: Gradual Integration
1. Start with enhanced belief engine (can run alongside existing)
2. Add dynamic resilience (remove old caps)
3. Integrate mood engine
4. Add strategy adaptation
5. Update consciousness calculation

### Step 4: Testing & Validation
1. Run unit tests for each component
2. Run integration tests
3. Compare behavior before/after
4. Tune parameters based on results

### Step 5: Cleanup
1. Remove old resilience caps
2. Remove duplicate code
3. Update documentation
4. Optimize performance

This implementation plan addresses all the architectural problems while maintaining system stability and modularity.

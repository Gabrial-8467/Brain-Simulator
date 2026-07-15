import math
import random
from typing import Any
from core.attention import Thought

class SleepManager:
    def __init__(self, cycle_period: int = 100):
        self.process_s = 0.0  # Homeostatic sleep pressure (fatigue)
        self.cycle_period = cycle_period

    def update_sleep_drives(self, brain: Any) -> None:
        # Sync from brain.fatigue if it was modified externally
        if abs(self.process_s - brain.fatigue) > 0.0001:
            self.process_s = brain.fatigue

        if brain.sleeping:
            self.process_s = max(0.0, self.process_s - 0.20)
        else:
            self.process_s = min(1.0, self.process_s + 0.02)
        
        # Process C: Circadian drive (sine wave of time of day)
        # We model the day/night cycle as cycle_period ticks.
        # Circadian alertness peaks at day and troughs at night.
        # So sleepiness drive Process C peaks at night: negative cos wave.
        process_c = 0.3 * (-math.cos(2 * math.pi * brain.step_counter / self.cycle_period))
        
        # Sync Process S (fatigue) back to brain for backward compatibility
        brain.fatigue = self.process_s
        
        # Melatonin accumulates with fatigue and circadian night
        if "melatonin" in brain.chemicals:
            melatonin_c = max(0.0, -process_c * 150.0) # higher at night
            brain.chemicals["melatonin"]["value"] = min(100.0, brain.chemicals["melatonin"]["value"] + self.process_s * 2.0 + melatonin_c * 0.1)

    def should_sleep(self, brain: Any) -> bool:
        process_c = 0.3 * (-math.cos(2 * math.pi * brain.step_counter / self.cycle_period))
        sleep_drive = self.process_s - process_c
        
        has_melatonin_trigger = "melatonin" in brain.chemicals and brain.chemicals["melatonin"]["value"] > 80.0
        return sleep_drive > 0.85 or has_melatonin_trigger

    def run_sleep_cycle(self, brain: Any) -> dict[str, Any]:
        brain.sleep_ticks_left -= 1
        
        # Decay homeostatic sleep pressure
        self.process_s = max(0.0, self.process_s - 0.25)
        brain.fatigue = self.process_s
        
        # Neurochemical recovery during sleep
        if "cortisol" in brain.chemicals:
            brain.chemicals["cortisol"]["value"] = max(
                brain._original_baselines["cortisol"],
                brain.chemicals["cortisol"]["value"] - 8.0
            )
        if "serotonin" in brain.chemicals:
            brain.chemicals["serotonin"]["value"] = min(
                brain.chemicals["serotonin"]["max"],
                brain.chemicals["serotonin"]["value"] + 5.0
            )
        if "norepinephrine" in brain.chemicals:
            brain.chemicals["norepinephrine"]["value"] = max(
                brain._original_baselines["norepinephrine"],
                brain.chemicals["norepinephrine"]["value"] - 10.0
            )
        if "melatonin" in brain.chemicals:
            brain.chemicals["melatonin"]["value"] = max(
                brain._original_baselines["melatonin"],
                brain.chemicals["melatonin"]["value"] - 25.0
            )
        brain._clamp()

        # Offline Consolidation Phase (SWS)
        if brain.sleep_ticks_left >= 2:
            if hasattr(brain, "autobiography") and brain.autobiography.events:
                candidates = [ev for ev in brain.autobiography.events if ev.get("description") != "cycle_step"]
                if candidates:
                    significant = candidates[-15:]
                    for ev in significant:
                        meta = ev.get("metadata", {}) or {}
                        action = meta.get("action") or "neutral"
                        regret = float(meta.get("regret", 0.0))
                        reward = 1.0 - (regret * 2.0)
                        mood_tone = "neutral"
                        if brain.decision_engine and hasattr(brain.decision_engine, "update_q_value"):
                            brain.decision_engine.update_q_value(mood_tone, action, reward)
            # Synaptic Pruning: Q-table decay
            if brain.decision_engine and hasattr(brain.decision_engine, "q_table"):
                for tone in brain.decision_engine.q_table:
                    for act in brain.decision_engine.q_table[tone]:
                        brain.decision_engine.q_table[tone][act] *= 0.98
        
        # REM Dream Consolidation Phase
        else:
            brain.worldview.update_beliefs(brain)
            dream_text = "I am dreaming of floating through memory pathways..."
            if hasattr(brain, "autobiography") and brain.autobiography.events:
                candidates = [ev for ev in brain.autobiography.events if ev.get("description") != "cycle_step"]
                if candidates:
                    ev = random.choice(candidates)
                    dream_text = f"Dreaming of: {ev.get('description', 'memories')}"
            
            dream_thought = Thought(
                content=dream_text,
                source="dream",
                emotional_weight=0.5,
                novelty=0.7,
                relevance_to_goals=0.3
            )
            brain.global_workspace.post(dream_thought)

        if brain.sleep_ticks_left <= 0:
            brain.sleeping = False

        brain.step_counter += 1
        return {"action": "sleep", "probabilities": {"neutral": 1.0}, "feedback": {}, "asleep": True}

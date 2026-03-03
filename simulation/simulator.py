import time

from simulation.environment import SyntheticEnvironment


class Simulator:
    def __init__(self, brain, tick_delay=0.1, environment=None, memory_manager=None):
        self.brain = brain
        self.tick_delay = tick_delay
        self.running = False
        self.memory_manager = memory_manager
        self.environment = environment or SyntheticEnvironment(
            deterministic=getattr(brain, "deterministic", False)
        )

    def run_scenario(self, scenario_events, steps=50):

        print("\n--- Simulation Start ---\n")

        try:
            for step in range(steps):
                # Feed one lived experience into perception each cycle.
                env_event = self.environment.generate_event()
                self.brain.perceive(env_event)
                # Feed sensory perception events into the same pipeline.
                vision_event = self.environment.generate_vision_event()
                self.brain.perceive(vision_event)
                hearing_event = self.environment.generate_hearing_event()
                self.brain.perceive(hearing_event)

                # Inject event if available
                if step < len(scenario_events):
                    event = scenario_events[step]
                    self.brain.inject_event(
                        effects=event.get("effects", {}),
                        event_type=event.get("event_type"),
                        source=event.get("source"),
                        tags=event.get("tags")
                    )

                decision = self.brain.tick()
                state = self.brain.get_state()

                print(f"Step {step}")
                print(
                    "State:",
                    {
                        "dopamine": round(state.get("dopamine", 0.0), 3),
                        "cortisol": round(state.get("cortisol", 0.0), 3),
                        "oxytocin": round(state.get("oxytocin", 0.0), 3),
                        "serotonin": round(state.get("serotonin", 0.0), 3),
                        "stage": state.get("development_stage"),
                        "consciousness_score": round(state.get("consciousness_score", 0.0), 3),
                    },
                )

                if decision:
                    print("Decision:", decision)

                print("-" * 40)

                if self.memory_manager and (step + 1) % 100 == 0:
                    self.memory_manager.save(self.brain.get_state())

                time.sleep(self.tick_delay)
        finally:
            if self.memory_manager:
                self.memory_manager.save(self.brain.get_state())

        print("\n--- Simulation End ---\n")

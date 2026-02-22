import time


class Simulator:
    def __init__(self, brain, tick_delay=0.1):
        self.brain = brain
        self.tick_delay = tick_delay
        self.running = False

    def run_scenario(self, scenario_events, steps=50):

        print("\n--- Simulation Start ---\n")

        for step in range(steps):

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

            print(f"Step {step}")
            print("State:", self.brain.get_state())

            if decision:
                print("Decision:", decision)

            print("-" * 40)

            time.sleep(self.tick_delay)

        print("\n--- Simulation End ---\n")

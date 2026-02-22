def build_structured_learning_scenario(total_steps=200):

    scenario_events = []

    for step in range(total_steps):

        event = {}

        # Every 10 steps → Praise
        if step % 10 == 0:
            event = {
                "effects": {
                    "dopamine": 8,
                    "oxytocin": 5,
                    "serotonin": 3
                },
                "event_type": "praise",
                "source": "caregiver",
                "tags": ["social", "positive"]
            }

        # Every 25 steps → Criticism
        if step % 25 == 0 and step != 0:
            event = {
                "effects": {
                    "cortisol": 10,
                    "dopamine": -4,
                    "serotonin": -2
                },
                "event_type": "criticism",
                "source": "caregiver",
                "tags": ["social", "negative"]
            }

        scenario_events.append(event)

    return scenario_events

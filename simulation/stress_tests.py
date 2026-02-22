def extreme_reward_test():
    return [
        {
            "event_type": "extreme_reward",
            "source": "system",
            "effects": {"dopamine": 10},
            "tags": ["overstim"]
        }
        for _ in range(10)
    ]


def extreme_stress_test():
    return [
        {
            "event_type": "extreme_threat",
            "source": "system",
            "effects": {"cortisol": 10},
            "tags": ["threat"]
        }
        for _ in range(10)
    ]


def oscillation_test():
    events = []

    for i in range(20):
        if i % 2 == 0:
            events.append({
                "event_type": "reward",
                "source": "system",
                "effects": {"dopamine": 5},
                "tags": ["reward"]
            })
        else:
            events.append({
                "event_type": "stress",
                "source": "system",
                "effects": {"cortisol": 5},
                "tags": ["stress"]
            })

    return events

import random

from .attention import GlobalWorkspace, Thought

CURIOSITY_TEMPLATES = [
    "I wonder what would happen if I {verb} the {object}.",
    "What does the recent {event} mean for me?",
    "I should recall a similar past experience.",
    "How does my current state influence my next action?",
]

VERBS = ["examine", "modify", "re-evaluate", "simulate"]
OBJECTS = ["environment", "memory trace", "chemical balance"]
EVENTS = ["praise", "failure", "unexpected perception"]


def generate_spontaneous(brain) -> None:
    dopamine = brain.chemicals.get("dopamine", {}).get("value", 0) / 100.0
    if random.random() > (0.5 + 0.3 * dopamine):
        return

    template = random.choice(CURIOSITY_TEMPLATES)
    thought_text = template.format(
        verb=random.choice(VERBS),
        object=random.choice(OBJECTS),
        event=random.choice(EVENTS),
    )

    th = Thought(
        content=thought_text,
        source="internal",
        emotional_weight=0.1,
        novelty=0.9,
        relevance_to_goals=0.2,
    )
    GlobalWorkspace.post(th)

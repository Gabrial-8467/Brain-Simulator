import random
import math

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


def _get_state_vector(chemicals_dict: dict, identity_dict: dict) -> list[float]:
    # Extract keys and normalize: chemicals / 100.0, identity in [0, 1]
    chems = ["dopamine", "cortisol", "oxytocin", "serotonin", "norepinephrine"]
    traits = ["competence", "social_value", "resilience", "intelligence"]
    
    vec = []
    for c in chems:
        val = chemicals_dict.get(c, 50.0)
        if isinstance(val, dict):
            val = val.get("value", 50.0)
        vec.append(float(val) / 100.0)
        
    for t in traits:
        val = identity_dict.get(t, 0.5)
        vec.append(float(val))
    return vec


def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def generate_spontaneous(brain) -> None:
    # 1. Gating check: Suppress spontaneous mind-wandering in Task Positive Network (TPN) mode
    if getattr(brain, "network_mode", None) == "TPN":
        return

    dopamine = brain.chemicals.get("dopamine", {}).get("value", 0) / 100.0
    # Higher dopamine increases spontaneous mind-wandering probability
    if random.random() > (0.4 + 0.4 * dopamine):
        return

    # Build current state vector
    curr_chems = {k: v["value"] for k, v in brain.chemicals.items()}
    curr_id = brain.identity.get_snapshot() if hasattr(brain, "identity") else {}
    curr_vec = _get_state_vector(curr_chems, curr_id)

    best_similarity = 0.0
    best_event = None

    # Scan autobiographical memory using Hopfield Network Attractor dynamics
    if hasattr(brain, "autobiography") and brain.autobiography.events:
        candidates = [
            ev for ev in brain.autobiography.events
            if ev.get("description") != "cycle_step" and "cycle_step" not in str(ev.get("description", ""))
        ]
        if candidates:
            # Convert current state to binary query pattern
            x = [1 if v >= 0.5 else -1 for v in curr_vec]
            w = getattr(brain, "hopfield_weights", [[0.0]*9 for _ in range(9)])

            # Converge query pattern onto Hopfield attractor state (up to 5 iterations)
            for _ in range(5):
                new_x = []
                for i in range(9):
                    val = sum(w[i][j] * x[j] for j in range(9))
                    new_x.append(1 if val >= 0.0 else -1)
                x = new_x

            # Search autobiography for the event closest to the converged attractor
            best_matches = []
            best_match_count = -1

            for ev in candidates[-60:]:
                ev_chems = ev.get("chemicals", {})
                ev_id = ev.get("identity", {})
                ev_vec = _get_state_vector(ev_chems, ev_id)
                ev_pattern = [1 if v >= 0.5 else -1 for v in ev_vec]

                # Calculate matching dimensions
                matches = sum(1 for a, b in zip(x, ev_pattern) if a == b)
                if matches > best_match_count:
                    best_match_count = matches
                    best_matches = [ev]
                elif matches == best_match_count:
                    best_matches.append(ev)

            # If matches represent high overlap (at least 7/9 dimensions aligned)
            if best_match_count >= 7:
                best_event = best_matches[-1]
                best_similarity = float(best_match_count) / 9.0

    # Replay memory if similarity exceeds cognitive threshold
    if best_event and best_similarity >= 0.77:
        desc = best_event.get("description", "a past experience")
        # Strip prefixes for natural cognitive thought content
        clean_desc = desc.replace("perceived_", "").replace("worldview_", "")
        thought_text = f"I am recalling when I experienced: {clean_desc}"
        
        # Recalled thought inherits original event parameters scaled by similarity
        orig_intensity = float((best_event.get("metadata", {}) or {}).get("intensity", 0.5))
        emo_weight = min(1.0, orig_intensity * best_similarity)
        
        th = Thought(
            content=thought_text,
            source="memory",
            emotional_weight=emo_weight,
            novelty=0.3,
            relevance_to_goals=0.4,
            metadata={
                "associative_replay": True,
                "similarity_score": round(best_similarity, 4),
                "original_event": best_event,
            }
        )
    else:
        # Fallback to standard curiosity template
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

    (getattr(brain, "global_workspace", None) or GlobalWorkspace).post(th)

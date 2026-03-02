from collections import deque
import time

from core.attention import GlobalWorkspace, Thought


class AutobiographicalMemory:
    def __init__(self, max_events=500):
        self.events = deque(maxlen=max_events)

    def record_event(self, description, chemicals, identity_snapshot, metadata=None):
        event = {
            "timestamp": time.time(),
            "description": description,
            "chemicals": chemicals.copy(),
            "identity": identity_snapshot.copy(),
            "metadata": metadata or {},
        }
        self.events.append(event)

    def get_recent_events(self, n=50):
        return list(self.events)[-n:]

    def propose_memory_thought(self, brain) -> None:
        if not self.events:
            return

        ev = self.events[-1]
        emo = 0.0
        for chem in ("dopamine", "oxytocin", "cortisol"):
            val = ev["chemicals"].get(chem, 0)
            if isinstance(val, dict):
                val = val.get("value", 0)
            if chem == "cortisol":
                emo += (100 - val) / 100.0
            else:
                emo += val / 100.0
        emo = min(1.0, emo / 3.0)

        th = Thought(
            content=f"Recall: {ev['description']}",
            source="memory",
            emotional_weight=emo,
            novelty=0.4,
            relevance_to_goals=0.3,
        )
        GlobalWorkspace.post(th)

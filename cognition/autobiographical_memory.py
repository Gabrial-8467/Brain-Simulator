from collections import deque
import time

from core.attention import GlobalWorkspace, Thought


class AutobiographicalMemory:
    SYSTEM_EVENT_KEYS = {"cycle_step", "internal_process", "tick", "update"}

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

    @classmethod
    def _is_system_event(cls, description: str) -> bool:
        text = str(description or "").lower()
        return any(key in text for key in cls.SYSTEM_EVENT_KEYS)

    def _select_recall_event(self):
        if not self.events:
            return None
        latest = self.events[-1]
        if not self._is_system_event(latest.get("description", "")):
            return latest
        for ev in reversed(self.events):
            if not self._is_system_event(ev.get("description", "")):
                return ev
        return latest

    def propose_memory_thought(self, brain) -> None:
        if not self.events:
            return

        ev = self._select_recall_event()
        if not ev:
            return

        description = ev.get("description", "")
        if self._is_system_event(description):
            emo = 0.0
        else:
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
            content=f"Recall: {description}",
            source="memory",
            emotional_weight=emo,
            novelty=0.4,
            relevance_to_goals=0.3,
        )
        GlobalWorkspace.post(th)

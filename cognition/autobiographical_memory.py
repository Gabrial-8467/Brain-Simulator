from collections import deque
import time

class AutobiographicalMemory:
    def __init__(self, max_events=500):
        self.events = deque(maxlen=max_events)

    def record_event(self, description, chemicals, identity_snapshot, metadata=None):
        event = {
            "timestamp": time.time(),
            "description": description,
            "chemicals": chemicals.copy(),
            "identity": identity_snapshot.copy(),
            "metadata": metadata or {}
        }
        self.events.append(event)

    def get_recent_events(self, n=50):
        return list(self.events)[-n:]

    def get_all_events(self):
        return list(self.events)

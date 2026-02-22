import uuid
import time


class Memory:
    def __init__(self, memory_type: str, content: dict, metadata: dict = None):
        self.id = str(uuid.uuid4())
        self.type = memory_type
        self.content = content
        self.metadata = metadata or {}

        self.created_at = time.time()
        self.last_accessed = time.time()

        self.importance = 1.0
        self.reinforcement_count = 0
        self.decay_rate = self.metadata.get("decay_rate", 0.001)

    def reinforce(self, weight: float = 1.0):
        self.importance += weight
        self.reinforcement_count += 1
        self.last_accessed = time.time()

    def decay(self):
        self.importance -= self.importance * self.decay_rate
        if self.importance < 0:
            self.importance = 0

    def to_dict(self):
        return self.__dict__
